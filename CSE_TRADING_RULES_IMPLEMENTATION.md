# CSE Trading Rules & Compliance System Implementation

## Overview

This document describes the implementation of the CSE (Casablanca Stock Exchange) trading rules and compliance system for Casablanca Insight. The system enforces trading rules, monitors compliance, and provides educational resources for users.

## Core Components

### 1. Database Schema

#### Trading Rules Table
```sql
CREATE TABLE trading_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) REFERENCES companies(ticker),
    rule_type VARCHAR(50) NOT NULL CHECK (rule_type IN (
        'daily_price_limit', 'circuit_breaker', 'trading_halt', 
        'order_restriction', 'market_segment_rule'
    )),
    rule_name VARCHAR(255) NOT NULL,
    rule_description TEXT,
    daily_price_limit_percent DECIMAL(5,2),
    circuit_breaker_threshold DECIMAL(5,2),
    halt_conditions JSONB,
    order_restrictions JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    effective_date DATE NOT NULL,
    expiry_date DATE,
    source VARCHAR(100) DEFAULT 'CSE',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);
```

#### Trading Rule Violations Table
```sql
CREATE TABLE trading_rule_violations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id UUID REFERENCES trading_rules(id),
    ticker VARCHAR(10) REFERENCES companies(ticker),
    violation_type VARCHAR(50) NOT NULL,
    violation_details JSONB,
    order_id UUID REFERENCES paper_trading_orders(id),
    user_id UUID REFERENCES users(id),
    price_at_violation DECIMAL(12,4),
    price_limit DECIMAL(12,4),
    violation_timestamp TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'active'
);
```

#### Trading Halts Table
```sql
CREATE TABLE trading_halts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) REFERENCES companies(ticker),
    halt_type VARCHAR(50) NOT NULL CHECK (halt_type IN (
        'circuit_breaker', 'news_pending', 'regulatory', 'technical', 'volatility'
    )),
    halt_reason TEXT NOT NULL,
    halt_start TIMESTAMPTZ NOT NULL,
    halt_end TIMESTAMPTZ,
    price_at_halt DECIMAL(12,4),
    volume_at_halt BIGINT,
    source VARCHAR(100) DEFAULT 'CSE',
    is_active BOOLEAN DEFAULT TRUE
);
```

#### Price Movement Alerts Table
```sql
CREATE TABLE price_movement_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) REFERENCES companies(ticker),
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN (
        'approaching_limit', 'circuit_breaker_warning', 'volatility_alert'
    )),
    current_price DECIMAL(12,4) NOT NULL,
    price_change_percent DECIMAL(8,4),
    threshold_percent DECIMAL(8,4),
    alert_message TEXT,
    is_triggered BOOLEAN DEFAULT FALSE,
    triggered_at TIMESTAMPTZ,
    acknowledged_at TIMESTAMPTZ
);
```

### 2. Backend Implementation

#### Trading Rules Service (`apps/backend/utils/trading_rules.py`)

The `TradingRulesService` class provides:

- **Rule Validation**: Validates orders against CSE trading rules
- **Price Limit Enforcement**: Enforces daily price movement limits (±10%)
- **Circuit Breaker Logic**: Triggers halts on significant price drops (15%+)
- **Violation Logging**: Records rule violations for compliance tracking
- **Halt Management**: Creates and manages trading halts

Key methods:
```python
def validate_order(self, validation: TradingRuleValidation) -> TradingRuleValidationResult
def _validate_daily_price_limit(self, validation, rule, current_price, daily_change_percent)
def _validate_circuit_breaker(self, validation, rule, current_price, daily_change_percent)
def create_trading_halt(self, halt_data: Dict[str, Any]) -> TradingHalt
def log_violation(self, violation_data: Dict[str, Any]) -> TradingRuleViolation
```

#### Compliance Router (`apps/backend/routers/compliance.py`)

API endpoints for compliance management:

