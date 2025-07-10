import { useState } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import { useTranslation } from 'react-i18next'
import { 
  ChartBarIcon, 
  GlobeAltIcon, 
  CurrencyDollarIcon,
  SparklesIcon,
  EnvelopeIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline'

const features = [
  {
    name: 'Real-time Market Data',
    description: 'Live quotes from Casablanca Stock Exchange (CSE) with MASI, MADEX, and MASI-ESG indices.',
    icon: ChartBarIcon,
  },
  {
    name: 'IFRS to GAAP Conversion',
    description: 'Automated conversion of Moroccan financial statements to US GAAP standards.',
    icon: CurrencyDollarIcon,
  },
  {
    name: 'AI-Powered Insights',
    description: 'GPT-4 powered analysis and natural language Q&A for investor queries.',
    icon: SparklesIcon,
  },
  {
    name: 'Multilingual Support',
    description: 'Interface available in English, French, and Arabic for comprehensive access.',
    icon: GlobeAltIcon,
  },
  {
    name: 'Portfolio Analytics',
    description: 'Advanced portfolio tracking with Monte Carlo simulations and risk metrics.',
    icon: UserGroupIcon,
  },
  {
    name: 'Morning Maghreb Newsletter',
    description: 'Daily market digest with AI-generated insights delivered to your inbox.',
    icon: EnvelopeIcon,
  },
]

export default function Home() {
  const { t } = useTranslation()
  const [email, setEmail] = useState('')

  const handleNewsletterSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Implement newsletter signup
    console.log('Newsletter signup:', email)
  }

  return (
    <>
      <Head>
        <title>Casablanca Insight - Morocco Market Research & Analytics</title>
        <meta 
          name="description" 
          content="Unified Morocco market research platform with real-time CSE data, IFRS to GAAP conversion, AI insights, and daily Morning Maghreb newsletter." 
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="bg-white">
        {/* Navigation */}
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <div className="flex-shrink-0 flex items-center">
                  <h1 className="text-2xl font-bold text-casablanca-blue">
                    Casablanca Insight
                  </h1>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <Link
                  href="/signup"
                  className="bg-casablanca-blue text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
                >
                  {t('signup')}
                </Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="relative overflow-hidden">
          <div className="max-w-7xl mx-auto">
            <div className="relative z-10 pb-8 bg-white sm:pb-16 md:pb-20 lg:max-w-2xl lg:w-full lg:pb-28 xl:pb-32">
              <main className="mt-10 mx-auto max-w-7xl px-4 sm:mt-12 sm:px-6 md:mt-16 lg:mt-20 lg:px-8 xl:mt-28">
                <div className="sm:text-center lg:text-left">
                  <h1 className="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
                    <span className="block xl:inline">Morocco Market</span>{' '}
                    <span className="block text-casablanca-blue xl:inline">
                      Research & Analytics
                    </span>
                  </h1>
                  <p className="mt-3 text-base text-gray-500 sm:mt-5 sm:text-lg sm:max-w-xl sm:mx-auto md:mt-5 md:text-xl lg:mx-0">
                    Unify fragmented French, Arabic, and Darija data into a comprehensive 
                    multilingual portal for serious investors. Track real-time CSE quotes, 
                    convert IFRS to GAAP, and get AI-powered insights with our daily 
                    Morning Maghreb newsletter.
                  </p>
                  <div className="mt-5 sm:mt-8 sm:flex sm:justify-center lg:justify-start">
                    <div className="rounded-md shadow">
                      <Link
                        href="/signup"
                        className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-casablanca-blue hover:bg-blue-700 md:py-4 md:text-lg md:px-10"
                      >
                        Get Started
                      </Link>
                    </div>
                    <div className="mt-3 sm:mt-0 sm:ml-3">
                      <Link
                        href="/dashboard"
                        className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-casablanca-blue bg-gray-100 hover:bg-gray-200 md:py-4 md:text-lg md:px-10"
                      >
                        View Demo
                      </Link>
                    </div>
                  </div>
                </div>
              </main>
            </div>
          </div>
          <div className="lg:absolute lg:inset-y-0 lg:right-0 lg:w-1/2">
            <div className="h-56 w-full bg-gradient-to-br from-morocco-red to-morocco-green sm:h-72 md:h-96 lg:w-full lg:h-full flex items-center justify-center">
              <div className="text-white text-center">
                <ChartBarIcon className="h-24 w-24 mx-auto mb-4 opacity-80" />
                <p className="text-xl font-semibold">Real-time Market Data</p>
              </div>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="py-12 bg-casablanca-light">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="lg:text-center">
              <h2 className="text-base text-casablanca-blue font-semibold tracking-wide uppercase">
                Features
              </h2>
              <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
                Everything you need for Morocco market analysis
              </p>
              <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
                From real-time market data to AI-powered insights, get comprehensive 
                tools for analyzing the Moroccan financial markets.
              </p>
            </div>

            <div className="mt-10">
              <div className="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10">
                {features.map((feature) => (
                  <div key={feature.name} className="relative">
                    <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-casablanca-blue text-white">
                      <feature.icon className="h-6 w-6" aria-hidden="true" />
                    </div>
                    <div className="ml-16">
                      <h3 className="text-lg leading-6 font-medium text-gray-900">
                        {feature.name}
                      </h3>
                      <p className="mt-2 text-base text-gray-500">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Newsletter Signup */}
        <div className="bg-casablanca-blue">
          <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8 lg:flex lg:items-center">
            <div className="lg:w-0 lg:flex-1">
              <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
                Sign up for Morning Maghreb
              </h2>
              <p className="mt-3 max-w-3xl text-lg leading-6 text-blue-200">
                Get daily market insights, top movers, and AI-powered analysis 
                delivered to your inbox every morning.
              </p>
            </div>
            <div className="mt-8 lg:mt-0 lg:ml-8">
              <form onSubmit={handleNewsletterSignup} className="sm:flex">
                <label htmlFor="email-address" className="sr-only">
                  Email address
                </label>
                <input
                  id="email-address"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-5 py-3 border border-transparent placeholder-gray-500 focus:ring-2 focus:ring-offset-2 focus:ring-white focus:border-white sm:max-w-xs rounded-md"
                  placeholder="Enter your email"
                />
                <div className="mt-3 rounded-md shadow sm:mt-0 sm:ml-3 sm:flex-shrink-0">
                  <button
                    type="submit"
                    className="w-full bg-morocco-red border border-transparent rounded-md py-3 px-5 flex items-center justify-center text-base font-medium text-white hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    Subscribe
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="bg-white">
          <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8">
            <div className="xl:grid xl:grid-cols-3 xl:gap-8">
              <div className="space-y-8 xl:col-span-1">
                <div>
                  <h3 className="text-2xl font-bold text-casablanca-blue">
                    Casablanca Insight
                  </h3>
                  <p className="mt-2 text-gray-500 text-sm">
                    Morocco-focused market research & analytics platform
                  </p>
                </div>
              </div>
              <div className="mt-12 grid grid-cols-2 gap-8 xl:mt-0 xl:col-span-2">
                <div className="md:grid md:grid-cols-2 md:gap-8">
                  <div>
                    <h3 className="text-sm font-semibold text-gray-400 tracking-wider uppercase">
                      Platform
                    </h3>
                    <ul className="mt-4 space-y-4">
                      <li>
                        <Link href="/dashboard" className="text-base text-gray-500 hover:text-gray-900">
                          Dashboard
                        </Link>
                      </li>
                      <li>
                        <Link href="/markets" className="text-base text-gray-500 hover:text-gray-900">
                          Markets
                        </Link>
                      </li>
                      <li>
                        <Link href="/portfolio" className="text-base text-gray-500 hover:text-gray-900">
                          Portfolio
                        </Link>
                      </li>
                    </ul>
                  </div>
                  <div className="mt-12 md:mt-0">
                    <h3 className="text-sm font-semibold text-gray-400 tracking-wider uppercase">
                      Company
                    </h3>
                    <ul className="mt-4 space-y-4">
                      <li>
                        <Link href="/about" className="text-base text-gray-500 hover:text-gray-900">
                          About
                        </Link>
                      </li>
                      <li>
                        <Link href="/contact" className="text-base text-gray-500 hover:text-gray-900">
                          Contact
                        </Link>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-12 border-t border-gray-200 pt-8">
              <p className="text-base text-gray-400 xl:text-center">
                &copy; 2024 Casablanca Insight. All rights reserved.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </>
  )
}