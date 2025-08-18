#!/usr/bin/env python3
import asyncio
from database.connection import get_db_session_context
from sqlalchemy import text

async def check_bcp():
    async with get_db_session_context() as session:
        result = await session.execute(text("SELECT ticker, name FROM companies WHERE ticker = 'BCP'"))
        rows = result.fetchall()
        print("BCP in DB:", rows)
        
        # Check first 20 companies
        result = await session.execute(text("SELECT ticker, name FROM companies ORDER BY ticker LIMIT 20"))
        rows = result.fetchall()
        print("First 20 companies:")
        for r in rows:
            print(f"  {r[0]}: {r[1]}")
        
        # Check if BCP is in first 20
        bcp_in_first_20 = any(r[0] == 'BCP' for r in rows)
        print(f"BCP in first 20: {bcp_in_first_20}")

if __name__ == "__main__":
    asyncio.run(check_bcp())
