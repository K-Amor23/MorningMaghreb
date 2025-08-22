#!/usr/bin/env python3
"""
Send a test newsletter via Resend using NEWSLETTER_FROM and NEWSLETTER_TO_TEST.

Env required:
  - RESEND_API_KEY
  - NEWSLETTER_FROM (e.g., "Morning Maghreb <newsletter@morningmaghreb.com>")
  - NEWSLETTER_TO_TEST (recipient email)

Loads latest newsletter_summaries and sends the most recent entry.
"""
import os
import sys
from typing import Optional

try:
    import resend
except Exception:
    print("❌ Missing dependency: pip install resend")
    sys.exit(1)

try:
    from supabase import create_client
except Exception:
    print("❌ Missing dependency: pip install supabase")
    sys.exit(1)


def fetch_latest_summary() -> Optional[dict]:
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return None
    client = create_client(url, key)
    res = (
        client.table("newsletter_summaries")
        .select("*")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    rows = res.data or []
    return rows[0] if rows else None


def markdown_to_html(md: str) -> str:
    # Minimal conversion: wrap in <pre> for safety. Replace with proper renderer if desired.
    from html import escape

    return f"<pre style='font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;'>{escape(md)}</pre>"


def main() -> None:
    api_key = os.getenv("RESEND_API_KEY")
    sender = os.getenv("NEWSLETTER_FROM")
    to = os.getenv("NEWSLETTER_TO_TEST")
    if not api_key or not sender or not to:
        print(
            "❌ Env vars missing: RESEND_API_KEY, NEWSLETTER_FROM, NEWSLETTER_TO_TEST"
        )
        sys.exit(1)

    summary = fetch_latest_summary()
    if not summary:
        print("❌ No newsletter_summaries found. Generate one first.")
        sys.exit(1)

    subject = summary.get("subject", "Morning Maghreb Weekly Recap")
    content = summary.get("content", "(no content)")
    html = markdown_to_html(content)

    resend.api_key = api_key
    resend.Emails.send(
        {
            "from": sender,
            "to": [to],
            "subject": subject,
            "html": html,
        }
    )

    print(f"✅ Test newsletter sent to {to}")
    print("Post-run checklist:")
    print("- Check inbox of NEWSLETTER_TO_TEST for the email.")


if __name__ == "__main__":
    main()
