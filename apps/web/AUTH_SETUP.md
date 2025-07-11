# Authentication & Watchlist Setup Guide

This guide will help you set up the authentication and watchlist features for Casablanca Insights.

## Prerequisites

1. A Supabase project
2. Environment variables configured

## Environment Variables

Make sure you have the following environment variables set in your `.env.local` file:

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Supabase Setup

### 1. Create the Watchlist Table

Run the SQL script in your Supabase SQL editor:

```sql
-- Create watchlists table
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, ticker)
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON watchlists (user_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_ticker ON watchlists (ticker);

-- Enable Row Level Security (RLS)
ALTER TABLE watchlists ENABLE ROW LEVEL SECURITY;

-- Create policy to allow users to only see their own watchlist items
CREATE POLICY "Users can view their own watchlist items" ON watchlists
    FOR SELECT USING (auth.uid() = user_id);

-- Create policy to allow users to insert their own watchlist items
CREATE POLICY "Users can insert their own watchlist items" ON watchlists
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Create policy to allow users to delete their own watchlist items
CREATE POLICY "Users can delete their own watchlist items" ON watchlists
    FOR DELETE USING (auth.uid() = user_id);

-- Create policy to allow users to update their own watchlist items
CREATE POLICY "Users can update their own watchlist items" ON watchlists
    FOR UPDATE USING (auth.uid() = user_id);
```

### 2. Configure Authentication

1. Go to your Supabase dashboard
2. Navigate to Authentication > Settings
3. Configure your site URL and redirect URLs:
   - Site URL: `http://localhost:3000` (for development)
   - Redirect URLs: `http://localhost:3000/dashboard`

### 3. Enable Email Authentication

1. Go to Authentication > Providers
2. Enable Email provider
3. Configure email templates if needed

## Features Implemented

### Authentication
- ✅ Sign up with email/password
- ✅ Sign in with email/password
- ✅ Auto-login with session persistence
- ✅ Sign out functionality
- ✅ Protected routes (dashboard requires authentication)

### Watchlist Management
- ✅ Add Moroccan stock tickers to watchlist
- ✅ Remove tickers from watchlist
- ✅ Display watchlist with real-time price data
- ✅ Duplicate ticker prevention
- ✅ User-specific watchlists

### UI Components
- ✅ Login page (`/login`)
- ✅ Signup page (`/signup`)
- ✅ Dashboard with watchlist integration
- ✅ Reusable AuthForm component
- ✅ Watchlist component with price display
- ✅ AddTickerForm component

## Usage

### For Users
1. Visit `/signup` to create an account
2. Visit `/login` to sign in
3. Access `/dashboard` to view your watchlist
4. Add Moroccan stock tickers (e.g., IAM, BCP, ATW)
5. Remove tickers by clicking the trash icon

### For Developers
- All authentication logic is handled by Supabase
- Watchlist data is stored in the `watchlists` table
- Row Level Security ensures users can only access their own data
- Components are reusable and follow the existing design system

## File Structure

```
apps/web/
├── pages/
│   ├── login.tsx          # Login page
│   ├── signup.tsx         # Signup page
│   └── dashboard.tsx      # Dashboard with watchlist
├── components/
│   ├── AuthForm.tsx       # Reusable auth form
│   ├── Watchlist.tsx      # Watchlist display
│   └── AddTickerForm.tsx  # Add ticker form
├── lib/
│   └── supabase.ts        # Supabase client
└── supabase-setup.sql     # Database setup script
```

## Testing

1. Start the development server: `npm run dev`
2. Visit `http://localhost:3000/signup`
3. Create a test account
4. Add some tickers to your watchlist
5. Test the remove functionality

## Next Steps

- [ ] Add Google OAuth authentication
- [ ] Implement real-time price updates
- [ ] Add price alerts functionality
- [ ] Create mobile app version
- [ ] Add portfolio tracking features 