#!/usr/bin/env python3
"""
Setup script for ETF and Bond database schema
This script applies the schema and handles any migration needs
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def get_database_connection():
    """Get database connection from environment variables"""
    try:
        # Try to get connection from environment
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            return psycopg2.connect(database_url)

        # Fallback to individual environment variables
        conn_params = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
            "database": os.getenv("DB_NAME", "casablanca_insights"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", ""),
        }
        return psycopg2.connect(**conn_params)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def run_sql_file(conn, file_path):
    """Run a SQL file against the database"""
    try:
        with open(file_path, "r") as f:
            sql_content = f.read()

        with conn.cursor() as cursor:
            cursor.execute(sql_content)
            conn.commit()
            print(f"✅ Successfully executed {file_path}")

    except Exception as e:
        print(f"❌ Error executing {file_path}: {e}")
        conn.rollback()
        raise e


def check_table_exists(conn, table_name):
    """Check if a table exists in the database"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """,
                (table_name,),
            )
            return cursor.fetchone()[0]
    except Exception as e:
        print(f"Error checking if table {table_name} exists: {e}")
        return False


def migrate_existing_schema(conn):
    """Migrate existing schema if needed"""
    try:
        # Check if ETFs table exists and needs migration
        if check_table_exists(conn, "etfs"):
            print("🔄 Migrating existing ETFs table...")
            with conn.cursor() as cursor:
                cursor.execute("ALTER TABLE etfs ALTER COLUMN ticker TYPE VARCHAR(20);")
                conn.commit()
                print("✅ ETFs table migrated")

        # Check if Bonds table exists and needs migration
        if check_table_exists(conn, "bonds"):
            print("🔄 Migrating existing Bonds table...")
            with conn.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE bonds ALTER COLUMN ticker TYPE VARCHAR(20);"
                )
                conn.commit()
                print("✅ Bonds table migrated")

        # Check if yield_curve table exists and needs migration
        if check_table_exists(conn, "yield_curve"):
            print("🔄 Migrating existing yield_curve table...")
            with conn.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE yield_curve ALTER COLUMN benchmark_bond TYPE VARCHAR(25);"
                )
                conn.commit()
                print("✅ yield_curve table migrated")

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        raise e


def main():
    """Main setup function"""
    print("🚀 Setting up ETF and Bond database schema...")

    # Get database connection
    conn = get_database_connection()
    if not conn:
        print(
            "❌ Could not connect to database. Please check your environment variables."
        )
        sys.exit(1)

    try:
        # Set isolation level for DDL operations
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        # Migrate existing schema if needed
        migrate_existing_schema(conn)

        # Apply the main schema
        schema_file = os.path.join(
            os.path.dirname(__file__),
            "..",
            "apps",
            "backend",
            "database",
            "etf_bond_schema.sql",
        )

        if os.path.exists(schema_file):
            print(f"📄 Applying schema from {schema_file}...")
            run_sql_file(conn, schema_file)
        else:
            print(f"❌ Schema file not found: {schema_file}")
            sys.exit(1)

        print("✅ ETF and Bond schema setup completed successfully!")

        # Verify the setup
        print("\n🔍 Verifying setup...")
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    table_name,
                    column_name,
                    data_type,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name IN ('etfs', 'bonds', 'yield_curve', 'etf_data', 'bond_data', 'bond_issuance_calendar')
                AND column_name IN ('ticker', 'benchmark_bond')
                ORDER BY table_name, column_name;
            """
            )

            results = cursor.fetchall()
            print("📊 Current field configurations:")
            for row in results:
                print(f"  {row[0]}.{row[1]}: {row[2]}({row[3]})")

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
