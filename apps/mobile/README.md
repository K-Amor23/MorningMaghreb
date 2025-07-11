# Casablanca Insight Mobile App

A React Native mobile application for Morocco market research and analytics, built with Expo.

## 📱 Features

### 🏠 Home Dashboard
- **MASI Index Overview** - Real-time Casablanca Stock Exchange main index
- **Top Movers** - Daily gainers and losers
- **Macro Indicators** - BAM policy rate, FX reserves, inflation, trade balance
- **Latest News** - Curated financial news with AI insights
- **Newsletter Signup** - Morning Maghreb daily digest

### 📈 Markets
- **Market Overview** - MASI, MADEX, and major stocks
- **Sector Performance** - Banking, Insurance, Real Estate, etc.
- **Market Statistics** - Volume, market cap, advancers/decliners
- **Trading Volume** - Real-time volume data (coming soon)

### 📰 News & Insights
- **Category Filtering** - Markets, Companies, Economy, Regulation, etc.
- **AI Market Insights** - Sentiment analysis, top sectors, risk levels
- **Trending Topics** - Popular hashtags and discussions
- **Featured Stories** - Curated content with read time estimates

### ⚙️ Settings
- **User Authentication** - Supabase Auth integration
- **Notification Preferences** - Push alerts, market alerts, newsletter
- **Language Support** - English, Arabic, French
- **Data & Privacy** - Export, privacy policy, terms of service
- **Account Management** - Sign out, delete account

## 🛠️ Tech Stack

- **Framework**: React Native with Expo SDK 50+
- **Navigation**: React Navigation v6
- **State Management**: Zustand with persistence
- **Styling**: React Native StyleSheet (NativeWind ready)
- **Authentication**: Supabase Auth
- **API**: RESTful API with FastAPI backend
- **Storage**: AsyncStorage for local data
- **Charts**: Victory Native (coming soon)

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Expo CLI: `npm install -g @expo/cli`
- Expo Go app on your phone (for testing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/casablanca-insight.git
   cd casablanca-insight/apps/mobile
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment Setup**
   Create a `.env` file in the mobile app directory:
   ```env
   EXPO_PUBLIC_SUPABASE_URL=your_supabase_url
   EXPO_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   EXPO_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Start the development server**
   ```bash
   npm start
   ```

5. **Run on device**
   - Install Expo Go on your phone
   - Scan the QR code from the terminal
   - Or press 'i' for iOS simulator, 'a' for Android emulator

## 📱 Development

### Project Structure

```
src/
├── screens/          # Main app screens
│   ├── HomeScreen.tsx
│   ├── MarketsScreen.tsx
│   ├── NewsScreen.tsx
│   └── SettingsScreen.tsx
├── components/       # Reusable components
├── services/         # API and external services
│   ├── api.ts
│   └── supabase.ts
├── store/           # State management
│   └── useStore.ts
├── hooks/           # Custom React hooks
└── types/           # TypeScript type definitions
```

### Key Components

#### State Management (Zustand)
```typescript
// Store with persistence
export const useStore = create<AppState>()(
  persist(
    (set, get) => ({
      // State and actions
    }),
    {
      name: 'casablanca-insight-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
)
```

#### API Service
```typescript
// Centralized API calls
class ApiService {
  async getMarketData(): Promise<MarketData[]>
  async getMacroData(): Promise<MacroData[]>
  async getNews(): Promise<NewsItem[]>
  async signupNewsletter(email: string): Promise<Response>
}
```

### Styling

The app uses React Native StyleSheet for styling, with a consistent design system:

- **Colors**: Morocco-inspired palette (red, green, gold, blue)
- **Typography**: System fonts with consistent sizing
- **Spacing**: 8px grid system
- **Components**: Card-based layout with shadows

### Navigation

Bottom tab navigation with 4 main sections:
- 🏠 Home - Dashboard and overview
- 📈 Markets - Detailed market data
- 📰 News - Financial news and insights
- ⚙️ Settings - User preferences and account

## 🧪 Testing

### Unit Tests
```bash
npm test
```

### E2E Tests (coming soon)
```bash
npm run test:e2e
```

## 📦 Building for Production

### iOS
```bash
# Install EAS CLI
npm install -g @expo/eas-cli

# Build for iOS
eas build --platform ios
```

### Android
```bash
# Build for Android
eas build --platform android
```

### OTA Updates
```bash
# Deploy update
eas update --branch production
```

## 🔧 Configuration

### Expo Configuration
- **SDK Version**: 50+
- **Platforms**: iOS, Android
- **Permissions**: Camera (for QR scanning), Notifications
- **Plugins**: Safe Area, Async Storage, Notifications

### Environment Variables
- `EXPO_PUBLIC_SUPABASE_URL` - Supabase project URL
- `EXPO_PUBLIC_SUPABASE_ANON_KEY` - Supabase anonymous key
- `EXPO_PUBLIC_API_URL` - Backend API URL

## 🚀 Deployment

### Expo Application Services (EAS)

1. **Setup EAS**
   ```bash
   eas login
   eas build:configure
   ```

2. **Build for stores**
   ```bash
   eas build --platform all
   ```

3. **Submit to stores**
   ```bash
   eas submit --platform ios
   eas submit --platform android
   ```

### App Store Requirements

- **iOS**: Apple Developer Account ($99/year)
- **Android**: Google Play Developer Account ($25 one-time)
- **Icons**: 1024x1024 app icon
- **Screenshots**: Device-specific screenshots
- **Privacy Policy**: Required for data collection

## 🔐 Security

- **Authentication**: JWT tokens via Supabase
- **API Security**: HTTPS only, rate limiting
- **Data Storage**: Encrypted AsyncStorage
- **Network Security**: Certificate pinning (coming soon)

## 📊 Analytics

- **User Engagement**: Screen views, feature usage
- **Performance**: App load times, API response times
- **Crash Reporting**: Error tracking and monitoring
- **A/B Testing**: Feature flags for gradual rollouts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style

- **TypeScript**: Strict mode enabled
- **ESLint**: Airbnb configuration
- **Prettier**: Code formatting
- **Husky**: Pre-commit hooks

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: [docs.casablancainsight.com](https://docs.casablancainsight.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/casablanca-insight/issues)
- **Discord**: [Community Server](https://discord.gg/casablancainsight)

## 🔮 Roadmap

### Phase 2 (Q2 2024)
- [ ] Push notifications
- [ ] Portfolio tracking
- [ ] Watchlist management
- [ ] Real-time price alerts
- [ ] Advanced charts with Victory Native

### Phase 3 (Q3 2024)
- [ ] Offline support
- [ ] Dark mode
- [ ] Biometric authentication
- [ ] Widget support
- [ ] Apple Watch companion app

### Phase 4 (Q4 2024)
- [ ] AI-powered insights
- [ ] Social features
- [ ] Advanced analytics
- [ ] Multi-language support
- [ ] Accessibility improvements 