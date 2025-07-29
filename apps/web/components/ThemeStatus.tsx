import React from 'react'
import { useTheme } from '@/lib/theme'
import { useClientOnly } from '@/lib/useClientOnly'

export default function ThemeStatus() {
  const { theme } = useTheme()
  const mounted = useClientOnly()

  if (!mounted) {
    // Return a placeholder during SSR to prevent hydration mismatch
    return (
      <div className="text-sm text-gray-500 dark:text-gray-400">
        Theme: Loading...
      </div>
    )
  }

  return (
    <div className="text-sm text-gray-500 dark:text-gray-400">
      Theme: {theme === 'dark' ? 'Dark' : 'Light'}
    </div>
  )
} 