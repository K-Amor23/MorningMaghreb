# 🔐 Complete Supabase Auth Implementation Guide

This guide covers the complete implementation of Supabase Auth with user profiles, subscription management, and all supporting features for Casablanca Insights.

## 🏗️ Architecture Overview

```
Supabase Auth → profiles table → Supporting Tables → Frontend Components
     ↓              ↓                ↓                    ↓
auth.users    user metadata    watchlists, alerts    useUser hook
```

## 📋 What's Implemented

### ✅ Core Authentication
- **Email/Password Login & Registration**
- **Google OAuth Integration**
- **JWT Session Management**
- **Password Recovery**
- **Protected Routes**

### ✅ User Profile Management
- **profiles table** - User metadata and preferences
- **Automatic profile creation** on signup
- **Profile updates** with form validation
- **Subscription tier management** (free/pro/admin)

### ✅ Supporting Features
- **watchlists** - User stock watchlists
- **price_alerts** - Price-based notifications
- **newsletter_settings** - Email preferences
- **billing_history** - Stripe integration
- **Row Level Security (RLS)** - Data isolation

## 🗄️ Database Schema

### 1. Profiles Table (Core User Metadata)
```sql
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'pro', 'admin')),
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    preferences JSONB DEFAULT '{}',
    language_preference VARCHAR(10) DEFAULT 'en',
    newsletter_frequency VARCHAR(20) DEFAULT 'weekly',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. Supporting Tables
- **watchlists** - User stock watchlists
- **price_alerts** - Price-based notifications
- **newsletter_settings** - Email preferences
- **billing_history** - Stripe webhook storage

### 3. Automatic Triggers
- **handle_new_user()** - Creates profile on signup
- **handle_user_update()** - Updates profile on auth changes
- **handle_stripe_webhook()** - Updates tier on payment

## 🚀 Setup Instructions

### Step 1: Configure Supabase Project

1. **Create Supabase Project**
   ```bash
   # Go to supabase.com and create new project
   # Note down your project URL and anon key
   ```

2. **Update Environment Variables**
   ```bash
   # apps/web/.env.local
   NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

### Step 2: Run Database Setup

1. **Execute SQL Script**
   ```bash
   # Copy contents of apps/web/supabase-setup.sql
   # Run in Supabase SQL Editor
   ```

2. **Verify Tables Created**
   - `profiles` - User metadata
   - `watchlists` - Stock watchlists
   - `price_alerts` - Price notifications
   - `newsletter_settings` - Email preferences
   - `billing_history` - Stripe data

### Step 3: Configure Authentication

1. **Enable Email Auth**
   - Go to Authentication → Providers
   - Enable Email provider
   - Configure email templates

2. **Enable Google OAuth** (Optional)
   - Go to Authentication → Providers → Google
   - Add Google OAuth credentials
   - Set redirect URL: `https://your-project-id.supabase.co/auth/v1/callback`

### Step 4: Test Implementation

1. **Start Development Server**
   ```bash
   cd apps/web
   npm run dev
   ```

2. **Test Authentication Flow**
   - Visit `/signup` - Create account
   - Visit `/login` - Sign in
   - Visit `/account/settings` - Manage profile
   - Visit `/dashboard` - Protected route

## 🧩 Frontend Implementation

### 1. useUser Hook
```typescript
// apps/web/lib/useUser.ts
import { useUser } from '@/lib/useUser'

function MyComponent() {
  const { user, profile, dashboard, loading, updateProfile, signOut } = useUser()
  
  if (loading) return <div>Loading...</div>
  if (!user) return <div>Please sign in</div>
  
  return (
    <div>
      <h1>Welcome, {profile?.full_name}</h1>
      <p>Tier: {profile?.tier}</p>
      <p>Watchlist Items: {dashboard?.watchlist_count}</p>
    </div>
  )
}
```

### 2. Protected Routes
```typescript
// Any page that requires authentication
export default function ProtectedPage() {
  const { user, loading } = useUser()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.replace('/login')
    }
  }, [user, loading, router])

  if (loading) return <div>Loading...</div>
  if (!user) return null

  return <div>Protected content</div>
}
```

### 3. Profile Management
```typescript
// Update user profile
const { updateProfile } = useUser()

const handleUpdate = async () => {
  await updateProfile({
    full_name: 'John Doe',
    language_preference: 'fr',
    preferences: { theme: 'dark' }
  })
}
```

## 🔒 Security Features

### Row Level Security (RLS)
All tables have RLS policies ensuring users can only access their own data:

