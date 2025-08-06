import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import { useEffect, useState } from 'react'
import { Toaster } from 'react-hot-toast'
import { SWRConfig } from 'swr'
import { supabase } from '@/lib/supabase'
import { ThemeProvider } from '@/lib/theme'
import { swrConfig } from '@/lib/swr'
import KeyboardShortcuts from '@/components/KeyboardShortcuts'
import PWAInstaller from '@/components/PWAInstaller'
import '@/lib/i18n'
import FeatureFlagsDebug from '@/components/FeatureFlagsDebug'
import { SpeedInsights } from '@vercel/speed-insights/next'
import { Analytics } from '@vercel/analytics/next'
import PasswordProtection from '@/components/PasswordProtection'
import { isPasswordProtectionEnabled, getCorrectPassword } from '@/lib/passwordConfig'

export default function App({ Component, pageProps }: AppProps) {
  const [accessGranted, setAccessGranted] = useState(false)

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

  const handleAccessGranted = () => {
    setAccessGranted(true)
  }

  const appContent = (
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
        <PWAInstaller />
        <FeatureFlagsDebug />
        <SpeedInsights />
        <Analytics />
      </ThemeProvider>
    </SWRConfig>
  )

  // If password protection is disabled, render normally
  if (!isPasswordProtectionEnabled()) {
    return appContent
  }

  // If password protection is enabled, wrap with PasswordProtection
  return (
    <PasswordProtection
      correctPassword={getCorrectPassword()}
      onAccessGranted={handleAccessGranted}
    >
      {appContent}
    </PasswordProtection>
  )
}