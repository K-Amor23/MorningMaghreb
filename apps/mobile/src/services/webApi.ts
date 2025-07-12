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
          : {}
      }
    )
  }
}

export const webApiService = new MobileApiService() 