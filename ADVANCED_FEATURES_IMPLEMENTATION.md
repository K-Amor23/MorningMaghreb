# Advanced Features Implementation Guide

## Overview

This document outlines the implementation of advanced features for the Casablanca Insights platform, including social features, premium analytics, data expansion, and admin dashboard enhancements.

## 🚀 **SOCIAL FEATURES**

### **1. User Follows System**

**Database Schema:**
```sql
-- User Follows System
CREATE TABLE user_follows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    follower_id UUID REFERENCES users(id) ON DELETE CASCADE,
    following_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(follower_id, following_id)
);
```

**API Endpoints:**
- `POST /api/social/follow/{user_id}` - Follow a user
- `DELETE /api/social/unfollow/{user_id}` - Unfollow a user
- `GET /api/social/followers` - Get user's followers
- `GET /api/social/following` - Get users being followed

**Features:**
- Follow/unfollow other investors
- View followers and following lists
- Social activity feed integration
- Privacy controls

### **2. Shared Watchlists**

**Database Schema:**
```sql
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
```

**API Endpoints:**
- `POST /api/social/watchlists` - Create shared watchlist
- `POST /api/social/watchlists/{watchlist_id}/items` - Add ticker to watchlist
- `GET /api/social/watchlists/public` - Get public watchlists
- `GET /api/social/watchlists/{watchlist_id}/items` - Get watchlist items

**Features:**
- Create and share watchlists
- Public/private visibility controls
- Follow other users' watchlists
- Featured watchlists for discovery

### **3. Leaderboards**

**Database Schema:**
```sql
-- Leaderboards
CREATE TABLE leaderboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    leaderboard_type VARCHAR(50) NOT NULL,
    score DECIMAL(15,4) NOT NULL,
    rank INTEGER,
    period VARCHAR(20) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**API Endpoints:**
- `POST /api/social/leaderboards/update` - Update leaderboard score
- `GET /api/social/leaderboards/{leaderboard_type}` - Get leaderboard rankings

**Leaderboard Types:**
- Portfolio Performance
- Trading Accuracy
- Prediction Accuracy
- Community Contribution

**Features:**
- Daily, weekly, monthly, yearly rankings
- Multiple leaderboard categories
- Real-time score updates
- Achievement tracking

### **4. Social Activity Feed**

**Database Schema:**
```sql
-- Social Activity Feed
CREATE TABLE social_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL,
    target_id UUID,
    target_type VARCHAR(50),
    content TEXT,
    metadata JSONB DEFAULT '{}',
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Activity Types:**
- `watchlist_created` - User created a shared watchlist
- `prediction_made` - User made a price prediction
- `portfolio_shared` - User shared portfolio performance
- `comment_posted` - User posted a comment
- `achievement_unlocked` - User unlocked an achievement

**API Endpoints:**
- `GET /api/social/feed` - Get social activity feed
- `POST /api/social/activities` - Create social activity

---

## 🧠 **PREMIUM ANALYTICS**

### **1. ML-Based Signals**

**Database Schema:**
```sql
-- ML Prediction Models
CREATE TABLE ml_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(255) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'training',
    accuracy_score DECIMAL(5,4),
    training_data_size INTEGER,
    last_trained TIMESTAMPTZ,
    hyperparameters JSONB DEFAULT '{}',
    model_path VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ML Predictions
CREATE TABLE ml_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID REFERENCES ml_models(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    prediction_type VARCHAR(50) NOT NULL,
    predicted_value DECIMAL(15,4) NOT NULL,
    confidence_score DECIMAL(5,4) NOT NULL,
    prediction_horizon INTEGER NOT NULL,
    prediction_date DATE NOT NULL,
    actual_value DECIMAL(15,4),
    accuracy_score DECIMAL(5,4),
    features_used JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Model Types:**
- `price_prediction` - Stock price predictions
- `volatility_forecast` - Volatility forecasting
- `sector_rotation` - Sector rotation signals
- `risk_assessment` - Risk assessment models
- `sentiment_analysis` - News sentiment analysis

**Prediction Types:**
- `price_target` - Price target predictions
- `volatility` - Volatility forecasts
- `trend_direction` - Trend direction signals
- `risk_score` - Risk scoring
- `sentiment_score` - Sentiment scores

**API Endpoints:**
- `POST /api/premium-analytics/predictions/price` - Generate price prediction
- `POST /api/premium-analytics/predictions/volatility` - Generate volatility forecast
- `GET /api/premium-analytics/signals/{ticker}` - Get ML signals for ticker

### **2. Portfolio Optimization**

**Database Schema:**
```sql
-- Portfolio Optimization Results
CREATE TABLE portfolio_optimizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    optimization_type VARCHAR(50) NOT NULL,
    target_return DECIMAL(5,4),
    risk_tolerance DECIMAL(5,4),
    time_horizon INTEGER,
    constraints JSONB DEFAULT '{}',
    optimal_weights JSONB NOT NULL,
    expected_return DECIMAL(5,4),
    expected_volatility DECIMAL(5,4),
    sharpe_ratio DECIMAL(5,4),
    max_drawdown DECIMAL(5,4),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Optimization Types:**
