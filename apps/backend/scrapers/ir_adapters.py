import asyncio
import aiohttp
from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup


class BaseIRAdapter:
    async def fetch_reports(self, session: aiohttp.ClientSession, base_url: str, company: str) -> List[Dict]:
        raise NotImplementedError


class WordPressIRAdapter(BaseIRAdapter):
    """
    Fetch PDFs via WordPress REST API if available.
    Tries /wp-json/wp/v2/media (PDF assets) and /wp-json/wp/v2/posts with finance keywords.
    """

    def __init__(self, site_origin: str):
        self.site_origin = site_origin.rstrip("/")
        self.keywords = ["rapport", "annuel", "financier", "financial", "results", "résultats", "etats"]

    async def fetch_reports(self, session: aiohttp.ClientSession, base_url: str, company: str) -> List[Dict]:
        results: List[Dict] = []

        # 1) Media endpoint (PDF assets)
        media_urls = [
            f"{self.site_origin}/wp-json/wp/v2/media?per_page=100",
        ]
        for api in media_urls:
            try:
                async with session.get(api, allow_redirects=True) as resp:
                    if resp.status != 200:
                        continue
                    data = await resp.json()
                if isinstance(data, list):
                    for item in data:
                        src = (item.get("source_url") or "").strip()
                        title = (item.get("title", {}).get("rendered") or item.get("title") or "").strip()
                        if src.lower().endswith(".pdf") and any(k in (title + " " + src).lower() for k in self.keywords):
                            results.append({
                                "url": src,
                                "title": title or "Financial Report",
                                "date": item.get("date") or "Unknown",
                                "company": company,
                                "type": "financial_report",
                                "trusted": True,
                            })
            except Exception:
                continue

        # 2) Posts endpoint (links inside content)
        posts_urls = [
            f"{self.site_origin}/wp-json/wp/v2/posts?per_page=50",
            f"{self.site_origin}/wp-json/wp/v2/pages?per_page=50",
        ]
        for api in posts_urls:
            try:
                async with session.get(api, allow_redirects=True) as resp:
                    if resp.status != 200:
                        continue
                    data = await resp.json()
                if isinstance(data, list):
                    for item in data:
                        title = (item.get("title", {}).get("rendered") or "").lower()
                        content = (item.get("content", {}).get("rendered") or "").lower()
                        if not any(k in title or k in content for k in self.keywords):
                            continue
                        # naive PDF link extraction
                        for token in content.split():
                            if token.startswith("http") and token.lower().endswith(".pdf"):
                                results.append({
                                    "url": token.strip('"\'<>'),
                                    "title": (item.get("title", {}).get("rendered") or "Financial Report"),
                                    "date": item.get("date") or "Unknown",
                                    "company": company,
                                    "type": "financial_report",
                                    "trusted": True,
                                })
            except Exception:
                continue

        return results


