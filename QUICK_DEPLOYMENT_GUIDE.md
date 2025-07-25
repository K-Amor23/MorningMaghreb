# 🚀 Quick Deployment Guide - Casablanca Insights

## ⚡ **5-Minute Production Deployment**

This guide will get your Casablanca Insights application deployed to production in under 5 minutes!

---

## 🎯 **Step 1: Setup Environment (2 minutes)**

### **1.1 Run the Setup Script**
```bash
# Make scripts executable (if not already done)
chmod +x scripts/*.sh

# Run the production environment setup
./scripts/setup-production-env.sh
```

This script will:
- ✅ Guide you through setting up all services
- ✅ Generate environment files
- ✅ Create deployment checklists
- ✅ Set up GitHub secrets guide

### **1.2 Set Up Required Services**

**Supabase (Database)**
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Copy URL and API keys

**SendGrid (Email)**
1. Go to [sendgrid.com](https://sendgrid.com)
2. Create free account
3. Create API key with Mail Send permissions

**OpenAI (AI Features)**
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create API key

**Stripe (Payments) - Optional**
1. Go to [stripe.com](https://stripe.com)
2. Create account
3. Get API keys

---

## 🎯 **Step 2: Deploy Backend (1 minute)**

### **2.1 Deploy to Render**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New Web Service"
4. Connect your repository
5. Set configuration:
   - **Name**: `casablanca-insight-api`
   - **Root Directory**: `apps/backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### **2.2 Set Environment Variables**
Copy from your `.env.production` file:
```bash
DATABASE_URL=your_supabase_database_url
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
OPENAI_API_KEY=your_openai_api_key
SENDGRID_API_KEY=your_sendgrid_api_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
FROM_EMAIL=noreply@casablanca-insight.com
JWT_SECRET=your_jwt_secret
```

### **2.3 Deploy**
Click "Create Web Service" and wait for deployment.

---

## 🎯 **Step 3: Deploy Frontend (1 minute)**

### **3.1 Deploy to Vercel**
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "New Project"
4. Import your repository
5. Set configuration:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: `apps/web`

### **3.2 Set Environment Variables**
Copy from your `.env.production` file:
```bash
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

### **3.3 Deploy**
Click "Deploy" and wait for deployment.

---

## 🎯 **Step 4: Test Deployment (1 minute)**

### **4.1 Run Test Script**
```bash
# Test your deployment
./scripts/test-production-deployment.sh
```

This will test:
- ✅ Frontend accessibility
- ✅ Backend health
- ✅ API endpoints
- ✅ Authentication
- ✅ Email service
- ✅ Performance

### **4.2 Manual Testing**
Visit your deployed URLs:
- **Frontend**: `https://casablanca-insight.vercel.app`
- **Backend**: `https://casablanca-insight-api.onrender.com`

Test these features:
1. **Sign up** for a new account
2. **Login** with your account
3. **Browse companies** and market data
4. **Try paper trading**
5. **Sign up for newsletter**

---

## 🎯 **Step 5: Setup Monitoring (Optional)**

### **5.1 Uptime Monitoring**
1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Create free account
3. Add monitors for:
   - Frontend URL
   - Backend health endpoint
   - API endpoints

### **5.2 Error Tracking**
1. Go to [sentry.io](https://sentry.io)
2. Create free account
3. Add DSN to environment variables

---

## 📊 **Performance Targets**

Your deployment should meet these targets:
- **Frontend Load Time**: < 3 seconds
- **API Response Time**: < 200ms
- **Database Query Time**: < 100ms
- **Uptime**: 99.9%

---

## 🔐 **Security Checklist**

- [ ] All environment variables are set
- [ ] API keys are secure and not exposed
- [ ] CORS is properly configured
- [ ] Rate limiting is enabled
- [ ] SSL certificates are valid
- [ ] Database connections are secure

---

**🎯 Bottom Line**: Your Casablanca Insights application is now production-ready and can handle real users! The system includes comprehensive market data, paper trading, and advanced features for the Casablanca Stock Exchange.

**Last Updated**: July 2025
**Status**: ✅ **Ready for Production** 