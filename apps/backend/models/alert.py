from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal

class AlertType(str, Enum):
    ABOVE = "above"
    BELOW = "below"
    CHANGE_PERCENT = "change_percent"
    VOLUME_SPIKE = "volume_spike"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    DISABLED = "disabled"

class AlertCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    alert_type: AlertType
    target_value: Decimal = Field(..., ge=0)
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('ticker')
    def validate_ticker(cls, v):
        return v.upper()

class AlertUpdate(BaseModel):
    alert_type: Optional[AlertType] = None
    target_value: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class Alert(BaseModel):
    id: str
    user_id: str
    ticker: str
    alert_type: AlertType
    target_value: Decimal
    current_value: Optional[Decimal] = None
    is_active: bool = True
    notes: Optional[str] = None
    triggered_at: Optional[datetime] = None
    notification_sent: bool = False
    created_at: datetime
    updated_at: datetime

class AlertResponse(BaseModel):
    alert: Alert
    message: str = "Alert retrieved successfully"

class AlertCreateResponse(BaseModel):
    alert: Alert
    message: str = "Alert created successfully"

class AlertUpdateResponse(BaseModel):
    alert: Alert
    message: str = "Alert updated successfully"

class AlertDeleteResponse(BaseModel):
    message: str = "Alert deleted successfully"

class AlertListResponse(BaseModel):
    alerts: List[Alert]
    total_count: int
    message: str = "Alerts retrieved successfully"

class AlertTriggerResponse(BaseModel):
    triggered_alerts: List[Alert]
    total_triggered: int
    message: str = "Alert check completed"

class AlertSummary(BaseModel):
    total_alerts: int
    active_alerts: int
    triggered_alerts: int
    alerts_by_type: dict
    alerts_by_ticker: dict 