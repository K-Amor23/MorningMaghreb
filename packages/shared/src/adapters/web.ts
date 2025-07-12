import { BaseApiService } from '../services/api'

// This will be provided by the consuming app
export interface SupabaseClient {
  auth: {
    getSession: () => Promise<{ data: { session: { access_token: string } | null } }>
  }
}

export class WebApiService extends BaseApiService {
  constructor(supabase: SupabaseClient) {
    super('/api', async () => {
      if (!supabase) {
        throw new Error('Supabase client not configured')
      }
      const { data: { session } } = await supabase.auth.getSession()
      return {
        'Authorization': `Bearer ${session?.access_token}`,
        'Content-Type': 'application/json',
      }
    })
  }
} 