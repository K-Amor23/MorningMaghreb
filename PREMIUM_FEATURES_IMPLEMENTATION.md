# Premium Features Implementation

This document outlines the complete implementation of premium features for the Casablanca Insight platform, including API access, data exports, custom reports, webhooks, and multilingual support.

## Overview

The premium features are designed for different subscription tiers:
- **Free**: Basic market data and limited features
- **Pro**: Advanced features, data exports, custom reports, multilingual support
- **Institutional**: All Pro features plus API access, webhooks, priority support

## Backend Implementation

### 1. Premium API Access (`/api/premium`)

**File**: `apps/backend/routers/premium_api.py`

#### Features:
- API key management for institutional users
- Rate limiting and authentication
- GAAP-normalized financial data endpoints
- Macro data endpoints with time-series support

#### Key Endpoints:
```typescript
POST /api/premium/api-keys          // Create API key
GET  /api/premium/api-keys          // List API keys
POST /api/premium/financials        // Get GAAP financial data
POST /api/premium/macro             // Get macro data
GET  /api/premium/usage             // Get API usage stats
```

#### Usage Example:
```bash
# Create API key
curl -X POST /api/premium/api-keys \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "key_name": "Production API",
    "permissions": ["read_financials", "read_macro"],
    "rate_limit_per_hour": 1000
  }'

# Use API key
curl -X POST /api/premium/financials \
  -H "X-API-Key: cas_sk_..." \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["ATW", "IAM"],
    "metrics": ["revenue", "net_income"],
    "gaap_only": true
  }'
```

### 2. Data Exports (`/api/exports`)

**File**: `apps/backend/routers/exports.py`

#### Features:
- Export financial data, macro data, and portfolio data
- Multiple formats: CSV, Excel (XLSX), JSON
- Background processing with status tracking
- Quick export endpoints for common use cases

#### Key Endpoints:
```typescript
POST /api/exports                    // Create export
GET  /api/exports/{id}              // Get export status
GET  /api/exports/{id}/download     // Download export
GET  /api/exports                    // List exports
POST /api/exports/financials/quick  // Quick financial export
POST /api/exports/macro/quick       // Quick macro export
```

#### Usage Example:
```bash
# Create financial export
curl -X POST /api/exports \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "export_type": "financials",
    "file_format": "xlsx",
    "filters": {
      "tickers": ["ATW", "IAM", "BCP"],
      "period": "2024-Q3"
    }
  }'

# Quick export
curl -X POST /api/exports/financials/quick \
  -H "Authorization: Bearer <token>" \
  -d 'tickers=ATW,IAM&period=2024-Q3&format=csv'
```

### 3. Custom Reports (`/api/reports`)

**File**: `apps/backend/routers/reports.py`

#### Features:
- Generate 1-page PDF investment summaries
- Multiple report types: investment summary, financial analysis, risk profile
- AI-powered content generation
- Background processing with progress tracking

#### Key Endpoints:
```typescript
POST /api/reports                    // Create report
GET  /api/reports/{id}              // Get report status
GET  /api/reports/{id}/download     // Download report
GET  /api/reports                    // List reports
GET  /api/reports/templates         // Get report templates
POST /api/reports/quick/{ticker}    // Quick report generation
```

#### Usage Example:
```bash
# Create investment summary
curl -X POST /api/reports \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "company_ticker": "ATW",
    "report_type": "investment_summary",
    "include_charts": true,
    "include_ai_summary": true
  }'

# Quick report
curl -X POST /api/reports/quick/ATW \
  -H "Authorization: Bearer <token>" \
  -d 'report_type=investment_summary'
```

### 4. Webhooks (`/api/webhooks`)

**File**: `apps/backend/routers/webhooks.py`

#### Features:
- Real-time data delivery via webhooks
- Multiple event types: price alerts, earnings releases, dividend payments
- Delivery history and failure tracking
- Webhook testing and validation

