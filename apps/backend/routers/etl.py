from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime

router = APIRouter()

@router.get("/")
async def get_etl():
    """Get ETL functionality"""
    return {"message": "ETL endpoint - coming soon"} 