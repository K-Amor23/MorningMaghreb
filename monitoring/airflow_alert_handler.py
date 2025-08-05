
#!/usr/bin/env python3
"""
Airflow Alert Handler
Handles DAG failures and sends notifications
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any

class AirflowAlertHandler:
    def __init__(self, slack_webhook: str = None, email_alerts: list = None):
        self.slack_webhook = slack_webhook
        self.email_alerts = email_alerts or []
    
    def handle_dag_failure(self, dag_id: str, task_id: str, error: str, context: Dict[str, Any]):
        """Handle DAG failure"""
        message = f"""
❌ Airflow DAG Failure Alert

🚨 Details:
• DAG: {dag_id}
• Failed Task: {task_id}
• Error: {error}
• Execution Date: {context.get('execution_date', 'Unknown')}
• Duration: {context.get('duration', 'Unknown')} seconds

🔗 Access Points:
• Airflow UI: http://localhost:8080
• Check logs for detailed error information
        """
        
        self._send_slack_alert(message)
        self._send_email_alert(f"Airflow DAG Failure - {dag_id}", message)
    
    def handle_sla_miss(self, dag_id: str, task_id: str, sla_time: str):
        """Handle SLA miss"""
        message = f"""
⚠️ Airflow SLA Miss Alert

⏰ Details:
• DAG: {dag_id}
• Task: {task_id}
• SLA Time: {sla_time}
• Current Time: {datetime.now().isoformat()}

🔗 Access Points:
• Airflow UI: http://localhost:8080
• Check task execution time
        """
        
        self._send_slack_alert(message)
        self._send_email_alert(f"Airflow SLA Miss - {dag_id}", message)
    
    def _send_slack_alert(self, message: str):
        """Send Slack alert"""
        if not self.slack_webhook:
            return
        
        try:
            response = requests.post(
                self.slack_webhook,
                json={"text": message},
                timeout=10
            )
            if response.status_code == 200:
                logging.info("Slack alert sent successfully")
            else:
                logging.error(f"Failed to send Slack alert: {response.status_code}")
        except Exception as e:
            logging.error(f"Error sending Slack alert: {e}")
    
    def _send_email_alert(self, subject: str, message: str):
        """Send email alert"""
        if not self.email_alerts:
            return
        
        # Implementation would use your email service
        logging.info(f"Email alert would be sent to {self.email_alerts}: {subject}")

# Usage in Airflow DAG
def send_failure_alert(context):
    """Airflow callback function"""
    handler = AirflowAlertHandler(
        slack_webhook="YOUR_SLACK_WEBHOOK",
        email_alerts=["admin@morningmaghreb.com"]
    )
    
    handler.handle_dag_failure(
        dag_id=context['dag'].dag_id,
        task_id=context['task'].task_id,
        error=str(context.get('exception', 'Unknown error')),
        context=context
    )
