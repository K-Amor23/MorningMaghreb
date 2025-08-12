import { useState, useEffect } from 'react'
import { useUser } from '@/lib/useUser'
import { LockClosedIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'

export default function PasswordProtectionAdmin() {
  const { user, profile } = useUser()
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [isEnabled, setIsEnabled] = useState(true)
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    // Check if password protection is enabled
    const enabled = process.env.NEXT_PUBLIC_ENABLE_PASSWORD_PROTECTION === 'true'
    setIsEnabled(enabled)
  }, [])

  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setMessage('')

    try {
      // Store/update preview password in cookie via lightweight API
      const res = await fetch('/api/password/set', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ currentPassword, newPassword })
      })
      if (!res.ok) throw new Error('Failed to update password')
      setMessage('Password updated successfully!')
      setCurrentPassword('')
      setNewPassword('')
    } catch (error) {
      setMessage('Failed to update password. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleToggleProtection = async () => {
    setIsLoading(true)
    try {
      const res = await fetch('/api/password/toggle', { method: 'POST' })
      if (!res.ok) throw new Error('Failed to toggle protection')
      setIsEnabled(!isEnabled)
      setMessage(`Password protection ${!isEnabled ? 'enabled' : 'disabled'} successfully!`)
    } catch (error) {
      setMessage('Failed to toggle password protection. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  // Only allow admin users to access this page
  if (!user || profile?.tier !== 'admin') {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <LockClosedIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">Access Denied</h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            You need admin privileges to access this page.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center mb-6">
              <LockClosedIcon className="h-8 w-8 text-indigo-600 mr-3" />
              <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                Password Protection Settings
              </h3>
            </div>

            {message && (
              <div className={`mb-4 p-3 rounded-md text-sm ${
                message.includes('successfully') 
                  ? 'bg-green-50 text-green-800 dark:bg-green-900/20 dark:text-green-400' 
                  : 'bg-red-50 text-red-800 dark:bg-red-900/20 dark:text-red-400'
              }`}>
                {message}
              </div>
            )}

            {/* Current Status */}
            <div className="mb-6">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                Current Status
              </h4>
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Password Protection: {isEnabled ? 'Enabled' : 'Disabled'}
                </span>
                <button
                  onClick={handleToggleProtection}
                  disabled={isLoading}
                  className="px-3 py-1 text-sm font-medium rounded-md bg-indigo-600 hover:bg-indigo-700 text-white disabled:opacity-50"
                >
                  {isEnabled ? 'Disable' : 'Enable'}
                </button>
              </div>
            </div>

            {/* Update Password Form */}
            <form onSubmit={handleUpdatePassword} className="space-y-4">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                Update Password
              </h4>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Current Password
                </label>
                <div className="relative">
                  <input
                    type={showCurrentPassword ? 'text' : 'password'}
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="Enter current password"
                    required
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                  >
                    {showCurrentPassword ? (
                      <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                    ) : (
                      <EyeIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  New Password
                </label>
                <div className="relative">
                  <input
                    type={showNewPassword ? 'text' : 'password'}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="Enter new password"
                    required
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                  >
                    {showNewPassword ? (
                      <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                    ) : (
                      <EyeIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading || !currentPassword || !newPassword}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Updating...' : 'Update Password'}
              </button>
            </form>

            {/* Information */}
            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-md">
              <h4 className="text-sm font-medium text-blue-900 dark:text-blue-400 mb-2">
                How it works
              </h4>
              <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
                <li>• Visitors must enter the password before accessing your site</li>
                <li>• Password is stored in session storage (cleared when browser closes)</li>
                <li>• Admin users can update the password through this interface</li>
                <li>• Protection can be enabled/disabled without redeployment</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 