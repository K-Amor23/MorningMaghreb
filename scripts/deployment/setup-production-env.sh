#!/bin/bash

# 🚀 Production Environment Setup Script
# This script helps set up all production environment variables and services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to prompt for input with default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    
    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " input
        input=${input:-$default}
    else
        read -p "$prompt: " input
    fi
    
    eval "$var_name='$input'"
}

# Function to generate random string
generate_random_string() {
    local length=${1:-32}
    openssl rand -base64 $length | tr -d "=+/" | cut -c1-$length
}

# Function to setup Supabase
setup_supabase() {
    print_status "Setting up Supabase..."
    
    echo ""
    echo "📋 Supabase Setup Instructions:"
    echo "1. Go to https://supabase.com"
    echo "2. Create a new project"
    echo "3. Note the URL and API keys"
    echo ""
    
    prompt_with_default "Enter your Supabase URL" "" SUPABASE_URL
    prompt_with_default "Enter your Supabase Anon Key" "" SUPABASE_ANON_KEY
    prompt_with_default "Enter your Supabase Service Role Key" "" SUPABASE_SERVICE_ROLE_KEY
    
    # Generate database URL
    DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.${SUPABASE_URL#https://}.supabase.co:5432/postgres"
    
    print_success "Supabase configuration captured"
}

# Function to setup OpenAI
setup_openai() {
    print_status "Setting up OpenAI..."
    
    echo ""
    echo "📋 OpenAI Setup Instructions:"
    echo "1. Go to https://platform.openai.com"
    echo "2. Create an API key"
    echo "3. Copy the key"
    echo ""
    
    prompt_with_default "Enter your OpenAI API Key" "" OPENAI_API_KEY
    
    print_success "OpenAI configuration captured"
}

# Function to setup SendGrid
setup_sendgrid() {
    print_status "Setting up SendGrid..."
    
    echo ""
    echo "📋 SendGrid Setup Instructions:"
    echo "1. Go to https://sendgrid.com"
    echo "2. Create a free account"
    echo "3. Create an API key with Mail Send permissions"
    echo "4. Verify your sender email"
    echo ""
    
    prompt_with_default "Enter your SendGrid API Key" "" SENDGRID_API_KEY
    prompt_with_default "Enter your sender email" "noreply@morningmaghreb.com" FROM_EMAIL
    
    print_success "SendGrid configuration captured"
}

# Function to setup Stripe
setup_stripe() {
    print_status "Setting up Stripe..."
    
    echo ""
    echo "📋 Stripe Setup Instructions:"
    echo "1. Go to https://stripe.com"
    echo "2. Create an account"
    echo "3. Get your API keys from the dashboard"
    echo "4. Set up webhook endpoints"
    echo ""
    
    prompt_with_default "Enter your Stripe Secret Key" "" STRIPE_SECRET_KEY
    prompt_with_default "Enter your Stripe Publishable Key" "" STRIPE_PUBLISHABLE_KEY
    prompt_with_default "Enter your Stripe Webhook Secret" "" STRIPE_WEBHOOK_SECRET
    
    print_success "Stripe configuration captured"
}

# Function to setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring services..."
    
    echo ""
    echo "📋 Monitoring Setup Instructions:"
    echo "1. Go to https://sentry.io for error tracking"
    echo "2. Go to https://uptimerobot.com for uptime monitoring"
    echo "3. Create accounts and get API keys"
    echo ""
    
    prompt_with_default "Enter your Sentry DSN (optional)" "" SENTRY_DSN
    prompt_with_default "Enter your Uptime Robot API Key (optional)" "" UPTIME_ROBOT_API_KEY
    
    print_success "Monitoring configuration captured"
}

# Function to setup custom domain
setup_domain() {
    print_status "Setting up custom domain..."
    
    echo ""
    echo "📋 Custom Domain Setup Instructions:"
    echo "1. Purchase a domain (e.g., morningmaghreb.com)"
    echo "2. Configure DNS settings"
    echo "3. Add domain to Vercel and Render"
    echo ""
    
    prompt_with_default "Enter your custom domain (optional)" "" CUSTOM_DOMAIN
    
    if [ -n "$CUSTOM_DOMAIN" ]; then
        FRONTEND_URL="https://$CUSTOM_DOMAIN"
        BACKEND_URL="https://api.$CUSTOM_DOMAIN"
    else
        FRONTEND_URL="https://morningmaghreb.com"
BACKEND_URL="https://morningmaghreb-api.onrender.com"
    fi
    
    print_success "Domain configuration captured"
}

