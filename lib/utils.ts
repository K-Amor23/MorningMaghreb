import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(value: number, currency: 'MAD' | 'USD' = 'MAD'): string {
  const symbol = currency === 'MAD' ? 'MAD' : '$'
  return new Intl.NumberFormat('en-US', {
    style: 'decimal',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value) + ` ${symbol}`
}

export function formatPercent(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value / 100)
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value)
}

export function calculatePercentChange(current: number, previous: number): number {
  if (previous === 0) return 0
  return ((current - previous) / previous) * 100
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(date))
}

export function formatDateTime(date: string | Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date))
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
}

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function generateRandomId(): string {
  return Math.random().toString(36).substr(2, 9)
}

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

export function getColorForChange(change: number): string {
  if (change > 0) return 'text-green-600'
  if (change < 0) return 'text-red-600'
  return 'text-gray-600'
}

export function getBackgroundColorForChange(change: number): string {
  if (change > 0) return 'bg-green-50'
  if (change < 0) return 'bg-red-50'
  return 'bg-gray-50'
}

// Financial calculations
export function calculateSharpeRatio(
  returns: number[],
  riskFreeRate: number = 0.02
): number {
  if (returns.length === 0) return 0
  
  const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length
  const excessReturns = returns.map(r => r - riskFreeRate / 252) // daily risk-free rate
  const volatility = calculateVolatility(excessReturns)
  
  return volatility === 0 ? 0 : (avgReturn - riskFreeRate / 252) / volatility
}

export function calculateVolatility(returns: number[]): number {
  if (returns.length < 2) return 0
  
  const mean = returns.reduce((sum, r) => sum + r, 0) / returns.length
  const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / (returns.length - 1)
  
  return Math.sqrt(variance)
}

export function calculateBeta(
  assetReturns: number[],
  marketReturns: number[]
): number {
  if (assetReturns.length !== marketReturns.length || assetReturns.length < 2) {
    return 1 // Default beta
  }
  
  const assetMean = assetReturns.reduce((sum, r) => sum + r, 0) / assetReturns.length
  const marketMean = marketReturns.reduce((sum, r) => sum + r, 0) / marketReturns.length
  
  let covariance = 0
  let marketVariance = 0
  
  for (let i = 0; i < assetReturns.length; i++) {
    const assetDiff = assetReturns[i] - assetMean
    const marketDiff = marketReturns[i] - marketMean
    covariance += assetDiff * marketDiff
    marketVariance += marketDiff * marketDiff
  }
  
  covariance /= assetReturns.length - 1
  marketVariance /= marketReturns.length - 1
  
  return marketVariance === 0 ? 1 : covariance / marketVariance
}