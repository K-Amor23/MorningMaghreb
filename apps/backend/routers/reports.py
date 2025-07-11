from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["Custom Reports"])

# Request/Response Models
class ReportRequest(BaseModel):
    company_ticker: str
    report_type: str = "investment_summary"  # 'investment_summary', 'financial_analysis', 'risk_profile'
    include_charts: bool = True
    include_ai_summary: bool = True
    custom_sections: Optional[List[str]] = None

class ReportStatus(BaseModel):
    id: str
    status: str  # 'pending', 'generating', 'completed', 'failed'
    progress: int = 0
    estimated_completion: Optional[datetime] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None

class ReportTemplate(BaseModel):
    id: str
    name: str
    description: str
    sections: List[str]
    is_default: bool = False

# Mock database functions (replace with actual Supabase calls)
async def get_user_subscription_tier(user_id: str) -> str:
    """Get user's subscription tier"""
    # Mock implementation - replace with actual database query
    return "pro"  # or "institutional"

async def create_report_record(user_id: str, report_data: dict) -> str:
    """Create report record in database"""
    # Mock implementation - replace with actual database insert
    return "mock_report_id"

async def update_report_status(report_id: str, status: str, **kwargs):
    """Update report status"""
    # Mock implementation
    logger.info(f"Report {report_id} status updated to {status}")

async def get_company_data(ticker: str) -> Dict[str, Any]:
    """Get company data for report generation"""
    # Mock company data
    return {
        "ticker": ticker,
        "name": f"Mock Company {ticker}",
        "sector": "Banking" if ticker in ["ATW", "BCP", "BMCE"] else "Telecommunications",
        "market_cap": 100000000000 + hash(ticker) % 50000000000,
        "current_price": 150.0 + hash(ticker) % 50,
        "price_change": (hash(ticker) % 20 - 10) / 100,
        "volume": 1000000 + hash(ticker) % 500000
    }

async def get_financial_data(ticker: str) -> Dict[str, Any]:
    """Get financial data for report generation"""
    # Mock financial data
    return {
        "revenue": 50000000000 + hash(ticker) % 20000000000,
        "net_income": 8000000000 + hash(ticker) % 4000000000,
        "total_assets": 200000000000 + hash(ticker) % 100000000000,
        "total_liabilities": 120000000000 + hash(ticker) % 60000000000,
        "roe": 15.0 + hash(ticker) % 10,
        "roa": 8.0 + hash(ticker) % 5,
        "debt_to_equity": 0.8 + (hash(ticker) % 10) / 10,
        "pe_ratio": 12.0 + hash(ticker) % 8,
        "pb_ratio": 1.2 + (hash(ticker) % 10) / 10,
        "dividend_yield": 3.5 + (hash(ticker) % 5) / 10
    }

async def get_ai_summary(ticker: str) -> str:
    """Get AI-generated summary for the company"""
    # Mock AI summary
    summaries = [
        f"{ticker} demonstrates strong financial performance with consistent revenue growth and solid profitability metrics. The company maintains a healthy balance sheet with manageable debt levels and attractive valuation ratios.",
        f"{ticker} shows promising fundamentals with improving operational efficiency and market positioning. Recent quarterly results indicate positive momentum, though investors should monitor sector-specific risks.",
        f"{ticker} presents a balanced investment opportunity with stable cash flows and reasonable valuation. The company's strategic initiatives and market share position it well for future growth."
    ]
    return summaries[hash(ticker) % len(summaries)]

async def get_risk_profile(ticker: str) -> Dict[str, Any]:
    """Get risk profile for the company"""
    # Mock risk profile
    return {
        "overall_risk": "Medium",
        "market_risk": "Medium",
        "credit_risk": "Low",
        "liquidity_risk": "Low",
        "operational_risk": "Medium",
        "risk_factors": [
            "Sector concentration risk",
            "Regulatory changes",
            "Economic cycle sensitivity",
            "Currency fluctuations"
        ]
    }

