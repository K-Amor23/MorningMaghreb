import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

// Check if we have valid credentials
const hasValidCredentials = supabaseUrl &&
  supabaseAnonKey &&
  supabaseUrl !== 'your_supabase_url' &&
  supabaseAnonKey !== 'your_supabase_anon_key' &&
  !supabaseAnonKey.includes('YOUR_NEW')

export const supabase = hasValidCredentials
  ? createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: true
    }
  })
  : null

export const isSupabaseConfigured = () => {
  return hasValidCredentials
}

// Helper function to check if Supabase is available
export const isSupabaseAvailable = () => {
  return supabase !== null
}

// Helper function to get Supabase client with error handling
export const getSupabaseClient = () => {
  if (!supabase) {
    throw new Error('Supabase is not configured. Please check your environment variables.')
  }
  return supabase
}

// Re-export MarketQuote type for compatibility
export type { MarketQuote } from './marketData' 