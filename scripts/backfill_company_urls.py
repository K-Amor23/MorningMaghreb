#!/usr/bin/env python3
"""
Backfill company_url and ir_url for ATW/IAM/BCP. Idempotent upserts.
"""
import os
import sys

try:
    from supabase import create_client
except Exception:
    print("❌ Missing dependency: pip install supabase")
    sys.exit(1)

MAP = {
    "ATW": {
        "company_url": "https://www.attijariwafabank.com/",
        "ir_url": "https://www.attijariwafabank.com/fr/investisseurs",
    },
    "IAM": {
        "company_url": "https://www.iam.ma/",
        "ir_url": "https://www.iam.ma/Investisseurs/Pages/default.aspx",
    },
    "BCP": {
        "company_url": "https://www.groupebcp.com/",
        "ir_url": "https://www.groupebcp.com/FR/groupe/finance/Pages/finance.aspx",
    },
}


def main():
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print(
            "❌ Env vars missing: NEXT_PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY"
        )
        sys.exit(1)
    client = create_client(url, key)
    for t, vals in MAP.items():
        client.table("companies").update(
            {
                "company_url": vals["company_url"],
                "ir_url": vals["ir_url"],
            }
        ).eq("ticker", t).execute()
    print("✅ Backfill complete for ATW/IAM/BCP company_url/ir_url")


if __name__ == "__main__":
    main()
