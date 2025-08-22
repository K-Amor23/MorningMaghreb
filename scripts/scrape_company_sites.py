#!/usr/bin/env python3
"""
Lightweight company site crawler: fetch homepage/IR page and extract candidate news links.
Upserts found items into company_news.

Env:
  - NEXT_PUBLIC_SUPABASE_URL
  - SUPABASE_SERVICE_ROLE_KEY

Idempotent via upsert on (ticker, url, published_at=NULL default).
"""
import os
import sys
from urllib.parse import urljoin, urlparse
from typing import List, Dict
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
    from supabase import create_client
except Exception:
    print("❌ Missing dependency: pip install requests beautifulsoup4 supabase")
    sys.exit(1)


TICKERS = ["ATW", "IAM", "BCP"]
NEWS_KEYS = [
    "actualite",
    "actualités",
    "actu",
    "communiqué",
    "communiques",
    "communiqués",
    "presse",
    "press",
    "news",
    "investisseur",
    "investisseurs",
    "relations",
    "relations-investisseurs",
]


def get_client():
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError("Supabase env missing")
    return create_client(url, key)


def fetch_company_rows(client) -> List[Dict]:
    res = (
        client.table("companies")
        .select("ticker,company_url,ir_url,name")
        .in_("ticker", TICKERS)
        .execute()
    )
    return res.data or []


def extract_links(base_url: str) -> List[str]:
    try:
        r = requests.get(base_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
    except Exception:
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a.get("href")
        text = (a.get_text() or "").strip()
        if not href or not text:
            continue
        u = urljoin(base_url, href)
        if any(k in text.lower() or k in u.lower() for k in NEWS_KEYS):
            links.append(u)
    # de-dup by netloc+path
    seen = set()
    uniq = []
    for l in links:
        parsed = urlparse(l)
        key = (parsed.netloc, parsed.path)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(l)
    return uniq[:20]


def upsert_candidate(client, ticker: str, name: str, url: str):
    source = urlparse(url).netloc
    preview = f"Site update link for {name}"
    # Check if exists by ticker+url
    try:
        existing = (
            client.table("company_news")
            .select("id")
            .eq("ticker", ticker)
            .eq("url", url)
            .limit(1)
            .execute()
        )
        if existing.data:
            return
    except Exception:
        pass
    # Insert with a default published_at to satisfy unique(ticker,url,published_at)
    client.table("company_news").insert(
        {
            "ticker": ticker,
            "headline": preview,
            "source": source,
            "url": url,
            "published_at": datetime.utcnow().isoformat(),
            "content_preview": preview,
            "scraped_at": datetime.utcnow().isoformat(),
        }
    ).execute()


def main():
    client = get_client()
    rows = fetch_company_rows(client)
    total = 0
    for row in rows:
        ticker = row.get("ticker")
        name = row.get("name") or ticker
        for base in filter(None, [row.get("ir_url"), row.get("company_url")]):
            links = extract_links(base)
            for l in links:
                upsert_candidate(client, ticker, name, l)
                total += 1
    print(f"✅ Company site crawl complete. Upserted ~{total} candidate links.")
    print("Post-run checklist:")
    print(
        "- SELECT ticker, headline, url FROM company_news WHERE ticker IN ('ATW','IAM','BCP') ORDER BY scraped_at DESC LIMIT 20;"
    )


if __name__ == "__main__":
    main()
