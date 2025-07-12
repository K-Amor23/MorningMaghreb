import React, { useState, useRef, useEffect } from 'react'
import { InformationCircleIcon } from '@heroicons/react/24/outline'

interface TooltipProps {
  content: string
  children?: React.ReactNode
  position?: 'top' | 'bottom' | 'left' | 'right'
  className?: string
  trigger?: 'hover' | 'click' | 'focus'
}

export default function Tooltip({ 
  content, 
  children, 
  position = 'top', 
  className = '',
  trigger = 'hover'
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 })
  const triggerRef = useRef<HTMLDivElement>(null)
  const tooltipRef = useRef<HTMLDivElement>(null)

  const showTooltip = () => setIsVisible(true)
  const hideTooltip = () => setIsVisible(false)

  const handleMouseEnter = () => {
    if (trigger === 'hover') showTooltip()
  }

  const handleMouseLeave = () => {
    if (trigger === 'hover') hideTooltip()
  }

  const handleClick = () => {
    if (trigger === 'click') {
      setIsVisible(!isVisible)
    }
  }

  const handleFocus = () => {
    if (trigger === 'focus') showTooltip()
  }

  const handleBlur = () => {
    if (trigger === 'focus') hideTooltip()
  }

  // Calculate tooltip position
  useEffect(() => {
    if (isVisible && triggerRef.current && tooltipRef.current) {
      const triggerRect = triggerRef.current.getBoundingClientRect()
      const tooltipRect = tooltipRef.current.getBoundingClientRect()
      
      let x = 0
      let y = 0

      switch (position) {
        case 'top':
          x = triggerRect.left + (triggerRect.width / 2) - (tooltipRect.width / 2)
          y = triggerRect.top - tooltipRect.height - 8
          break
        case 'bottom':
          x = triggerRect.left + (triggerRect.width / 2) - (tooltipRect.width / 2)
          y = triggerRect.bottom + 8
          break
        case 'left':
          x = triggerRect.left - tooltipRect.width - 8
          y = triggerRect.top + (triggerRect.height / 2) - (tooltipRect.height / 2)
          break
        case 'right':
          x = triggerRect.right + 8
          y = triggerRect.top + (triggerRect.height / 2) - (tooltipRect.height / 2)
          break
      }

      // Ensure tooltip stays within viewport
      const viewportWidth = window.innerWidth
      const viewportHeight = window.innerHeight

      if (x < 0) x = 8
      if (x + tooltipRect.width > viewportWidth) x = viewportWidth - tooltipRect.width - 8
      if (y < 0) y = 8
      if (y + tooltipRect.height > viewportHeight) y = viewportHeight - tooltipRect.height - 8

      setTooltipPosition({ x, y })
    }
  }, [isVisible, position])

  // Close tooltip on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isVisible) {
        hideTooltip()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isVisible])

  // Close tooltip when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (triggerRef.current && !triggerRef.current.contains(e.target as Node)) {
        hideTooltip()
      }
    }

    if (isVisible) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isVisible])

  return (
    <div className={`relative inline-block ${className}`}>
      <div
        ref={triggerRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
        onFocus={handleFocus}
        onBlur={handleBlur}
        className="inline-flex items-center"
        tabIndex={0}
        role="button"
        aria-describedby={isVisible ? 'tooltip' : undefined}
      >
        {children || <InformationCircleIcon className="h-4 w-4 text-gray-400" />}
      </div>

      {isVisible && (
        <div
          ref={tooltipRef}
          id="tooltip"
          role="tooltip"
          className={`absolute z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg max-w-xs ${position === 'top' ? 'bottom-full mb-2' : position === 'bottom' ? 'top-full mt-2' : position === 'left' ? 'right-full mr-2' : 'left-full ml-2'}`}
          style={{
            left: `${tooltipPosition.x}px`,
            top: `${tooltipPosition.y}px`,
          }}
        >
          {content}
          <div className={`absolute w-2 h-2 bg-gray-900 transform rotate-45 ${
            position === 'top' ? 'top-full -mt-1 left-1/2 -translate-x-1/2' :
            position === 'bottom' ? 'bottom-full -mb-1 left-1/2 -translate-x-1/2' :
            position === 'left' ? 'left-full -ml-1 top-1/2 -translate-y-1/2' :
            'right-full -mr-1 top-1/2 -translate-y-1/2'
          }`} />
        </div>
      )}
    </div>
  )
}

// Finance-specific tooltip components
export const FinanceTooltip = ({ term, children }: { term: string; children?: React.ReactNode }) => {
  const tooltipContent = {
    'P/E Ratio': 'Price-to-Earnings ratio measures a company\'s stock price relative to its earnings per share. A higher P/E suggests higher growth expectations.',
    'Market Cap': 'Market capitalization is the total value of a company\'s shares. It\'s calculated by multiplying the current stock price by the number of outstanding shares.',
    'Volume': 'Trading volume is the number of shares traded in a given period. Higher volume often indicates more active trading and liquidity.',
    'Beta': 'Beta measures a stock\'s volatility compared to the overall market. A beta of 1 means the stock moves with the market, while >1 means more volatile.',
    'Dividend Yield': 'Dividend yield is the annual dividend payment as a percentage of the current stock price. It shows how much a company pays out in dividends.',
    'ROE': 'Return on Equity measures how efficiently a company uses shareholders\' money to generate profits. Higher ROE generally indicates better performance.',
    'Debt-to-Equity': 'This ratio compares a company\'s total debt to its shareholders\' equity. Lower ratios generally indicate less financial risk.',
    'EPS': 'Earnings Per Share is the portion of a company\'s profit allocated to each outstanding share. It\'s a key measure of profitability.',
    'ROA': 'Return on Assets measures how efficiently a company uses its assets to generate earnings. Higher ROA indicates better asset utilization.',
    'Current Ratio': 'This liquidity ratio measures a company\'s ability to pay short-term obligations. A ratio above 1 indicates good short-term financial health.',
  }[term] || `Information about ${term}`

  return (
    <Tooltip content={tooltipContent} trigger="hover">
      {children}
    </Tooltip>
  )
} 