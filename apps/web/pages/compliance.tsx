import React from 'react'
import { useRouter } from 'next/router'
import { useUser } from '@/lib/useUser'
import ComplianceDashboard from '@/components/ComplianceDashboard'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

export default function CompliancePage() {
  const router = useRouter()
  const { user, profile, loading } = useUser()

  // Redirect if not authenticated
  if (!loading && !user) {
    router.push('/login')
    return null
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      <ComplianceDashboard userId={user?.id || ''} />
      <Footer />
    </div>
  )
} 