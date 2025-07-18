from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class ReportType(str, Enum):
    PNL = "pnl"
    BALANCE = "balance"
    CASHFLOW = "cashflow"
    OTHER = "other"

class JobType(str, Enum):
    FETCH = "fetch"
    EXTRACT = "extract"
    CLEAN = "clean"
    TRANSLATE = "translate"
    LIVE_UPDATE = "live_update"

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class FinancialLine(BaseModel):
    """Individual line item in a financial statement"""
    label: str
    value: float
    unit: str = "MAD"
    category: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class FinancialData(BaseModel):
    """Raw financial data extracted from PDF"""
    company: str
    year: int
    quarter: Optional[int] = None
    report_type: ReportType
    language: str = "fr"
    source_url: Optional[str] = None
    pdf_filename: Optional[str] = None
    lines: List[FinancialLine]
    extraction_metadata: Optional[Dict[str, Any]] = None

class GAAPFinancialData(BaseModel):
    """Clean GAAP financial data"""
    company: str
    year: int
    quarter: Optional[int] = None
    report_type: ReportType
    raw_id: Optional[UUID] = None
    data: Dict[str, float]  # GAAP label -> value
    ratios: Optional[Dict[str, float]] = None
    ai_summary: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)

class LabelMapping(BaseModel):
    """French to GAAP label mapping"""
    french_label: str
    gaap_label: str
    category: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class ETLJob(BaseModel):
    """ETL job tracking"""
    job_type: JobType
    status: JobStatus = JobStatus.PENDING
    company: Optional[str] = None
    year: Optional[int] = None
    quarter: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class FinancialsRawDB(BaseModel):
    """Database model for raw financials"""
    id: UUID
    company: str
    year: int
    quarter: Optional[int]
    report_type: ReportType
    language: str
    source_url: Optional[str]
    pdf_filename: Optional[str]
    json_data: Dict[str, Any]
    extraction_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class FinancialsGAAPDB(BaseModel):
    """Database model for GAAP financials"""
    id: UUID
    raw_id: Optional[UUID]
    company: str
    year: int
    quarter: Optional[int]
    report_type: ReportType
    json_data: Dict[str, Any]
    ratios: Optional[Dict[str, Any]]
    ai_summary: Optional[str]
    confidence_score: float
    created_at: datetime
    updated_at: datetime

class ETLJobDB(BaseModel):
    """Database model for ETL jobs"""
    id: UUID
    job_type: JobType
    status: JobStatus
    company: Optional[str]
    year: Optional[int]
    quarter: Optional[int]
    metadata: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

# API Response Models
class ETLJobResponse(BaseModel):
    id: UUID
    job_type: JobType
    status: JobStatus
    company: Optional[str]
    year: Optional[int]
    quarter: Optional[int]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

class FinancialSummary(BaseModel):
    """Summary of financial data for API responses"""
    company: str
    year: int
    quarter: Optional[int]
    report_type: ReportType
    revenue: Optional[float]
    net_income: Optional[float]
    total_assets: Optional[float]
    total_liabilities: Optional[float]
    ratios: Optional[Dict[str, float]]
    summary: Optional[str]
    last_updated: datetime 