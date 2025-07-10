from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from routers import markets, financials, macro, portfolio, newsletter, chat, auth
from database import init_db
from utils.auth import verify_token

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database
    await init_db()
    yield
    # Cleanup if needed

app = FastAPI(
    title="Casablanca Insight API",
    description="Morocco-focused market research & analytics API",
    version="1.0.0",
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

@app.get("/")
async def root():
    return {
        "message": "Welcome to Casablanca Insight API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
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
        "email": user.email
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )