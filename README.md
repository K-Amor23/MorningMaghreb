# Morning Maghreb

**A Morocco-focused market research & analytics webapp**

> 📖 **Quick Start**: See [cursor_startup.md](cursor_startup.md) for confirmed working startup commands and troubleshooting guide.

Casablanca Insight unifies fragmented French, Arabic, and Darija data into a multilingual portal for serious investors. Track real-time Casablanca Stock Exchange (CSE) quotes, ingest IFRS financials and convert to U.S. GAAP, monitor macro & central-bank indicators, and run long-term portfolio analyses—all powered by AI summaries and delivered in a daily email digest, *Morning Maghreb*.

---

## 🚀 Features

### **Core Market Features**
* **Real-time Market Data**
  Live quotes, volumes, and sector indices (MASI, MADEX, MASI-ESG).
  Watchlists, price alerts, and interactive charts with advanced search functionality.

* **Volume Data & Analytics**
  Comprehensive volume data collection from multiple sources with automated ETL pipeline.
  Volume ratio analysis, high/low volume alerts, and trend identification.

* **Financials & GAAP Conversion**
  Automated PDF scraping (Tabula‑Py) → IFRS tables → JSON/YAML-driven U.S. GAAP mapping → key ratio calculations.

* **AI-Powered Insights**
  GPT‑4 summaries of IFRS→GAAP adjustments, natural-language Q&A "Investor Chatbot," and narrative snippets in your newsletter.

* **ETF & Bond Data Integration**
  Comprehensive Moroccan ETF and bond data with real-time pricing, yield curves, and bond calendar.
  Automated scraping of ETF holdings, bond maturities, and yield curve analysis.

### **Advanced Trading & Portfolio Features**
* **Paper Trading Platform**
  Full-featured paper trading with virtual accounts, real-time order execution, portfolio tracking, and performance analytics. Includes order history, position management, and trading performance metrics.

* **Portfolio Toolkit**
  Import holdings (CSV/API), P/L attribution, performance metrics (Sharpe, Sortino, Beta), drawdown curves, Monte Carlo simulations, and mean‑variance optimization.

* **Advanced Features Dashboard**
  Company comparison tools, custom screens, dividend tracking, earnings calendar, and economic indicator tracking.

### **Currency & Economic Features**
* **Smart Currency Converter & Remittance Rate Advisor**
  Compare USD→MAD exchange rates across Remitly, Wise, Western Union against official BAM rates. Get AI-powered recommendations for the best time to transfer money and set rate alerts.

* **Currency Analysis Tools**
  Currency pair comparison, trend analysis, forecasting, and insights with historical data visualization.

* **Macro & Central-Bank Module**
  Automated scraping of Bank Al-Maghrib (BAM) economic data including policy rates, foreign exchange reserves, inflation (CPI), money supply (M1/M2/M3), balance of payments, and credit to economy. Real-time data fetching with intelligent parsing and RESTful API endpoints.

* **Enhanced Macro Analytics**
  Comprehensive macro data pages for exchange rates, GDP, inflation, interest rates, and trade balance.
  Interactive charts and analysis tools for economic indicators with historical data visualization.

### **Premium Features**
* **API Key Management**
  Generate and manage API keys for programmatic access to market data and analytics.

* **Data Export Tools**
  Export market data, financial statements, and portfolio analytics in multiple formats (CSV, JSON, Excel).

* **Custom Report Builder**
  Create personalized reports with custom metrics, charts, and data visualizations.

* **Translation Management**
  Multi-language support with custom translation management for French, Arabic, and English content.

* **Webhook Integration**
  Set up webhooks for real-time notifications on market events, price alerts, and portfolio changes.

### **Content & Communication**
* **"Morning Maghreb" Newsletter**
  Daily email digest with top market movers, corporate actions, macro highlights, and AI-generated commentary.
  Complete newsletter system with dedicated marketing page, subscriber management, and multi-language support.

* **AI Content Moderation with Cultural Guardrails**
  Automated content screening to ensure all generated content respects Moroccan cultural sensitivities and legal requirements. Detects and replaces sensitive topics while maintaining business focus.

* **Sentiment Analysis & Voting**
  Community-driven sentiment analysis with voting system for stocks and market indicators.

* **Compliance & Market Guide**
  Comprehensive trading rules, price limits, circuit breakers, and regulatory information for the Casablanca Stock Exchange.

* **Portfolio Sharing & Contest Promotion**
  Social features for sharing portfolio performance and contest participation.
  Enhanced contest promotion with dedicated components and user engagement tools.

### **User Experience & Management**
* **Advanced Search & Navigation**
  Intelligent search bar with company lookup, keyboard shortcuts (⌘K), and smooth expansion animations.

