# Migration Guide: Using Shared Package

This guide shows how to migrate existing code to use the new `@casablanca-insight/shared` package.

## 1. Install Shared Package

The shared package is already configured in the workspace. You can start using it immediately.

## 2. Migrate API Services

### Before (Web App)

```typescript
// apps/web/lib/portfolioService.ts
import { supabase } from './supabase'

export interface PortfolioHolding {
  // ... duplicated types
}

class PortfolioService {
  private baseUrl = '/api'

  private async getAuthHeaders() {
    // ... duplicated auth logic
  }

  async getUserPortfolios() {
    // ... duplicated API calls
  }
}
```

### After (Web App)

```typescript
// apps/web/lib/apiService.ts
import { WebApiService } from '@casablanca-insight/shared'
import { supabase } from './supabase'

export const apiService = new WebApiService(supabase)
```

### Before (Mobile App)

```typescript
// apps/mobile/src/services/api.ts
class ApiService {
  private baseUrl: string

  constructor() {
    this.baseUrl = API_BASE_URL
  }

  async getMarketData(): Promise<MarketData[]> {
    // ... duplicated API logic
  }
}
```

### After (Mobile App)

```typescript
// apps/mobile/src/services/api.ts
import { MobileApiService } from '@casablanca-insight/shared'

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000'
export const apiService = new MobileApiService(API_BASE_URL)
```

## 3. Migrate Components

### Before (Duplicated SentimentVoting)

```typescript
// apps/web/components/SentimentVoting.tsx
// apps/mobile/src/components/SentimentVoting.tsx
// Both files had nearly identical logic
```

### After (Shared Component)

```typescript
// apps/web/components/SentimentVoting.tsx
import { SentimentVoting as SharedSentimentVoting } from '@casablanca-insight/shared'
import { ArrowUpIcon, ArrowRightIcon, ArrowDownIcon } from '@heroicons/react/24/outline'
import { apiService } from '@/lib/apiService'
import toast from 'react-hot-toast'

export const SentimentVoting: React.FC<{ ticker: string; companyName?: string }> = (props) => (
  <SharedSentimentVoting
    {...props}
    apiService={apiService}
    renderButton={({ sentiment, label, icon, isSelected, isLoading, onPress }) => {
      const getIcon = () => {
        switch (sentiment) {
          case 'bullish': return <ArrowUpIcon className="h-4 w-4" />
          case 'neutral': return <ArrowRightIcon className="h-4 w-4" />
          case 'bearish': return <ArrowDownIcon className="h-4 w-4" />
        }
      }
      
      return (
        <button
          onClick={onPress}
          disabled={isLoading}
          className={`
            flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all
            ${isSelected ? 'ring-2 ring-offset-2 ring-blue-500' : ''}
            ${isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-md'}
          `}
        >
          {getIcon()}
          <span>{label}</span>
        </button>
      )
    }}
    renderResults={({ sentimentData }) => (
      <div className="space-y-2">
        <div className="flex justify-between">
          <span>📈 Bullish</span>
          <span>{sentimentData.bullish_count} ({sentimentData.bullish_percentage.toFixed(1)}%)</span>
        </div>
        {/* ... more results */}
      </div>
    )}
    renderLoading={() => (
      <div className="animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-10 bg-gray-200 rounded"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
        </div>
      </div>
    )}
    renderError={(error) => toast.error(error)}
  />
)
```

```typescript
// apps/mobile/src/components/SentimentVoting.tsx
import { SentimentVoting as SharedSentimentVoting } from '@casablanca-insight/shared'
import { View, Text, TouchableOpacity, ActivityIndicator, Alert } from 'react-native'
import { apiService } from '../services/api'

export const SentimentVoting: React.FC<{ ticker: string; companyName?: string }> = (props) => (
  <SharedSentimentVoting
    {...props}
    apiService={apiService}
    renderButton={({ sentiment, label, icon, isSelected, isLoading, onPress }) => (
      <TouchableOpacity
        style={[styles.voteButton, isSelected && styles.selectedVoteButton]}
        onPress={onPress}
        disabled={isLoading}
      >
        <Text style={styles.voteEmoji}>{icon}</Text>
        <Text style={styles.voteText}>{label}</Text>
        {isLoading && <ActivityIndicator size="small" />}
      </TouchableOpacity>
    )}
    renderResults={({ sentimentData }) => (
      <View style={styles.resultsContainer}>
        <Text style={styles.resultsTitle}>Community Results</Text>
        <View style={styles.resultRow}>
          <Text style={styles.resultLabel}>📈 Bullish</Text>
          <Text style={styles.resultValue}>
            {sentimentData.bullish_count} ({sentimentData.bullish_percentage.toFixed(1)}%)
          </Text>
        </View>
        {/* ... more results */}
      </View>
    )}
    renderLoading={() => (
      <View style={styles.container}>
        <ActivityIndicator size="small" color="#1e3a8a" />
        <Text style={styles.loadingText}>Loading sentiment data...</Text>
      </View>
    )}
    renderError={(error) => Alert.alert('Error', error)}
  />
)
```

## 4. Migrate Utilities

### Before

```typescript
// Duplicated in multiple files
export const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'MAD',
  }).format(amount)
}
```

### After

```typescript
// apps/web/components/SomeComponent.tsx
import { formatCurrency } from '@casablanca-insight/shared'

const formatted = formatCurrency(1234.56) // "MAD 1,234.56"
```

## 5. Update Package Dependencies

### Web App (apps/web/package.json)

```json
{
  "dependencies": {
    "@casablanca-insight/shared": "workspace:*",
    // ... other dependencies
  }
}
```

### Mobile App (apps/mobile/package.json)

```json
{
  "dependencies": {
    "@casablanca-insight/shared": "workspace:*",
    // ... other dependencies
  }
}
```

## 6. Benefits After Migration

1. **Reduced Duplication**: Shared logic is maintained in one place
2. **Type Safety**: Consistent types across platforms
3. **Easier Maintenance**: Changes to shared logic only need to be made once
4. **Better Testing**: Shared code can be tested independently
5. **Consistent API**: Same API service interface across platforms

## 7. Migration Checklist

- [ ] Install shared package in workspace
- [ ] Migrate API services to use shared base classes
- [ ] Update components to use shared versions
- [ ] Replace duplicated utilities with shared ones
- [ ] Update type imports to use shared types
- [ ] Test all functionality after migration
- [ ] Remove old duplicated files
- [ ] Update documentation

## 8. Rollback Plan

If issues arise during migration:

1. Keep old files with `.backup` extension
2. Use feature flags to toggle between old and new implementations
3. Gradually migrate components one at a time
4. Monitor for any regressions

## 9. Next Steps

After successful migration:

1. Add more shared components (PortfolioHoldings, MarketOverview, etc.)
2. Create shared hooks for common state management
3. Add shared validation schemas
4. Implement shared error handling
5. Add shared testing utilities 