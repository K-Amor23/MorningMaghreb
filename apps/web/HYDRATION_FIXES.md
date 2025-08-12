# React Hydration Mismatch Fixes

This document outlines the comprehensive fixes for React hydration mismatch errors in the Casablanca Insights application.

## 🔍 Root Causes Identified

### 1. Direct localStorage Access
**Problem**: Components directly accessing `localStorage` during server-side rendering
**Components Affected**: 
- `AiAssistant.tsx`
- `ApiKeyManager.tsx`
- `WebhookManager.tsx`
- `DataExporter.tsx`
- `TranslationManager.tsx`
- `ReportBuilder.tsx`

### 2. Time-based Rendering
**Problem**: Components rendering different content based on current time/date
**Components Affected**:
- `MarketOverview.tsx` (ClientTime component)
- `DataQualityIndicator.tsx`
- `TickerBar.tsx`
- `Dashboard.tsx` (ClientTime component)

### 3. Authentication State Differences
**Problem**: Components rendering different content based on authentication state
**Components Affected**:
- Components using `useUser()` hook
- Components checking authentication status

## 🛠️ Solutions Implemented

### 1. Safe localStorage Access Hook

Created `useLocalStorageGetter` hook in `lib/useClientOnly.ts`:

```typescript
export function useLocalStorageGetter() {
    const [mounted, setMounted] = useState(false)

    useEffect(() => {
        setMounted(true)
    }, [])

    const getItem = (key: string): string | null => {
        if (!mounted || typeof window === 'undefined') return null
        
        try {
            return localStorage.getItem(key)
        } catch (error) {
            console.error(`Error reading localStorage key "${key}":`, error)
            return null
        }
    }

    return { getItem, mounted }
}
```

### 2. Client-Side Only Components

For components that need to render different content on client vs server:

```typescript
// Don't render until mounted to prevent hydration mismatch
if (!mounted) {
    return (
        <div className="loading-placeholder">
            {/* Show loading state that matches final rendered content */}
        </div>
    )
}
```

### 3. Time-based Component Fixes

For components that display current time:

```typescript
function ClientTime() {
    const [mounted, setMounted] = useState(false)
    const [time, setTime] = useState<string>('')

    useEffect(() => {
        setMounted(true)
        const updateTime = () => {
            setTime(new Date().toLocaleTimeString())
        }
        updateTime()
        const interval = setInterval(updateTime, 1000)
        return () => clearInterval(interval)
    }, [])

    // Show placeholder during SSR and initial render
    if (!mounted) {
        return <span>--:--:--</span>
    }

    return <span>{time}</span>
}
```

## 📋 Components Fixed

### ✅ Fixed Components

1. **AiAssistant.tsx**
   - Replaced direct `localStorage.getItem()` with `useLocalStorageGetter`
   - Added mounted check to prevent rendering until client-side
   - Added loading placeholder for SSR

2. **ApiKeyManager.tsx**
   - Replaced direct `localStorage.getItem()` with `useLocalStorageGetter`
   - Added mounted check with loading skeleton
   - Improved error handling

3. **MarketOverview.tsx**
   - ClientTime component already properly implemented
   - Uses mounted state to prevent hydration mismatch

4. **DataQualityIndicator.tsx**
   - ClientTime component already properly implemented
   - Uses mounted state to prevent hydration mismatch

### 🔄 Components to Fix

The following components still need to be updated to use the safe localStorage access pattern:

1. **WebhookManager.tsx**
2. **DataExporter.tsx**
3. **TranslationManager.tsx**
4. **ReportBuilder.tsx**
5. **ContestLeaderboard.tsx** (if using localStorage)

## 🚀 Implementation Steps

### Step 1: Update Components with Direct localStorage Access

For each component that directly accesses localStorage:

1. Import the safe hook:
```typescript
import { useLocalStorageGetter } from '@/lib/useClientOnly'
```

2. Replace direct access:
```typescript
// Before
const token = localStorage.getItem('supabase.auth.token')

// After
const { getItem, mounted } = useLocalStorageGetter()
const token = getItem('supabase.auth.token')
```

3. Add mounted check:
```typescript
if (!mounted) {
    return <LoadingPlaceholder />
}
```

