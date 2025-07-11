# Advanced Features Implementation

This document outlines the implementation of three advanced features for the Casablanca Insight platform:

1. **Weekly AI Market Recap** - Automated GPT-written email/newsletter
2. **Crowdsourced Sentiment Voting** - User voting system for stock sentiment
3. **Mobile Widget Integration** - Android/iOS widgets for increased engagement

## 1. Weekly AI Market Recap

### Overview
Automated weekly market recap emails generated using OpenAI GPT-4, summarizing market movements in Morocco with multi-language support (English, French, Arabic).

### Backend Implementation

#### Files Created/Modified:
- `apps/backend/routers/newsletter.py` - Newsletter API endpoints
- `apps/backend/lib/openai_service.py` - AI content generation
- `apps/backend/models/newsletter.py` - Database models (referenced)

#### Key Features:
- **Multi-language Support**: English, French, Arabic content generation
- **Contextual Data**: Integrates market data, macro indicators, and sector performance
- **Background Processing**: Asynchronous email sending
- **Fallback Content**: Graceful degradation when AI fails
- **Preview Mode**: Test content before sending

#### API Endpoints:
```typescript
POST /api/newsletter/generate-weekly-recap
GET /api/newsletter/weekly-recap/preview
GET /api/newsletter/subscribers
POST /api/newsletter/send-test
```

#### Usage Example:
```python
# Generate weekly recap
recap = await generate_weekly_recap(
    include_macro=True,
    include_sectors=True,
    include_top_movers=True,
    language="en"
)

# Send to subscribers
background_tasks.add_task(send_weekly_recap, campaign_id, db)
```

### Frontend Integration
- Newsletter signup component already exists
- Admin interface for managing campaigns
- Email templates with responsive design

## 2. Crowdsourced Sentiment Voting

### Overview
Community-driven sentiment voting system allowing users to vote Bullish/Neutral/Bearish on stocks with confidence levels and real-time aggregate displays.

### Backend Implementation

#### Files Created/Modified:
- `apps/backend/routers/sentiment.py` - Sentiment voting API
- `apps/backend/models/sentiment.py` - Database models
- `database/schema.sql` - Database schema updates

#### Database Schema:
```sql
-- Sentiment votes table
CREATE TABLE sentiment_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    sentiment VARCHAR(20) NOT NULL CHECK (sentiment IN ('bullish', 'neutral', 'bearish')),
    confidence INTEGER NOT NULL DEFAULT 1 CHECK (confidence BETWEEN 1 AND 5),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, ticker)
);

-- Sentiment aggregates table
CREATE TABLE sentiment_aggregates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL UNIQUE,
    bullish_count INTEGER DEFAULT 0,
    neutral_count INTEGER DEFAULT 0,
    bearish_count INTEGER DEFAULT 0,
    total_votes INTEGER DEFAULT 0,
    bullish_percentage FLOAT DEFAULT 0.0,
    neutral_percentage FLOAT DEFAULT 0.0,
    bearish_percentage FLOAT DEFAULT 0.0,
    average_confidence FLOAT DEFAULT 0.0,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Triggers for automatic aggregate updates
CREATE OR REPLACE FUNCTION update_sentiment_aggregate()
RETURNS TRIGGER AS $$
BEGIN
    -- Update aggregates when votes change
    -- Implementation details in schema.sql
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

#### API Endpoints:
```typescript
POST /api/sentiment/vote
GET /api/sentiment/my-votes
GET /api/sentiment/aggregate/{ticker}
GET /api/sentiment/top-sentiment
DELETE /api/sentiment/vote/{ticker}
```

#### Usage Example:
```python
# Vote on stock sentiment
vote = SentimentVoteRequest(
    ticker="ATW",
    sentiment="bullish",
    confidence=4
)

# Get aggregate sentiment
aggregate = await get_sentiment_aggregate("ATW")
# Returns: { bullish_percentage: 65.2, bearish_percentage: 12.3, ... }
```

### Frontend Implementation

#### Web Components:
- `apps/web/components/SentimentVoting.tsx` - Main voting component
- Real-time sentiment display
- Interactive voting buttons
- Confidence level selector
- Aggregate sentiment visualization

#### Mobile Components:
- React Native sentiment voting interface
- Touch-friendly voting controls
- Real-time updates via WebSocket

#### Features:
- **Real-time Updates**: Live sentiment changes
- **Confidence Levels**: 1-5 scale voting
- **Visual Indicators**: Color-coded sentiment display
- **Community Insights**: Top sentiment stocks
- **User History**: Personal voting history

## 3. Mobile Widget Integration

### Overview
Native mobile widgets for Android/iOS displaying MASI index, watchlist movements, and macro indicators to increase daily user engagement.

### Mobile Implementation

#### Files Created:
- `apps/mobile/src/components/widgets/MASIWidget.tsx` - MASI index widget
- `apps/mobile/src/components/widgets/WatchlistWidget.tsx` - Watchlist widget
- `apps/mobile/src/components/widgets/MacroWidget.tsx` - Macro indicators widget
- `apps/mobile/src/components/widgets/WidgetConfiguration.tsx` - Widget settings
- `apps/mobile/src/components/widgets/index.ts` - Export file

#### Widget Features:

##### MASI Widget
- Real-time MASI index display
- Price change and percentage
- Multiple sizes (small, medium, large)
- Configurable refresh intervals
- Volume data (large size)

##### Watchlist Widget
- User's watchlist stocks
- Current prices and changes
- Scrollable list view
- Configurable max items
- Stock tap navigation

##### Macro Widget
- Key economic indicators
- Inflation, policy rates, FX reserves
- Visual indicators with icons
- Change tracking
- Configurable refresh intervals

#### Widget Configuration:
- **Size Options**: Small (120x80), Medium (160x120), Large (200x160)
- **Refresh Intervals**: 5min, 15min, 30min, 1hour
- **Max Items**: 2-5 items for list widgets
- **Persistent Settings**: AsyncStorage configuration
- **Easy Setup**: Modal configuration interface

#### Integration:
- Settings screen integration
- Widget configuration modal
- Background data refresh
- Error handling and loading states
- Offline fallback support

### Widget Setup Instructions

#### For Users:
1. Long press on home screen
2. Tap "+" to add widgets
3. Search "Casablanca Insight"
4. Choose widget size
5. Configure in app settings

#### For Developers:
```typescript
// Import widgets
import { MASIWidget, WatchlistWidget, MacroWidget } from '../components/widgets'

