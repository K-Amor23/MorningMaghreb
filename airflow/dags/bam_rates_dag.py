"""
Airflow DAG to fetch Bank Al-Maghrib official USD/MAD rate and upsert into Supabase
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
import logging
import requests
from bs4 import BeautifulSoup
from decimal import Decimal
from supabase import create_client, Client


default_args = {
    'owner': 'casablanca-insights',
    'depends_on_past': False,
    'start_date': datetime(2025, 8, 6),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
}


def get_supabase() -> Client:
    """Build Supabase client from Airflow Connection named 'supabase'."""
    conn = BaseHook.get_connection("supabase")
    url = conn.host
    service_key = conn.extra_dejson.get('service_role_key') or conn.password
    if not url or not service_key:
        raise RuntimeError("Supabase connection not configured correctly")
    return create_client(url, service_key)


def fetch_bam_usd_mad_rate() -> Decimal:
    """Scrape BAM reference exchange rate page and extract USD/MAD.

    Tries French and English reference pages.
    """
    CANDIDATE_PATHS = [
        "https://www.bkam.ma/Marches/Principaux-indicateurs/Marche-des-changes/Cours-de-change/Cours-de-reference",
        "https://www.bkam.ma/en/Markets/Key-indicators/Foreign-exchange-market/Foreign-exchange-rates/Transfer-exchange-rate",
    ]

    for url in CANDIDATE_PATHS:
        try:
            resp = requests.get(url, timeout=30, headers={
                "User-Agent": "Mozilla/5.0",
                "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
            })
            if resp.status_code != 200:
                logging.warning(f"BAM page {url} returned {resp.status_code}")
                continue
            soup = BeautifulSoup(resp.text, 'html.parser')
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = [c.get_text(strip=True) for c in row.find_all(['td','th'])]
                    if not cols:
                        continue
                    label = cols[0].lower()
                    if any(k in label for k in ["usd", "us dollar", "dollar", "etats-unis"]):
                        # try to find a numeric value in the rest of columns
                        for cell in cols[1:]:
                            try:
                                val = Decimal(str(cell).replace(',', '.'))
                                if val > 0:
                                    return val
                            except Exception:
                                continue
        except Exception as e:
            logging.warning(f"Error scraping {url}: {e}")

    raise RuntimeError("Could not extract USD/MAD from BAM pages")


def upsert_bam_rate_to_supabase(**_):
    rate = fetch_bam_usd_mad_rate()
    sb = get_supabase()
    payload = {
        "currency_pair": "USD/MAD",
        "rate": float(rate),
        "rate_date": datetime.utcnow().date().isoformat(),
        "source": "Bank Al-Maghrib",
        "scraped_at": datetime.utcnow().isoformat(),
    }
    # Table must exist with RLS configured appropriately
    sb.table("bam_rates").upsert(payload, on_conflict="currency_pair,rate_date").execute()
    logging.info(f"Upserted BAM USD/MAD {rate}")


with DAG(
    dag_id="bam_exchange_rate_daily",
    default_args=default_args,
    schedule_interval="0 * * * *",  # hourly; adjust to daily if desired
    catchup=False,
    tags=["currency","bam","supabase"],
) as dag:
    collect = PythonOperator(
        task_id="collect_bam_usd_mad",
        python_callable=upsert_bam_rate_to_supabase,
        provide_context=True,
    )


