import { useState, useEffect } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { 
  KeyIcon, 
  DocumentArrowDownIcon, 
  DocumentTextIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  CogIcon,
  GlobeAltIcon,
  BellIcon
} from '@heroicons/react/24/outline'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import ApiKeyManager from '@/components/premium/ApiKeyManager'
import DataExporter from '@/components/premium/DataExporter'
import ReportBuilder from '@/components/premium/ReportBuilder'
import WebhookManager from '@/components/premium/WebhookManager'
import TranslationManager from '@/components/premium/TranslationManager'
import { supabase } from '@/lib/supabase'
import toast from 'react-hot-toast'

type ActiveTab = 'api-keys' | 'exports' | 'reports' | 'webhooks' | 'translations'

export default function PremiumFeatures() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<ActiveTab>('api-keys')
  const [user, setUser] = useState<any>(null)
  const [userSubscriptionTier, setUserSubscriptionTier] = useState<string>('free')
  const [authLoading, setAuthLoading] = useState(true)

  const tabs = [
    {
      id: 'api-keys' as ActiveTab,
      name: 'API Keys',
      icon: KeyIcon,
      description: 'Manage API keys for programmatic access',
      tier: 'institutional'
    },
    {
      id: 'exports' as ActiveTab,
      name: 'Data Exports',
      icon: DocumentArrowDownIcon,
      description: 'Export financial and macro data in multiple formats',
      tier: 'pro'
    },
    {
      id: 'reports' as ActiveTab,
      name: 'Custom Reports',
      icon: DocumentTextIcon,
      description: 'Generate 1-page PDF investment summaries',
      tier: 'pro'
    },
    {
      id: 'webhooks' as ActiveTab,
      name: 'Webhooks',
      icon: BellIcon,
      description: 'Set up real-time data delivery',
      tier: 'institutional'
    },
    {
      id: 'translations' as ActiveTab,
      name: 'Multilingual',
      icon: GlobeAltIcon,
      description: 'AI-powered content translation',
      tier: 'pro'
    }
  ]

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (!supabase) {
          console.error('Supabase not configured')
          setAuthLoading(false)
          return
        }

        const { data: { session } } = await supabase.auth.getSession()
        
        if (!session) {
          router.replace('/login')
          return
        }

        setUser(session.user)
        
        // Mock subscription tier - replace with actual database query
        setUserSubscriptionTier('pro') // or 'institutional' for testing
        
      } catch (error) {
        console.error('Auth check error:', error)
        router.replace('/login')
      } finally {
        setAuthLoading(false)
      }
    }

    checkAuth()

    // Listen for auth changes
    if (supabase) {
      const { data: { subscription } } = supabase.auth.onAuthStateChange(
        async (event, session) => {
          if (event === 'SIGNED_OUT') {
            setUser(null)
            router.replace('/login')
          } else if (session) {
            setUser(session.user)
          }
        }
      )

      return () => subscription.unsubscribe()
    }
  }, [router])

  const renderActiveComponent = () => {
    switch (activeTab) {
      case 'api-keys':
        return <ApiKeyManager userSubscriptionTier={userSubscriptionTier} />
      case 'exports':
        return <DataExporter userSubscriptionTier={userSubscriptionTier} />
      case 'reports':
        return <ReportBuilder userSubscriptionTier={userSubscriptionTier} />
      case 'webhooks':
        return <WebhookManager userSubscriptionTier={userSubscriptionTier} />
      case 'translations':
        return <TranslationManager userSubscriptionTier={userSubscriptionTier} />
      default:
        return <ApiKeyManager userSubscriptionTier={userSubscriptionTier} />
    }
  }

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'institutional':
        return 'text-purple-600 bg-purple-100 dark:text-purple-400 dark:bg-purple-900/20'
      case 'pro':
        return 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/20'
      default:
        return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/20'
    }
  }

  const getTierLabel = (tier: string) => {
    switch (tier) {
      case 'institutional':
        return 'Institutional'
      case 'pro':
        return 'Pro'
      default:
        return 'Free'
    }
  }

  // Show loading while checking authentication
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-dark-bg flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-casablanca-blue"></div>
      </div>
    )
  }

  // Don't render anything if not authenticated
  if (!user) {
    return null
  }

  return (
    <>
      <Head>
        <title>Premium Features - Casablanca Insight</title>
        <meta name="description" content="Premium features for Casablanca Insight including API access, data exports, custom reports, webhooks, and multilingual support." />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-dark-bg">
        <Header />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                  Premium Features
                </h1>
                <p className="text-lg text-gray-600 dark:text-gray-400">
                  Advanced tools for institutional and professional investors
                </p>
              </div>
              <div className="flex items-center space-x-3">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getTierColor(userSubscriptionTier)}`}>
                  {getTierLabel(userSubscriptionTier)} Tier
                </span>
                {userSubscriptionTier === 'free' && (
                  <button className="px-4 py-2 bg-casablanca-blue text-white rounded-md hover:bg-blue-700 transition-colors">
                    Upgrade
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Feature Overview */}
          <div className="mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-dark-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-dark-border">
              <div className="flex items-center space-x-3 mb-3">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
                  <KeyIcon className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">API Access</h3>
                  <span className="text-xs text-purple-600 dark:text-purple-400 font-medium">Institutional</span>
                </div>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Programmatic access to financial data, macro indicators, and market quotes with rate limiting and authentication.
              </p>
            </div>

            <div className="bg-white dark:bg-dark-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-dark-border">
              <div className="flex items-center space-x-3 mb-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                  <DocumentArrowDownIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">Data Exports</h3>
                  <span className="text-xs text-blue-600 dark:text-blue-400 font-medium">Pro+</span>
                </div>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Export financial data, macro indicators, and portfolio data in CSV, Excel, or JSON formats with custom filtering.
              </p>
            </div>

            <div className="bg-white dark:bg-dark-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-dark-border">
              <div className="flex items-center space-x-3 mb-3">
                <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                  <DocumentTextIcon className="w-6 h-6 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">Custom Reports</h3>
                  <span className="text-xs text-green-600 dark:text-green-400 font-medium">Pro+</span>
                </div>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Generate 1-page PDF investment summaries with key ratios, AI analysis, and risk profiles for any Moroccan company.
              </p>
            </div>

            <div className="bg-white dark:bg-dark-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-dark-border">
              <div className="flex items-center space-x-3 mb-3">
                <div className="p-2 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg">
                  <BellIcon className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">Webhooks</h3>
                  <span className="text-xs text-yellow-600 dark:text-yellow-400 font-medium">Institutional</span>
                </div>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Real-time data delivery via webhooks for price alerts, earnings releases, and dividend payments.
              </p>
            </div>

            <div className="bg-white dark:bg-dark-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-dark-border">
              <div className="flex items-center space-x-3 mb-3">
                <div className="p-2 bg-indigo-100 dark:bg-indigo-900/20 rounded-lg">
                  <GlobeAltIcon className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">Multilingual</h3>
                  <span className="text-xs text-indigo-600 dark:text-indigo-400 font-medium">Pro+</span>
                </div>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                AI-powered translation for reports, summaries, and content in English, French, and Arabic.
              </p>
            </div>

            <div className="bg-gradient-to-br from-casablanca-blue to-blue-600 p-6 rounded-lg shadow-sm text-white">
              <h3 className="font-semibold mb-2">Premium Support</h3>
              <p className="text-sm text-blue-100">
                Priority support, dedicated account management, and custom integrations for institutional clients.
              </p>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="mb-6">
            <div className="border-b border-gray-200 dark:border-dark-border">
              <nav className="-mb-px flex space-x-8 overflow-x-auto">
                {tabs.map((tab) => {
                  const Icon = tab.icon
                  const hasAccess = userSubscriptionTier === tab.tier || 
                    (tab.tier === 'pro' && userSubscriptionTier === 'institutional')
                  
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      disabled={!hasAccess}
                      className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors ${
                        activeTab === tab.id
                          ? 'border-casablanca-blue text-casablanca-blue'
                          : hasAccess
                            ? 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                            : 'border-transparent text-gray-300 cursor-not-allowed dark:text-gray-600'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span>{tab.name}</span>
                      {!hasAccess && (
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTierColor(tab.tier)}`}>
                          {getTierLabel(tab.tier)}
                        </span>
                      )}
                    </button>
                  )
                })}
              </nav>
            </div>
          </div>

          {/* Active Component */}
          <div className="mb-8">
            {renderActiveComponent()}
          </div>

          {/* Subscription Information */}
          <div className="bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Subscription Tiers
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-4 border border-gray-200 dark:border-dark-border rounded-lg">
                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Free</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                  Basic market data and limited features
                </p>
                <ul className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
                  <li>• Basic market data</li>
                  <li>• Limited financials</li>
                  <li>• Basic portfolio tracking</li>
                </ul>
              </div>
              
              <div className="text-center p-4 border border-blue-200 dark:border-blue-800 rounded-lg bg-blue-50 dark:bg-blue-900/10">
                <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">Pro</h4>
                <p className="text-sm text-blue-700 dark:text-blue-300 mb-3">
                  Advanced features for serious investors
                </p>
                <ul className="text-xs text-blue-600 dark:text-blue-400 space-y-1">
                  <li>• All Free features</li>
                  <li>• Data exports (CSV/XLS)</li>
                  <li>• Custom reports</li>
                  <li>• Multilingual support</li>
                  <li>• Advanced analytics</li>
                </ul>
              </div>
              
              <div className="text-center p-4 border border-purple-200 dark:border-purple-800 rounded-lg bg-purple-50 dark:bg-purple-900/10">
                <h4 className="font-semibold text-purple-900 dark:text-purple-100 mb-2">Institutional</h4>
                <p className="text-sm text-purple-700 dark:text-purple-300 mb-3">
                  Enterprise features for institutions
                </p>
                <ul className="text-xs text-purple-600 dark:text-purple-400 space-y-1">
                  <li>• All Pro features</li>
                  <li>• API access</li>
                  <li>• Webhook integrations</li>
                  <li>• Priority support</li>
                  <li>• Custom integrations</li>
                </ul>
              </div>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </>
  )
}

 