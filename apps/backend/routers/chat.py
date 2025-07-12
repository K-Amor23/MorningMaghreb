from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime

router = APIRouter()

@router.get("/")
async def get_chat():
    """Get chat functionality"""
    return {"message": "Chat endpoint - coming soon"} 