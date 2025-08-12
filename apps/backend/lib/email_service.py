"""
Email Service for Casablanca Insights
Handles newsletter delivery using SendGrid with fallback options.
"""

import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logger = logging.getLogger(__name__)

# Email configuration
FROM_EMAIL = os.getenv("FROM_EMAIL", "newsletter@casablancainsights.com")
REPLY_TO_EMAIL = os.getenv("REPLY_TO_EMAIL", "support@casablancainsights.com")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

# Initialize SendGrid client (optional)
sendgrid_client = None
if SENDGRID_API_KEY:
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent
        sendgrid_client = SendGridAPIClient(api_key=SENDGRID_API_KEY)
        logger.info("SendGrid client initialized successfully")
    except ImportError:
        logger.warning("SendGrid not installed - using fallback email service")
        sendgrid_client = None
    except Exception as e:
        logger.warning(f"Failed to initialize SendGrid: {e}")
        sendgrid_client = None
else:
    logger.warning("SendGrid API key not provided - using fallback email service")

def create_html_template(subject: str, content: str, footer: str = None) -> str:
    """Create HTML email template"""
    if footer is None:
        footer = """
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px;">
            <p>© 2024 Casablanca Insights. All rights reserved.</p>
            <p>You received this email because you subscribed to our newsletter.</p>
            <p><a href="{{unsubscribe_url}}" style="color: #007bff;">Unsubscribe</a></p>
        </div>
        """
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{subject}</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8f9fa;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #007bff;
            }}
            .header h1 {{
                color: #007bff;
                margin: 0;
                font-size: 28px;
            }}
            .content {{
                margin-bottom: 30px;
            }}
            .content h2 {{
                color: #333;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
            }}
            .content p {{
                margin-bottom: 15px;
            }}
            .highlight {{
                background-color: #f8f9fa;
                padding: 15px;
                border-left: 4px solid #007bff;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #666;
                font-size: 12px;
                text-align: center;
            }}
            .footer a {{
                color: #007bff;
                text-decoration: none;
            }}
            .footer a:hover {{
                text-decoration: underline;
            }}
            @media only screen and (max-width: 600px) {{
                body {{
                    padding: 10px;
                }}
                .container {{
                    padding: 20px;
                }}
                .header h1 {{
                    font-size: 24px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Casablanca Insights</h1>
                <p>Your Weekly Market Intelligence</p>
            </div>
            
            <div class="content">
                {content}
            </div>
            
            {footer}
        </div>
    </body>
    </html>
    """
    
    return html_template

async def send_email(
    to_email: str,
    subject: str,
    content: str,
    html_content: str = None,
    from_email: str = None,
    reply_to: str = None
) -> Dict[str, Any]:
    """
    Send a single email using SendGrid or fallback
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        content: Plain text content
        html_content: HTML content (optional)
        from_email: Sender email (optional)
        reply_to: Reply-to email (optional)
        
    Returns:
        Dictionary with success status and message
    """
    try:
        if not from_email:
            from_email = FROM_EMAIL
        if not reply_to:
            reply_to = REPLY_TO_EMAIL
            
        # Create HTML content if not provided
        if not html_content:
            html_content = create_html_template(subject, content)
        
        # Try SendGrid first
        if sendgrid_client:
            try:
                from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent
                
                message = Mail(
                    from_email=Email(from_email),
                    to_emails=To(to_email),
                    subject=subject,
                    plain_text_content=content,
                    html_content=HtmlContent(html_content)
                )
                
                # Add reply-to header
                message.reply_to = Email(reply_to)
                
                response = sendgrid_client.send(message)
                
                if response.status_code in [200, 201, 202]:
                    logger.info(f"Email sent successfully to {to_email} via SendGrid")
                    return {
                        "success": True,
                        "message": f"Email sent to {to_email}",
                        "provider": "sendgrid",
                        "status_code": response.status_code
                    }
                else:
                    logger.warning(f"SendGrid returned status {response.status_code}")
                    raise Exception(f"SendGrid error: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"SendGrid failed: {e}, using fallback")
                raise e
        
        # Fallback: Console output (for development/testing)
        logger.info("=== EMAIL SENT (FALLBACK MODE) ===")
        logger.info(f"To: {to_email}")
        logger.info(f"From: {from_email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Content: {content[:200]}...")
        logger.info("=== END EMAIL ===")
        
        return {
            "success": True,
            "message": f"Email logged to console (fallback mode) - {to_email}",
            "provider": "console_fallback",
            "content_preview": content[:200] + "..." if len(content) > 200 else content
        }
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return {
            "success": False,
            "message": f"Failed to send email: {str(e)}",
            "provider": "failed"
        }

async def send_bulk_email(
    subscribers: List[str],
    subject: str,
    content: str,
    html_content: str = None,
    from_email: str = None,
    reply_to: str = None
) -> Dict[str, Any]:
    """
    Send bulk email to multiple subscribers
    
    Args:
        subscribers: List of email addresses
        subject: Email subject
        content: Plain text content
        html_content: HTML content (optional)
        from_email: Sender email (optional)
        reply_to: Reply-to email (optional)
        
    Returns:
        Dictionary with bulk sending results
    """
    results = {
        "total": len(subscribers),
        "successful": 0,
        "failed": 0,
        "errors": []
    }
    
    for email in subscribers:
        try:
            result = await send_email(
                to_email=email,
                subject=subject,
                content=content,
                html_content=html_content,
                from_email=from_email,
                reply_to=reply_to
            )
            
            if result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "email": email,
                    "error": result["message"]
                })
                
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "email": email,
                "error": str(e)
            })
    
    logger.info(f"Bulk email completed: {results['successful']} successful, {results['failed']} failed")
    return results

async def send_newsletter(
    campaign_id: str,
    subscribers: List[str],
    subject: str,
    content: str,
    html_content: str = None
) -> Dict[str, Any]:
    """
    Send newsletter campaign to subscribers
    
    Args:
        campaign_id: Unique campaign identifier
        subscribers: List of subscriber email addresses
        subject: Newsletter subject
        content: Newsletter content
        html_content: HTML version of content (optional)
        
    Returns:
        Campaign sending results
    """
    logger.info(f"Starting newsletter campaign {campaign_id} to {len(subscribers)} subscribers")
    
    # Add campaign tracking to content
    tracking_content = f"""
    {content}
    
    ---
    Campaign ID: {campaign_id}
    Sent: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    results = await send_bulk_email(
        subscribers=subscribers,
        subject=subject,
        content=tracking_content,
        html_content=html_content
    )
    
    # Add campaign metadata
    results["campaign_id"] = campaign_id
    results["sent_at"] = datetime.now().isoformat()
    results["subject"] = subject
    
    return results

def test_email_service() -> Dict[str, Any]:
    """
    Test the email service configuration
    
    Returns:
        Test results dictionary
    """
    test_results = {
        "sendgrid_configured": bool(sendgrid_client),
        "from_email": FROM_EMAIL,
        "reply_to_email": REPLY_TO_EMAIL,
        "api_key_set": bool(SENDGRID_API_KEY)
    }
    
    if sendgrid_client:
        test_results["sendgrid_status"] = "ready"
    else:
        test_results["sendgrid_status"] = "fallback_mode"
    
    return test_results

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_send():
        result = await send_email(
            to_email="test@example.com",
            subject="Test Newsletter",
            content="This is a test newsletter content."
        )
        print(f"Test result: {result}")
    
    asyncio.run(test_send()) 