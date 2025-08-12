import { useState, useEffect } from 'react'

/**
 * Hook to ensure a component only renders on the client side
 * This prevents hydration mismatches when using browser-only APIs
 */
export function useClientOnly() {
    const [mounted, setMounted] = useState(false)

    useEffect(() => {
        setMounted(true)
    }, [])

    return mounted
}

/**
 * Hook to safely access localStorage with hydration protection
 */
export function useLocalStorage<T>(key: string, defaultValue: T) {
    const [value, setValue] = useState<T>(defaultValue)
    const [mounted, setMounted] = useState(false)

    useEffect(() => {
        setMounted(true)
    }, [])

    useEffect(() => {
        if (!mounted) return

        try {
            const item = localStorage.getItem(key)
            if (item !== null) {
                setValue(JSON.parse(item))
            }
        } catch (error) {
            console.error(`Error reading localStorage key "${key}":`, error)
        }
    }, [key, mounted])

    const setStoredValue = (newValue: T) => {
        if (!mounted) return

        try {
            setValue(newValue)
            localStorage.setItem(key, JSON.stringify(newValue))
        } catch (error) {
            console.error(`Error setting localStorage key "${key}":`, error)
        }
    }

    return [value, setStoredValue] as const
}

/**
 * Hook to safely access window.matchMedia with hydration protection
 */
export function useMediaQuery(query: string) {
    const [matches, setMatches] = useState(false)
    const [mounted, setMounted] = useState(false)

    useEffect(() => {
        setMounted(true)
    }, [])

    useEffect(() => {
        if (!mounted || typeof window === 'undefined') return

        const mediaQuery = window.matchMedia(query)
        setMatches(mediaQuery.matches)

        const handler = (event: MediaQueryListEvent) => {
            setMatches(event.matches)
        }

        mediaQuery.addEventListener('change', handler)
        return () => mediaQuery.removeEventListener('change', handler)
    }, [query, mounted])

    return matches
}

/**
 * Hook to safely access localStorage.getItem with hydration protection
 * Returns a function that can be called to get the value safely
 */
export function useLocalStorageGetter() {
    const [mounted, setMounted] = useState(false)

    useEffect(() => {
        setMounted(true)
    }, [])

    const getItem = (key: string): string | null => {
        if (!mounted || typeof window === 'undefined') return null

        try {
            return localStorage.getItem(key)
        } catch (error) {
            console.error(`Error reading localStorage key "${key}":`, error)
            return null
        }
    }

    return { getItem, mounted }
} 