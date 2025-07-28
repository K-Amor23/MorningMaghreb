-- Week 3 Database Schema Updates
-- Portfolio Management, Notifications, and Risk Analytics

-- =====================================================
-- PORTFOLIO MANAGEMENT TABLES
-- =====================================================

-- Portfolios table
CREATE TABLE IF NOT EXISTS portfolios (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cash_balance DECIMAL(15,2) DEFAULT 0.0,
    total_value DECIMAL(15,2) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB
);

-- Portfolio trades table
CREATE TABLE IF NOT EXISTS portfolio_trades (
    id SERIAL PRIMARY KEY,
    portfolio_id VARCHAR(255) REFERENCES portfolios(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    quantity DECIMAL(15,4) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    trade_type VARCHAR(10) NOT NULL CHECK (trade_type IN ('buy', 'sell')),
    trade_date DATE NOT NULL,
    commission DECIMAL(10,2) DEFAULT 0.0,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- Portfolio positions table (calculated from trades)
CREATE TABLE IF NOT EXISTS portfolio_positions (
    id SERIAL PRIMARY KEY,
    portfolio_id VARCHAR(255) REFERENCES portfolios(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    quantity DECIMAL(15,4) NOT NULL,
    avg_price DECIMAL(10,2) NOT NULL,
    market_value DECIMAL(15,2) DEFAULT 0.0,
    unrealized_pnl DECIMAL(15,2) DEFAULT 0.0,
    unrealized_pnl_percent DECIMAL(5,2) DEFAULT 0.0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(portfolio_id, ticker)
);

-- Portfolio performance history
CREATE TABLE IF NOT EXISTS portfolio_performance (
    id SERIAL PRIMARY KEY,
    portfolio_id VARCHAR(255) REFERENCES portfolios(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_value DECIMAL(15,2) NOT NULL,
    total_pnl DECIMAL(15,2) NOT NULL,
    total_pnl_percent DECIMAL(5,2) NOT NULL,
    positions_count INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(portfolio_id, date)
);

-- =====================================================
-- NOTIFICATION SYSTEM TABLES
-- =====================================================

-- User notification preferences
CREATE TABLE IF NOT EXISTS user_notification_preferences (
    user_id VARCHAR(255) PRIMARY KEY,
    web_push_enabled BOOLEAN DEFAULT TRUE,
    email_enabled BOOLEAN DEFAULT TRUE,
    sms_enabled BOOLEAN DEFAULT FALSE,
    in_app_enabled BOOLEAN DEFAULT TRUE,
    price_alerts BOOLEAN DEFAULT TRUE,
    portfolio_updates BOOLEAN DEFAULT TRUE,
    market_updates BOOLEAN DEFAULT TRUE,
    news_alerts BOOLEAN DEFAULT FALSE,
    system_alerts BOOLEAN DEFAULT TRUE,
    backtest_notifications BOOLEAN DEFAULT TRUE,
    risk_alerts BOOLEAN DEFAULT TRUE,
    quiet_hours_start TIME DEFAULT '22:00',
    quiet_hours_end TIME DEFAULT '08:00',
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Push notification subscriptions
CREATE TABLE IF NOT EXISTS push_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    endpoint TEXT NOT NULL,
    p256dh VARCHAR(255) NOT NULL,
    auth VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(user_id, endpoint)
);

-- Notifications history
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    data JSONB,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE
);

-- Notification logs for analytics
CREATE TABLE IF NOT EXISTS notification_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    channels_attempted TEXT[] NOT NULL,
    success_count INTEGER NOT NULL,
    total_channels INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- RISK ANALYTICS TABLES
-- =====================================================

-- Portfolio risk metrics
CREATE TABLE IF NOT EXISTS portfolio_risk_metrics (
    id SERIAL PRIMARY KEY,
    portfolio_id VARCHAR(255) REFERENCES portfolios(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    volatility DECIMAL(5,4) NOT NULL,
    sharpe_ratio DECIMAL(5,4) NOT NULL,
    sortino_ratio DECIMAL(5,4) NOT NULL,
    max_drawdown DECIMAL(5,4) NOT NULL,
    var_95 DECIMAL(5,4) NOT NULL,
    var_99 DECIMAL(5,4) NOT NULL,
    cvar_95 DECIMAL(5,4) NOT NULL,
    beta DECIMAL(5,4) NOT NULL,
    alpha DECIMAL(5,4) NOT NULL,
    information_ratio DECIMAL(5,4) NOT NULL,
    treynor_ratio DECIMAL(5,4) NOT NULL,
    calmar_ratio DECIMAL(5,4) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(portfolio_id, date)
);

-- Concentration risk metrics
CREATE TABLE IF NOT EXISTS portfolio_concentration_risk (
    id SERIAL PRIMARY KEY,
    portfolio_id VARCHAR(255) REFERENCES portfolios(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    largest_position_weight DECIMAL(5,4) NOT NULL,
    top_5_positions_weight DECIMAL(5,4) NOT NULL,
    sector_concentration DECIMAL(5,4) NOT NULL,
    geographic_concentration DECIMAL(5,4) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(portfolio_id, date)
);

-- Liquidity risk metrics
CREATE TABLE IF NOT EXISTS portfolio_liquidity_risk (
    id SERIAL PRIMARY KEY,
    portfolio_id VARCHAR(255) REFERENCES portfolios(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    average_daily_volume DECIMAL(15,2) NOT NULL,
    liquidity_score DECIMAL(5,4) NOT NULL,
    days_to_liquidate DECIMAL(5,2) NOT NULL,
    bid_ask_spread DECIMAL(5,4) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(portfolio_id, date)
);

-- Stress test results
CREATE TABLE IF NOT EXISTS portfolio_stress_tests (
    id SERIAL PRIMARY KEY,
    portfolio_id VARCHAR(255) REFERENCES portfolios(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    scenario VARCHAR(50) NOT NULL,
    portfolio_loss DECIMAL(15,2) NOT NULL,
    portfolio_loss_percent DECIMAL(5,2) NOT NULL,
    worst_affected_positions TEXT[] NOT NULL,
    recovery_time_days INTEGER NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Watchlist risk analysis
CREATE TABLE IF NOT EXISTS watchlist_risk_analysis (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    watchlist_name VARCHAR(255) NOT NULL,
    tickers TEXT[] NOT NULL,
    watchlist_size INTEGER NOT NULL,
    total_market_cap DECIMAL(15,2) NOT NULL,
    sector_allocation JSONB NOT NULL,
    sector_concentration DECIMAL(5,4) NOT NULL,
    average_daily_volume DECIMAL(15,2) NOT NULL,
    average_volatility DECIMAL(5,4) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Portfolio indexes
CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolios_created_at ON portfolios(created_at);

-- Trade indexes
CREATE INDEX IF NOT EXISTS idx_portfolio_trades_portfolio_id ON portfolio_trades(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_trades_ticker ON portfolio_trades(ticker);
CREATE INDEX IF NOT EXISTS idx_portfolio_trades_date ON portfolio_trades(trade_date);

-- Position indexes
CREATE INDEX IF NOT EXISTS idx_portfolio_positions_portfolio_id ON portfolio_positions(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_positions_ticker ON portfolio_positions(ticker);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_portfolio_performance_portfolio_id ON portfolio_performance(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_performance_date ON portfolio_performance(date);

-- Notification indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read);

-- Push subscription indexes
CREATE INDEX IF NOT EXISTS idx_push_subscriptions_user_id ON push_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_push_subscriptions_active ON push_subscriptions(is_active);

-- Risk metrics indexes
CREATE INDEX IF NOT EXISTS idx_risk_metrics_portfolio_id ON portfolio_risk_metrics(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_risk_metrics_date ON portfolio_risk_metrics(date);

-- =====================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =====================================================

-- Function to update portfolio positions when trades are added
CREATE OR REPLACE FUNCTION update_portfolio_positions()
RETURNS TRIGGER AS $$
BEGIN
    -- Update or insert position based on trade
    INSERT INTO portfolio_positions (portfolio_id, ticker, quantity, avg_price, market_value, unrealized_pnl, unrealized_pnl_percent)
    VALUES (
        NEW.portfolio_id,
        NEW.ticker,
        CASE 
            WHEN NEW.trade_type = 'buy' THEN 
                COALESCE((SELECT quantity FROM portfolio_positions WHERE portfolio_id = NEW.portfolio_id AND ticker = NEW.ticker), 0) + NEW.quantity
            ELSE 
                COALESCE((SELECT quantity FROM portfolio_positions WHERE portfolio_id = NEW.portfolio_id AND ticker = NEW.ticker), 0) - NEW.quantity
        END,
        CASE 
            WHEN NEW.trade_type = 'buy' THEN 
                (COALESCE((SELECT avg_price * quantity FROM portfolio_positions WHERE portfolio_id = NEW.portfolio_id AND ticker = NEW.ticker), 0) + NEW.price * NEW.quantity) / 
                (COALESCE((SELECT quantity FROM portfolio_positions WHERE portfolio_id = NEW.portfolio_id AND ticker = NEW.ticker), 0) + NEW.quantity)
            ELSE 
                COALESCE((SELECT avg_price FROM portfolio_positions WHERE portfolio_id = NEW.portfolio_id AND ticker = NEW.ticker), NEW.price)
        END,
        0, -- Will be updated by separate process
        0, -- Will be updated by separate process
        0  -- Will be updated by separate process
    )
    ON CONFLICT (portfolio_id, ticker) DO UPDATE SET
        quantity = EXCLUDED.quantity,
        avg_price = EXCLUDED.avg_price,
        last_updated = NOW();
    
    -- Remove position if quantity becomes zero or negative
    DELETE FROM portfolio_positions 
    WHERE portfolio_id = NEW.portfolio_id 
    AND ticker = NEW.ticker 
    AND quantity <= 0;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for portfolio trades
CREATE TRIGGER trigger_update_portfolio_positions
    AFTER INSERT ON portfolio_trades
    FOR EACH ROW
    EXECUTE FUNCTION update_portfolio_positions();

-- Function to update portfolio total value
CREATE OR REPLACE FUNCTION update_portfolio_total_value()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE portfolios 
    SET total_value = (
        SELECT COALESCE(SUM(market_value), 0) 
        FROM portfolio_positions 
        WHERE portfolio_id = NEW.portfolio_id
    ) + cash_balance
    WHERE id = NEW.portfolio_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for portfolio positions
CREATE TRIGGER trigger_update_portfolio_total_value
    AFTER INSERT OR UPDATE ON portfolio_positions
    FOR EACH ROW
    EXECUTE FUNCTION update_portfolio_total_value();

-- =====================================================
-- SAMPLE DATA FOR TESTING
-- =====================================================

-- Insert sample portfolio
INSERT INTO portfolios (id, user_id, name, description, cash_balance) 
VALUES ('portfolio_test_user_123_1', 'test_user_123', 'Test Portfolio', 'Sample portfolio for testing', 50000.0)
ON CONFLICT (id) DO NOTHING;

-- Insert sample notification preferences
INSERT INTO user_notification_preferences (user_id, web_push_enabled, email_enabled, price_alerts, portfolio_updates)
VALUES ('test_user_123', TRUE, TRUE, TRUE, TRUE)
ON CONFLICT (user_id) DO NOTHING;

-- Insert sample push subscription
INSERT INTO push_subscriptions (user_id, endpoint, p256dh, auth)
VALUES ('test_user_123', 'https://fcm.googleapis.com/fcm/send/test', 'test_p256dh_key', 'test_auth_key')
ON CONFLICT (user_id, endpoint) DO NOTHING;

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Portfolio summary view
CREATE OR REPLACE VIEW portfolio_summary AS
SELECT 
    p.id,
    p.name,
    p.cash_balance,
    p.total_value,
    COUNT(pp.ticker) as positions_count,
    COALESCE(SUM(pp.unrealized_pnl), 0) as total_unrealized_pnl,
    COALESCE(SUM(pp.unrealized_pnl_percent * pp.market_value / NULLIF(p.total_value, 0)), 0) as weighted_pnl_percent
FROM portfolios p
LEFT JOIN portfolio_positions pp ON p.id = pp.portfolio_id
WHERE p.is_active = TRUE
GROUP BY p.id, p.name, p.cash_balance, p.total_value;

-- Recent trades view
CREATE OR REPLACE VIEW recent_trades AS
SELECT 
    pt.portfolio_id,
    pt.ticker,
    pt.quantity,
    pt.price,
    pt.trade_type,
    pt.trade_date,
    pt.commission,
    pt.notes,
    pt.created_at
FROM portfolio_trades pt
ORDER BY pt.created_at DESC
LIMIT 100;

-- Notification summary view
CREATE OR REPLACE VIEW notification_summary AS
SELECT 
    user_id,
    COUNT(*) as total_notifications,
    COUNT(*) FILTER (WHERE read = TRUE) as read_notifications,
    COUNT(*) FILTER (WHERE read = FALSE) as unread_notifications,
    MAX(created_at) as last_notification
FROM notifications
GROUP BY user_id;

-- =====================================================
-- CLEANUP AND MAINTENANCE
-- =====================================================

-- Function to clean up old data
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Delete notifications older than 90 days
    DELETE FROM notifications WHERE created_at < NOW() - INTERVAL '90 days';
    
    -- Delete notification logs older than 30 days
    DELETE FROM notification_logs WHERE timestamp < NOW() - INTERVAL '30 days';
    
    -- Delete performance data older than 2 years
    DELETE FROM portfolio_performance WHERE date < CURRENT_DATE - INTERVAL '2 years';
    
    -- Delete risk metrics older than 1 year
    DELETE FROM portfolio_risk_metrics WHERE date < CURRENT_DATE - INTERVAL '1 year';
    DELETE FROM portfolio_concentration_risk WHERE date < CURRENT_DATE - INTERVAL '1 year';
    DELETE FROM portfolio_liquidity_risk WHERE date < CURRENT_DATE - INTERVAL '1 year';
    DELETE FROM portfolio_stress_tests WHERE date < CURRENT_DATE - INTERVAL '1 year';
END;
$$ LANGUAGE plpgsql;

-- Schedule cleanup (run this manually or set up a cron job)
-- SELECT cleanup_old_data();

COMMIT; 