* **Account Management**
  Comprehensive user account management with profile settings, preferences, and subscription management.

* **Feature Flags System**
  Dynamic feature toggling for A/B testing and gradual feature rollouts.

* **Freemium & Pro Tiers**
  Subscriber management via Supabase Auth + Stripe; role-based access and billing.

---

## 🛠 Tech Stack

| Layer               | Technology                                            |
| ------------------- | ----------------------------------------------------- |
| **Frontend**        | Next.js 15, React, Tailwind CSS, Recharts, React‑i18next |
| **Backend**         | FastAPI (Python) with comprehensive ETL pipeline     |
| **ETL & Scraping**  | Python (requests, BeautifulSoup, Tabula‑Py, pandas)   |
| **Database**        | PostgreSQL + TimescaleDB; Redis (cache)               |
| **Email**           | SendGrid or Mailgun                                   |
| **Auth & Billing**  | Supabase Auth; Stripe integration                     |
| **AI & NLP**        | OpenAI GPT‑4o‑mini / GPT‑4; Cursor; Codex             |
| **Hosting & CI/CD** | Vercel (frontend); Render (backend)                   |

---

## 📥 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-org/casablanca-insight.git
cd casablanca-insight
```

### 2. Install dependencies

```bash
# Install web app dependencies
cd apps/web && npm install

# Install backend dependencies
cd ../backend && pip install -r requirements.txt

# Install mobile app dependencies (optional)
cd ../mobile && npm install
```

### 3. Configure environment

Copy the environment template and configure your variables:

```bash
cp env.template .env.local
```

Edit `.env.local` with your actual API keys and configuration.

### 4. Set up the database

```bash
# Run the database schema
psql -d your_database -f database/schema.sql
```

### 5. Run the development servers

```bash
# Start the web app
cd apps/web && npm run dev

# Start the backend (in another terminal)
cd apps/backend && uvicorn casablanca_insights.main:app --reload --host 127.0.0.1 --port 8000
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

