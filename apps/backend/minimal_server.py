from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Import only the inventory sync router
from routers.inventory_sync import router as inventory_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting minimal server for inventory sync testing...")
    yield
    logger.info("Shutting down minimal server...")

app = FastAPI(
    title="Inventory Sync API",
    description="Minimal API for Business Central to Zoho inventory synchronization",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include inventory sync router
app.include_router(inventory_router, tags=["inventory-sync"])

@app.get("/")
async def root():
    return {
        "message": "Inventory Sync API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "inventory_health": "/api/inventory/health",
            "test_bc": "/api/inventory/test-bc-connection",
            "test_zoho": "/api/inventory/test-zoho-connection",
            "sync": "/api/inventory/sync",
            "history": "/api/inventory/history",
            "logs": "/api/inventory/logs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "inventory_sync_api",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)