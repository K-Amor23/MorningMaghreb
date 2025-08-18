import asyncio
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import aiohttp

DB_AVAILABLE = False
try:
    from database.connection import get_db_session_context  # type: ignore
    from sqlalchemy import text  # type: ignore

    DB_AVAILABLE = True
except Exception:
    DB_AVAILABLE = False

from etl.fetch_ir_reports import IRReportFetcher
from scrapers.ir_adapters import (
    BaseIRAdapter, WordPressIRAdapter, PlaywrightIRAdapter, 
    StaticFilesAdapter, SimpleHTMLIRAdapter, SitemapIRAdapter,
    CSEDocumentHostAdapter, AfricanMarketsAdapter
)

# Shared fetch headers (avoid truncated/bad UA)
UA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.113 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr,en;q=0.9",
    "Connection": "keep-alive",
}
from storage.local_fs import LocalFileStorage


async def fetch_active_companies(limit: Optional[int] = None) -> List[Tuple[str, str]]:
    """Return list of (ticker, company_name) for active companies from DB."""
    if not DB_AVAILABLE:
        return []
    query = """
        SELECT ticker, name
        FROM companies
        WHERE (is_active = TRUE OR is_active = 'Y')
        ORDER BY ticker
    """
    if limit is not None:
        query += f" LIMIT {int(limit)}"

    async with get_db_session_context() as session:
        result = await session.execute(text(query))
        rows = result.fetchall()
        return [(r[0], r[1]) for r in rows if r and r[0]]


def load_companies_from_json(limit: Optional[int] = None) -> List[Tuple[str, str]]:
    """Fallback: read tickers and names from company_ir_pages.json."""
    json_path = Path("apps/backend/data/company_ir_pages.json")
    companies: List[Tuple[str, str]] = []
    if json_path.exists():
        data = json.loads(json_path.read_text(encoding="utf-8"))
        for ticker, info in data.items():
            name = info.get("name") or ticker
            companies.append((ticker, name))
    companies.sort(key=lambda x: x[0])
    if limit is not None:
        companies = companies[: int(limit)]
    return companies


def infer_year_and_type(title: str, url: str) -> Tuple[Optional[int], str]:
    """Infer year and report_type from link text/url."""
    blob = f"{title} {url}"
    year = None
    m = re.search(r"(20\d{2})", blob)
    if m:
        year = int(m.group(1))

    t_low = blob.lower()
    report_type = "unknown"
    if any(k in t_low for k in ["annual", "rapport annuel"]):
        report_type = "annual_report"
    elif any(
        k in t_low
        for k in [
            "quarterly",
            "trimestriel",
            "trimestre",
            "q1",
            "q2",
            "q3",
            "q4",
            "t1",
            "t2",
            "t3",
            "t4",
        ]
    ):
        report_type = "quarterly_report"
    elif any(k in t_low for k in ["semester", "semestriel", "semestre"]):
        # treat semi-annual as financial statements unless title says annual explicitly
        report_type = "financial_statement"
    elif any(
        k in t_low
        for k in [
            "financial",
            "financier",
            "compte",
            "états financiers",
            "etats financiers",
        ]
    ):
        report_type = "financial_statement"

    return year, report_type


async def upsert_company_report(row: Dict[str, Any], company_name: str) -> None:
    """Insert discovered report into company_reports if not present."""
    if not DB_AVAILABLE or os.environ.get("WRITE_DB") != "1":
        return
    insert_sql = text(
        """
        INSERT INTO public.company_reports
            (id, ticker, company_name, title, report_type, report_year, report_quarter, url, source, scraped_at, created_at, updated_at)
        VALUES
            (
                gen_random_uuid(),
                :ticker,
                :company_name,
                :title,
                :report_type,
                :year,
                :quarter,
                :url,
                :source,
                now(),
                now(),
                now()
            )
        ON CONFLICT (url) DO NOTHING
        """
    )

    async with get_db_session_context() as session:
        await session.execute(
            insert_sql,
            {
                "ticker": row.get("ticker") or row.get("company"),
                "company_name": company_name,
                "title": row.get("title") or "Financial Report",
                "report_type": (row.get("report_type") or "unknown"),
                "year": str(row.get("year")) if row.get("year") else None,
                "quarter": str(row.get("quarter")) if row.get("quarter") else None,
                "url": row.get("url"),
                "source": row.get("source") or "issuer",
            },
        )


