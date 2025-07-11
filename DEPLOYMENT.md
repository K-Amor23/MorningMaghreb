# Casablanca Insight - Deployment Guide

This guide covers the complete deployment setup for Casablanca Insight across multiple platforms.

## 🏗️ Architecture Overview

```
Frontend (Next.js) → Vercel
Backend (FastAPI) → Render
Database → Supabase
Storage → Supabase Storage
ETL Jobs → Render Background Worker
Email → SendGrid
AI → OpenAI API
```

## 📋 Prerequisites

1. **GitHub Account** - For source control and CI/CD
2. **Vercel Account** - For frontend hosting
3. **Render Account** - For backend hosting
4. **Supabase Account** - For database and auth
5. **OpenAI Account** - For AI features
6. **Stripe Account** - For payments
7. **SendGrid Account** - For email

## 🚀 Step-by-Step Deployment

### 1. Frontend Deployment (Vercel)

#### Setup Vercel Project
1. Connect your GitHub repository to Vercel
2. Configure build settings:
   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

#### Environment Variables
Add these to your Vercel project settings:
```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
OPENAI_API_KEY=your_openai_api_key
SENDGRID_API_KEY=your_sendgrid_api_key
```

### 2. Backend Deployment (Render)

#### Setup Render Services
1. Create a new Web Service for the API
2. Create a new Background Worker for ETL jobs
3. Connect your GitHub repository

#### Web Service Configuration
- **Name**: `casablanca-insight-api`
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Plan**: Free (or upgrade as needed)

#### Background Worker Configuration
- **Name**: `casablanca-insight-worker`
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `celery -A etl.celery_app worker --loglevel=info`
- **Plan**: Free (or upgrade as needed)

#### Environment Variables
Add these to both services:
```
DATABASE_URL=your_supabase_database_url
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_api_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
REDIS_URL=your_redis_url
```

### 3. Database Setup (Supabase)

#### Create Supabase Project
1. Create a new project in Supabase
2. Note down your project URL and anon key
3. Set up authentication providers (email, Google, etc.)

#### Database Schema
Run the SQL from `database/schema.sql` in your Supabase SQL editor:

```sql
-- Create tables for market data
CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price DECIMAL(10,2),
    change_percent DECIMAL(5,2),
    volume BIGINT,
    market_cap DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create tables for user portfolios
CREATE TABLE IF NOT EXISTS portfolios (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    symbol VARCHAR(10) NOT NULL,
    shares INTEGER NOT NULL,
    avg_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create tables for news articles
CREATE TABLE IF NOT EXISTS news_articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    category VARCHAR(50),
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Storage Buckets
Create storage buckets for:
- `pdf-reports` - For storing financial reports
- `user-uploads` - For user-uploaded files

### 4. Email Service (SendGrid)

#### Setup SendGrid
1. Create a SendGrid account
2. Verify your sender domain
3. Create an API key with full access
4. Add the API key to your environment variables

#### Email Templates
Create templates for:
- Welcome email
- Daily newsletter
- Market alerts
- Password reset

### 5. Payment Integration (Stripe)

#### Setup Stripe
1. Create a Stripe account
2. Get your API keys (publishable and secret)
3. Set up webhook endpoints
4. Configure products and pricing plans

#### Webhook Configuration
Set up webhooks for:
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`

### 6. AI Integration (OpenAI)

#### Setup OpenAI
1. Create an OpenAI account
2. Get your API key
3. Set up usage limits and billing
4. Test API connectivity

## 🔧 Local Development Setup

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Environment Variables (.env.local)
```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Stripe
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# SendGrid
SENDGRID_API_KEY=your_sendgrid_api_key
```

## 🚀 CI/CD Pipeline

### GitHub Actions Setup
1. Add repository secrets:
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`
   - `RENDER_SERVICE_ID`
   - `RENDER_API_KEY`

2. The workflow will automatically:
   - Run tests on pull requests
   - Deploy to staging on develop branch
   - Deploy to production on main branch

## 📊 Monitoring & Analytics

### Vercel Analytics
- Enable Vercel Analytics for frontend monitoring
- Track page views, performance, and errors

### Render Monitoring
- Monitor service health and performance
- Set up alerts for downtime

### Supabase Monitoring
- Monitor database performance
- Track authentication events
- Monitor storage usage

## 🔒 Security Considerations

### Environment Variables
- Never commit sensitive keys to version control
- Use environment-specific configurations
- Rotate keys regularly

### CORS Configuration
- Configure CORS properly for production
- Limit allowed origins to your domains

### Rate Limiting
- Implement rate limiting on API endpoints
- Protect against abuse and DDoS

### Authentication
- Use JWT tokens with proper expiration
- Implement refresh token rotation
- Secure password reset flows

## 💰 Cost Optimization

### Free Tier Limits
- **Vercel**: 100GB bandwidth, 100 serverless function executions
- **Render**: 750 hours/month for web services, 750 hours/month for workers
- **Supabase**: 500MB database, 1GB file storage, 50,000 monthly active users
- **SendGrid**: 100 emails/day
- **OpenAI**: Pay-per-use (set usage limits)

### Scaling Considerations
- Monitor usage and upgrade before hitting limits
- Consider caching strategies to reduce API calls
- Optimize database queries for performance

## 🐛 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check dependency versions
   - Verify environment variables
   - Review build logs

2. **Database Connection Issues**
   - Verify DATABASE_URL format
   - Check Supabase project status
   - Ensure proper SSL configuration

3. **CORS Errors**
   - Verify allowed origins in backend
   - Check frontend API URL configuration

4. **Authentication Issues**
   - Verify Supabase configuration
   - Check JWT token expiration
   - Review auth flow implementation

### Support Resources
- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 📈 Performance Optimization

### Frontend
- Enable Next.js image optimization
- Implement proper caching strategies
- Use dynamic imports for code splitting

### Backend
- Implement database connection pooling
- Use Redis for caching
- Optimize API response times

### Database
- Create proper indexes
- Monitor query performance
- Implement data archiving strategies

## 🔄 Maintenance

### Regular Tasks
- Monitor error logs
- Update dependencies
- Backup database
- Review security settings
- Monitor costs and usage

### Updates
- Keep dependencies updated
- Monitor for security vulnerabilities
- Test updates in staging environment
- Plan maintenance windows

---

This deployment guide covers the essential steps to get Casablanca Insight running in production. Follow each section carefully and test thoroughly before going live. 