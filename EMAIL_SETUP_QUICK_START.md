# 📧 Email Service Quick Start - Casablanca Insights

## ⚡ **5-Minute Email Setup**

This guide will get your email service working in under 5 minutes!

---

## 🎯 **Option 1: SendGrid (Recommended)**

### **Step 1: Create SendGrid Account**
1. Go to [sendgrid.com](https://sendgrid.com)
2. Click "Start for Free"
3. Sign up with your email

### **Step 2: Get API Key**
1. Go to Settings → API Keys
2. Click "Create API Key"
3. Name: "Casablanca Insights"
4. Permissions: "Full Access"
5. Copy the API key

### **Step 3: Verify Sender Email**
1. Go to Settings → Sender Authentication
2. Choose "Single Sender Verification"
3. Add: `noreply@casablanca-insight.com`
4. Verify via email

### **Step 4: Set Environment Variables**
```bash
# Add to your .env.production file
SENDGRID_API_KEY=your_api_key_here
FROM_EMAIL=noreply@casablanca-insight.com
```

### **Step 5: Test**
```bash
# Run the test script
python scripts/test_email_service.py
```

---

## 🗄️ **Option 2: Supabase Email**

### **Step 1: Configure Supabase**
1. Go to your Supabase project
2. Navigate to Authentication → Settings
3. Scroll to "SMTP Settings"
4. Configure with your email provider

### **Step 2: Set Environment Variables**
```bash
# Add to your .env.production file
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
FROM_EMAIL=noreply@casablanca-insight.com
```

### **Step 3: Test**
```bash
# Run the test script
python scripts/test_email_service.py
```

---

## 🔧 **Option 3: Gmail SMTP (Development)**

### **Step 1: Create App Password**
1. Go to your Google Account settings
2. Security → 2-Step Verification → App passwords
3. Generate app password for "Mail"

### **Step 2: Set Environment Variables**
```bash
# Add to your .env.production file
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@casablanca-insight.com
```

### **Step 3: Test**
```bash
# Run the test script
python scripts/test_email_service.py
```

---

## 🧪 **Testing Your Email Setup**

### **Run the Test Script**
```bash
# From project root
python scripts/test_email_service.py
```

This will test:
- ✅ Basic email sending
- ✅ Welcome emails
- ✅ Newsletter emails
- ✅ Password reset emails
- ✅ Bulk email sending

### **Test via API**
```bash
# Test newsletter signup
curl -X POST http://localhost:8000/api/newsletter/send-test \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

---

## 📧 **Email Types Available**

### **1. Welcome Emails**
```python
from lib.email_service import send_welcome_email

await send_welcome_email(
    email="user@example.com",
    name="John Doe"
)
```

### **2. Newsletter Emails**
```python
from lib.email_service import send_newsletter

await send_newsletter(
    email="user@example.com",
    subject="Weekly Market Recap",
    content="Market summary content..."
)
```

### **3. Password Reset Emails**
```python
from lib.email_service import send_password_reset

await send_password_reset(
    email="user@example.com",
    reset_token="reset_token_123"
)
```

### **4. Custom Emails**
```python
from lib.email_service import send_email

await send_email(
    to_email="user@example.com",
    subject="Custom Subject",
    content="Email content",
    html_content="<h1>HTML Content</h1>"
)
```

### **5. Bulk Emails**
```python
from lib.email_service import send_bulk_email

await send_bulk_email(
    subscribers=["user1@example.com", "user2@example.com"],
    subject="Bulk Email",
    content="Bulk email content"
)
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

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

### **Test Commands**

**SendGrid**
```bash
# Test API key
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.sendgrid.com/v3/user/profile
```

**Supabase**
```bash
# Check SMTP settings in Supabase dashboard
# Verify sender email is configured
```

**SMTP**
```bash
# Test SMTP connection
telnet smtp.gmail.com 587
```

---

## 📊 **Email Analytics**

### **SendGrid Analytics**
If using SendGrid, you get:
- Open rates
- Click rates
- Bounce rates
- Spam reports
- Unsubscribe rates

### **Custom Tracking**
Add tracking to emails:
```python
tracking_url = f"{site_url}/email/track?email={email}&campaign={campaign_id}"
```

---

## 🔒 **Security Best Practices**

1. **Use App Passwords** - Don't use main passwords for SMTP
2. **Verify Sender Domains** - Set up SPF, DKIM, DMARC
3. **Rate Limiting** - Limit email sending rates
4. **Unsubscribe Compliance** - Include unsubscribe links

---

## 🎯 **Quick Checklist**

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

### **Testing**
- [ ] Run test script
- [ ] Test welcome emails
- [ ] Test newsletter emails
- [ ] Verify email delivery

---

## 📞 **Support**

### **SendGrid**
- Documentation: https://sendgrid.com/docs
- Support: https://support.sendgrid.com

### **Supabase**
- Documentation: https://supabase.com/docs
- Support: https://supabase.com/support

---

**🎯 Bottom Line**: Use SendGrid for production, Supabase for simplicity, or Gmail SMTP for development. All options work with your Casablanca Insights application!

**Last Updated**: July 2025
**Status**: ✅ **Ready to Use** 