from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.bash import BashOperator

# Repo root inside the container. Set REPO_ROOT env in your Airflow environment
# to override (e.g., /opt/airflow/repo).
REPO_ROOT = os.environ.get("REPO_ROOT", "/opt/airflow/repo")
PY = f"cd {REPO_ROOT} && python"

default_args = {
    "owner": "morningmaghreb",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="master_data_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 8, 1),
    schedule_interval="0 18 * * 0",  # Weekly: Sun 18:00 America/New_York (set Airflow TZ)
    catchup=False,
    max_active_runs=1,
    tags=["morningmaghreb"],
) as dag:

    seed_companies = BashOperator(
        task_id="seed_companies",
        bash_command=f"{PY} scripts/seed_companies.py",
    )

    scrape_news = BashOperator(
        task_id="scrape_news",
        bash_command=f"{PY} scripts/scrape_news.py",
    )

    generate_weekly_summary = BashOperator(
        task_id="generate_weekly_summary",
        bash_command=f"{PY} scripts/generate_weekly_summary.py",
    )

    send_newsletter_test = BashOperator(
        task_id="send_newsletter_test",
        bash_command=(
            "if [ \"$APP_ENV\" = \"prod\" ] || [ \"$SEND_TEST\" = \"1\" ]; then "
            f"{PY} scripts/send_newsletter.py; "
            "else echo 'Skipping test send'; fi"
        ),
    )

    seed_companies >> scrape_news >> generate_weekly_summary >> send_newsletter_test


