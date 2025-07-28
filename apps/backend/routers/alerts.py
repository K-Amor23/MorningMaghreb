from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List

from models.alert import (
    AlertCreate, AlertUpdate, Alert,
    AlertResponse, AlertCreateResponse, AlertUpdateResponse,
    AlertDeleteResponse, AlertListResponse, AlertTriggerResponse
)
from models.user import UserProfile
from services.alert_service import alert_service
from services.auth_service import auth_service

router = APIRouter()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    return await auth_service.get_current_user(token)

@router.get("/", response_model=AlertListResponse)
async def get_user_alerts(current_user: UserProfile = Depends(get_current_user)):
    """Get all alerts for the current user"""
    alerts = await alert_service.get_user_alerts(current_user.id)
    return AlertListResponse(
        alerts=alerts,
        total_count=len(alerts)
    )

@router.post("/", response_model=AlertCreateResponse)
async def create_alert(
    alert_data: AlertCreate,
    current_user: UserProfile = Depends(get_current_user)
):
    """Create a new price alert for the current user"""
    alert = await alert_service.create_alert(current_user.id, alert_data)
    return AlertCreateResponse(alert=alert)

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """Get a specific alert"""
    alert = await alert_service.get_alert(alert_id, current_user.id)
    return AlertResponse(alert=alert)

@router.put("/{alert_id}", response_model=AlertUpdateResponse)
async def update_alert(
    alert_id: str,
    update_data: AlertUpdate,
    current_user: UserProfile = Depends(get_current_user)
):
    """Update an alert"""
    alert = await alert_service.update_alert(alert_id, current_user.id, update_data)
    return AlertUpdateResponse(alert=alert)

@router.delete("/{alert_id}", response_model=AlertDeleteResponse)
async def delete_alert(
    alert_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """Delete an alert"""
    await alert_service.delete_alert(alert_id, current_user.id)
    return AlertDeleteResponse()

@router.post("/trigger", response_model=AlertTriggerResponse)
async def trigger_alerts():
    """Background job to check and trigger alerts (admin only)"""
    # In a real implementation, this would be called by a background job
    # For now, we'll allow it to be called manually for testing
    triggered_alerts = await alert_service.check_alerts()
    return AlertTriggerResponse(
        triggered_alerts=triggered_alerts,
        total_triggered=len(triggered_alerts)
    ) 