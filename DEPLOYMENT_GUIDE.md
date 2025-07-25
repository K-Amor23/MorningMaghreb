# 🚀 Production Deployment Guide - Casablanca Insights

## 📋 **Deployment Overview**

This guide will help you deploy Casablanca Insights to production with:
- **Frontend**: Vercel (Next.js)
- **Backend**: Render (FastAPI)
- **Database**: Supabase (PostgreSQL)
- **Email**: SendGrid
- **Monitoring**: Uptime Robot + Sentry

---

## 🎯 **Step 1: Environment Variables Setup**

### **Required Environment Variables**

Create a `.env.production` file in the root directory:

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Stripe Configuration
STRIPE_SECRET_KEY=your_stripe_secret_key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# SendGrid Configuration
SENDGRID_API_KEY=your_sendgrid_api_key
FROM_EMAIL=noreply@casablanca-insight.com

# Production Configuration
NEXT_PUBLIC_ENV=production
NEXT_PUBLIC_API_URL=https://casablanca-insight-api.onrender.com
NEXT_PUBLIC_SITE_URL=https://casablanca-insight.vercel.app

# Database Configuration
DATABASE_URL=your_supabase_database_url

# Redis Configuration (for caching)
REDIS_URL=your_redis_url

# JWT Configuration
JWT_SECRET=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# Monitoring Configuration
SENTRY_DSN=your_sentry_dsn
UPTIME_ROBOT_API_KEY=your_uptime_robot_api_key

# Feature Flags
NEXT_PUBLIC_PREMIUM_ENFORCEMENT=true
NEXT_PUBLIC_ENABLE_PREMIUM_FEATURES=true
NEXT_PUBLIC_ENABLE_PAPER_TRADING=true
NEXT_PUBLIC_ENABLE_SENTIMENT_VOTING=true
NEXT_PUBLIC_ENABLE_ADVANCED_CHARTS=true
NEXT_PUBLIC_ENABLE_REAL_TIME_DATA=true
```

---

## 🎯 **Step 2: Backend Deployment (Render)**

### **2.1 Create Render Account**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your repository

### **2.2 Deploy Backend Service**

1. **Create New Web Service**
   - Repository: `your-username/casablanca-insights`
   - Root Directory: `apps/backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Set Environment Variables in Render**
   ```bash
   # Copy from your .env.production file
   DATABASE_URL=your_supabase_database_url
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   OPENAI_API_KEY=your_openai_api_key
   STRIPE_SECRET_KEY=your_stripe_secret_key
   STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
   SENDGRID_API_KEY=your_sendgrid_api_key
   FROM_EMAIL=noreply@casablanca-insight.com
   JWT_SECRET=your_jwt_secret_key
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION=3600
   REDIS_URL=your_redis_url
   SENTRY_DSN=your_sentry_dsn
   ```

3. **Deploy the Service**
   - Click "Create Web Service"
   - Wait for build to complete
   - Note the service URL (e.g., `https://casablanca-insight-api.onrender.com`)

### **2.3 Deploy Background Worker (Optional)**

