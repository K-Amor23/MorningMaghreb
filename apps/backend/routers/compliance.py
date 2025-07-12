from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
import uuid
from uuid import UUID

from models.paper_trading import (
    TradingRule, TradingRuleCreate, TradingRuleViolation, TradingHalt,
    TradingHaltCreate, PriceMovementAlert, ComplianceDashboardLog,
    TradingRuleValidation, TradingRuleValidationResult, ComplianceSummary
)
from utils.auth import get_current_user
from utils.trading_rules import trading_rules_service

router = APIRouter(prefix="/compliance", tags=["Trading Rules & Compliance"])

@router.get("/rules", response_model=List[TradingRule])
async def get_trading_rules(
    ticker: Optional[str] = Query(None, description="Filter by specific ticker"),
    rule_type: Optional[str] = Query(None, description="Filter by rule type"),
    current_user = Depends(get_current_user)
):
    """Get trading rules (filtered by ticker and/or rule type)"""
    rules = list(trading_rules_service.trading_rules.values())
    
    if ticker:
        rules = [r for r in rules if r.ticker == ticker or r.ticker is None]
    
    if rule_type:
        rules = [r for r in rules if r.rule_type == rule_type]
    
    return rules

@router.post("/rules", response_model=TradingRule)
async def create_trading_rule(
    rule_data: TradingRuleCreate,
    current_user = Depends(get_current_user)
):
    """Create a new trading rule (admin only)"""
    # In production, check if user has admin privileges
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    rule_id = str(uuid.uuid4())
    rule = TradingRule(
        id=UUID(rule_id),
        ticker=rule_data.ticker,
        rule_type=rule_data.rule_type,
        rule_name=rule_data.rule_name,
        rule_description=rule_data.rule_description,
        daily_price_limit_percent=rule_data.daily_price_limit_percent,
        circuit_breaker_threshold=rule_data.circuit_breaker_threshold,
        halt_conditions=rule_data.halt_conditions,
        order_restrictions=rule_data.order_restrictions,
        is_active=True,
        effective_date=rule_data.effective_date,
        expiry_date=rule_data.expiry_date,
        source=rule_data.source,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by=current_user.id
    )
    
    trading_rules_service.trading_rules[rule_id] = rule
    return rule

@router.post("/validate-order", response_model=TradingRuleValidationResult)
async def validate_order(
    validation: TradingRuleValidation,
    current_user = Depends(get_current_user)
):
    """Validate an order against CSE trading rules"""
    return trading_rules_service.validate_order(validation)

@router.get("/halts", response_model=List[TradingHalt])
async def get_trading_halts(
    ticker: Optional[str] = Query(None, description="Filter by ticker"),
    active_only: bool = Query(True, description="Show only active halts"),
    current_user = Depends(get_current_user)
):
    """Get trading halts"""
    halts = list(trading_rules_service.trading_halts.values())
    
    if ticker:
        halts = [h for h in halts if h.ticker == ticker]
    
    if active_only:
        halts = [h for h in halts if h.is_active and h.halt_end is None]
    
    return halts

@router.post("/halts", response_model=TradingHalt)
async def create_trading_halt(
    halt_data: TradingHaltCreate,
    current_user = Depends(get_current_user)
):
    """Create a new trading halt (admin only)"""
    # In production, check if user has admin privileges
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return trading_rules_service.create_trading_halt(halt_data.dict())

@router.post("/halts/{ticker}/end")
async def end_trading_halt(
    ticker: str,
    reason: str = "Manual end",
    current_user = Depends(get_current_user)
):
    """End an active trading halt (admin only)"""
    # In production, check if user has admin privileges
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    halted = trading_rules_service.end_trading_halt(ticker, reason)
    if not halted:
        raise HTTPException(status_code=404, detail="No active halt found for this ticker")
    
    return {"message": f"Trading halt ended for {ticker}", "halt": halted}

@router.get("/alerts", response_model=List[PriceMovementAlert])
async def get_price_alerts(
    ticker: Optional[str] = Query(None, description="Filter by ticker"),
    triggered_only: bool = Query(False, description="Show only triggered alerts"),
    current_user = Depends(get_current_user)
):
    """Get price movement alerts"""
    alerts = list(trading_rules_service.price_alerts.values())
    
    if ticker:
        alerts = [a for a in alerts if a.ticker == ticker]
    
    if triggered_only:
        alerts = [a for a in alerts if a.is_triggered]
    
    return alerts

@router.post("/alerts", response_model=PriceMovementAlert)
async def create_price_alert(
    alert_data: dict,
    current_user = Depends(get_current_user)
):
    """Create a price movement alert"""
    return trading_rules_service.create_price_alert(alert_data)

@router.get("/violations", response_model=List[TradingRuleViolation])
async def get_rule_violations(
    ticker: Optional[str] = Query(None, description="Filter by ticker"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user = Depends(get_current_user)
):
    """Get trading rule violations"""
    violations = list(trading_rules_service.rule_violations.values())
    
    if ticker:
        violations = [v for v in violations if v.ticker == ticker]
    
    if status:
        violations = [v for v in violations if v.status == status]
    
    return violations

@router.get("/summary", response_model=ComplianceSummary)
async def get_compliance_summary(current_user = Depends(get_current_user)):
    """Get compliance dashboard summary"""
    summary_data = trading_rules_service.get_compliance_summary()
    
    return ComplianceSummary(
        active_halts=summary_data["active_halts"],
        recent_violations=summary_data["recent_violations"],
        price_alerts=summary_data["price_alerts"],
        total_violations_today=summary_data["total_violations_today"],
        total_halts_today=summary_data["total_halts_today"],
        stocks_nearing_limits=summary_data["stocks_nearing_limits"]
    )

@router.get("/education/circuit-breakers")
async def get_circuit_breaker_info():
    """Get educational information about circuit breakers"""
    return {
        "title": "CSE Circuit Breakers",
        "description": "Circuit breakers are automatic trading halts triggered by significant price movements to prevent market panic and allow time for information dissemination.",
        "rules": [
            {
                "threshold": "15% drop",
                "action": "Trading halt for 15 minutes",
                "description": "When a stock drops 15% or more from the previous day's close"
            },
            {
                "threshold": "20% drop", 
                "action": "Trading halt for 30 minutes",
                "description": "When a stock drops 20% or more from the previous day's close"
            }
        ],
        "examples": [
            {
                "date": "2024-01-15",
                "ticker": "ATW",
                "drop": "16.5%",
                "reason": "Earnings announcement"
            },
            {
                "date": "2024-01-10", 
                "ticker": "IAM",
                "drop": "18.2%",
                "reason": "Regulatory news"
            }
        ]
    }

@router.get("/education/price-limits")
async def get_price_limit_info():
    """Get educational information about daily price limits"""
    return {
        "title": "CSE Daily Price Limits",
        "description": "Daily price limits prevent excessive volatility by restricting the maximum price movement allowed in a single trading day.",
        "limits": [
            {
                "type": "Standard stocks",
                "limit": "±10%",
                "description": "Most listed securities have a 10% daily price movement limit"
            },
            {
                "type": "New listings",
                "limit": "±20%", 
                "description": "Newly listed securities may have higher limits for the first 30 days"
            }
        ],
        "calculation": "Price limits are calculated from the previous day's closing price",
        "exceptions": [
            "Market makers may be exempt from certain limits",
            "Regulatory announcements may temporarily suspend limits"
        ]
    } 