import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import Link from 'next/link'
import { ArrowLeftIcon, StarIcon } from '@heroicons/react/24/outline'
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import CompanyHeader from '@/components/company/CompanyHeader'
import SnapshotMetrics from '@/components/company/SnapshotMetrics'
import FinancialChart from '@/components/company/FinancialChart'
import FinancialTable from '@/components/company/FinancialTable'
import AiSummary from '@/components/company/AiSummary'
import CorporateActions from '@/components/company/CorporateActions'

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
  aiSummary: string
  financialData: {
    revenue: { year: number; value: number }[]
    netIncome: { year: number; value: number }[]
    eps: { year: number; value: number }[]
  }
  incomeStatement: {
    revenue: number
    costOfRevenue: number
    grossProfit: number
    operatingExpenses: number
    operatingIncome: number
    netIncome: number
  }
  balanceSheet: {
    totalAssets: number
    totalLiabilities: number
    totalEquity: number
    cash: number
    debt: number
  }
  corporateActions: {
    dividends: { date: string; amount: number }[]
    earnings: { date: string; estimate: number }[]
    splits: { date: string; ratio: string }[]
  }
}

// Mock data for demonstration
const mockCompanyData: Record<string, CompanyData> = {
  ATW: {
    ticker: 'ATW',
    name: 'Attijariwafa Bank',
    sector: 'Banking',
    currentPrice: 410.10,
    priceChange: 1.28,
    priceChangePercent: 0.31,
    marketCap: 102000000000,
    revenue: 41500000000,
    netIncome: 8100000000,
    peRatio: 11.3,
    dividendYield: 4.1,
    roe: 19.4,
    aiSummary: "Attijariwafa Bank continues to demonstrate strong performance in Q3 2024 with robust loan growth and improved asset quality. The bank's diversified revenue streams and strategic expansion across Africa are driving sustainable growth. Net interest income increased 7.2% year-over-year, while the cost-to-income ratio improved to 45.8%. The bank's digital transformation initiatives are enhancing customer experience and operational efficiency.",
    financialData: {
      revenue: [
        { year: 2020, value: 35000000000 },
        { year: 2021, value: 37000000000 },
        { year: 2022, value: 38500000000 },
        { year: 2023, value: 40000000000 },
        { year: 2024, value: 41500000000 }
      ],
      netIncome: [
        { year: 2020, value: 6500000000 },
        { year: 2021, value: 7000000000 },
        { year: 2022, value: 7400000000 },
        { year: 2023, value: 7800000000 },
        { year: 2024, value: 8100000000 }
      ],
      eps: [
        { year: 2020, value: 12.5 },
        { year: 2021, value: 13.4 },
        { year: 2022, value: 14.2 },
        { year: 2023, value: 15.0 },
        { year: 2024, value: 15.6 }
      ]
    },
    incomeStatement: {
      revenue: 41500000000,
      costOfRevenue: 25000000000,
      grossProfit: 16500000000,
      operatingExpenses: 8400000000,
      operatingIncome: 8100000000,
      netIncome: 8100000000
    },
    balanceSheet: {
      totalAssets: 880000000000,
      totalLiabilities: 780000000000,
      totalEquity: 100000000000,
      cash: 22000000000,
      debt: 32000000000
    },
    corporateActions: {
      dividends: [
        { date: '2024-06-20', amount: 15.0 },
        { date: '2023-12-20', amount: 14.5 },
        { date: '2023-06-20', amount: 14.0 }
      ],
      earnings: [
        { date: '2024-10-28', estimate: 4.2 },
        { date: '2024-07-28', estimate: 3.8 }
      ],
      splits: []
    }
  },
  IAM: {
    ticker: 'IAM',
    name: 'Maroc Telecom',
    sector: 'Telecommunications',
    currentPrice: 89.45,
    priceChange: 2.15,
    priceChangePercent: 2.46,
    marketCap: 98000000000,
    revenue: 36800000000,
    netIncome: 6700000000,
    peRatio: 14.2,
    dividendYield: 4.6,
    roe: 18.5,
    aiSummary: "Maroc Telecom reported strong Q3 2024 results with revenue growth of 8.2% driven by mobile data and fixed broadband expansion. The company's strategic investments in 5G infrastructure and digital services are paying off, with EBITDA margins improving to 42.3%. Management expects continued growth in the Moroccan market while expanding operations in sub-Saharan Africa.",
    financialData: {
      revenue: [
        { year: 2020, value: 32000000000 },
        { year: 2021, value: 33500000000 },
        { year: 2022, value: 34500000000 },
        { year: 2023, value: 35500000000 },
        { year: 2024, value: 36800000000 }
      ],
      netIncome: [
        { year: 2020, value: 5800000000 },
        { year: 2021, value: 6100000000 },
        { year: 2022, value: 6300000000 },
        { year: 2023, value: 6500000000 },
        { year: 2024, value: 6700000000 }
      ],
      eps: [
        { year: 2020, value: 6.2 },
        { year: 2021, value: 6.5 },
        { year: 2022, value: 6.7 },
        { year: 2023, value: 6.9 },
        { year: 2024, value: 7.1 }
      ]
    },
    incomeStatement: {
      revenue: 36800000000,
      costOfRevenue: 21200000000,
      grossProfit: 15600000000,
      operatingExpenses: 8900000000,
      operatingIncome: 6700000000,
      netIncome: 6700000000
    },
    balanceSheet: {
      totalAssets: 85000000000,
      totalLiabilities: 45000000000,
      totalEquity: 40000000000,
      cash: 12000000000,
      debt: 18000000000
    },
    corporateActions: {
      dividends: [
        { date: '2024-06-15', amount: 3.5 },
        { date: '2023-12-15', amount: 3.2 },
        { date: '2023-06-15', amount: 3.0 }
      ],
      earnings: [
        { date: '2024-10-25', estimate: 1.8 },
        { date: '2024-07-25', estimate: 1.6 }
      ],
      splits: []
    }
  },
  BCP: {
    ticker: 'BCP',
    name: 'Banque Centrale Populaire',
    sector: 'Banking',
    currentPrice: 245.60,
    priceChange: -3.20,
    priceChangePercent: -1.29,
    marketCap: 125000000000,
    revenue: 45000000000,
    netIncome: 8500000000,
    peRatio: 14.7,
    dividendYield: 3.8,
    roe: 16.2,
    aiSummary: "BCP demonstrated resilient performance in Q3 2024 despite challenging economic conditions. Net interest income grew 6.8% year-over-year, supported by strong loan growth and improved net interest margins. The bank's digital transformation initiatives are driving operational efficiency, with cost-to-income ratio improving to 48.2%. Asset quality remains stable with NPL ratio at 3.1%.",
    financialData: {
      revenue: [
        { year: 2020, value: 38000000000 },
        { year: 2021, value: 40000000000 },
        { year: 2022, value: 42000000000 },
        { year: 2023, value: 43500000000 },
        { year: 2024, value: 45000000000 }
      ],
      netIncome: [
        { year: 2020, value: 7200000000 },
        { year: 2021, value: 7600000000 },
        { year: 2022, value: 8000000000 },
        { year: 2023, value: 8300000000 },
        { year: 2024, value: 8500000000 }
      ],
      eps: [
        { year: 2020, value: 8.5 },
        { year: 2021, value: 9.0 },
        { year: 2022, value: 9.5 },
        { year: 2023, value: 9.8 },
        { year: 2024, value: 10.1 }
      ]
    },
    incomeStatement: {
      revenue: 45000000000,
      costOfRevenue: 28000000000,
      grossProfit: 17000000000,
      operatingExpenses: 8500000000,
      operatingIncome: 8500000000,
      netIncome: 8500000000
    },
    balanceSheet: {
      totalAssets: 950000000000,
      totalLiabilities: 850000000000,
      totalEquity: 100000000000,
      cash: 25000000000,
      debt: 35000000000
    },
    corporateActions: {
      dividends: [
        { date: '2024-07-10', amount: 8.5 },
        { date: '2023-12-10', amount: 8.0 },
        { date: '2023-07-10', amount: 7.5 }
      ],
      earnings: [
        { date: '2024-10-30', estimate: 2.8 },
        { date: '2024-07-30', estimate: 2.5 }
      ],
      splits: []
    }
  }
}

