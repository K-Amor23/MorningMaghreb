# Premium Features Implementation

## Overview

This document describes the implementation of clickable premium feature cards and development bypass for access control in the Casablanca Insight application.

## Features Implemented

### 1. Clickable Premium Feature Cards

Each premium feature card on the `/premium` page is now wrapped in a `<Link>` component that routes to its respective feature page:

- **GAAP Financials** → `/company/IAM` (example company page with GAAP data)
- **AI Summaries & Earnings** → `/company/ATW` (example company page with AI summaries)
- **Portfolio Statistics** → `/portfolio` (advanced portfolio analytics)
- **Smart FX Converter** → `/convert` (currency converter with remittance advice)
- **Newsletter Customization** → `/dashboard` (dashboard with newsletter settings)

#### Implementation Details

```typescript
// Updated features array in /pages/premium.tsx
const features = [
  {
    icon: DocumentTextIcon,
    title: 'GAAP Financials',
    description: 'Access to GAAP financials for 100+ companies with detailed analysis',
    href: '/company/IAM' // Clickable link
  },
  // ... other features
]

// Updated JSX with Link wrapper
<Link 
  href={feature.href}
  className="text-center p-6 rounded-lg bg-gray-50 dark:bg-dark-bg hover:bg-gray-100 dark:hover:bg-dark-hover transition-colors cursor-pointer group"
>
  {/* Feature content */}
  <div className="mt-4 text-sm text-casablanca-blue group-hover:text-blue-600 transition-colors">
    Try it now →
  </div>
</Link>
```

#### Benefits

- **Fast Testing**: Developers can quickly test each feature from the premium page
- **Design Iteration**: Easy to iterate on feature designs and user flows
- **User Experience**: Users can preview features before upgrading
- **Development Workflow**: Streamlined testing and development process

### 2. Dev Bypass for Access Control

When `NEXT_PUBLIC_ENV=dev` is set in `.env.local`, any authenticated user is treated as having `tier: 'pro'` in the access control logic.

#### Implementation Details

```typescript
// Updated useProAccess hook in /lib/useUser.ts
export function useProAccess() {
  const { profile } = useUser()
  // Dev bypass: treat any user as pro when NEXT_PUBLIC_ENV=dev
  const isDev = process.env.NEXT_PUBLIC_ENV === 'dev'
  return profile?.tier === 'pro' || profile?.tier === 'admin' || isDev
}
```

#### Usage

1. **Development Environment**:
   ```env
   NEXT_PUBLIC_ENV=dev
   ```

2. **Production Environment**:
   ```env
   NEXT_PUBLIC_ENV=production
   ```

#### Protected Pages

The following pages now have proper access control with dev bypass:

- `/portfolio` - Advanced portfolio analytics
- `/convert` - Smart FX converter
- `/advanced-features` - Professional investment tools
- `/premium-features` - API keys, data exports, etc.

#### Access Control Flow

```typescript
// Example from /pages/portfolio.tsx
export default function Portfolio() {
  const { user, profile, loading } = useUser()
  const isPro = useProAccess()

  // Check access control
  if (loading) {
    return <LoadingSpinner />
  }

  if (!isPro) {
    return <PremiumRequiredPrompt />
  }

  // Render premium content
  return <PortfolioContent />
}
```

### 3. Production Behavior (No Change)

In production environments:

- Only authenticated users with `tier: 'pro'` (set via Stripe webhook or admin override) can access premium routes
- Unauthorized users see an upgrade prompt with a link to `/premium`
- Access control is enforced at the page level with consistent UI

## Files Modified

### Core Files
- `apps/web/lib/useUser.ts` - Added dev bypass logic
- `apps/web/pages/premium.tsx` - Made feature cards clickable
- `apps/web/pages/portfolio.tsx` - Added access control
- `apps/web/pages/advanced-features.tsx` - Added access control
- `apps/web/pages/premium-features.tsx` - Updated to use new useUser hook

### Configuration
- `env.template` - Documented dev bypass environment variable

## Development Workflow

### For Developers

1. **Set up dev environment**:
   ```bash
   # In .env.local
   NEXT_PUBLIC_ENV=dev
   ```

2. **Test premium features**:
   - Visit `/premium`
   - Click any feature card to test the feature
   - All premium pages will be accessible regardless of user tier

3. **Test production behavior**:
   ```bash
   # In .env.local
   NEXT_PUBLIC_ENV=production
   ```
   - Premium pages will require actual pro tier

### For Users

1. **Free Tier**: Can browse premium features but get upgrade prompts
2. **Pro Tier**: Full access to all premium features
3. **Admin Tier**: Access to institutional features (API keys, webhooks)

## Security Considerations

- Dev bypass only works when `NEXT_PUBLIC_ENV=dev` is explicitly set
- Production deployments should never have this environment variable set to "dev"
- Access control is enforced at both client and server levels
- Stripe webhooks properly update user tiers in production

## Future Enhancements

1. **Feature Previews**: Add limited preview functionality for free users
2. **Trial Access**: Implement time-limited trial access to premium features
3. **Usage Analytics**: Track feature usage to inform product decisions
4. **A/B Testing**: Test different premium feature presentations

## Testing

### Manual Testing Checklist

- [ ] Premium page feature cards are clickable
- [ ] Dev bypass works when `NEXT_PUBLIC_ENV=dev`
- [ ] Access control works when `NEXT_PUBLIC_ENV=production`
- [ ] Upgrade prompts appear for unauthorized users
- [ ] All premium pages load correctly for authorized users
- [ ] Loading states work properly
- [ ] Error handling works for edge cases

### Automated Testing

Consider adding tests for:
- Access control logic
- Dev bypass functionality
- Premium page routing
- User tier validation 