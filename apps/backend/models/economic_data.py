from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, date
from uuid import UUID
from enum import Enum

class EconomicIndicatorType(str, Enum):
    """Types of economic indicators"""
    KEY_POLICY_RATE = "key_policy_rate"
    FOREIGN_EXCHANGE_RESERVES = "foreign_exchange_reserves"
    INFLATION_CPI = "inflation_cpi"
    MONEY_SUPPLY = "money_supply"
    BALANCE_OF_PAYMENTS = "balance_of_payments"
    CREDIT_TO_ECONOMY = "credit_to_economy"

class DataFrequency(str, Enum):
    """Frequency of data updates"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class EconomicDataPoint(BaseModel):
    """Individual economic data point"""
    date: date
    value: float
    unit: str = "MAD"
    indicator: EconomicIndicatorType
    source: str = "BAM"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None

class EconomicDataSet(BaseModel):
    """Collection of economic data points"""
    indicator: EconomicIndicatorType
    frequency: DataFrequency
    source: str = "BAM"
    data_points: List[EconomicDataPoint]
    latest_date: Optional[date] = None
    earliest_date: Optional[date] = None
    total_points: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class EconomicDataRaw(BaseModel):
    """Raw economic data from source"""
    indicator: EconomicIndicatorType
    source_url: str
    file_path: str
    original_filename: str
    file_size: int
    download_date: datetime
    parsing_metadata: Optional[Dict[str, Any]] = None
    raw_content_hash: Optional[str] = None

class EconomicDataParsed(BaseModel):
    """Parsed economic data"""
    indicator: EconomicIndicatorType
    raw_data_id: Optional[UUID] = None
    parsed_data: Dict[str, Any]
    data_points: List[EconomicDataPoint]
    parsing_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    parsing_errors: List[str] = []
    parsed_at: datetime = Field(default_factory=datetime.now)

# Database Models
class EconomicDataRawDB(BaseModel):
    """Database model for raw economic data"""
    id: UUID
    indicator: EconomicIndicatorType
    source_url: str
    file_path: str
    original_filename: str
    file_size: int
    download_date: datetime
    parsing_metadata: Optional[Dict[str, Any]]
    raw_content_hash: Optional[str]
    created_at: datetime
    updated_at: datetime

class EconomicDataParsedDB(BaseModel):
    """Database model for parsed economic data"""
    id: UUID
    indicator: EconomicIndicatorType
    raw_data_id: Optional[UUID]
    parsed_data: Dict[str, Any]
    data_points: List[Dict[str, Any]]  # JSON representation of EconomicDataPoint
    parsing_confidence: float
    parsing_errors: List[str]
    parsed_at: datetime
    created_at: datetime
    updated_at: datetime

# API Response Models
class EconomicDataSummary(BaseModel):
    """Summary of economic data for API responses"""
    indicator: EconomicIndicatorType
    latest_value: Optional[float]
    latest_date: Optional[date]
    unit: str
    frequency: DataFrequency
    source: str
    last_updated: datetime
    trend: Optional[str] = None  # "up", "down", "stable"
    change_percentage: Optional[float] = None

class EconomicDataResponse(BaseModel):
    """API response for economic data"""
    indicator: EconomicIndicatorType
    data_points: List[EconomicDataPoint]
    summary: EconomicDataSummary
    metadata: Dict[str, Any]

class EconomicDataBulkResponse(BaseModel):
    """Bulk API response for multiple indicators"""
    indicators: Dict[EconomicIndicatorType, EconomicDataResponse]
    total_indicators: int
    last_updated: datetime

# Configuration Models
class EconomicDataSourceConfig(BaseModel):
    """Configuration for economic data sources"""
    indicator: EconomicIndicatorType
    url: str
    frequency: DataFrequency
    format: str  # "xls", "pdf", "csv"
    description: str
    enabled: bool = True
    retry_attempts: int = 3
    timeout_seconds: int = 30

class EconomicDataETLJob(BaseModel):
    """ETL job for economic data"""
    job_id: UUID
    indicator: EconomicIndicatorType
    status: str = "pending"  # "pending", "running", "completed", "failed"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    files_processed: int = 0
    data_points_extracted: int = 0
    errors: List[str] = []
    metadata: Optional[Dict[str, Any]] = None 