import Head from 'next/head'
import { useState } from 'react'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import NewsletterSignup from '@/components/NewsletterSignup'
import { 
  EnvelopeIcon, 
  ClockIcon, 
  ChartBarIcon, 
  GlobeAltIcon,
  CheckCircleIcon,
  StarIcon,
  UsersIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'

export default function NewsletterPage() {
  const [activeTab, setActiveTab] = useState('overview')

  const features = [
    {
      icon: ClockIcon,
      title: 'Daily Delivery',
      description: 'Get market insights delivered to your inbox every morning at 8:00 AM'
    },
    {
      icon: ChartBarIcon,
      title: 'Market Analysis',
      description: 'AI-powered analysis of MASI, MADEX, and top movers'
    },
    {
      icon: GlobeAltIcon,
      title: 'Multi-language',
      description: 'Available in English, French, and Arabic'
    },
    {
      icon: StarIcon,
      title: 'Premium Content',
      description: 'Exclusive insights and early access to market reports'
    }
  ]

  const sampleContent = [
    {
      title: 'Market Overview',
      content: 'MASI index gained 1.2% yesterday, led by banking sector...'
    },
    {
      title: 'Top Movers',
      content: 'ATW +2.1%, IAM -0.8%, CIH +1.5%...'
    },
    {
      title: 'Economic Indicators',
      content: 'Inflation rate at 2.1%, Dirham stable against Euro...'
    },
    {
      title: 'AI Insights',
      content: 'Our AI predicts continued strength in financial services...'
    }
  ]

  const testimonials = [
    {
      name: 'Ahmed Benali',
      role: 'Portfolio Manager',
      company: 'Moroccan Investment Fund',
      content: 'Morning Maghreb gives me the edge I need to make informed decisions before the market opens.',
      rating: 5
    },
    {
      name: 'Fatima Zahra',
      role: 'Retail Investor',
      company: 'Individual Trader',
      content: 'The daily insights help me understand market trends and make better investment choices.',
      rating: 5
    },
    {
      name: 'Karim El Amrani',
      role: 'Financial Analyst',
      company: 'Casablanca Securities',
      content: 'Professional-grade analysis delivered in an easy-to-understand format. Highly recommended.',
      rating: 5
    }
  ]

  const tabs = [
    { id: 'overview', label: 'Overview', icon: DocumentTextIcon },
    { id: 'features', label: 'Features', icon: StarIcon },
    { id: 'sample', label: 'Sample Content', icon: EnvelopeIcon },
    { id: 'testimonials', label: 'Testimonials', icon: UsersIcon }
  ]

  return (
    <>
      <Head>
        <title>Morning Maghreb Newsletter - Casablanca Insight</title>
        <meta 
          name="description" 
          content="Subscribe to Morning Maghreb - your daily source for Moroccan market insights, CSE analysis, and AI-powered financial intelligence." 
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Header />

        <main className="px-4 py-6 max-w-7xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-casablanca-blue rounded-full mb-6">
              <EnvelopeIcon className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
              Morning Maghreb
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
              Your daily source for Moroccan market insights, CSE analysis, and AI-powered financial intelligence. 
              Stay ahead of the market with our comprehensive morning digest.
            </p>
            
            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
                <div className="text-2xl font-bold text-casablanca-blue">2,500+</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Active Subscribers</div>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
                <div className="text-2xl font-bold text-casablanca-blue">98%</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Open Rate</div>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
                <div className="text-2xl font-bold text-casablanca-blue">365</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Days Per Year</div>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="mb-8">
            <div className="flex flex-wrap gap-2 justify-center">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-casablanca-blue text-white'
                      : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-600'
                  }`}
                >
                  <tab.icon className="h-4 w-4" />
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          <div className="mb-12">
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                    What is Morning Maghreb?
                  </h2>
                  <div className="space-y-4 text-gray-600 dark:text-gray-300">
                    <p>
                      Morning Maghreb is your comprehensive daily digest of the Moroccan financial markets, 
                      delivered to your inbox every morning at 8:00 AM. Our AI-powered analysis covers 
                      everything you need to know about the Casablanca Stock Exchange (CSE).
                    </p>
                    <p>
                      From MASI and MADEX index movements to individual stock performance, economic indicators, 
                      and market sentiment analysis, we provide the insights you need to make informed 
                      investment decisions.
                    </p>
                    <p>
                      Whether you're a professional investor, retail trader, or simply interested in 
                      the Moroccan economy, Morning Maghreb keeps you informed and ahead of the curve.
                    </p>
                  </div>
                  
                  <div className="mt-8">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                      What You'll Get:
                    </h3>
                    <ul className="space-y-2">
                      {[
                        'Daily market overview and index performance',
                        'Top gainers and losers analysis',
                        'Economic indicators and macro trends',
                        'AI-powered market sentiment analysis',
                        'Sector-specific insights and opportunities',
                        'Trading volume analysis and liquidity insights',
                        'Regulatory updates and market news',
                        'Weekly investment themes and strategies'
                      ].map((item, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <CheckCircleIcon className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-600 dark:text-gray-300">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
                
                <div>
                  <NewsletterSignup 
                    title="Start Your Day Informed"
                    subtitle="Join 2,500+ investors who trust Morning Maghreb"
                    cta="Subscribe Free"
                  />
                </div>
              </div>
            )}

            {activeTab === 'features' && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-8 text-center">
                  Why Choose Morning Maghreb?
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                  {features.map((feature, index) => (
                    <div key={index} className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
                      <div className="flex items-start gap-4">
                        <div className="flex-shrink-0">
                          <feature.icon className="h-8 w-8 text-casablanca-blue" />
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                            {feature.title}
                          </h3>
                          <p className="text-gray-600 dark:text-gray-300">
                            {feature.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="bg-gradient-to-r from-casablanca-blue to-blue-600 rounded-lg p-8 text-white text-center">
                  <h3 className="text-2xl font-bold mb-4">
                    Ready to Get Started?
                  </h3>
                  <p className="text-blue-100 mb-6">
                    Join thousands of investors who start their day with Morning Maghreb
                  </p>
                  <NewsletterSignup 
                    title=""
                    subtitle=""
                    cta="Subscribe Now"
                  />
                </div>
              </div>
            )}

            {activeTab === 'sample' && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-8 text-center">
                  Sample Newsletter Content
                </h2>
                
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8 mb-8">
                  <div className="border-b border-gray-200 dark:border-gray-600 pb-4 mb-6">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                      Morning Maghreb - December 18, 2024
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      Your daily digest of Moroccan market insights
                    </p>
                  </div>
                  
                  <div className="space-y-6">
                    {sampleContent.map((section, index) => (
                      <div key={index} className="border-b border-gray-100 dark:border-gray-700 pb-4 last:border-b-0">
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                          📊 {section.title}
                        </h4>
                        <p className="text-gray-600 dark:text-gray-300">
                          {section.content}
                        </p>
                      </div>
                    ))}
                  </div>
                  
                  <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-600">
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      This is a sample of our daily newsletter content. Actual content may vary based on market conditions and news.
                    </p>
                  </div>
                </div>

                <div className="text-center">
                  <NewsletterSignup 
                    title="Get the Real Thing"
                    subtitle="Subscribe to receive actual Morning Maghreb newsletters"
                    cta="Subscribe Free"
                  />
                </div>
              </div>
            )}

            {activeTab === 'testimonials' && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-8 text-center">
                  What Our Subscribers Say
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  {testimonials.map((testimonial, index) => (
                    <div key={index} className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
                      <div className="flex items-center gap-1 mb-4">
                        {[...Array(testimonial.rating)].map((_, i) => (
                          <StarIcon key={i} className="h-4 w-4 text-yellow-400 fill-current" />
                        ))}
                      </div>
                      <p className="text-gray-600 dark:text-gray-300 mb-4 italic">
                        "{testimonial.content}"
                      </p>
                      <div>
                        <div className="font-semibold text-gray-900 dark:text-white">
                          {testimonial.name}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {testimonial.role} at {testimonial.company}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="text-center">
                  <NewsletterSignup 
                    title="Join Our Community"
                    subtitle="Become part of our growing community of informed investors"
                    cta="Subscribe Today"
                  />
                </div>
              </div>
            )}
          </div>

          {/* FAQ Section */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">
              Frequently Asked Questions
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  How often is the newsletter sent?
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Morning Maghreb is delivered daily at 8:00 AM Moroccan time, Monday through Friday.
                </p>
              </div>
              
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  Is it really free?
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Yes! Morning Maghreb is completely free. We believe everyone should have access to quality market insights.
                </p>
              </div>
              
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  Can I unsubscribe anytime?
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Absolutely. You can unsubscribe at any time by clicking the unsubscribe link in any newsletter email.
                </p>
              </div>
              
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  What languages are supported?
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Morning Maghreb is available in English, French, and Arabic. You can choose your preferred language.
                </p>
              </div>
              
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  Do you share my email with third parties?
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  No, we never share your email address with third parties. Your privacy is important to us.
                </p>
              </div>
              
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  How accurate is the market data?
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  We source our data from official exchanges and reliable financial data providers to ensure accuracy.
                </p>
              </div>
            </div>
          </div>

          {/* Final CTA */}
          <div className="text-center">
            <div className="bg-gradient-to-r from-casablanca-blue to-blue-600 rounded-lg p-8 text-white">
              <h2 className="text-3xl font-bold mb-4">
                Start Your Day with Market Intelligence
              </h2>
              <p className="text-xl text-blue-100 mb-6">
                Join thousands of investors who trust Morning Maghreb for their daily market insights
              </p>
              <NewsletterSignup 
                title=""
                subtitle=""
                cta="Subscribe to Morning Maghreb"
              />
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </>
  )
} 