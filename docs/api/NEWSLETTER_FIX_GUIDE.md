# 🔧 Newsletter Signup Fix Guide

## 🚨 Issue Identified

The newsletter signup is failing because your Supabase credentials in `vercel.json` are still placeholders instead of real credentials.

### Current Problem:
```json
{
  "NEXT_PUBLIC_SUPABASE_ANON_KEY": "YOUR_NEW_ANON_KEY_HERE",
  "SUPABASE_SERVICE_ROLE_KEY": "YOUR_NEW_SERVICE_ROLE_KEY_HERE"
}
```

## 🔧 Step-by-Step Fix

### Step 1: Get Your Supabase Credentials

1. **Go to Supabase Dashboard**
   - Visit: https://supabase.com/dashboard
   - Sign in to your account

2. **Select Your Project**
   - Choose your Morning Maghreb project
   - If you don't see it, you may need to create a new project

3. **Get API Credentials**
   - Go to **Settings** → **API**
   - Copy these values:
     - **Project URL** (e.g., `https://your-project-id.supabase.co`)
     - **anon/public key** (starts with `eyJ...`)
     - **service_role key** (starts with `eyJ...`)

### Step 2: Update Vercel Configuration

1. **Edit `apps/web/vercel.json`**
   ```json
   {
     "env": {
       "NEXT_PUBLIC_SUPABASE_URL": "https://your-project-id.supabase.co",
       "NEXT_PUBLIC_SUPABASE_ANON_KEY": "your-actual-anon-key-here",
       "SUPABASE_SERVICE_ROLE_KEY": "your-actual-service-role-key-here"
     }
   }
   ```

2. **Replace the placeholder values** with your actual credentials

### Step 3: Deploy the Changes

```bash
# Commit the changes
git add apps/web/vercel.json
git commit -m "Update Supabase credentials for newsletter"

# Push to GitHub
git push origin main

# Deploy to Vercel
cd apps/web
npx vercel --prod
```

### Step 4: Test the Newsletter

1. **Visit your site**: https://morningmaghreb.com
2. **Try signing up** for the newsletter
3. **Check if it works** now

## 🔍 Troubleshooting

### If you get "Database table missing" error:

Run the database setup script:
```bash
python scripts/deploy_master_pipeline_tables.py
```

### If you get "Supabase not configured" error:

1. Check that your environment variables are set correctly
2. Make sure you're using the correct project URL
3. Verify the API keys are copied correctly

### If you get "Email already subscribed" error:

This is actually good - it means the connection is working! The email is already in the database.

## 📊 Verification Steps

### Check Current Status:
```bash
# Run the diagnostic script
python3 scripts/fix_supabase_newsletter.py
```

### Test the API directly:
```bash
curl -X POST https://morningmaghreb.com/api/newsletter/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

## 🎯 Expected Results

After fixing the credentials:

✅ **Newsletter signup works**
✅ **No more "Failed to subscribe" errors**
✅ **Emails are stored in Supabase database**
✅ **Proper error messages for duplicate emails**

## 🔗 Helpful Links

- **Supabase Dashboard**: https://supabase.com/dashboard
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Your Site**: https://morningmaghreb.com
- **GitHub Repository**: https://github.com/K-Amor23/MorningMaghreb

## 🚀 Quick Fix Script

Run this to get step-by-step guidance:
```bash
python3 scripts/fix_supabase_newsletter.py
```

---

**🎉 Once you update the Supabase credentials, the newsletter signup will work perfectly!** 