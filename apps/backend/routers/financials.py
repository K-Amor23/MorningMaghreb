from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime

router = APIRouter()

@router.get("/")
async def get_financials():
    """Get financial data"""
    return {"message": "Financials endpoint - coming soon"} 