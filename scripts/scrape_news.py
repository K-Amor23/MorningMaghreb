#!/usr/bin/env python3
"""
Scrape Moroccan business news for selected tickers (ATW, IAM, BCP) into 'company_news'.

Env required:
  - NEXT_PUBLIC_SUPABASE_URL
  - SUPABASE_SERVICE_ROLE_KEY

Idempotent via upsert on (ticker, url, published_at) where applicable.
"""
import os
import sys
import asyncio
from typing import List, Dict

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "apps", "backend", "etl"))

try:
    from news_sentiment_scraper import NewsSentimentScraper  # type: ignore
except Exception as e:
    print("❌ Could not import NewsSentimentScraper. Ensure path is correct.", e)
    sys.exit(1)

try:
    from supabase import create_client  # type: ignore
except Exception:
    create_client = None  # optional; we fallback to ticker names


TICKERS: List[str] = ["ATW", "IAM", "BCP"]


async def run() -> int:
    total = 0
    async with NewsSentimentScraper(
        batch_size=len(TICKERS), max_concurrent=5
    ) as scraper:
        # Try to fetch real company names from Supabase for better news results
        companies: List[Dict[str, str]] = []
        if (
            create_client
            and os.getenv("NEXT_PUBLIC_SUPABASE_URL")
            and os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        ):
            try:
                client = create_client(
                    os.getenv("NEXT_PUBLIC_SUPABASE_URL"),
                    os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
                )
                res = (
                    client.table("companies")
                    .select("ticker,name")
                    .in_("ticker", TICKERS)
                    .execute()
                )
                name_map = {
                    row.get("ticker"): row.get("name") for row in (res.data or [])
                }
                companies = [
                    {"ticker": t, "name": name_map.get(t) or t} for t in TICKERS
                ]
            except Exception:
                companies = [{"ticker": t, "name": t} for t in TICKERS]
        else:
            companies = [{"ticker": t, "name": t} for t in TICKERS]

        # Narrow scrape by overriding companies list
        scraper.companies = companies
        results = await scraper.run_batch_scraping()
        total = int(results.get("total_news", 0))
        return total


def main() -> None:
    if not os.getenv("NEXT_PUBLIC_SUPABASE_URL") or not os.getenv(
        "SUPABASE_SERVICE_ROLE_KEY"
    ):
        print(
            "❌ Env vars missing: NEXT_PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY"
        )
        sys.exit(1)

    total = asyncio.run(run())
    print(f"✅ Scrape complete. Inserted ~{total} news items (see logs for details)")
    print("Post-run checklist:")
    print(
        "- SELECT ticker, headline, published_at FROM company_news WHERE ticker IN ('ATW','IAM','BCP') ORDER BY published_at DESC LIMIT 20;"
    )


if __name__ == "__main__":
    main()
