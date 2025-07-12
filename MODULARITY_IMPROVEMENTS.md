# Codebase Modularity Improvements

## Current State Analysis

The Casablanca Insight codebase has a well-structured monorepo with three main applications:

- **Backend** (`apps/backend`): FastAPI Python application with modular routers
- **Web** (`apps/web`): Next.js React application
- **Mobile** (`apps/mobile`): React Native Expo application

## Identified Issues

### 1. Code Duplication
- **SentimentVoting components**: Nearly identical logic between web and mobile
- **API services**: Similar patterns but different implementations
- **Data types**: Duplicated interfaces across platforms
- **Utility functions**: Auth, formatting, validation duplicated

### 2. Inconsistent Patterns
- Different API service implementations
- Platform-specific type definitions
- Scattered utility functions

### 3. Maintenance Overhead
- Changes need to be made in multiple places
- Risk of inconsistencies between platforms
- Difficult to ensure type safety across platforms

## Implemented Solution: Shared Package

### Structure
```
packages/shared/
├── src/
│   ├── types/           # Shared TypeScript interfaces
│   ├── services/        # Platform-agnostic API services
│   ├── adapters/        # Platform-specific implementations
│   ├── components/      # Reusable React components
│   ├── utils/          # Common utility functions
│   └── index.ts        # Main export file
├── package.json
├── tsconfig.json
└── README.md
```

### Key Features

#### 1. Shared Types
```typescript
// Single source of truth for all data structures
export interface MarketData {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
  volume: number
}

export interface SentimentData {
  ticker: string
  bullish_count: number
  neutral_count: number
  bearish_count: number
  // ... consistent across platforms
}
```

#### 2. Platform-Agnostic API Service
```typescript
export abstract class BaseApiService {
  protected abstract getAuthHeaders(): Promise<Record<string, string>>
  
  async getMarketData(): Promise<MarketData[]> {
    return this.request<MarketData[]>('/api/markets/quotes')
  }
  
  async voteSentiment(vote: SentimentVote): Promise<void> {
    const validatedVote = SentimentVoteSchema.parse(vote)
    return this.request<void>('/api/sentiment/vote', {
      method: 'POST',
      body: JSON.stringify(validatedVote),
    })
  }
}
```

#### 3. Platform-Specific Adapters
```typescript
// Web adapter
export class WebApiService extends BaseApiService {
  constructor(supabase: SupabaseClient) {
    super('/api', async () => ({
      'Authorization': `Bearer ${session?.access_token}`,
      'Content-Type': 'application/json',
    }))
  }
}

// Mobile adapter
export class MobileApiService extends BaseApiService {
  constructor(baseUrl: string) {
    super(baseUrl, async () => ({
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    }))
  }
}
```

#### 4. Reusable Components
```typescript
// Platform-agnostic component with platform-specific rendering
export const SentimentVoting: React.FC<SentimentVotingProps> = ({
  ticker,
  apiService,
  renderButton,    // Platform-specific button rendering
  renderResults,   // Platform-specific results rendering
  renderLoading,   // Platform-specific loading state
}) => {
  // Shared logic here
}
```

#### 5. Shared Utilities
```typescript
export const formatCurrency = (amount: number, currency: string = 'MAD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

export const calculateGainLoss = (currentPrice: number, purchasePrice: number, quantity: number) => {
  const totalGainLoss = (currentPrice - purchasePrice) * quantity
  const totalGainLossPercent = ((currentPrice - purchasePrice) / purchasePrice) * 100
  return { totalGainLoss, totalGainLossPercent }
}
```

## Benefits Achieved

### 1. Reduced Duplication
- **Before**: ~300 lines of duplicated SentimentVoting logic
- **After**: Single shared component with platform-specific rendering
- **Before**: Duplicated API service patterns
- **After**: Single base class with platform adapters

### 2. Improved Type Safety
- Consistent types across all platforms
- Shared validation schemas
- Better IntelliSense and error detection

### 3. Easier Maintenance
- Changes to shared logic only need to be made once
- Consistent API patterns across platforms
- Centralized utility functions

### 4. Better Testing
- Shared logic can be tested independently
- Platform-specific code is isolated
- Easier to mock and test components

### 5. Enhanced Developer Experience
- Single source of truth for types
- Consistent patterns across platforms
- Better code organization

## Migration Strategy

### Phase 1: Foundation (Completed)
- ✅ Created shared package structure
- ✅ Implemented core types and utilities
- ✅ Created platform-agnostic API service
- ✅ Built SentimentVoting component example

### Phase 2: Migration (Next Steps)
- [ ] Migrate existing API services to use shared base classes
- [ ] Update components to use shared versions
- [ ] Replace duplicated utilities
- [ ] Update type imports

### Phase 3: Expansion (Future)
- [ ] Add more shared components (PortfolioHoldings, MarketOverview)
- [ ] Create shared hooks for state management
- [ ] Implement shared error handling
- [ ] Add shared testing utilities

## Recommendations

### 1. Immediate Actions
1. **Add shared package to workspace dependencies**
2. **Start migrating API services** to use shared base classes
3. **Update SentimentVoting components** to use shared version
4. **Replace duplicated utilities** with shared ones

### 2. Best Practices Going Forward
1. **New features should use shared types** from the start
2. **API services should extend BaseApiService**
3. **Components should be platform-agnostic** with platform-specific rendering
4. **Utilities should be shared** unless platform-specific

### 3. Architecture Improvements
1. **Consider adding more shared packages** for specific domains:
   - `@casablanca-insight/ui` - Shared UI components
   - `@casablanca-insight/validation` - Shared validation schemas
   - `@casablanca-insight/testing` - Shared testing utilities

2. **Implement shared state management**:
   - Zustand stores for common state
   - Shared hooks for data fetching
   - Platform-agnostic state persistence

3. **Add shared configuration**:
   - Environment variables
   - Feature flags
   - API endpoints

### 4. Backend Considerations
1. **Consider creating shared Python package** for backend utilities
2. **Standardize API response formats** across all endpoints
3. **Implement consistent error handling** patterns
4. **Add shared database models** and validation

## Success Metrics

### Code Quality
- **Reduced duplication**: Target 70% reduction in duplicated code
- **Type safety**: 100% shared types across platforms
- **Test coverage**: Improved coverage for shared components

### Developer Experience
- **Faster development**: New features use shared components
- **Consistent patterns**: Same API patterns across platforms
- **Better documentation**: Centralized documentation for shared code

### Maintenance
- **Reduced bugs**: Single source of truth reduces inconsistencies
- **Easier updates**: Changes propagate across all platforms
- **Better testing**: Shared logic can be tested independently

## Conclusion

The implemented shared package structure provides a solid foundation for reducing duplication and improving maintainability across the Casablanca Insight platform. The modular approach allows for platform-specific implementations while maintaining consistency in core business logic.

The next steps involve gradually migrating existing code to use the shared package, which will result in a more maintainable, type-safe, and consistent codebase across all platforms. 