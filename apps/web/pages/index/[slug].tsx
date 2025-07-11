import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import Link from 'next/link'
import { ArrowLeftIcon, ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/outline'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

interface IndexData {
  symbol: string
  name: string
  currentValue: number
  change: number
  changePercent: number
  description: string
  constituents: {
    ticker: string
    name: string
    weight: number
    price: number
    change: number
    changePercent: number
  }[]
}

const mockIndexData: Record<string, IndexData> = {
  masi: {
    symbol: 'MASI',
    name: 'Moroccan All Shares Index',
    currentValue: 12456.78,
    change: 45.23,
    changePercent: 0.36,
    description: 'The Moroccan All Shares Index (MASI) is the main benchmark index of the Casablanca Stock Exchange, representing the performance of all listed companies.',
    constituents: [
      { ticker: 'ATW', name: 'Attijariwafa Bank', weight: 15.2, price: 45.60, change: 0.85, changePercent: 1.90 },
      { ticker: 'BCP', name: 'Banque Centrale Populaire', weight: 12.8, price: 245.60, change: -3.20, changePercent: -1.29 },
      { ticker: 'IAM', name: 'Maroc Telecom', weight: 11.5, price: 89.45, change: 2.15, changePercent: 2.46 },
      { ticker: 'BMCE', name: 'BMCE Bank', weight: 8.9, price: 23.45, change: -0.32, changePercent: -1.35 },
      { ticker: 'CIH', name: 'CIH Bank', weight: 7.3, price: 34.20, change: 0.45, changePercent: 1.33 },
      { ticker: 'WAA', name: 'Wafa Assurance', weight: 6.1, price: 67.80, change: -1.20, changePercent: -1.74 },
      { ticker: 'CMT', name: 'Compagnie Minière', weight: 5.8, price: 89.45, change: 2.15, changePercent: 2.46 },
    ]
  },
  madex: {
    symbol: 'MADEX',
    name: 'Most Active Shares Index',
    currentValue: 10234.56,
    change: -23.45,
    changePercent: -0.23,
    description: 'The MADEX index tracks the most actively traded shares on the Casablanca Stock Exchange, providing a measure of market liquidity.',
    constituents: [
      { ticker: 'ATW', name: 'Attijariwafa Bank', weight: 18.5, price: 45.60, change: 0.85, changePercent: 1.90 },
      { ticker: 'BCP', name: 'Banque Centrale Populaire', weight: 16.2, price: 245.60, change: -3.20, changePercent: -1.29 },
      { ticker: 'IAM', name: 'Maroc Telecom', weight: 14.8, price: 89.45, change: 2.15, changePercent: 2.46 },
      { ticker: 'BMCE', name: 'BMCE Bank', weight: 12.1, price: 23.45, change: -0.32, changePercent: -1.35 },
      { ticker: 'CIH', name: 'CIH Bank', weight: 10.3, price: 34.20, change: 0.45, changePercent: 1.33 },
      { ticker: 'WAA', name: 'Wafa Assurance', weight: 8.7, price: 67.80, change: -1.20, changePercent: -1.74 },
      { ticker: 'CMT', name: 'Compagnie Minière', weight: 7.4, price: 89.45, change: 2.15, changePercent: 2.46 },
    ]
  }
}

export default function IndexPage() {
  const router = useRouter()
  const { slug } = router.query
  const [indexData, setIndexData] = useState<IndexData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (slug && typeof slug === 'string') {
      // Simulate API call
      setTimeout(() => {
        const data = mockIndexData[slug.toLowerCase()]
        if (data) {
          setIndexData(data)
        } else {
          router.push('/404')
        }
        setLoading(false)
      }, 500)
    }
  }, [slug, router])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-dark-bg">
        <Header />
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-casablanca-blue"></div>
        </div>
        <Footer />
      </div>
    )
  }

  if (!indexData) {
    return null
  }

  const isPositive = indexData.changePercent >= 0

  return (
    <>
      <Head>
        <title>{indexData.name} ({indexData.symbol}) - Index Profile | Casablanca Insight</title>
        <meta 
          name="description" 
          content={`${indexData.name} (${indexData.symbol}) index profile with current value, performance, and constituent companies.`}
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-dark-bg text-gray-900 dark:text-dark-text">
        <Header />
        
        <main className="px-4 py-6 max-w-7xl mx-auto">
          {/* Back Navigation */}
          <div className="mb-6">
            <Link 
              href="/"
              className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
            >
              <ArrowLeftIcon className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Link>
          </div>

          {/* Index Header */}
          <div className="bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6 mb-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {indexData.name}
                  </h1>
                  <span className="text-lg font-medium text-gray-500 dark:text-gray-400">
                    {indexData.symbol}
                  </span>
                </div>
                
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  {indexData.description}
                </p>

                <div className="flex items-center space-x-6">
                  <div>
                    <div className="text-3xl font-bold text-gray-900 dark:text-white">
                      {indexData.currentValue.toFixed(2)}
                    </div>
                    <div className={`flex items-center text-sm ${
                      isPositive ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {isPositive ? (
                        <ArrowUpIcon className="h-4 w-4 mr-1" />
                      ) : (
                        <ArrowDownIcon className="h-4 w-4 mr-1" />
                      )}
                      {isPositive ? '+' : ''}{indexData.change.toFixed(2)} ({isPositive ? '+' : ''}{indexData.changePercent.toFixed(2)}%)
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Constituents Table */}
          <div className="bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Constituent Companies
            </h2>
            
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-dark-border">
                    <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider py-2">Company</th>
                    <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider py-2">Weight</th>
                    <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider py-2">Price</th>
                    <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider py-2">Change</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-dark-border">
                  {indexData.constituents.map((company) => (
                    <tr key={company.ticker} className="hover:bg-gray-50 dark:hover:bg-dark-hover">
                      <td className="py-3">
                        <Link href={`/company/${company.ticker}`} className="block">
                          <div>
                            <div className="text-sm font-medium text-gray-900 dark:text-white hover:text-casablanca-blue">
                              {company.ticker}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">
                              {company.name}
                            </div>
                          </div>
                        </Link>
                      </td>
                      <td className="py-3 text-sm text-gray-900 dark:text-white">
                        {company.weight.toFixed(1)}%
                      </td>
                      <td className="py-3 text-sm text-gray-900 dark:text-white">
                        {company.price.toFixed(2)} MAD
                      </td>
                      <td className="py-3">
                        <div className={`flex items-center text-sm ${
                          company.changePercent >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {company.changePercent >= 0 ? (
                            <ArrowUpIcon className="h-3 w-3 mr-1" />
                          ) : (
                            <ArrowDownIcon className="h-3 w-3 mr-1" />
                          )}
                          {company.changePercent >= 0 ? '+' : ''}{company.changePercent.toFixed(2)}%
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </>
  )
} 