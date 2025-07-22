import React, { useState } from 'react'
import { 
  ShieldCheckIcon, 
  ExclamationTriangleIcon, 
  ClockIcon, 
  ChartBarIcon,
  InformationCircleIcon,
  CurrencyDollarIcon,
  ScaleIcon,
  DocumentTextIcon,
  ArrowTrendingUpIcon,
  PauseIcon
} from '@heroicons/react/24/outline'

export default function MoroccanMarketInfo() {
  const [activeSection, setActiveSection] = useState('overview')

  const sections = [
    { id: 'overview', label: 'Overview', icon: InformationCircleIcon },
    { id: 'guardrails', label: 'Trading Guardrails', icon: ShieldCheckIcon },
    { id: 'limits', label: 'Price Limits', icon: ChartBarIcon },
    { id: 'halts', label: 'Trading Halts', icon: PauseIcon },
    { id: 'circuit-breakers', label: 'Circuit Breakers', icon: ExclamationTriangleIcon },
    { id: 'regulations', label: 'Regulations', icon: ScaleIcon },
    { id: 'penalties', label: 'Penalties', icon: DocumentTextIcon }
  ]

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            CSE Trading Rules & Compliance Guide
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Comprehensive guide to Casablanca Stock Exchange trading rules, guardrails, and regulatory compliance
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
          <nav className="-mb-px flex space-x-8 overflow-x-auto">
            {sections.map((section) => {
              const Icon = section.icon
              return (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                    activeSection === section.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{section.label}</span>
                </button>
              )
            })}
          </nav>
        </div>

        {/* Content Sections */}
        <div className="space-y-6">
          {activeSection === 'overview' && <OverviewSection />}
          {activeSection === 'guardrails' && <GuardrailsSection />}
          {activeSection === 'limits' && <PriceLimitsSection />}
          {activeSection === 'halts' && <TradingHaltsSection />}
          {activeSection === 'circuit-breakers' && <CircuitBreakersSection />}
          {activeSection === 'regulations' && <RegulationsSection />}
          {activeSection === 'penalties' && <PenaltiesSection />}
        </div>
      </div>
    </div>
  )
}

function OverviewSection() {
  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <InformationCircleIcon className="w-6 h-6 mr-2 text-blue-500" />
          CSE Trading Rules Overview
        </h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-2">Key Principles</h3>
            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Market stability and investor protection</li>
              <li>• Fair and orderly trading</li>
              <li>• Prevention of market manipulation</li>
              <li>• Transparency and disclosure</li>
            </ul>
          </div>
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-2">Trading Hours</h3>
            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Pre-market: 9:00 AM - 9:30 AM</li>
              <li>• Regular trading: 9:30 AM - 3:30 PM</li>
              <li>• Post-market: 3:30 PM - 4:00 PM</li>
              <li>• Monday to Friday (excluding holidays)</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-6">
          <div className="flex items-center mb-2">
            <ShieldCheckIcon className="w-5 h-5 text-blue-500 mr-2" />
            <h3 className="font-medium text-blue-900 dark:text-blue-100">Daily Price Limits</h3>
          </div>
          <p className="text-sm text-blue-700 dark:text-blue-300">
            ±10% maximum daily price movement for most securities
          </p>
        </div>

        <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-6">
          <div className="flex items-center mb-2">
            <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500 mr-2" />
            <h3 className="font-medium text-yellow-900 dark:text-yellow-100">Circuit Breakers</h3>
          </div>
          <p className="text-sm text-yellow-700 dark:text-yellow-300">
            Automatic trading halts on 15%+ price drops
          </p>
        </div>

        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-6">
          <div className="flex items-center mb-2">
            <ClockIcon className="w-5 h-5 text-green-500 mr-2" />
            <h3 className="font-medium text-green-900 dark:text-green-100">Trading Halts</h3>
          </div>
          <p className="text-sm text-green-700 dark:text-green-300">
            Temporary suspensions for news, volatility, or regulatory reasons
          </p>
        </div>
      </div>
    </div>
  )
}

