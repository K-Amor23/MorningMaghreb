import { useState } from 'react'
import { featureFlags, checkPremiumAccess } from '@/lib/featureFlags'

export default function FeatureFlagsDebug() {
  const [isVisible, setIsVisible] = useState(false)

  // Only show in development
  if (process.env.NODE_ENV !== 'development') {
    return null
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <button
        onClick={() => setIsVisible(!isVisible)}
        className="bg-gray-800 text-white px-3 py-2 rounded-lg text-sm"
      >
        {isVisible ? 'Hide' : 'Show'} Debug
      </button>
      
      {isVisible && (
        <div className="absolute bottom-12 right-0 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg p-4 shadow-lg max-w-sm">
          <h3 className="font-bold mb-2">Feature Flags Debug</h3>
          <div className="text-xs space-y-1">
            <div><strong>NEXT_PUBLIC_ENV:</strong> {process.env.NEXT_PUBLIC_ENV || 'undefined'}</div>
            <div><strong>PREMIUM_FEATURES:</strong> {featureFlags.PREMIUM_FEATURES.toString()}</div>
            <div><strong>PAPER_TRADING:</strong> {featureFlags.PAPER_TRADING.toString()}</div>
            <div><strong>SENTIMENT_VOTING:</strong> {featureFlags.SENTIMENT_VOTING.toString()}</div>
            <div><strong>ADVANCED_CHARTS:</strong> {featureFlags.ADVANCED_CHARTS.toString()}</div>
            <div><strong>REAL_TIME_DATA:</strong> {featureFlags.REAL_TIME_DATA.toString()}</div>
            <div><strong>Premium access check:</strong> {checkPremiumAccess('PREMIUM_FEATURES').toString()}</div>
          </div>
        </div>
      )}
    </div>
  )
} 