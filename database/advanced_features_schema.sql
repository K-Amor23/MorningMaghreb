-- Advanced Features Database Schema
-- Social Features, Premium Analytics, Data Expansion, Admin Dashboard

-- ============================================================================
-- 1. SOCIAL FEATURES
-- ============================================================================

-- User Follows System
CREATE TABLE user_follows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    follower_id UUID REFERENCES users(id) ON DELETE CASCADE,
    following_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(follower_id, following_id)
);

CREATE INDEX idx_user_follows_follower ON user_follows (follower_id);
CREATE INDEX idx_user_follows_following ON user_follows (following_id);

-- Shared Watchlists
CREATE TABLE shared_watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    follower_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE shared_watchlist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    watchlist_id UUID REFERENCES shared_watchlists(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT,
    UNIQUE(watchlist_id, ticker)
);

CREATE INDEX idx_shared_watchlists_user_id ON shared_watchlists (user_id);
CREATE INDEX idx_shared_watchlists_public ON shared_watchlists (is_public) WHERE is_public = TRUE;
CREATE INDEX idx_shared_watchlist_items_watchlist ON shared_watchlist_items (watchlist_id);

-- Leaderboards
CREATE TABLE leaderboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    leaderboard_type VARCHAR(50) NOT NULL CHECK (leaderboard_type IN ('portfolio_performance', 'trading_accuracy', 'prediction_accuracy', 'community_contribution')),
    score DECIMAL(15,4) NOT NULL,
    rank INTEGER,
    period VARCHAR(20) NOT NULL CHECK (period IN ('daily', 'weekly', 'monthly', 'yearly')),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_leaderboards_user_type ON leaderboards (user_id, leaderboard_type);
CREATE INDEX idx_leaderboards_type_period ON leaderboards (leaderboard_type, period, period_start);
CREATE INDEX idx_leaderboards_rank ON leaderboards (leaderboard_type, period, rank) WHERE rank IS NOT NULL;

-- Social Activity Feed
CREATE TABLE social_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL CHECK (activity_type IN ('watchlist_created', 'prediction_made', 'portfolio_shared', 'comment_posted', 'achievement_unlocked')),
    target_id UUID, -- ID of the target entity (watchlist, prediction, etc.)
    target_type VARCHAR(50), -- Type of target entity
    content TEXT,
    metadata JSONB DEFAULT '{}',
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_social_activities_user_id ON social_activities (user_id);
CREATE INDEX idx_social_activities_type ON social_activities (activity_type);
CREATE INDEX idx_social_activities_public ON social_activities (is_public, created_at DESC) WHERE is_public = TRUE;

-- ============================================================================
-- 2. PREMIUM ANALYTICS - ML-BASED SIGNALS
-- ============================================================================

-- ML Prediction Models
CREATE TABLE ml_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(255) NOT NULL,
    model_type VARCHAR(50) NOT NULL CHECK (model_type IN ('price_prediction', 'volatility_forecast', 'sector_rotation', 'risk_assessment', 'sentiment_analysis')),
    version VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'training' CHECK (status IN ('training', 'active', 'deprecated', 'failed')),
    accuracy_score DECIMAL(5,4),
    training_data_size INTEGER,
    last_trained TIMESTAMPTZ,
    hyperparameters JSONB DEFAULT '{}',
    model_path VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ml_models_type_status ON ml_models (model_type, status);
CREATE INDEX idx_ml_models_active ON ml_models (model_type, status) WHERE status = 'active';