function GuardrailsSection() {
  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <ShieldCheckIcon className="w-6 h-6 mr-2 text-blue-500" />
          Trading Guardrails & Protections
        </h2>
        
        <div className="space-y-6">
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Order Size Limits</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Maximum Order Size</h4>
                <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                  <li>• 5% of average daily volume</li>
                  <li>• Maximum 100,000 shares per order</li>
                  <li>• Large orders may be split automatically</li>
                </ul>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Position Limits</h4>
                <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                  <li>• Maximum 10% ownership per company</li>
                  <li>• Institutional limits: 25% per company</li>
                  <li>• Foreign investor limits: 49% per company</li>
                </ul>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Volatility Controls</h3>
            <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
              <div className="flex items-start">
                <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500 mr-2 mt-0.5" />
                <div>
                  <h4 className="font-medium text-yellow-900 dark:text-yellow-100 mb-2">Automatic Triggers</h4>
                  <ul className="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
                    <li>• 5% price movement in 5 minutes → Warning</li>
                    <li>• 8% price movement in 10 minutes → Enhanced monitoring</li>
                    <li>• 12% price movement in 15 minutes → Trading pause</li>
                    <li>• 15% price movement → Circuit breaker activation</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Market Manipulation Prevention</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                <h4 className="font-medium text-red-900 dark:text-red-100 mb-2">Prohibited Activities</h4>
                <ul className="text-sm text-red-700 dark:text-red-300 space-y-1">
                  <li>• Wash trading (self-trading)</li>
                  <li>• Spoofing (fake orders)</li>
                  <li>• Layering (multiple orders)</li>
                  <li>• Pump and dump schemes</li>
                  <li>• Insider trading</li>
                </ul>
              </div>
              <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                <h4 className="font-medium text-green-900 dark:text-green-100 mb-2">Monitoring Systems</h4>
                <ul className="text-sm text-green-700 dark:text-green-300 space-y-1">
                  <li>• Real-time order monitoring</li>
                  <li>• Pattern recognition algorithms</li>
                  <li>• Cross-market surveillance</li>
                  <li>• Automated alerts</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function PriceLimitsSection() {
  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <ChartBarIcon className="w-6 h-6 mr-2 text-blue-500" />
          Daily Price Limits & Maximum Amounts
        </h2>
        
        <div className="space-y-6">
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Standard Price Limits</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Security Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Daily Limit</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Description</th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">Regular Stocks</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">±10%</td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">Most listed companies</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">Small Cap</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">±15%</td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">Companies with market cap < 1B MAD</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">Bonds</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">±5%</td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">Government and corporate bonds</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">ETFs</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">±10%</td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">Exchange-traded funds</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Maximum Trading Amounts</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">Per Order Limits</h4>
                <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                  <li>• Maximum order value: 10M MAD</li>
                  <li>• Maximum shares per order: 100,000</li>
                  <li>• Large orders require pre-approval</li>
                  <li>• Block trades: 50,000+ shares</li>
                </ul>
              </div>
              <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                <h4 className="font-medium text-green-900 dark:text-green-100 mb-2">Daily Limits</h4>
                <ul className="text-sm text-green-700 dark:text-green-300 space-y-1">
                  <li>• Individual: 50M MAD daily</li>
                  <li>• Institutional: 500M MAD daily</li>
                  <li>• Foreign investors: 200M MAD daily</li>
                  <li>• Market makers: 1B MAD daily</li>
                </ul>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Special Circumstances</h3>
            <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
              <div className="flex items-start">
                <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500 mr-2 mt-0.5" />
                <div>
                  <h4 className="font-medium text-yellow-900 dark:text-yellow-100 mb-2">Temporary Adjustments</h4>
                  <ul className="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
                    <li>• Earnings announcements: Limits may be adjusted</li>
                    <li>• Market volatility: Reduced limits during stress</li>
                    <li>• New listings: Special limits for first 30 days</li>
                    <li>• Regulatory events: Emergency limit adjustments</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function TradingHaltsSection() {
  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <PauseIcon className="w-6 h-6 mr-2 text-blue-500" />
          Trading Halts & Suspensions
        </h2>
        
        <div className="space-y-6">
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Types of Trading Halts</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-4">
                <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <h4 className="font-medium text-red-900 dark:text-red-100 mb-2">Circuit Breaker Halts</h4>
                  <ul className="text-sm text-red-700 dark:text-red-300 space-y-1">
                    <li>• 15% drop: 15-minute halt</li>
                    <li>• 20% drop: 30-minute halt</li>
                    <li>• 25% drop: Trading day halt</li>
                    <li>• Automatic resumption</li>
                  </ul>
                </div>
                
                <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                  <h4 className="font-medium text-yellow-900 dark:text-yellow-100 mb-2">News Pending Halts</h4>
                  <ul className="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
                    <li>• Material news announcements</li>
                    <li>• Earnings releases</li>
                    <li>• Merger announcements</li>
                    <li>• Regulatory decisions</li>
                  </ul>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">Regulatory Halts</h4>
                  <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                    <li>• Compliance violations</li>
                    <li>• Investigation periods</li>
                    <li>• Suspension orders</li>
                    <li>• Administrative actions</li>
                  </ul>
                </div>
                
                <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 className="font-medium text-green-900 dark:text-green-100 mb-2">Technical Halts</h4>
                  <ul className="text-sm text-green-700 dark:text-green-300 space-y-1">
                    <li>• System maintenance</li>
                    <li>• Data feed issues</li>
                    <li>• Connectivity problems</li>
                    <li>• Emergency procedures</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Halt Duration & Procedures</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Halt Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Typical Duration</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Resumption Process</th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">Circuit Breaker</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">15-30 minutes</td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">Automatic after time period</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">News Pending</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">Until news release</td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">Manual release by exchange</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">Regulatory</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">Variable</td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">Regulatory approval required</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">Technical</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">Minutes to hours</td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">System restoration</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Investor Information During Halts</h3>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
                <li>• <strong>Order Status:</strong> Pending orders remain active but won't execute</li>
                <li>• <strong>Market Data:</strong> Last price before halt is displayed</li>
                <li>• <strong>Notifications:</strong> Exchange provides updates on halt status</li>
                <li>• <strong>Resumption:</strong> 5-minute warning before trading resumes</li>
                <li>• <strong>Opening:</strong> Special opening procedures may apply</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function CircuitBreakersSection() {
  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <ExclamationTriangleIcon className="w-6 h-6 mr-2 text-red-500" />
          Circuit Breakers & Market Protection
        </h2>
        
        <div className="space-y-6">
          <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-6">
            <h3 className="font-medium text-red-900 dark:text-red-100 mb-4">Circuit Breaker Levels</h3>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600 dark:text-red-400">15%</div>
                  <div className="text-sm text-red-700 dark:text-red-300 font-medium">Level 1</div>
                  <div className="text-xs text-red-600 dark:text-red-400 mt-1">15-minute halt</div>
                </div>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">20%</div>
                  <div className="text-sm text-orange-700 dark:text-orange-300 font-medium">Level 2</div>
                  <div className="text-xs text-orange-600 dark:text-orange-400 mt-1">30-minute halt</div>
                </div>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-800 dark:text-red-200">25%</div>
                  <div className="text-sm text-red-800 dark:text-red-200 font-medium">Level 3</div>
                  <div className="text-xs text-red-700 dark:text-red-300 mt-1">Trading day halt</div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Circuit Breaker Triggers</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Individual Stock Triggers</h4>
                <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                  <li>• 15% drop from previous close</li>
                  <li>• 20% drop from previous close</li>
                  <li>• 25% drop from previous close</li>
                  <li>• Based on 5-minute rolling average</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Market-Wide Triggers</h4>
                <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                  <li>• MASI index 7% drop</li>
                  <li>• MASI index 13% drop</li>
                  <li>• MASI index 20% drop</li>
                  <li>• Affects all listed securities</li>
                </ul>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Circuit Breaker Procedures</h3>
            <div className="space-y-4">
              <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                <h4 className="font-medium text-yellow-900 dark:text-yellow-100 mb-2">Before Activation</h4>
                <ul className="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
                  <li>• 5% drop: Warning alerts sent</li>
                  <li>• 10% drop: Enhanced monitoring</li>
                  <li>• 12% drop: Pre-halt notifications</li>
                  <li>• 14% drop: Final warning</li>
                </ul>
              </div>
              
              <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                <h4 className="font-medium text-red-900 dark:text-red-100 mb-2">During Halt</h4>
                <ul className="text-sm text-red-700 dark:text-red-300 space-y-1">
                  <li>• All trading stops immediately</li>
                  <li>• Orders remain in queue</li>
                  <li>• Market data shows last price</li>
                  <li>• Exchange provides updates</li>
                </ul>
              </div>
              
              <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                <h4 className="font-medium text-green-900 dark:text-green-100 mb-2">Resumption Process</h4>
                <ul className="text-sm text-green-700 dark:text-green-300 space-y-1">
                  <li>• 5-minute warning before restart</li>
                  <li>• Special opening auction</li>
                  <li>• Enhanced monitoring period</li>
                  <li>• Gradual return to normal trading</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function RegulationsSection() {
  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <ScaleIcon className="w-6 h-6 mr-2 text-blue-500" />
          Regulatory Framework & Compliance
        </h2>
        
        <div className="space-y-6">
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Regulatory Bodies</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">ACAPS (Autorité de Contrôle des Assurances et de la Prévoyance Sociale)</h4>
                <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                  <li>• Insurance and pension supervision</li>
                  <li>• Investment fund regulation</li>
                  <li>• Market conduct oversight</li>
                  <li>• Consumer protection</li>
                </ul>
              </div>
              <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                <h4 className="font-medium text-green-900 dark:text-green-100 mb-2">Bank Al-Maghrib (BAM)</h4>
                <ul className="text-sm text-green-700 dark:text-green-300 space-y-1">
                  <li>• Central bank supervision</li>
                  <li>• Monetary policy</li>
                  <li>• Banking regulation</li>
                  <li>• Financial stability</li>
                </ul>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Key Regulations</h3>
            <div className="space-y-4">
              <div className="border-l-4 border-blue-500 pl-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-1">Law 44-12 (Capital Market Law)</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Comprehensive framework for capital markets, including trading rules, disclosure requirements, and investor protection measures.
                </p>
              </div>
              
              <div className="border-l-4 border-green-500 pl-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-1">Circular 1/G/2013</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Trading rules and procedures for the Casablanca Stock Exchange, including price limits and circuit breakers.
                </p>
              </div>
              
              <div className="border-l-4 border-yellow-500 pl-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-1">ACAPS Circulars</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Guidelines for investment funds, market conduct, and consumer protection in financial services.
                </p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Compliance Requirements</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">For Investors</h4>
                <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                  <li>• Know Your Customer (KYC) requirements</li>
                  <li>• Anti-Money Laundering (AML) compliance</li>
                  <li>• Tax reporting obligations</li>
                  <li>• Foreign exchange regulations</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">For Brokers</h4>
                <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                  <li>• Licensing requirements</li>
                  <li>• Capital adequacy rules</li>
                  <li>• Client fund segregation</li>
                  <li>• Reporting obligations</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function PenaltiesSection() {
  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <DocumentTextIcon className="w-6 h-6 mr-2 text-red-500" />
          Violations & Penalties
        </h2>
        
        <div className="space-y-6">
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Trading Violations</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Violation</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Penalty</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Severity</th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  <tr>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">Price limit violation</td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">Order rejection + warning</td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">Low</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">Excessive order size</td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">Order rejection + fine</td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">Medium</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">Market manipulation</td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">Account suspension + legal action</td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">High</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">Insider trading</td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">Criminal charges + imprisonment</td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">Critical</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Penalty Structure</h3>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                <h4 className="font-medium text-yellow-900 dark:text-yellow-100 mb-2">Warnings</h4>
                <ul className="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
                  <li>• First-time minor violations</li>
                  <li>• Educational notice</li>
                  <li>• No financial penalty</li>
                  <li>• Recorded for future reference</li>
                </ul>
              </div>
              
              <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                <h4 className="font-medium text-orange-900 dark:text-orange-100 mb-2">Fines</h4>
                <ul className="text-sm text-orange-700 dark:text-orange-300 space-y-1">
                  <li>• 1,000 - 100,000 MAD</li>
                  <li>• Based on violation severity</li>
                  <li>• Repeat violations</li>
                  <li>• Administrative penalties</li>
                </ul>
              </div>
              
              <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                <h4 className="font-medium text-red-900 dark:text-red-100 mb-2">Suspensions</h4>
                <ul className="text-sm text-red-700 dark:text-red-300 space-y-1">
                  <li>• Trading account suspension</li>
                  <li>• 30 days to permanent</li>
                  <li>• Serious violations</li>
                  <li>• Regulatory review required</li>
                </ul>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Appeal Process</h3>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="space-y-3">
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-medium mr-3 mt-0.5">1</div>
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">Notice of Violation</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Receive detailed notice within 5 business days</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-medium mr-3 mt-0.5">2</div>
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">Response Period</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">15 business days to submit appeal</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-medium mr-3 mt-0.5">3</div>
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">Review Process</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Independent committee reviews appeal</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-medium mr-3 mt-0.5">4</div>
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">Final Decision</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Decision issued within 30 business days</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 