export default function CompanyPage() {
  const router = useRouter()
  const { ticker } = router.query
  const [companyData, setCompanyData] = useState<CompanyData | null>(null)
  const [isInWatchlist, setIsInWatchlist] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (ticker && typeof ticker === 'string') {
      // Simulate API call
      setTimeout(() => {
        const upperTicker = ticker.toUpperCase()
        const data = mockCompanyData[upperTicker]
        
        if (data) {
          setCompanyData(data)
        } else {
          router.push('/404')
        }
        setLoading(false)
      }, 100) // Reduced timeout for faster loading
    }
  }, [ticker, router])

  const toggleWatchlist = () => {
    setIsInWatchlist(!isInWatchlist)
    // TODO: Implement actual watchlist toggle with Supabase
  }

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

  if (!companyData) {
    return null
  }

  return (
    <>
      <Head>
        <title>{companyData.name} ({companyData.ticker}) - Company Profile | Casablanca Insight</title>
        <meta 
          name="description" 
          content={`${companyData.name} (${companyData.ticker}) company profile with financial data, charts, and AI-powered insights. Market cap: ${(companyData.marketCap / 1000000000).toFixed(1)}B MAD, P/E: ${companyData.peRatio}, ROE: ${companyData.roe}%`}
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

          {/* Company Header */}
          <CompanyHeader 
            company={companyData}
            isInWatchlist={isInWatchlist}
            onToggleWatchlist={toggleWatchlist}
          />

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              <SnapshotMetrics company={companyData} />
              <FinancialChart data={companyData.financialData} />
              <FinancialTable 
                incomeStatement={companyData.incomeStatement}
                balanceSheet={companyData.balanceSheet}
              />
              <AiSummary summary={companyData.aiSummary} />
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              <CorporateActions actions={companyData.corporateActions} />
              
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