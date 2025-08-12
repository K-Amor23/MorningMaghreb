import { useState, useEffect } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { supabase } from './supabase'

interface Profile {
  id: string
  full_name?: string
  avatar_url?: string
  tier?: string
  language_preference?: string
  newsletter_frequency?: string
  preferences?: {
    theme?: string
    notifications?: boolean
    email_alerts?: boolean
  }
  created_at: string
  updated_at: string
}

interface Dashboard {
  total_portfolio_value: number
  total_gain_loss: number
  gain_loss_percentage: number
  total_positions: number
  watchlist_count: number
  active_alerts_count?: number
}

interface UseUserReturn {
  user: User | null
  profile: Profile | null
  dashboard: Dashboard | null
  loading: boolean
  error: string | null
  signOut: () => Promise<void>
  updateProfile: (updates: Partial<Profile>) => Promise<void>
}

export function useUser(): UseUserReturn {
  const [user, setUser] = useState<User | null>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [dashboard, setDashboard] = useState<Dashboard | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Get initial session
    const getInitialSession = async () => {
      try {
        if (!supabase) {
          console.error('Supabase is not configured')
          setError('Supabase is not configured')
          setLoading(false)
          return
        }

        const { data: { session }, error } = await supabase.auth.getSession()
        if (error) {
          console.error('Error getting session:', error)
          setError(error.message)
        } else {
          setUser(session?.user ?? null)
          if (session?.user) {
            await fetchProfile(session.user.id)
            await fetchDashboard(session.user.id)
          }
        }
      } catch (err) {
        console.error('Error in getInitialSession:', err)
        setError('Failed to get session')
      } finally {
        setLoading(false)
      }
    }

    getInitialSession()

    // Listen for auth changes
    if (!supabase) {
      console.error('Supabase is not configured')
      setLoading(false)
      return
    }

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        setUser(session?.user ?? null)
        if (session?.user) {
          await fetchProfile(session.user.id)
          await fetchDashboard(session.user.id)
        } else {
          setProfile(null)
          setDashboard(null)
        }
        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  const fetchProfile = async (userId: string) => {
    try {
      if (!supabase) {
        console.error('Supabase is not configured')
        return
      }

      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single()

      if (error) {
        console.error('Error fetching profile:', error)
        // Create profile if it doesn't exist
        if (error.code === 'PGRST116') {
          await createProfile(userId)
        }
      } else {
        setProfile(data)
      }
    } catch (err) {
      console.error('Error in fetchProfile:', err)
    }
  }

  const fetchDashboard = async (userId: string) => {
    try {
      // This would typically fetch from a dashboard table or calculate from other tables
      // For now, return mock data
      setDashboard({
        total_portfolio_value: 0,
        total_gain_loss: 0,
        gain_loss_percentage: 0,
        total_positions: 0,
        watchlist_count: 0
      })
    } catch (err) {
      console.error('Error in fetchDashboard:', err)
    }
  }

  const createProfile = async (userId: string) => {
    try {
      if (!supabase) {
        console.error('Supabase is not configured')
        return
      }

      const { data, error } = await supabase
        .from('profiles')
        .insert([
          {
            id: userId,
            full_name: user?.user_metadata?.full_name || '',
            avatar_url: user?.user_metadata?.avatar_url || '',
            tier: 'free'
          }
        ])
        .select()
        .single()

      if (error) {
        console.error('Error creating profile:', error)
      } else {
        setProfile(data)
      }
    } catch (err) {
      console.error('Error in createProfile:', err)
    }
  }

  const signOut = async () => {
    try {
      if (!supabase) {
        console.error('Supabase is not configured')
        setError('Supabase is not configured')
        return
      }

      const { error } = await supabase.auth.signOut()
      if (error) {
        console.error('Error signing out:', error)
        setError(error.message)
      }
    } catch (err) {
      console.error('Error in signOut:', err)
      setError('Failed to sign out')
    }
  }

  const updateProfile = async (updates: Partial<Profile>) => {
    if (!user) return

    try {
      if (!supabase) {
        console.error('Supabase is not configured')
        setError('Supabase is not configured')
        return
      }

      const { data, error } = await supabase
        .from('profiles')
        .update(updates)
        .eq('id', user.id)
        .select()
        .single()

      if (error) {
        console.error('Error updating profile:', error)
        setError(error.message)
      } else {
        setProfile(data)
      }
    } catch (err) {
      console.error('Error in updateProfile:', err)
      setError('Failed to update profile')
    }
  }

  return {
    user,
    profile,
    dashboard,
    loading,
    error,
    signOut,
    updateProfile
  }
}

// Hook for checking pro access
export function useProAccess() {
  const { profile } = useUser()
  return {
    isPro: profile?.tier === 'pro' || profile?.tier === 'admin',
    isAdmin: profile?.tier === 'admin'
  }
} 