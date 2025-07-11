'use client'

import { useTheme } from '@/lib/theme'

export default function ThemeStatus() {
  const { theme } = useTheme()

  return (
    <div className="fixed bottom-4 right-4 bg-white dark:bg-dark-card p-2 rounded-lg shadow-lg text-xs text-gray-600 dark:text-dark-text-secondary">
      Theme: {theme}
    </div>
  )
} 