#!/usr/bin/env python3
"""
Generate weekly AI summary from recent company_news and store in newsletter_summaries (Markdown).

Env required:
  - NEXT_PUBLIC_SUPABASE_URL
  - SUPABASE_SERVICE_ROLE_KEY
  - OPENAI_API_KEY

Idempotent per (summary_date, language).
"""
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any

try:
    from supabase import create_client
except Exception:
    print("❌ Missing dependency: pip install supabase")
    sys.exit(1)

try:
    from openai import OpenAI
except Exception:
    print("❌ Missing dependency: pip install openai")
    sys.exit(1)


def fetch_recent_news(client, tickers: List[str], days: int = 7) -> List[Dict[str, Any]]:
    since = (datetime.utcnow() - timedelta(days=days)).date().isoformat()
    rows: List[Dict[str, Any]] = []
    for t in tickers:
        try:
            res = client.table("company_news").select("ticker,headline,source,published_at").gte("published_at", since).eq("ticker", t).order("published_at", desc=True).limit(50).execute()
            rows.extend(res.data or [])
        except Exception:
            pass
    return rows


def build_markdown_summary(items: List[Dict[str, Any]]) -> str:
    if not items:
        return "# Weekly Moroccan Business Recap\n\n_No major headlines available this week._\n"
    lines = ["# Weekly Moroccan Business Recap", ""]
    # Group a few highlights
    for it in items[:10]:
        ts = (it.get("published_at") or "")[:10]
        lines.append(f"- [{ts}] {it.get('ticker')}: {it.get('headline')} ({it.get('source')})")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    oai = os.getenv("OPENAI_API_KEY")
    if not url or not key or not oai:
        print("❌ Env vars missing: NEXT_PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, OPENAI_API_KEY")
        sys.exit(1)

    client = create_client(url, key)
    tickers = ["ATW", "IAM", "BCP"]
    news = fetch_recent_news(client, tickers, days=7)

    # Prepare context for OpenAI
    head_blob = "\n".join([f"- {n.get('ticker')}: {n.get('headline')} ({n.get('source')})" for n in news[:50]])
    md_seed = build_markdown_summary(news)

    # Generate with OpenAI (constrained, factual)
    ai = OpenAI(api_key=oai)
    system = (
        "You are a careful financial editor for Moroccan markets. "
        "Write a concise weekly recap in Markdown: macro highlights, sectors, 3-5 notable company items. "
        "Neutral tone, factual, <= 250 words."
    )
    user = f"Recent headlines (subset):\n{head_blob}\n\nDraft base:\n{md_seed}"

    try:
        resp = ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.4,
            max_tokens=600,
        )
        content = resp.choices[0].message.content or md_seed
    except Exception:
        content = md_seed

    subject = f"Moroccan Markets Weekly Recap — {datetime.utcnow().date().isoformat()}"
    summary_date = datetime.utcnow().date().isoformat()

    # Upsert Markdown summary
    client.table("newsletter_summaries").upsert({
        "summary_date": summary_date,
        "language": "en",
        "subject": subject,
        "content": content,
    }, on_conflict="summary_date,language").execute()

    print("✅ Weekly summary created (Markdown)")
    print("Post-run checklist:")
    print("- SELECT subject, created_at FROM newsletter_summaries ORDER BY created_at DESC LIMIT 1;")


if __name__ == "__main__":
    main()