#### Key Endpoints:
```typescript
POST /api/webhooks                   // Create webhook
GET  /api/webhooks                   // List webhooks
PATCH /api/webhooks/{id}/toggle      // Toggle webhook status
POST /api/webhooks/{id}/test         // Test webhook
GET  /api/webhooks/{id}/deliveries   // Get delivery history
DELETE /api/webhooks/{id}            // Delete webhook
```

#### Usage Example:
```bash
# Create webhook
curl -X POST /api/webhooks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Price Alerts for ATW",
    "url": "https://your-server.com/webhook",
    "events": ["price_alert", "earnings_release"],
    "secret": "optional_secret_key"
  }'

# Test webhook
curl -X POST /api/webhooks/{id}/test \
  -H "Authorization: Bearer <token>"
```

### 5. Multilingual Support (`/api/translations`)

**File**: `apps/backend/routers/translations.py`

#### Features:
- AI-powered translation for financial content
- Support for English, French, Arabic, Spanish, German
- Language detection
- Translation history and caching

#### Key Endpoints:
```typescript
POST /api/translations/translate     // Translate text
POST /api/translations/detect        // Detect language
GET  /api/translations               // Get translation history
```

#### Usage Example:
```bash
# Translate text
curl -X POST /api/translations/translate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Attijariwafa Bank reported strong Q3 results",
    "source_language": "en",
    "target_language": "fr",
    "content_type": "report"
  }'

# Detect language
curl -X POST /api/translations/detect \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"text": "Sample text to detect"}'
```

## Frontend Implementation

### 1. Premium Features Page

**File**: `apps/web/pages/premium-features.tsx`

#### Features:
- Tabbed interface for all premium features
- Subscription tier-based access control
- Modern, responsive design
- Integration with all premium components

#### Navigation:
- Added "Premium" link to main navigation
- Accessible at `/premium-features`

### 2. API Key Manager

**File**: `apps/web/components/premium/ApiKeyManager.tsx`

#### Features:
- Create, list, and delete API keys
- Permission management
- Rate limit configuration
- Usage statistics display
- Institutional tier access control

#### Key Components:
- API key creation form
- API key list with status indicators
- Usage metrics display
- Copy-to-clipboard functionality

### 3. Data Exporter

**File**: `apps/web/components/premium/DataExporter.tsx`

#### Features:
- Export creation with custom filters
- Multiple file format support
- Export history and status tracking
- Quick export buttons for common scenarios
- Pro and Institutional tier access

#### Key Components:
- Export creation form
- Export history list
- Status indicators and progress tracking
- Download functionality

### 4. Report Builder

**File**: `apps/web/components/premium/ReportBuilder.tsx`

#### Features:
- Custom report generation
- Multiple report types and templates
- Report history and status tracking
- Quick report generation
- Pro and Institutional tier access

#### Key Components:
- Report creation form
- Report templates selection
- Report history list
- Download functionality

### 5. Webhook Manager

**File**: `apps/web/components/premium/WebhookManager.tsx`

#### Features:
- Webhook creation and management
- Event subscription configuration
- Delivery history and failure tracking
- Webhook testing functionality
- Institutional tier access control

#### Key Components:
- Webhook creation form
- Webhook list with status indicators
- Delivery history modal
- Test and toggle functionality

### 6. Translation Manager

**File**: `apps/web/components/premium/TranslationManager.tsx`

#### Features:
- Text translation interface
- Language detection
- Translation history
- Quick translation samples
- Pro and Institutional tier access

#### Key Components:
- Translation form
- Language selection dropdowns
- Translation history list
- Quick translation buttons

## Database Schema

### New Tables Added:

