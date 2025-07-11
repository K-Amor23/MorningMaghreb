# 📈 Casablanca Stock Exchange Paper Trading Simulator

## 🎯 Overview

A comprehensive paper trading platform for the Casablanca Stock Exchange that allows users to practice trading Moroccan stocks with virtual money. This simulator provides a realistic trading experience without financial risk.

## ✨ Features

### 🏦 Account Management
- **Virtual Trading Accounts**: Start with 100,000 MAD virtual balance
- **Multiple Accounts**: Create and manage multiple paper trading accounts
- **Real-time Balance Tracking**: Monitor cash and position values
- **Account Performance Metrics**: Track total P&L and return percentages

### 💹 Trading Interface
- **Stock Selection**: Choose from major Moroccan stocks (ATW, IAM, BCP, BMCE, etc.)
- **Buy/Sell Orders**: Place market orders with quantity and price
- **Real-time Quotes**: View current prices and daily changes
- **Commission Simulation**: 0.1% commission on all trades
- **Order Validation**: Check sufficient funds and shares before execution

### 📊 Portfolio Management
- **Position Tracking**: Monitor current holdings and average costs
- **Unrealized P&L**: Real-time profit/loss calculations
- **Portfolio Weighting**: View position allocations
- **Performance Analytics**: Track individual stock performance

### 📋 Order Management
- **Order History**: Complete record of all trades
- **Status Filtering**: Filter by filled, pending, cancelled orders
- **Trade Details**: View execution prices, commissions, and timestamps
- **Order Statistics**: Summary of trading activity

### 📈 Performance Analytics
- **Total Return**: Overall portfolio performance
- **Win Rate**: Percentage of profitable trades
- **Best/Worst Performers**: Top and bottom performing stocks
- **Trade Statistics**: Detailed breakdown of trading activity

## 🏗️ Architecture

### Database Schema
```sql
-- Paper Trading Accounts
CREATE TABLE paper_trading_accounts (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    account_name VARCHAR(255),
    initial_balance DECIMAL(15,2),
    current_balance DECIMAL(15,2),
    total_pnl DECIMAL(15,2),
    total_pnl_percent DECIMAL(8,6),
    is_active BOOLEAN,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

-- Trading Orders
CREATE TABLE paper_trading_orders (
    id UUID PRIMARY KEY,
    account_id UUID REFERENCES paper_trading_accounts(id),
    ticker VARCHAR(10),
    order_type VARCHAR(10), -- 'buy' or 'sell'
    order_status VARCHAR(20), -- 'pending', 'filled', 'cancelled', 'rejected'
    quantity DECIMAL(15,6),
    price DECIMAL(12,4),
    total_amount DECIMAL(15,2),
    commission DECIMAL(10,2),
    filled_quantity DECIMAL(15,6),
    filled_price DECIMAL(12,4),
    filled_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

-- Trading Positions
CREATE TABLE paper_trading_positions (
    id UUID PRIMARY KEY,
    account_id UUID REFERENCES paper_trading_accounts(id),
    ticker VARCHAR(10),
    quantity DECIMAL(15,6),
    avg_cost DECIMAL(12,4),
    total_cost DECIMAL(15,2),
    current_value DECIMAL(15,2),
    unrealized_pnl DECIMAL(15,2),
    unrealized_pnl_percent DECIMAL(8,6),
    last_updated TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

-- Trading Transactions
CREATE TABLE paper_trading_transactions (
    id UUID PRIMARY KEY,
    account_id UUID REFERENCES paper_trading_accounts(id),
    order_id UUID REFERENCES paper_trading_orders(id),
    ticker VARCHAR(10),
    transaction_type VARCHAR(10), -- 'buy' or 'sell'
    quantity DECIMAL(15,6),
    price DECIMAL(12,4),
    total_amount DECIMAL(15,2),
    commission DECIMAL(10,2),
    net_amount DECIMAL(15,2),
    balance_before DECIMAL(15,2),
    balance_after DECIMAL(15,2),
    created_at TIMESTAMPTZ
);
```

### Backend API Endpoints

#### Account Management
- `POST /api/paper-trading/accounts` - Create new trading account
- `GET /api/paper-trading/accounts` - List user's trading accounts
- `GET /api/paper-trading/accounts/{accountId}` - Get account summary with positions

#### Trading Operations
- `POST /api/paper-trading/accounts/{accountId}/orders` - Place new order
- `GET /api/paper-trading/accounts/{accountId}/orders` - Get order history
- `GET /api/paper-trading/accounts/{accountId}/transactions` - Get transaction history

#### Performance Analytics
- `GET /api/paper-trading/accounts/{accountId}/performance` - Get performance metrics

### Frontend Components

#### Core Components
- `TradingAccountOverview` - Account summary and position overview
- `TradingInterface` - Stock selection and order placement
- `PortfolioPositions` - Detailed position management
- `OrderHistory` - Order tracking and filtering
- `TradingPerformance` - Performance analytics and insights

#### Features
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Mode Support**: Consistent with existing theme system
- **Real-time Updates**: Live price updates and position calculations
- **Error Handling**: Comprehensive error states and user feedback
- **Loading States**: Smooth loading experiences throughout

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Next.js application running
- Supabase authentication configured

### Installation

1. **Database Setup**
   ```sql
   -- Run the paper trading schema from database/schema.sql
   -- This creates all necessary tables and indexes
   ```

