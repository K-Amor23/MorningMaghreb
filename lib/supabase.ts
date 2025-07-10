import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Types for database tables
export interface User {
  id: string
  email: string
  created_at: string
  subscription_tier: 'free' | 'pro'
  preferences: {
    language: 'en' | 'fr' | 'ar'
    newsletter_time: string
    watchlist: string[]
  }
}

export interface Subscription {
  id: string
  user_id: string
  stripe_customer_id: string
  stripe_subscription_id: string
  status: 'active' | 'canceled' | 'past_due'
  current_period_start: string
  current_period_end: string
  plan: 'free' | 'pro'
}

export interface MarketQuote {
  ticker: string
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  change: number
  change_percent: number
}

export interface FinancialReport {
  id: string
  ticker: string
  period: string
  report_type: 'quarterly' | 'annual'
  ifrs_data: any
  gaap_data: any
  created_at: string
}

export interface Portfolio {
  id: string
  user_id: string
  name: string
  holdings: PortfolioHolding[]
  created_at: string
  updated_at: string
}

export interface PortfolioHolding {
  ticker: string
  quantity: number
  purchase_price: number
  purchase_date: string
  current_price?: number
  current_value?: number
  unrealized_pnl?: number
}