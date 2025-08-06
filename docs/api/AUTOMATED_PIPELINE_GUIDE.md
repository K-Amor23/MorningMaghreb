# 🚀 Automated Pipeline Guide for Vercel + Supabase

## Overview

This guide sets up a fully automated data pipeline that runs continuously using Vercel and Supabase. The pipeline automatically scrapes market data, stores it in Supabase, and updates your website.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Actions│    │   Vercel Cron   │    │   Supabase DB   │
│                 │    │                 │    │                 │
│ • Every 6 hours │    │ • Every 6 hours │    │ • Real-time data│
│ • Manual trigger│    │ • API endpoint  │    │ • Notifications │
│ • Auto deploy   │    │ • Data updates  │    │ • Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vercel Site   │    │   Admin Panel   │    │   Real-time UI  │
│                 │    │                 │    │                 │
│ • Auto deployed │    │ • Pipeline monitor│   │ • Live updates  │
│ • Password protected│ │ • Manual triggers│   │ • Market data   │
│ • Production    │    │ • Status alerts │    │ • Charts        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 What's Been Set Up

### ✅ 1. GitHub Actions Workflow
- **Location**: `.github/workflows/automated-pipeline.yml`
- **Schedule**: Every 6 hours
- **Features**:
  - Automatic code deployment
  - Database updates
  - Vercel deployment
  - Success/failure notifications

### ✅ 2. Vercel Cron Job
- **Location**: `apps/web/pages/api/cron/pipeline.ts`
- **Schedule**: Every 6 hours
- **Features**:
  - Updates market data
  - Stores in Supabase
  - Logs execution
  - Sends notifications

### ✅ 3. Monitoring Dashboard
- **Location**: `apps/web/pages/admin/pipeline-monitor.tsx`
- **Access**: Admin users only
- **Features**:
  - Real-time pipeline status
  - Manual trigger button
  - Data quality metrics
  - Automation status

### ✅ 4. Supabase Database Tables
- **Location**: `database/master_pipeline_tables.sql`
- **Tables**:
  - `company_prices` - Market data
  - `market_indices` - Index data
  - `macro_indicators` - Economic data
  - `pipeline_notifications` - Status logs
  - `data_quality_logs` - Quality metrics

## 🔧 Setup Instructions

### Step 1: Add GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions, and add:

```
NEXT_PUBLIC_SUPABASE_URL=https://supabase-sky-garden.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
VERCEL_TOKEN=your_vercel_token
VERCEL_ORG_ID=your_vercel_org_id
VERCEL_PROJECT_ID=your_vercel_project_id
```

### Step 2: Deploy the Pipeline

```bash
# Commit and push all changes
git add .
git commit -m "Setup automated pipeline"
git push origin main

# Deploy to Vercel
cd apps/web
npx vercel --prod
```

### Step 3: Test the Pipeline

1. **Manual Trigger**: Visit `/admin/pipeline-monitor` and click "Trigger Pipeline Now"
2. **Automatic Test**: Wait for the next 6-hour cycle
3. **GitHub Actions**: Check the Actions tab in your GitHub repository

## 📊 Monitoring & Management

### Admin Dashboard
- **URL**: `https://morningmaghreb.com/admin/pipeline-monitor`
- **Access**: Admin users only
- **Features**:
  - Real-time pipeline status
  - Last run information
  - Data quality metrics
  - Manual trigger button

### GitHub Actions
- **URL**: `https://github.com/K-Amor23/MorningMaghreb/actions`
- **Features**:
  - Workflow execution history
  - Success/failure logs
  - Manual trigger option

### Vercel Dashboard
- **URL**: `https://vercel.com/dashboard`
- **Features**:
  - Deployment status
  - Function logs
  - Performance metrics

## 🔄 Pipeline Schedule

| Component | Frequency | Description |
|-----------|-----------|-------------|
| GitHub Actions | Every 6 hours | Full pipeline execution |
| Vercel Cron | Every 6 hours | Data updates |
| Manual Trigger | On-demand | Admin dashboard |
| Real-time Updates | Continuous | Supabase subscriptions |

## 📈 Data Flow

1. **Data Sources** → Mock data (replace with real scrapers)
2. **Processing** → Data validation and transformation
3. **Storage** → Supabase database tables
4. **Notification** → Success/failure alerts
5. **Display** → Real-time website updates

## 🛠️ Customization

### Adding Real Data Sources

Replace mock data in `apps/web/pages/api/cron/pipeline.ts`:

```typescript
// Replace mockCompanyData with real scraping
const realCompanyData = await scrapeAfricanMarkets()
const realMarketData = await scrapeCasablancaBourse()
const realMacroData = await scrapeBankAlMaghrib()
```

### Modifying Schedule

Update the cron schedule in:
- `.github/workflows/automated-pipeline.yml` (GitHub Actions)
- `apps/web/pages/api/cron/pipeline.ts` (Vercel Cron)

### Adding New Data Types

1. Add new table to `database/master_pipeline_tables.sql`
2. Update pipeline API in `apps/web/pages/api/cron/pipeline.ts`
3. Add monitoring in `apps/web/pages/admin/pipeline-monitor.tsx`

## 🚨 Troubleshooting

### Common Issues

1. **Pipeline not running**:
   - Check GitHub Actions tab
   - Verify secrets are set correctly
   - Check Vercel function logs

2. **Data not updating**:
   - Verify Supabase credentials
   - Check database table permissions
   - Test manual trigger

3. **Admin dashboard not loading**:
   - Ensure user has admin privileges
   - Check Supabase connection
   - Verify table exists

### Debug Commands

```bash
# Test pipeline manually
curl -X POST https://morningmaghreb.com/api/cron/pipeline

# Check GitHub Actions
gh run list --workflow=automated-pipeline.yml

# View Vercel logs
vercel logs --follow
```

## 🎯 Next Steps

1. **Replace Mock Data**: Implement real data scrapers
2. **Add Error Handling**: Improve failure recovery
3. **Expand Monitoring**: Add more detailed metrics
4. **Optimize Performance**: Reduce execution time
5. **Add Notifications**: Email/Slack alerts

## 📞 Support

- **GitHub Issues**: Report bugs and feature requests
- **Admin Dashboard**: Monitor pipeline status
- **Vercel Dashboard**: Check deployment status
- **Supabase Dashboard**: Monitor database

---

**🎉 Your automated pipeline is now ready to run continuously!** 