async def main(limit: Optional[int] = None) -> None:
    companies: List[Tuple[str, str]] = []
    # Optional filter by env TICKERS (comma-separated)
    tickers_filter = None
    env_tickers = os.environ.get("TICKERS")
    if env_tickers:
        tickers_filter = {t.strip().upper() for t in env_tickers.split(',') if t.strip()}
    
    # Prefer DB; fallback to JSON
    db_companies = await fetch_active_companies(None)  # Get all companies first
    if db_companies:
        companies = db_companies
    else:
        companies = load_companies_from_json(None)  # Get all companies first
    
    if tickers_filter:
        companies = [(t, n) for (t, n) in companies if t.upper() in tickers_filter]
    
    # Apply limit after filtering
    if limit is not None:
        companies = companies[:limit]
    
    storage = LocalFileStorage()
    total_found = 0
    all_results: Dict[str, Any] = {
        "started_at": datetime.utcnow().isoformat(),
        "companies": [],
    }

    # Load optional per-company adapter config
    config_path = Path("data/ir_adapters_config.json")
    config_data: Dict[str, Any] = {}
    if config_path.exists():
        try:
            config_data = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            config_data = {}
    
    async with IRReportFetcher(storage) as fetcher:
        for ticker, name in companies:
            try:
                reports = await fetcher.fetch_company_reports(ticker)
                
                # Config-driven adapters
                if not reports:
                    company_cfg = (config_data.get("companies", {}).get(ticker)) if isinstance(config_data, dict) else None
                    if company_cfg:
                        origin = company_cfg.get("origin")
                        pages = company_cfg.get("pages") or []
                        priority_sources = company_cfg.get("priority_sources", [])
                        
                        # Follow priority order if specified
                        if priority_sources:
                            for source in priority_sources:
                                if source == "cse_document_host" and not reports:
                                    # Try CSE document host first for BCP
                                    adapter_cse = CSEDocumentHostAdapter(ticker)
                                    async with aiohttp.ClientSession(headers=UA_HEADERS) as session:
                                        cse_reports = await adapter_cse.fetch_reports(session, origin or "", ticker)
                                        if cse_reports:
                                            reports = cse_reports
                                            break
                                            
                                elif source == "simple_html" and not reports and pages:
                                    adapter_html = SimpleHTMLIRAdapter(pages)
                                    async with aiohttp.ClientSession(headers=UA_HEADERS) as session:
                                        base = pages[0].split('/')[0] + '//' + pages[0].split('/')[2]
                                        html_reports = await adapter_html.fetch_reports(session, base, ticker)
                                        if html_reports:
                                            reports = html_reports
                                            break
                                            
                                elif source == "playwright" and not reports and pages:
                                    adapter_pw = PlaywrightIRAdapter(pages, config=company_cfg)
                                    async with aiohttp.ClientSession() as session:
                                        base = pages[0].split('/')[0] + '//' + pages[0].split('/')[2]
                                        pw_reports = await adapter_pw.fetch_reports(session, base, ticker)
                                        if pw_reports:
                                            reports = pw_reports
                                            break
                                            
                                elif source == "wordpress" and not reports and origin:
                                    adapter_wp: BaseIRAdapter = WordPressIRAdapter(origin)
                                    async with aiohttp.ClientSession(headers=UA_HEADERS) as session:
                                        wp_reports = await adapter_wp.fetch_reports(session, origin, ticker)
                                        if wp_reports:
                                            reports = wp_reports
                                            break
                                            
                                elif source == "sitemap" and not reports and origin:
                                    adapter_sm = SitemapIRAdapter(origin)
                                    async with aiohttp.ClientSession(headers=UA_HEADERS) as session:
                                        sm_reports = await adapter_sm.fetch_reports(session, origin, ticker)
                                        if sm_reports:
                                            reports = sm_reports
                                            break
                                            
                                elif source == "african_markets" and not reports and origin:
                                    adapter_am = AfricanMarketsAdapter(ticker)
                                    async with aiohttp.ClientSession(headers=UA_HEADERS) as session:
                                        am_reports = await adapter_am.fetch_reports(session, origin or "", ticker)
                                        if am_reports:
                                            reports = am_reports
                                            break
                        else:
                            # Fallback to original logic if no priority specified
                            # 1) Try Simple HTML first if pages provided
                            if pages:
                                adapter_html = SimpleHTMLIRAdapter(pages)
                                async with aiohttp.ClientSession(headers=UA_HEADERS) as session:
                                    base = pages[0].split('/')[0] + '//' + pages[0].split('/')[2]
                                    html_reports = await adapter_html.fetch_reports(session, base, ticker)
                                    if html_reports:
                                        reports = html_reports
                            # 2) Playwright with config for selectors/scrolls
                            if not reports and pages:
                                adapter_pw = PlaywrightIRAdapter(pages, config=company_cfg)
                                async with aiohttp.ClientSession() as session:
                                    base = pages[0].split('/')[0] + '//' + pages[0].split('/')[2]
                                    pw_reports = await adapter_pw.fetch_reports(session, base, ticker)
                                    if pw_reports:
                                        reports = pw_reports
                            # 3) WordPress JSON if origin looks like WP
                            if not reports and origin and any(h in origin for h in ["iam.ma", "bcp.ma", "cihbank.ma"]):
                                adapter_wp: BaseIRAdapter = WordPressIRAdapter(origin)
                                async with aiohttp.ClientSession(headers=UA_HEADERS) as session:
                                    wp_reports = await adapter_wp.fetch_reports(session, origin, ticker)
                                    if wp_reports:
                                        reports = wp_reports
                            # 4) Sitemap discovery as last resort
                            if not reports and origin:
                                adapter_sm = SitemapIRAdapter(origin)
                                async with aiohttp.ClientSession(headers=UA_HEADERS) as session:
                                    sm_reports = await adapter_sm.fetch_reports(session, origin, ticker)
                                    if sm_reports:
                                        reports = sm_reports
                            # 5) African Markets as last resort
                            if not reports and origin:
                                adapter_am = AfricanMarketsAdapter(ticker)
                                async with aiohttp.ClientSession(headers=UA_HEADERS) as session:
                                    am_reports = await adapter_am.fetch_reports(session, origin, ticker)
                                    if am_reports:
                                        reports = am_reports
                
                # Universal CSE fallback for all companies
                if not reports:
                    print(f"  Trying universal CSE fallback for {ticker}")
                    adapter_cse = CSEDocumentHostAdapter(ticker)
                    async with aiohttp.ClientSession(headers=UA_HEADERS) as session:
                        cse_reports = await adapter_cse.fetch_reports(session, "", ticker)
                        if cse_reports:
                            reports = cse_reports
                            print(f"  CSE fallback found {len(cse_reports)} reports for {ticker}")

                # enrich with year/type
                enriched: List[Dict[str, Any]] = []
                for r in reports:
                    y, rt = infer_year_and_type(
                        r.get("title") or "", r.get("url") or ""
                    )
                    r["year"] = y
                    r["report_type"] = rt
                    enriched.append(r)
                total_found += len(enriched)
                # insert into DB
                for r in enriched:
                    await upsert_company_report(r, name)
                all_results["companies"].append(
                    {"ticker": ticker, "name": name, "count": len(enriched)}
                )
            except Exception as e:
                all_results["companies"].append(
                    {"ticker": ticker, "name": name, "error": str(e)}
                )

    all_results["total_found"] = total_found
    all_results["finished_at"] = datetime.utcnow().isoformat()
    out_dir = Path("apps/backend/data/financial_reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"discovery_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    out_file.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    print(f"Done. Total reports discovered: {total_found}. Saved to {out_file}")


if __name__ == "__main__":
    import os

    lim = os.environ.get("LIMIT")
    asyncio.run(main(int(lim) if lim else None))
