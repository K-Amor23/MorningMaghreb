# 🚀 Upcoming Phases Roadmap - Casablanca Insights

This document outlines the implementation roadmap for Weeks 2 and 3, focusing on user features and advanced analytics capabilities.

## 📅 Phase Overview

| Phase | Timeline | Focus | Key Deliverables |
|-------|----------|-------|------------------|
| **Week 1** | Complete | Production Deployment & Monitoring | ✅ Production-ready platform |
| **Week 2** | Next | User Features & Authentication | 🔄 User management, watchlists, alerts |
| **Week 3** | Future | Advanced Analytics & Portfolio | 📊 AI signals, backtesting, paper trading |

---

## 🎯 Week 2: User Features & Authentication

### 📋 Objectives
- Enable production Supabase Auth
- Implement user management features
- Add watchlists and alerts
- Enable real-time push notifications
- Start mobile PWA integration

### 🔐 Authentication & User Management

#### 1. Production Supabase Auth Setup
```bash
# Configure production auth settings
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_ANON_KEY="your-anon-key"

# Enable auth providers
- Email/Password authentication
- Social login (Google, GitHub)
- Magic link authentication
- Phone number authentication
```

#### 2. User Profile Management
```typescript
// User profile interface
interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  preferences: {
    language: 'en' | 'fr' | 'ar';
    timezone: string;
    notifications: {
      email: boolean;
      push: boolean;
      sms: boolean;
    };
    theme: 'light' | 'dark' | 'auto';
  };
  subscription: {
    plan: 'free' | 'premium' | 'enterprise';
    status: 'active' | 'cancelled' | 'expired';
    expires_at: string;
  };
  created_at: string;
  updated_at: string;
}
```

#### 3. Authentication Flow Implementation
```typescript
// Auth service implementation
class AuthService {
  async signUp(email: string, password: string): Promise<UserProfile>
  async signIn(email: string, password: string): Promise<UserProfile>
  async signOut(): Promise<void>
  async resetPassword(email: string): Promise<void>
  async updateProfile(updates: Partial<UserProfile>): Promise<UserProfile>
  async deleteAccount(): Promise<void>
}
```

### 📱 Watchlists & Alerts

#### 1. Watchlist Management
```typescript
// Watchlist interface
interface Watchlist {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  companies: WatchlistItem[];
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

interface WatchlistItem {
  ticker: string;
  company_name: string;
  added_at: string;
  notes?: string;
}
```

#### 2. Price Alerts
```typescript
// Alert interface
interface PriceAlert {
  id: string;
  user_id: string;
  ticker: string;
  type: 'above' | 'below' | 'percent_change';
  value: number;
  status: 'active' | 'triggered' | 'cancelled';
  notification_channels: ('email' | 'push' | 'sms')[];
  created_at: string;
  triggered_at?: string;
}
```

#### 3. Alert Implementation
```typescript
// Alert service
class AlertService {
  async createAlert(alert: Omit<PriceAlert, 'id' | 'created_at'>): Promise<PriceAlert>
  async updateAlert(id: string, updates: Partial<PriceAlert>): Promise<PriceAlert>
  async deleteAlert(id: string): Promise<void>
  async checkAlerts(ticker: string, currentPrice: number): Promise<PriceAlert[]>
  async triggerAlert(alert: PriceAlert): Promise<void>
}
```

### 🔔 Real-time Push Notifications

#### 1. Notification System
```typescript
// Notification interface
interface Notification {
  id: string;
  user_id: string;
  type: 'alert' | 'news' | 'system' | 'market_update';
  title: string;
  message: string;
  data?: Record<string, any>;
  read: boolean;
  created_at: string;
  read_at?: string;
}
```

#### 2. Push Notification Setup
```typescript
// Push notification service
class PushNotificationService {
  async subscribe(userId: string, subscription: PushSubscription): Promise<void>
  async unsubscribe(userId: string): Promise<void>
  async sendNotification(userId: string, notification: Notification): Promise<void>
  async sendBulkNotification(userIds: string[], notification: Notification): Promise<void>
}
```

#### 3. WebSocket Integration
```typescript
// Real-time notification handler
class NotificationHandler {
  constructor(private ws: WebSocket) {}
  
  onPriceAlert(alert: PriceAlert): void {
    this.ws.send(JSON.stringify({
      type: 'price_alert',
      data: alert
    }));
  }
  
  onMarketUpdate(update: MarketUpdate): void {
    this.ws.send(JSON.stringify({
      type: 'market_update',
      data: update
    }));
  }
}
```

### 📱 Mobile PWA Integration

#### 1. Progressive Web App Setup
```json
// manifest.json
{
  "name": "Casablanca Insights",
  "short_name": "Casablanca",
  "description": "Moroccan Market Analytics Platform",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#1f2937",
  "icons": [
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

#### 2. Service Worker Implementation
```typescript
// service-worker.ts
class CasablancaServiceWorker {
  async handleInstall(event: InstallEvent): Promise<void> {
    await event.waitUntil(
      caches.open('casablanca-v1').then(cache => {
        return cache.addAll([
          '/',
          '/static/js/bundle.js',
          '/static/css/main.css',
          '/manifest.json'
        ]);
      })
    );
  }
  
