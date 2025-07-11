from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging

# Import routers
from routers import markets, financials, macro, portfolio, newsletter, chat, auth, etl, economic_data, advanced_features
from routers import premium_api, exports, reports, translations, webhooks, currency, moderation, paper_trading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    allow_origins=["http://localhost:3000", "https://casablanca-insight.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(markets.router, prefix="/api/markets", tags=["markets"])
app.include_router(financials.router, prefix="/api/financials", tags=["financials"])
app.include_router(macro.router, prefix="/api/macro", tags=["macro"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(newsletter.router, prefix="/api/newsletter", tags=["newsletter"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(etl.router, prefix="/api/etl", tags=["etl"])
app.include_router(economic_data.router, prefix="/api/economic-data", tags=["economic-data"])
app.include_router(advanced_features.router, prefix="/api/advanced", tags=["advanced-features"])

# Premium feature routers
app.include_router(premium_api.router, prefix="/api/premium", tags=["premium-api"])
app.include_router(exports.router, prefix="/api/exports", tags=["data-exports"])
app.include_router(reports.router, prefix="/api/reports", tags=["custom-reports"])
app.include_router(translations.router, prefix="/api/translations", tags=["multilingual"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhook-integrations"])

# New feature routers
app.include_router(currency.router, prefix="/api/currency", tags=["currency"])
app.include_router(moderation.router, prefix="/api/moderation", tags=["moderation"])
app.include_router(paper_trading.router, prefix="/api", tags=["paper-trading"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Casablanca Insight API",
        "version": "2.0.0",
        "features": {
            "core": ["market_data", "financials", "macro", "portfolio", "newsletter", "chat"],
            "advanced": ["company_comparison", "earnings_calendar", "dividend_tracker", "custom_screens"],
            "premium": ["api_access", "data_exports", "custom_reports", "multilingual", "webhooks"]
        },
        "subscription_tiers": {
            "free": "Basic market data and limited features",
            "pro": "Advanced features, exports, custom reports",
            "institutional": "API access, webhooks, priority support"
        },
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Protected endpoint example
@app.get("/protected")
async def protected_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user = await verify_token(credentials.credentials)
    return {
        "message": "Access granted",
        "user_id": user.id,
        "subscription_tier": user.subscription_tier
    }

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