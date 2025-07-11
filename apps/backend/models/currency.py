from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID

class BAMRate(BaseModel):
    id: Optional[UUID] = None
    currency_pair: str = Field(..., description="Currency pair e.g., 'USD/MAD'")
    rate: Decimal = Field(..., description="Exchange rate")
    rate_date: date = Field(..., description="Date of the rate")
    source: str = Field(default="BAM", description="Source of the rate")
    created_at: Optional[datetime] = None

class RemittanceRate(BaseModel):
    id: Optional[UUID] = None
    service_name: str = Field(..., description="Remittance service name")
    currency_pair: str = Field(..., description="Currency pair")
    rate: Decimal = Field(..., description="Exchange rate")
    fee_amount: Optional[Decimal] = Field(None, description="Fee amount")
    fee_currency: str = Field(default="USD", description="Fee currency")
    fee_type: str = Field(default="fixed", description="Type of fee")
    transfer_amount: Optional[Decimal] = Field(None, description="Transfer amount used for calculation")
    effective_rate: Optional[Decimal] = Field(None, description="Rate after fees")
    spread_percentage: Optional[Decimal] = Field(None, description="% difference from BAM rate")
    rate_date: date = Field(..., description="Date of the rate")
    scraped_at: Optional[datetime] = None
    is_active: bool = Field(default=True, description="Whether rate is still active")

class RateAlert(BaseModel):
    id: Optional[UUID] = None
    user_id: UUID = Field(..., description="User ID")
    currency_pair: str = Field(..., description="Currency pair to monitor")
    target_rate: Decimal = Field(..., description="Target rate for alert")
    alert_type: str = Field(default="above", description="Alert when rate goes above/below target")
    is_active: bool = Field(default=True, description="Whether alert is active")
    last_triggered: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class RateAnalysis(BaseModel):
    id: Optional[UUID] = None
    currency_pair: str = Field(..., description="Currency pair")
    analysis_date: date = Field(..., description="Date of analysis")
    bam_rate: Decimal = Field(..., description="Official BAM rate")
    best_service: str = Field(..., description="Best remittance service")
    best_rate: Decimal = Field(..., description="Best available rate")
    best_spread: Decimal = Field(..., description="Best spread percentage")
    avg_spread_30d: Optional[Decimal] = Field(None, description="Average spread over 30 days")
    percentile_30d: Optional[int] = Field(None, description="How good is today's rate (1-100)")
    ai_advice: Optional[str] = Field(None, description="AI-generated recommendation")
    created_at: Optional[datetime] = None

class CurrencyComparison(BaseModel):
    currency_pair: str
    bam_rate: Decimal
    services: List[RemittanceRate]
    best_service: str
    best_rate: Decimal
    best_spread: Decimal
    recommendation: str
    is_good_time: bool
    percentile_30d: Optional[int] = None

class RateAlertCreate(BaseModel):
    currency_pair: str = Field(..., description="Currency pair to monitor")
    target_rate: Decimal = Field(..., description="Target rate for alert")
    alert_type: str = Field(default="above", description="Alert when rate goes above/below target")

class RateAlertResponse(BaseModel):
    id: UUID
    currency_pair: str
    target_rate: Decimal
    alert_type: str
    is_active: bool
    created_at: datetime 