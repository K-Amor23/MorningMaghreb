import asyncio
import os
import re
import unicodedata
from datetime import datetime
from typing import List, Dict, Any, Optional

import aiohttp
from sqlalchemy import text

from database.connection import get_db_session_context
from scrapers.ir_adapters import StaticFilesAdapter


def _normalize_text(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()


def infer_year_and_type(title: str, url: str) -> (int, str):
    blob = f"{title or ''} {url or ''}"
    norm = _normalize_text(blob)

    year = datetime.utcnow().year
    m = re.search(r"(20\d{2})", norm)
    if m:
        try:
            y = int(m.group(1))
            if 2000 <= y <= 2100:
                year = y
        except Exception:
            pass

    if re.search(r"\bq([1-4])\b", norm) or re.search(r"\bt([1-4])\b", norm) or re.search(r"trimestre\s*([1-4])", norm):
        return year, "quarterly_report"
    if any(k in norm for k in ["semestriel", "semestre", "semester", "interim"]):
        return year, "annual_report"
    if any(k in norm for k in ["annual report", "rapport annuel", "annual"]):
        return year, "annual_report"
    if any(k in norm for k in ["etats financiers", "financial statements", "financier", "financial", "compte"]):
        return year, "financial_statement"
    return year, "unknown"


async def head_ok(session: aiohttp.ClientSession, url: str) -> bool:
    try:
        async with session.head(url, allow_redirects=True) as resp:
            if resp.status >= 400:
                return False
            ct = (resp.headers.get("content-type") or "").lower()
            if "pdf" not in ct:
                return False
            cl = resp.headers.get("content-length")
            if cl and cl.isdigit() and int(cl) < 30000:
                return False
            return True
    except Exception:
        return False


async def insert_reports(rows: List[Dict[str, Any]]):
    if not rows:
        return
    insert_sql = text(
        """
        INSERT INTO public.company_reports
            (id, ticker, company_name, url, title, source, report_type, year, quarter, language, published_date, created_at, updated_at)
        VALUES
            (gen_random_uuid(), :ticker, :company_name, :url, :title, :source, :report_type, :year, :quarter, :language, :published_date, now(), now())
        ON CONFLICT (url) DO NOTHING
        """
    )
    async with get_db_session_context() as session:
        for r in rows:
            await session.execute(insert_sql, r)


async def seed_atw() -> int:
    pages = [
        "https://ir.attijariwafabank.com/financial-information/annual-reports",
        "https://ir.attijariwafabank.com/financial-information/financial-results",
    ]
    adapter = StaticFilesAdapter(pages)
    UA_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.113 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr,en;q=0.9",
        "Connection": "keep-alive",
    }
    async with aiohttp.ClientSession(headers=UA_HEADERS) as session:
        reports = await adapter.fetch_reports(session, "https://ir.attijariwafabank.com", "ATW")
        # Validate links
        valid: List[Dict[str, Any]] = []
        seen = set()
        for r in reports:
            url = r.get("url")
            if not url or url in seen:
                continue
            seen.add(url)
            if await head_ok(session, url):
                y, rt = infer_year_and_type(r.get("title") or "", url)
                valid.append({
                    "ticker": "ATW",
                    "company_name": "Attijariwafa Bank",
                    "url": url,
                    "title": r.get("title") or "Financial Report",
                    "source": "issuer",
                    "report_type": rt,
                    "year": y,
                    "quarter": None,
                    "language": "fr",
                    "published_date": None,
                })
        await insert_reports(valid)
        return len(valid)


async def main():
    tickers = (os.environ.get("TICKERS") or "ATW").split(",")
    total = 0
    if "ATW" in {t.strip().upper() for t in tickers}:
        total += await seed_atw()
    print(f"Inserted {total} reports")


if __name__ == "__main__":
    asyncio.run(main())