2. **Backend Integration**
   ```bash
   # The paper trading router is already included in the backend
   # No additional installation required
   ```

3. **Frontend Access**
   ```bash
   # Navigate to the paper trading page
   http://localhost:3000/paper-trading
   ```

### Usage

1. **Create Account**
   - Visit the paper trading page
   - System automatically creates a default account with 100,000 MAD
   - Customize account name and initial balance

2. **Start Trading**
   - Select stocks from the available Moroccan companies
   - Choose buy or sell orders
   - Enter quantity and price
   - Review order summary and place trade

3. **Monitor Performance**
   - Track positions and unrealized P&L
   - View order history and transaction details
   - Analyze performance metrics and insights

## 📊 Available Stocks

The simulator includes major Moroccan stocks:

| Ticker | Company Name | Sector |
|--------|--------------|--------|
| ATW | Attijariwafa Bank | Banking |
| IAM | Maroc Telecom | Telecommunications |
| BCP | Banque Centrale Populaire | Banking |
| BMCE | BMCE Bank | Banking |
| ONA | Omnium Nord Africain | Conglomerates |
| CMT | Ciments du Maroc | Building Materials |
| LAFA | Lafarge Ciments | Building Materials |
| CIH | CIH Bank | Banking |
| MNG | Managem | Mining |
| TMA | Taqa Morocco | Energy |

## 🔧 Configuration

### Commission Rates
- **Trading Commission**: 0.1% of trade value
- **Minimum Commission**: None
- **Maximum Commission**: None

### Order Types
- **Market Orders**: Immediate execution at current price
- **Limit Orders**: Coming soon
- **Stop Orders**: Coming soon

### Risk Management
- **Position Limits**: No maximum position size
- **Cash Requirements**: Must have sufficient funds for buy orders
- **Share Requirements**: Must have sufficient shares for sell orders

## 🎨 UI/UX Features

### Design System
- **Consistent Styling**: Matches existing Casablanca Insight design
- **Color Coding**: Green for gains, red for losses
- **Interactive Elements**: Hover states and transitions
- **Accessibility**: Screen reader friendly and keyboard navigation

### User Experience
- **Intuitive Navigation**: Tab-based interface for easy switching
- **Real-time Feedback**: Immediate order confirmation and updates
- **Error Prevention**: Validation before order placement
- **Helpful Tooltips**: Contextual information and guidance

## 🔒 Security & Compliance

### Data Protection
- **User Isolation**: Each user can only access their own accounts
- **Secure API**: All endpoints require authentication
- **Data Validation**: Input sanitization and validation
- **Audit Trail**: Complete transaction history

### Paper Trading Disclaimer
- **Educational Purpose**: Clearly marked as simulation only
- **No Real Money**: All transactions are virtual
- **Risk Warning**: Disclaimers about real trading risks
- **Performance Disclaimer**: Past performance doesn't guarantee future results

## 🚧 Future Enhancements

### Planned Features
- **Advanced Order Types**: Limit orders, stop-loss, trailing stops
- **Real-time Market Data**: Live price feeds from CSE
- **Technical Analysis**: Charts and indicators
- **Portfolio Optimization**: Asset allocation tools
- **Social Trading**: Share strategies and performance
- **Mobile App**: Native mobile trading experience

### Integration Opportunities
- **Real Market Data**: Connect to actual CSE data feeds
- **News Integration**: Real-time news impact on positions
- **AI Insights**: Machine learning trading recommendations
- **Backtesting**: Historical strategy testing
- **Paper to Real**: Seamless transition to real trading

## 📝 API Documentation

### Request/Response Examples

#### Create Account
```json
POST /api/paper-trading/accounts
{
  "account_name": "My Trading Account",
  "initial_balance": 100000
}

Response:
{
  "id": "account-uuid",
  "account_name": "My Trading Account",
  "initial_balance": 100000,
  "current_balance": 100000,
  "total_pnl": 0,
  "total_pnl_percent": 0,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Place Order
```json
POST /api/paper-trading/accounts/{accountId}/orders
{
  "ticker": "ATW",
  "order_type": "buy",
  "quantity": 100,
  "price": 410.00,
  "notes": "Initial position"
}

Response:
{
  "id": "order-uuid",
  "ticker": "ATW",
  "order_type": "buy",
  "order_status": "filled",
  "quantity": 100,
  "price": 410.00,
  "total_amount": 41000.00,
  "commission": 41.00,
  "filled_at": "2024-01-01T00:00:00Z"
}
```

## 🤝 Contributing

### Development Guidelines
- **Code Style**: Follow existing TypeScript/React patterns
- **Testing**: Add unit tests for new components
- **Documentation**: Update docs for new features
- **Accessibility**: Ensure WCAG compliance

### Testing
```bash
# Run frontend tests
npm run test

# Run backend tests
cd apps/backend && python -m pytest

# Run integration tests
npm run test:integration
```

## 📞 Support

For questions or issues with the paper trading simulator:

1. **Documentation**: Check this README and inline code comments
2. **Issues**: Create GitHub issues for bugs or feature requests
3. **Discussions**: Use GitHub Discussions for general questions
4. **Email**: Contact the development team

---

**Disclaimer**: This is a paper trading simulator for educational purposes only. No real money is involved. Past performance does not guarantee future results. Always do your own research before making real investment decisions. 