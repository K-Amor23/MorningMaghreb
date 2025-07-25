import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from contextlib import asynccontextmanager

# Configure logging
logger = logging.getLogger(__name__)

# ============================================
# DATABASE CONFIGURATION
# ============================================

# Get database URL from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/casablanca_insights"
)

# Supabase specific configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# If using Supabase, construct the connection string
if SUPABASE_URL and SUPABASE_KEY:
    # Extract database host from Supabase URL
    # Example: https://xyz.supabase.co -> xyz.supabase.co
    host = SUPABASE_URL.replace("https://", "").replace("http://", "")
    DATABASE_URL = f"postgresql+asyncpg://postgres:{SUPABASE_KEY}@{host}:5432/postgres"

# ============================================
# ENGINE CONFIGURATION
# ============================================

# Create async engine with optimized settings
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    poolclass=StaticPool,  # Use static pool for better performance
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections every hour
    connect_args={
        "server_settings": {
            "application_name": "casablanca_insights_api",
            "timezone": "UTC"
        }
    }
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# ============================================
# SESSION MANAGEMENT
# ============================================

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

@asynccontextmanager
async def get_db_session_context():
    """Context manager for database sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

# ============================================
# CONNECTION TESTING
# ============================================

async def test_connection() -> bool:
    """Test database connection"""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute("SELECT 1")
            await result.fetchone()
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

async def get_database_info() -> dict:
    """Get database information"""
    try:
        async with AsyncSessionLocal() as session:
            # Get database version
            result = await session.execute("SELECT version()")
            version = await result.fetchone()
            
            # Get table count
            result = await session.execute("""
                SELECT COUNT(*) as table_count 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            table_count = await result.fetchone()
            
            # Get connection info
            result = await session.execute("SELECT current_database(), current_user")
            db_info = await result.fetchone()
            
            return {
                "version": version[0] if version else "Unknown",
                "table_count": table_count[0] if table_count else 0,
                "database": db_info[0] if db_info else "Unknown",
                "user": db_info[1] if db_info else "Unknown",
                "connection_status": "Connected"
            }
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {
            "version": "Unknown",
            "table_count": 0,
            "database": "Unknown",
            "user": "Unknown",
            "connection_status": f"Error: {str(e)}"
        }

# ============================================
# MIGRATION SUPPORT
# ============================================

async def run_migration(migration_sql: str) -> bool:
    """Run a SQL migration"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(migration_sql)
            await session.commit()
            logger.info("Migration executed successfully")
            return True
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

async def check_migration_status(version: str) -> bool:
    """Check if a migration has been applied"""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                "SELECT 1 FROM schema_migrations WHERE version = :version",
                {"version": version}
            )
            return result.fetchone() is not None
    except Exception as e:
        logger.error(f"Error checking migration status: {e}")
        return False

# ============================================
# HEALTH CHECK
# ============================================

async def health_check() -> dict:
    """Database health check"""
    try:
        # Test connection
        connection_ok = await test_connection()
        
        if not connection_ok:
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "error": "Cannot connect to database"
            }
        
        # Get database info
        db_info = await get_database_info()
        
        return {
            "status": "healthy" if connection_ok else "unhealthy",
            "database": db_info,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

# ============================================
# INITIALIZATION
# ============================================

async def init_database():
    """Initialize database connection and verify setup"""
    logger.info("Initializing database connection...")
    
    # Test connection
    if not await test_connection():
        logger.error("Failed to connect to database")
        return False
    
    # Get database info
    db_info = await get_database_info()
    logger.info(f"Connected to database: {db_info['database']}")
    logger.info(f"Database version: {db_info['version']}")
    logger.info(f"Tables found: {db_info['table_count']}")
    
    return True

async def close_database():
    """Close database connections"""
    logger.info("Closing database connections...")
    await engine.dispose()
    logger.info("Database connections closed") 