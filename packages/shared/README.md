# @morningmaghreb/shared

Shared utilities, types, and services for the Casablanca Insight platform.

## Features

- **Shared Types**: Common TypeScript interfaces used across web and mobile
- **API Services**: Platform-agnostic API service with platform-specific adapters
- **Utilities**: Common formatting, validation, and calculation functions
- **Components**: Reusable React components with platform-specific rendering

## Installation

This package is part of the monorepo workspace. It's automatically available to other packages in the workspace.

## Usage

### Types

```typescript
import type { 
  MarketData, 
  SentimentData, 
  PortfolioHolding 
} from '@morningmaghreb/shared'
```

### API Services

#### Web App

```typescript
import { WebApiService } from '@morningmaghreb/shared'
import { supabase } from '@/lib/supabase'

const apiService = new WebApiService(supabase)

// Use the service
const marketData = await apiService.getMarketData()
const sentiment = await apiService.getSentimentAggregate('ATW')
```

#### Mobile App

```typescript
import { MobileApiService } from '@morningmaghreb/shared'

const apiService = new MobileApiService('https://api.morningmaghreb.com')

// Use the service
const marketData = await apiService.getMarketData()
```

### Utilities

```typescript
import { 
  formatCurrency, 
  formatPercentage, 
  calculateGainLoss 
} from '@morningmaghreb/shared'

const formatted = formatCurrency(1234.56) // "MAD 1,234.56"
const percentage = formatPercentage(5.23) // "+5.23%"
const { totalGainLoss, totalGainLossPercent } = calculateGainLoss(100, 90, 10)
```

### Components

#### SentimentVoting Component

The SentimentVoting component is designed to be platform-agnostic with platform-specific rendering:

```typescript
import { SentimentVoting } from '@morningmaghreb/shared'

// Web implementation
<SentimentVoting
  ticker="ATW"
  companyName="Attijariwafa Bank"
  apiService={apiService}
  renderButton={({ sentiment, label, icon, isSelected, isLoading, onPress }) => (
    <button 
      onClick={onPress}
      disabled={isLoading}
      className={`btn ${isSelected ? 'selected' : ''}`}
    >
      {icon} {label}
    </button>
  )}
  renderResults={({ sentimentData }) => (
    <div className="results">
      {/* Web-specific results rendering */}
    </div>
  )}
  renderLoading={() => <div>Loading...</div>}
/>
```

## Development

### Building

```bash
cd packages/shared
npm run build
```

### Development Mode

```bash
npm run dev
```

### Testing

```bash
npm test
```

## Structure

```
src/
├── types/           # Shared TypeScript interfaces
├── services/        # API service base classes
├── adapters/        # Platform-specific implementations
├── components/      # Reusable React components
├── utils/          # Common utility functions
└── index.ts        # Main export file
```

## Contributing

When adding new shared functionality:

1. Add types to `src/types/`
2. Add utilities to `src/utils/`
3. Add services to `src/services/`
4. Add platform adapters if needed
5. Update the main `index.ts` export
6. Update this README

## Best Practices

- Keep platform-specific code in adapters
- Use TypeScript for all shared code
- Provide comprehensive type definitions
- Include validation schemas for API requests
- Make components configurable for different platforms
- Use abstract classes for services to allow platform-specific implementations 