# Casablanca Insight

**A Morocco-focused market research & analytics webapp**

Casablanca Insight unifies fragmented French, Arabic, and Darija data into a multilingual portal for serious investors. Track real-time Casablanca Stock Exchange (CSE) quotes, ingest IFRS financials and convert to U.S. GAAP, monitor macro & central-bank indicators, and run long-term portfolio analyses—all powered by AI summaries and delivered in a daily email digest, *Morning Maghreb*.

---

## 🚀 Features

* **Real-time Market Data**
  Live quotes, volumes, and sector indices (MASI, MADEX, MASI-ESG).
  Watchlists, price alerts, and interactive charts.

* **Financials & GAAP Conversion**
  Automated PDF scraping (Tabula‑Py) → IFRS tables → JSON/YAML-driven U.S. GAAP mapping → key ratio calculations.

* **AI-Powered Insights**
  GPT‑4 summaries of IFRS→GAAP adjustments, natural-language Q\&A “Investor Chatbot,” and narrative snippets in your newsletter.

* **Macro & Central-Bank Module**
  Automated scraping of Bank Al-Maghrib (BAM) economic data including policy rates, foreign exchange reserves, inflation (CPI), money supply (M1/M2/M3), balance of payments, and credit to economy. Real-time data fetching with intelligent parsing and RESTful API endpoints.

* **Portfolio Toolkit**
  Import holdings (CSV/API), P/L attribution, performance metrics (Sharpe, Sortino, Beta), drawdown curves, Monte Carlo simulations, and mean‑variance optimization.

* **“Morning Maghreb” Newsletter**
  Daily email digest with top market movers, corporate actions, macro highlights, and AI-generated commentary.

* **Smart Currency Converter & Remittance Rate Advisor**
  Compare USD→MAD exchange rates across Remitly, Wise, Western Union against official BAM rates. Get AI-powered recommendations for the best time to transfer money and set rate alerts.

* **AI Content Moderation with Cultural Guardrails**
  Automated content screening to ensure all generated content respects Moroccan cultural sensitivities and legal requirements. Detects and replaces sensitive topics while maintaining business focus.

* **Freemium & Pro Tiers**
  Subscriber management via Supabase Auth + Stripe; role-based access and billing.

---

## 🛠 Tech Stack

| Layer               | Technology                                            |
| ------------------- | ----------------------------------------------------- |
| **Frontend**        | Next.js, React, Tailwind CSS, Recharts, React‑i18next |
| **Backend**         | FastAPI (Python) or Node.js microservices             |
| **ETL & Scraping**  | Python (requests, BeautifulSoup, Tabula‑Py, pandas)   |
| **Database**        | PostgreSQL + TimescaleDB; Redis (cache)               |
| **Email**           | SendGrid or Mailgun                                   |
| **Auth & Billing**  | Supabase Auth / Firebase Auth; Stripe                 |
| **AI & NLP**        | OpenAI GPT‑4o‑mini / GPT‑4; Cursor; Codex             |
| **Hosting & CI/CD** | Vercel / Netlify (frontend); Render / AWS Cloud Run   |

---

## 📥 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-org/casablanca-insight.git
cd casablanca-insight
```

### 2. Install dependencies

```bash
npm install
# or
yarn install
```

### 3. Configure environment

Copy the environment template and configure your variables:

```bash
cp env.template .env.local
```

Edit `.env.local` with your actual API keys and configuration.

### 4. Run the development server

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🚀 Deployment

For production deployment, see the comprehensive [Deployment Guide](DEPLOYMENT.md) which covers:

- **Frontend**: Vercel deployment
- **Backend**: Render deployment with FastAPI
- **Database**: Supabase setup
- **ETL Jobs**: Background workers
- **CI/CD**: GitHub Actions automation

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
│   │   ├── etl/          # ETL modules (financials, economic data)
│   │   ├── models/       # Pydantic data models
│   │   ├── routers/      # FastAPI route handlers
│   │   ├── data/         # Configuration files
│   │   └── main.py       # FastAPI application entry point
│   ├── web/              # Next.js frontend application
│   │   ├── pages/        # Next.js pages (routes)
│   │   ├── components/   # Reusable UI components
│   │   └── lib/          # Utility modules
│   └── mobile/           # React Native mobile app
├── database/             # Database schemas and migrations
├── docs/                 # Documentation and guides
└── .github/              # GitHub Actions workflows
```

---

## 📈 Usage

* **Explore Market Data**: View live equity quotes and macro series.
* **Analyze Financials**: Access GAAP‑converted statements and key ratios.
* **Monitor Economic Data**: Track BAM indicators including policy rates, inflation, and foreign exchange reserves.
* **Interact with AI**: Summarize reports or ask questions via chat.
* **Manage Portfolio**: Import holdings and run simulations.
* **Subscribe**: Sign up for “Morning Maghreb” to receive daily insights by email.

### Economic Data API

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
```

For detailed API documentation, see [Economic Data README](apps/backend/README_ECONOMIC_DATA.md).

---

## 🤝 Contributing

Contributions are welcome! Please open issues for bugs or feature requests and submit pull requests for enhancements.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m "Add feature"`)
4. Push to your branch (`git push origin feature/YourFeature`)
5. Open a pull request

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
