# Feature Flags System

This document describes the feature flags system implemented in Casablanca Insight to control premium enforcement and feature toggles.

## Overview

The feature flags system allows you to:
- Disable premium enforcement globally
- Control individual feature access
- Enable development bypasses
- Manage usage and project limits
- Debug feature flag status in development

## Configuration

### Environment Variables

Add these to your `.env.local` file:

```env
# Feature Flags Configuration
NEXT_PUBLIC_ENV=production
NEXT_PUBLIC_PREMIUM_ENFORCEMENT=false
```

### Environment Settings

| Environment | Premium Enforcement | Dev Bypass | Usage Limits | Description |
|-------------|-------------------|------------|--------------|-------------|
| `development` | Disabled | Enabled | Disabled | Local development |
| `dev` | Disabled | Enabled | Disabled | Development testing |
| `staging` | Enabled | Disabled | Enabled | Pre-production testing |
| `production` | Enabled | Disabled | Enabled | Live production |

## Feature Flags

### Premium Enforcement

- **`PREMIUM_ENFORCEMENT`**: Controls whether premium tier checks are enforced
  - `false`: All users can access premium features
  - `true`: Only pro/admin users can access premium features

### Feature Toggles

- **`ENABLE_ADVANCED_FEATURES`**: Enable/disable advanced features
- **`ENABLE_API_ACCESS`**: Enable/disable API key management
- **`ENABLE_DATA_EXPORTS`**: Enable/disable data export functionality
- **`ENABLE_CUSTOM_REPORTS`**: Enable/disable custom report generation
- **`ENABLE_WEBHOOKS`**: Enable/disable webhook management
- **`ENABLE_TRANSLATIONS`**: Enable/disable multilingual features

### Development Overrides

- **`DEV_BYPASS_PREMIUM`**: Automatically enabled in dev environment
- **`DEV_BYPASS_RATE_LIMITS`**: Automatically enabled in dev environment

### Usage Limits

- **`ENABLE_USAGE_LIMITS`**: Enable/disable usage tracking and limits
- **`ENABLE_PROJECT_LIMITS`**: Enable/disable project-based limits

## Usage

### In Components

```typescript
import { checkPremiumAccess, isPremiumEnforced } from '@/lib/featureFlags'

// Check if user has premium access
if (!checkPremiumAccess(userTier)) {
  return <PremiumRequiredMessage />
}

// Check if premium enforcement is enabled
if (isPremiumEnforced()) {
  // Show upgrade message
} else {
  // Show feature disabled message
}
```

### In API Routes

```typescript
import { checkRateLimit } from '@/lib/featureFlags'

// Check rate limits with feature flag override
if (!checkRateLimit(userTier, currentUsage, limit)) {
  return res.status(429).json({ error: 'Rate limit exceeded' })
}
```

## Debug Tools

### API Endpoint

Access feature flags status at `/api/feature-flags`:

```bash
curl http://localhost:3000/api/feature-flags
```

Response:
```json
{
  "flags": {
    "PREMIUM_ENFORCEMENT": false,
    "DEV_BYPASS_PREMIUM": true,
    "ENABLE_API_ACCESS": true,
    // ... other flags
  },
  "status": {
    "premiumEnforced": false,
    "devBypass": true,
    "environment": "development",
    "timestamp": "2024-12-19T10:30:00.000Z"
  }
}
```

### Debug Component

In development mode, a debug panel is available in the bottom-right corner showing:
- Current environment
- Premium enforcement status
- Dev bypass status
- All feature flag values
- Last update timestamp

## Implementation Details

### File Structure

```
apps/web/
├── lib/
│   └── featureFlags.ts          # Feature flags configuration
├── components/
│   └── FeatureFlagsDebug.tsx    # Debug component
├── pages/
│   └── api/
│       └── feature-flags.ts     # API endpoint
└── components/premium/          # Premium components using flags
    ├── ApiKeyManager.tsx
    ├── DataExporter.tsx
    ├── ReportBuilder.tsx
    ├── WebhookManager.tsx
    └── TranslationManager.tsx
```

### Updated Components

All premium components now use the feature flags system:

1. **ApiKeyManager**: Institutional tier check with feature flag override
2. **DataExporter**: Pro tier check with feature flag override
3. **ReportBuilder**: Pro tier check with feature flag override
4. **WebhookManager**: Institutional tier check with feature flag override
5. **TranslationManager**: Pro tier check with feature flag override

### User Hooks

The `useProAccess` hook has been updated to use the feature flags system:

```typescript
export function useProAccess() {
  const { profile } = useUser()
  const userTier = profile?.tier || 'free'
  
  // Use feature flag system for premium access check
  return checkPremiumAccess(userTier)
}
```

## Migration Guide

### Before (Hard-coded checks)

```typescript
// Old way - hard-coded tier checks
if (userSubscriptionTier !== 'pro' && userSubscriptionTier !== 'institutional') {
  return <PremiumRequiredMessage />
}
```

### After (Feature flag system)

```typescript
// New way - feature flag controlled
import { checkPremiumAccess, isPremiumEnforced } from '@/lib/featureFlags'

if (!checkPremiumAccess(userSubscriptionTier)) {
  return (
    <div>
      {isPremiumEnforced() ? (
        <PremiumRequiredMessage />
      ) : (
        <FeatureDisabledMessage />
      )}
    </div>
  )
}
```

## Testing

### Development Testing

1. Set `NEXT_PUBLIC_ENV=dev` in `.env.local`
2. All premium features will be accessible regardless of user tier
3. Use the debug panel to verify flag status

### Production Testing

1. Set `NEXT_PUBLIC_ENV=production` and `NEXT_PUBLIC_PREMIUM_ENFORCEMENT=false`
2. Premium features will be accessible but with "Feature Disabled" messages
3. Set `NEXT_PUBLIC_PREMIUM_ENFORCEMENT=true` to enable full enforcement

### Staging Testing

1. Set `NEXT_PUBLIC_ENV=staging`
2. Premium enforcement is enabled but with testing limits
3. Use real user tiers for testing

## Troubleshooting

### Feature Flags Not Working

1. Check environment variables are set correctly
2. Verify the debug panel shows expected values
3. Check browser console for any errors
4. Ensure components are importing from `@/lib/featureFlags`

### Debug Panel Not Showing

1. Ensure you're in development mode (`NODE_ENV=development`)
2. Check that `FeatureFlagsDebug` is imported in `_app.tsx`
3. Verify the component is not being blocked by other UI elements

### API Endpoint Not Responding

1. Check that `/api/feature-flags` route exists
2. Verify the API route is properly exported
3. Check server logs for any errors

## Future Enhancements

- [ ] Remote feature flag management
- [ ] A/B testing support
- [ ] User-specific feature flags
- [ ] Feature flag analytics
- [ ] Rollout percentage controls 