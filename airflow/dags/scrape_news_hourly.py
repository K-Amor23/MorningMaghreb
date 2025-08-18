from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {"owner": "morningmaghreb", "retries": 1, "retry_delay": timedelta(minutes=5)}

with DAG(
    dag_id="scrape_news_hourly",
    default_args=default_args,
    start_date=datetime(2025, 8, 1),
    schedule_interval="*/30 * * * *",  # every 30 minutes
    catchup=False,
    max_active_runs=1,
    tags=["morningmaghreb", "scrape"],
) as dag:
    BashOperator(
        task_id="scrape_news",
        bash_command="cd /opt/airflow/repo && python scripts/scrape_news.py",
    )






