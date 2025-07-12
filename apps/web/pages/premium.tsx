import { useState } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { 
  CheckIcon,
  XMarkIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  StarIcon,
  ChartBarIcon,
  DocumentTextIcon,
  CurrencyDollarIcon,
  BellIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

export default function Premium() {
  const router = useRouter()
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly')
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null)

  const features = [
    {
      icon: DocumentTextIcon,
      title: 'GAAP Financials',
      description: 'Access to GAAP financials for 100+ companies with detailed analysis',
      href: '/company/IAM' // Example company page with GAAP data
    },
    {
      icon: StarIcon,
      title: 'AI Summaries & Earnings',
      description: 'AI-powered earnings recaps and company summaries',
      href: '/company/ATW' // Example company page with AI summaries
    },
    {
      icon: ChartBarIcon,
      title: 'Portfolio Statistics',
      description: 'Advanced portfolio metrics including Sharpe ratio and Monte Carlo analysis',
      href: '/portfolio'
    },
    {
      icon: CurrencyDollarIcon,
      title: 'Smart FX Converter',
      description: 'Intelligent currency conversion with real-time alerts',
      href: '/convert'
    },
    {
      icon: GlobeAltIcon,
      title: 'Newsletter Customization',
      description: 'Personalized newsletter with your preferred content and frequency',
      href: '/dashboard' // Dashboard has newsletter settings
    }
  ]

  const comparisonData = [
    {
      feature: 'Basic Market Data',
      free: true,
      premium: true
    },
    {
      feature: 'GAAP Financials',
      free: false,
      premium: true
    },
    {
      feature: 'AI Summaries',
      free: false,
      premium: true
    },
    {
      feature: 'Portfolio Analytics',
      free: false,
      premium: true
    },
    {
      feature: 'FX Converter & Alerts',
      free: false,
      premium: true
    },
    {
      feature: 'Custom Newsletters',
      free: false,
      premium: true
    },
    {
      feature: 'Data Exports',
      free: false,
      premium: true
    },
    {
      feature: 'API Access',
      free: false,
      premium: true
    }
  ]

  const faqs = [
    {
      question: 'Do I lose access if I cancel?',
      answer: 'No, you\'ll continue to have access to premium features until the end of your current billing period. After that, you\'ll be downgraded to the free tier.'
    },
    {
      question: 'Can I downgrade anytime?',
      answer: 'Yes, you can downgrade to the free tier at any time. Your premium features will remain active until the end of your current billing period.'
    },
    {
      question: 'Is there a free trial?',
      answer: 'Yes! You can try premium features free for 7 days. No credit card required to start your trial.'
    },
    {
      question: 'What payment methods do you accept?',
      answer: 'We accept all major credit cards, debit cards, and PayPal. All payments are processed securely through Stripe.'
    },
    {
      question: 'Can I change my billing cycle?',
      answer: 'Yes, you can switch between monthly and yearly billing at any time. Yearly plans offer a 17% discount compared to monthly billing.'
    }
  ]

  const handleUpgrade = async () => {
    try {
      // Redirect to Stripe checkout
      const response = await fetch('/api/stripe/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          priceId: billingCycle === 'monthly' ? 'price_monthly' : 'price_yearly',
          successUrl: `${window.location.origin}/dashboard?upgraded=true`,
          cancelUrl: `${window.location.origin}/premium`,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        if (errorData.error === 'Payment processing is not configured') {
          // Show a message that payment is not configured
          alert('Payment processing is not configured. Please contact support to set up payment processing.')
          return
        }
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const { url } = await response.json()
      if (url) {
        window.location.href = url
      }
    } catch (error) {
      console.error('Error creating checkout session:', error)
      // Show user-friendly error message
      alert('Unable to process payment at this time. Please try again later or contact support.')
    }
  }

  const toggleFaq = (index: number) => {
    setExpandedFaq(expandedFaq === index ? null : index)
  }

  return (
    <>
      <Head>
        <title>Premium - Casablanca Insight</title>
        <meta name="description" content="Unlock premium features including GAAP financials, AI summaries, portfolio analytics, and more with Casablanca Insight Premium." />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-dark-bg">
        <Header />

        <main>
          {/* Hero Section */}
          <section className="bg-gradient-to-br from-casablanca-blue to-blue-600 text-white py-20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
              <h1 className="text-4xl md:text-6xl font-bold mb-6">
                Unlock More with Casablanca Insight Premium
              </h1>
              <p className="text-xl md:text-2xl text-blue-100 mb-8 max-w-3xl mx-auto">
                Get access to advanced financial data, AI-powered insights, and professional portfolio tools
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={handleUpgrade}
                  className="bg-white text-casablanca-blue px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors"
                >
                  Start Free Trial
                </button>
                <button
                  onClick={() => document.getElementById('pricing')?.scrollIntoView({ behavior: 'smooth' })}
                  className="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white hover:text-casablanca-blue transition-colors"
                >
                  View Pricing
                </button>
              </div>
            </div>
          </section>

          {/* Feature List */}
          <section className="py-20 bg-white dark:bg-dark-card">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-16">
                <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
                  Pro-Only Features
                </h2>
                <p className="text-xl text-gray-600 dark:text-gray-400">
                  Everything you need for professional financial analysis
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {features.map((feature, index) => (
                  <Link 
                    key={index} 
                    href={feature.href}
                    className="text-center p-6 rounded-lg bg-gray-50 dark:bg-dark-bg hover:bg-gray-100 dark:hover:bg-dark-hover transition-colors cursor-pointer group"
                  >
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-casablanca-blue text-white rounded-full mb-4 group-hover:bg-blue-600 transition-colors">
                      <feature.icon className="w-8 h-8" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      {feature.description}
                    </p>
                    <div className="mt-4 text-sm text-casablanca-blue group-hover:text-blue-600 transition-colors">
                      Try it now →
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </section>

          {/* Comparison Table */}
          <section className="py-20 bg-gray-50 dark:bg-dark-bg">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-16">
                <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
                  Free vs Premium
                </h2>
                <p className="text-xl text-gray-600 dark:text-gray-400">
                  See what you get with each plan
                </p>
              </div>

              <div className="bg-white dark:bg-dark-card rounded-lg shadow-lg overflow-hidden">
                <div className="grid grid-cols-3 bg-gray-50 dark:bg-dark-bg">
                  <div className="p-6 text-center">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Feature</h3>
                  </div>
                  <div className="p-6 text-center border-l border-gray-200 dark:border-dark-border">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Free</h3>
                  </div>
                  <div className="p-6 text-center border-l border-gray-200 dark:border-dark-border bg-casablanca-blue text-white">
                    <h3 className="text-lg font-semibold">Premium</h3>
                  </div>
                </div>

                {comparisonData.map((item, index) => (
                  <div key={index} className="grid grid-cols-3 border-t border-gray-200 dark:border-dark-border">
                    <div className="p-6 flex items-center">
                      <span className="text-gray-900 dark:text-white font-medium">{item.feature}</span>
                    </div>
                    <div className="p-6 flex items-center justify-center border-l border-gray-200 dark:border-dark-border">
                      {item.free ? (
                        <CheckIcon className="w-6 h-6 text-green-500" />
                      ) : (
                        <XMarkIcon className="w-6 h-6 text-gray-400" />
                      )}
                    </div>
                    <div className="p-6 flex items-center justify-center border-l border-gray-200 dark:border-dark-border bg-blue-50 dark:bg-blue-900/20">
                      {item.premium ? (
                        <CheckIcon className="w-6 h-6 text-green-500" />
                      ) : (
                        <XMarkIcon className="w-6 h-6 text-gray-400" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Pricing Block */}
          <section id="pricing" className="py-20 bg-white dark:bg-dark-card">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
                Simple, Transparent Pricing
              </h2>
              <p className="text-xl text-gray-600 dark:text-gray-400 mb-12">
                Choose the plan that works best for you
              </p>

              {/* Billing Toggle */}
              <div className="flex items-center justify-center mb-8">
                <span className={`mr-4 text-sm ${billingCycle === 'monthly' ? 'text-gray-900 dark:text-white' : 'text-gray-500'}`}>
                  Monthly
                </span>
                <button
                  onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    billingCycle === 'yearly' ? 'bg-casablanca-blue' : 'bg-gray-200'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      billingCycle === 'yearly' ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
                <span className={`ml-4 text-sm ${billingCycle === 'yearly' ? 'text-gray-900 dark:text-white' : 'text-gray-500'}`}>
                  Yearly <span className="text-green-600 font-semibold">(Save 17%)</span>
                </span>
              </div>

              {/* Pricing Card */}
              <div className="bg-gradient-to-br from-casablanca-blue to-blue-600 rounded-2xl p-8 text-white max-w-md mx-auto">
                <h3 className="text-2xl font-bold mb-4">Premium</h3>
                <div className="mb-6">
                  <span className="text-4xl font-bold">
                    ${billingCycle === 'monthly' ? '9' : '90'}
                  </span>
                  <span className="text-xl text-blue-100">
                    /{billingCycle === 'monthly' ? 'month' : 'year'}
                  </span>
                </div>
                <ul className="text-left mb-8 space-y-3">
                  {features.map((feature, index) => (
                    <li key={index} className="flex items-center">
                      <CheckIcon className="w-5 h-5 text-green-400 mr-3 flex-shrink-0" />
                      <span>{feature.title}</span>
                    </li>
                  ))}
                </ul>
                <button
                  onClick={handleUpgrade}
                  className="w-full bg-white text-casablanca-blue py-4 px-6 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors"
                >
                  {billingCycle === 'monthly' ? 'Start Free Trial' : 'Start Free Trial'}
                </button>
                <p className="text-sm text-blue-100 mt-4">
                  7-day free trial • Cancel anytime
                </p>
              </div>
            </div>
          </section>

          {/* FAQ Section */}
          <section className="py-20 bg-gray-50 dark:bg-dark-bg">
            <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-16">
                <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
                  Frequently Asked Questions
                </h2>
                <p className="text-xl text-gray-600 dark:text-gray-400">
                  Everything you need to know about Premium
                </p>
              </div>

              <div className="space-y-4">
                {faqs.map((faq, index) => (
                  <div key={index} className="bg-white dark:bg-dark-card rounded-lg border border-gray-200 dark:border-dark-border">
                    <button
                      onClick={() => toggleFaq(index)}
                      className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 dark:hover:bg-dark-hover transition-colors"
                    >
                      <span className="font-medium text-gray-900 dark:text-white">
                        {faq.question}
                      </span>
                      {expandedFaq === index ? (
                        <ChevronUpIcon className="w-5 h-5 text-gray-500" />
                      ) : (
                        <ChevronDownIcon className="w-5 h-5 text-gray-500" />
                      )}
                    </button>
                    {expandedFaq === index && (
                      <div className="px-6 pb-4">
                        <p className="text-gray-600 dark:text-gray-400">
                          {faq.answer}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Upgrade CTA */}
          <section className="py-20 bg-casablanca-blue text-white">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Ready to Upgrade?
              </h2>
              <p className="text-xl text-blue-100 mb-8">
                Join thousands of investors who trust Casablanca Insight Premium
              </p>
              <button
                onClick={handleUpgrade}
                className="bg-white text-casablanca-blue px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors"
              >
                Upgrade to Premium
              </button>
            </div>
          </section>
        </main>

        <Footer />
      </div>
    </>
  )
} 