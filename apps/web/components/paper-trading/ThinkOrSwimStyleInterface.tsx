import { useState, useEffect, useCallback } from 'react'
import { delayedMarketData, DelayedQuote } from '@/lib/delayedMarketData'
import { useUser } from '@/lib/useUser'
import toast from 'react-hot-toast'
import { 
  ChartBarIcon, 
  ClockIcon, 
  ExclamationTriangleIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  MinusIcon
} from '@heroicons/react/24/outline'

interface ThinkOrSwimStyleInterfaceProps {
  accountId: string
}

interface OrderForm {
  ticker: string
  orderType: 'market' | 'limit' | 'stop' | 'stop_limit'
  side: 'buy' | 'sell'
  quantity: number
  price: number
  stopPrice?: number
  timeInForce: 'day' | 'gtc' | 'ioc'
  notes: string
}

interface Position {
  ticker: string
  name: string
  quantity: number
  averagePrice: number
  currentPrice: number
  marketValue: number
  unrealizedPnL: number
  unrealizedPnLPercent: number
  lastUpdated: string
}

export default function ThinkOrSwimStyleInterface({ accountId }: ThinkOrSwimStyleInterfaceProps) {
  const { user } = useUser()
  const [quotes, setQuotes] = useState<DelayedQuote[]>([])
  const [selectedQuote, setSelectedQuote] = useState<DelayedQuote | null>(null)
  const [positions, setPositions] = useState<Position[]>([])
  const [orderForm, setOrderForm] = useState<OrderForm>({
    ticker: '',
    orderType: 'market',
    side: 'buy',
    quantity: 0,
    price: 0,
    timeInForce: 'day',
    notes: ''
  })
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [showDelayWarning, setShowDelayWarning] = useState(true)

  // Load delayed market data
  const loadMarketData = useCallback(async () => {
    try {
      setLoading(true)
      const marketQuotes = await delayedMarketData.getAllDelayedQuotes()
      setQuotes(marketQuotes)
      
      if (selectedQuote) {
        const updatedQuote = marketQuotes.find(q => q.ticker === selectedQuote.ticker)
        if (updatedQuote) {
          setSelectedQuote(updatedQuote)
          setOrderForm(prev => ({
            ...prev,
            price: updatedQuote.currentPrice
          }))
        }
      }
    } catch (error) {
      console.error('Error loading market data:', error)
      toast.error('Failed to load market data')
    } finally {
      setLoading(false)
    }
  }, [selectedQuote])

  // Load positions
  const loadPositions = useCallback(async () => {
    try {
      // Mock positions - in real implementation, this would come from API
      const mockPositions: Position[] = [
        {
          ticker: 'ATW',
          name: 'Attijariwafa Bank',
          quantity: 100,
          averagePrice: 408.50,
          currentPrice: 410.10,
          marketValue: 41010,
          unrealizedPnL: 160,
          unrealizedPnLPercent: 0.39,
          lastUpdated: new Date().toISOString()
        },
        {
          ticker: 'IAM',
          name: 'Maroc Telecom',
          quantity: 200,
          averagePrice: 158.20,
          currentPrice: 156.30,
          marketValue: 31260,
          unrealizedPnL: -380,
          unrealizedPnLPercent: -1.20,
          lastUpdated: new Date().toISOString()
        }
      ]
      setPositions(mockPositions)
    } catch (error) {
      console.error('Error loading positions:', error)
    }
  }, [])

  // Real-time updates
  useEffect(() => {
    loadMarketData()
    loadPositions()

    // Set up real-time updates every 5 seconds
    const interval = setInterval(() => {
      loadMarketData()
      loadPositions()
    }, 5000)

    return () => clearInterval(interval)
  }, [loadMarketData, loadPositions])

  const handleQuoteSelect = (quote: DelayedQuote) => {
    setSelectedQuote(quote)
    setOrderForm(prev => ({
      ...prev,
      ticker: quote.ticker,
      price: quote.currentPrice
    }))
  }

  const handleOrderTypeChange = (orderType: OrderForm['orderType']) => {
    setOrderForm(prev => ({ ...prev, orderType }))
  }

  const handleSideChange = (side: 'buy' | 'sell') => {
    setOrderForm(prev => ({ ...prev, side }))
  }

  const calculateTotal = () => {
    return orderForm.quantity * orderForm.price
  }

  const calculateCommission = () => {
    const total = calculateTotal()
    return total * 0.001 // 0.1% commission
  }

  const calculateNetAmount = () => {
    const total = calculateTotal()
    const commission = calculateCommission()
    return orderForm.side === 'buy' ? total + commission : total - commission
  }

  const validateOrder = () => {
    if (!orderForm.ticker) {
      toast.error('Please select a stock')
      return false
    }
    if (orderForm.quantity <= 0) {
      toast.error('Quantity must be greater than 0')
      return false
    }
    if (orderForm.price <= 0) {
      toast.error('Price must be greater than 0')
      return false
    }
    if (orderForm.orderType === 'stop_limit' && !orderForm.stopPrice) {
      toast.error('Stop price is required for stop limit orders')
      return false
    }
    return true
  }

  const handleSubmitOrder = async () => {
    if (!validateOrder()) return

    setSubmitting(true)
    try {
      // Simulate order submission with delay
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))

      // Mock order execution
      const order = {
        id: `order-${Date.now()}`,
        accountId,
        ...orderForm,
        status: 'filled',
        filledAt: new Date().toISOString(),
        commission: calculateCommission(),
        totalAmount: calculateTotal()
      }

      toast.success(`Order executed: ${orderForm.side.toUpperCase()} ${orderForm.quantity} ${orderForm.ticker} @ ${orderForm.price}`)
      
      // Reset form
      setOrderForm({
        ticker: '',
        orderType: 'market',
        side: 'buy',
        quantity: 0,
        price: 0,
        timeInForce: 'day',
        notes: ''
      })

      // Reload positions
      loadPositions()
    } catch (error) {
      console.error('Error submitting order:', error)
      toast.error('Failed to submit order')
    } finally {
      setSubmitting(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'MAD',
      minimumFractionDigits: 2
    }).format(amount)
  }

  const formatPercent = (percent: number) => {
    return `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`
  }

  const getColorForChange = (value: number) => {
    if (value > 0) return 'text-green-600'
    if (value < 0) return 'text-red-600'
    return 'text-gray-600'
  }

  return (
    <div className="bg-gray-50 dark:bg-gray-900 min-h-screen">
      {/* Delay Warning Banner */}
      {showDelayWarning && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border-b border-yellow-200 dark:border-yellow-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <ClockIcon className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mr-2" />
                <span className="text-sm text-yellow-800 dark:text-yellow-200">
                  <strong>Delayed Data:</strong> Market data is delayed by 15 minutes for paper trading
                </span>
              </div>
              <button
                onClick={() => setShowDelayWarning(false)}
                className="text-yellow-600 dark:text-yellow-400 hover:text-yellow-800 dark:hover:text-yellow-200"
              >
                <ExclamationTriangleIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Market Data Panel */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Market Data (Delayed)
                </h2>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Symbol
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Price
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Change
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Volume
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        High/Low
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {quotes.map((quote) => (
                      <tr 
                        key={quote.ticker}
                        onClick={() => handleQuoteSelect(quote)}
                        className={`hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer ${
                          selectedQuote?.ticker === quote.ticker ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                        }`}
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {quote.ticker}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              {quote.name}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {formatCurrency(quote.currentPrice)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className={`text-sm font-medium ${getColorForChange(quote.change)}`}>
                            {formatCurrency(quote.change)}
                          </div>
                          <div className={`text-sm ${getColorForChange(quote.changePercent)}`}>
                            {formatPercent(quote.changePercent)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {quote.volume.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {formatCurrency(quote.high)} / {formatCurrency(quote.low)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Trading Panel */}
          <div className="space-y-6">
            {/* Order Entry */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Order Entry
                </h3>
              </div>
              <div className="p-6 space-y-4">
                {/* Selected Stock */}
                {selectedQuote && (
                  <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {selectedQuote.ticker} - {selectedQuote.name}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {formatCurrency(selectedQuote.currentPrice)}
                        </div>
                      </div>
                      <div className={`text-sm font-medium ${getColorForChange(selectedQuote.change)}`}>
                        {formatPercent(selectedQuote.changePercent)}
                      </div>
                    </div>
                  </div>
                )}

                {/* Order Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Order Type
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {(['market', 'limit', 'stop', 'stop_limit'] as const).map((type) => (
                      <button
                        key={type}
                        onClick={() => handleOrderTypeChange(type)}
                        className={`px-3 py-2 text-sm font-medium rounded-md ${
                          orderForm.orderType === type
                            ? 'bg-casablanca-blue text-white'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                        }`}
                      >
                        {type.replace('_', ' ').toUpperCase()}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Buy/Sell Buttons */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Side
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => handleSideChange('buy')}
                      className={`px-4 py-2 text-sm font-medium rounded-md ${
                        orderForm.side === 'buy'
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                      }`}
                    >
                      BUY
                    </button>
                    <button
                      onClick={() => handleSideChange('sell')}
                      className={`px-4 py-2 text-sm font-medium rounded-md ${
                        orderForm.side === 'sell'
                          ? 'bg-red-600 text-white'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                      }`}
                    >
                      SELL
                    </button>
                  </div>
                </div>

                {/* Quantity */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Quantity
                  </label>
                  <input
                    type="number"
                    value={orderForm.quantity}
                    onChange={(e) => setOrderForm(prev => ({ ...prev, quantity: parseInt(e.target.value) || 0 }))}
                    className="mt-1 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-casablanca-blue focus:border-casablanca-blue dark:bg-gray-700 dark:text-white"
                    placeholder="0"
                  />
                </div>

                {/* Price */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Price
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={orderForm.price}
                    onChange={(e) => setOrderForm(prev => ({ ...prev, price: parseFloat(e.target.value) || 0 }))}
                    className="mt-1 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-casablanca-blue focus:border-casablanca-blue dark:bg-gray-700 dark:text-white"
                    placeholder="0.00"
                  />
                </div>

                {/* Stop Price (for stop orders) */}
                {(orderForm.orderType === 'stop' || orderForm.orderType === 'stop_limit') && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Stop Price
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={orderForm.stopPrice || ''}
                      onChange={(e) => setOrderForm(prev => ({ ...prev, stopPrice: parseFloat(e.target.value) || undefined }))}
                      className="mt-1 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-casablanca-blue focus:border-casablanca-blue dark:bg-gray-700 dark:text-white"
                      placeholder="0.00"
                    />
                  </div>
                )}

                {/* Time in Force */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Time in Force
                  </label>
                  <select
                    value={orderForm.timeInForce}
                    onChange={(e) => setOrderForm(prev => ({ ...prev, timeInForce: e.target.value as 'day' | 'gtc' | 'ioc' }))}
                    className="mt-1 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-casablanca-blue focus:border-casablanca-blue dark:bg-gray-700 dark:text-white"
                  >
                    <option value="day">Day</option>
                    <option value="gtc">Good Till Cancelled</option>
                    <option value="ioc">Immediate or Cancel</option>
                  </select>
                </div>

                {/* Notes */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Notes
                  </label>
                  <textarea
                    value={orderForm.notes}
                    onChange={(e) => setOrderForm(prev => ({ ...prev, notes: e.target.value }))}
                    rows={2}
                    className="mt-1 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-casablanca-blue focus:border-casablanca-blue dark:bg-gray-700 dark:text-white"
                    placeholder="Optional notes..."
                  />
                </div>

                {/* Order Summary */}
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Total:</span>
                    <span className="font-medium">{formatCurrency(calculateTotal())}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Commission:</span>
                    <span className="font-medium">{formatCurrency(calculateCommission())}</span>
                  </div>
                  <div className="flex justify-between text-sm font-medium">
                    <span className="text-gray-900 dark:text-white">Net Amount:</span>
                    <span className="text-gray-900 dark:text-white">{formatCurrency(calculateNetAmount())}</span>
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  onClick={handleSubmitOrder}
                  disabled={submitting || !selectedQuote}
                  className="w-full bg-casablanca-blue text-white py-2 px-4 rounded-md hover:bg-casablanca-blue/90 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  {submitting ? 'Submitting...' : `Submit ${orderForm.side.toUpperCase()} Order`}
                </button>
              </div>
            </div>

            {/* Positions */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Positions
                </h3>
              </div>
              <div className="p-6">
                {positions.length === 0 ? (
                  <p className="text-gray-500 dark:text-gray-400 text-center py-4">
                    No positions
                  </p>
                ) : (
                  <div className="space-y-4">
                    {positions.map((position) => (
                      <div key={position.ticker} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <div className="font-medium text-gray-900 dark:text-white">
                              {position.ticker}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              {position.name}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-medium text-gray-900 dark:text-white">
                              {formatCurrency(position.currentPrice)}
                            </div>
                            <div className={`text-sm ${getColorForChange(position.unrealizedPnLPercent)}`}>
                              {formatPercent(position.unrealizedPnLPercent)}
                            </div>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Quantity:</span>
                            <span className="ml-2 font-medium">{position.quantity}</span>
                          </div>
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Avg Price:</span>
                            <span className="ml-2 font-medium">{formatCurrency(position.averagePrice)}</span>
                          </div>
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Market Value:</span>
                            <span className="ml-2 font-medium">{formatCurrency(position.marketValue)}</span>
                          </div>
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Unrealized P&L:</span>
                            <span className={`ml-2 font-medium ${getColorForChange(position.unrealizedPnL)}`}>
                              {formatCurrency(position.unrealizedPnL)}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 