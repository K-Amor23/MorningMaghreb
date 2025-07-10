**Casablanca Insight Technical Specification**

---

## 1. System Architecture

**High‑Level Diagram (Textual)**
```
[Frontend (Next.js)]  <-->  [API Gateway / BFF (FastAPI)]
       |                        |         |        |
       |                        |         |        +--> [OpenAI Service]
       |                        |         |        +--> [SendGrid]
       |                        |         +--> [ETL Scheduler (K8s CronJobs)]
       |                        |                   |--> PDF Scraper Service
       |                        |                   |--> Macro Ingest Service
       |                        |                   |--> CSE Data Ingest
       |                        +--> [PostgreSQL + TimescaleDB]
       |                        +--> [Redis Cache]
       |                        +--> [Supabase Auth]
       |                        +--> [Stripe Billing]
```

### 1.1 Frontend
- **Framework:** Next.js (React)  
- **Styling:** Tailwind CSS  
- **Charts:** Recharts / D3  
- **i18n:** React‑i18next  
- **Hosting:** Vercel (serverless SSR)  
- **Auth:** Supabase Auth integration via `@supabase/supabase-js`

### 1.2 Backend (BFF / API)
- **Language:** Python 3.10+ with FastAPI  
- **Server:** Uvicorn / Gunicorn  
- **Responsibilities:**  
  - Expose REST endpoints for market data, financials, macro, portfolio, newsletter trigger  
  - Validate JWT from Supabase  
  - Proxy/compose external API calls (CSE feed, Trading Economics, OpenAI)  
  - Cache heavy or repeated responses in Redis

### 1.3 ETL & Scheduler
- **Orchestration:** Kubernetes CronJobs / AWS EventBridge  
- **Tasks:**  
  - **PDF Scraper Service:** Tabula-Py + pdfplumber pipelines nightly  
  - **GAAP Converter Service:** Apply JSON mapping and adjustment hooks  
  - **Macro Ingest Service:** Fetch BAM CSV/Excel via HTTP, fallback to Trading Economics API  
  - **CSE Ingest Service:** Download licensed CSV/FTP or scrape via community API  
- **Data Storage:** Write raw and processed data into PostgreSQL (TimescaleDB extension for time-series)

### 1.4 Database & Cache
- **PostgreSQL (+ TimescaleDB plugin)**  
  - **Schemas & Tables:**  
    - `users`, `subscriptions`, `roles`  
    - `quotes` (ticker, timestamp, open, high, low, close, volume)  
    - `financial_reports` (ticker, period, IFRS JSON, raw PDF link)  
    - `gaap_reports` (ticker, period, GAAP JSON)  
    - `ratios` (ticker, period, ratio_name, value)  
    - `macro_series` (series_code, date, value)  
    - `portfolios`, `holdings`, `simulations`  
    - `newsletter_logs` (user_id, sent_at, status)  
- **Redis**  
  - Cache layer for: real-time quotes, AI summaries, light API queries

---

## 2. API Endpoint Specifications

| Method | Endpoint                        | Auth                | Description                                          |
|--------|---------------------------------|---------------------|------------------------------------------------------|
| GET    | `/api/markets/quotes?tickers=`  | Public / Visitor    | Return latest quotes for comma-separated symbols     |
| GET    | `/api/markets/history`          | Subscriber          | OHLCV history for a symbol over a date range         |
| GET    | `/api/financials/{ticker}`      | Subscriber          | IFRS raw and GAAP‑converted P&L, BS, CF              |
| POST   | `/api/financials/convert`       | Admin               | Trigger on-demand GAAP conversion for one report     |
| GET    | `/api/macro/series?code=&from=` | Public / Subscriber | Time-series for macro series (policy_rate, CPI, etc) |
| POST   | `/api/chat`                     | Subscriber          | Pass user query + context to OpenAI, return answer   |
| GET    | `/api/portfolio`                | Subscriber          | Fetch user’s current portfolio holdings              |
| POST   | `/api/portfolio/import`         | Subscriber          | Upload CSV or connect broker API (future)            |
| GET    | `/api/newsletter`               | Admin               | List pending newsletter jobs                         |
| POST   | `/api/newsletter/send`          | Admin               | Enqueue/send daily digest via SendGrid               |
| POST   | `/api/auth/signup`              | Public              | Create new user via Supabase Auth                    |
| POST   | `/api/auth/login`               | Public              | Issue JWT via Supabase Auth                          |

**Request / Response** schemas to be documented in OpenAPI spec file.

---

## 3. Data Models & Schema (ER Diagram Text)

```
Users --< Subscriptions
Users --< Portfolios --< Holdings
Tickers --< Quotes(time-series)
Tickers --< FinancialReports --< GaapReports --< Ratios
MacroSeries(time-series)
Users --< NewsletterLogs
```

### 3.1 Example: `quotes` table
```sql
CREATE TABLE quotes (
  ticker TEXT NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  open NUMERIC,
  high NUMERIC,
  low NUMERIC,
  close NUMERIC,
  volume BIGINT,
  PRIMARY KEY (ticker, ts)
);
SELECT create_hypertable('quotes', 'ts');
```

---

## 4. CI/CD & Deployment
- **Repo Structure:** Monorepo with `frontend/`, `backend/`, `etl/` directories  
- **CI:** GitHub Actions runs lint, tests, build on PRs  
- **CD:**  
  - **Frontend:** Auto-Deploy to Vercel on merge to `main`  
  - **Backend:** Deploy Docker image to AWS Cloud Run / Render  
  - **ETL Jobs:** Container images scheduled in Kubernetes cluster  

---

## 5. Third-Party Integrations
- **Supabase Auth**: OAuth2 JWT issuance; protects private endpoints  
- **Stripe**: Plan and subscription management via `stripe-node` SDK  
- **SendGrid / Mailgun**: Email dispatch, templates, tracking  
- **OpenAI**: Chat completions and embeddings (GPT-4o-mini)  
- **Trading Economics API**: Fallback macro data  
- **CSE Licensed Feed / Scraper**: Equity data

---

## 6. Security & Compliance
- **Transport**: TLS v1.2+ everywhere  
- **Authentication**: JWT via Supabase; RBAC on backend  
- **Secrets Management**: Environment variables; no secrets in repo  
- **Rate Limiting**: 100 requests/min per user via FastAPI middleware  
- **Data Privacy**: GDPR‑compliant consent on signup; ability to delete user data

---

## 7. Monitoring & Logging
- **Logging**: Structured JSON logs via Python `logging` → forwarded to Logflare / Datadog  
- **Error Tracking**: Sentry SDK for backend and frontend  
- **Metrics**: Prometheus exporters on API; Grafana dashboards for ETL job success rates

---

## 8. Performance & Scalability
- **Caching**: Redis TTL of 5m for market data; 24h for AI summaries  
- **Load Balancing**: Managed by Vercel / Cloud Run autoscaling  
- **Database**: Read replicas for heavy analytical queries; TimescaleDB for efficient time-series

---

## 9. Development & Local Setup
1. Clone monorepo  
2. Create `.env.local` in each service  
3. Run `docker-compose up` (Postgres+Redis+Supabase emulator)  
4. `cd frontend && npm install && npm run dev`  
5. `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`  
6. ETL: `cd etl && airflow scheduler & airflow webserver` (optional)

---

**End of Technical Specification**

