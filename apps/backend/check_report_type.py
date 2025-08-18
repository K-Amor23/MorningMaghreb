#!/usr/bin/env python3
import asyncio
from database.connection import get_db_session_context
from sqlalchemy import text

async def check_report_type():
    async with get_db_session_context() as session:
        # Check the report_type column definition
        result = await session.execute(text("""
            SELECT column_name, data_type, udt_name, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'company_reports' AND column_name = 'report_type'
        """))
        rows = result.fetchall()
        print("report_type column info:")
        for row in rows:
            print(f"  {row}")
        
        # Check if it's an enum and what values it accepts
        result = await session.execute(text("""
            SELECT typname, enumlabel 
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid 
            WHERE t.typname = 'report_type_enum'
            ORDER BY e.enumsortorder
        """))
        enum_values = result.fetchall()
        if enum_values:
            print(f"\nEnum values for report_type_enum:")
            for row in enum_values:
                print(f"  {row}")
        else:
            print(f"\nNo enum found for report_type_enum")
            
        # Check the actual table structure
        result = await session.execute(text("""
            SELECT column_name, data_type, udt_name, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'company_reports'
            ORDER BY ordinal_position
        """))
        print(f"\nAll columns in company_reports:")
        for row in result.fetchall():
            print(f"  {row}")

if __name__ == "__main__":
    asyncio.run(check_report_type())