# Function to generate environment file
generate_env_file() {
    print_status "Generating environment files..."
    
    # Generate JWT secret
    JWT_SECRET=$(generate_random_string 32)
    
    # Create .env.production
    cat > .env.production << EOF
# Production Environment Variables for Casablanca Insights

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=$SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY

# OpenAI Configuration
OPENAI_API_KEY=$OPENAI_API_KEY

# Stripe Configuration
STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=$STRIPE_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET=$STRIPE_WEBHOOK_SECRET

# SendGrid Configuration
SENDGRID_API_KEY=$SENDGRID_API_KEY
FROM_EMAIL=$FROM_EMAIL

# Production Configuration
NEXT_PUBLIC_ENV=production
NEXT_PUBLIC_API_URL=$BACKEND_URL
NEXT_PUBLIC_SITE_URL=$FRONTEND_URL

# Database Configuration
DATABASE_URL=$DATABASE_URL

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379

# JWT Configuration
JWT_SECRET=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# Monitoring Configuration
SENTRY_DSN=$SENTRY_DSN
UPTIME_ROBOT_API_KEY=$UPTIME_ROBOT_API_KEY

# Feature Flags
NEXT_PUBLIC_PREMIUM_ENFORCEMENT=true
NEXT_PUBLIC_ENABLE_PREMIUM_FEATURES=true
NEXT_PUBLIC_ENABLE_PAPER_TRADING=true
NEXT_PUBLIC_ENABLE_SENTIMENT_VOTING=true
NEXT_PUBLIC_ENABLE_ADVANCED_CHARTS=true
NEXT_PUBLIC_ENABLE_REAL_TIME_DATA=true
EOF

    # Create .env.local for local development
    cat > .env.local << EOF
# Local Development Environment Variables

# Copy from .env.production and modify as needed
# Use this file for local development

NEXT_PUBLIC_ENV=development
NEXT_PUBLIC_PREMIUM_ENFORCEMENT=false
EOF

    print_success "Environment files generated"
}

# Function to create deployment checklist
create_deployment_checklist() {
    print_status "Creating deployment checklist..."
    
    cat > DEPLOYMENT_CHECKLIST.md << EOF
# 🚀 Production Deployment Checklist

## ✅ Pre-Deployment Checklist

### Environment Variables
- [ ] Supabase URL and keys configured
- [ ] OpenAI API key set
- [ ] SendGrid API key configured
- [ ] Stripe keys configured
- [ ] Custom domain configured (optional)
- [ ] Monitoring services configured

### Services Setup
- [ ] Supabase project created and configured
- [ ] SendGrid account created and verified
- [ ] Stripe account created and configured
- [ ] Vercel account created
- [ ] Render account created
- [ ] Custom domain purchased (optional)

### Database Setup
- [ ] Run database migrations
- [ ] Set up Row Level Security (RLS)
- [ ] Configure database backups
- [ ] Test database connectivity

## 🚀 Deployment Steps

### 1. Backend Deployment (Render)
- [ ] Create new web service on Render
- [ ] Connect GitHub repository
- [ ] Set environment variables
- [ ] Deploy and test

### 2. Frontend Deployment (Vercel)
- [ ] Import repository to Vercel
- [ ] Set environment variables
- [ ] Deploy and test
- [ ] Configure custom domain (optional)

### 3. Email Service Setup
- [ ] Configure SendGrid templates
- [ ] Test email sending
- [ ] Set up email tracking

### 4. Monitoring Setup
- [ ] Configure Uptime Robot monitors
- [ ] Set up Sentry error tracking
- [ ] Configure alerts

## 🧪 Post-Deployment Testing

### Health Checks
- [ ] Frontend loads correctly
- [ ] Backend API responds
- [ ] Database connections work
- [ ] Email service functions

### Feature Testing
- [ ] User authentication works
- [ ] Paper trading functions
- [ ] Newsletter signup works
- [ ] Sentiment voting works
- [ ] Mobile app functions

### Performance Testing
- [ ] Page load times < 3 seconds
- [ ] API response times < 200ms
- [ ] Database query performance
- [ ] Mobile responsiveness

## 📊 Monitoring & Maintenance

### Daily Monitoring
- [ ] Check uptime monitors
- [ ] Review error logs
- [ ] Monitor performance metrics
- [ ] Check email delivery rates

### Weekly Tasks
- [ ] Review user feedback
- [ ] Update dependencies
- [ ] Backup database
- [ ] Review security logs

### Monthly Tasks
- [ ] Performance optimization
- [ ] Security audit
- [ ] Feature planning
- [ ] User analytics review

## 🚨 Emergency Procedures

### Service Outages
- [ ] Check status pages
- [ ] Review error logs
- [ ] Contact service providers
- [ ] Communicate with users

### Data Issues
- [ ] Verify data integrity
- [ ] Check backup status
- [ ] Restore if necessary
- [ ] Investigate root cause

## 📞 Contact Information

### Service Providers
- **Vercel**: https://vercel.com/support
- **Render**: https://render.com/docs/help
- **Supabase**: https://supabase.com/support
- **SendGrid**: https://support.sendgrid.com
- **Stripe**: https://support.stripe.com

### Emergency Contacts
- **Developer**: [Your Contact Info]
- **DevOps**: [DevOps Contact Info]
- **Business**: [Business Contact Info]

---

**Last Updated**: $(date)
**Status**: Ready for Production Deployment
EOF

    print_success "Deployment checklist created"
}