- `markowitz` - Markowitz mean-variance optimization
- `black_litterman` - Black-Litterman model
- `risk_parity` - Risk parity optimization
- `maximum_sharpe` - Maximum Sharpe ratio
- `minimum_variance` - Minimum variance

**API Endpoints:**
- `POST /api/premium-analytics/optimization/markowitz` - Markowitz optimization
- `POST /api/premium-analytics/optimization/black-litterman` - Black-Litterman optimization
- `GET /api/premium-analytics/optimizations` - Get user optimizations

**Features:**
- Mean-variance optimization
- Black-Litterman model with views
- Risk tolerance customization
- Sector and position constraints
- Performance metrics calculation

---

## 📊 **DATA EXPANSION**

### **1. Bonds**

**Database Schema:**
```sql
-- Bonds Table
CREATE TABLE bonds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bond_code VARCHAR(20) UNIQUE NOT NULL,
    issuer_name VARCHAR(255) NOT NULL,
    issuer_type VARCHAR(50),
    bond_type VARCHAR(50),
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
```

**Bond Types:**
- Government bonds
- Corporate bonds
- Municipal bonds
- Supranational bonds

**Features:**
- Yield curve analysis
- Credit rating tracking
- Maturity date management
- Price and yield history

### **2. ETFs**

**Database Schema:**
```sql
-- ETFs Table
CREATE TABLE etfs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    asset_class VARCHAR(50),
    investment_strategy VARCHAR(100),
    expense_ratio DECIMAL(5,4),
    total_assets DECIMAL(20,2),
    inception_date DATE,
    benchmark_index VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

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
```

**Asset Classes:**
- Equity ETFs
- Fixed Income ETFs
- Commodity ETFs
- Real Estate ETFs
- Mixed ETFs

**Features:**
- Holdings analysis
- Expense ratio tracking
- Asset allocation breakdown
- Performance comparison

### **3. Commodities**

**Database Schema:**
```sql
-- Commodities Table
CREATE TABLE commodities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commodity_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50),
    unit VARCHAR(20) NOT NULL,
    exchange VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

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
```

**Commodity Categories:**
- Energy (oil, gas, coal)
- Metals (gold, silver, copper)
- Agriculture (wheat, corn, soybeans)
- Livestock (cattle, hogs)

**Features:**
- Price tracking
- Volume analysis
- Open interest monitoring
- Category-based filtering

---

## 🛠 **ADMIN DASHBOARD ENHANCEMENTS**

### **1. User Analytics**

**Database Schema:**
```sql
-- User Analytics
CREATE TABLE user_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255),
    page_visited VARCHAR(255),
    action_type VARCHAR(50),
    action_data JSONB DEFAULT '{}',
    user_agent TEXT,
    ip_address INET,
    session_duration INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Analytics Features:**
- User engagement tracking
- Session duration analysis
- Page visit patterns
- Action type distribution
- Retention analysis

**API Endpoints:**
- `POST /api/admin-dashboard/analytics/track` - Track user activity
- `GET /api/admin-dashboard/analytics/engagement` - Get engagement metrics
- `GET /api/admin-dashboard/analytics/retention` - Get retention analysis
- `GET /api/admin-dashboard/analytics/top-users` - Get top performing users

### **2. Data Ingestion Monitoring**

**Database Schema:**
```sql
-- Data Ingestion Monitoring
CREATE TABLE data_ingestion_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_name VARCHAR(100) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    ingestion_type VARCHAR(50) NOT NULL,
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
```

**Monitoring Features:**
- Ingestion job tracking
- Success rate monitoring
- Processing time analysis
- Error tracking and reporting
- Source-specific metrics

**API Endpoints:**
- `POST /api/admin-dashboard/ingestion/log` - Log data ingestion
- `PUT /api/admin-dashboard/ingestion/{log_id}/complete` - Complete ingestion
- `GET /api/admin-dashboard/ingestion/summary` - Get ingestion summary

### **3. System Performance Monitoring**

**Database Schema:**
```sql
-- System Performance Metrics
CREATE TABLE system_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    metric_unit VARCHAR(20),
    component VARCHAR(50),
    severity VARCHAR(20),
    tags JSONB DEFAULT '{}',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Performance Metrics:**
