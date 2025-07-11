import { useState, useEffect } from 'react'
import { useUser } from '@/lib/useUser'
import toast from 'react-hot-toast'

interface TradingInterfaceProps {
  accountId: string
}

interface StockQuote {
  ticker: string
  name: string
  price: number
  change: number
  changePercent: number
}

interface OrderForm {
  ticker: string
  orderType: 'buy' | 'sell'
  quantity: number
  price: number
  notes: string
}

export default function TradingInterface({ accountId }: TradingInterfaceProps) {
  const { user } = useUser()
  const [availableStocks, setAvailableStocks] = useState<StockQuote[]>([])
  const [selectedStock, setSelectedStock] = useState<StockQuote | null>(null)
  const [orderForm, setOrderForm] = useState<OrderForm>({
    ticker: '',
    orderType: 'buy',
    quantity: 0,
    price: 0,
    notes: ''
  })
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  // Mock stock data for Moroccan stocks
  const mockStocks: StockQuote[] = [
    { ticker: 'ATW', name: 'Attijariwafa Bank', price: 410.10, change: 1.28, changePercent: 0.31 },
    { ticker: 'IAM', name: 'Maroc Telecom', price: 156.30, change: -2.10, changePercent: -1.33 },
    { ticker: 'BCP', name: 'Banque Centrale Populaire', price: 268.60, change: 8.10, changePercent: 3.11 },
    { ticker: 'BMCE', name: 'BMCE Bank', price: 187.40, change: -0.90, changePercent: -0.48 },
    { ticker: 'ONA', name: 'Omnium Nord Africain', price: 456.20, change: 3.40, changePercent: 0.75 },
    { ticker: 'CMT', name: 'Ciments du Maroc', price: 234.50, change: 1.20, changePercent: 0.51 },
    { ticker: 'LAFA', name: 'Lafarge Ciments', price: 189.80, change: -1.50, changePercent: -0.78 },
    { ticker: 'CIH', name: 'CIH Bank', price: 312.25, change: 2.75, changePercent: 0.89 },
    { ticker: 'MNG', name: 'Managem', price: 445.60, change: 5.40, changePercent: 1.23 },
    { ticker: 'TMA', name: 'Taqa Morocco', price: 123.40, change: -0.60, changePercent: -0.48 }
  ]

  useEffect(() => {
    setAvailableStocks(mockStocks)
  }, [])

  useEffect(() => {
    if (selectedStock) {
      setOrderForm(prev => ({
        ...prev,
        ticker: selectedStock.ticker,
        price: selectedStock.price
      }))
    }
  }, [selectedStock])

  const handleStockSelect = (stock: StockQuote) => {
    setSelectedStock(stock)
  }

  const handleOrderTypeChange = (type: 'buy' | 'sell') => {
    setOrderForm(prev => ({ ...prev, orderType: type }))
  }

  const handleQuantityChange = (quantity: number) => {
    setOrderForm(prev => ({ ...prev, quantity }))
  }

  const handlePriceChange = (price: number) => {
    setOrderForm(prev => ({ ...prev, price }))
  }

  const handleNotesChange = (notes: string) => {
    setOrderForm(prev => ({ ...prev, notes }))
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
    return orderForm.orderType === 'buy' ? total + commission : total - commission
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
    return true
  }

  const handleSubmitOrder = async () => {
    if (!validateOrder()) return

    setSubmitting(true)
    try {
      const response = await fetch(`/api/paper-trading/accounts/${accountId}/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ticker: orderForm.ticker,
          order_type: orderForm.orderType,
          quantity: orderForm.quantity,
          price: orderForm.price,
          notes: orderForm.notes
        })
      })

      if (response.ok) {
        const order = await response.json()
        toast.success(`${orderForm.orderType.toUpperCase()} order placed successfully!`)
        
        // Reset form
        setOrderForm({
          ticker: '',
          orderType: 'buy',
          quantity: 0,
          price: 0,
          notes: ''
        })
        setSelectedStock(null)
      } else {
        const error = await response.json()
        toast.error(error.detail || 'Failed to place order')
      }
    } catch (error) {
      console.error('Error placing order:', error)
      toast.error('Error placing order')
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
    if (value > 0) return 'text-green-600 dark:text-green-400'
    if (value < 0) return 'text-red-600 dark:text-red-400'
    return 'text-gray-600 dark:text-gray-400'
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Stock Selection */}
      <div className="space-y-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Select Stock
          </h2>
          
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {availableStocks.map((stock) => (
              <div
                key={stock.ticker}
                onClick={() => handleStockSelect(stock)}
                className={`
                  p-4 rounded-lg border cursor-pointer transition-colors
                  ${selectedStock?.ticker === stock.ticker
                    ? 'border-casablanca-blue bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }
                `}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">
                      {stock.ticker}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {stock.name}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-medium text-gray-900 dark:text-white">
                      {formatCurrency(stock.price)}
                    </div>
                    <div className={`text-sm ${getColorForChange(stock.change)}`}>
                      {formatPercent(stock.changePercent)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Order Form */}
      <div className="space-y-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Place Order
          </h2>

          {selectedStock && (
            <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">
                    {selectedStock.ticker} - {selectedStock.name}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Current Price: {formatCurrency(selectedStock.price)}
                  </div>
                </div>
                <div className={`text-sm font-medium ${getColorForChange(selectedStock.change)}`}>
                  {formatPercent(selectedStock.changePercent)}
                </div>
              </div>
            </div>
          )}

          <form className="space-y-4">
            {/* Order Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Order Type
              </label>
              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={() => handleOrderTypeChange('buy')}
                  className={`
                    flex-1 py-2 px-4 rounded-md font-medium transition-colors
                    ${orderForm.orderType === 'buy'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                    }
                  `}
                >
                  Buy
                </button>
                <button
                  type="button"
                  onClick={() => handleOrderTypeChange('sell')}
                  className={`
                    flex-1 py-2 px-4 rounded-md font-medium transition-colors
                    ${orderForm.orderType === 'sell'
                      ? 'bg-red-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                    }
                  `}
                >
                  Sell
                </button>
              </div>
            </div>

            {/* Quantity */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Quantity
              </label>
              <input
                type="number"
                min="1"
                value={orderForm.quantity || ''}
                onChange={(e) => handleQuantityChange(Number(e.target.value))}
                className="block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-casablanca-blue focus:ring-casablanca-blue sm:text-sm"
                placeholder="Enter quantity"
              />
            </div>

            {/* Price */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Price per Share (MAD)
              </label>
              <input
                type="number"
                min="0.01"
                step="0.01"
                value={orderForm.price || ''}
                onChange={(e) => handlePriceChange(Number(e.target.value))}
                className="block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-casablanca-blue focus:ring-casablanca-blue sm:text-sm"
                placeholder="Enter price"
              />
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Notes (Optional)
              </label>
              <textarea
                value={orderForm.notes}
                onChange={(e) => handleNotesChange(e.target.value)}
                rows={3}
                className="block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-casablanca-blue focus:ring-casablanca-blue sm:text-sm"
                placeholder="Add notes about this trade..."
              />
            </div>

            {/* Order Summary */}
            {orderForm.quantity > 0 && orderForm.price > 0 && (
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                  Order Summary
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Total Value:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {formatCurrency(calculateTotal())}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Commission (0.1%):</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {formatCurrency(calculateCommission())}
                    </span>
                  </div>
                  <div className="border-t border-gray-200 dark:border-gray-600 pt-2">
                    <div className="flex justify-between">
                      <span className="font-medium text-gray-900 dark:text-white">
                        Net Amount:
                      </span>
                      <span className={`font-bold ${orderForm.orderType === 'buy' ? 'text-red-600' : 'text-green-600'}`}>
                        {formatCurrency(calculateNetAmount())}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="button"
              onClick={handleSubmitOrder}
              disabled={submitting || !orderForm.ticker || orderForm.quantity <= 0 || orderForm.price <= 0}
              className={`
                w-full py-3 px-4 rounded-md font-medium transition-colors
                ${orderForm.orderType === 'buy'
                  ? 'bg-green-600 hover:bg-green-700 text-white'
                  : 'bg-red-600 hover:bg-red-700 text-white'
                }
                disabled:opacity-50 disabled:cursor-not-allowed
              `}
            >
              {submitting ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Placing Order...
                </div>
              ) : (
                `Place ${orderForm.orderType.toUpperCase()} Order`
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
} 