# Authentication dependency (mock)
async def get_current_user() -> dict:
    """Get current authenticated user"""
    return {"id": "mock_user_id", "subscription_tier": "pro"}

# Report Management
@router.post("/", response_model=ReportStatus)
async def create_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Create a new custom report"""
    try:
        # Check subscription tier
        subscription_tier = await get_user_subscription_tier(user["id"])
        if subscription_tier not in ["pro", "institutional"]:
            raise HTTPException(status_code=403, detail="Pro or Institutional tier required for custom reports")
        
        # Validate report type
        valid_types = ["investment_summary", "financial_analysis", "risk_profile"]
        if request.report_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid report type. Must be one of: {valid_types}")
        
        # Create report record
        report_id = await create_report_record(user["id"], {
            "company_ticker": request.company_ticker,
            "report_type": request.report_type,
            "include_charts": request.include_charts,
            "include_ai_summary": request.include_ai_summary,
            "custom_sections": request.custom_sections or []
        })
        
        # Add background task for processing
        background_tasks.add_task(generate_report, report_id, request, user["id"])
        
        return ReportStatus(
            id=report_id,
            status="pending",
            progress=0,
            estimated_completion=datetime.utcnow() + timedelta(minutes=3)
        )
        
    except Exception as e:
        logger.error(f"Error creating report: {e}")
        raise HTTPException(status_code=500, detail="Failed to create report")

@router.get("/{report_id}", response_model=ReportStatus)
async def get_report_status(
    report_id: str,
    user: dict = Depends(get_current_user)
):
    """Get report status and download URL"""
    try:
        # Mock report status (replace with actual database query)
        report_status = {
            "id": report_id,
            "status": "completed",
            "progress": 100,
            "download_url": f"/api/reports/{report_id}/download",
            "estimated_completion": None
        }
        
        return ReportStatus(**report_status)
        
    except Exception as e:
        logger.error(f"Error getting report status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get report status")

@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    user: dict = Depends(get_current_user)
):
    """Download the generated report"""
    try:
        # Mock PDF generation (replace with actual PDF generation)
        if report_id == "mock_report_id":
            # For now, return a JSON file with report data
            # In production, this would generate an actual PDF
            report_data = await generate_mock_report_data()
            
            import io
            output = io.BytesIO()
            output.write(json.dumps(report_data, indent=2, default=str).encode())
            output.seek(0)
            
            return FileResponse(
                output,
                media_type="application/json",
                filename=f"investment_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            )
        else:
            raise HTTPException(status_code=404, detail="Report not found")
            
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        raise HTTPException(status_code=500, detail="Failed to download report")

@router.get("/", response_model=List[Dict[str, Any]])
async def list_reports(
    user: dict = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List user's report history"""
    try:
        # Mock report history (replace with actual database query)
        reports = [
            {
                "id": "report_1",
                "company_ticker": "ATW",
                "report_type": "investment_summary",
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(days=1),
                "download_count": 1,
                "file_size_bytes": 245760
            },
            {
                "id": "report_2",
                "company_ticker": "IAM",
                "report_type": "financial_analysis",
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(days=3),
                "download_count": 2,
                "file_size_bytes": 512000
            },
            {
                "id": "report_3",
                "company_ticker": "BCP",
                "report_type": "risk_profile",
                "status": "failed",
                "created_at": datetime.utcnow() - timedelta(days=5),
                "download_count": 0,
                "file_size_bytes": None
            }
        ]
        
        return reports[offset:offset + limit]
        
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to list reports")