# Function to create GitHub secrets guide
create_github_secrets_guide() {
    print_status "Creating GitHub secrets guide..."
    
    cat > GITHUB_SECRETS_GUIDE.md << EOF
# 🔐 GitHub Secrets Setup Guide

## Required Secrets

Add these secrets to your GitHub repository (Settings > Secrets and variables > Actions):

### Vercel Secrets
\`\`\`
VERCEL_TOKEN=your_vercel_token
VERCEL_ORG_ID=your_vercel_org_id
VERCEL_PROJECT_ID=your_vercel_project_id
\`\`\`

### Render Secrets
\`\`\`
RENDER_TOKEN=your_render_token
RENDER_SERVICE_ID=your_render_service_id
\`\`\`

### Application Secrets
\`\`\`
DATABASE_URL=$DATABASE_URL
SUPABASE_URL=$SUPABASE_URL
SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY
OPENAI_API_KEY=$OPENAI_API_KEY
SENDGRID_API_KEY=$SENDGRID_API_KEY
STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET=$STRIPE_WEBHOOK_SECRET
JWT_SECRET=$JWT_SECRET
\`\`\`

### Monitoring Secrets
\`\`\`
SENTRY_DSN=$SENTRY_DSN
UPTIME_ROBOT_API_KEY=$UPTIME_ROBOT_API_KEY
SLACK_WEBHOOK_URL=your_slack_webhook_url
\`\`\`

### Deployment URLs
\`\`\`
FRONTEND_URL=$FRONTEND_URL
BACKEND_URL=$BACKEND_URL
\`\`\`

## How to Get These Values

### Vercel
1. Install Vercel CLI: \`npm i -g vercel\`
2. Login: \`vercel login\`
3. Get token: \`vercel whoami\`
4. Get project info: \`vercel projects\`

### Render
1. Go to Render dashboard
2. Navigate to your service
3. Copy the service ID from the URL
4. Generate API token in account settings

### Other Services
- **Supabase**: From your project settings
- **OpenAI**: From your API keys page
- **SendGrid**: From your API keys page
- **Stripe**: From your dashboard
- **Sentry**: From your project settings
- **Uptime Robot**: From your API settings

## Security Notes

- Never commit secrets to your repository
- Use environment-specific secrets
- Rotate secrets regularly
- Monitor secret usage
- Use least privilege principle

---

**Generated**: $(date)
EOF

    print_success "GitHub secrets guide created"
}

# Main function
main() {
    echo "🚀 Casablanca Insights Production Environment Setup"
    echo "=================================================="
    echo ""
    
    # Setup all services
    setup_supabase
    setup_openai
    setup_sendgrid
    setup_stripe
    setup_monitoring
    setup_domain
    
    # Generate files
    generate_env_file
    create_deployment_checklist
    create_github_secrets_guide
    
    echo ""
    print_success "Production environment setup completed!"
    echo ""
    echo "📁 Generated files:"
    echo "  - .env.production (Production environment variables)"
    echo "  - .env.local (Local development variables)"
    echo "  - DEPLOYMENT_CHECKLIST.md (Deployment checklist)"
    echo "  - GITHUB_SECRETS_GUIDE.md (GitHub secrets guide)"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Review and update the generated files"
    echo "2. Set up your services (Supabase, SendGrid, etc.)"
    echo "3. Add secrets to GitHub repository"
    echo "4. Run the deployment script: ./scripts/deploy.sh"
    echo ""
    echo "📚 Documentation:"
    echo "  - DEPLOYMENT_GUIDE.md (Comprehensive deployment guide)"
    echo "  - DEPLOYMENT_CHECKLIST.md (Step-by-step checklist)"
    echo ""
}

# Run main function
main "$@" 