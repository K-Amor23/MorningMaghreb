import { useState } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import Link from 'next/link'
import useSWR from 'swr'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import CompanyHeader from '@/components/company/CompanyHeader'
import SnapshotMetrics from '@/components/company/SnapshotMetrics'
import FinancialChart from '@/components/company/FinancialChart'
import FinancialTable from '@/components/company/FinancialTable'
import AiSummary from '@/components/company/AiSummary'
import CorporateActions from '@/components/company/CorporateActions'
import SentimentVoting from '@/components/SentimentVoting'

interface PriceData {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface CompanyData {
  ticker: string
  name: string
  sector: string
  logo?: string
  currentPrice: number
  priceChange: number
  priceChangePercent: number
  marketCap: number
  revenue: number
  netIncome: number
  peRatio: number
  dividendYield: number
  roe: number
  sharesOutstanding?: number
  bourseInfo?: any
  lastUpdated: string
}

interface ApiResponse {
  company: CompanyData
  priceData: {
    last90Days: PriceData[]
    currentPrice: number
    priceChange: number
    priceChangePercent: number
  }
  metadata: {
    dataQuality: string
    lastUpdated: string
    sources: string[]
  }
}

// SWR fetcher function
const fetcher = (url: string) => fetch(url).then(res => {
  if (!res.ok) {
    throw new Error(`HTTP error! status: ${res.status}`)
  }
  return res.json()
})

export default function CompanyPage() {
  const router = useRouter()
  const { ticker } = router.query
  const [isInWatchlist, setIsInWatchlist] = useState(false)

  // Use SWR for data fetching - company summary
  const { data: summaryData, error: summaryError, isLoading: summaryLoading } = useSWR<ApiResponse>(
    ticker ? `/api/companies/${ticker}/summary` : null,
    fetcher,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      errorRetryCount: 3,
      errorRetryInterval: 1000
    }
  )

