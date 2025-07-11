from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import io
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/exports", tags=["Data Exports"])

# Request/Response Models
class ExportRequest(BaseModel):
    export_type: str  # 'financials', 'macro', 'portfolio', 'custom'
    file_format: str = "csv"  # 'csv', 'xlsx', 'json'
    filters: Dict[str, Any] = {}
    include_metadata: bool = True

class ExportStatus(BaseModel):
    id: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    progress: int = 0
    estimated_completion: Optional[datetime] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None

# Mock database functions (replace with actual Supabase calls)
async def get_user_subscription_tier(user_id: str) -> str:
    """Get user's subscription tier"""
    # Mock implementation - replace with actual database query
    return "pro"  # or "institutional"

async def create_export_record(user_id: str, export_data: dict) -> str:
    """Create export record in database"""
    # Mock implementation - replace with actual database insert
    return "mock_export_id"

async def update_export_status(export_id: str, status: str, **kwargs):
    """Update export status"""
    # Mock implementation
    logger.info(f"Export {export_id} status updated to {status}")

# Authentication dependency (mock)
async def get_current_user() -> dict:
    """Get current authenticated user"""
    return {"id": "mock_user_id", "subscription_tier": "pro"}

# Export Management
@router.post("/", response_model=ExportStatus)
async def create_export(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Create a new data export"""
    try:
        # Check subscription tier
        subscription_tier = await get_user_subscription_tier(user["id"])
        if subscription_tier not in ["pro", "institutional"]:
            raise HTTPException(status_code=403, detail="Pro or Institutional tier required for exports")
        
        # Validate export type
        valid_types = ["financials", "macro", "portfolio", "custom"]
        if request.export_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid export type. Must be one of: {valid_types}")
        
        # Validate file format
        valid_formats = ["csv", "xlsx", "json"]
        if request.file_format not in valid_formats:
            raise HTTPException(status_code=400, detail=f"Invalid file format. Must be one of: {valid_formats}")
        
        # Create export record
        export_id = await create_export_record(user["id"], {
            "export_type": request.export_type,
            "file_format": request.file_format,
            "filters": request.filters,
            "include_metadata": request.include_metadata
        })
        
        # Add background task for processing
        background_tasks.add_task(process_export, export_id, request, user["id"])
        
        return ExportStatus(
            id=export_id,
            status="pending",
            progress=0,
            estimated_completion=datetime.utcnow() + timedelta(minutes=5)
        )
        
    except Exception as e:
        logger.error(f"Error creating export: {e}")
        raise HTTPException(status_code=500, detail="Failed to create export")

@router.get("/{export_id}", response_model=ExportStatus)
async def get_export_status(
    export_id: str,
    user: dict = Depends(get_current_user)
):
    """Get export status and download URL"""
    try:
        # Mock export status (replace with actual database query)
        export_status = {
            "id": export_id,
            "status": "completed",
            "progress": 100,
            "download_url": f"/api/exports/{export_id}/download",
            "estimated_completion": None
        }
        
        return ExportStatus(**export_status)
        
    except Exception as e:
        logger.error(f"Error getting export status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get export status")

@router.get("/{export_id}/download")
async def download_export(
    export_id: str,
    user: dict = Depends(get_current_user)
):
    """Download the exported file"""
    try:
        # Mock file generation (replace with actual file retrieval)
        if export_id == "mock_export_id":
            # Generate mock financial data
            data = generate_mock_financial_data()
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Create file in memory
            output = io.BytesIO()
            
            # Write based on format (default to CSV)
            df.to_csv(output, index=False)
            output.seek(0)
            
            return FileResponse(
                output,
                media_type="text/csv",
                filename=f"financial_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            )
        else:
            raise HTTPException(status_code=404, detail="Export not found")
            
    except Exception as e:
        logger.error(f"Error downloading export: {e}")
        raise HTTPException(status_code=500, detail="Failed to download export")

@router.get("/", response_model=List[Dict[str, Any]])
async def list_exports(
    user: dict = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List user's export history"""
    try:
        # Mock export history (replace with actual database query)
        exports = [
            {
                "id": "export_1",
                "export_type": "financials",
                "file_format": "csv",
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(days=1),
                "download_count": 1,
                "file_size_bytes": 245760
            },
            {
                "id": "export_2",
                "export_type": "macro",
                "file_format": "xlsx",
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(days=3),
                "download_count": 2,
                "file_size_bytes": 512000
            },
            {
                "id": "export_3",
                "export_type": "portfolio",
                "file_format": "json",
                "status": "failed",
                "created_at": datetime.utcnow() - timedelta(days=5),
                "download_count": 0,
                "file_size_bytes": None
            }
        ]
        
        return exports[offset:offset + limit]
        
    except Exception as e:
        logger.error(f"Error listing exports: {e}")
        raise HTTPException(status_code=500, detail="Failed to list exports")

# Background task for processing exports
async def process_export(export_id: str, request: ExportRequest, user_id: str):
    """Process export in background"""
    try:
        # Update status to processing
        await update_export_status(export_id, "processing", progress=25)
        
        # Simulate processing time
        import asyncio
        await asyncio.sleep(2)
        
        # Update progress
        await update_export_status(export_id, "processing", progress=75)
        
        # Simulate more processing
        await asyncio.sleep(1)
        
        # Mark as completed
        await update_export_status(export_id, "completed", progress=100)
        
        logger.info(f"Export {export_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error processing export {export_id}: {e}")
        await update_export_status(export_id, "failed", error_message=str(e))

# Helper function to generate mock financial data
def generate_mock_financial_data() -> List[Dict[str, Any]]:
    """Generate mock financial data for export"""
    companies = ["ATW", "IAM", "BCP", "BMCE", "WAA"]
    periods = ["2024-Q1", "2024-Q2", "2024-Q3", "2023-Q4", "2023-Q3"]
    
    data = []
    for company in companies:
        for period in periods:
            # Generate realistic mock data
            revenue = 50000000000 + hash(f"{company}{period}") % 20000000000
            net_income = revenue * (0.15 + (hash(f"{company}{period}") % 10) / 100)
            assets = revenue * (2.5 + (hash(f"{company}{period}") % 10) / 10)
            liabilities = assets * (0.6 + (hash(f"{company}{period}") % 10) / 100)
            
            data.append({
                "ticker": company,
                "period": period,
                "revenue": revenue,
                "net_income": net_income,
                "total_assets": assets,
                "total_liabilities": liabilities,
                "roe": (net_income / (assets - liabilities)) * 100,
                "debt_to_equity": liabilities / (assets - liabilities),
                "current_ratio": (assets * 0.3) / (liabilities * 0.4),
                "pe_ratio": 12.0 + hash(f"{company}{period}") % 8,
                "market_cap": revenue * (1.2 + (hash(f"{company}{period}") % 10) / 100)
            })
    
    return data

# Quick Export Endpoints (for common use cases)
@router.post("/financials/quick")
async def quick_financial_export(
    tickers: List[str] = Query(..., description="List of tickers to export"),
    period: str = Query("2024-Q3", description="Financial period"),
    format: str = Query("csv", description="Export format"),
    user: dict = Depends(get_current_user)
):
    """Quick export of financial data for specified companies"""
    try:
        # Check subscription tier
        subscription_tier = await get_user_subscription_tier(user["id"])
        if subscription_tier not in ["pro", "institutional"]:
            raise HTTPException(status_code=403, detail="Pro or Institutional tier required")
        
        # Generate data
        data = []
        for ticker in tickers:
            # Mock financial data
            revenue = 50000000000 + hash(f"{ticker}{period}") % 20000000000
            net_income = revenue * (0.15 + (hash(f"{ticker}{period}") % 10) / 100)
            
            data.append({
                "ticker": ticker,
                "period": period,
                "revenue": revenue,
                "net_income": net_income,
                "roe": 15.0 + hash(ticker) % 10,
                "pe_ratio": 12.0 + hash(ticker) % 8,
                "debt_to_equity": 0.8 + (hash(ticker) % 10) / 10
            })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Create file in memory
        output = io.BytesIO()
        
        if format.lower() == "xlsx":
            df.to_excel(output, index=False)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"financials_{period}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
        else:
            df.to_csv(output, index=False)
            media_type = "text/csv"
            filename = f"financials_{period}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        output.seek(0)
        
        return FileResponse(
            output,
            media_type=media_type,
            filename=filename
        )
        
    except Exception as e:
        logger.error(f"Error in quick financial export: {e}")
        raise HTTPException(status_code=500, detail="Failed to export financial data")

@router.post("/macro/quick")
async def quick_macro_export(
    series_codes: List[str] = Query(..., description="List of macro series codes"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    format: str = Query("csv", description="Export format"),
    user: dict = Depends(get_current_user)
):
    """Quick export of macroeconomic time-series data"""
    try:
        # Check subscription tier
        subscription_tier = await get_user_subscription_tier(user["id"])
        if subscription_tier not in ["pro", "institutional"]:
            raise HTTPException(status_code=403, detail="Pro or Institutional tier required")
        
        # Generate time-series data
        data = []
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        for series_code in series_codes:
            current = start
            while current <= end:
                # Generate mock values
                if "cpi" in series_code.lower():
                    value = 120.0 + (hash(f"{series_code}{current}") % 20 - 10)
                elif "gdp" in series_code.lower():
                    value = 1200000000000 + (hash(f"{series_code}{current}") % 100000000000 - 50000000000)
                else:
                    value = 100.0 + (hash(f"{series_code}{current}") % 20 - 10)
                
                data.append({
                    "series_code": series_code,
                    "date": current.strftime("%Y-%m-%d"),
                    "value": value,
                    "change": (hash(f"{series_code}{current}") % 20 - 10) / 100
                })
                
                current += timedelta(days=30)  # Monthly frequency
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Create file in memory
        output = io.BytesIO()
        
        if format.lower() == "xlsx":
            df.to_excel(output, index=False)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"macro_data_{start_date}_to_{end_date}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
        else:
            df.to_csv(output, index=False)
            media_type = "text/csv"
            filename = f"macro_data_{start_date}_to_{end_date}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        output.seek(0)
        
        return FileResponse(
            output,
            media_type=media_type,
            filename=filename
        )
        
    except Exception as e:
        logger.error(f"Error in quick macro export: {e}")
        raise HTTPException(status_code=500, detail="Failed to export macro data") 