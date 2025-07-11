# Supabase Setup Guide for Casablanca Insights

## 🚀 Quick Setup

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `casablanca-insights`
   - **Database Password**: Choose a strong password
   - **Region**: Choose closest to you
5. Click "Create new project"

### 2. Get Your Project Credentials

1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (starts with `https://`)
   - **anon public** key (starts with `eyJ`)

### 3. Update Environment File

Edit `apps/web/.env.local` and add your credentials:

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4. Set Up Database Schema

1. In your Supabase dashboard, go to **SQL Editor**
2. Copy and paste the contents of `apps/web/supabase-setup.sql`
3. Click "Run" to create:
   - `watchlists` table
   - `price_alerts` table
   - Row Level Security (RLS) policies
   - Sample data

### 5. Configure Google OAuth (Optional)

1. In Supabase Dashboard → **Authentication** → **Providers** → **Google**
2. Enable Google provider
3. Add your Google OAuth credentials:
   - **Client ID**: From Google Cloud Console
   - **Client Secret**: From Google Cloud Console
4. Set redirect URL to: `https://your-project-id.supabase.co/auth/v1/callback`

### 6. Test the Application

1. Restart your development server: `npm run dev`
2. Visit http://localhost:3000/signup
3. Test both email/password and Google OAuth
4. Add stocks to your watchlist
5. Create price alerts

## 🔧 Google OAuth Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API

### 2. Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Choose "Web application"
4. Add authorized redirect URIs:
   - `https://your-project-id.supabase.co/auth/v1/callback`
   - `http://localhost:3000/auth/callback` (for development)

### 3. Get Credentials

Copy the **Client ID** and **Client Secret** to Supabase.

## 📊 Market Data API (Optional)

### Alpha Vantage Setup

1. Go to [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Get a free API key
3. Add to `.env.local`:
   ```bash
   NEXT_PUBLIC_ALPHA_VANTAGE_API_KEY=your_api_key_here
   ```

**Note**: Without this key, the app uses realistic mock data with live updates.

## 🗄️ Database Schema

The setup script creates these tables:

### watchlists
- `id`: UUID primary key
- `user_id`: References auth.users
- `ticker`: Stock symbol
- `created_at`: Timestamp

### price_alerts
- `id`: UUID primary key
- `user_id`: References auth.users
- `ticker`: Stock symbol
- `alert_type`: 'above' or 'below'
- `price_threshold`: Decimal price
- `is_active`: Boolean
- `created_at`: Timestamp
- `triggered_at`: Optional timestamp

## 🔒 Security Features

- **Row Level Security (RLS)**: Users can only access their own data
- **Authentication**: Email/password and Google OAuth
- **Authorization**: Proper user isolation
- **Input Validation**: Server-side validation

## 🚨 Troubleshooting

### Common Issues

1. **"Invalid URL" Error**
   - Make sure Supabase URL is correct
   - Check for extra spaces in .env.local

2. **Authentication Not Working**
   - Verify Supabase credentials
   - Check browser console for errors
   - Ensure RLS policies are enabled

3. **Database Errors**
   - Run the SQL setup script again
   - Check Supabase logs for errors

4. **Google OAuth Issues**
   - Verify redirect URIs match exactly
   - Check Google Cloud Console settings
   - Ensure Google+ API is enabled

### Environment Variables Checklist

```bash
# Required for basic functionality
NEXT_PUBLIC_SUPABASE_URL=✅
NEXT_PUBLIC_SUPABASE_ANON_KEY=✅

# Optional for enhanced features
NEXT_PUBLIC_ALPHA_VANTAGE_API_KEY=❓
```

## 🎯 Next Steps

1. **Configure Supabase**: Follow steps 1-4 above
2. **Test Authentication**: Create accounts and test login
3. **Add Google OAuth**: Follow Google OAuth setup
4. **Get Market Data API**: Optional for real data
5. **Deploy**: Ready for production

## 📱 Mobile App

The mobile app uses the same Supabase configuration:
- Update `apps/mobile/.env.local` with the same credentials
- Use `EXPO_PUBLIC_` prefix instead of `NEXT_PUBLIC_`

## 🆘 Support

If you encounter issues:
1. Check the browser console for errors
2. Verify all environment variables are set
3. Ensure database schema is properly created
4. Check Supabase dashboard for any errors 