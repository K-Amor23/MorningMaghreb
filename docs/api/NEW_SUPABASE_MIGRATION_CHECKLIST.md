# 🚀 New Supabase Migration Checklist

## ✅ **Configuration Updated**

The following files have been updated to use the new Supabase instance (`supabase-sky-garden`):

- ✅ `vercel.json` - Updated URL
- ✅ `apps/web/vercel.json` - Updated URL  
- ✅ `scripts/MASTER_MIGRATION_GUIDE.md` - Updated project reference
- ✅ `scripts/manual_supabase_setup.md` - Updated project reference

## 🔑 **API Keys Required**

You need to update the API keys in the following files:

### **1. Update vercel.json files**
Replace the placeholder keys with your actual API keys:

```json
{
  "NEXT_PUBLIC_SUPABASE_URL": "https://supabase-sky-garden.supabase.co",
  "NEXT_PUBLIC_SUPABASE_ANON_KEY": "YOUR_ACTUAL_ANON_KEY",
  "SUPABASE_SERVICE_ROLE_KEY": "YOUR_ACTUAL_SERVICE_ROLE_KEY"
}
```

### **2. Set Environment Variables**
For local development, set these environment variables:

```bash
export NEXT_PUBLIC_SUPABASE_URL="https://supabase-sky-garden.supabase.co"
export NEXT_PUBLIC_SUPABASE_ANON_KEY="your_actual_anon_key"
export SUPABASE_SERVICE_ROLE_KEY="your_actual_service_role_key"
```

### **3. Mobile App Configuration**
For the mobile app, set these environment variables:

```bash
export EXPO_PUBLIC_SUPABASE_URL="https://supabase-sky-garden.supabase.co"
export EXPO_PUBLIC_SUPABASE_ANON_KEY="your_actual_anon_key"
```

## 🗄️ **Database Migration Steps**

### **Step 1: Access New Supabase Dashboard**
1. Go to [https://supabase.com](https://supabase.com)
2. Sign in to your account
3. Select your project: `supabase-sky-garden`
4. Navigate to **SQL Editor**

### **Step 2: Run Master Schema Migration**
1. Copy the entire content from `database/MASTER_SCHEMA_MIGRATION.sql`
2. Paste it into the SQL Editor
3. Click **Run** to execute the complete schema

### **Step 3: Verify Migration**
After running the migration, you should see:
- ✅ **Success message**: "Master schema migration completed successfully!"
- ✅ **All tables created** in the Table Editor
- ✅ **All indexes created** for performance

## 🔐 **Authentication & Newsletter Verification**

### **Authentication Features**
All authentication features are configured to use the new Supabase instance:

- ✅ **User Registration** - Uses `supabase.auth.signUp()`
- ✅ **User Login** - Uses `supabase.auth.signInWithPassword()`
- ✅ **Password Reset** - Uses `supabase.auth.resetPasswordForEmail()`
- ✅ **Profile Updates** - Uses `supabase.auth.updateUser()`
- ✅ **Session Management** - Uses `supabase.auth.getSession()`
- ✅ **Logout** - Uses `supabase.auth.signOut()`

### **Newsletter Signup**
The newsletter signup system is configured to use the new Supabase instance:

- ✅ **API Endpoint** - `/api/newsletter/signup` uses new Supabase
- ✅ **Database Table** - `newsletter_subscribers` in new instance
- ✅ **Email Validation** - Proper email validation
- ✅ **Duplicate Prevention** - Checks for existing subscribers

### **Mobile App Authentication**
The mobile app authentication is configured correctly:

- ✅ **Supabase Client** - Uses environment variables
- ✅ **Biometric Auth** - Integrated with local authentication
- ✅ **Secure Storage** - Uses Expo SecureStore
- ✅ **Session Persistence** - Proper session management

## 🧪 **Testing Checklist**

### **Test Authentication**
- [ ] User registration works
- [ ] User login works
- [ ] Password reset works
- [ ] Profile updates work
- [ ] Logout works
- [ ] Session persistence works

### **Test Newsletter Signup**
- [ ] Newsletter signup form works
- [ ] Email validation works
- [ ] Duplicate email prevention works
- [ ] Success/error messages display correctly

### **Test Mobile App**
- [ ] Mobile authentication works
- [ ] Biometric authentication works (if available)
- [ ] Session persistence works
- [ ] Profile management works

### **Test Database Features**
- [ ] User profiles are created automatically
- [ ] Watchlists work correctly
- [ ] Price alerts work correctly
- [ ] Sentiment voting works
- [ ] Paper trading works
- [ ] Portfolio management works

## 🔧 **Verification Script**

Run the verification script to check your configuration:

```bash
python3 scripts/verify_new_supabase_config.py
```

This script will:
- ✅ Check all configuration files
- ✅ Verify environment variables
- ✅ Test Supabase connections
- ✅ Generate fix scripts if needed

## 🚨 **Common Issues & Solutions**

### **Issue: "API key not found"**
**Solution**: Update the API keys in `vercel.json` and environment variables

### **Issue: "Database connection failed"**
**Solution**: 
1. Verify the new Supabase instance is active
2. Check API keys are correct
3. Ensure the schema migration has been run

### **Issue: "Authentication not working"**
**Solution**:
1. Check Supabase Auth settings in dashboard
2. Verify redirect URLs are configured
3. Check email templates are set up

### **Issue: "Newsletter signup failing"**
**Solution**:
1. Verify `newsletter_subscribers` table exists
2. Check RLS policies are configured
3. Test the API endpoint directly

## 📊 **Migration Status**

### **✅ Completed**
- [x] Configuration files updated
- [x] Migration guides updated
- [x] Verification script created
- [x] All auth endpoints configured
- [x] Newsletter signup configured

### **⏳ Pending**
- [ ] Update API keys in vercel.json
- [ ] Set environment variables
- [ ] Run master schema migration
- [ ] Test all functionality
- [ ] Deploy to production

## 🎯 **Next Steps**

1. **Get API Keys**: Get the anon and service role keys from your new Supabase instance
2. **Update Configuration**: Replace placeholder keys with actual keys
3. **Run Migration**: Execute the master schema migration
4. **Test Everything**: Run comprehensive tests
5. **Deploy**: Deploy the updated configuration

## 📞 **Support**

If you encounter issues:

1. **Check the verification script**: `python3 scripts/verify_new_supabase_config.py`
2. **Review the migration guide**: `scripts/MASTER_MIGRATION_GUIDE.md`
3. **Check Supabase logs**: Look for errors in the Supabase dashboard
4. **Test connections**: Use the verification script to test connections

---

**🎉 Your authentication and newsletter signups are now configured to use the new Supabase instance!** 