class PlaywrightIRAdapter(BaseIRAdapter):
    """Headless render for JS-heavy pages with optional per-company config."""

    def __init__(self, pages: List[str], config: Optional[dict] = None):
        self.pages = pages
        self.config = config or {}

    async def fetch_reports(self, session: aiohttp.ClientSession, base_url: str, company: str) -> List[Dict]:
        try:
            from playwright.async_api import async_playwright  # type: ignore
        except Exception:
            return []

        results: List[Dict] = []
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True, args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ])
            context = await browser.new_context(
                user_agent=
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.113 Safari/537.36",
                locale="fr-FR"
            )
            page = await context.new_page()
            for url in self.pages:
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                    # Try to dismiss cookie/consent banners
                    consent_selectors = self.config.get("consent_selectors") or [
                        "button:has-text('Accept')",
                        "button:has-text('Accepter')",
                        "#onetrust-accept-btn-handler",
                        "button[aria-label='accept']",
                    ]
                    for sel in consent_selectors:
                        try:
                            btn = page.locator(sel)
                            if await btn.count() > 0:
                                await btn.first.click(timeout=2000)
                                await page.wait_for_timeout(500)
                        except Exception:
                            pass
                    # Optional click sequence (tabs like Publications/Results)
                    click_sequence = self.config.get("click_sequence", []) or []
                    wait_after_click = int(self.config.get("wait_after_click", 1000))
                    for sel in click_sequence:
                        try:
                            el = page.locator(sel)
                            if await el.count() > 0:
                                await el.first.click(timeout=4000)
                                await page.wait_for_timeout(wait_after_click)
                        except Exception:
                            pass
                    # Scroll to load dynamic content
                    scroll_steps = int(self.config.get("scroll_steps", 5))
                    for _ in range(max(1, scroll_steps)):
                        await page.mouse.wheel(0, 2000)
                        await page.wait_for_timeout(600)
                    # Wait for any link list
                    wait_for = self.config.get("wait_for") or "a[href]"
                    try:
                        await page.wait_for_selector(wait_for, timeout=7000)
                    except Exception:
                        pass
                    link_selector = self.config.get("link_selector") or "a[href]"
                    anchors = await page.eval_on_selector_all(
                        link_selector,
                        "els => els.map(a => ({href: a.getAttribute('href'), text: (a.textContent||'').trim()}))")
                    # Optional regex filter
                    regex = None
                    pattern = self.config.get("link_regex")
                    if isinstance(pattern, str) and pattern:
                        try:
                            regex = re.compile(pattern, re.IGNORECASE)
                        except Exception:
                            regex = None
                    for a in anchors or []:
                        href = a.get("href")
                        is_match = False
                        if isinstance(href, str):
                            h = href.lower()
                            is_match = h.endswith(".pdf") or ("/static-files/" in h)
                            if regex is not None:
                                is_match = bool(regex.search(href))
                        if is_match:
                            full = href if href.startswith("http") else (base_url.rstrip("/") + "/" + href.lstrip("/"))
                            results.append({
                                "url": full,
                                "title": (a.get("text") or "Financial Report").strip(),
                                "date": "Unknown",
                                "company": company,
                                "type": "financial_report",
                                "trusted": bool(self.config.get("trusted", True)),
                            })
                except Exception:
                    continue
            await browser.close()

        return results


class StaticFilesAdapter(BaseIRAdapter):
    """Directly scan a page for /static-files/ PDF links (e.g., ATW IR site)."""

    def __init__(self, pages: List[str]):
        self.pages = pages

    async def fetch_reports(self, session: aiohttp.ClientSession, base_url: str, company: str) -> List[Dict]:
        results: List[Dict] = []
        for url in self.pages:
            try:
                async with session.get(url, allow_redirects=True) as resp:
                    if resp.status != 200:
                        continue
                    html = await resp.text()
                # robust regex scan for static-files PDFs
                import re
                for m in re.finditer(r"https?://[^\s'\"]+/static-files/[A-Za-z0-9\-]+", html):
                    link = m.group(0)
                    if link:
                        results.append({
                            "url": link,
                            "title": "Financial Report",
                            "date": "Unknown",
                            "company": company,
                            "type": "financial_report",
                            "trusted": True,
                        })
            except Exception:
                continue
        return results


class SimpleHTMLIRAdapter(BaseIRAdapter):
    """Extract PDF links from static HTML pages using basic heuristics."""

    def __init__(self, pages: List[str]):
        self.pages = pages

    async def fetch_reports(self, session: aiohttp.ClientSession, base_url: str, company: str) -> List[Dict]:
        results: List[Dict] = []
        patterns = [
            r"href=\"(https?://[^\"]+\.pdf)\"",
            r"href='(https?://[^']+\.pdf)'",
        ]
        for url in self.pages:
            try:
                async with session.get(url, allow_redirects=True) as resp:
                    if resp.status != 200:
                        continue
                    html = await resp.text()
                for pat in patterns:
                    for m in re.finditer(pat, html, flags=re.IGNORECASE):
                        link = m.group(1)
                        if link:
                            results.append({
                                "url": link,
                                "title": "Financial Report",
                                "date": "Unknown",
                                "company": company,
                                "type": "financial_report",
                                "trusted": True,
                            })
            except Exception:
                continue
        return results


