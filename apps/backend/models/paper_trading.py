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
    order_type: str = Field(..., regex="^(buy|sell)$")
    order_status: str = Field(default="pending", regex="^(pending|filled|cancelled|rejected)$")
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
    order_type: str = Field(..., regex="^(buy|sell)$")
    quantity: Decimal = Field(..., gt=0)
    price: Decimal = Field(..., gt=0)
    notes: Optional[str] = None

class PaperTradingTransaction(BaseModel):
    id: UUID
    account_id: UUID
    order_id: Optional[UUID] = None
    ticker: str
    transaction_type: str = Field(..., regex="^(buy|sell)$")
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
    transaction_type: str = Field(..., regex="^(deposit|withdrawal|dividend|commission)$")
    amount: Decimal
    description: Optional[str] = None
    balance_before: Decimal
    balance_after: Decimal
    created_at: datetime

class PaperTradingCashTransactionCreate(BaseModel):
    transaction_type: str = Field(..., regex="^(deposit|withdrawal)$")
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