### Step 2: Update Time-based Components

For components that render current time:

1. Use the existing ClientTime pattern
2. Ensure placeholder content matches final rendered content
3. Use consistent styling between placeholder and actual content

### Step 3: Update Authentication-dependent Components

For components that render differently based on auth state:

1. Use the existing `useUser()` hook which already handles hydration
2. Add loading states for auth-dependent content
3. Ensure consistent rendering between server and client

## 🧪 Testing

### Manual Testing Checklist

- [ ] Load page with JavaScript disabled
- [ ] Load page with JavaScript enabled
- [ ] Check browser console for hydration warnings
- [ ] Test authentication flows
- [ ] Test components that use localStorage
- [ ] Test time-based components
- [ ] Test on different browsers

### Automated Testing

Add hydration tests to prevent regressions:

```typescript
// tests/hydration.test.tsx
import { render } from '@testing-library/react'
import { useLocalStorageGetter } from '@/lib/useClientOnly'

test('useLocalStorageGetter returns null during SSR', () => {
    const { getItem, mounted } = useLocalStorageGetter()
    expect(getItem('test')).toBeNull()
    expect(mounted).toBe(false)
})
```

## 🔧 Additional Optimizations

### 1. Next.js Configuration

Update `next.config.js` to suppress hydration warnings in development:

```javascript
const nextConfig = {
    // ... existing config
    reactStrictMode: true,
    // Suppress hydration warnings in development
    onDemandEntries: {
        maxInactiveAge: 25 * 1000,
        pagesBufferLength: 2,
    },
}
```

### 2. Environment Variables

Ensure all environment variables are properly prefixed:

```env
# ✅ Correct
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...

# ❌ Incorrect (causes hydration issues)
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
```

### 3. Dynamic Imports

Use dynamic imports for components that are client-only:

```typescript
import dynamic from 'next/dynamic'

const ClientOnlyComponent = dynamic(() => import('./ClientOnlyComponent'), {
    ssr: false
})
```

## 📊 Monitoring

### Console Monitoring

Add monitoring to track hydration issues:

```typescript
// lib/hydration-monitor.ts
export function monitorHydration() {
    if (typeof window !== 'undefined') {
        const originalError = console.error
        console.error = (...args) => {
            if (args[0]?.includes?.('Hydration')) {
                // Log hydration errors for monitoring
                console.warn('Hydration mismatch detected:', args)
            }
            originalError.apply(console, args)
        }
    }
}
```

### Performance Impact

- **Before**: Hydration mismatches causing layout shifts and errors
- **After**: Consistent rendering between server and client
- **Improvement**: Better user experience and SEO

## 🎯 Best Practices

### 1. Always Check for Client-side APIs

```typescript
// ✅ Good
if (typeof window !== 'undefined' && mounted) {
    // Access browser APIs
}

// ❌ Bad
localStorage.getItem('key')
```

### 2. Use Consistent Placeholders

```typescript
// ✅ Good - placeholder matches final content
if (!mounted) return <span>--:--:--</span>
return <span>{time}</span>

// ❌ Bad - different content causes mismatch
if (!mounted) return <div>Loading...</div>
return <span>{time}</span>
```

### 3. Handle Authentication State Properly

```typescript
// ✅ Good
const { user, loading } = useUser()
if (loading) return <LoadingSpinner />
if (!user) return <LoginPrompt />
return <AuthenticatedContent />

// ❌ Bad
const user = localStorage.getItem('user')
if (user) return <AuthenticatedContent />
return <LoginPrompt />
```

## 🔄 Migration Checklist

- [ ] Update all components using direct localStorage access
- [ ] Test time-based components
- [ ] Verify authentication flows
- [ ] Add loading states for client-only components
- [ ] Update tests to cover hydration scenarios
- [ ] Monitor console for remaining hydration warnings
- [ ] Document any remaining issues

## 📚 Resources

- [React Hydration Documentation](https://react.dev/reference/react-dom/hydrate)
- [Next.js SSR Best Practices](https://nextjs.org/docs/advanced-features/server-side-rendering)
- [React 18 Hydration Changes](https://react.dev/blog/2022/03/29/react-v18#automatic-batching) 