  async handleFetch(event: FetchEvent): Promise<Response> {
    // Handle offline functionality
    // Cache API responses
    // Serve cached content when offline
  }
}
```

---

## 🧠 Week 3: Advanced Analytics & Portfolio Management

### 📊 Analytics Dashboard

#### 1. AI Signals & Predictions
```typescript
// AI signal interface
interface AISignal {
  id: string;
  ticker: string;
  signal_type: 'buy' | 'sell' | 'hold';
  confidence: number; // 0-100
  reasoning: string;
  factors: {
    technical: number;
    fundamental: number;
    sentiment: number;
    market: number;
  };
  generated_at: string;
  expires_at: string;
}
```

#### 2. AI Signal Generation
```python
# AI signal generator
class AISignalGenerator:
    def __init__(self):
        self.model = self.load_model()
        self.feature_extractor = FeatureExtractor()
    
    def generate_signals(self, ticker: str) -> List[AISignal]:
        # Extract features
        features = self.feature_extractor.extract(ticker)
        
        # Generate predictions
        predictions = self.model.predict(features)
        
        # Convert to signals
        signals = self.convert_to_signals(predictions, ticker)
        
        return signals
    
    def extract_features(self, ticker: str) -> Dict[str, float]:
        return {
            'price_momentum': self.calculate_momentum(ticker),
            'volume_trend': self.analyze_volume(ticker),
            'technical_indicators': self.get_technical_indicators(ticker),
            'fundamental_ratios': self.get_fundamental_ratios(ticker),
            'sentiment_score': self.get_sentiment_score(ticker),
            'market_correlation': self.get_market_correlation(ticker)
        }
```

#### 3. Technical Analysis Indicators
```typescript
// Technical analysis service
class TechnicalAnalysisService {
  calculateRSI(prices: number[], period: number = 14): number[]
  calculateMACD(prices: number[]): { macd: number[], signal: number[], histogram: number[] }
  calculateBollingerBands(prices: number[], period: number = 20): { upper: number[], middle: number[], lower: number[] }
  calculateMovingAverages(prices: number[], periods: number[]): Record<number, number[]>
  identifySupportResistance(prices: number[]): { support: number[], resistance: number[] }
}
```

### 📈 Backtesting Engine

#### 1. Backtesting Framework
```typescript
// Backtesting interface
interface BacktestConfig {
  ticker: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  strategy: TradingStrategy;
  commission_rate: number;
  slippage: number;
}

interface BacktestResult {
  total_return: number;
  annualized_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  equity_curve: EquityPoint[];
  trades: Trade[];
}
```

#### 2. Strategy Implementation
```typescript
// Trading strategy interface
interface TradingStrategy {
  name: string;
  description: string;
  parameters: Record<string, number>;
  
  generateSignals(data: MarketData): Signal[];
  calculatePositionSize(capital: number, signal: Signal): number;
  shouldExit(position: Position, data: MarketData): boolean;
}

// Example: Moving Average Crossover Strategy
class MACrossoverStrategy implements TradingStrategy {
  name = 'MA Crossover';
  description = 'Buy when short MA crosses above long MA, sell when it crosses below';
  parameters = { short_period: 10, long_period: 30 };
  
  generateSignals(data: MarketData): Signal[] {
    const shortMA = this.calculateMA(data.prices, this.parameters.short_period);
    const longMA = this.calculateMA(data.prices, this.parameters.long_period);
    
    const signals: Signal[] = [];
    
    for (let i = 1; i < data.prices.length; i++) {
      if (shortMA[i] > longMA[i] && shortMA[i-1] <= longMA[i-1]) {
        signals.push({ type: 'buy', date: data.dates[i], price: data.prices[i] });
      } else if (shortMA[i] < longMA[i] && shortMA[i-1] >= longMA[i-1]) {
        signals.push({ type: 'sell', date: data.dates[i], price: data.prices[i] });
      }
    }
    
    return signals;
  }
}
```

#### 3. Backtesting Engine
```typescript
// Backtesting engine
class BacktestingEngine {
  async runBacktest(config: BacktestConfig): Promise<BacktestResult> {
    // Load historical data
    const data = await this.loadHistoricalData(config.ticker, config.start_date, config.end_date);
    
    // Generate signals
    const signals = config.strategy.generateSignals(data);
    
    // Simulate trading
    const portfolio = new Portfolio(config.initial_capital);
    const trades: Trade[] = [];
    
    for (const signal of signals) {
      if (signal.type === 'buy' && !portfolio.hasPosition(config.ticker)) {
        const positionSize = config.strategy.calculatePositionSize(portfolio.cash, signal);
        const trade = portfolio.buy(config.ticker, positionSize, signal.price, signal.date);
        trades.push(trade);
      } else if (signal.type === 'sell' && portfolio.hasPosition(config.ticker)) {
        const trade = portfolio.sell(config.ticker, signal.price, signal.date);
        trades.push(trade);
      }
    }
    
    // Calculate results
    return this.calculateResults(portfolio, trades, data);
  }
}
```

### 💼 Portfolio Management

#### 1. Paper Trading System
```typescript
// Paper trading interface
interface PaperTradingAccount {
  id: string;
  user_id: string;
  name: string;
  initial_balance: number;
  current_balance: number;
  cash: number;
  positions: Position[];
  trades: Trade[];
  created_at: string;
  updated_at: string;
}