-- ML Predictions
CREATE TABLE ml_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID REFERENCES ml_models(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    prediction_type VARCHAR(50) NOT NULL CHECK (prediction_type IN ('price_target', 'volatility', 'trend_direction', 'risk_score', 'sentiment_score')),
    predicted_value DECIMAL(15,4) NOT NULL,
    confidence_score DECIMAL(5,4) NOT NULL,
    prediction_horizon INTEGER NOT NULL, -- Days into the future
    prediction_date DATE NOT NULL,
    actual_value DECIMAL(15,4),
    accuracy_score DECIMAL(5,4),
    features_used JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ml_predictions_ticker_date ON ml_predictions (ticker, prediction_date);
CREATE INDEX idx_ml_predictions_model_type ON ml_predictions (model_id, prediction_type);
CREATE INDEX idx_ml_predictions_confidence ON ml_predictions (confidence_score DESC) WHERE confidence_score > 0.7;

-- Portfolio Optimization Results
CREATE TABLE portfolio_optimizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    optimization_type VARCHAR(50) NOT NULL CHECK (optimization_type IN ('markowitz', 'black_litterman', 'risk_parity', 'maximum_sharpe', 'minimum_variance')),
    target_return DECIMAL(5,4),
    risk_tolerance DECIMAL(5,4),
    time_horizon INTEGER, -- Days
    constraints JSONB DEFAULT '{}', -- Sector limits, position limits, etc.
    optimal_weights JSONB NOT NULL, -- {ticker: weight}
    expected_return DECIMAL(5,4),
    expected_volatility DECIMAL(5,4),
    sharpe_ratio DECIMAL(5,4),
    max_drawdown DECIMAL(5,4),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_portfolio_optimizations_user_id ON portfolio_optimizations (user_id);
CREATE INDEX idx_portfolio_optimizations_type ON portfolio_optimizations (optimization_type);

-- ============================================================================
-- 3. DATA EXPANSION - ADDITIONAL FINANCIAL INSTRUMENTS
-- ============================================================================

-- Bonds Table
CREATE TABLE bonds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bond_code VARCHAR(20) UNIQUE NOT NULL,
    issuer_name VARCHAR(255) NOT NULL,
    issuer_type VARCHAR(50) CHECK (issuer_type IN ('government', 'corporate', 'municipal', 'supranational')),
    bond_type VARCHAR(50) CHECK (bond_type IN ('fixed_rate', 'floating_rate', 'zero_coupon', 'convertible')),
    face_value DECIMAL(15,2) NOT NULL,
    coupon_rate DECIMAL(5,4),
    maturity_date DATE NOT NULL,
    issue_date DATE,
    yield_to_maturity DECIMAL(5,4),
    credit_rating VARCHAR(10),
    currency VARCHAR(3) DEFAULT 'MAD',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bonds_issuer_type ON bonds (issuer_type);
CREATE INDEX idx_bonds_maturity_date ON bonds (maturity_date);
CREATE INDEX idx_bonds_active ON bonds (is_active) WHERE is_active = TRUE;

-- Bond Prices
CREATE TABLE bond_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bond_code VARCHAR(20) REFERENCES bonds(bond_code) ON DELETE CASCADE,
    price DECIMAL(15,4) NOT NULL,
    yield DECIMAL(5,4),
    volume BIGINT,
    trade_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bond_prices_bond_date ON bond_prices (bond_code, trade_date DESC);

-- ETFs Table
CREATE TABLE etfs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    asset_class VARCHAR(50) CHECK (asset_class IN ('equity', 'fixed_income', 'commodity', 'real_estate', 'mixed')),
    investment_strategy VARCHAR(100),
    expense_ratio DECIMAL(5,4),
    total_assets DECIMAL(20,2),
    inception_date DATE,
    benchmark_index VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_etfs_asset_class ON etfs (asset_class);
CREATE INDEX idx_etfs_active ON etfs (is_active) WHERE is_active = TRUE;

-- ETF Holdings
CREATE TABLE etf_holdings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    etf_ticker VARCHAR(10) REFERENCES etfs(ticker) ON DELETE CASCADE,
    holding_ticker VARCHAR(10),
    holding_name VARCHAR(255),
    weight DECIMAL(5,4) NOT NULL,
    shares_held BIGINT,
    market_value DECIMAL(15,2),
    as_of_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_etf_holdings_etf_date ON etf_holdings (etf_ticker, as_of_date);
CREATE INDEX idx_etf_holdings_weight ON etf_holdings (etf_ticker, weight DESC);

-- Commodities Table
CREATE TABLE commodities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commodity_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) CHECK (category IN ('energy', 'metals', 'agriculture', 'livestock')),
    unit VARCHAR(20) NOT NULL, -- barrel, ounce, ton, etc.
    exchange VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_commodities_category ON commodities (category);
