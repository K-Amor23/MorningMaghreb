// Formatting utilities
export const formatCurrency = (amount: number, currency: string = 'MAD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

export const formatPercentage = (value: number, decimals: number = 2): string => {
  return `${value >= 0 ? '+' : ''}${value.toFixed(decimals)}%`
}

export const formatNumber = (value: number, decimals: number = 2): string => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

export const formatVolume = (volume: number): string => {
  if (volume >= 1e9) {
    return `${(volume / 1e9).toFixed(2)}B`
  } else if (volume >= 1e6) {
    return `${(volume / 1e6).toFixed(2)}M`
  } else if (volume >= 1e3) {
    return `${(volume / 1e3).toFixed(2)}K`
  }
  return volume.toString()
}

// Date utilities
export const formatDate = (date: string | Date): string => {
  const d = new Date(date)
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export const formatDateTime = (date: string | Date): string => {
  const d = new Date(date)
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export const getRelativeTime = (date: string | Date): string => {
  const now = new Date()
  const past = new Date(date)
  const diffInSeconds = Math.floor((now.getTime() - past.getTime()) / 1000)

  if (diffInSeconds < 60) {
    return 'Just now'
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60)
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600)
    return `${hours} hour${hours > 1 ? 's' : ''} ago`
  } else if (diffInSeconds < 2592000) {
    const days = Math.floor(diffInSeconds / 86400)
    return `${days} day${days > 1 ? 's' : ''} ago`
  } else {
    return formatDate(date)
  }
}

// Color utilities
export const getChangeColor = (change: number): string => {
  if (change > 0) return 'text-green-600'
  if (change < 0) return 'text-red-600'
  return 'text-gray-600'
}

export const getSentimentColor = (sentiment: string): string => {
  switch (sentiment) {
    case 'bullish':
      return 'text-green-600'
    case 'neutral':
      return 'text-gray-600'
    case 'bearish':
      return 'text-red-600'
    default:
      return 'text-gray-600'
  }
}

// Validation utilities
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export const isValidTicker = (ticker: string): boolean => {
  return /^[A-Z]{1,5}$/.test(ticker)
}

// Calculation utilities
export const calculateGainLoss = (currentPrice: number, purchasePrice: number, quantity: number) => {
  const totalGainLoss = (currentPrice - purchasePrice) * quantity
  const totalGainLossPercent = ((currentPrice - purchasePrice) / purchasePrice) * 100
  return { totalGainLoss, totalGainLossPercent }
}

export const calculatePortfolioValue = (holdings: Array<{ quantity: number; current_price?: number }>) => {
  return holdings.reduce((total, holding) => {
    return total + (holding.quantity * (holding.current_price || 0))
  }, 0)
}

// Storage utilities
export const storage = {
  get: (key: string): any => {
    if (typeof window === 'undefined') return null
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : null
    } catch {
      return null
    }
  },
  
  set: (key: string, value: any): void => {
    if (typeof window === 'undefined') return
    try {
      localStorage.setItem(key, JSON.stringify(value))
    } catch {
      // Ignore storage errors
    }
  },
  
  remove: (key: string): void => {
    if (typeof window === 'undefined') return
    try {
      localStorage.removeItem(key)
    } catch {
      // Ignore storage errors
    }
  }
}

// Feature flag utilities
export const isFeatureEnabled = (feature: string, flags: Record<string, boolean>): boolean => {
  return flags[feature] || false
}

// Error handling utilities
export const handleApiError = (error: any): string => {
  if (error.response?.data?.detail) {
    return error.response.data.detail
  }
  if (error.message) {
    return error.message
  }
  return 'An unexpected error occurred'
}

// Debounce utility
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

// Throttle utility
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
} 