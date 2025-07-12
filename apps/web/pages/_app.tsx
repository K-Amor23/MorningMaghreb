import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import { useEffect } from 'react'
import { Toaster } from 'react-hot-toast'
import { SWRConfig } from 'swr'
import { supabase } from '@/lib/supabase'
import { ThemeProvider } from '@/lib/theme'
import { swrConfig } from '@/lib/swr'
import KeyboardShortcuts from '@/components/KeyboardShortcuts'
import '@/lib/i18n'
import FeatureFlagsDebug from '@/components/FeatureFlagsDebug'

export default function App({ Component, pageProps }: AppProps) {
  useEffect(() => {
    // Only set up auth listener if Supabase is configured
    if (supabase) {
      // Set up Supabase auth state listener
      const {
        data: { subscription },
      } = supabase.auth.onAuthStateChange(async (event, session) => {
        if (event === 'SIGNED_IN') {
          console.log('User signed in:', session?.user?.email)
        } else if (event === 'SIGNED_OUT') {
          console.log('User signed out')
        }
      })

      return () => subscription.unsubscribe()
    }
  }, [])

  return (
    <SWRConfig value={swrConfig}>
      <ThemeProvider>
        <Component {...pageProps} />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
        <KeyboardShortcuts />
        <FeatureFlagsDebug />
      </ThemeProvider>
    </SWRConfig>
  )
}