import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
import json
from pathlib import Path
from typing import List, Dict, Optional, Set
import re
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse

from storage.local_fs import LocalFileStorage
from models.financials import ETLJob, JobType, JobStatus

logger = logging.getLogger(__name__)


class IRReportFetcher:
    """Fetches financial reports from company IR pages"""
    
    def __init__(self, storage: LocalFileStorage):
        self.storage = storage
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Moroccan companies with their IR pages
        self.company_ir_pages = {
            "ATW": {
                "base_url": "https://ir.attijariwafabank.com/financial-information/annual-reports",
                "selectors": {
                    "reports": "a[href*='.pdf'], a[href*='/static-files/']",
                    "title": "h1, h2, h3, td",
                    "date": ".date, .published-date, td",
                },
            },
            "IAM": {
                "base_url": "https://www.iam.ma/fr/investisseurs/informations-financieres",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date",
                },
            },
            "BCP": {
                "base_url": "https://www.bcp.ma/fr/investisseurs/informations-financieres",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date",
                },
            },
            "BMCE": {
                "base_url": "https://www.bmcebankofafrica.com/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date",
                },
            },
            "CIH": {
                "base_url": "https://www.cih.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date",
                },
            },
            "WAA": {
                "base_url": "https://www.wafaassurance.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date",
                },
            },
            "LBV": {
                "base_url": "https://www.labelvie.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date",
                },
            },
            "TMA": {
                "base_url": "https://www.taqamorocco.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date",
                },
            },
            "ADH": {
                "base_url": "https://www.addoha.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date",
                },
            },
            "LES": {
                "base_url": "https://www.lesieurcristal.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date",
                },
            },
            "SOT": {
                "base_url": "https://www.sothema.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date",
                },
            },
            "CTM": {
                "base_url": "https://www.ctm.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date",
                },
            },
        }

        # Load extended seeds from JSON if available (path-safe relative to this file)
        try:
            base_dir = Path(__file__).resolve().parent  # .../apps/backend/etl
            candidates = [
                base_dir.parent / "data" / "company_ir_pages.json",  # apps/backend/data/company_ir_pages.json
                Path.cwd() / "apps" / "backend" / "data" / "company_ir_pages.json",
                Path("apps/backend/data/company_ir_pages.json"),
            ]
            seeds_path = next((p for p in candidates if p.exists()), None)
            if seeds_path:
                data = json.loads(seeds_path.read_text(encoding="utf-8"))
                for ticker, info in data.items():
                    base = info.get("ir_url") or info.get("base_url")
                    if not base:
                        continue
                    self.company_ir_pages[ticker] = {
                        "base_url": base,
                        "selectors": {
                            "reports": "a[href*='.pdf'], a[href*='/static-files/']",
                            "title": "h1, h2, h3, td",
                            "date": ".date, .published-date, td",
                        },
                    }
            # Ensure ATW override stays correct
            self.company_ir_pages["ATW"][
                "base_url"
            ] = "https://ir.attijariwafabank.com/financial-information/annual-reports"
        except Exception:
            pass

        # Default URL template for companies not explicitly mapped
        self.default_ir_url_template = "https://www.{company_name}.ma/fr/investisseurs"
        
        # Report type patterns
        self.report_patterns = {
            "pnl": [
                r"compte.*resultat",
                r"resultat.*exploitation",
                r"pnl",
                r"profit.*loss",
                r"compte.*exploitation",
            ],
            "balance": [
                r"bilan",
                r"balance.*sheet",
                r"situation.*financiere",
                r"actif.*passif",
            ],
            "cashflow": [
                r"flux.*tresorerie",
                r"cash.*flow",
                r"tableau.*flux",
                r"variation.*tresorerie",
            ],
        }
    
    async def __aenter__(self):
        import ssl

        # Create SSL context that doesn't verify certificates (for development)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=connector,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "fr,en;q=0.9",
                "Connection": "keep-alive",
            },
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_company_reports(
        self, company: str, year: Optional[int] = None
    ) -> List[Dict]:
        """Fetch all available reports for a company"""
        company_config = self._get_company_config(company)
        if not company_config:
            logger.warning(f"No IR page configured for company: {company}")
            return []

        seed_url = company_config["base_url"]
        candidate_pages: List[str] = [seed_url]
        # Include optional per-company additional report pages from JSON config
        extra_pages = company_config.get("report_pages") if isinstance(company_config, dict) else None
        if isinstance(extra_pages, list):
            for p in extra_pages:
                if isinstance(p, str) and p:
                    candidate_pages.append(p)
        trusted_pages = set([p for p in candidate_pages])
        reports: List[Dict] = []

        try:
            # 1) Try seed page first
            reports.extend(await self._harvest_from_page(seed_url, company, trust_page=seed_url in trusted_pages))
            if reports:
                return reports

            # 2) Slug probing on root and locale variants
            candidate_pages.extend(await self._probe_discovery_pages(seed_url))
            for url in candidate_pages:
                if url == seed_url:
                        continue
                reports.extend(await self._harvest_from_page(url, company, trust_page=url in trusted_pages))
                if reports:
                    return self._dedupe_reports(reports)

            # 3) Sitemap discovery
            sitemap_pages = await self._discover_from_sitemap(seed_url)
            for url in sitemap_pages:
                reports.extend(await self._harvest_from_page(url, company, trust_page=url in trusted_pages))
                if reports:
                    return self._dedupe_reports(reports)

            # 4) Shallow BFS crawl (same domain), depth 3, max 60 pages from seed and candidates
            reports = await self._crawl_bfs_for_pdfs(
                seed_url, company, max_depth=3, max_pages=60
            )
            if reports:
                return self._dedupe_reports(reports)

            for url in candidate_pages:
                more = await self._crawl_bfs_for_pdfs(
                    url, company, max_depth=3, max_pages=60
                )
                reports.extend(more)
                if reports:
                    return self._dedupe_reports(reports)

            return self._dedupe_reports(reports)
        
        except Exception as e:
            logger.error(f"Error fetching reports for {company}: {e}")
            return self._dedupe_reports(reports)
    
    def _get_company_config(self, company: str) -> Optional[Dict]:
        """Get company IR page configuration with fallback to default template"""
        if company in self.company_ir_pages:
            return self.company_ir_pages[company]
        
        # Fallback to default template
        company_name_lower = company.lower()
        fallback_url = self.default_ir_url_template.format(
            company_name=company_name_lower
        )
        
        return {
            "base_url": fallback_url,
            "selectors": {
                "reports": "a[href*='.pdf']",
                "title": "h1, h2, h3",
                "date": ".date, .published-date",
            },
        }

    async def _harvest_from_page(self, url: str, company: str, trust_page: bool = False) -> List[Dict]:
        """Fetch a page and extract PDF report links with simple scoring."""
        try:
            async with self.session.get(url, allow_redirects=True) as resp:
                if resp.status != 200:
                    return []
                html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all("a", href=True)
            results: List[Dict] = []
            for a in links:
                href = a.get("href")
                text = a.get_text(strip=True) or ""
                abs_url = urljoin(url, href)
                if not abs_url.lower().startswith("http"):
                    continue
                if not (
                    abs_url.lower().endswith(".pdf")
                    or "/static-files/" in abs_url.lower()
                ):
                    # keep non-pdf candidates if strongly indicative
                    if self._score_text(text, abs_url) < 0.7:
                        continue
                results.append(
                    {
                        "url": abs_url,
                        "title": text or "Financial Report",
                        "date": "Unknown",
                        "company": company,
                        "type": "financial_report",
                    }
                )
            # Keep only likely IR PDFs and validate via HEAD; drop obvious marketing PDFs
            deny = [
                "catalogue",
                "smartphone",
                "conditions_generales",
                "fidelio",
                "brochure",
                "flyer",
            ]
            if trust_page:
                filtered = [r for r in results if r["url"].lower().endswith(".pdf") and not any(d in r["url"].lower() for d in deny)]
            else:
                filtered = [
                    r
                    for r in results
                    if self._is_ir_pdf(r["title"], r["url"]) and not any(d in r["url"].lower() for d in deny)
                ]
            validated: List[Dict] = []
            for r in filtered:
                try:
                    if await self._is_valid_pdf_url(r["url"]):
                        validated.append(r)
                except Exception:
                    continue
            results = validated
            return results
        except Exception:
            return []

    async def _probe_discovery_pages(self, seed_url: str) -> List[str]:
        """Probe common IR slugs on root and locale variants."""
        parsed = urlparse(seed_url)
        base_origin = f"{parsed.scheme}://{parsed.netloc}"
        locales = ["/", "/fr/", "/en/"]
        slugs = [
            # English
            "investors",
            "investor-relations",
            "investor",
            "investor-centre",
            "financial-information",
            "financial-information/annual-reports",
            "financial-information/financial-results",
            "publications",
            "annual-reports",
            "reports",
            # French
            "investisseurs",
            "informations-financieres",
            "publications-financieres",
            "rapports-financiers",
            "resultats-financiers",
            "rapport-annuel",
            "rapport-annuels",
            "publications",
            "documents",
            "documentation",
            "telechargements",
        ]
        candidates: List[str] = []
        for loc in locales:
            for slug in slugs:
                candidates.append(urljoin(base_origin + loc, slug))
        found: List[str] = []
        for url in candidates:
            try:
                async with self.session.get(url, allow_redirects=True) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        if ".pdf" in html.lower():
                            found.append(url)
            except Exception:
                continue
        return found

    async def _discover_from_sitemap(self, seed_url: str) -> List[str]:
        """Fetch /sitemap.xml and return candidate pages mentioning report tokens or years."""
        try:
            parsed = urlparse(seed_url)
            base_origin = f"{parsed.scheme}://{parsed.netloc}"
            sitemap_url = urljoin(base_origin + "/", "sitemap.xml")
            async with self.session.get(sitemap_url, allow_redirects=True) as resp:
                if resp.status != 200:
                    return []
                xml = await resp.text()
                # naive parse for loc tags
                locs = re.findall(r"<loc>(.*?)</loc>", xml, re.IGNORECASE)
                cands: List[str] = []
                for loc in locs:
                    url = loc.strip()
                    if not url.lower().startswith(base_origin.lower()):
                        continue
                    if re.search(
                        r"(annual|rapport|finance|financial-information|reporting|reports|20\d{2})",
                        url,
                        re.IGNORECASE,
                    ):
                        cands.append(url)
                return cands[:50]
        except Exception:
            return []

    def _score_text(self, text: str, url: str) -> float:
        """Score a link by keywords in text/url."""
        t = (text or "").lower()
        u = (url or "").lower()
        score = 0.0
        if re.search(
            r"(annual report|financial statements|consolidated|ifrs|financial results|financial report)",
            t,
        ):
            score += 0.5
        if re.search(
            r"(rapport annuel|etats financiers|états financiers|consolidé|consolide|rapport financier|document de référence|resultats financiers|publications financières)",
            t,
        ):
            score += 0.5
        if re.search(
            r"(annual|rapport|finance|financieres|financieres|report|publications|results|resultats)",
            u,
        ):
            score += 0.3
        if re.search(r"20\d{2}", t + " " + u):
            score += 0.2
        return min(score, 1.0)

    def _is_ir_pdf(self, title: str, url: str) -> bool:
        """Heuristic: is this URL likely an IR PDF (report/publication)?"""
        if not url:
            return False
        u = url.lower()
        if not (u.endswith(".pdf") or "/static-files/" in u):
            return False
        # Path tokens indicative of IR/publications
        path_tokens = [
            "invest",
            "investor",
            "investisseur",
            "investisseurs",
            "financial",
            "financier",
            "financieres",
            "financières",
            "publications",
            "rapport",
            "annual",
            "results",
            "resultats",
            "résultats",
            # common asset paths where reports live
            "/wp-content/uploads/",
            "/media/",
            "/documents/",
            "/document/",
            "/files/",
        ]
        if any(tok in u for tok in path_tokens):
            return True
        # Title keywords
        t = (title or "").lower()
        if re.search(
            r"(rapport|annual|financial|financier|etats financiers|états financiers|results|résultats)",
            t,
        ):
            return True
        return False

    async def _is_valid_pdf_url(self, url: str) -> bool:
        """HEAD check for content-type and size thresholds to reduce noise."""
        try:
            async with self.session.head(url, allow_redirects=True) as resp:
                ct = (resp.headers.get("content-type") or "").lower()
                if "pdf" not in ct:
                    return False
                cl = resp.headers.get("content-length")
                if cl is not None:
                    try:
                        if int(cl) < 30000:  # 30 KB minimum
                            return False
                    except Exception:
                        pass
                return True
        except Exception:
            # Fallback: accept if URL looks like a static-files link
            return url.lower().endswith(".pdf") or "/static-files/" in url.lower()

    async def _crawl_bfs_for_pdfs(
        self, seed_url: str, company: str, max_depth: int = 2, max_pages: int = 20
    ) -> List[Dict]:
        """Same-domain BFS crawl collecting PDF links with limits."""
        parsed = urlparse(seed_url)
        domain = parsed.netloc
        queue: List[tuple[str, int]] = [(seed_url, 0)]
        visited: Set[str] = set()
        collected: List[Dict] = []
        while queue and len(visited) < max_pages:
            url, depth = queue.pop(0)
            if url in visited or depth > max_depth:
                continue
            visited.add(url)
            try:
                async with self.session.get(url, allow_redirects=True) as resp:
                    if resp.status != 200:
                        continue
                    html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a.get("href")
                    abs_url = urljoin(url, href)
                    p = urlparse(abs_url)
                    if p.netloc != domain:
                        continue
                    if (
                        abs_url.lower().endswith(".pdf")
                        or "/static-files/" in abs_url.lower()
                    ):
                        title = a.get_text(strip=True) or "Financial Report"
                        collected.append(
                            {
                                "url": abs_url,
                                "title": title,
                                "date": "Unknown",
                                "company": company,
                                "type": "financial_report",
                            }
                        )
                    else:
                        if (
                            depth < max_depth
                            and self._score_text(a.get_text(strip=True) or "", abs_url)
                            >= 0.7
                        ):
                            queue.append((abs_url, depth + 1))
            except Exception:
                continue
        return collected

    def _dedupe_reports(self, reports: List[Dict]) -> List[Dict]:
        seen: Set[str] = set()
        unique: List[Dict] = []
        for r in reports:
            u = r.get("url")
            if u and u not in seen:
                seen.add(u)
                unique.append(r)
        return unique

    async def _extract_report_info(
        self, link_element, pdf_url: str, company: str
    ) -> Optional[Dict]:
        """Extract report information from link element"""
        try:
            # Get link text and title
            link_text = link_element.get_text(strip=True)
            title = link_element.get("title", link_text)
            
            # Try to extract year from text
            year_match = re.search(r"20\d{2}", title + link_text)
            year = int(year_match.group()) if year_match else datetime.now().year
            
            # Determine report type
            report_type = self._classify_report_type(title + link_text)
            
            # Extract quarter if present
            quarter = self._extract_quarter(title + link_text)
            
            return {
                "company": company,
                "year": year,
                "quarter": quarter,
                "report_type": report_type,
                "title": title,
                "url": pdf_url,
                "filename": self._generate_filename(
                    company, year, quarter, report_type
                ),
            }
        
        except Exception as e:
            logger.error(f"Error extracting report info: {e}")
            return None
    
    def _classify_report_type(self, text: str) -> str:
        """Classify report type based on text content"""
        text_lower = text.lower()
        
        for report_type, patterns in self.report_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return report_type
        
        return "other"
    
    def _extract_quarter(self, text: str) -> Optional[int]:
        """Extract quarter number from text"""
        quarter_patterns = [
            r"T(\d)",  # T1, T2, T3, T4
            r"Q(\d)",  # Q1, Q2, Q3, Q4
            r"(\d)er.*trimestre",  # 1er trimestre
            r"(\d)ème.*trimestre",  # 2ème trimestre
            r"(\d)rd.*trimestre",  # 3rd trimestre
            r"(\d)th.*trimestre",  # 4th trimestre
        ]
        
        for pattern in quarter_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                quarter = int(match.group(1))
                if 1 <= quarter <= 4:
                    return quarter
        
        return None
    
    def _generate_filename(
        self, company: str, year: int, quarter: Optional[int], report_type: str
    ) -> str:
        """Generate standardized filename"""
        filename = f"{company}_{year}"
        if quarter:
            filename += f"_Q{quarter}"
        filename += f"_{report_type}.pdf"
        return filename
    
    async def download_report(self, report_info: Dict) -> Optional[str]:
        """Download a single report"""
        try:
            async with self.session.get(report_info["url"]) as response:
                if response.status != 200:
                    logger.error(
                        f"Failed to download {report_info['url']}: {response.status}"
                    )
                    return None
                
                content = await response.read()
                
                # Save to local storage
                file_path = await self.storage.save_pdf(
                    content=content,
                    filename=report_info["filename"],
                    company=report_info["company"],
                    year=report_info["year"],
                )
                
                logger.info(f"Downloaded {report_info['filename']} to {file_path}")
                return file_path
        
        except Exception as e:
            logger.error(f"Error downloading {report_info['url']}: {e}")
            return None
    
    async def fetch_all_reports(
        self, companies: Optional[List[str]] = None, year: Optional[int] = None
    ) -> List[Dict]:
        """Fetch reports for all companies or specified companies"""
        if companies is None:
            companies = list(self.company_ir_pages.keys())
        
        all_reports = []
        
        async with self:
            for company in companies:
                logger.info(f"Fetching reports for {company}")
                company_reports = await self.fetch_company_reports(company, year)
                all_reports.extend(company_reports)
        
        return all_reports
    
    async def download_all_reports(self, reports: List[Dict]) -> List[str]:
        """Download all reports in the list"""
        downloaded_files = []
        
        async with self:
            for report in reports:
                file_path = await self.download_report(report)
                if file_path:
                    downloaded_files.append(file_path)
        
        return downloaded_files


# Example usage
async def main():
    """Example usage of the IR Report Fetcher"""
    storage = LocalFileStorage()
    
    async with IRReportFetcher(storage) as fetcher:
        # Fetch reports for ATW for 2024
        reports = await fetcher.fetch_company_reports("ATW", 2024)
        print(f"Found {len(reports)} reports for ATW")
        
        # Download all reports
        downloaded = await fetcher.download_all_reports(reports)
        print(f"Downloaded {len(downloaded)} files")


if __name__ == "__main__":
    asyncio.run(main()) 
