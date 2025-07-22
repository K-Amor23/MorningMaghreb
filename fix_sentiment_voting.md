# 🔧 Fix Sentiment Voting 404 Issue

## Problem
The sentiment voting feature is showing as `false` in your debug panel and redirecting to 404 because the feature flag is disabled.

## Solution

### 1. Update Environment Variables

Add these environment variables to your `.env.local` file in the `apps/web` directory:

```env
# Feature Flags - Enable Sentiment Voting
NEXT_PUBLIC_ENV=development
NEXT_PUBLIC_ENABLE_SENTIMENT_VOTING=true
NEXT_PUBLIC_ENABLE_PAPER_TRADING=true
NEXT_PUBLIC_ENABLE_PREMIUM_FEATURES=true
NEXT_PUBLIC_ENABLE_ADVANCED_CHARTS=true
NEXT_PUBLIC_ENABLE_REAL_TIME_DATA=true
NEXT_PUBLIC_PREMIUM_ENFORCEMENT=false
```

### 2. Restart Development Server

After updating the environment variables, restart your development server:

```bash
# Stop the current server (Ctrl+C)
# Then restart
npm run dev
```

### 3. Verify Database Tables Exist

Make sure the sentiment voting tables exist in your Supabase database. Run this SQL in your Supabase SQL editor:

```sql
-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('sentiment_votes', 'sentiment_aggregates');

-- If tables don't exist, create them:
CREATE TABLE IF NOT EXISTS sentiment_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    sentiment VARCHAR(20) NOT NULL CHECK (sentiment IN ('bullish', 'neutral', 'bearish')),
    confidence INTEGER NOT NULL DEFAULT 3 CHECK (confidence >= 1 AND confidence <= 5),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, ticker)
);

CREATE TABLE IF NOT EXISTS sentiment_aggregates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL UNIQUE,
    bullish_count INTEGER DEFAULT 0,
    neutral_count INTEGER DEFAULT 0,
    bearish_count INTEGER DEFAULT 0,
    total_votes INTEGER DEFAULT 0,
    bullish_percentage DECIMAL(5,2) DEFAULT 0.0,
    neutral_percentage DECIMAL(5,2) DEFAULT 0.0,
    bearish_percentage DECIMAL(5,2) DEFAULT 0.0,
    average_confidence DECIMAL(3,2) DEFAULT 0.0,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);
```

### 4. Test the Fix

1. **Check Debug Panel**: The debug panel should now show `SENTIMENT_VOTING: true`
2. **Try Voting**: Go to a company page and try voting on sentiment
3. **Check Network**: Open browser dev tools and verify the API calls are working

### 5. Expected Behavior After Fix

- ✅ `SENTIMENT_VOTING: true` in debug panel
- ✅ Sentiment voting buttons work without 404 errors
- ✅ Votes are saved to Supabase database
- ✅ Real-time sentiment aggregates update

### 6. Troubleshooting

If you still get 404 errors:

1. **Check API Routes**: Verify these files exist:
   - `apps/web/pages/api/sentiment/vote.ts`
   - `apps/web/pages/api/sentiment/my-votes.ts`
   - `apps/web/pages/api/sentiment/aggregate/[ticker].ts`

2. **Check Supabase Connection**: Verify your Supabase environment variables are correct

3. **Check Authentication**: Make sure you're logged in (sentiment voting requires authentication)

4. **Check Console Errors**: Look for any JavaScript errors in the browser console

### 7. Environment Variables Reference

| Variable | Purpose | Default |
|----------|---------|---------|
| `NEXT_PUBLIC_ENABLE_SENTIMENT_VOTING` | Enable sentiment voting feature | `false` |
| `NEXT_PUBLIC_ENV` | Environment mode | `development` |
| `NEXT_PUBLIC_PREMIUM_ENFORCEMENT` | Enable premium restrictions | `false` |

## Quick Fix Command

If you want to quickly enable all features for development, add this to your `.env.local`:

```env
NEXT_PUBLIC_ENV=development
NEXT_PUBLIC_ENABLE_SENTIMENT_VOTING=true
NEXT_PUBLIC_ENABLE_PAPER_TRADING=true
NEXT_PUBLIC_ENABLE_PREMIUM_FEATURES=true
NEXT_PUBLIC_ENABLE_ADVANCED_CHARTS=true
NEXT_PUBLIC_ENABLE_REAL_TIME_DATA=true
NEXT_PUBLIC_PREMIUM_ENFORCEMENT=false
```

Then restart your development server and the sentiment voting should work! 