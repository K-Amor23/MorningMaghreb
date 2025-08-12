import React, { useState, useEffect } from 'react'

/**
 * Hook to prevent hydration mismatch by ensuring component only renders on client
 */
export function useClientOnly() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return mounted
}

/**
 * Hook to safely generate random values only on client side
 */
export function useRandomValue(initialValue: number, min: number, max: number) {
  const [value, setValue] = useState(initialValue)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (mounted) {
      setValue(initialValue + safeRandom(-(max - min) / 2, (max - min) / 2))
    }
  }, [mounted, initialValue, min, max])

  return mounted ? value : initialValue
}

/**
 * Hook to safely generate dates only on client side
 */
export function useClientDate(initialDate?: Date) {
  const [date, setDate] = useState(initialDate || new Date())
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    if (!initialDate) {
      setDate(new Date())
    }
  }, [initialDate])

  return mounted ? date : (initialDate || new Date())
}

/**
 * Component wrapper to prevent hydration mismatch
 */
export function ClientOnly({ children, fallback = null }: { children: React.ReactNode; fallback?: React.ReactNode }) {
  const mounted = useClientOnly()

  if (!mounted) {
    return <>{ fallback } </>
  }

  return <>{ children } </>
}

/**
 * Safe random number generator that only runs on client
 */
export function safeRandom(min: number = 0, max: number = 1): number {
  if (typeof window === 'undefined') {
    return min // Return minimum value during SSR
  }
  return min + (Math.random() * (max - min))
}

/**
 * Safe date formatter that handles SSR
 */
export function safeDateFormat(date: Date | string, options?: Intl.DateTimeFormatOptions): string {
  if (typeof window === 'undefined') {
    return new Date(date).toISOString() // Return ISO string during SSR
  }
  return new Date(date).toLocaleDateString('en-US', options)
}

/**
 * Safe time formatter that handles SSR
 */
export function safeTimeFormat(date: Date | string, options?: Intl.DateTimeFormatOptions): string {
  if (typeof window === 'undefined') {
    return new Date(date).toISOString() // Return ISO string during SSR
  }
  return new Date(date).toLocaleTimeString('en-US', options)
} 