**Health Checks:**
- Backend: [http://localhost:8000/health](http://localhost:8000/health) → `{"status":"healthy","version":"2.0.0"}`
- Frontend: [http://localhost:3000](http://localhost:3000) → `200 OK`
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

**Quick Start with Makefile:**
```bash
# Kill any existing processes on ports 8000 and 3000
make kill-ports

# Start backend
make start-backend

# Start frontend (in another terminal)
make start-frontend

# Check health of both servers
make health-check
```

**Note:** The backend runs in "basic mode" if `OPENAI_API_KEY` is not provided, with AI features disabled but core functionality intact.

---

## 🚀 Deployment

For production deployment, see the comprehensive [Deployment Guide](DEPLOYMENT.md) which covers:

- **Frontend**: Vercel deployment with Next.js optimization
- **Backend**: Render deployment with FastAPI and background workers
- **Database**: Supabase setup with real-time subscriptions
- **ETL Jobs**: Automated data pipeline with error handling
- **CI/CD**: GitHub Actions automation with testing

### Quick Deploy

1. **Frontend**: Connect your GitHub repo to Vercel
2. **Backend**: Deploy to Render using the `render.yaml` configuration
3. **Database**: Set up Supabase project and run the schema
4. **Environment**: Configure all environment variables in your hosting platforms

---

## 🧩 Project Structure

```
casablanca-insights/
├── apps/
│   ├── backend/          # FastAPI backend with ETL pipeline
│   │   ├── etl/          # ETL modules (financials, economic data, currency)
│   │   ├── models/       # Pydantic data models
│   │   ├── routers/      # FastAPI route handlers
│   │   ├── data/         # Configuration files
│   │   └── main.py       # FastAPI application entry point
│   ├── web/              # Next.js frontend application
│   │   ├── pages/        # Next.js pages and API routes
│   │   ├── components/   # Reusable UI components
│   │   │   ├── paper-trading/  # Paper trading components
│   │   │   ├── premium/        # Premium feature components
│   │   │   └── advanced/       # Advanced feature components
│   │   └── lib/          # Utility modules
│   └── mobile/           # React Native mobile app
├── database/             # Database schemas and migrations
├── docs/                 # Documentation and guides
└── .github/              # GitHub Actions workflows
```

---

## 📈 Usage

### **Market Data & Analysis**
* **Explore Market Data**: View live equity quotes and macro series with advanced filtering
* **Analyze Financials**: Access GAAP‑converted statements and key ratios
* **Monitor Economic Data**: Track BAM indicators including policy rates, inflation, and foreign exchange reserves
* **Currency Analysis**: Compare exchange rates, analyze trends, and get transfer recommendations

### **Trading & Portfolio**
* **Paper Trading**: Practice trading with virtual accounts and real-time market data
* **Portfolio Management**: Import holdings and run advanced analytics and simulations
* **Advanced Features**: Use company comparison tools, custom screens, and dividend tracking

### **Premium Features**
* **API Access**: Generate API keys for programmatic data access
* **Data Export**: Export market data and analytics in multiple formats
* **Custom Reports**: Build personalized reports with custom metrics and visualizations
* **Webhooks**: Set up real-time notifications for market events

### **AI & Communication**
* **AI Chat**: Interact with AI for market insights and analysis
* **Content Moderation**: Automated content screening with cultural sensitivity
* **Newsletter**: Subscribe to "Morning Maghreb" for daily insights

### **Economic Data API**

The backend provides comprehensive economic data endpoints:

```bash
# Get available economic indicators
GET /api/economic-data/indicators

# Get latest policy rate
GET /api/economic-data/key_policy_rate/latest

# Fetch new data from BAM
POST /api/economic-data/fetch

# Get economic dashboard
GET /api/economic-data/dashboard/overview

# Currency comparison
GET /api/currency/compare/USD/MAD

# Paper trading accounts
GET /api/paper-trading/accounts

# ETF and Bond data
GET /api/markets/etfs
GET /api/markets/bonds
GET /api/markets/bond-calendar
GET /api/markets/yield-curve

# Macro data endpoints
GET /api/macro/exchange-rates
GET /api/macro/gdp
GET /api/macro/inflation
GET /api/macro/interest-rates
GET /api/macro/trade-balance
```

For detailed API documentation, see [Economic Data README](apps/backend/README_ECONOMIC_DATA.md).

---

## 🔧 Recent Updates

### **Volume Data Integration & Airflow Pipeline**
- ✅ **Volume Scraper Integration**: Comprehensive volume data collection from multiple sources (African Markets, Wafabourse, Investing.com)
- ✅ **Airflow ETL Pipeline**: Enhanced DAG with volume data tasks, automated daily collection and processing
- ✅ **Volume Analytics**: Volume ratio calculations, high/low volume alerts, and trend analysis
- ✅ **Database Integration**: Supabase storage with volume_analysis and market_data tables

### **Newsletter System & Marketing**
- ✅ **Morning Maghreb Newsletter**: Complete newsletter system with dedicated page, signup forms, and Supabase integration
- ✅ **Newsletter Page**: Comprehensive marketing page with features, testimonials, sample content, and FAQ
- ✅ **Email Management**: Subscriber management, campaign tracking, and delivery analytics
- ✅ **Multi-language Support**: Newsletter available in English, French, and Arabic

### **Compliance & Market Guide**
- ✅ **Comprehensive Compliance Page**: Detailed trading guardrails, price limits, trading halts, and regulatory information
- ✅ **Market Guide**: Complete guide to Casablanca Stock Exchange rules and regulations
- ✅ **Trading Rules**: Price limits, circuit breakers, and investor protection information

### **Search Bar & UI Improvements**
- Fixed search bar cutoff issue in header layout
- Improved responsive design and mobile experience
- Enhanced keyboard shortcuts and accessibility
- Better visual hierarchy and spacing

### **Premium Features Implementation**
- Complete API key management system
- Advanced data export capabilities
- Custom report builder with visualization tools
- Multi-language translation management
- Webhook integration for real-time notifications

### **Paper Trading Platform**
- Full virtual trading environment
- Real-time order execution and portfolio tracking
- Performance analytics and reporting
- Order history and position management

### **Currency & Economic Enhancements**
- Advanced currency comparison tools
- Trend analysis and forecasting
- Remittance rate optimization
- Enhanced economic data visualization

### **ETF & Bond Data Integration**
- Comprehensive Moroccan ETF and bond data collection
- Real-time pricing and yield curve analysis
- Bond calendar with maturity tracking
- Automated ETL pipeline for fixed income data
- Interactive charts and analytics for fixed income instruments

### **Enhanced Macro Analytics**
- Dedicated pages for exchange rates, GDP, inflation, interest rates, and trade balance
- Interactive economic indicator charts with historical data
- Real-time macro data scraping and processing
- Advanced economic data visualization tools

### **Social Features & Contest Enhancement**
- Portfolio sharing functionality for social engagement
- Enhanced contest promotion components
- Improved user engagement and community features

---

## 🤝 Contributing

Contributions are welcome! Please open issues for bugs or feature requests and submit pull requests for enhancements.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m "Add feature"`)
4. Push to your branch (`git push origin feature/YourFeature`)
5. Open a pull request

### Development Guidelines
- Follow the existing code style and conventions
- Add tests for new features
- Update documentation for API changes
- Ensure all features work across supported languages

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For support, please:
- Check the [documentation](docs/)
- Open an issue on GitHub
- Contact the development team

**Built with ❤️ for the Moroccan investment community**
