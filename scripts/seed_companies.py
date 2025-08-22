#!/usr/bin/env python3
"""
Seed/refresh core companies (ATW, IAM, BCP) into the 'companies' table and add a snapshot to 'market_data'.

Env required (no renames):
  - NEXT_PUBLIC_SUPABASE_URL
  - SUPABASE_SERVICE_ROLE_KEY

Idempotent: upsert on ticker, safe to re-run.
"""
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

try:
    from supabase import create_client
except Exception:
    print("❌ Missing dependency: pip install supabase")
    sys.exit(1)


COMPANIES: List[Dict[str, Any]] = [
    {
        "ticker": "ATW",
        "name": "Attijariwafa Bank",
        "sector": "Banking",
        "industry": "Financial Services",
        "market_cap": None,
        "current_price": None,
        "price_change_percent": None,
        "pe_ratio": None,
        "dividend_yield": None,
        "size_category": "Large Cap",
        "sector_group": "Financial Services",
        "exchange": "Casablanca Stock Exchange (BVC)",
        "country": "Morocco",
        "company_url": None,
        "ir_url": None,
        "base_url": None,
        "is_active": True,
    },
    {
        "ticker": "IAM",
        "name": "Maroc Telecom",
        "sector": "Telecommunications",
        "industry": "Telecom",
        "market_cap": None,
        "current_price": None,
        "price_change_percent": None,
        "pe_ratio": None,
        "dividend_yield": None,
        "size_category": "Large Cap",
        "sector_group": "Telecommunications",
        "exchange": "Casablanca Stock Exchange (BVC)",
        "country": "Morocco",
        "company_url": None,
        "ir_url": None,
        "base_url": None,
        "is_active": True,
    },
    {
        "ticker": "BCP",
        "name": "Banque Centrale Populaire",
        "sector": "Banking",
        "industry": "Financial Services",
        "market_cap": None,
        "current_price": None,
        "price_change_percent": None,
        "pe_ratio": None,
        "dividend_yield": None,
        "size_category": "Large Cap",
        "sector_group": "Financial Services",
        "exchange": "Casablanca Stock Exchange (BVC)",
        "country": "Morocco",
        "company_url": None,
        "ir_url": None,
        "base_url": None,
        "is_active": True,
    },
]


def main() -> None:
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print(
            "❌ Env vars missing: NEXT_PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY"
        )
        sys.exit(1)

    client = create_client(url, key)

    upserted = 0
    updated = 0
    failed = 0

    # Fetch existing tickers to count new vs updated
    try:
        existing = client.table("companies").select("ticker").execute()
        existing_tickers = {r["ticker"] for r in (existing.data or [])}
    except Exception:
        existing_tickers = set()

    for c in COMPANIES:
        payload = dict(c)
        payload["last_updated"] = datetime.utcnow().isoformat()
        payload["updated_at"] = datetime.utcnow().isoformat()
        try:
            client.table("companies").upsert(payload, on_conflict="ticker").execute()
            if c["ticker"] in existing_tickers:
                updated += 1
            else:
                upserted += 1

            # Best-effort market_data snapshot
            try:
                client.table("market_data").insert(
                    {
                        "ticker": c["ticker"],
                        "price": c.get("current_price"),
                        "volume": None,
                        "change_percent": c.get("price_change_percent"),
                        "timestamp": datetime.utcnow().isoformat(),
                        "source": "seed_companies",
                    }
                ).execute()
            except Exception:
                pass
        except Exception as e:
            failed += 1
            print(f"❌ Upsert failed for {c['ticker']}: {e}")

    print(f"✅ Seed complete. New: {upserted}, Updated: {updated}, Failed: {failed}")
    print("Post-run checklist:")
    print("- SELECT ticker, name FROM companies WHERE ticker IN ('ATW','IAM','BCP');")


if __name__ == "__main__":
    main()