CREATE INDEX idx_commodities_active ON commodities (is_active) WHERE is_active = TRUE;

-- Commodity Prices
CREATE TABLE commodity_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commodity_code VARCHAR(20) REFERENCES commodities(commodity_code) ON DELETE CASCADE,
    price DECIMAL(15,4) NOT NULL,
    volume BIGINT,
    open_interest INTEGER,
    trade_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_commodity_prices_commodity_date ON commodity_prices (commodity_code, trade_date DESC);

-- ============================================================================
-- 4. ADMIN DASHBOARD ENHANCEMENTS
-- ============================================================================

-- User Analytics
CREATE TABLE user_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255),
    page_visited VARCHAR(255),
    action_type VARCHAR(50) CHECK (action_type IN ('view', 'click', 'search', 'export', 'api_call')),
    action_data JSONB DEFAULT '{}',
    user_agent TEXT,
    ip_address INET,
    session_duration INTEGER, -- seconds
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_user_analytics_user_id ON user_analytics (user_id);
CREATE INDEX idx_user_analytics_page_action ON user_analytics (page_visited, action_type);
CREATE INDEX idx_user_analytics_created ON user_analytics (created_at DESC);

-- Data Ingestion Monitoring
CREATE TABLE data_ingestion_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_name VARCHAR(100) NOT NULL,
    data_type VARCHAR(50) NOT NULL CHECK (data_type IN ('market_data', 'financial_reports', 'economic_data', 'news', 'sentiment')),
    ingestion_type VARCHAR(50) NOT NULL CHECK (ingestion_type IN ('scheduled', 'manual', 'real_time', 'batch')),
    records_processed INTEGER NOT NULL,
    records_successful INTEGER NOT NULL,
    records_failed INTEGER DEFAULT 0,
    processing_time_ms INTEGER,
    file_size_bytes BIGINT,
    error_messages TEXT[],
    metadata JSONB DEFAULT '{}',
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_data_ingestion_logs_source_type ON data_ingestion_logs (source_name, data_type);
CREATE INDEX idx_data_ingestion_logs_started ON data_ingestion_logs (started_at DESC);
CREATE INDEX idx_data_ingestion_logs_success_rate ON data_ingestion_logs (source_name, (records_successful::float / records_processed::float));

-- System Performance Metrics
CREATE TABLE system_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    metric_unit VARCHAR(20),
    component VARCHAR(50) CHECK (component IN ('api', 'database', 'etl', 'frontend', 'cache')),
    severity VARCHAR(20) CHECK (severity IN ('info', 'warning', 'error', 'critical')),
    tags JSONB DEFAULT '{}',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_system_performance_metric_component ON system_performance (metric_name, component);
CREATE INDEX idx_system_performance_recorded ON system_performance (recorded_at DESC);
CREATE INDEX idx_system_performance_severity ON system_performance (severity, recorded_at DESC) WHERE severity IN ('error', 'critical');

-- ============================================================================
-- 5. VIEWS FOR ANALYTICS
-- ============================================================================

-- User Engagement Summary
CREATE VIEW user_engagement_summary AS
SELECT 
    u.id as user_id,
    u.email,
    up.subscription_tier,
    COUNT(DISTINCT ua.session_id) as total_sessions,
    AVG(ua.session_duration) as avg_session_duration,
    COUNT(ua.id) as total_actions,
    MAX(ua.created_at) as last_activity,
    COUNT(DISTINCT w.ticker) as watchlist_items,
    COUNT(DISTINCT pa.id) as active_alerts
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
LEFT JOIN user_analytics ua ON u.id = ua.user_id
LEFT JOIN watchlists w ON u.id = w.user_id
LEFT JOIN price_alerts pa ON u.id = pa.user_id AND pa.is_active = TRUE
GROUP BY u.id, u.email, up.subscription_tier;

