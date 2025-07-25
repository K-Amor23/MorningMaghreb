# 📧 Email Service Setup Guide - Casablanca Insights

## 🎯 **Overview**

This guide will help you set up email services for your Casablanca Insights application. We support multiple email providers with automatic fallback:

1. **SendGrid** (Recommended for production)
2. **Supabase Email** (Built-in with your database)
3. **SMTP** (Development fallback)

---

## 🚀 **Option 1: SendGrid Setup (Recommended)**

### **Step 1: Create SendGrid Account**

1. **Go to SendGrid**
   - Visit [sendgrid.com](https://sendgrid.com)
   - Click "Start for Free"
   - Sign up with your email

2. **Verify Your Account**
   - Check your email for verification
   - Complete the account setup

### **Step 2: Create API Key**

1. **Navigate to API Keys**
   - Go to Settings → API Keys
   - Click "Create API Key"

2. **Configure API Key**
   ```
   Name: Casablanca Insights
   Permissions: Full Access (or Restricted Access with Mail Send)
   ```

3. **Copy the API Key**
   - Save the API key securely
   - You won't be able to see it again

### **Step 3: Verify Sender Email**

1. **Go to Sender Authentication**
   - Navigate to Settings → Sender Authentication
   - Choose "Single Sender Verification"

2. **Add Your Email**
   ```
   From Name: Casablanca Insights
   From Email: noreply@casablanca-insight.com
   Company: Casablanca Insights
   Address: Your address
   City: Your city
   Country: Your country
   ```

3. **Verify Email**
   - Check your email for verification link
   - Click the verification link

### **Step 4: Set Environment Variables**

Add to your `.env.production` file:
```bash
SENDGRID_API_KEY=your_sendgrid_api_key_here
FROM_EMAIL=noreply@casablanca-insight.com
```

### **Step 5: Test SendGrid**

```bash
# Test email sending
curl -X POST https://your-backend-url/api/newsletter/send-test \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

---

## 🗄️ **Option 2: Supabase Email Setup**

### **Step 1: Configure Supabase Email**

1. **Go to Supabase Dashboard**
   - Visit [supabase.com](https://supabase.com)
   - Open your project

2. **Navigate to Authentication**
   - Go to Authentication → Settings
   - Scroll to "SMTP Settings"

3. **Configure SMTP**
   ```
   Host: smtp.gmail.com (or your SMTP provider)
   Port: 587
   Username: your-email@gmail.com
   Password: your-app-password
   Sender Name: Casablanca Insights
   Sender Email: noreply@casablanca-insight.com
   ```

### **Step 2: Set Environment Variables**

Add to your `.env.production` file:
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
FROM_EMAIL=noreply@casablanca-insight.com
```

### **Step 3: Test Supabase Email**

```bash
# Test email sending
curl -X POST https://your-backend-url/api/newsletter/send-test \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

---

## 🔧 **Option 3: Custom SMTP Setup**

### **Step 1: Choose SMTP Provider**

Popular options:
- **Gmail**: smtp.gmail.com:587
- **Outlook**: smtp-mail.outlook.com:587
- **Yahoo**: smtp.mail.yahoo.com:587
- **Custom**: Your own SMTP server

### **Step 2: Configure SMTP**

Add to your `.env.production` file:
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@casablanca-insight.com
```

### **Step 3: Update Email Service**

Modify `apps/backend/lib/email_service.py` to use your SMTP settings:

```python
# Add to EmailService.__init__()
self.smtp_host = os.getenv("SMTP_HOST")
self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
self.smtp_username = os.getenv("SMTP_USERNAME")
self.smtp_password = os.getenv("SMTP_PASSWORD")
```

---

## 📧 **Email Templates**

### **Welcome Email Template**

The system automatically generates beautiful welcome emails:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Welcome to Casablanca Insights</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .button { background: #667eea; color: white; padding: 12px 30px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 Welcome to Casablanca Insights!</h1>
    </div>
    <div class="content">
        <h2>Hello {name}!</h2>
        <p>Thank you for joining Casablanca Insights!</p>
        <a href="{dashboard_url}" class="button">Go to Dashboard</a>
    </div>
</body>
</html>
```

### **Newsletter Template**

Weekly market recap emails:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Weekly Market Recap</title>
</head>
<body>
    <div class="header">
        <h1>📈 Casablanca Insights</h1>
        <p>Weekly Market Recap</p>
    </div>
    <div class="content">
        {content}
    </div>
</body>
</html>
```

### **Password Reset Template**

Secure password reset emails:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Reset Your Password</title>
</head>
<body>
    <div class="header">
        <h1>🔐 Password Reset</h1>
    </div>
    <div class="content">
        <p>Click the button below to reset your password:</p>
        <a href="{reset_url}" class="button">Reset Password</a>
    </div>
</body>
</html>
```

---

## 🧪 **Testing Email Service**

### **Test Script**

Create a test script to verify email functionality:

```python
# test_email.py
import asyncio
from lib.email_service import send_email, send_welcome_email

async def test_email():
    # Test basic email
    success = await send_email(
        to_email="test@example.com",
        subject="Test Email",
        content="This is a test email from Casablanca Insights"
    )
    print(f"Basic email: {'✅ Success' if success else '❌ Failed'}")
    
    # Test welcome email
    success = await send_welcome_email(
        email="test@example.com",
        name="Test User"
    )
    print(f"Welcome email: {'✅ Success' if success else '❌ Failed'}")

if __name__ == "__main__":
    asyncio.run(test_email())
```

### **API Testing**

Test via API endpoints:

```bash
# Test newsletter signup
curl -X POST http://localhost:8000/api/newsletter/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Test welcome email
curl -X POST http://localhost:8000/api/newsletter/send-test \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

---

## 📊 **Email Analytics & Tracking**

### **SendGrid Analytics**

If using SendGrid, you get access to:

- **Open Rates**: Track email opens
- **Click Rates**: Track link clicks
- **Bounce Rates**: Monitor delivery issues
- **Spam Reports**: Track spam complaints
- **Unsubscribe Rates**: Monitor engagement

### **Custom Tracking**

Add tracking to your emails:

```python
# Add tracking parameters
tracking_url = f"{site_url}/email/track?email={email}&campaign={campaign_id}"

# Add to email content
html_content = html_content.replace(
    '</body>',
    f'<img src="{tracking_url}" width="1" height="1" style="display:none;" /></body>'
)
```

---

## 🔒 **Security Best Practices**

### **Email Security**

1. **Use App Passwords**
   - Don't use your main password for SMTP
   - Generate app-specific passwords

2. **Verify Sender Domains**
   - Set up SPF, DKIM, and DMARC records
   - Improve email deliverability

3. **Rate Limiting**
   - Limit email sending rates
   - Prevent abuse

4. **Unsubscribe Compliance**
   - Include unsubscribe links
   - Honor unsubscribe requests

### **Environment Variables**

Never commit email credentials to version control:

```bash
# ✅ Good - Use environment variables
SENDGRID_API_KEY=your_api_key_here

# ❌ Bad - Don't hardcode in files
SENDGRID_API_KEY=SG.abc123...
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

**SendGrid Issues**
```bash
# Check API key
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.sendgrid.com/v3/user/profile

# Check sender verification
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.sendgrid.com/v3/verified_senders
```

**Supabase Email Issues**
```bash
# Check SMTP settings in Supabase dashboard
# Verify sender email is configured
# Check service role key permissions
```

**SMTP Issues**
```bash
# Test SMTP connection
telnet smtp.gmail.com 587

# Check credentials
# Verify app passwords for Gmail
```

### **Error Messages**

**"Authentication failed"**
- Check API key/credentials
- Verify sender email is verified
- Check SMTP settings

**"Rate limit exceeded"**
- Reduce email sending frequency
- Upgrade SendGrid plan
- Implement rate limiting

**"Email not delivered"**
- Check spam folder
- Verify sender domain
- Check bounce handling

---

## 📈 **Production Recommendations**

### **For Production Use**

1. **Use SendGrid**
   - Best deliverability
   - Comprehensive analytics
   - Reliable infrastructure

2. **Set Up Domain Authentication**
   - Configure SPF, DKIM, DMARC
   - Use custom domain for sending

3. **Monitor Email Metrics**
   - Track open rates
   - Monitor bounce rates
   - Watch for spam complaints

4. **Implement Rate Limiting**
   - Limit emails per user
   - Respect unsubscribe requests
   - Follow email best practices

### **Scaling Considerations**

- **Bulk Email**: Use SendGrid's bulk sending
- **Templates**: Create reusable email templates
- **Segmentation**: Send targeted emails
- **Automation**: Set up email workflows

---

## 🎯 **Quick Setup Checklist**

### **SendGrid Setup**
- [ ] Create SendGrid account
- [ ] Generate API key
- [ ] Verify sender email
- [ ] Set environment variables
- [ ] Test email sending

### **Supabase Setup**
- [ ] Configure SMTP in Supabase
- [ ] Set environment variables
- [ ] Test email sending
- [ ] Verify sender settings

### **Testing**
- [ ] Test welcome emails
- [ ] Test newsletter emails
- [ ] Test password reset emails
- [ ] Verify email delivery
- [ ] Check spam folder

### **Production**
- [ ] Set up domain authentication
- [ ] Configure monitoring
- [ ] Set up rate limiting
- [ ] Test with real users

---

## 📞 **Support Resources**

### **SendGrid**
- **Documentation**: https://sendgrid.com/docs
- **Support**: https://support.sendgrid.com
- **API Reference**: https://sendgrid.com/docs/API_Reference

### **Supabase**
- **Documentation**: https://supabase.com/docs
- **Support**: https://supabase.com/support
- **Community**: https://github.com/supabase/supabase

### **General Email**
- **Email Best Practices**: https://www.emailbestpractices.com
- **Deliverability Guide**: https://sendgrid.com/blog/email-deliverability-guide

---

**🎯 Bottom Line**: Set up SendGrid for the best email experience, or use Supabase's built-in email for simplicity. Both options will work well for your Casablanca Insights application!

**Last Updated**: July 2025
**Status**: ✅ **Ready for Production** 