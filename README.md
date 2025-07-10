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
  Bank Al Maghrib policy rates, reserves, money supply, CPI, trade balance, policy calendar, and scenario simulator.

* **Portfolio Toolkit**
  Import holdings (CSV/API), P/L attribution, performance metrics (Sharpe, Sortino, Beta), drawdown curves, Monte Carlo simulations, and mean‑variance optimization.

* **“Morning Maghreb” Newsletter**
  Daily email digest with top market movers, corporate actions, macro highlights, and AI-generated commentary.

* **Freemium & Pro Tiers**
  Subscriber management via Supabase Auth + Stripe; role-based access and billing.

---

## 🛠 Tech Stack

| Layer               | Technology                                            |
| ------------------- | ----------------------------------------------------- |
| **Frontend**        | Next.js, React, Tailwind CSS, Recharts, React‑i18next |
| **Backend**         | FastAPI (Python) or Node.js microservices             |
| **ETL & Scraping**  | Python (requests, BeautifulSoup, Tabula‑Py)           |
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

Create a `.env.local` file at the project root with the following variables:

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
OPENAI_API_KEY=your_openai_api_key
STRIPE_SECRET_KEY=your_stripe_secret_key
SENDGRID_API_KEY=your_sendgrid_api_key
```

### 4. Run the development server

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧩 Project Structure

```
my-casablanca-insight/
├── pages/                # Next.js pages (routes)
│   ├── _app.js           # Application wrapper
│   ├── index.js          # Home page
│   ├── signup.js         # Newsletter signup page
│   └── api/newsletter.js # Newsletter dispatch endpoint
├── components/           # Reusable UI components
├── lib/                  # Library and utility modules (Supabase, OpenAI)
├── styles/               # Global and component-specific styles
├── scripts/              # ETL, scraping, and newsletter automation scripts
├── .env.local            # Environment variables (not committed)
├── next.config.js        # Next.js configuration
├── tailwind.config.js    # Tailwind CSS configuration
└── package.json          # Project metadata and scripts
```

---

## 📈 Usage

* **Explore Market Data**: View live equity quotes and macro series.
* **Analyze Financials**: Access GAAP‑converted statements and key ratios.
* **Interact with AI**: Summarize reports or ask questions via chat.
* **Manage Portfolio**: Import holdings and run simulations.
* **Subscribe**: Sign up for “Morning Maghreb” to receive daily insights by email.

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