```sql
-- Example: Users can only see their own watchlist
CREATE POLICY "Users can view their own watchlist items" ON watchlists
    FOR SELECT USING (auth.uid() = user_id);
```

### Automatic Profile Creation
When a user signs up, a profile is automatically created:

```sql
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

### Subscription Management
Stripe webhooks automatically update user tiers:

```sql
-- When payment succeeds, upgrade to pro
UPDATE profiles SET tier = 'pro' 
WHERE stripe_customer_id = NEW.stripe_customer_id;
```

## 💳 Stripe Integration

### 1. Webhook Setup
```typescript
// pages/api/webhooks/stripe.ts
export default async function handler(req, res) {
  const event = stripe.webhooks.constructEvent(
    req.body,
    req.headers['stripe-signature'],
    process.env.STRIPE_WEBHOOK_SECRET
  )

  if (event.type === 'invoice.payment_succeeded') {
    // Update user tier to 'pro'
    await updateUserTier(event.data.object.customer, 'pro')
  }
}
```

### 2. Database Integration
```sql
-- Insert billing record
INSERT INTO billing_history (
  user_id, stripe_customer_id, amount, status
) VALUES (
  auth.uid(), 'cus_xxx', 29.99, 'succeeded'
);
```

## 📊 User Dashboard Data

The `user_dashboard` view provides aggregated user data:

```sql
CREATE VIEW user_dashboard AS
SELECT 
  p.id,
  p.email,
  p.full_name,
  p.tier,
  COUNT(w.ticker) as watchlist_count,
  COUNT(pa.id) as active_alerts_count
FROM profiles p
LEFT JOIN watchlists w ON p.id = w.user_id
LEFT JOIN price_alerts pa ON p.id = pa.user_id AND pa.is_active = true
GROUP BY p.id, p.email, p.full_name, p.tier;
```

## 🎯 Usage Examples

### Check User Tier
```typescript
import { useProAccess, useAdminAccess } from '@/lib/useUser'

function MyComponent() {
  const isPro = useProAccess()
  const isAdmin = useAdminAccess()
  
  return (
    <div>
      {isPro && <ProFeature />}
      {isAdmin && <AdminPanel />}
    </div>
  )
}
```

### Manage Watchlist
```typescript
// Add to watchlist
const { data, error } = await supabase
  .from('watchlists')
  .insert({ user_id: user.id, ticker: 'IAM' })

// Get user's watchlist
const { data: watchlist } = await supabase
  .from('watchlists')
  .select('*')
  .eq('user_id', user.id)
```

### Update Profile
```typescript
const { updateProfile } = useUser()

await updateProfile({
  full_name: 'New Name',
  language_preference: 'fr',
  preferences: { theme: 'dark' }
})
```

## 🔧 Troubleshooting

### Common Issues

1. **"Supabase client not configured"**
   - Check environment variables
   - Verify Supabase URL and key

2. **"Profile not found"**
   - Run the SQL setup script
   - Check if triggers are created

3. **"RLS policy violation"**
   - Verify user is authenticated
   - Check RLS policies are enabled

4. **"Google OAuth not working"**
   - Verify redirect URLs
   - Check Google Cloud Console settings

### Debug Commands
```bash
# Check Supabase connection
npm run test-auth

# View database logs
# Go to Supabase Dashboard → Logs

# Test RLS policies
# Go to Supabase Dashboard → SQL Editor
```

## 📱 Mobile App Integration

The same Supabase configuration works for the mobile app:

```typescript
// apps/mobile/src/services/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
  },
})
```

## 🚀 Production Deployment

### Environment Variables
```bash
# Production .env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Security Checklist
- [ ] RLS policies enabled on all tables
- [ ] Environment variables set in production
- [ ] Stripe webhooks configured
- [ ] Email templates customized
- [ ] Google OAuth redirect URLs updated

## 📈 Next Steps

1. **Implement Stripe Checkout** for subscription upgrades
2. **Add Email Notifications** for price alerts
3. **Create Admin Dashboard** for user management
4. **Add Analytics** for user behavior tracking
5. **Implement Real-time Updates** with Supabase subscriptions

## 🆘 Support

If you encounter issues:
1. Check the browser console for errors
2. Verify all environment variables are set
3. Ensure database schema is properly created
4. Check Supabase dashboard for any errors
5. Review the troubleshooting section above

---

**🎉 Congratulations!** You now have a complete, production-ready authentication system with user profiles, subscription management, and all supporting features. 