- API response times
- CPU and memory usage
- Database performance
- Cache hit rates
- Error rates

**API Endpoints:**
- `POST /api/admin-dashboard/performance/log` - Log performance metric
- `GET /api/admin-dashboard/performance/summary` - Get performance summary

### **4. Dashboard Overview**

**Features:**
- Real-time system health monitoring
- User engagement metrics
- Data quality assessment
- Ingestion pipeline status
- Performance trend analysis

**API Endpoints:**
- `GET /api/admin-dashboard/overview` - Get comprehensive overview
- `GET /api/admin-dashboard/data-expansion/summary` - Get data expansion summary

---

## 🔧 **IMPLEMENTATION GUIDE**

### **1. Database Setup**

Run the advanced features schema:
```bash
# Apply the advanced features schema
psql -d your_database -f database/advanced_features_schema.sql
```

### **2. Backend Services**

The following services have been implemented:

- `SocialService` - User follows, shared watchlists, leaderboards
- `PremiumAnalyticsService` - ML signals, portfolio optimization
- `DataExpansionService` - Bonds, ETFs, commodities management
- `AdminDashboardService` - User analytics, monitoring

### **3. API Routers**

New API routers have been added:

- `/api/social/*` - Social features endpoints
- `/api/premium-analytics/*` - Premium analytics endpoints
- `/api/admin-dashboard/*` - Admin dashboard endpoints

### **4. Frontend Components**

Enhanced admin dashboard component:
- `EnhancedAdminDashboard.tsx` - Comprehensive admin interface
- Tabbed interface for different monitoring areas
- Real-time metrics and charts
- Status indicators and alerts

### **5. Dependencies**

Additional Python dependencies:
```txt
numpy>=1.21.0
scipy>=1.7.0
pandas>=1.3.0
scikit-learn>=1.0.0
```

### **6. Configuration**

Environment variables for advanced features:
```env
# ML Model Configuration
ML_MODELS_PATH=/path/to/models
ML_PREDICTION_ENABLED=true
ML_CONFIDENCE_THRESHOLD=0.7

# Social Features
SOCIAL_FEATURES_ENABLED=true
MAX_WATCHLIST_ITEMS=100
MAX_FOLLOWERS=1000

# Admin Dashboard
ADMIN_ANALYTICS_ENABLED=true
PERFORMANCE_MONITORING_ENABLED=true
DATA_INGESTION_MONITORING_ENABLED=true
```

---

## 📈 **USAGE EXAMPLES**

### **Social Features**

```javascript
// Follow a user
await fetch('/api/social/follow/user123', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
});

// Create shared watchlist
await fetch('/api/social/watchlists', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({
        name: 'Tech Stocks',
        description: 'High-growth technology companies',
        is_public: true
    })
});

// Get leaderboard
const leaderboard = await fetch('/api/social/leaderboards/portfolio_performance?period=monthly');
```

### **Premium Analytics**

```javascript
// Generate price prediction
const prediction = await fetch('/api/premium-analytics/predictions/price', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({
        ticker: 'ATW',
        prediction_horizon: 30,
        confidence_threshold: 0.7
    })
});

// Portfolio optimization
const optimization = await fetch('/api/premium-analytics/optimization/markowitz', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({
        tickers: ['ATW', 'BCP', 'IAM'],
        target_return: 0.12,
        risk_tolerance: 0.5
    })
});
```

### **Admin Dashboard**

```javascript
// Track user activity
await fetch('/api/admin-dashboard/analytics/track', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({
        session_id: 'session123',
        page_visited: '/dashboard',
        action_type: 'view',
        session_duration: 300
    })
});

// Get engagement metrics
const metrics = await fetch('/api/admin-dashboard/analytics/engagement?days=30');
```

---

## 🚀 **DEPLOYMENT CHECKLIST**

### **Pre-deployment**
- [ ] Database schema applied
- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Services tested locally
- [ ] API endpoints validated

### **Deployment**
- [ ] Backend services deployed
- [ ] Database migrations applied
- [ ] Frontend components built
- [ ] API routes configured
- [ ] Monitoring enabled

### **Post-deployment**
- [ ] Admin dashboard accessible
- [ ] Social features functional
- [ ] Premium analytics working
- [ ] Data expansion operational
- [ ] Performance monitoring active

---

## 📚 **FURTHER READING**

- [Social Features API Documentation](./docs/social-api.md)
- [Premium Analytics Guide](./docs/premium-analytics.md)
- [Admin Dashboard Manual](./docs/admin-dashboard.md)
- [Data Expansion Reference](./docs/data-expansion.md)

---

**The advanced features are now ready for production deployment!** 🎉 