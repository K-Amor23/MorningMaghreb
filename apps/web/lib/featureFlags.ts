// Feature flags configuration
export const featureFlags = {
  PREMIUM_FEATURES: process.env.NEXT_PUBLIC_ENABLE_PREMIUM_FEATURES === 'true',
  PAPER_TRADING: process.env.NEXT_PUBLIC_ENABLE_PAPER_TRADING === 'true',
  SENTIMENT_VOTING: process.env.NEXT_PUBLIC_ENABLE_SENTIMENT_VOTING === 'true',
  ADVANCED_CHARTS: process.env.NEXT_PUBLIC_ENABLE_ADVANCED_CHARTS === 'true',
  REAL_TIME_DATA: process.env.NEXT_PUBLIC_ENABLE_REAL_TIME_DATA === 'true',
}

// Check if premium access is required for a feature
export function checkPremiumAccess(feature: keyof typeof featureFlags): boolean {
  // For now, return true to allow all features
  // This should be replaced with actual premium access logic
  return true
}

// Check if premium features are enforced
export function isPremiumEnforced(): boolean {
  return process.env.NEXT_PUBLIC_ENFORCE_PREMIUM === 'true'
}

// Check if development bypass is enabled
export function hasDevBypass(): boolean {
  return process.env.NODE_ENV === 'development' || process.env.NEXT_PUBLIC_DEV_BYPASS === 'true'
} 