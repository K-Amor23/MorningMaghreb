from __future__ import annotations

import os
from datetime import datetime, timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import ShortCircuitOperator


def env_ready() -> bool:
    base_url = os.environ.get("NEXT_PUBLIC_SITE_URL")
    admin_token = os.environ.get("ADMIN_API_TOKEN")
    return bool(base_url and admin_token)


local_tz = pendulum.timezone("Africa/Casablanca")

default_args = {
    "owner": "morningmaghreb",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="weekly_newsletter",
    description="Scrape news, generate weekly summary, and send newsletter via Next.js APIs",
    start_date=datetime(2025, 8, 1, tzinfo=local_tz),
    schedule_interval="0 8 * * MON",  # Mondays 08:00 Africa/Casablanca
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["morningmaghreb", "newsletter", "scrape"],
) as dag:
    check_env = ShortCircuitOperator(
        task_id="check_env",
        python_callable=env_ready,
    )

    # Use env mapping to avoid embedding secrets in command strings
    env_mapping = {
        "BASE_URL": os.environ.get("NEXT_PUBLIC_SITE_URL", ""),
        "ADMIN_API_TOKEN": os.environ.get("ADMIN_API_TOKEN", ""),
    }

    scrape_news = BashOperator(
        task_id="scrape_news",
        bash_command='curl -sSf -X POST -H "x-admin-token: $ADMIN_API_TOKEN" "$BASE_URL/api/news/scrape"',
        env=env_mapping,
    )

    generate_summary = BashOperator(
        task_id="generate_summary",
        bash_command='curl -sSf -X POST -H "x-admin-token: $ADMIN_API_TOKEN" "$BASE_URL/api/summary/run"',
        env=env_mapping,
    )

    send_weekly = BashOperator(
        task_id="send_weekly",
        bash_command='curl -sSf -X POST -H "Content-Type: application/json" -H "x-admin-token: $ADMIN_API_TOKEN" -d "{\\"language\\":\\"en\\"}" "$BASE_URL/api/newsletter/send-weekly"',
        env=env_mapping,
    )

    done = EmptyOperator(task_id="done")

    check_env >> scrape_news >> generate_summary >> send_weekly >> done


