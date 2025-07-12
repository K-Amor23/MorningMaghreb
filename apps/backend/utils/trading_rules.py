from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
import uuid
from fastapi import HTTPException
from uuid import UUID

from models.paper_trading import (
    TradingRule, TradingRuleValidation, TradingRuleValidationResult,
    TradingHalt, PriceMovementAlert, TradingRuleViolation
)

class TradingRulesService:
    """Service for handling CSE trading rules and compliance"""
    
    def __init__(self):
        # Mock data storage - in production, this would be database queries
        self.trading_rules = {}
        self.trading_halts = {}
        self.price_alerts = {}
        self.rule_violations = {}
        
        # Initialize with default CSE rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize with default CSE trading rules"""
        # General market rules (apply to all stocks)
        general_rules = [
            {
                "id": str(uuid.uuid4()),
                "ticker": None,  # Applies to all stocks
                "rule_type": "daily_price_limit",
                "rule_name": "CSE Daily Price Limit",
                "rule_description": "Standard daily price movement limit for all listed securities",
                "daily_price_limit_percent": Decimal("10.00"),
                "is_active": True,
                "effective_date": datetime.now(),
                "source": "CSE"
            },
            {
                "id": str(uuid.uuid4()),
                "ticker": None,
                "rule_type": "circuit_breaker",
                "rule_name": "CSE Circuit Breaker",
                "rule_description": "Automatic trading halt when price drops 15% or more",
                "circuit_breaker_threshold": Decimal("15.00"),
                "is_active": True,
                "effective_date": datetime.now(),
                "source": "CSE"
            }
        ]
        
        # Specific rules for major stocks
        stock_rules = [
            ("ATW", "Attijariwafa Bank"),
            ("IAM", "Maroc Telecom"),
            ("BCP", "Banque Centrale Populaire"),
            ("BMCE", "BMCE Bank"),
            ("ONA", "Omnium Nord Africain"),
            ("CMT", "Ciments du Maroc"),
            ("LAFA", "Lafarge Ciments")
        ]
        
        for ticker, name in stock_rules:
            rule_id = str(uuid.uuid4())
            self.trading_rules[rule_id] = TradingRule(
                id=UUID(rule_id),
                ticker=ticker,
                rule_type="daily_price_limit",
                rule_name=f"{ticker} Price Limit",
                rule_description=f"Daily price movement limit for {name}",
                daily_price_limit_percent=Decimal("10.00"),
                circuit_breaker_threshold=None,
                halt_conditions=None,
                order_restrictions=None,
                is_active=True,
                effective_date=datetime.now(),
                expiry_date=None,
                source="CSE",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by=None
            )
        
        # Add general rules
        for rule_data in general_rules:
            rule = TradingRule(
                id=UUID(rule_data["id"]),
                ticker=rule_data["ticker"],
                rule_type=rule_data["rule_type"],
                rule_name=rule_data["rule_name"],
                rule_description=rule_data["rule_description"],
                daily_price_limit_percent=rule_data["daily_price_limit_percent"],
                circuit_breaker_threshold=rule_data.get("circuit_breaker_threshold"),
                halt_conditions=rule_data.get("halt_conditions"),
                order_restrictions=rule_data.get("order_restrictions"),
                is_active=rule_data["is_active"],
                effective_date=rule_data["effective_date"],
                expiry_date=rule_data.get("expiry_date"),
                source=rule_data["source"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by=UUID(rule_data["created_by"]) if rule_data.get("created_by") else None
            )
            self.trading_rules[rule.id] = rule
    
    def validate_order(self, validation: TradingRuleValidation) -> TradingRuleValidationResult:
        """Validate an order against CSE trading rules"""
        violations = []
        warnings = []
        blocked_reasons = []
        price_limits = {}
        halt_status = {}
        
        # Check if stock is halted
        halt_status = self._check_trading_halt(validation.ticker)
        if halt_status.get("is_halted"):
            blocked_reasons.append(f"Trading halted: {halt_status.get('reason', 'Unknown reason')}")
        
        # Get applicable rules for this ticker
        applicable_rules = self._get_applicable_rules(validation.ticker)
        
        for rule in applicable_rules:
            if rule.rule_type == "daily_price_limit":
                limit_result = self._validate_daily_price_limit(
                    validation, rule, validation.current_market_price, validation.daily_price_change_percent
                )
                violations.extend(limit_result.get("violations", []))
                warnings.extend(limit_result.get("warnings", []))
                if limit_result.get("blocked"):
                    blocked_reasons.append(limit_result.get("blocked_reason", "Price limit exceeded"))
                price_limits[rule.rule_type] = limit_result.get("limits", {})
            
            elif rule.rule_type == "circuit_breaker":
                circuit_result = self._validate_circuit_breaker(
                    validation, rule, validation.current_market_price, validation.daily_price_change_percent
                )
                violations.extend(circuit_result.get("violations", []))
                warnings.extend(circuit_result.get("warnings", []))
                if circuit_result.get("blocked"):
                    blocked_reasons.append(circuit_result.get("blocked_reason", "Circuit breaker triggered"))
        
        is_valid = len(blocked_reasons) == 0
        
        return TradingRuleValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings,
            blocked_reasons=blocked_reasons,
            price_limits=price_limits,
            halt_status=halt_status
        )
    
    def _get_applicable_rules(self, ticker: str) -> List[TradingRule]:
        """Get all applicable rules for a ticker (including general rules)"""
        applicable_rules = []
        
        for rule in self.trading_rules.values():
            if rule.is_active and (
                rule.ticker is None or  # General rule
                rule.ticker == ticker   # Specific rule for this ticker
            ):
                applicable_rules.append(rule)
        
        return applicable_rules
    
    def _check_trading_halt(self, ticker: str) -> Dict[str, Any]:
        """Check if a stock is currently halted"""
        for halt in self.trading_halts.values():
            if halt.ticker == ticker and halt.is_active and halt.halt_end is None:
                return {
                    "is_halted": True,
                    "halt_type": halt.halt_type,
                    "reason": halt.halt_reason,
                    "halt_start": halt.halt_start
                }
        
        return {"is_halted": False}
    
    def _validate_daily_price_limit(
        self, 
        validation: TradingRuleValidation, 
        rule: TradingRule,
        current_price: Optional[Decimal],
        daily_change_percent: Optional[Decimal]
    ) -> Dict[str, Any]:
        """Validate against daily price movement limits"""
        result = {"violations": [], "warnings": [], "blocked": False}
        
        if not rule.daily_price_limit_percent:
            return result
        
        if daily_change_percent is None:
            return result
        
        limit_percent = rule.daily_price_limit_percent
        abs_change = abs(daily_change_percent)
        
        # Check if approaching limit (80% of limit)
        warning_threshold = limit_percent * Decimal("0.8")
        if abs_change >= warning_threshold:
            result["warnings"].append(
                f"Price movement ({daily_change_percent:.2f}%) approaching daily limit ({limit_percent}%)"
            )
        
        # Check if limit exceeded
        if abs_change > limit_percent:
            result["violations"].append(
                f"Daily price limit exceeded: {daily_change_percent:.2f}% (limit: {limit_percent}%)"
            )
            result["blocked"] = True
            result["blocked_reason"] = f"Daily price limit exceeded ({daily_change_percent:.2f}% > {limit_percent}%)"
        
        result["limits"] = {
            "daily_limit_percent": limit_percent,
            "current_change_percent": daily_change_percent,
            "remaining_percent": limit_percent - abs_change
        }
        
        return result
    
    def _validate_circuit_breaker(
        self,
        validation: TradingRuleValidation,
        rule: TradingRule,
        current_price: Optional[Decimal],
        daily_change_percent: Optional[Decimal]
    ) -> Dict[str, Any]:
        """Validate against circuit breaker rules"""
        result = {"violations": [], "warnings": [], "blocked": False}
        
        if not rule.circuit_breaker_threshold:
            return result
        
        if daily_change_percent is None:
            return result
        
        threshold = rule.circuit_breaker_threshold
        
        # Circuit breaker typically triggers on significant drops
        if daily_change_percent < -threshold:
            result["violations"].append(
                f"Circuit breaker threshold exceeded: {daily_change_percent:.2f}% (threshold: {threshold}%)"
            )
            result["blocked"] = True
            result["blocked_reason"] = f"Circuit breaker triggered ({daily_change_percent:.2f}% < -{threshold}%)"
        
        # Warning when approaching circuit breaker (70% of threshold)
        warning_threshold = threshold * Decimal("0.7")
        if daily_change_percent < -warning_threshold:
            result["warnings"].append(
                f"Approaching circuit breaker threshold: {daily_change_percent:.2f}% (threshold: {threshold}%)"
            )
        
        return result
    
    def create_trading_halt(self, halt_data: Dict[str, Any]) -> TradingHalt:
        """Create a new trading halt"""
        halt_id = str(uuid.uuid4())
        halt = TradingHalt(
            id=UUID(halt_id),
            ticker=halt_data["ticker"],
            halt_type=halt_data["halt_type"],
            halt_reason=halt_data["halt_reason"],
            halt_start=halt_data["halt_start"],
            halt_end=halt_data.get("halt_end"),
            price_at_halt=halt_data.get("price_at_halt"),
            volume_at_halt=halt_data.get("volume_at_halt"),
            source=halt_data.get("source", "CSE"),
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.trading_halts[halt_id] = halt
        return halt
    
    def end_trading_halt(self, ticker: str, reason: str = "Manual end") -> Optional[TradingHalt]:
        """End an active trading halt for a stock"""
        for halt in self.trading_halts.values():
            if halt.ticker == ticker and halt.is_active and halt.halt_end is None:
                halt.halt_end = datetime.now()
                halt.is_active = False
                halt.updated_at = datetime.now()
                return halt
        return None
    
    def create_price_alert(self, alert_data: Dict[str, Any]) -> PriceMovementAlert:
        """Create a price movement alert"""
        alert_id = str(uuid.uuid4())
        alert = PriceMovementAlert(
            id=UUID(alert_id),
            ticker=alert_data["ticker"],
            alert_type=alert_data["alert_type"],
            current_price=alert_data["current_price"],
            price_change_percent=alert_data.get("price_change_percent"),
            threshold_percent=alert_data.get("threshold_percent"),
            alert_message=alert_data.get("alert_message"),
            is_triggered=alert_data.get("is_triggered", False),
            triggered_at=alert_data.get("triggered_at"),
            acknowledged_at=alert_data.get("acknowledged_at"),
            created_at=datetime.now()
        )
        
        self.price_alerts[alert_id] = alert
        return alert
    
    def log_violation(self, violation_data: Dict[str, Any]) -> TradingRuleViolation:
        """Log a trading rule violation"""
        violation_id = str(uuid.uuid4())
        violation = TradingRuleViolation(
            id=UUID(violation_id),
            rule_id=violation_data["rule_id"],
            ticker=violation_data["ticker"],
            violation_type=violation_data["violation_type"],
            violation_details=violation_data.get("violation_details"),
            order_id=violation_data.get("order_id"),
            user_id=violation_data.get("user_id"),
            price_at_violation=violation_data.get("price_at_violation"),
            price_limit=violation_data.get("price_limit"),
            violation_timestamp=datetime.now(),
            resolved_at=violation_data.get("resolved_at"),
            status=violation_data.get("status", "active")
        )
        
        self.rule_violations[violation_id] = violation
        return violation
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get compliance dashboard summary"""
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        # Get active halts
        active_halts = [
            halt for halt in self.trading_halts.values()
            if halt.is_active and halt.halt_end is None
        ]
        
        # Get recent violations (last 24 hours)
        recent_violations = [
            violation for violation in self.rule_violations.values()
            if violation.violation_timestamp >= today_start
        ]
        
        # Get triggered price alerts
        triggered_alerts = [
            alert for alert in self.price_alerts.values()
            if alert.is_triggered and alert.triggered_at and alert.triggered_at >= today_start
        ]
        
        # Get stocks nearing limits (mock data for now)
        stocks_nearing_limits = ["ATW", "IAM", "BCP"]  # Mock data
        
        return {
            "active_halts": active_halts,
            "recent_violations": recent_violations,
            "price_alerts": triggered_alerts,
            "total_violations_today": len(recent_violations),
            "total_halts_today": len([h for h in active_halts if h.halt_start >= today_start]),
            "stocks_nearing_limits": stocks_nearing_limits
        }

# Global instance
trading_rules_service = TradingRulesService() 