interface Position {
  ticker: string;
  shares: number;
  average_price: number;
  current_price: number;
  unrealized_pnl: number;
  realized_pnl: number;
  total_pnl: number;
}
```

#### 2. Portfolio Tracking
```typescript
// Portfolio service
class PortfolioService {
  async createAccount(userId: string, name: string, initialBalance: number): Promise<PaperTradingAccount>
  async getAccount(accountId: string): Promise<PaperTradingAccount>
  async placeOrder(accountId: string, order: Order): Promise<Trade>
  async getPositions(accountId: string): Promise<Position[]>
  async getPerformance(accountId: string, period: string): Promise<PerformanceMetrics>
  async getTradeHistory(accountId: string): Promise<Trade[]>
}
```

#### 3. Live Data Integration
```typescript
// Live data service
class LiveDataService {
  private ws: WebSocket;
  
  constructor() {
    this.ws = new WebSocket('ws://localhost:8000/ws');
    this.setupEventHandlers();
  }
  
  private setupEventHandlers(): void {
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMarketUpdate(data);
    };
  }
  
  private handleMarketUpdate(data: MarketUpdate): void {
    // Update portfolio positions with live prices
    // Trigger alerts if conditions are met
    // Update P&L calculations
  }
}
```

### 📊 Risk Metrics & Analytics

#### 1. Risk Calculation Engine
```typescript
// Risk metrics service
class RiskMetricsService {
  calculateVaR(returns: number[], confidence: number = 0.95): number
  calculateSharpeRatio(returns: number[], riskFreeRate: number = 0.02): number
  calculateMaxDrawdown(equity: number[]): { maxDrawdown: number, startDate: string, endDate: string }
  calculateBeta(portfolioReturns: number[], marketReturns: number[]): number
  calculateAlpha(portfolioReturns: number[], marketReturns: number[], riskFreeRate: number): number
  calculateSortinoRatio(returns: number[], riskFreeRate: number = 0.02): number
}
```

#### 2. Portfolio Analytics Dashboard
```typescript
// Analytics dashboard components
interface AnalyticsDashboard {
  performance: {
    totalReturn: number;
    annualizedReturn: number;
    volatility: number;
    sharpeRatio: number;
    maxDrawdown: number;
  };
  risk: {
    var: number;
    beta: number;
    alpha: number;
    sortinoRatio: number;
  };
  allocation: {
    bySector: Record<string, number>;
    byAsset: Record<string, number>;
    topHoldings: Position[];
  };
  attribution: {
    factors: FactorAttribution[];
    sectors: SectorAttribution[];
  };
}
```

---

## 🛠️ Implementation Timeline

### Week 2 Implementation Plan

#### Day 1-2: Authentication Setup
- [ ] Configure production Supabase Auth
- [ ] Implement user registration/login flows
- [ ] Add password reset functionality
- [ ] Set up social login providers

#### Day 3-4: User Profile & Preferences
- [ ] Create user profile management
- [ ] Implement user preferences
- [ ] Add subscription management
- [ ] Set up user settings page

#### Day 5-7: Watchlists & Alerts
- [ ] Implement watchlist CRUD operations
- [ ] Create price alert system
- [ ] Add alert notification channels
- [ ] Build watchlist UI components

### Week 3 Implementation Plan

#### Day 1-3: Analytics Dashboard
- [ ] Implement AI signal generation
- [ ] Create technical analysis indicators
- [ ] Build analytics dashboard UI
- [ ] Add signal visualization components

#### Day 4-5: Backtesting Engine
- [ ] Create backtesting framework
- [ ] Implement trading strategies
- [ ] Add strategy performance metrics
- [ ] Build backtesting UI

#### Day 6-7: Portfolio Management
- [ ] Implement paper trading system
- [ ] Create portfolio tracking
- [ ] Add live data integration
- [ ] Build portfolio analytics

---

## 🎯 Success Metrics

### Week 2 Success Criteria
- ✅ User registration/login working
- ✅ Watchlists functional
- ✅ Price alerts operational
- ✅ Push notifications working
- ✅ Mobile PWA accessible

### Week 3 Success Criteria
- ✅ AI signals generating
- ✅ Backtesting engine functional
- ✅ Paper trading operational
- ✅ Risk metrics calculating
- ✅ Analytics dashboard complete

---

## 📞 Support & Resources

### Development Team
- **Frontend Lead**: UI/UX implementation
- **Backend Lead**: API development
- **Data Scientist**: AI/ML implementation
- **DevOps**: Infrastructure support

### Documentation
- **API Documentation**: `/docs/api/`
- **Component Library**: `/docs/components/`
- **Testing Guide**: `/docs/testing/`
- **Deployment Guide**: `/docs/deployment/`

---

**🎯 Ready to build the future of Moroccan market analytics!** 