from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routers (simplified for basic startup)
try:
    from routers import markets, financials, macro, portfolio, newsletter, chat, auth, economic_data, advanced_features, admin, companies, watchlists, alerts
    # Skip problematic routers for now
    # from routers import premium_api, exports, reports, translations, webhooks, currency, moderation, paper_trading, compliance
    # Skip ETL router temporarily due to missing dependencies
    # from routers import etl
    logger.info("Core routers imported successfully")
    all_routers_available = True
except ImportError as e:
    logger.warning(f"Some routers could not be imported: {e}")
    # Basic routers only
    from routers import markets, auth
    all_routers_available = False

# Database initialization (mock)
async def init_db():
    """Initialize database connection"""
    logger.info("Initializing database connection...")
    # Mock database initialization
    pass

async def close_db():
    """Close database connection"""
    logger.info("Closing database connection...")
    # Mock database cleanup
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    await init_db()
    yield
    await close_db()

app = FastAPI(
    title="Casablanca Insight API",
    description="Morocco-focused market research & analytics API with premium features",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://morningmaghreb.com", "https://www.morningmaghreb.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include core routers
app.include_router(markets.router, prefix="/api/markets", tags=["markets"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# Include new user feature routers
try:
    from routers import watchlists
    app.include_router(watchlists.router, prefix="/api/watchlists", tags=["watchlists"])
    logger.info("Watchlists router loaded successfully")
except ImportError as e:
    logger.warning(f"Watchlists router could not be loaded: {e}")

try:
    from routers import alerts
    app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
    logger.info("Alerts router loaded successfully")
except ImportError as e:
    logger.warning(f"Alerts router could not be loaded: {e}")

# Try to include advanced_features router (it has minimal dependencies)
try:
    from routers import advanced_features
    app.include_router(advanced_features.router, tags=["advanced-features"])
    logger.info("Advanced features router loaded successfully")
except ImportError as e:
    logger.warning(f"Advanced features router could not be loaded: {e}")

# Try to include companies router
try:
    from routers import companies
    app.include_router(companies.router, prefix="/api/companies", tags=["companies"])
    logger.info("Companies router loaded successfully")
except ImportError as e:
    logger.warning(f"Companies router could not be loaded: {e}")

# Include Week 3 routers
try:
    from routers import portfolio
    app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
    logger.info("Portfolio router loaded successfully")
except ImportError as e:
    logger.warning(f"Portfolio router could not be loaded: {e}")

try:
    from routers import notifications
    app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
    logger.info("Notifications router loaded successfully")
except ImportError as e:
    logger.warning(f"Notifications router could not be loaded: {e}")

try:
    from routers import risk_analytics
    app.include_router(risk_analytics.router, prefix="/api/risk-analytics", tags=["risk-analytics"])
    logger.info("Risk Analytics router loaded successfully")
except ImportError as e:
    logger.warning(f"Risk Analytics router could not be loaded: {e}")

if all_routers_available:
    # Include additional routers if available
    try:
        from routers import financials
        app.include_router(financials.router, prefix="/api/financials", tags=["financials"])
        logger.info("Financials router loaded successfully")
    except ImportError as e:
        logger.warning(f"Financials router could not be loaded: {e}")

    try:
        from routers import macro
        app.include_router(macro.router, prefix="/api/macro", tags=["macro"])
        logger.info("Macro router loaded successfully")
    except ImportError as e:
        logger.warning(f"Macro router could not be loaded: {e}")

    try:
        from routers import newsletter
        app.include_router(newsletter.router, prefix="/api/newsletter", tags=["newsletter"])
        logger.info("Newsletter router loaded successfully")
    except ImportError as e:
        logger.warning(f"Newsletter router could not be loaded: {e}")

    try:
        from routers import chat
        app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
        logger.info("Chat router loaded successfully")
    except ImportError as e:
        logger.warning(f"Chat router could not be loaded: {e}")

    try:
        from routers import economic_data
        app.include_router(economic_data.router, prefix="/api/economic-data", tags=["economic-data"])
        logger.info("Economic data router loaded successfully")
    except ImportError as e:
        logger.warning(f"Economic data router could not be loaded: {e}")

    try:
        from routers import admin
        app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
        logger.info("Admin router loaded successfully")
    except ImportError as e:
        logger.warning(f"Admin router could not be loaded: {e}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Casablanca Insights API",
        "version": "2.0.0",
        "description": "Morocco-focused market research & analytics API",
        "features": [
            "Real-time market data",
            "Portfolio management",
            "Risk analytics",
            "Push notifications",
            "Backtesting engine",
            "Advanced analytics"
        ],
        "endpoints": {
            "markets": "/api/markets",
            "companies": "/api/companies",
            "portfolio": "/api/portfolio",
            "notifications": "/api/notifications",
            "risk-analytics": "/api/risk-analytics",
            "watchlists": "/api/watchlists",
            "alerts": "/api/alerts"
        },
        "documentation": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-15T10:30:00Z",
        "version": "2.0.0",
        "features": {
            "portfolio_management": True,
            "backtesting_engine": True,
            "risk_analytics": True,
            "push_notifications": True,
            "real_time_data": True
        }
    }

# Protected endpoint example
@app.get("/protected")
async def protected_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Example protected endpoint"""
    try:
        # Verify token (mock implementation)
        user = await verify_token(credentials.credentials)
        return {
            "message": "Protected endpoint accessed successfully",
            "user_id": user.id,
            "subscription_tier": user.subscription_tier
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# Mock token verification (replace with actual implementation)
async def verify_token(token: str):
    """Verify JWT token and return user info"""
    # Mock implementation - replace with actual token verification
    class MockUser:
        def __init__(self):
            self.id = "mock_user_id"
            self.subscription_tier = "pro"
    
    return MockUser()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)