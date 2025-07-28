"""
Admin Dashboard Router
Handles user analytics, data ingestion monitoring, and system performance metrics
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from database.connection import get_db
from services.admin_dashboard_service import AdminDashboardService
from utils.auth import get_current_user

router = APIRouter()
security = HTTPBearer()

# ============================================================================
# USER ANALYTICS
# ============================================================================

@router.post("/analytics/track")
async def track_user_activity(
    session_id: str,
    page_visited: str,
    action_type: str,
    action_data: Optional[Dict[str, Any]] = None,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
    session_duration: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track user activity for analytics"""
    dashboard_service = AdminDashboardService(db)
    return await dashboard_service.track_user_activity(
        current_user["id"],
        session_id,
        page_visited,
        action_type,
        action_data,
        user_agent,
        ip_address,
        session_duration
    )

@router.get("/analytics/engagement")
async def get_user_engagement_metrics(
    days: int = Query(30, ge=1, le=365),
    user_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user engagement metrics (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    dashboard_service = AdminDashboardService(db)
    return await dashboard_service.get_user_engagement_metrics(days, user_id)

@router.get("/analytics/retention")
async def get_user_retention_analysis(
    days: int = Query(90, ge=30, le=365),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze user retention patterns (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    dashboard_service = AdminDashboardService(db)
    return await dashboard_service.get_user_retention_analysis(days)

@router.get("/analytics/top-users")
async def get_top_performing_users(
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get top performing users (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    dashboard_service = AdminDashboardService(db)
    return await dashboard_service.get_top_performing_users(limit)

# ============================================================================
# DATA INGESTION MONITORING
# ============================================================================

@router.post("/ingestion/log")
async def log_data_ingestion(
    source_name: str,
    data_type: str,
    ingestion_type: str,
    records_processed: int,
    records_successful: int,
    records_failed: int = 0,
    processing_time_ms: Optional[int] = None,
    file_size_bytes: Optional[int] = None,
    error_messages: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log data ingestion activity (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    dashboard_service = AdminDashboardService(db)
    return await dashboard_service.log_data_ingestion(
        source_name,
        data_type,
        ingestion_type,
        records_processed,
        records_successful,
        records_failed,
        processing_time_ms,
        file_size_bytes,
        error_messages,
        metadata
    )

@router.put("/ingestion/{log_id}/complete")
async def complete_data_ingestion(
    log_id: str,
    error_messages: Optional[List[str]] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark data ingestion as completed (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    dashboard_service = AdminDashboardService(db)
    return await dashboard_service.complete_data_ingestion(log_id, error_messages)

@router.get("/ingestion/summary")
async def get_data_ingestion_summary(
    days: int = Query(30, ge=1, le=365),
    source_name: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get data ingestion summary (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    dashboard_service = AdminDashboardService(db)
    return await dashboard_service.get_data_ingestion_summary(days, source_name)

# ============================================================================
# SYSTEM PERFORMANCE MONITORING
# ============================================================================

@router.post("/performance/log")
async def log_system_performance(
    metric_name: str,
    metric_value: float,
    metric_unit: Optional[str] = None,
    component: str = "api",
    severity: str = "info",
    tags: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log system performance metric (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from decimal import Decimal
    dashboard_service = AdminDashboardService(db)
    return await dashboard_service.log_system_performance(
        metric_name,
        Decimal(str(metric_value)),
        metric_unit,
        component,
        severity,
        tags
    )

@router.get("/performance/summary")
async def get_system_performance_summary(
    hours: int = Query(24, ge=1, le=168),
    component: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system performance summary (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    dashboard_service = AdminDashboardService(db)
    return await dashboard_service.get_system_performance_summary(hours, component)

# ============================================================================
# DASHBOARD OVERVIEW
# ============================================================================

@router.get("/overview")
async def get_admin_dashboard_overview(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive admin dashboard overview (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    dashboard_service = AdminDashboardService(db)
    return await dashboard_service.get_admin_dashboard_overview()

# ============================================================================
# DATA EXPANSION ENDPOINTS
# ============================================================================

@router.get("/data-expansion/summary")
async def get_data_expansion_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get data expansion summary (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from services.data_expansion_service import DataExpansionService
    expansion_service = DataExpansionService(db)
    return await expansion_service.get_expanded_market_data()

@router.get("/data-expansion/bonds")
async def get_bonds_summary(
    issuer_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get bonds summary (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from services.data_expansion_service import DataExpansionService
    expansion_service = DataExpansionService(db)
    return await expansion_service.get_bonds(issuer_type)

@router.get("/data-expansion/etfs")
async def get_etfs_summary(
    asset_class: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get ETFs summary (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from services.data_expansion_service import DataExpansionService
    expansion_service = DataExpansionService(db)
    return await expansion_service.get_etfs(asset_class)

@router.get("/data-expansion/commodities")
async def get_commodities_summary(
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get commodities summary (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from services.data_expansion_service import DataExpansionService
    expansion_service = DataExpansionService(db)
    return await expansion_service.get_commodities(category) 