- `GET /api/compliance/rules` - Get trading rules
- `POST /api/compliance/rules` - Create new trading rule (admin)
- `POST /api/compliance/validate-order` - Validate order against rules
- `GET /api/compliance/halts` - Get trading halts
- `POST /api/compliance/halts` - Create trading halt (admin)
- `POST /api/compliance/halts/{ticker}/end` - End trading halt (admin)
- `GET /api/compliance/alerts` - Get price alerts
- `GET /api/compliance/violations` - Get rule violations
- `GET /api/compliance/summary` - Get compliance dashboard summary
- `GET /api/compliance/education/circuit-breakers` - Educational info
- `GET /api/compliance/education/price-limits` - Educational info

#### Paper Trading Integration

The paper trading system now integrates with trading rules:

```python
# In apps/backend/routers/paper_trading.py
validation = TradingRuleValidation(
    ticker=order_data.ticker,
    order_type=order_data.order_type,
    quantity=order_data.quantity,
    price=order_data.price,
    current_market_price=order_data.price,
    daily_price_change_percent=Decimal("5.0")
)

validation_result = trading_rules_service.validate_order(validation)

if not validation_result.is_valid:
    # Log violation and block order
    raise HTTPException(
        status_code=400,
        detail={
            "message": "Order blocked by CSE trading rules",
            "blocked_reasons": validation_result.blocked_reasons,
            "warnings": validation_result.warnings,
            "violations": validation_result.violations
        }
    )
```

### 3. Frontend Implementation

#### Compliance Dashboard (`apps/web/components/ComplianceDashboard.tsx`)

A comprehensive dashboard with multiple tabs:

1. **Overview Tab**: 
   - Statistics cards (active halts, violations, alerts, stocks nearing limits)
   - Active trading halts display
   - Stocks nearing daily limits

2. **Trading Halts Tab**:
   - List of all active trading halts
   - Halt details (type, reason, duration, price)

3. **Violations Tab**:
   - Recent rule violations
   - Violation details and timestamps

4. **Price Alerts Tab**:
   - Price movement alerts
   - Alert triggers and thresholds

5. **Education Tab**:
   - Circuit breaker explanations
   - Daily price limit information
   - CSE trading rules overview

#### Compliance Page (`apps/web/pages/compliance.tsx`)

Dedicated page for accessing the compliance dashboard with authentication.

### 4. Default CSE Rules

The system initializes with default CSE trading rules:

#### General Market Rules (Apply to All Stocks)
- **Daily Price Limit**: ±10% maximum daily price movement
- **Circuit Breaker**: 15% drop triggers automatic trading halt

#### Stock-Specific Rules
- **ATW** (Attijariwafa Bank): ±10% daily limit
- **IAM** (Maroc Telecom): ±10% daily limit
- **BCP** (Banque Centrale Populaire): ±10% daily limit
- **BMCE** (BMCE Bank): ±10% daily limit
- **ONA** (Omnium Nord Africain): ±10% daily limit
- **CMT** (Ciments du Maroc): ±10% daily limit
- **LAFA** (Lafarge Ciments): ±10% daily limit

### 5. Rule Validation Logic

#### Daily Price Limit Validation
```python
def _validate_daily_price_limit(self, validation, rule, current_price, daily_change_percent):
    limit_percent = rule.daily_price_limit_percent
    abs_change = abs(daily_change_percent)
    
    # Warning at 80% of limit
    warning_threshold = limit_percent * Decimal("0.8")
    if abs_change >= warning_threshold:
        result["warnings"].append(
            f"Price movement ({daily_change_percent:.2f}%) approaching daily limit ({limit_percent}%)"
        )
    
    # Block at limit exceeded
    if abs_change > limit_percent:
        result["violations"].append(
            f"Daily price limit exceeded: {daily_change_percent:.2f}% (limit: {limit_percent}%)"
        )
        result["blocked"] = True
```