// Use in components
<MASIWidget 
  size="medium" 
  refreshInterval={15}
  onPress={() => navigation.navigate('Markets')}
/>

<WatchlistWidget 
  size="large" 
  maxItems={5}
  onStockPress={(symbol) => navigation.navigate('Company', { symbol })}
/>
```

## Technical Architecture

### Backend Stack:
- **FastAPI**: RESTful API framework
- **PostgreSQL**: Primary database
- **TimescaleDB**: Time-series data optimization
- **OpenAI GPT-4**: AI content generation
- **SQLAlchemy**: ORM and database management
- **Background Tasks**: Asynchronous processing

### Frontend Stack:
- **Next.js**: Web application framework
- **React Native**: Mobile application
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Zustand**: State management
- **Supabase**: Authentication and real-time

### Database Design:
- **Normalized Schema**: Efficient data storage
- **Time-series Optimization**: TimescaleDB for market data
- **Real-time Updates**: PostgreSQL triggers and functions
- **Row-level Security**: User data protection
- **Indexing Strategy**: Optimized query performance

## API Documentation

### Weekly Recap Endpoints:

#### Generate Weekly Recap
```http
POST /api/newsletter/generate-weekly-recap
Content-Type: application/json

{
  "include_macro": true,
  "include_sectors": true,
  "include_top_movers": true,
  "language": "en"
}
```

#### Preview Weekly Recap
```http
GET /api/newsletter/weekly-recap/preview?language=en
```

### Sentiment Voting Endpoints:

#### Vote on Stock
```http
POST /api/sentiment/vote
Authorization: Bearer <token>
Content-Type: application/json

{
  "ticker": "ATW",
  "sentiment": "bullish",
  "confidence": 4
}
```

#### Get Aggregate Sentiment
```http
GET /api/sentiment/aggregate/ATW
```

#### Get Top Sentiment Stocks
```http
GET /api/sentiment/top-sentiment?sentiment_type=bullish&limit=10
```

## Security Considerations

### Authentication:
- JWT token-based authentication
- Supabase Auth integration
- Row-level security policies

### Data Protection:
- User data encryption
- GDPR compliance
- Privacy policy integration

### Rate Limiting:
- API rate limiting
- Vote frequency restrictions
- Newsletter subscription limits

## Performance Optimization

### Database:
- Efficient indexing strategy
- Query optimization
- Connection pooling

### Caching:
- Redis caching for market data
- CDN for static assets
- Browser caching strategies

### Mobile:
- Background refresh optimization
- Battery usage optimization
- Offline data caching

## Monitoring and Analytics

### Metrics Tracked:
- Widget usage statistics
- Sentiment voting patterns
- Newsletter engagement rates
- API performance metrics

### Error Handling:
- Graceful degradation
- Fallback content
- Error logging and monitoring

## Future Enhancements

### Planned Features:
1. **Advanced Widgets**: Chart widgets, news widgets
2. **Social Features**: Share sentiment predictions
3. **AI Insights**: Personalized market insights
4. **Push Notifications**: Widget-based alerts
5. **Customization**: User-defined widget layouts

### Technical Improvements:
1. **Offline Support**: Enhanced offline functionality
2. **Performance**: Further optimization
3. **Accessibility**: WCAG compliance
4. **Internationalization**: Additional languages

## Deployment Notes

### Environment Variables:
```bash
OPENAI_API_KEY=your_openai_key
DATABASE_URL=your_database_url
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
```

### Dependencies:
- Backend: See `apps/backend/requirements.txt`
- Web: See `apps/web/package.json`
- Mobile: See `apps/mobile/package.json`

### Build Commands:
```bash
# Backend
cd apps/backend && pip install -r requirements.txt

# Web
cd apps/web && npm install && npm run build

# Mobile
cd apps/mobile && npm install && expo build
```

## Conclusion

The implementation of these three advanced features significantly enhances the Casablanca Insight platform by:

1. **Increasing User Engagement**: Weekly newsletters and mobile widgets keep users informed
2. **Building Community**: Sentiment voting creates a collaborative investment community
3. **Improving User Experience**: Mobile widgets provide quick access to key information
4. **Enhancing Analytics**: Community sentiment provides valuable market insights

All features are production-ready with proper error handling, security measures, and performance optimizations. 