  // Use SWR for trading data
  const { data: tradingData, error: tradingError, isLoading: tradingLoading } = useSWR(
    ticker ? `/api/companies/${ticker}/trading?days=90&include_signals=true` : null,
    fetcher,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      errorRetryCount: 3,
      errorRetryInterval: 1000
    }
  )

  // Use SWR for reports data
  const { data: reportsData, error: reportsError, isLoading: reportsLoading } = useSWR(
    ticker ? `/api/companies/${ticker}/reports?limit=10` : null,
    fetcher,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      errorRetryCount: 3,
      errorRetryInterval: 1000
    }
  )

  // Use SWR for news data
  const { data: newsData, error: newsError, isLoading: newsLoading } = useSWR(
    ticker ? `/api/companies/${ticker}/news?days=30&limit=10` : null,
    fetcher,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      errorRetryCount: 3,
      errorRetryInterval: 1000
    }
  )

  // Combined loading state
  const isLoading = summaryLoading || tradingLoading || reportsLoading || newsLoading
  const error = summaryError || tradingError || reportsError || newsError
  const data = summaryData

  const toggleWatchlist = () => {
    setIsInWatchlist(!isInWatchlist)
    // TODO: Implement actual watchlist toggle with Supabase
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-dark-bg">
        <Header />
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-casablanca-blue mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading company data...</p>
          </div>
        </div>
        <Footer />
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-dark-bg">
        <Header />
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-red-500 text-6xl mb-4">⚠️</div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Error Loading Data
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {error.message || 'Failed to load company data'}
            </p>
            <Link
              href="/"
              className="inline-flex items-center px-4 py-2 bg-casablanca-blue text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <ArrowLeftIcon className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Link>
          </div>
        </div>
        <Footer />
      </div>
    )
  }

  // No data state
  if (!data) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-dark-bg">
        <Header />
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-gray-400 text-6xl mb-4">📊</div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Data Loading
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Company data is being prepared. Please check back soon.
            </p>
            <Link
              href="/"
              className="inline-flex items-center px-4 py-2 bg-casablanca-blue text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <ArrowLeftIcon className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Link>
          </div>
        </div>
        <Footer />
      </div>
    )
  }

  const { company, priceData, metadata } = data

  // Transform price data for charts
  const financialData = {
    revenue: [
      { year: 2020, value: company.revenue * 0.8 },
      { year: 2021, value: company.revenue * 0.9 },
      { year: 2022, value: company.revenue * 0.95 },
      { year: 2023, value: company.revenue },
      { year: 2024, value: company.revenue * 1.05 }
    ],
    netIncome: [
      { year: 2020, value: company.netIncome * 0.8 },
      { year: 2021, value: company.netIncome * 0.9 },
      { year: 2022, value: company.netIncome * 0.95 },
      { year: 2023, value: company.netIncome },
      { year: 2024, value: company.netIncome * 1.05 }
    ],
    eps: [
      { year: 2020, value: (company.netIncome * 0.8) / (company.sharesOutstanding || 1000000000) },
      { year: 2021, value: (company.netIncome * 0.9) / (company.sharesOutstanding || 1000000000) },
      { year: 2022, value: (company.netIncome * 0.95) / (company.sharesOutstanding || 1000000000) },
      { year: 2023, value: company.netIncome / (company.sharesOutstanding || 1000000000) },
      { year: 2024, value: (company.netIncome * 1.05) / (company.sharesOutstanding || 1000000000) }
    ]
  }

  // Mock financial statements
  const incomeStatement = {
    revenue: company.revenue,
    costOfRevenue: company.revenue * 0.6,
    grossProfit: company.revenue * 0.4,
    operatingExpenses: company.revenue * 0.2,
    operatingIncome: company.revenue * 0.2,
    netIncome: company.netIncome
  }

  const balanceSheet = {
    totalAssets: company.marketCap * 1.5,
    totalLiabilities: company.marketCap * 0.8,
    totalEquity: company.marketCap * 0.7,
    cash: company.marketCap * 0.1,
    debt: company.marketCap * 0.3
  }

  // Mock corporate actions
  const corporateActions = {
    dividends: [
      { date: '2024-06-15', amount: 2.5 },
      { date: '2024-03-15', amount: 2.3 },
      { date: '2023-12-15', amount: 2.1 }
    ],
    earnings: [
      { date: '2024-10-25', estimate: 2.8 },
      { date: '2024-07-25', estimate: 2.5 },
      { date: '2024-04-25', estimate: 2.3 }
    ],
    splits: []
  }

  // Mock AI summary
  const aiSummary = `${company.name} continues to demonstrate strong performance with a current market cap of ${(company.marketCap / 1000000000).toFixed(1)}B MAD. The company operates in the ${company.sector} sector and shows a P/E ratio of ${company.peRatio.toFixed(1)}. Recent price movement shows ${company.priceChangePercent > 0 ? 'positive' : 'negative'} momentum with a ${Math.abs(company.priceChangePercent).toFixed(2)}% change. The company's financial metrics indicate ${company.roe > 15 ? 'strong' : 'moderate'} operational efficiency with an ROE of ${company.roe.toFixed(1)}%.`

  return (
    <>
      <Head>
        <title>{company.name} ({company.ticker}) - Company Profile | Casablanca Insight</title>
        <meta
          name="description"
          content={`${company.name} (${company.ticker}) company profile with financial data, charts, and AI-powered insights. Market cap: ${(company.marketCap / 1000000000).toFixed(1)}B MAD, P/E: ${company.peRatio.toFixed(1)}, ROE: ${company.roe.toFixed(1)}%`}
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

          {/* Data Quality Indicator */}
          <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <div className="flex items-center text-sm text-blue-700 dark:text-blue-300">
              <span className="font-medium">Data Quality:</span>
              <span className="ml-2 px-2 py-1 bg-blue-100 dark:bg-blue-800 rounded text-xs">
                {metadata.dataQuality === 'real' ? 'Real Data' : 'Generated Data'}
              </span>
              <span className="ml-2">• Last updated: {new Date(metadata.lastUpdated).toLocaleDateString()}</span>
            </div>
          </div>

          {/* Company Header */}
          <CompanyHeader
            company={company}
            isInWatchlist={isInWatchlist}
            onToggleWatchlist={toggleWatchlist}
          />

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              <SnapshotMetrics company={company} />
              <FinancialChart data={financialData} />
              <FinancialTable
                incomeStatement={incomeStatement}
                balanceSheet={balanceSheet}
              />
              <AiSummary ticker={company.ticker} />
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              <SentimentVoting ticker={company.ticker} companyName={company.name} />
              <CorporateActions actions={corporateActions} />

              {/* Filing Downloads */}
              <div className="bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Filings & Reports
                </h3>
                <div className="space-y-3">
                  <a
                    href="#"
                    className="block p-3 border border-gray-200 dark:border-dark-border rounded-lg hover:bg-gray-50 dark:hover:bg-dark-hover transition-colors"
                  >
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      Q3 2024 Financial Report
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      PDF • 2.3 MB • Oct 25, 2024
                    </div>
                  </a>
                  <a
                    href="#"
                    className="block p-3 border border-gray-200 dark:border-dark-border rounded-lg hover:bg-gray-50 dark:hover:bg-dark-hover transition-colors"
                  >
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      Annual Report 2023
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      PDF • 5.1 MB • Mar 15, 2024
                    </div>
                  </a>
                  <a
                    href="#"
                    className="block p-3 border border-gray-200 dark:border-dark-border rounded-lg hover:bg-gray-50 dark:hover:bg-dark-hover transition-colors"
                  >
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      Investor Relations
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      External Link • Company Website
                    </div>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </>
  )
} 