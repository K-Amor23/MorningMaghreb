# Global Search Feature

## Overview

The Global Search Bar is a powerful search component that allows users to quickly find and navigate to company pages by searching for ticker symbols or company names.

## Features

### 🔍 Search Capabilities
- **Ticker Search**: Search by company ticker symbols (e.g., "ATW", "IAM")
- **Company Name Search**: Search by full company names (e.g., "Maroc Telecom", "Attijariwafa Bank")
- **Sector Search**: Search by industry sectors (e.g., "Banks", "Telecommunications")

### ⌨️ Keyboard Navigation
- **Arrow Keys**: Navigate through search results
- **Enter**: Select highlighted result or first result if only one
- **Escape**: Close search dropdown
- **Ctrl/Cmd + K**: Quick focus on search bar

### 📱 Responsive Design
- **Desktop**: Integrated search bar in header navigation
- **Mobile**: Modal search interface accessible via search icon

### 🎯 Smart Filtering
- Real-time search with 300ms debounce
- API-powered search with fallback to local data
- Results limited to 10 items for performance
- Case-insensitive matching

## Implementation

### Components

#### SearchBar.tsx
```typescript
interface Company {
  ticker: string
  name: string
  sector?: string
}

interface SearchBarProps {
  className?: string
}
```

**Key Features:**
- Debounced API calls to `/api/search/companies`
- Keyboard navigation with arrow keys
- Click outside to close
- Loading states and error handling
- Fallback to local data if API fails

#### Header.tsx Integration
- Desktop: Search bar positioned between logo and navigation
- Mobile: Search button in header, modal overlay for search interface

### API Endpoint

#### `/api/search/companies`
```typescript
GET /api/search/companies?q={query}

Response:
{
  success: boolean
  data: Company[]
  total: number
  query: string
}
```

**Supported Companies:**
- ATW - Attijariwafa Bank
- IAM - Maroc Telecom
- BCP - Banque Centrale Populaire
- BMCE - BMCE Bank
- ONA - Omnium Nord Africain
- MASI - MASI Index
- MADEX - MADEX Index
- MASI-ESG - MASI ESG Index
- And more...

## Usage

### Desktop
1. Click on the search bar in the header
2. Type ticker symbol or company name
3. Use arrow keys to navigate results
4. Press Enter to select or click on result
5. Use Ctrl/Cmd + K for quick access

### Mobile
1. Tap the search icon in the header
2. Search modal opens
3. Type to search
4. Tap result to navigate
5. Tap X to close modal

## Navigation

When a company is selected from search results, users are automatically navigated to:
```
/company/{ticker}
```

Example: Selecting "ATW" navigates to `/company/ATW`

## Styling

The search component uses Tailwind CSS classes and supports:
- Light/dark theme modes
- Responsive design
- Focus states and hover effects
- Loading animations
- Custom color scheme (casablanca-blue)

## Future Enhancements

- [ ] Search history
- [ ] Recent searches
- [ ] Search suggestions
- [ ] Advanced filters (sector, market cap, etc.)
- [ ] Search analytics
- [ ] Voice search support 