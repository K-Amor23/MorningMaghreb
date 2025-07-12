import { BaseApiService } from '@casablanca-insight/shared'
import AsyncStorage from '@react-native-async-storage/async-storage'

export class MobileApiService extends BaseApiService {
  constructor() {
    super(
      process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000',
      async () => {
        const token = await AsyncStorage.getItem('auth_token')
        return token 
          ? { 'Authorization': `Bearer ${token}` }
          : {} as Record<string, string>
      }
    )
  }

  // Override methods to provide mock data for development
  async getMarketData(): Promise<any[]> {
    try {
      // For now, return mock data. Replace with actual API call
      return [
        {
          symbol: 'MASI',
          name: 'Moroccan All Shares Index',
          price: 12456.78,
          change: 45.23,
          changePercent: 0.36,
          volume: 2300000000,
        },
        {
          symbol: 'MADEX',
          name: 'Most Active Shares Index',
          price: 10234.56,
          change: -23.45,
          changePercent: -0.23,
          volume: 1800000000,
        },
        {
          symbol: 'ATW',
          name: 'Attijariwafa Bank',
          price: 45.60,
          change: 0.85,
          changePercent: 1.90,
          volume: 234000000,
        },
        {
          symbol: 'BMCE',
          name: 'BMCE Bank',
          price: 23.45,
          change: -0.32,
          changePercent: -1.35,
          volume: 123000000,
        },
        {
          symbol: 'CIH',
          name: 'CIH Bank',
          price: 34.20,
          change: 0.45,
          changePercent: 1.33,
          volume: 156000000,
        },
      ]
    } catch (error) {
      console.error('Error fetching market data:', error)
      return []
    }
  }

  async getMacroData(): Promise<any[]> {
    try {
      return [
        {
          indicator: 'BAM Policy Rate',
          value: '3.00%',
          change: '0.00%',
          description: 'Bank Al-Maghrib benchmark rate',
        },
        {
          indicator: 'FX Reserves',
          value: '$34.2B',
          change: '+$0.8B',
          description: 'Foreign exchange reserves',
        },
        {
          indicator: 'Inflation Rate',
          value: '2.8%',
          change: '-0.1%',
          description: 'Consumer price index YoY',
        },
        {
          indicator: 'Trade Balance',
          value: '-$2.1B',
          change: '-$0.3B',
          description: 'Monthly trade deficit',
        },
      ]
    } catch (error) {
      console.error('Error fetching macro data:', error)
      return []
    }
  }

  async getNews(): Promise<any[]> {
    try {
      return [
        {
          id: '1',
          title: 'MASI Gains 0.36% on Banking Sector Strength',
          excerpt: 'The Moroccan All Shares Index closed higher today, led by strong performance in the banking sector.',
          category: 'market',
          publishedAt: '2 hours ago',
          readTime: '3 min read',
        },
        {
          id: '2',
          title: 'Bank Al-Maghrib Maintains 3% Policy Rate',
          excerpt: 'The central bank kept its benchmark interest rate unchanged at 3% for the third consecutive meeting.',
          category: 'economic',
          publishedAt: '4 hours ago',
          readTime: '2 min read',
        },
        {
          id: '3',
          title: 'Attijariwafa Bank Reports Q3 Earnings Beat',
          excerpt: 'Morocco\'s largest bank reported quarterly earnings of 2.8 billion MAD, exceeding analyst expectations.',
          category: 'company',
          publishedAt: '6 hours ago',
          readTime: '4 min read',
        },
        {
          id: '4',
          title: 'New ESG Reporting Requirements Announced',
          excerpt: 'The Moroccan Capital Market Authority introduced new mandatory ESG reporting standards.',
          category: 'regulatory',
          publishedAt: '1 day ago',
          readTime: '3 min read',
        },
      ]
    } catch (error) {
      console.error('Error fetching news:', error)
      return []
    }
  }
}

export const apiService = new MobileApiService() 