from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import random

from models.paper_trading import (
    PaperTradingAccount, PaperTradingAccountCreate, PaperTradingOrder,
    PaperTradingOrderCreate, PaperTradingTransaction, PaperTradingPosition,
    PaperTradingCashTransaction, PaperTradingCashTransactionCreate,
    TradingAccountSummary, OrderHistory, TransactionHistory, TradingPerformance,
    TradingRuleValidation, TradingRuleValidationResult
)
from utils.auth import get_current_user
from utils.trading_rules import trading_rules_service

router = APIRouter(prefix="/paper-trading", tags=["Paper Trading"])

# Mock data storage - in production, this would be database queries
mock_accounts = {}
mock_orders = {}
mock_transactions = {}
mock_positions = {}

# Commission rate (0.1% of trade value)
COMMISSION_RATE = Decimal('0.001')

@router.post("/accounts", response_model=PaperTradingAccount)
async def create_trading_account(
    account_data: PaperTradingAccountCreate,
    current_user = Depends(get_current_user)
):
    """Create a new paper trading account"""
    account_id = str(uuid.uuid4())
    
    account = PaperTradingAccount(
        id=account_id,
        user_id=current_user.id,
        account_name=account_data.account_name,
        initial_balance=account_data.initial_balance,
        current_balance=account_data.initial_balance,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    mock_accounts[account_id] = account
    
    # Create initial cash transaction
    cash_transaction = PaperTradingCashTransaction(
        id=str(uuid.uuid4()),
        account_id=account_id,
        transaction_type="deposit",
        amount=account_data.initial_balance,
        description="Initial account funding",
        balance_before=Decimal('0.00'),
        balance_after=account_data.initial_balance,
        created_at=datetime.now()
    )
    
    return account

@router.get("/accounts", response_model=List[PaperTradingAccount])
async def get_trading_accounts(current_user = Depends(get_current_user)):
    """Get all trading accounts for the current user"""
    user_accounts = [
        account for account in mock_accounts.values()
        if account.user_id == current_user.id
    ]
    return user_accounts

@router.get("/accounts/{account_id}", response_model=TradingAccountSummary)
async def get_account_summary(
    account_id: str,
    current_user = Depends(get_current_user)
):
    """Get detailed account summary with positions"""
    if account_id not in mock_accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = mock_accounts[account_id]
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get positions for this account
    account_positions = [
        pos for pos in mock_positions.values()
        if pos.account_id == account_id
    ]
    
    # Calculate totals
    total_positions_value = sum(pos.current_value for pos in account_positions)
    total_unrealized_pnl = sum(pos.unrealized_pnl for pos in account_positions)
    available_cash = account.current_balance
    total_account_value = available_cash + total_positions_value
    
    # Calculate total PnL percentage
    total_unrealized_pnl_percent = (
        (total_unrealized_pnl / account.initial_balance * 100)
        if account.initial_balance > 0 else Decimal('0.00')
    )
    
    return TradingAccountSummary(
        account=account,
        positions=account_positions,
        total_positions_value=total_positions_value,
        total_unrealized_pnl=total_unrealized_pnl,
        total_unrealized_pnl_percent=total_unrealized_pnl_percent,
        available_cash=available_cash,
        total_account_value=total_account_value
    )

@router.post("/accounts/{account_id}/orders", response_model=PaperTradingOrder)
async def place_order(
    account_id: str,
    order_data: PaperTradingOrderCreate,
    current_user = Depends(get_current_user)
):
    """Place a new trading order"""
    if account_id not in mock_accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = mock_accounts[account_id]
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Calculate order details
    total_amount = order_data.quantity * order_data.price
    commission = total_amount * COMMISSION_RATE
    net_amount = total_amount + commission
    
    # Check if user has enough cash for buy orders
    if order_data.order_type == "buy":
        if account.current_balance < net_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient funds. Required: {net_amount} MAD, Available: {account.current_balance} MAD"
            )
    
    # Check if user has enough shares for sell orders
    if order_data.order_type == "sell":
        position_key = f"{account_id}_{order_data.ticker}"
        if position_key in mock_positions:
            position = mock_positions[position_key]
            if position.quantity < order_data.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient shares. Required: {order_data.quantity}, Available: {position.quantity}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"No position found for {order_data.ticker}"
            )
    
    # Validate order against CSE trading rules
    validation = TradingRuleValidation(
        ticker=order_data.ticker,
        order_type=order_data.order_type,
        quantity=order_data.quantity,
        price=order_data.price,
        current_market_price=order_data.price,  # Mock current price
        daily_price_change_percent=Decimal("5.0")  # Mock daily change
    )
    
    validation_result = trading_rules_service.validate_order(validation)
    
    if not validation_result.is_valid:
        # Log the violation
        for rule in trading_rules_service.trading_rules.values():
            if rule.ticker == order_data.ticker or rule.ticker is None:
                trading_rules_service.log_violation({
                    "rule_id": rule.id,
                    "ticker": order_data.ticker,
                    "violation_type": "price_limit_exceeded",
                    "order_id": None,  # Will be set after order creation
                    "user_id": current_user.id,
                    "price_at_violation": order_data.price,
                    "price_limit": None,
                    "violation_details": {
                        "blocked_reasons": validation_result.blocked_reasons,
                        "warnings": validation_result.warnings
                    }
                })
        
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Order blocked by CSE trading rules",
                "blocked_reasons": validation_result.blocked_reasons,
                "warnings": validation_result.warnings,
                "violations": validation_result.violations
            }
        )
    
    # Create order
    order_id = str(uuid.uuid4())
    order = PaperTradingOrder(
        id=order_id,
        account_id=account_id,
        ticker=order_data.ticker,
        order_type=order_data.order_type,
        quantity=order_data.quantity,
        price=order_data.price,
        total_amount=total_amount,
        commission=commission,
        notes=order_data.notes,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    mock_orders[order_id] = order
    
    # Execute order immediately (in real trading, this would be queued)
    await execute_order(order_id)
    
    return order

@router.get("/accounts/{account_id}/orders", response_model=OrderHistory)
async def get_order_history(
    account_id: str,
    status: Optional[str] = Query(None, regex="^(pending|filled|cancelled|rejected)$"),
    current_user = Depends(get_current_user)
):
    """Get order history for an account"""
    if account_id not in mock_accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = mock_accounts[account_id]
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Filter orders by account and status
    account_orders = [
        order for order in mock_orders.values()
        if order.account_id == account_id
    ]
    
    if status:
        account_orders = [order for order in account_orders if order.order_status == status]
    
    # Sort by creation date (newest first)
    account_orders.sort(key=lambda x: x.created_at, reverse=True)
    
    # Calculate statistics
    total_orders = len(account_orders)
    filled_orders = len([o for o in account_orders if o.order_status == "filled"])
    pending_orders = len([o for o in account_orders if o.order_status == "pending"])
    cancelled_orders = len([o for o in account_orders if o.order_status == "cancelled"])
    
    return OrderHistory(
        orders=account_orders,
        total_orders=total_orders,
        filled_orders=filled_orders,
        pending_orders=pending_orders,
        cancelled_orders=cancelled_orders
    )

@router.get("/accounts/{account_id}/transactions", response_model=TransactionHistory)
async def get_transaction_history(
    account_id: str,
    limit: int = Query(50, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """Get transaction history for an account"""
    if account_id not in mock_accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = mock_accounts[account_id]
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get transactions for this account
    account_transactions = [
        tx for tx in mock_transactions.values()
        if tx.account_id == account_id
    ]
    
    # Sort by creation date (newest first) and limit
    account_transactions.sort(key=lambda x: x.created_at, reverse=True)
    account_transactions = account_transactions[:limit]
    
    # Calculate statistics
    total_transactions = len(account_transactions)
    total_buy_amount = sum(
        tx.total_amount for tx in account_transactions
        if tx.transaction_type == "buy"
    )
    total_sell_amount = sum(
        tx.total_amount for tx in account_transactions
        if tx.transaction_type == "sell"
    )
    total_commission = sum(tx.commission for tx in account_transactions)
    
    return TransactionHistory(
        transactions=account_transactions,
        total_transactions=total_transactions,
        total_buy_amount=total_buy_amount,
        total_sell_amount=total_sell_amount,
        total_commission=total_commission
    )

@router.get("/accounts/{account_id}/performance", response_model=TradingPerformance)
async def get_trading_performance(
    account_id: str,
    current_user = Depends(get_current_user)
):
    """Get trading performance metrics"""
    if account_id not in mock_accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = mock_accounts[account_id]
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get all transactions for this account
    account_transactions = [
        tx for tx in mock_transactions.values()
        if tx.account_id == account_id
    ]
    
    # Calculate performance metrics
    total_return = account.current_balance - account.initial_balance
    total_return_percent = (
        (total_return / account.initial_balance * 100)
        if account.initial_balance > 0 else Decimal('0.00')
    )
    
    # Find best and worst performers
    positions = [pos for pos in mock_positions.values() if pos.account_id == account_id]
    if positions:
        best_performer = max(positions, key=lambda x: x.unrealized_pnl_percent).ticker
        worst_performer = min(positions, key=lambda x: x.unrealized_pnl_percent).ticker
    else:
        best_performer = None
        worst_performer = None
    
    # Calculate trade statistics
    total_trades = len(account_transactions)
    winning_trades = len([tx for tx in account_transactions if tx.net_amount > 0])
    losing_trades = len([tx for tx in account_transactions if tx.net_amount < 0])
    win_rate = (
        (winning_trades / total_trades * 100)
        if total_trades > 0 else Decimal('0.00')
    )
    
    return TradingPerformance(
        total_return=total_return,
        total_return_percent=total_return_percent,
        best_performer=best_performer,
        worst_performer=worst_performer,
        total_trades=total_trades,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        win_rate=win_rate
    )

async def execute_order(order_id: str):
    """Execute a trading order (simplified - immediate execution)"""
    if order_id not in mock_orders:
        return
    
    order = mock_orders[order_id]
    account = mock_accounts[order.account_id]
    
    # Update order status
    order.order_status = "filled"
    order.filled_quantity = order.quantity
    order.filled_price = order.price
    order.filled_at = datetime.now()
    order.updated_at = datetime.now()
    
    # Create transaction
    transaction_id = str(uuid.uuid4())
    balance_before = account.current_balance
    
    if order.order_type == "buy":
        # Deduct cash for buy
        net_amount = order.total_amount + order.commission
        account.current_balance -= net_amount
        
        # Update or create position
        position_key = f"{order.account_id}_{order.ticker}"
        if position_key in mock_positions:
            position = mock_positions[position_key]
            # Calculate new average cost
            total_shares = position.quantity + order.quantity
            total_cost = position.total_cost + order.total_amount
            position.avg_cost = total_cost / total_shares
            position.quantity = total_shares
            position.total_cost = total_cost
        else:
            position = PaperTradingPosition(
                id=str(uuid.uuid4()),
                account_id=order.account_id,
                ticker=order.ticker,
                quantity=order.quantity,
                avg_cost=order.price,
                total_cost=order.total_amount,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            mock_positions[position_key] = position
        
    else:  # sell
        # Add cash for sell
        net_amount = order.total_amount - order.commission
        account.current_balance += net_amount
        
        # Update position
        position_key = f"{order.account_id}_{order.ticker}"
        position = mock_positions[position_key]
        position.quantity -= order.quantity
        position.total_cost = position.avg_cost * position.quantity
        
        # Remove position if quantity becomes zero
        if position.quantity <= 0:
            del mock_positions[position_key]
    
    # Create transaction record
    transaction = PaperTradingTransaction(
        id=transaction_id,
        account_id=order.account_id,
        order_id=order_id,
        ticker=order.ticker,
        transaction_type=order.order_type,
        quantity=order.quantity,
        price=order.price,
        total_amount=order.total_amount,
        commission=order.commission,
        net_amount=net_amount,
        balance_before=balance_before,
        balance_after=account.current_balance,
        created_at=datetime.now()
    )
    
    mock_transactions[transaction_id] = transaction
    
    # Update account PnL
    account.total_pnl = account.current_balance - account.initial_balance
    account.total_pnl_percent = (
        (account.total_pnl / account.initial_balance * 100)
        if account.initial_balance > 0 else Decimal('0.00')
    )
    account.updated_at = datetime.now()
    
    # Update position current value and PnL (mock current price)
    if order.order_type == "buy":
        position_key = f"{order.account_id}_{order.ticker}"
        if position_key in mock_positions:
            position = mock_positions[position_key]
            # Mock current price (in real app, this would come from market data)
            current_price = order.price * (1 + random.uniform(-0.05, 0.05))
            position.current_value = position.quantity * Decimal(str(current_price))
            position.unrealized_pnl = position.current_value - position.total_cost
            position.unrealized_pnl_percent = (
                (position.unrealized_pnl / position.total_cost * 100)
                if position.total_cost > 0 else Decimal('0.00')
            )
            position.last_updated = datetime.now()
            position.updated_at = datetime.now() 