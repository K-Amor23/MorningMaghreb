# Morning Maghreb Deployment Guide

## 🚀 Domain Transition Complete: casablanca-insight → morningmaghreb.com

Your project has been successfully updated to use the new domain `morningmaghreb.com`. Here's your complete deployment checklist:

## 📋 Pre-Deployment Checklist

### 1. Domain Configuration
- [ ] **DNS Setup**: Configure your domain at your domain registrar
  - Point `morningmaghreb.com` to Vercel (frontend)
  - Point `api.morningmaghreb.com` to Railway/Render (backend)
  - Set up email records for `@morningmaghreb.com`

### 2. Environment Variables Update
Update these environment variables in your deployment platforms:

#### Vercel (Frontend)
```env
NEXT_PUBLIC_SITE_URL=https://morningmaghreb.com
NEXT_PUBLIC_API_URL=https://api.morningmaghreb.com
NEXT_PUBLIC_WEBSOCKET_URL=wss://api.morningmaghreb.com/ws
```

#### Railway/Render (Backend)
```env
FRONTEND_URL=https://morningmaghreb.com
FROM_EMAIL=noreply@morningmaghreb.com
ALERT_EMAILS=["admin@morningmaghreb.com"]
```

#### Supabase
- [ ] Update any domain-specific configurations
- [ ] Verify RLS policies work with new domain

#### SendGrid
- [ ] Verify sender email: `noreply@morningmaghreb.com`
- [ ] Update webhook endpoints if needed

## 🛠️ Deployment Steps

### Step 1: Frontend Deployment (Vercel)
```bash
# Deploy to Vercel with new domain
vercel --prod
```

### Step 2: Backend Deployment (Railway/Render)
```bash
# Deploy backend with updated configuration
# Your backend should now use morningmaghreb-api service name
```

### Step 3: Database Verification (Supabase)
- [ ] Test database connections
- [ ] Verify all tables and functions work
- [ ] Check RLS policies

### Step 4: Email Service (SendGrid)
- [ ] Test email sending with new domain
- [ ] Verify webhook configurations

## 🔧 Configuration Updates Made

### Backend Changes
- ✅ CORS origins updated to `morningmaghreb.com`
- ✅ Service names updated in `render.yaml`
- ✅ Email addresses updated to `@morningmaghreb.com`
- ✅ User agent updated to `Morning-Maghreb/1.0`

### Frontend Changes
- ✅ Package name updated to `morningmaghreb`
- ✅ Shared package imports updated
- ✅ Service worker cache name updated
- ✅ Admin email updated

### Mobile App Changes
- ✅ Package dependencies updated
- ✅ Storage name updated
- ✅ Redirect URLs updated
- ✅ Import statements updated

### Infrastructure Changes
- ✅ Deployment scripts updated
- ✅ Monitoring configurations updated
- ✅ Alert email addresses updated
- ✅ Webhook configurations updated

## 🌐 Domain Setup Instructions

### 1. Vercel Domain Configuration
1. Go to your Vercel dashboard
2. Select your project
3. Go to Settings → Domains
4. Add `morningmaghreb.com`
5. Configure DNS records as instructed

### 2. Railway/Render Domain Configuration
1. Go to your Railway/Render dashboard
2. Select your backend service
3. Add custom domain: `api.morningmaghreb.com`
4. Configure SSL certificate

### 3. Email Domain Setup
1. Configure DNS records for email:
   ```
   MX @ mail.morningmaghreb.com
   TXT @ v=spf1 include:_spf.google.com ~all
   ```
2. Set up SendGrid domain authentication

## 🔍 Post-Deployment Verification

### 1. Frontend Tests
- [ ] Homepage loads correctly
- [ ] All API calls work
- [ ] Authentication flows work
- [ ] WebSocket connections work

### 2. Backend Tests
- [ ] Health check endpoint: `https://api.morningmaghreb.com/health`
- [ ] All API endpoints respond correctly
- [ ] CORS headers are properly set
- [ ] Database connections work

### 3. Email Tests
- [ ] SendGrid integration works
- [ ] Newsletter emails send correctly
- [ ] Alert emails work

### 4. Mobile App Tests
- [ ] App builds with new package names
- [ ] API calls work with new domain
- [ ] Authentication flows work

## 🚨 Important Notes

### Breaking Changes
- All import statements using `@casablanca-insight/shared` now use `@morningmaghreb/shared`
- Email addresses changed from `@casablanca-insight.com` to `@morningmaghreb.com`
- Service names in deployment platforms updated

### Environment Variables
Make sure to update these in all your deployment platforms:
- `NEXT_PUBLIC_SITE_URL`
- `NEXT_PUBLIC_API_URL`
- `FROM_EMAIL`
- `ALERT_EMAILS`

### DNS Configuration
Your DNS should point:
- `morningmaghreb.com` → Vercel
- `api.morningmaghreb.com` → Railway/Render
- `www.morningmaghreb.com` → Vercel (optional)

## 📞 Support

If you encounter any issues during deployment:
1. Check the deployment logs in Vercel/Railway/Render
2. Verify DNS propagation (can take up to 48 hours)
3. Test endpoints individually
4. Check environment variables are correctly set

## 🎉 Success Criteria

Your deployment is successful when:
- ✅ `https://morningmaghreb.com` loads your frontend
- ✅ `https://api.morningmaghreb.com/health` returns 200 OK
- ✅ All email notifications work with new domain
- ✅ Mobile app can connect to new API endpoints
- ✅ No console errors related to CORS or domain issues

---

**Next Steps:**
1. Configure your domain DNS settings
2. Deploy to your platforms with updated environment variables
3. Test all functionality
4. Update any external integrations (if any)
5. Monitor for any issues in the first 24-48 hours

Good luck with your new domain! 🚀 