1. **Create New Background Worker**
   - Repository: `your-username/casablanca-insights`
   - Root Directory: `apps/backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `celery -A etl.celery_app worker --loglevel=info`

2. **Set Same Environment Variables**
   - Copy all environment variables from the web service

---

## 🎯 **Step 3: Frontend Deployment (Vercel)**

### **3.1 Create Vercel Account**
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Import your repository

### **3.2 Deploy Frontend**

1. **Import Repository**
   - Repository: `your-username/casablanca-insights`
   - Framework Preset: `Next.js`
   - Root Directory: `apps/web`

2. **Set Environment Variables in Vercel**
   ```bash
   # Copy from your .env.production file
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   NEXT_PUBLIC_API_URL=https://casablanca-insight-api.onrender.com
   NEXT_PUBLIC_SITE_URL=https://casablanca-insight.vercel.app
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
   NEXT_PUBLIC_ENV=production
   NEXT_PUBLIC_PREMIUM_ENFORCEMENT=true
   NEXT_PUBLIC_ENABLE_PREMIUM_FEATURES=true
   NEXT_PUBLIC_ENABLE_PAPER_TRADING=true
   NEXT_PUBLIC_ENABLE_SENTIMENT_VOTING=true
   NEXT_PUBLIC_ENABLE_ADVANCED_CHARTS=true
   NEXT_PUBLIC_ENABLE_REAL_TIME_DATA=true
   ```

3. **Deploy the Application**
   - Click "Deploy"
   - Wait for build to complete
   - Note the deployment URL

---

## 🎯 **Step 4: Email Service Setup (SendGrid)**

### **4.1 Create SendGrid Account**
1. Go to [sendgrid.com](https://sendgrid.com)
2. Sign up for a free account
3. Verify your domain or use single sender verification

### **4.2 Configure SendGrid**

1. **Create API Key**
   ```bash
   # In SendGrid Dashboard
   Settings > API Keys > Create API Key
   # Name: "Casablanca Insights"
   # Permissions: "Full Access" or "Restricted Access" with Mail Send
   ```

2. **Verify Sender Email**
   ```bash
   # Settings > Sender Authentication
   # Add: noreply@casablanca-insight.com
   # Verify via email or DNS
   ```

3. **Create Email Templates**
   ```bash
   # Marketing > Dynamic Templates
   # Create templates for:
   # - Welcome Email
   # - Newsletter
   # - Password Reset
   # - Account Verification
   ```

### **4.3 Test Email Service**

```bash
# Test email sending
curl -X POST https://casablanca-insight-api.onrender.com/api/newsletter/send-test \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "subject": "Test Email"}'
```

---

## 🎯 **Step 5: Monitoring Setup**

### **5.1 Uptime Robot Setup**

1. **Create Account**
   - Go to [uptimerobot.com](https://uptimerobot.com)
   - Sign up for free account

2. **Add Monitors**
   ```bash
   # Frontend Monitor
   URL: https://casablanca-insight.vercel.app
   Type: HTTP(s)
   Interval: 5 minutes
   Alert: Email + Slack

   # Backend Monitor
   URL: https://casablanca-insight-api.onrender.com/health
   Type: HTTP(s)
   Interval: 5 minutes
   Alert: Email + Slack

   # API Monitor
   URL: https://casablanca-insight-api.onrender.com/api/health
   Type: HTTP(s)
   Interval: 5 minutes
   Alert: Email + Slack
   ```

### **5.2 Sentry Setup (Error Tracking)**

1. **Create Sentry Account**
   - Go to [sentry.io](https://sentry.io)
   - Sign up and create new project

2. **Configure Sentry**
   ```bash
   # Get DSN from Sentry project settings
   # Add to environment variables
   SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
   ```

3. **Add Sentry to Frontend**
   ```bash
   # Install Sentry SDK
   npm install @sentry/nextjs

   # Configure in next.config.js
   const { withSentryConfig } = require('@sentry/nextjs');
   ```

---

## 🎯 **Step 6: Domain & SSL Setup**

### **6.1 Custom Domain (Optional)**

1. **Add Custom Domain to Vercel**
   ```bash
   # In Vercel Dashboard
   Settings > Domains > Add Domain
   # Add: casablanca-insight.com
   ```

2. **Configure DNS**
   ```bash
   # Add CNAME record
   Type: CNAME
   Name: @
   Value: cname.vercel-dns.com
   ```

3. **Add Custom Domain to Render**
   ```bash
   # In Render Dashboard
   Settings > Custom Domains > Add Domain
   # Add: api.casablanca-insight.com
   ```

### **6.2 SSL Certificates**
- Vercel and Render provide automatic SSL certificates
- No additional configuration needed

---

## 🎯 **Step 7: Database Setup (Supabase)**

### **7.1 Supabase Configuration**

1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Note the URL and API keys

2. **Run Database Migrations**
   ```bash
   # Connect to Supabase SQL Editor
   # Run the schema files:
   # - database/schema.sql
   # - database/advanced_features_supabase.sql
   # - database/volume_analysis_schema.sql
   ```

3. **Set Row Level Security**
   ```bash
   # Enable RLS on all tables
   # Configure policies for user data isolation
   ```

### **7.2 Test Database Connection**

```bash
# Test database connectivity
curl -X GET https://casablanca-insight-api.onrender.com/api/health/database
```

---

## 🎯 **Step 8: End-to-End Testing**

### **8.1 Health Checks**

```bash
# Frontend Health Check
curl -I https://casablanca-insight.vercel.app

# Backend Health Check
curl -I https://casablanca-insight-api.onrender.com/health

