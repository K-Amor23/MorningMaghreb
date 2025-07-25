# Newsletter System Setup Guide

## Overview
The Casablanca Insights newsletter system leverages OpenAI to generate AI-powered financial content including weekly recaps, daily summaries, and company-specific analyses.

## Features
- 🤖 **AI-Powered Content**: Uses OpenAI GPT to generate engaging financial content
- 📊 **Market Data Integration**: Incorporates real-time market data and analysis
- 🌍 **Multi-Language Support**: English, French, and Arabic content generation
- 📧 **Email Delivery**: SendGrid integration for professional email delivery
- 📈 **Analytics Dashboard**: Track subscribers, campaigns, and engagement
- 🔄 **Automated Generation**: Can be integrated with Airflow for scheduled newsletters

## Quick Start

### 1. Environment Setup
```bash
# Copy environment template
cp env.template .env

# Edit .env and add your API keys:
OPENAI_API_KEY=your_openai_api_key_here
SENDGRID_API_KEY=your_sendgrid_api_key_here
DATABASE_URL=your_database_url_here
```

### 2. Test Newsletter Generation
```bash
# Test the complete newsletter system
cd apps/backend
python scripts/test_newsletter_generation.py

# Generate specific content types
python scripts/generate_newsletter_content.py --type weekly-recap
python scripts/generate_newsletter_content.py --type daily-summary
python scripts/generate_newsletter_content.py --type company-analysis --ticker ATW
```

### 3. Interactive Dashboard
```bash
# Launch the newsletter management dashboard
cd apps/backend
python scripts/newsletter_dashboard.py
```

## API Endpoints

### Newsletter Generation
- `POST /api/newsletter/weekly-recap/preview` - Preview weekly recap
- `POST /api/newsletter/generate-weekly-recap` - Generate and save weekly recap
- `POST /api/newsletter/daily-summary/preview` - Preview daily summary
- `POST /api/newsletter/generate-daily-summary` - Generate and save daily summary
- `POST /api/newsletter/company-analysis/{ticker}` - Generate company-specific analysis

### Email Management
- `POST /api/newsletter/send-test` - Send test email
- `POST /api/newsletter/send-campaign/{campaign_id}` - Send campaign to subscribers
- `GET /api/newsletter/subscribers` - List all subscribers
- `POST /api/newsletter/subscribe` - Add new subscriber

### Analytics
- `GET /api/newsletter/stats` - Newsletter statistics
- `GET /api/newsletter/campaigns` - List all campaigns
- `GET /api/newsletter/content` - List generated content

## Content Types

### Weekly Recap
- Market performance summary
- Top gainers and losers
- Sector analysis
- Economic indicators
- Upcoming earnings

### Daily Summary
- Market open/close data
- Key price movements
- Volume analysis
- News highlights
- Technical indicators

### Company Analysis
- Financial performance
- Recent news and events
- Technical analysis
- Risk assessment
- Investment outlook

## Configuration Options

### Content Generation
```python
# In scripts/generate_newsletter_content.py
LANGUAGES = ['en', 'fr', 'ar']  # Supported languages
CONTENT_TYPES = ['weekly-recap', 'daily-summary', 'company-analysis']
MAX_TOKENS = 2000  # OpenAI token limit
TEMPERATURE = 0.7  # Creativity level
```

### Email Settings
```python
# In lib/email_service.py
FROM_EMAIL = "newsletter@casablancainsights.com"
REPLY_TO_EMAIL = "support@casablancainsights.com"
EMAIL_TEMPLATE_PATH = "templates/newsletter.html"
```

## Integration with Airflow

### Weekly Newsletter DAG
```python
# Example Airflow DAG for automated newsletters
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

def generate_weekly_newsletter():
    import subprocess
    subprocess.run([
        "python", "scripts/generate_newsletter_content.py",
        "--type", "weekly-recap",
        "--save", "true"
    ])

dag = DAG(
    'weekly_newsletter',
    schedule_interval='0 9 * * 1',  # Every Monday at 9 AM
    start_date=datetime(2024, 1, 1)
)

generate_task = PythonOperator(
    task_id='generate_weekly_newsletter',
    python_callable=generate_weekly_newsletter,
    dag=dag
)
```

## Monitoring and Analytics

### Dashboard Features
- Real-time subscriber count
- Campaign performance metrics
- Content generation statistics
- Email delivery rates
- OpenAI API usage tracking

### Logging
- Content generation logs
- Email delivery logs
- Error tracking
- Performance metrics

## Troubleshooting

### Common Issues

1. **OpenAI API Key Not Set**
   ```
   Warning: OpenAI API key not provided - AI features will be disabled
   ```
   Solution: Add your OpenAI API key to the `.env` file

2. **SendGrid Connection Error**
   ```
   Error: Failed to send email via SendGrid
   ```
   Solution: Verify SendGrid API key and sender email configuration

3. **Market Data Unavailable**
   ```
   Warning: Market data not available, using fallback content
   ```
   Solution: Check backend API connectivity and market data sources

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python scripts/test_newsletter_generation.py --debug
```

## Advanced Features

### Custom Content Templates
Create custom templates for different newsletter types:
```html
<!-- templates/custom_newsletter.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{title}}</title>
</head>
<body>
    <h1>{{title}}</h1>
    <div class="content">{{content}}</div>
    <div class="footer">{{footer}}</div>
</body>
</html>
```

### A/B Testing
Implement A/B testing for newsletter content:
```python
# Test different content styles
variants = [
    {"style": "professional", "tone": "formal"},
    {"style": "casual", "tone": "friendly"},
    {"style": "technical", "tone": "analytical"}
]
```

### Subscriber Segmentation
Segment subscribers for targeted content:
```python
# Segment by interests
segments = {
    "technical": ["ATW", "IAM", "CIH"],
    "fundamental": ["BMCE", "ATW", "CIH"],
    "dividend": ["ATW", "IAM", "BMCE"]
}
```

## Security Considerations

### API Key Management
- Store API keys in environment variables
- Use secure key rotation
- Monitor API usage and costs
- Implement rate limiting

### Data Privacy
- GDPR compliance for subscriber data
- Secure email delivery
- Data retention policies
- Unsubscribe mechanisms

## Performance Optimization

### Caching
- Cache market data for 5 minutes
- Cache generated content for 1 hour
- Use Redis for session management

### Batch Processing
- Process multiple newsletters in batches
- Use async/await for API calls
- Implement queue system for large subscriber lists

## Cost Management

### OpenAI Usage
- Monitor token usage
- Implement content length limits
- Use efficient prompts
- Cache similar requests

### SendGrid Costs
- Monitor email volume
- Implement subscriber limits
- Use efficient templates
- Track delivery rates

## Next Steps

1. **Set up environment variables** with your API keys
2. **Test the newsletter generation** with sample content
3. **Configure email delivery** with SendGrid
4. **Set up monitoring** and analytics
5. **Integrate with Airflow** for automated scheduling
6. **Customize content templates** for your brand
7. **Implement subscriber management** system
8. **Add A/B testing** capabilities

## Support

For issues or questions:
- Check the troubleshooting section
- Review API documentation
- Test with the provided scripts
- Monitor logs for errors

---

**Note**: This newsletter system is designed to work with the existing Casablanca Insights backend and can be easily integrated with the smart IR scraping system for comprehensive financial content generation. 