-- Data Quality Summary
CREATE VIEW data_quality_summary AS
SELECT 
    data_type,
    COUNT(*) as total_records,
    COUNT(CASE WHEN status = 'valid' THEN 1 END) as valid_records,
    COUNT(CASE WHEN status = 'invalid' THEN 1 END) as invalid_records,
    ROUND(
        COUNT(CASE WHEN status = 'valid' THEN 1 END)::float / COUNT(*)::float * 100, 2
    ) as quality_percentage,
    MAX(created_at) as last_updated
FROM data_quality_flags
GROUP BY data_type;

-- ML Model Performance
CREATE VIEW ml_model_performance AS
SELECT 
    mm.model_name,
    mm.model_type,
    mm.version,
    mm.accuracy_score as training_accuracy,
    AVG(mp.accuracy_score) as prediction_accuracy,
    COUNT(mp.id) as total_predictions,
    COUNT(CASE WHEN mp.actual_value IS NOT NULL THEN 1 END) as completed_predictions,
    MAX(mp.created_at) as last_prediction
FROM ml_models mm
LEFT JOIN ml_predictions mp ON mm.id = mp.model_id
WHERE mm.status = 'active'
GROUP BY mm.id, mm.model_name, mm.model_type, mm.version, mm.accuracy_score;

-- ============================================================================
-- 6. FUNCTIONS FOR ADVANCED ANALYTICS
-- ============================================================================

-- Function to calculate user engagement score
CREATE OR REPLACE FUNCTION calculate_user_engagement_score(user_uuid UUID)
RETURNS DECIMAL AS $$
DECLARE
    engagement_score DECIMAL;
BEGIN
    SELECT 
        (COALESCE(session_count, 0) * 0.3 +
         COALESCE(action_count, 0) * 0.2 +
         COALESCE(watchlist_count, 0) * 0.2 +
         COALESCE(alert_count, 0) * 0.15 +
         COALESCE(avg_session_duration, 0) / 3600 * 0.15)::DECIMAL(5,2)
    INTO engagement_score
    FROM (
        SELECT 
            COUNT(DISTINCT session_id) as session_count,
            COUNT(*) as action_count,
            (SELECT COUNT(*) FROM watchlists WHERE user_id = user_uuid) as watchlist_count,
            (SELECT COUNT(*) FROM price_alerts WHERE user_id = user_uuid AND is_active = TRUE) as alert_count,
            AVG(session_duration) as avg_session_duration
        FROM user_analytics 
        WHERE user_id = user_uuid
    ) stats;
    
    RETURN COALESCE(engagement_score, 0);
END;
$$ LANGUAGE plpgsql;

-- Function to get top performing users
CREATE OR REPLACE FUNCTION get_top_performing_users(limit_count INTEGER DEFAULT 10)
RETURNS TABLE (
    user_id UUID,
    email VARCHAR,
    engagement_score DECIMAL,
    subscription_tier VARCHAR,
    last_activity TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id,
        u.email,
        calculate_user_engagement_score(u.id) as engagement_score,
        up.subscription_tier,
        MAX(ua.created_at) as last_activity
    FROM users u
    LEFT JOIN user_profiles up ON u.id = up.user_id
    LEFT JOIN user_analytics ua ON u.id = ua.user_id
    GROUP BY u.id, u.email, up.subscription_tier
    ORDER BY calculate_user_engagement_score(u.id) DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate data freshness score
CREATE OR REPLACE FUNCTION calculate_data_freshness_score()
RETURNS DECIMAL AS $$
DECLARE
    freshness_score DECIMAL;
BEGIN
    SELECT 
        AVG(
            CASE 
                WHEN EXTRACT(EPOCH FROM (NOW() - last_updated)) < 3600 THEN 1.0  -- Less than 1 hour
                WHEN EXTRACT(EPOCH FROM (NOW() - last_updated)) < 86400 THEN 0.8  -- Less than 1 day
                WHEN EXTRACT(EPOCH FROM (NOW() - last_updated)) < 604800 THEN 0.6  -- Less than 1 week
                ELSE 0.3
            END
        ) * 100
    INTO freshness_score
    FROM data_quality_summary;
    
    RETURN COALESCE(freshness_score, 0);
END;
$$ LANGUAGE plpgsql; 