# API Health Check
curl -I https://casablanca-insight-api.onrender.com/api/health
```

### **8.2 Feature Testing**

1. **Authentication Flow**
   ```bash
   # Test signup/login
   # Visit: https://casablanca-insight.vercel.app/signup
   # Create account and verify login
   ```

2. **API Endpoints**
   ```bash
   # Test company data
   curl https://casablanca-insight-api.onrender.com/api/companies

   # Test market data
   curl https://casablanca-insight-api.onrender.com/api/markets/quotes

   # Test sentiment voting
   curl -X POST https://casablanca-insight-api.onrender.com/api/sentiment/vote \
     -H "Content-Type: application/json" \
     -d '{"ticker": "ATW", "sentiment": "bullish", "confidence": 4}'
   ```

3. **Email Functionality**
   ```bash
   # Test newsletter signup
   curl -X POST https://casablanca-insight-api.onrender.com/api/newsletter/signup \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com"}'
   ```

### **8.3 Performance Testing**

```bash
# Test API response times
curl -w "@curl-format.txt" -o /dev/null -s https://casablanca-insight-api.onrender.com/api/companies

# Test frontend load time
# Use browser dev tools or Lighthouse
```

---

## 🎯 **Step 9: CI/CD Pipeline**

### **9.1 GitHub Actions Setup**

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd apps/web
          npm ci
      - name: Run tests
        run: |
          cd apps/web
          npm run test

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./apps/web

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Render
        run: |
          # Render auto-deploys on push to main
          echo "Deployment triggered"
```

### **9.2 Environment Secrets**

Add these secrets to GitHub repository:

```bash
# Vercel Secrets
VERCEL_TOKEN=your_vercel_token
VERCEL_ORG_ID=your_vercel_org_id
VERCEL_PROJECT_ID=your_vercel_project_id

# Render Secrets (if using manual deployment)
RENDER_TOKEN=your_render_token
RENDER_SERVICE_ID=your_render_service_id
```

---

## 🎯 **Step 10: Post-Deployment Checklist**

### **10.1 Security Checklist**
- [ ] All environment variables are set
- [ ] API keys are secure and not exposed
- [ ] CORS is properly configured
- [ ] Rate limiting is enabled
- [ ] SSL certificates are valid
- [ ] Database connections are secure

### **10.2 Performance Checklist**
- [ ] Frontend loads in <3 seconds
- [ ] API responses are <200ms
- [ ] Database queries are optimized
- [ ] Caching is implemented
- [ ] CDN is configured

### **10.3 Monitoring Checklist**
- [ ] Uptime monitors are active
- [ ] Error tracking is working
- [ ] Performance monitoring is set up
- [ ] Alerts are configured
- [ ] Logs are being collected

### **10.4 Feature Checklist**
- [ ] Authentication works
- [ ] Paper trading functions
- [ ] Newsletter signup works
- [ ] Sentiment voting works
- [ ] Mobile app is functional
- [ ] All API endpoints respond

---

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Build Failures**
   ```bash
   # Check build logs in Vercel/Render
   # Verify all dependencies are in package.json/requirements.txt
   # Check for TypeScript errors
   ```

2. **Environment Variables**
   ```bash
   # Verify all variables are set in deployment platforms
   # Check for typos in variable names
   # Ensure sensitive data is not exposed
   ```

3. **Database Connection**
   ```bash
   # Verify DATABASE_URL is correct
   # Check Supabase connection limits
   # Test connection from deployment environment
   ```

4. **CORS Issues**
   ```bash
   # Verify CORS configuration in backend
   # Check frontend API URL is correct
   # Test API calls from browser console
   ```

### **Support Resources**
- Vercel Documentation: https://vercel.com/docs
- Render Documentation: https://render.com/docs
- Supabase Documentation: https://supabase.com/docs
- SendGrid Documentation: https://sendgrid.com/docs

---

## 🎉 **Deployment Complete!**

Your Casablanca Insights application is now deployed to production with:
- ✅ Frontend on Vercel
- ✅ Backend on Render
- ✅ Database on Supabase
- ✅ Email service on SendGrid
- ✅ Monitoring with Uptime Robot + Sentry
- ✅ Custom domain and SSL
- ✅ CI/CD pipeline

**Next Steps:**
1. Monitor the application for 24-48 hours
2. Gather user feedback
3. Optimize performance based on usage
4. Plan feature enhancements

---

**Last Updated**: July 2025
**Status**: ✅ **Ready for Production Deployment** 