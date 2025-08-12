import React, { createContext, useContext, useEffect, useState } from 'react'
import { useLocalStorage, useMediaQuery } from './useClientOnly'

type Theme = 'light' | 'dark'

interface ThemeContextType {
  theme: Theme
  toggleTheme: () => void
  setTheme: (theme: Theme) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [storedTheme, setStoredTheme] = useLocalStorage<Theme>('theme', 'light')
  const prefersDark = useMediaQuery('(prefers-color-scheme: dark)')
  const [theme, setThemeState] = useState<Theme>('light')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return

    // Use stored theme if available, otherwise use system preference
    const initialTheme = storedTheme || (prefersDark ? 'dark' : 'light')
    setThemeState(initialTheme)
  }, [storedTheme, prefersDark, mounted])

  useEffect(() => {
    if (!mounted) return
    // Update document class when theme changes
    document.documentElement.classList.remove('light', 'dark')
    document.documentElement.classList.add(theme)
    setStoredTheme(theme)
  }, [theme, mounted, setStoredTheme])

  const toggleTheme = () => {
    setThemeState((prev) => prev === 'light' ? 'dark' : 'light')
  }

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme)
  }

  // Prevent hydration mismatch by not rendering theme-dependent content until mounted
  if (!mounted) {
    return <>{children}</>
  }

  return React.createElement(
    ThemeContext.Provider,
    { value: { theme, toggleTheme, setTheme } },
    children
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)

  // During SSR or when context is not available, return default values
  if (context === undefined) {
    return {
      theme: 'light' as Theme,
      toggleTheme: () => { },
      setTheme: () => { }
    }
  }

  return context
} 