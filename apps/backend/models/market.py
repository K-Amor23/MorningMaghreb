from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Quote(BaseModel):
    ticker: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime

class HistoricalData(BaseModel):
    ticker: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

class MarketSummary(BaseModel):
    masi_index: float
    masi_change: float
    madex_index: float
    madex_change: float
    masi_esg_index: float
    masi_esg_change: float
    positive_movers: int
    negative_movers: int
    total_volume: int
    top_gainers: List[Quote]
    top_losers: List[Quote]
    timestamp: datetime 