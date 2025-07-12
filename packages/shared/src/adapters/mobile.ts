import { BaseApiService } from '../services/api'

export class MobileApiService extends BaseApiService {
  constructor(baseUrl: string = 'http://localhost:8000') {
    super(baseUrl, async () => {
      // For mobile, we'll need to implement token storage/retrieval
      // This is a placeholder - the actual implementation will depend on
      // how authentication is handled in the mobile app
      const token = await this.getStoredToken()
      return {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json',
      }
    })
  }

  private async getStoredToken(): Promise<string | null> {
    // This should be implemented by the mobile app
    // using AsyncStorage or similar
    return null
  }
} 