class CSEDocumentHostAdapter(BaseIRAdapter):
    """Fetch financial reports from Casablanca Stock Exchange document host for any company."""
    
    def __init__(self, company_ticker: str):
        self.company_ticker = company_ticker
        self.base_url = "https://www.casablanca-bourse.com"
        
        # Working CSE endpoints we discovered
        self.working_endpoints = [
            f"{self.base_url}/fr/marche-cash/instruments-actions",
            f"{self.base_url}/fr/listing-des-emetteurs",
            f"{self.base_url}/fr/publications-des-emetteurs"
        ]
        
    async def fetch_reports(self, session: aiohttp.ClientSession, base_url: str, company: str) -> List[Dict]:
        results: List[Dict] = []
        
        for endpoint in self.working_endpoints:
            try:
                print(f"  Trying CSE endpoint: {endpoint}")
                async with session.get(endpoint) as resp:
                    if resp.status != 200:
                        continue
                    
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for company-specific content
                    text_content = soup.get_text()
                    if self.company_ticker in text_content:
                        print(f"    Found {self.company_ticker} content on {endpoint}")
                        
                        # Look for PDF links
                        pdf_links = soup.find_all('a', href=lambda x: x and x.lower().endswith('.pdf'))
                        for pdf_link in pdf_links:
                            href = pdf_link.get('href', '')
                            text = pdf_link.get_text(strip=True)
                            
                            # Check if this PDF is related to our company
                            if (self.company_ticker.lower() in text.lower() or 
                                self.company_ticker.lower() in href.lower() or
                                any(keyword in text.lower() for keyword in ['rapport', 'report', 'financier', 'financial', 'annuel', 'annual'])):
                                
                                full_url = href if href.startswith('http') else f"{self.base_url}/{href.lstrip('/')}"
                                results.append({
                                    "url": full_url,
                                    "title": text or f"Financial Report - {self.company_ticker}",
                                    "date": "Unknown",
                                    "company": company,
                                    "type": "financial_report",
                                    "trusted": True,
                                    "source": "cse_document_host"
                                })
                        
                        # Look for company detail pages (like /fr/live-market/emetteurs/{TICKER_CODE})
                        company_links = soup.find_all('a', href=True)
                        for link in company_links:
                            href = link.get('href', '')
                            text = link.get_text(strip=True)
                            
                            # Look for company detail pages - this is the key pattern
                            if (href.startswith('/fr/live-market/emetteurs/') and 
                                self.company_ticker.lower() in href.lower()):
                                
                                full_url = f"{self.base_url}{href}"
                                print(f"    Found company detail page: {full_url}")
                                
                                # Try to fetch this company detail page
                                try:
                                    async with session.get(full_url) as company_resp:
                                        if company_resp.status == 200:
                                            company_html = await company_resp.text()
                                            company_soup = BeautifulSoup(company_html, 'html.parser')
                                            
                                            # Look for PDFs on this company page
                                            company_pdfs = company_soup.find_all('a', href=lambda x: x and x.lower().endswith('.pdf'))
                                            for pdf_link in company_pdfs:
                                                pdf_href = pdf_link.get('href', '')
                                                pdf_text = pdf_link.get_text(strip=True)
                                                
                                                pdf_full_url = pdf_href if pdf_href.startswith('http') else f"{self.base_url}/{pdf_href.lstrip('/')}"
                                                results.append({
                                                    "url": pdf_full_url,
                                                    "title": pdf_text or f"Financial Report - {self.company_ticker}",
                                                    "date": "Unknown",
                                                    "company": company,
                                                    "type": "financial_report",
                                                    "trusted": True,
                                                    "source": "cse_document_host"
                                                })
                                            
                                            # Also look for any financial report links (not just PDFs)
                                            financial_links = company_soup.find_all('a', href=True)
                                            for fin_link in financial_links:
                                                fin_href = fin_link.get('href', '')
                                                fin_text = fin_link.get_text(strip=True)
                                                
                                                # Look for financial report indicators
                                                if any(keyword in fin_text.lower() for keyword in ['rapport', 'report', 'financier', 'financial', 'annuel', 'annual', 'trimestre', 'quarter']):
                                                    fin_full_url = fin_href if fin_href.startswith('http') else f"{self.base_url}/{fin_href.lstrip('/')}"
                                                    results.append({
                                                        "url": fin_full_url,
                                                        "title": fin_text or f"Financial Report - {self.company_ticker}",
                                                        "source": "cse_document_host"
                                                    })
                                except Exception as e:
                                    print(f"      Error fetching company page {full_url}: {e}")
                                    continue
                                    
            except Exception as e:
                print(f"    Error with endpoint {endpoint}: {e}")
                continue
                
        return results


