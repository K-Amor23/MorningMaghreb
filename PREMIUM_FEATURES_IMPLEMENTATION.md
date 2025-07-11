# Premium Features Implementation

## Overview

This document outlines the implementation of the Premium tier landing page and subscription system for Casablanca Insights.

## New Files Created

### 1. Premium Landing Page (`/apps/web/pages/premium.tsx`)
- **Route**: `/premium`
- **Features**:
  - Hero section with "Unlock More with Casablanca Insight Premium"
  - Feature list showcasing 5 key premium features
  - Pricing block with monthly/yearly toggle ($9/month or $90/year)
  - Free vs Premium comparison table
  - FAQ section with expandable questions
  - Upgrade CTA section

### 2. Stripe Checkout API (`/apps/web/pages/api/stripe/checkout.ts`)
- **Endpoint**: `/api/stripe/checkout`
- **Method**: POST
- **Purpose**: Creates Stripe checkout sessions for premium subscriptions
- **Parameters**:
  - `priceId`: Stripe price ID for monthly/yearly plans
  - `successUrl`: Redirect URL after successful payment
  - `cancelUrl`: Redirect URL if payment is cancelled

### 3. Stripe Webhook Handler (`/apps/web/pages/api/stripe/webhook.ts`)
- **Endpoint**: `/api/stripe/webhook`
- **Purpose**: Processes Stripe webhook events
- **Events Handled**:
  - `checkout.session.completed`: Updates user tier to 'pro'
  - `customer.subscription.deleted`: Downgrades user to 'free'
  - `invoice.payment_failed`: Handles failed payments

## Updated Files

### Header Component (`/apps/web/components/Header.tsx`)
- Updated Premium link to point to `/premium` instead of `/premium-features`
- Styled Premium link with yellow color and underline hover effect

## Premium Features

The premium tier includes the following features:

1. **GAAP Financials** - Access to GAAP financials for 100+ companies
2. **AI Summaries & Earnings** - AI-powered earnings recaps and company summaries
3. **Portfolio Statistics** - Advanced portfolio metrics (Sharpe ratio, Monte Carlo analysis)
4. **Smart FX Converter** - Intelligent currency conversion with real-time alerts
5. **Newsletter Customization** - Personalized newsletter with preferred content

## Pricing Structure

- **Monthly**: $9/month
- **Yearly**: $90/year (17% discount)
- **Free Trial**: 7 days, no credit card required

## Database Schema Requirements

The following fields should be added to the `profiles` table:

```sql
ALTER TABLE profiles ADD COLUMN tier VARCHAR(20) DEFAULT 'free';
ALTER TABLE profiles ADD COLUMN stripe_customer_id VARCHAR(255);
ALTER TABLE profiles ADD COLUMN stripe_subscription_id VARCHAR(255);
```

## Environment Variables

Add the following to your `.env.local`:

```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_stripe_webhook_secret
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
```

## Stripe Setup

1. **Create Products and Prices**:
   - Create a "Premium Subscription" product in Stripe
   - Create two prices:
     - Monthly: $9/month
     - Yearly: $90/year

2. **Configure Webhooks**:
   - Set webhook endpoint to: `https://yourdomain.com/api/stripe/webhook`
   - Subscribe to events:
     - `checkout.session.completed`
     - `customer.subscription.deleted`
     - `invoice.payment_failed`

3. **Update Price IDs**:
   - Replace `price_monthly` and `price_yearly` in the premium page with actual Stripe price IDs

## User Flow

1. User visits `/premium`
2. User selects monthly/yearly billing
3. User clicks "Start Free Trial" or "Upgrade to Premium"
4. User is redirected to Stripe checkout
5. After successful payment, user is redirected to `/dashboard?upgraded=true`
6. Webhook updates user's tier to 'pro' in database

## Testing

1. **Local Testing**:
   - Use Stripe test keys
   - Use Stripe CLI to forward webhooks: `stripe listen --forward-to localhost:3000/api/stripe/webhook`

2. **Test Cards**:
   - Success: `4242 4242 4242 4242`
   - Decline: `4000 0000 0000 0002`

## Dependencies Added

- `stripe`: Stripe SDK for Node.js
- `micro`: For handling raw request bodies in webhooks

## Next Steps

1. Set up actual Stripe account and get production keys
2. Configure webhook endpoints in Stripe dashboard
3. Test the complete payment flow
4. Add email notifications for subscription events
5. Implement subscription management in user account settings
6. Add analytics tracking for conversion rates 