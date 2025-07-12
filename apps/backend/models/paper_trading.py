from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID

class PaperTradingAccount(BaseModel):
    id: UUID
    user_id: UUID
    account_name: str = "Paper Trading Account"
    initial_balance: Decimal = Field(default=100000.00, description="Initial account balance in MAD")
    current_balance: Decimal = Field(default=100000.00, description="Current account balance in MAD")
    total_pnl: Decimal = Field(default=0.00, description="Total profit/loss in MAD")
    total_pnl_percent: Decimal = Field(default=0.00, description="Total profit/loss percentage")
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class PaperTradingAccountCreate(BaseModel):
    account_name: str = "Paper Trading Account"
    initial_balance: Decimal = Field(default=100000.00, ge=0, description="Initial balance in MAD")

class PaperTradingOrder(BaseModel):
    id: UUID
    account_id: UUID
    ticker: str
    order_type: str = Field(..., pattern="^(buy|sell)$")
    order_status: str = Field(default="pending", pattern="^(pending|filled|cancelled|rejected)$")
    quantity: Decimal = Field(..., gt=0)
    price: Decimal = Field(..., gt=0)
    total_amount: Decimal
    commission: Decimal = Field(default=0.00)
    filled_quantity: Decimal = Field(default=0.00)
    filled_price: Optional[Decimal] = None
    filled_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class PaperTradingOrderCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    order_type: str = Field(..., pattern="^(buy|sell)$")
    quantity: Decimal = Field(..., gt=0)
    price: Decimal = Field(..., gt=0)
    notes: Optional[str] = None

class PaperTradingTransaction(BaseModel):
    id: UUID
    account_id: UUID
    order_id: Optional[UUID] = None
    ticker: str
    transaction_type: str = Field(..., pattern="^(buy|sell)$")
    quantity: Decimal = Field(..., gt=0)
    price: Decimal = Field(..., gt=0)
    total_amount: Decimal
    commission: Decimal = Field(default=0.00)
    net_amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    created_at: datetime

class PaperTradingPosition(BaseModel):
    id: UUID
    account_id: UUID
    ticker: str
    quantity: Decimal = Field(default=0.00)
    avg_cost: Decimal = Field(default=0.00)
    total_cost: Decimal = Field(default=0.00)
    current_value: Decimal = Field(default=0.00)
    unrealized_pnl: Decimal = Field(default=0.00)
    unrealized_pnl_percent: Decimal = Field(default=0.00)
    last_updated: datetime
    created_at: datetime
    updated_at: datetime

class PaperTradingCashTransaction(BaseModel):
    id: UUID
    account_id: UUID
    transaction_type: str = Field(..., pattern="^(deposit|withdrawal|dividend|commission)$")
    amount: Decimal
    description: Optional[str] = None
    balance_before: Decimal
    balance_after: Decimal
    created_at: datetime

class PaperTradingCashTransactionCreate(BaseModel):
    transaction_type: str = Field(..., pattern="^(deposit|withdrawal)$")
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None

class TradingAccountSummary(BaseModel):
    account: PaperTradingAccount
    positions: List[PaperTradingPosition]
    total_positions_value: Decimal
    total_unrealized_pnl: Decimal
    total_unrealized_pnl_percent: Decimal
    available_cash: Decimal
    total_account_value: Decimal

class OrderHistory(BaseModel):
    orders: List[PaperTradingOrder]
    total_orders: int
    filled_orders: int
    pending_orders: int
    cancelled_orders: int

class TransactionHistory(BaseModel):
    transactions: List[PaperTradingTransaction]
    total_transactions: int
    total_buy_amount: Decimal
    total_sell_amount: Decimal
    total_commission: Decimal

class TradingPerformance(BaseModel):
    total_return: Decimal
    total_return_percent: Decimal
    best_performer: Optional[str] = None
    worst_performer: Optional[str] = None
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: Decimal