class SitemapIRAdapter(BaseIRAdapter):
    """Discover PDFs via sitemap.xml (and nested sitemaps)."""

    def __init__(self, origin: str):
        self.origin = origin.rstrip('/')

    async def _get(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        try:
            async with session.get(url, allow_redirects=True) as resp:
                if resp.status != 200:
                    return None
                return await resp.text()
        except Exception:
            return None

    async def fetch_reports(self, session: aiohttp.ClientSession, base_url: str, company: str) -> List[Dict]:
        results: List[Dict] = []
        sitemap_urls = [f"{self.origin}/sitemap.xml"]
        visited = set()
        pdfs: List[str] = []
        while sitemap_urls:
            url = sitemap_urls.pop(0)
            if url in visited:
                continue
            visited.add(url)
            xml = await self._get(session, url)
            if not xml:
                continue
            # nested sitemaps
            for m in re.finditer(r"<loc>(.*?)</loc>", xml, flags=re.IGNORECASE):
                loc = m.group(1).strip()
                if not loc.startswith("http"):
                    continue
                if loc.endswith('.xml') and self.origin in loc:
                    sitemap_urls.append(loc)
                elif self.origin in loc and loc.lower().endswith('.pdf'):
                    pdfs.append(loc)
                elif self.origin in loc and re.search(r"(rapport|annual|financ|publication|results)", loc, re.IGNORECASE):
                    # potential HTML page; skip here; Sitemap adapter focuses on direct PDFs
                    pass
        for link in sorted(set(pdfs)):
            results.append({
                "url": link,
                "title": "Financial Report",
                "date": "Unknown",
                "company": company,
                "type": "financial_report",
                "trusted": True,
            })
        return results


class AfricanMarketsAdapter(BaseIRAdapter):
    """Fetch comprehensive company data from African Markets website."""
    
    def __init__(self, company_ticker: str):
        self.company_ticker = company_ticker
        self.base_url = "https://www.african-markets.com"
        self.exchange_url = f"{self.base_url}/en/stock-markets/bvc"
        
    async def fetch_reports(self, session: aiohttp.ClientSession, base_url: str, company: str) -> List[Dict]:
        results: List[Dict] = []
        
        try:
            # Step 1: Try direct company URL pattern first (most reliable)
            direct_url = f"{self.base_url}/en/stock-markets/bvc/listed-companies/company?code={self.company_ticker}.MA"
            print(f"    Trying direct African Markets URL: {direct_url}")
            
            async with session.get(direct_url) as direct_resp:
                if direct_resp.status == 200:
                    direct_html = await direct_resp.text()
                    direct_soup = BeautifulSoup(direct_html, 'html.parser')
                    
                    # Extract all available data
                    self._extract_financial_reports(direct_soup, results, direct_url)
                    self._extract_market_data(direct_soup, results, direct_url)
                    self._extract_news_announcements(direct_soup, results, direct_url)
                    
                    if results:
                        print(f"      Found {len(results)} items from African Markets")
                        return results
            
            # Step 2: If direct URL failed, try to find company on BVC exchange page
            print(f"    Direct URL failed, searching BVC exchange page for {self.company_ticker}")
            
            async with session.get(self.exchange_url) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for company links
                    company_links = soup.find_all('a', href=True)
                    company_url = None
                    
                    for link in company_links:
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        # Look for company-specific links
                        if (self.company_ticker.lower() in text.lower() or 
                            self.company_ticker.lower() in href.lower()):
                            company_url = href if href.startswith('http') else f"{self.base_url}{href}"
                            print(f"      Found company page: {company_url}")
                            break
                    
                    # Step 3: If company found, scrape their detailed page
                    if company_url:
                        async with session.get(company_url) as company_resp:
                            if company_resp.status == 200:
                                company_html = await company_resp.text()
                                company_soup = BeautifulSoup(company_html, 'html.parser')
                                
                                # Extract financial reports and documents
                                self._extract_financial_reports(company_soup, results, company_url)
                                
                                # Extract market data
                                self._extract_market_data(company_soup, results, company_url)
                                
                                # Extract news and announcements
                                self._extract_news_announcements(company_soup, results, company_url)
                                
        except Exception as e:
            print(f"      Error in African Markets adapter: {e}")
            
        return results
    
    def _extract_financial_reports(self, soup: BeautifulSoup, results: List[Dict], base_url: str):
        """Extract financial reports and documents from company page."""
        # Look for financial reports section
        reports_section = soup.find('div', string=lambda x: x and 'Reports' in x)
        if reports_section:
            report_links = reports_section.find_all('a', href=True)
            for link in report_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if any(keyword in text.lower() for keyword in ['annual', 'quarterly', 'financial', 'report', 'rapport']):
                    full_url = href if href.startswith('http') else f"{self.base_url}{href}"
                    results.append({
                        "url": full_url,
                        "title": text,
                        "type": "financial_report",
                        "source": "african_markets",
                        "ticker": self.company_ticker,
                        "trusted": True
                    })
    
    def _extract_market_data(self, soup: BeautifulSoup, results: List[Dict], base_url: str):
        """Extract market data and trading information."""
        # Look for market data like price, volume, market cap
        market_data = {}
        
        # Price information
        price_elem = soup.find(string=lambda x: x and 'MAD' in x)
        if price_elem:
            market_data['price'] = price_elem.strip()
        
        # Volume information
        volume_elem = soup.find(string=lambda x: x and 'Volume' in x)
        if volume_elem:
            market_data['volume'] = volume_elem.strip()
        
        # Market cap
        cap_elem = soup.find(string=lambda x: x and 'Market Cap' in x)
        if cap_elem:
            market_data['market_cap'] = cap_elem.strip()
        
        if market_data:
            results.append({
                "url": base_url,
                "title": f"Market Data - {self.company_ticker}",
                "type": "market_data",
                "source": "african_markets",
                "ticker": self.company_ticker,
                "data": market_data,
                "trusted": True
            })
    
    def _extract_news_announcements(self, soup: BeautifulSoup, results: List[Dict], base_url: str):
        """Extract news and company announcements."""
        # Look for news section
        news_links = soup.find_all('a', href=True)
        for link in news_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Look for news and announcements
            if any(keyword in text.lower() for keyword in ['communiqué', 'press', 'news', 'announcement', 'dividend']):
                full_url = href if href.startswith('http') else f"{self.base_url}{href}"
                results.append({
                    "url": full_url,
                    "title": text,
                    "type": "news_announcement",
                    "source": "african_markets",
                    "ticker": self.company_ticker,
                    "trusted": True
                })


