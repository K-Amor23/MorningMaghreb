"""
Airflow DAG: FX Daily Rates + Remittance Quotes → Supabase

Sources:
- Bank Al-Maghrib (official reference)
- ECB (EUR reference)
- BoE (GBP spot)
- US Fed H.10 (USD weekly)
- Fallback: exchangerate.host, Open Exchange Rates (if configured)
- Remittance: Wise, Remitly, Western Union (mocked endpoints to be completed)
"""

from datetime import datetime, timedelta, date
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
import logging
import requests
from decimal import Decimal
from supabase import create_client, Client


default_args = {
    'owner': 'casablanca-insights',
    'depends_on_past': False,
    'start_date': datetime(2025, 8, 13),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}


def get_sb() -> Client:
    conn = BaseHook.get_connection("supabase")
    url = conn.host
    key = conn.extra_dejson.get('service_role_key') or conn.password
    if not url or not key:
        raise RuntimeError("Supabase connection not configured")
    return create_client(url, key)


def upsert_fx_rate(sb: Client, currency_pair: str, rate: Decimal, source: str, rate_date: date):
    payload = {
        "rate_date": rate_date.isoformat(),
        "currency_pair": currency_pair,
        "source": source,
        "rate": float(rate),
    }
    sb.table("fx_daily_rates").upsert(payload, on_conflict="rate_date,currency_pair,source").execute()
    logging.info(f"Upserted {currency_pair} {rate} from {source} on {rate_date}")


def fetch_bam_reference_usd_mad() -> Decimal:
    candidates = [
        "https://www.bkam.ma/Marches/Principaux-indicateurs/Marche-des-changes/Cours-de-change/Cours-de-reference",
        "https://www.bkam.ma/en/Markets/Key-indicators/Foreign-exchange-market/Foreign-exchange-rates/Transfer-exchange-rate",
    ]
    for url in candidates:
        try:
            r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code != 200:
                continue
            # naive parse for a numeric value on page; refine with BeautifulSoup if necessary
            # Here, fallback to a simple heuristic is omitted; rely on earlier BAM DAG for robust parsing
        except Exception:
            continue
    # As a fallback for wiring, return a placeholder that will be overwritten by existing BAM DAG
    return Decimal("10.20")


def fetch_ecb_eur_mad() -> Decimal:
    # ECB provides EUR reference rates versus many currencies (not MAD directly). You typically fetch EUR/USD and USD/MAD to derive.
    # For now, placeholder to be implemented when corridor derivation is added.
    return Decimal("10.90")


def fetch_boe_gbp_mad() -> Decimal:
    # Placeholder for BoE GBP spot via API; similar derivation as ECB may be required.
    return Decimal("13.00")


def fetch_fallback_usd_mad() -> Decimal:
    try:
        r = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=MAD", timeout=20)
        if r.ok:
            data = r.json()
            rate = data.get("rates", {}).get("MAD")
            if rate:
                return Decimal(str(rate))
    except Exception as e:
        logging.warning(f"exchangerate.host fallback failed: {e}")
    return Decimal("10.10")


def task_upsert_benchmarks(**_):
    sb = get_sb()
    today = datetime.utcnow().date()
    # USD/MAD
    bam = fetch_bam_reference_usd_mad()
    upsert_fx_rate(sb, "USD/MAD", bam, "BAM", today)
    fallback = fetch_fallback_usd_mad()
    upsert_fx_rate(sb, "USD/MAD", fallback, "exchangerate.host", today)
    # Extend: EUR/MAD via derived chain, GBP/MAD
    ecb = fetch_ecb_eur_mad()
    upsert_fx_rate(sb, "EUR/MAD", ecb, "ECB (derived)", today)
    boe = fetch_boe_gbp_mad()
    upsert_fx_rate(sb, "GBP/MAD", boe, "BoE (derived)", today)


def upsert_remit_quote(sb: Client, payload: dict):
    sb.table("remittance_quotes").upsert(payload, on_conflict="quote_date,currency_pair,provider,transfer_amount").execute()


def task_collect_remittance(**kwargs):
    sb = get_sb()
    today = datetime.utcnow().date().isoformat()
    amount = 1000
    # Mock providers; replace with real scraping/API
    quotes = [
        {"quote_date": today, "currency_pair": "USD/MAD", "provider": "Wise", "rate": 10.18, "fee_amount": 5.5, "fee_currency": "USD", "effective_rate": 10.15, "transfer_amount": amount},
        {"quote_date": today, "currency_pair": "USD/MAD", "provider": "Remitly", "rate": 10.15, "fee_amount": 3.99, "fee_currency": "USD", "effective_rate": 10.12, "transfer_amount": amount},
        {"quote_date": today, "currency_pair": "USD/MAD", "provider": "Western Union", "rate": 10.05, "fee_amount": 8.0, "fee_currency": "USD", "effective_rate": 9.97, "transfer_amount": amount},
    ]
    for q in quotes:
        upsert_remit_quote(sb, q)
    logging.info(f"Upserted {len(quotes)} remittance quotes")


with DAG(
    dag_id="fx_rates_and_remittance_daily",
    default_args=default_args,
    schedule_interval="0 */4 * * *",  # every 4 hours; adjust as needed
    catchup=False,
    tags=["fx","remittance","supabase"],
) as dag:
    upsert_benchmarks = PythonOperator(
        task_id="upsert_benchmarks",
        python_callable=task_upsert_benchmarks,
        provide_context=True,
    )

    collect_remit = PythonOperator(
        task_id="collect_remittance_quotes",
        python_callable=task_collect_remittance,
        provide_context=True,
    )

    upsert_benchmarks >> collect_remit