#### Circuit Breaker Validation
```python
def _validate_circuit_breaker(self, validation, rule, current_price, daily_change_percent):
    threshold = rule.circuit_breaker_threshold
    
    # Warning at 70% of threshold
    warning_threshold = threshold * Decimal("0.7")
    if daily_change_percent < -warning_threshold:
        result["warnings"].append(
            f"Approaching circuit breaker threshold: {daily_change_percent:.2f}% (threshold: {threshold}%)"
        )
    
    # Block at threshold exceeded
    if daily_change_percent < -threshold:
        result["violations"].append(
            f"Circuit breaker threshold exceeded: {daily_change_percent:.2f}% (threshold: {threshold}%)"
        )
        result["blocked"] = True
```

### 6. User Education Features

#### Circuit Breaker Education
- Explanation of circuit breaker purpose
- Threshold levels (15% and 20% drops)
- Historical examples
- Trading halt durations

#### Daily Price Limits Education
- Purpose of price limits
- Standard vs. new listing limits
- Calculation methodology
- Exceptions and special cases

#### CSE Trading Rules Overview
- Order types (market, limit, stop)
- Trading hours
- Regulatory requirements

### 7. Compliance Dashboard Features

#### Real-time Monitoring
- Active trading halts display
- Stocks approaching daily limits
- Recent violations tracking
- Price movement alerts

#### Administrative Functions
- Create new trading rules
- Manage trading halts
- Monitor compliance violations
- Generate compliance reports

#### User Notifications
- Clear error messages when orders are blocked
- Warnings when approaching limits
- Educational tooltips explaining rules

### 8. Integration Points

#### Paper Trading Integration
- All orders validated against CSE rules
- Real-time rule enforcement
- Violation logging and tracking
- User feedback on blocked orders

#### Market Data Integration
- Real-time price monitoring
- Daily price change calculations
- Alert triggering based on thresholds
- Historical compliance tracking

#### User Management Integration
- Admin-only rule creation
- User-specific violation tracking
- Role-based access control
- Compliance reporting by user

### 9. Future Enhancements

#### Planned Features
1. **Real-time CSE Data Integration**: Connect to actual CSE feeds
2. **Automated Rule Updates**: Sync with CSE regulatory announcements
3. **Advanced Analytics**: Compliance trend analysis
4. **Mobile Notifications**: Real-time alerts on mobile devices
5. **API Access**: External compliance monitoring tools

#### Technical Improvements
1. **Database Optimization**: Indexing for large-scale compliance data
2. **Caching**: Performance optimization for rule lookups
3. **WebSocket Integration**: Real-time compliance updates
4. **Machine Learning**: Predictive compliance monitoring

### 10. Security Considerations

#### Access Control
- Admin-only rule creation and modification
- User-specific violation tracking
- Audit logging for all compliance actions
- Role-based dashboard access

#### Data Protection
- Encrypted storage of sensitive compliance data
- Secure API endpoints with authentication
- Compliance with data retention policies
- Regular security audits

### 11. Testing Strategy

#### Unit Tests
- Rule validation logic
- Price limit calculations
- Circuit breaker triggers
- Violation logging

#### Integration Tests
- Paper trading with rule enforcement
- API endpoint functionality
- Database operations
- Frontend-backend communication

#### User Acceptance Tests
- Compliance dashboard usability
- Order blocking scenarios
- Educational content clarity
- Administrative functions

## Conclusion

The CSE trading rules and compliance system provides a comprehensive solution for enforcing Casablanca Stock Exchange regulations in the paper trading environment. The system combines real-time rule validation, educational resources, and administrative tools to ensure users understand and comply with CSE trading rules while maintaining a safe and educational trading experience.

The implementation is modular and extensible, allowing for future enhancements such as real-time CSE data integration, advanced analytics, and mobile notifications. The system serves both educational and compliance monitoring purposes, making it valuable for both individual traders and institutional users. 