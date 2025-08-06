import { useState, useEffect } from 'react'
import { LockClosedIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'

interface PasswordProtectionProps {
  children: React.ReactNode
  correctPassword: string
  onAccessGranted: () => void
}

export default function PasswordProtection({ 
  children, 
  correctPassword, 
  onAccessGranted 
}: PasswordProtectionProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Check if user is already authenticated (stored in sessionStorage)
  useEffect(() => {
    const authenticated = sessionStorage.getItem('morningmaghreb_authenticated')
    if (authenticated === 'true') {
      setIsAuthenticated(true)
      onAccessGranted()
    }
  }, [onAccessGranted])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    // Simulate a small delay for better UX
    await new Promise(resolve => setTimeout(resolve, 500))

    if (password === correctPassword) {
      setIsAuthenticated(true)
      sessionStorage.setItem('morningmaghreb_authenticated', 'true')
      onAccessGranted()
    } else {
      setError('Incorrect password. Please try again.')
      setPassword('')
    }
    
    setIsLoading(false)
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    sessionStorage.removeItem('morningmaghreb_authenticated')
    setPassword('')
    setError('')
  }

  if (isAuthenticated) {
    return (
      <div className="relative">
        {/* Logout button */}
        <button
          onClick={handleLogout}
          className="fixed top-4 right-4 z-50 bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded-md text-sm font-medium transition-colors"
        >
          Logout
        </button>
        {children}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-indigo-600 rounded-full flex items-center justify-center">
            <LockClosedIcon className="h-8 w-8 text-white" />
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900 dark:text-white">
            Morning Maghreb
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Enter password to access the platform
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="password" className="sr-only">
              Password
            </label>
            <div className="relative">
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                required
                className="relative block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                ) : (
                  <EyeIcon className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className="text-red-600 dark:text-red-400 text-sm text-center">
              {error}
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={isLoading || !password}
              className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Verifying...
                </div>
              ) : (
                'Access Platform'
              )}
            </button>
          </div>
        </form>

        <div className="text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Protected by Morning Maghreb Security
          </p>
        </div>
      </div>
    </div>
  )
} 