```sql
-- API Keys
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_name VARCHAR(255) NOT NULL,
    api_key_hash VARCHAR(255) UNIQUE NOT NULL,
    permissions TEXT[] DEFAULT '{}',
    rate_limit_per_hour INTEGER DEFAULT 1000,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Data Exports
CREATE TABLE data_exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    export_type VARCHAR(50) NOT NULL,
    file_format VARCHAR(10) NOT NULL,
    filters JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    file_path VARCHAR(500),
    file_size_bytes BIGINT,
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Custom Reports
CREATE TABLE custom_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_ticker VARCHAR(10) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    file_path VARCHAR(500),
    file_size_bytes BIGINT,
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Webhooks
CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    events TEXT[] DEFAULT '{}',
    secret_key VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    delivery_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    last_delivery TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Webhook Deliveries
CREATE TABLE webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID REFERENCES webhooks(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    payload JSONB,
    status VARCHAR(20) NOT NULL,
    response_code INTEGER,
    response_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Translations
CREATE TABLE translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    source_text TEXT NOT NULL,
    source_language VARCHAR(10) NOT NULL,
    target_language VARCHAR(10) NOT NULL,
    translated_text TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    word_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Authentication & Authorization

### Subscription Tier Checks:
- All premium endpoints check user subscription tier
- Free users are blocked from premium features
- Pro users can access exports, reports, and translations
- Institutional users get full access including API keys and webhooks

### API Key Authentication:
- API keys are hashed before storage
- Rate limiting per API key
- Permission-based access control
- Expiration date support

## Error Handling

### Backend Error Responses:
```json
{
  "error": "Subscription tier required",
  "message": "Pro or Institutional tier required for this feature",
  "code": "TIER_REQUIRED"
}
```

### Frontend Error Handling:
- Toast notifications for user feedback
- Loading states and disabled buttons
- Graceful degradation for failed requests
- Retry mechanisms for transient failures

## Performance Considerations

### Backend Optimizations:
- Background task processing for heavy operations
- Database indexing on frequently queried fields
- Caching for translation results
- Rate limiting to prevent abuse

### Frontend Optimizations:
- Lazy loading of premium components
- Debounced API calls
- Optimistic UI updates
- Efficient state management

## Security Features

### Data Protection:
- API keys are hashed using SHA-256
- Webhook secrets for verification
- Row-level security policies
- Input validation and sanitization

### Access Control:
- JWT token-based authentication
- Subscription tier validation
- Permission-based feature access
- Rate limiting and abuse prevention

## Testing

### Backend Testing:
- Unit tests for all premium endpoints
- Integration tests for database operations
- Mock external API calls
- Error scenario testing

### Frontend Testing:
- Component unit tests
- Integration tests for user flows
- Subscription tier access testing
- Error handling validation

## Deployment

### Environment Variables:
```bash
# Required for premium features
OPENAI_API_KEY=your_openai_key
DATABASE_URL=your_database_url
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key

# Optional for advanced features
REDIS_URL=your_redis_url
SENDGRID_API_KEY=your_sendgrid_key
```

### Database Migrations:
- Run schema updates for new tables
- Create indexes for performance
- Set up row-level security policies
- Configure backup strategies

## Monitoring & Analytics

### Metrics to Track:
- API key usage and rate limiting
- Export and report generation times
- Webhook delivery success rates
- Translation accuracy and usage
- Feature adoption by subscription tier

### Logging:
- API request/response logging
- Error tracking and alerting
- Performance monitoring
- User activity analytics

## Future Enhancements

### Planned Features:
1. **Advanced Analytics**: Custom dashboard creation
2. **Data Visualization**: Interactive charts and graphs
3. **Collaboration Tools**: Team workspaces and sharing
4. **Mobile Apps**: Native mobile premium features
5. **API Marketplace**: Third-party integrations

### Technical Improvements:
1. **Real-time Updates**: WebSocket connections for live data
2. **Advanced Caching**: Redis-based caching layer
3. **Microservices**: Service decomposition for scalability
4. **Machine Learning**: AI-powered insights and predictions

## Support & Documentation

### User Documentation:
- Feature guides and tutorials
- API documentation with examples
- Best practices and use cases
- Troubleshooting guides

### Developer Documentation:
- API reference documentation
- Integration guides
- Code examples and SDKs
- Contributing guidelines

## Conclusion

The premium features implementation provides a comprehensive set of tools for professional and institutional investors, with proper access control, security measures, and performance optimizations. The modular design allows for easy extension and maintenance, while the user-friendly interface ensures a smooth experience for all subscription tiers. 