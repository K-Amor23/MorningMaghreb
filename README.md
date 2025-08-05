# 🌅 Morning Maghreb

**A comprehensive Morocco-focused market research & analytics platform with real-time data collection**

[![Vercel](https://img.shields.io/badge/Vercel-Deployed-blue)](https://morningmaghreb.com)
[![Supabase](https://img.shields.io/badge/Supabase-Database-green)](https://supabase.com)
[![Next.js](https://img.shields.io/badge/Next.js-Framework-black)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-Language-blue)](https://typescriptlang.org)

## 📊 **Project Overview**

Morning Maghreb is a comprehensive financial analytics platform focused on the Moroccan stock market. It provides real-time market data, user authentication, premium features, and automated data collection for 78+ Moroccan companies.

### 🎯 **Key Features**

- **Real-time Market Data**: Live ticker updates every 5 minutes
- **User Authentication**: Complete signup/login system with Supabase
- **Premium Subscriptions**: Stripe integration for pro/premium tiers
- **Automated Data Collection**: Daily comprehensive market data scraping
- **Live Ticker Orchestrator**: Multi-source real-time data collection
- **Paper Trading**: Simulated trading environment
- **Trading Contests**: User competitions and leaderboards
- **Newsletter System**: Automated market newsletters
- **AI Summaries**: AI-powered company analysis
- **Mobile App**: React Native mobile application

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Data Sources  │
│   (Next.js)     │◄──►│   (Supabase)    │◄──►│   (Scrapers)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
    Vercel Deploy         Database Schema         Live Orchestrator
    (morningmaghreb.com)  (Complete Setup)       (Every 5 minutes)
```

## 🚀 **Current Status**

### ✅ **Completed Features**

#### **Infrastructure & Deployment**
- ✅ **Vercel Deployment**: Production deployment at `morningmaghreb.com`
- ✅ **Supabase Database**: New database (`skygarden`) configured
- ✅ **Environment Variables**: All production variables set
- ✅ **Domain Configuration**: Custom domain configured
- ✅ **Branding Update**: Complete rebrand from "Casablanca Insights" to "Morning Maghreb"

#### **Data Collection System**
- ✅ **Live Ticker Orchestrator**: Real-time data collection every 5 minutes
- ✅ **Comprehensive Data Collection**: Daily collection of 78+ companies
- ✅ **Multiple Data Sources**: African Markets, Casablanca Bourse, Wafa Bourse
- ✅ **Automated Scheduling**: Cron jobs for daily data collection
- ✅ **Data Storage**: JSON files and Supabase database integration

#### **User Features**
- ✅ **Authentication System**: Complete Supabase Auth integration
- ✅ **User Profiles**: Tier management (free/pro/admin)
- ✅ **Watchlists**: User-defined company tracking
- ✅ **Price Alerts**: Custom price notifications
- ✅ **Paper Trading**: Simulated trading environment
- ✅ **Trading Contests**: User competitions
- ✅ **Newsletter System**: Automated market newsletters

#### **Market Data**
- ✅ **Real-time Tickers**: 16 priority companies with live updates
- ✅ **Historical Data**: OHLCV data for all companies
- ✅ **Company Information**: Comprehensive company profiles
- ✅ **Financial Reports**: Automated report collection
- ✅ **News & Sentiment**: Market news with sentiment analysis

### 🔧 **Technical Implementation**

#### **Frontend (Next.js)**
- **Framework**: Next.js with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React hooks and context
- **Authentication**: Supabase Auth integration
- **Real-time Updates**: WebSocket connections
- **Mobile Responsive**: Optimized for all devices

#### **Backend (Supabase)**
- **Database**: PostgreSQL with Supabase
- **Authentication**: Row Level Security (RLS)
- **Real-time**: Live subscriptions
- **Storage**: File uploads and data storage
- **Functions**: Serverless functions for complex operations

#### **Data Collection**
- **Live Orchestrator**: Python-based real-time data collection
- **Multiple Sources**: 3 different data sources for redundancy
- **Automated Scheduling**: Cron jobs for daily updates
- **Error Handling**: Comprehensive error recovery
- **Data Validation**: Quality checks and validation

## 📈 **Live Ticker System**

### **Priority Companies (16)**
```
ATW  - Attijariwafa Bank
IAM  - Maroc Telecom
BCP  - Banque Centrale Populaire
BMCE - BMCE Bank of Africa
CIH  - Crédit Immobilier et Hôtelier
WAA  - Wafa Assurance
SAH  - Saham Assurance
ADH  - Addoha
LBV  - Label Vie
MAR  - Marjane Holding
LES  - Lesieur Cristal
CEN  - Ciments du Maroc
HOL  - Holcim Maroc
LAF  - Lafarge Ciments
MSA  - Managem
TMA  - Taqa Morocco
```

### **Data Sources**
1. **African Markets**: Comprehensive company data
2. **Casablanca Bourse**: Official exchange data
3. **Wafa Bourse**: Additional market data

### **Update Frequency**
- **Live Tickers**: Every 5 minutes
- **Daily Data**: 6:00 AM UTC daily
- **Real-time**: Continuous monitoring

## 🗄️ **Database Schema**

### **Core Tables**
- `profiles` - User authentication and profiles
- `companies` - Company information
- `company_prices` - Historical OHLCV data
- `company_reports` - Financial reports
- `company_news` - News and sentiment
- `watchlists` - User watchlists
- `price_alerts` - Price notifications
- `paper_trading_accounts` - Simulated trading
- `contests` - Trading competitions
- `newsletter_subscribers` - Newsletter system

### **Advanced Features**
- `ai_summaries` - AI-generated analysis
- `chat_queries` - User chat history
- `sentiment_votes` - User sentiment tracking
- `market_data` - Market summaries

## 🚀 **Deployment Status**

### **Production Environment**
- **Frontend**: Vercel (`morningmaghreb.com`)
- **Database**: Supabase (`skygarden`)
- **Domain**: `morningmaghreb.com`
- **SSL**: Automatic HTTPS
- **CDN**: Global content delivery

### **Environment Variables**
```bash
NEXT_PUBLIC_SUPABASE_URL=https://gzsgehciddnrssuqxtsj.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_API_URL=https://morningmaghreb-api.onrender.com
SENDGRID_FROM_EMAIL=admin@morningmaghreb.com
```

## 📋 **Setup Instructions**

### **Prerequisites**
- Node.js 18+
- Python 3.9+
- Git
- Vercel CLI
- Supabase account

### **Local Development**
```bash
# Clone the repository
git clone https://github.com/your-username/morning-maghreb.git
cd morning-maghreb

# Install dependencies
cd apps/web
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your Supabase credentials

# Start development server
npm run dev
```

### **Database Setup**
1. **Create Supabase Project**: Create new project in Supabase dashboard
2. **Set up Schema**: Copy and paste `database/complete_supabase_schema.sql` into SQL Editor
3. **Configure Environment**: Update environment variables with new database credentials
4. **Test Connection**: Visit `/test-db-connection` to verify setup

### **Data Collection Setup**
```bash
# Install Python dependencies
python3 -m pip install schedule requests aiohttp beautifulsoup4

# Test data collection
./scripts/test_comprehensive_collection.sh

# Start live ticker orchestrator
./scripts/start_live_orchestrator.sh

# Set up daily cron job
./scripts/setup_data_collection_cron.sh
```

## 🔧 **Scripts & Tools**

### **Data Collection**
- `scripts/collect_market_data_comprehensive.py` - Daily data collection
- `scripts/live_ticker_orchestrator.py` - Real-time ticker updates
- `scripts/test_comprehensive_collection.sh` - Test data collection

### **Database Management**
- `scripts/setup_database_manual_guide.md` - Manual schema setup guide
- `scripts/migrate_data_manual.py` - Data migration utilities
- `database/complete_supabase_schema.sql` - Complete database schema

### **Deployment**
- `vercel.json` - Vercel deployment configuration
- `scripts/start_live_orchestrator.sh` - Production orchestrator startup
- `scripts/morning-maghreb-live-ticker.service` - Systemd service file

## 📊 **Monitoring & Logs**

### **Log Files**
- `logs/live_ticker_orchestrator.log` - Real-time ticker logs
- `logs/comprehensive_data_collection.log` - Daily collection logs
- `logs/cron.log` - Cron job execution logs

### **Data Files**
- `apps/backend/data/live_tickers/` - Real-time ticker data
- `apps/backend/data/` - Historical market data
- `apps/backend/data/moroccan_*` - Country-specific data

## 🎯 **Premium Features**

### **Subscription Tiers**
- **Free**: Basic market data, limited features
- **Premium ($7/month)**: Advanced analytics, real-time data, alerts
- **Pro ($15/month)**: Full access, paper trading, contests

### **Premium Features**
- Real-time ticker data
- Advanced charting and analytics
- Price alerts and notifications
- Paper trading simulation
- Trading contests and leaderboards
- AI-powered company summaries
- Newsletter subscriptions
- Data export capabilities

## 🔐 **Security & Privacy**

### **Authentication**
- Supabase Auth with email/password
- Social login integration (Google, GitHub)
- Password reset functionality
- Email verification

### **Data Protection**
- Row Level Security (RLS) policies
- Encrypted data transmission
- GDPR compliance
- User data privacy controls

### **API Security**
- Rate limiting
- CORS configuration
- Input validation
- SQL injection prevention

## 🚀 **Performance**

### **Optimizations**
- Next.js automatic optimization
- Image optimization
- Code splitting
- Caching strategies
- CDN delivery

### **Scalability**
- Serverless architecture
- Database connection pooling
- Horizontal scaling ready
- Load balancing support

## 📈 **Analytics & Monitoring**

### **User Analytics**
- User engagement tracking
- Feature usage analytics
- Conversion tracking
- A/B testing capabilities

### **System Monitoring**
- Real-time error tracking
- Performance monitoring
- Uptime monitoring
- Data collection metrics

## 🤝 **Contributing**

### **Development Workflow**
1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

### **Code Standards**
- TypeScript for type safety
- ESLint for code quality
- Prettier for formatting
- Jest for testing

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Supabase** for backend infrastructure
- **Vercel** for deployment platform
- **Next.js** for frontend framework
- **African Markets** for data sources
- **Casablanca Bourse** for official market data

## 📞 **Support**

For support and questions:
- **Email**: admin@morningmaghreb.com
- **Documentation**: [docs.morningmaghreb.com](https://docs.morningmaghreb.com)
- **Issues**: [GitHub Issues](https://github.com/your-username/morning-maghreb/issues)

---

**Morning Maghreb** - Empowering Moroccan market insights with real-time data and advanced analytics. 🌅📈