# Report Templates
@router.get("/templates", response_model=List[ReportTemplate])
async def get_report_templates(user: dict = Depends(get_current_user)):
    """Get available report templates"""
    try:
        templates = [
            ReportTemplate(
                id="investment_summary",
                name="Investment Summary",
                description="1-page overview with key metrics, AI summary, and risk profile",
                sections=["company_overview", "financial_highlights", "ai_summary", "risk_assessment"],
                is_default=True
            ),
            ReportTemplate(
                id="financial_analysis",
                name="Financial Analysis",
                description="Detailed financial analysis with ratios and trends",
                sections=["income_statement", "balance_sheet", "cash_flow", "ratios_analysis", "trends"],
                is_default=False
            ),
            ReportTemplate(
                id="risk_profile",
                name="Risk Profile",
                description="Comprehensive risk assessment and mitigation strategies",
                sections=["risk_overview", "risk_factors", "stress_testing", "mitigation_strategies"],
                is_default=False
            )
        ]
        
        return templates
        
    except Exception as e:
        logger.error(f"Error getting report templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get report templates")

# Quick Report Generation
@router.post("/quick/{ticker}")
async def quick_report(
    ticker: str,
    report_type: str = Query("investment_summary", description="Report type"),
    user: dict = Depends(get_current_user)
):
    """Generate a quick report for immediate download"""
    try:
        # Check subscription tier
        subscription_tier = await get_user_subscription_tier(user["id"])
        if subscription_tier not in ["pro", "institutional"]:
            raise HTTPException(status_code=403, detail="Pro or Institutional tier required")
        
        # Generate report data
        report_data = await generate_mock_report_data(ticker, report_type)
        
        # Create file in memory
        import io
        output = io.BytesIO()
        output.write(json.dumps(report_data, indent=2, default=str).encode())
        output.seek(0)
        
        return FileResponse(
            output,
            media_type="application/json",
            filename=f"{ticker}_{report_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
    except Exception as e:
        logger.error(f"Error generating quick report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate quick report")

# Background task for report generation
async def generate_report(report_id: str, request: ReportRequest, user_id: str):
    """Generate report in background"""
    try:
        # Update status to generating
        await update_report_status(report_id, "generating", progress=25)
        
        # Simulate processing time
        import asyncio
        await asyncio.sleep(1)
        
        # Update progress
        await update_report_status(report_id, "generating", progress=75)
        
        # Simulate more processing
        await asyncio.sleep(1)
        
        # Mark as completed
        await update_report_status(report_id, "completed", progress=100)
        
        logger.info(f"Report {report_id} generated successfully")
        
    except Exception as e:
        logger.error(f"Error generating report {report_id}: {e}")
        await update_report_status(report_id, "failed", error_message=str(e))

# Helper function to generate mock report data
async def generate_mock_report_data(ticker: str = "ATW", report_type: str = "investment_summary") -> Dict[str, Any]:
    """Generate mock report data"""
    company_data = await get_company_data(ticker)
    financial_data = await get_financial_data(ticker)
    ai_summary = await get_ai_summary(ticker)
    risk_profile = await get_risk_profile(ticker)
    
    report_data = {
        "report_metadata": {
            "ticker": ticker,
            "report_type": report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "version": "1.0"
        },
        "company_overview": {
            "name": company_data["name"],
            "sector": company_data["sector"],
            "market_cap": company_data["market_cap"],
            "current_price": company_data["current_price"],
            "price_change": company_data["price_change"],
            "volume": company_data["volume"]
        },
        "financial_highlights": {
            "revenue": financial_data["revenue"],
            "net_income": financial_data["net_income"],
            "roe": financial_data["roe"],
            "pe_ratio": financial_data["pe_ratio"],
            "debt_to_equity": financial_data["debt_to_equity"],
            "dividend_yield": financial_data["dividend_yield"]
        },
        "ai_summary": ai_summary,
        "risk_assessment": risk_profile,
        "investment_recommendation": {
            "rating": "Hold",
            "target_price": company_data["current_price"] * (1 + (hash(ticker) % 20 - 10) / 100),
            "time_horizon": "12 months",
            "confidence_level": "Medium"
        }
    }
    
    return report_data 