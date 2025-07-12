import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import { KEYBOARD_SHORTCUTS } from '@/lib/accessibility'

interface KeyboardShortcutsProps {
  onSearch?: () => void
  onThemeToggle?: () => void
}

export default function KeyboardShortcuts({ onSearch, onThemeToggle }: KeyboardShortcutsProps) {
  const router = useRouter()
  const [showHelp, setShowHelp] = useState(false)

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in input fields
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return
      }

      // Ctrl+K or Cmd+K for search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        onSearch?.()
        return
      }

      // Alt+H for home
      if (e.altKey && e.key === 'h') {
        e.preventDefault()
        router.push('/')
        return
      }

      // Alt+M for markets
      if (e.altKey && e.key === 'm') {
        e.preventDefault()
        router.push('/markets')
        return
      }

      // Alt+P for portfolio
      if (e.altKey && e.key === 'p') {
        e.preventDefault()
        router.push('/portfolio')
        return
      }

      // Alt+N for news
      if (e.altKey && e.key === 'n') {
        e.preventDefault()
        router.push('/news')
        return
      }

      // Alt+T for theme toggle
      if (e.altKey && e.key === 't') {
        e.preventDefault()
        onThemeToggle?.()
        return
      }

      // ? for help
      if (e.key === '?') {
        e.preventDefault()
        setShowHelp(!showHelp)
        return
      }

      // Escape to close help
      if (e.key === 'Escape' && showHelp) {
        setShowHelp(false)
        return
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [router, onSearch, onThemeToggle, showHelp])

  if (!showHelp) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Keyboard Shortcuts
          </h2>
          <button
            onClick={() => setShowHelp(false)}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            aria-label="Close keyboard shortcuts help"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div className="p-6">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-700 dark:text-gray-300">Search</span>
              <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600">
                {navigator.platform.includes('Mac') ? '⌘' : 'Ctrl'}+K
              </kbd>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-700 dark:text-gray-300">Navigate Home</span>
              <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600">
                Alt+H
              </kbd>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-700 dark:text-gray-300">Navigate Markets</span>
              <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600">
                Alt+M
              </kbd>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-700 dark:text-gray-300">Navigate Portfolio</span>
              <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600">
                Alt+P
              </kbd>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-700 dark:text-gray-300">Navigate News</span>
              <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600">
                Alt+N
              </kbd>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-700 dark:text-gray-300">Toggle Theme</span>
              <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600">
                Alt+T
              </kbd>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-700 dark:text-gray-300">Show/Hide Help</span>
              <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600">
                ?
              </kbd>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-700 dark:text-gray-300">Close Modal</span>
              <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600">
                Esc
              </kbd>
            </div>
          </div>
          
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Press <kbd className="px-1 py-0.5 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600">?</kbd> anytime to show this help.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
} 