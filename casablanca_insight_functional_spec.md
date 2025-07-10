**Casablanca Insight Functional Specification**

---

## 1. Introduction & Purpose
This functional specification defines the concrete behaviors, user interactions, data flows, and acceptance criteria for the Casablanca Insight web application. It translates the high‑level vision into detailed feature-level requirements.

**Audience:** Product managers, developers, QA engineers

---

## 2. User Roles & Permissions

| Role         | Description                                        | Access                                        |
|--------------|----------------------------------------------------|-----------------------------------------------|
| Visitor      | Unauthenticated website visitor                    | Home page, Signup page, Documentation         |
| Subscriber   | Registered user with active subscription           | All market data, financials, AI summaries, macro tools, portfolio tools, newsletter settings |
| Admin        | Internal administrator                             | Subscriber features + user management, content management, newsletter dispatch controls |

---

## 3. Functional Modules

### 3.1 Market Data Module
- **3.1.1 Real-time Quotes**  
  - **Description:** Display live price, volume, change for MASI, MADEX, MASI-ESG, and individual tickers.  
  - **User Story:** As a Subscriber, I can view up-to-date prices and percent changes for indices and my watchlist so I know current market movement.  
  - **Acceptance Criteria:**  
    - Real-time data updates at 1-minute intervals.  
    - User can filter by index or custom watchlist.
- **3.1.2 Historical Charts**  
  - **Description:** Render interactive candlestick and line charts for selected symbols over selectable date ranges.  
  - **User Story:** As a Subscriber, I can view 1-day, 1-week, 1-month, 1-year, and all-time charts with technical overlays (SMA, RSI).  
  - **Acceptance Criteria:**  
    - Charts load within 300ms.  
    - Overlays toggle on/off.

### 3.2 Financials & GAAP Module
- **3.2.1 IFRS Data Ingestion**  
  - **Description:** Scrape PDF financial reports nightly; extract P&L, balance sheet, cash flows.  
  - **User Story:** As an Admin, I want automated ETL that fetches latest IFRS tables so data stays current.  
  - **Acceptance Criteria:**  
    - ETL pipeline completes without errors; logs stored.  
    - New data appears in UI within 6 hours of publication.
- **3.2.2 GAAP Conversion**  
  - **Description:** Map IFRS line items to U.S. GAAP categories and apply adjustment hooks.  
  - **User Story:** As a Subscriber, I can switch between IFRS and GAAP views to compare reported vs. adjusted results.  
  - **Acceptance Criteria:**  
    - GAAP P&L and BS can be toggled.  
    - Key ratios update accordingly.
- **3.2.3 Ratio Dashboard**  
  - **Description:** Display computed ratios (ROE, EBITDA margin, current ratio) for each issuer.  
  - **User Story:** As a Subscriber, I can quickly scan financial health metrics for comparison.  
  
### 3.3 AI Summaries & Chatbot
- **3.3.1 Report Summary Endpoint**  
  - **Description:** Generate 3–4 sentence LLM summary of IFRS→GAAP adjustments.  
  - **User Story:** As a Subscriber, I want concise commentary on quarterly changes without reading entire reports.  
  - **Acceptance Criteria:**  
    - Summaries cached per company+period.  
    - Summaries deliver within 2 seconds.
- **3.3.2 Investor Chatbot**  
  - **Description:** Provide a chat interface to query financials and market data.  
  - **User Story:** As a Subscriber, I can ask, “What drove Company X’s revenue change?” and receive a precise answer.  
  - **Acceptance Criteria:**  
    - Chat context limited to last 3 user queries.  
    - Rate-limit to 20 messages per hour.

### 3.4 Macro & Central Bank Module
- **3.4.1 Data Series Explorer**  
  - **Description:** Present time-series data for policy rate, reserves, money supply, CPI.  
- **3.4.2 Policy Calendar**  
  - **Description:** List upcoming MPC meeting dates and decision history.  
- **3.4.3 Scenario Simulator**  
  - **Description:** Model impact of hypothetical policy-rate changes on index returns via regression.  

### 3.5 Portfolio Toolkit
- **3.5.1 Portfolio Import**  
  - **Description:** CSV upload or broker-API connect to load current holdings.  
- **3.5.2 Performance Metrics**  
  - **Description:** Compute P/L attribution, Sharpe, Sortino, Beta, drawdowns.  
- **3.5.3 Monte Carlo Simulator**  
  - **Description:** Run 1,000 trial projections over user-defined horizon; display probability distributions.  
- **3.5.4 Optimizer**  
  - **Description:** Markowitz optimizer to generate efficient frontier; allow weight adjustments.  

### 3.6 Newsletter & Email Service
- **3.6.1 Signup & Preferences**  
  - **Description:** Collect email, name, delivery time preferences; manage unsubscribe.  
- **3.6.2 Digest Generation**  
  - **Description:** Compile top movers, corporate actions, GAAP summaries, macro bullet points.  
- **3.6.3 Dispatch**  
  - **Description:** Send daily at user-specified time via SendGrid; track open/click rates.  

### 3.7 Authentication & Billing
- **3.7.1 User Registration & Login**  
  - **Description:** Email/password signup, magic links, password reset.  
- **3.7.2 Subscription Management**  
  - **Description:** Stripe integration for freemium vs. pro plan upgrades and cancellations.  

---

## 4. Data & API Specifications
(Outline REST endpoints, request/response schemas, sample payloads. E.g., `/api/markets/quotes`, `/api/financials/{ticker}` )

---

## 5. Error Handling & Logging
- Standardized error codes (400, 401, 403, 500)  
- Centralized logging for ETL jobs, API errors, AI failures  
- Automated alerts on pipeline exceptions

---

## 6. Acceptance Tests & Criteria
- **ETL Pipeline:** No failures for 30-day backfill.  
- **UI Loading:** All primary pages load within 500ms under normal conditions.  
- **Newsletter Deliverability:** 95% successful deliveries; <2% unsubscribe rate.

---

## 7. Dependencies & Constraints
- Availability of CSE data feed  
- Stability of BAM CSV/PDF formats  
- OpenAI rate limits and cost  

---

## 8. Glossary
- **MPC:** Monetary Policy Committee  
- **IFRS:** International Financial Reporting Standards  
- **GAAP:** Generally Accepted Accounting Principles

---

*End of Functional Specification*

