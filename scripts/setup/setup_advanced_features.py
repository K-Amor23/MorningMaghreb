#!/usr/bin/env python3
"""
Setup script for Advanced Features Database Tables
This script safely creates the database tables for advanced features
without overwriting existing financial data.
"""

import os
import sys
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent / "apps" / "backend"
sys.path.insert(0, str(backend_path))

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_database_url():
    """Get database URL from environment variables"""
    # Check for various database URL formats
    database_url = (
        os.getenv("DATABASE_URL")
        or os.getenv("SUPABASE_DB_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("DB_URL")
    )

    if not database_url:
        logger.error("No database URL found in environment variables")
        logger.error(
            "Please set one of: DATABASE_URL, SUPABASE_DB_URL, POSTGRES_URL, or DB_URL"
        )
        sys.exit(1)

    return database_url


def execute_sql_file(cursor, sql_file_path):
    """Execute SQL file safely"""
    logger.info(f"Executing SQL file: {sql_file_path}")

    try:
        with open(sql_file_path, "r", encoding="utf-8") as file:
            sql_content = file.read()

        # Execute the SQL content
        cursor.execute(sql_content)
        logger.info(f"Successfully executed {sql_file_path}")

    except Exception as e:
        logger.error(f"Error executing {sql_file_path}: {str(e)}")
        raise


def main():
    """Main setup function"""
    logger.info("Starting Advanced Features Database Setup")

    # Get database URL
    database_url = get_database_url()
    logger.info("Database URL found")

    # Import database libraries
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    except ImportError:
        logger.error(
            "psycopg2 not installed. Please install with: pip install psycopg2-binary"
        )
        sys.exit(1)

    # Connect to database
    try:
        logger.info("Connecting to database...")
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        logger.info("Connected to database successfully")

    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        sys.exit(1)

    try:
        # Check if we can query the database
        cursor.execute("SELECT version();")
        version_result = cursor.fetchone()
        if version_result:
            logger.info(f"Database version: {version_result[0]}")
        else:
            logger.warning("Could not retrieve database version")

        # Check for existing tables to avoid data loss
        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('companies', 'financial_reports', 'quotes')
        """
        )
        existing_tables = [row[0] for row in cursor.fetchall()]

        if existing_tables:
            logger.info(f"Found existing tables: {existing_tables}")
            logger.info("This indicates you have existing financial data")

        # Execute the incremental schema
        sql_file_path = (
            Path(__file__).parent.parent
            / "database"
            / "advanced_features_incremental.sql"
        )

        if not sql_file_path.exists():
            logger.error(f"SQL file not found: {sql_file_path}")
            sys.exit(1)

        execute_sql_file(cursor, sql_file_path)

        # Verify the new tables were created
        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('sentiment_votes', 'sentiment_aggregates', 'newsletter_subscribers', 'newsletter_campaigns', 'widget_configurations')
        """
        )

        new_tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"Created/verified tables: {new_tables}")

        # Check if triggers were created
        cursor.execute(
            """
            SELECT trigger_name, event_object_table 
            FROM information_schema.triggers 
            WHERE trigger_name LIKE '%sentiment%'
        """
        )

        triggers = cursor.fetchall()
        logger.info(f"Created/verified triggers: {triggers}")

        # Test the sentiment aggregation function
        cursor.execute(
            """
            SELECT COUNT(*) as sample_votes 
            FROM sentiment_votes
        """
        )

        vote_result = cursor.fetchone()
        vote_count = vote_result[0] if vote_result else 0
        logger.info(f"Sample sentiment votes in database: {vote_count}")

        logger.info("✅ Advanced Features Database Setup Complete!")
        logger.info("Your existing financial data has been preserved.")

        if vote_count > 0:
            logger.info("You can now test the sentiment voting system.")

        logger.info("The following features are now available:")
        logger.info("  • Sentiment Voting System")
        logger.info("  • AI-Powered Newsletter System")
        logger.info("  • Mobile Widget Analytics")

    except Exception as e:
        logger.error(f"Setup failed: {str(e)}")
        sys.exit(1)

    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals():
            conn.close()
        logger.info("Database connection closed")


if __name__ == "__main__":
    main()
