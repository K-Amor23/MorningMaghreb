import { useState } from 'react'
import { useRouter } from 'next/router'
import { useUser } from '@/lib/useUser'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

export default function AccountSettings() {
  const { t } = useTranslation()
  const router = useRouter()
  const { user, profile, dashboard, loading, error, updateProfile, signOut } = useUser()
  const [updating, setUpdating] = useState(false)

  // Redirect if not authenticated
  if (!loading && !user) {
    router.replace('/login')
    return null
  }

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-casablanca-light">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="space-y-4">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              <div className="h-4 bg-gray-200 rounded w-2/3"></div>
            </div>
          </div>
        </div>
        <Footer />
      </div>
    )
  }

  const handleProfileUpdate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setUpdating(true)

    const formData = new FormData(e.currentTarget)
    const updates = {
      full_name: formData.get('full_name') as string,
      language_preference: formData.get('language_preference') as 'en' | 'fr' | 'ar',
      newsletter_frequency: formData.get('newsletter_frequency') as 'daily' | 'weekly' | 'monthly',
      preferences: {
        theme: formData.get('theme') as string,
        notifications: formData.get('notifications') === 'on',
        email_alerts: formData.get('email_alerts') === 'on'
      }
    }

    try {
      await updateProfile(updates)
      toast.success('Profile updated successfully!')
    } catch (err) {
      toast.error('Failed to update profile')
    } finally {
      setUpdating(false)
    }
  }

  const handleSignOut = async () => {
    try {
      await signOut()
      toast.success('Signed out successfully')
      router.push('/')
    } catch (err) {
      toast.error('Failed to sign out')
    }
  }

  return (
    <div className="min-h-screen bg-casablanca-light">
      <Header />

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Page Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {t('Account Settings')}
            </h1>
            <p className="text-gray-600">
              {t('Manage your account preferences and subscription settings')}
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600">{error}</p>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Profile Information */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">
                  {t('Profile Information')}
                </h2>

                <form onSubmit={handleProfileUpdate} className="space-y-6">
                  {/* Email (Read-only) */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {t('Email Address')}
                    </label>
                    <input
                      type="email"
                      value={user?.email || ''}
                      disabled
                      className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500"
                    />
                    <p className="mt-1 text-sm text-gray-500">
                      {t('Email address cannot be changed')}
                    </p>
                  </div>

                  {/* Full Name */}
                  <div>
                    <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-2">
                      {t('Full Name')}
                    </label>
                    <input
                      type="text"
                      id="full_name"
                      name="full_name"
                      defaultValue={profile?.full_name || ''}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-casablanca-blue focus:border-transparent"
                    />
                  </div>

                  {/* Language Preference */}
                  <div>
                    <label htmlFor="language_preference" className="block text-sm font-medium text-gray-700 mb-2">
                      {t('Language Preference')}
                    </label>
                    <select
                      id="language_preference"
                      name="language_preference"
                      defaultValue={profile?.language_preference || 'en'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-casablanca-blue focus:border-transparent"
                    >
                      <option value="en">English</option>
                      <option value="fr">Français</option>
                      <option value="ar">العربية</option>
                    </select>
                  </div>

                  {/* Newsletter Frequency */}
                  <div>
                    <label htmlFor="newsletter_frequency" className="block text-sm font-medium text-gray-700 mb-2">
                      {t('Newsletter Frequency')}
                    </label>
                    <select
                      id="newsletter_frequency"
                      name="newsletter_frequency"
                      defaultValue={profile?.newsletter_frequency || 'weekly'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-casablanca-blue focus:border-transparent"
                    >
                      <option value="daily">{t('Daily')}</option>
                      <option value="weekly">{t('Weekly')}</option>
                      <option value="monthly">{t('Monthly')}</option>
                    </select>
                  </div>

                  {/* Theme Preference */}
                  <div>
                    <label htmlFor="theme" className="block text-sm font-medium text-gray-700 mb-2">
                      {t('Theme')}
                    </label>
                    <select
                      id="theme"
                      name="theme"
                      defaultValue={profile?.preferences?.theme || 'system'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-casablanca-blue focus:border-transparent"
                    >
                      <option value="system">{t('System')}</option>
                      <option value="light">{t('Light')}</option>
                      <option value="dark">{t('Dark')}</option>
                    </select>
                  </div>

                  {/* Notifications */}
                  <div className="space-y-4">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="notifications"
                        name="notifications"
                        defaultChecked={profile?.preferences?.notifications || false}
                        className="h-4 w-4 text-casablanca-blue focus:ring-casablanca-blue border-gray-300 rounded"
                      />
                      <label htmlFor="notifications" className="ml-2 block text-sm text-gray-900">
                        {t('Enable push notifications')}
                      </label>
                    </div>

                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="email_alerts"
                        name="email_alerts"
                        defaultChecked={profile?.preferences?.email_alerts || false}
                        className="h-4 w-4 text-casablanca-blue focus:ring-casablanca-blue border-gray-300 rounded"
                      />
                      <label htmlFor="email_alerts" className="ml-2 block text-sm text-gray-900">
                        {t('Enable email alerts')}
                      </label>
                    </div>
                  </div>

                  {/* Submit Button */}
                  <div className="pt-4">
                    <button
                      type="submit"
                      disabled={updating}
                      className="w-full bg-casablanca-blue text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-casablanca-blue focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {updating ? t('Updating...') : t('Update Profile')}
                    </button>
                  </div>
                </form>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Account Status */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  {t('Account Status')}
                </h3>

                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">{t('Subscription Tier')}:</span>
                    <span className={`text-sm font-medium ${profile?.tier === 'pro' ? 'text-green-600' :
                        profile?.tier === 'admin' ? 'text-purple-600' : 'text-gray-600'
                      }`}>
                      {profile?.tier?.toUpperCase() || 'FREE'}
                    </span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">{t('Member Since')}:</span>
                    <span className="text-sm text-gray-900">
                      {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : '-'}
                    </span>
                  </div>

                  {dashboard && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">{t('Watchlist Items')}:</span>
                        <span className="text-sm text-gray-900">{dashboard.watchlist_count}</span>
                      </div>

                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">{t('Active Alerts')}:</span>
                        <span className="text-sm text-gray-900">{dashboard.active_alerts_count}</span>
                      </div>
                    </>
                  )}
                </div>

                {profile?.tier === 'free' && (
                  <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                    <p className="text-sm text-blue-800">
                      {t('Upgrade to Pro for advanced features and unlimited access')}
                    </p>
                    <button
                      onClick={() => router.push('/premium-features')}
                      className="mt-2 text-sm text-blue-600 hover:text-blue-800 font-medium"
                    >
                      {t('Learn More')} →
                    </button>
                  </div>
                )}
              </div>

              {/* Account Actions */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  {t('Account Actions')}
                </h3>

                <div className="space-y-3">
                  <button
                    onClick={() => router.push('/dashboard')}
                    className="w-full text-left text-sm text-gray-600 hover:text-gray-900 py-2 px-3 rounded-md hover:bg-gray-50"
                  >
                    {t('Go to Dashboard')}
                  </button>

                  <button
                    onClick={() => router.push('/portfolio')}
                    className="w-full text-left text-sm text-gray-600 hover:text-gray-900 py-2 px-3 rounded-md hover:bg-gray-50"
                  >
                    {t('View Portfolio')}
                  </button>

                  <button
                    onClick={() => router.push('/premium-features')}
                    className="w-full text-left text-sm text-gray-600 hover:text-gray-900 py-2 px-3 rounded-md hover:bg-gray-50"
                  >
                    {t('Premium Features')}
                  </button>

                  <hr className="my-3" />

                  <button
                    onClick={handleSignOut}
                    className="w-full text-left text-sm text-red-600 hover:text-red-800 py-2 px-3 rounded-md hover:bg-red-50"
                  >
                    {t('Sign Out')}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  )
} 