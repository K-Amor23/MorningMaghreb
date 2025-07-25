-- User Features Migration for Casablanca Insights
-- Adds watchlists and alerts functionality

-- ============================================
-- WATCHLISTS TABLE
-- ============================================

-- Watchlists table
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL DEFAULT 'My Watchlist',
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, name)
);

-- Watchlist items table
CREATE TABLE IF NOT EXISTS watchlist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    watchlist_id UUID REFERENCES watchlists(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT,
    target_price DECIMAL(10,2),
    UNIQUE(watchlist_id, company_id)
);

-- ============================================
-- ALERTS TABLE
-- ============================================

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN (
        'price_above', 'price_below', 'price_change_percent', 
        'volume_above', 'rsi_above', 'rsi_below', 'macd_crossover',
        'moving_average_crossover', 'bollinger_breakout'
    )),
    condition_value DECIMAL(10,4) NOT NULL,
    condition_operator VARCHAR(10) DEFAULT '=' CHECK (condition_operator IN ('=', '>', '<', '>=', '<=')),
    is_active BOOLEAN DEFAULT TRUE,
    is_triggered BOOLEAN DEFAULT FALSE,
    triggered_at TIMESTAMPTZ,
    notification_method VARCHAR(20) DEFAULT 'email' CHECK (notification_method IN ('email', 'push', 'sms', 'webhook')),
    notification_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Alert history table
CREATE TABLE IF NOT EXISTS alert_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
    triggered_at TIMESTAMPTZ DEFAULT NOW(),
    trigger_value DECIMAL(10,4),
    condition_value DECIMAL(10,4),
    notification_sent BOOLEAN DEFAULT FALSE,
    notification_sent_at TIMESTAMPTZ,
    notification_error TEXT
);

