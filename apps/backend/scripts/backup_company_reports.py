import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from database.connection import get_db_session_context
from sqlalchemy import text


async def backup_company_reports() -> str:
    out_dir = Path("apps/backend/data/backups")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"company_reports_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

    rows_out = []
    async with get_db_session_context() as session:
        result = await session.execute(text("SELECT * FROM public.company_reports ORDER BY created_at DESC"))
        cols = result.keys()
        for row in result.fetchall():
            rec: Dict[str, Any] = {}
            for c, v in zip(cols, row):
                try:
                    rec[c] = v.isoformat() if hasattr(v, "isoformat") else v
                except Exception:
                    rec[c] = str(v)
            rows_out.append(rec)

    out_file.write_text(json.dumps(rows_out, indent=2), encoding="utf-8")
    return str(out_file)


if __name__ == "__main__":
    path = asyncio.run(backup_company_reports())
    print("Backup saved to:", path)