# CSE Trading Rules and Compliance Models
class TradingRule(BaseModel):
    id: UUID
    ticker: Optional[str] = None  # None means applies to all stocks
    rule_type: str = Field(..., pattern="^(daily_price_limit|circuit_breaker|trading_halt|order_restriction|market_segment_rule)$")
    rule_name: str
    rule_description: Optional[str] = None
    daily_price_limit_percent: Optional[Decimal] = None
    circuit_breaker_threshold: Optional[Decimal] = None
    halt_conditions: Optional[dict] = None
    order_restrictions: Optional[dict] = None
    is_active: bool = True
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    source: str = "CSE"
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

class TradingRuleCreate(BaseModel):
    ticker: Optional[str] = None
    rule_type: str = Field(..., pattern="^(daily_price_limit|circuit_breaker|trading_halt|order_restriction|market_segment_rule)$")
    rule_name: str
    rule_description: Optional[str] = None
    daily_price_limit_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    circuit_breaker_threshold: Optional[Decimal] = Field(None, ge=0, le=100)
    halt_conditions: Optional[dict] = None
    order_restrictions: Optional[dict] = None
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    source: str = "CSE"

class TradingRuleViolation(BaseModel):
    id: UUID
    rule_id: UUID
    ticker: str
    violation_type: str
    violation_details: Optional[dict] = None
    order_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    price_at_violation: Optional[Decimal] = None
    price_limit: Optional[Decimal] = None
    violation_timestamp: datetime
    resolved_at: Optional[datetime] = None
    status: str = Field(default="active", pattern="^(active|resolved|ignored)$")

class TradingHalt(BaseModel):
    id: UUID
    ticker: str
    halt_type: str = Field(..., pattern="^(circuit_breaker|news_pending|regulatory|technical|volatility)$")
    halt_reason: str
    halt_start: datetime
    halt_end: Optional[datetime] = None
    price_at_halt: Optional[Decimal] = None
    volume_at_halt: Optional[int] = None
    source: str = "CSE"
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class TradingHaltCreate(BaseModel):
    ticker: str
    halt_type: str = Field(..., pattern="^(circuit_breaker|news_pending|regulatory|technical|volatility)$")
    halt_reason: str
    halt_start: datetime
    halt_end: Optional[datetime] = None
    price_at_halt: Optional[Decimal] = None
    volume_at_halt: Optional[int] = None
    source: str = "CSE"

class PriceMovementAlert(BaseModel):
    id: UUID
    ticker: str
    alert_type: str = Field(..., pattern="^(approaching_limit|circuit_breaker_warning|volatility_alert)$")
    current_price: Decimal
    price_change_percent: Optional[Decimal] = None
    threshold_percent: Optional[Decimal] = None
    alert_message: Optional[str] = None
    is_triggered: bool = False
    triggered_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime

class ComplianceDashboardLog(BaseModel):
    id: UUID
    log_type: str = Field(..., pattern="^(rule_violation|trading_halt|price_alert|circuit_breaker|admin_action)$")
    ticker: Optional[str] = None
    user_id: Optional[UUID] = None
    action_details: Optional[dict] = None
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    timestamp: datetime

class TradingRuleValidation(BaseModel):
    ticker: str
    order_type: str
    quantity: Decimal
    price: Decimal
    current_market_price: Optional[Decimal] = None
    daily_price_change_percent: Optional[Decimal] = None

class TradingRuleValidationResult(BaseModel):
    is_valid: bool
    violations: List[str] = []
    warnings: List[str] = []
    blocked_reasons: List[str] = []
    price_limits: Optional[dict] = None
    halt_status: Optional[dict] = None

class ComplianceSummary(BaseModel):
    active_halts: List[TradingHalt]
    recent_violations: List[TradingRuleViolation]
    price_alerts: List[PriceMovementAlert]
    total_violations_today: int
    total_halts_today: int
    stocks_nearing_limits: List[str] 