-- ============================================
-- USER PREFERENCES TABLE
-- ============================================

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    default_watchlist_id UUID REFERENCES watchlists(id),
    timezone VARCHAR(50) DEFAULT 'Africa/Casablanca',
    language VARCHAR(10) DEFAULT 'en',
    currency VARCHAR(3) DEFAULT 'MAD',
    theme VARCHAR(20) DEFAULT 'light' CHECK (theme IN ('light', 'dark', 'auto')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================

-- Watchlists indexes
CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON watchlists(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_is_public ON watchlists(is_public);
CREATE INDEX IF NOT EXISTS idx_watchlist_items_watchlist_id ON watchlist_items(watchlist_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_items_company_id ON watchlist_items(company_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_items_ticker ON watchlist_items(ticker);

-- Alerts indexes
CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_company_id ON alerts(company_id);
CREATE INDEX IF NOT EXISTS idx_alerts_ticker ON alerts(ticker);
CREATE INDEX IF NOT EXISTS idx_alerts_is_active ON alerts(is_active);
CREATE INDEX IF NOT EXISTS idx_alerts_is_triggered ON alerts(is_triggered);
CREATE INDEX IF NOT EXISTS idx_alerts_alert_type ON alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_alert_history_alert_id ON alert_history(alert_id);
CREATE INDEX IF NOT EXISTS idx_alert_history_triggered_at ON alert_history(triggered_at);

-- User preferences indexes
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to check and trigger alerts
CREATE OR REPLACE FUNCTION check_alerts()
RETURNS TRIGGER AS $$
DECLARE
    alert_record RECORD;
    current_value DECIMAL(10,4);
    should_trigger BOOLEAN := FALSE;
BEGIN
    -- Get all active alerts for this ticker
    FOR alert_record IN 
        SELECT * FROM alerts 
        WHERE ticker = NEW.ticker 
        AND is_active = TRUE 
        AND is_triggered = FALSE
    LOOP
        -- Determine current value based on alert type
        CASE alert_record.alert_type
            WHEN 'price_above', 'price_below' THEN
                current_value := NEW.close;
            WHEN 'price_change_percent' THEN
                -- Calculate price change percentage (would need previous price)
                current_value := 0; -- Placeholder
            WHEN 'volume_above' THEN
                current_value := NEW.volume;
            WHEN 'rsi_above', 'rsi_below' THEN
                -- Get RSI from analytics_signals table
                SELECT rsi INTO current_value 
                FROM analytics_signals 
                WHERE ticker = NEW.ticker 
                AND date = NEW.date 
                LIMIT 1;
            WHEN 'macd_crossover' THEN
                -- Check MACD crossover (would need previous values)
                current_value := 0; -- Placeholder
            WHEN 'moving_average_crossover' THEN
                -- Check moving average crossover
                current_value := 0; -- Placeholder
            WHEN 'bollinger_breakout' THEN
                -- Check Bollinger Bands breakout
                current_value := 0; -- Placeholder
        END CASE;
        
        -- Check if condition is met
        CASE alert_record.condition_operator
            WHEN '=' THEN should_trigger := (current_value = alert_record.condition_value);
            WHEN '>' THEN should_trigger := (current_value > alert_record.condition_value);
            WHEN '<' THEN should_trigger := (current_value < alert_record.condition_value);
            WHEN '>=' THEN should_trigger := (current_value >= alert_record.condition_value);
            WHEN '<=' THEN should_trigger := (current_value <= alert_record.condition_value);
        END CASE;
        
        -- Trigger alert if condition is met
        IF should_trigger THEN
            -- Update alert as triggered
            UPDATE alerts 
            SET is_triggered = TRUE, triggered_at = NOW()
            WHERE id = alert_record.id;
            
            -- Insert into alert history
            INSERT INTO alert_history (
                alert_id, triggered_at, trigger_value, condition_value
            ) VALUES (
                alert_record.id, NOW(), current_value, alert_record.condition_value
            );
        END IF;
    END LOOP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- TRIGGERS
-- ============================================

-- Triggers for updated_at
CREATE TRIGGER update_watchlists_updated_at 
    BEFORE UPDATE ON watchlists 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alerts_updated_at 
    BEFORE UPDATE ON alerts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at 
    BEFORE UPDATE ON user_preferences 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for alert checking
CREATE TRIGGER check_alerts_trigger
    AFTER INSERT OR UPDATE ON company_prices
    FOR EACH ROW
    EXECUTE FUNCTION check_alerts();

-- ============================================
-- VIEWS
-- ============================================

-- View for user watchlists with company info
CREATE OR REPLACE VIEW user_watchlists_view AS
SELECT 
    w.id as watchlist_id,
    w.user_id,
    w.name as watchlist_name,
    w.description,
    w.is_public,
    w.created_at as watchlist_created_at,
    wi.id as item_id,
    wi.ticker,
    wi.added_at,
    wi.notes,
    wi.target_price,
    c.name as company_name,
    c.sector,
    c.market_cap_billion,
    cp.close as current_price,
    cp.change_1d_percent as price_change_percent
FROM watchlists w
LEFT JOIN watchlist_items wi ON w.id = wi.watchlist_id
LEFT JOIN companies c ON wi.company_id = c.id
LEFT JOIN company_prices cp ON wi.ticker = cp.ticker 
    AND cp.date = (SELECT MAX(date) FROM company_prices WHERE ticker = wi.ticker)
ORDER BY w.created_at DESC, wi.added_at DESC;

-- View for active alerts with company info
CREATE OR REPLACE VIEW active_alerts_view AS
SELECT 
    a.id as alert_id,
    a.user_id,
    a.ticker,
    a.alert_type,
    a.condition_value,
    a.condition_operator,
    a.is_active,
    a.is_triggered,
    a.triggered_at,
    a.notification_method,
    a.created_at as alert_created_at,
    c.name as company_name,
    c.sector,
    cp.close as current_price,
    cp.change_1d_percent as price_change_percent
FROM alerts a
LEFT JOIN companies c ON a.company_id = c.id
LEFT JOIN company_prices cp ON a.ticker = cp.ticker 
    AND cp.date = (SELECT MAX(date) FROM company_prices WHERE ticker = a.ticker)
WHERE a.is_active = TRUE
ORDER BY a.created_at DESC;

-- View for alert history
CREATE OR REPLACE VIEW alert_history_view AS
SELECT 
    ah.id,
    ah.alert_id,
    ah.triggered_at,
    ah.trigger_value,
    ah.condition_value,
    ah.notification_sent,
    ah.notification_sent_at,
    ah.notification_error,
    a.user_id,
    a.ticker,
    a.alert_type,
    a.condition_operator,
    c.name as company_name
FROM alert_history ah
JOIN alerts a ON ah.alert_id = a.id
LEFT JOIN companies c ON a.company_id = c.id
ORDER BY ah.triggered_at DESC;

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on tables
ALTER TABLE watchlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlist_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Watchlists policies
CREATE POLICY "Users can view their own watchlists" ON watchlists
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own watchlists" ON watchlists
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own watchlists" ON watchlists
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own watchlists" ON watchlists
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view public watchlists" ON watchlists
    FOR SELECT USING (is_public = TRUE);

-- Watchlist items policies
CREATE POLICY "Users can view items in their watchlists" ON watchlist_items
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM watchlists w 
            WHERE w.id = watchlist_items.watchlist_id 
            AND w.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert items in their watchlists" ON watchlist_items
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM watchlists w 
            WHERE w.id = watchlist_items.watchlist_id 
            AND w.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update items in their watchlists" ON watchlist_items
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM watchlists w 
            WHERE w.id = watchlist_items.watchlist_id 
            AND w.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete items in their watchlists" ON watchlist_items
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM watchlists w 
            WHERE w.id = watchlist_items.watchlist_id 
            AND w.user_id = auth.uid()
        )
    );

-- Alerts policies
CREATE POLICY "Users can view their own alerts" ON alerts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own alerts" ON alerts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own alerts" ON alerts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own alerts" ON alerts
    FOR DELETE USING (auth.uid() = user_id);

-- Alert history policies
CREATE POLICY "Users can view their own alert history" ON alert_history
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM alerts a 
            WHERE a.id = alert_history.alert_id 
            AND a.user_id = auth.uid()
        )
    );

-- User preferences policies
CREATE POLICY "Users can view their own preferences" ON user_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own preferences" ON user_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own preferences" ON user_preferences
    FOR UPDATE USING (auth.uid() = user_id);

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON TABLE watchlists IS 'User watchlists for tracking companies';
COMMENT ON TABLE watchlist_items IS 'Individual companies in watchlists';
COMMENT ON TABLE alerts IS 'User alerts for price and technical indicator conditions';
COMMENT ON TABLE alert_history IS 'History of triggered alerts';
COMMENT ON TABLE user_preferences IS 'User preferences and notification settings';

COMMENT ON COLUMN alerts.alert_type IS 'Type of alert: price_above, price_below, price_change_percent, volume_above, rsi_above, rsi_below, macd_crossover, moving_average_crossover, bollinger_breakout';
COMMENT ON COLUMN alerts.condition_operator IS 'Comparison operator: =, >, <, >=, <=';
COMMENT ON COLUMN alerts.notification_method IS 'How to notify user: email, push, sms, webhook'; 