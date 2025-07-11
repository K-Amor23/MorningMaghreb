import { useState } from 'react'
import { 
  PlusIcon, 
  MinusIcon, 
  PencilIcon, 
  TrashIcon, 
  CheckIcon, 
  XMarkIcon 
} from '@heroicons/react/24/outline'
import { PortfolioHolding, portfolioService } from '@/lib/portfolioService'
import toast from 'react-hot-toast'

interface PortfolioHoldingsProps {
  portfolioId: string
  holdings: PortfolioHolding[]
  onHoldingsUpdate: () => void
}

interface EditingHolding {
  id: string
  field: 'quantity' | 'purchase_price' | 'notes'
  value: string | number
}

export default function PortfolioHoldings({ 
  portfolioId, 
  holdings, 
  onHoldingsUpdate 
}: PortfolioHoldingsProps) {
  const [editing, setEditing] = useState<EditingHolding | null>(null)
  const [loading, setLoading] = useState<string | null>(null)

  const handleQuantityAdjustment = async (holdingId: string, adjustment: number) => {
    setLoading(holdingId)
    try {
      await portfolioService.adjustHoldingQuantity(portfolioId, holdingId, adjustment)
      toast.success('Portfolio updated successfully')
      onHoldingsUpdate()
    } catch (error) {
      console.error('Error adjusting quantity:', error)
      toast.error('Failed to update portfolio')
    } finally {
      setLoading(null)
    }
  }

  const handleDeleteHolding = async (holdingId: string) => {
    if (!confirm('Are you sure you want to remove this holding?')) {
      return
    }

    setLoading(holdingId)
    try {
      await portfolioService.deleteHolding(portfolioId, holdingId)
      toast.success('Holding removed successfully')
      onHoldingsUpdate()
    } catch (error) {
      console.error('Error deleting holding:', error)
      toast.error('Failed to remove holding')
    } finally {
      setLoading(null)
    }
  }

  const startEditing = (holdingId: string, field: 'quantity' | 'purchase_price' | 'notes', value: string | number) => {
    setEditing({ id: holdingId, field, value })
  }

  const cancelEditing = () => {
    setEditing(null)
  }

  const saveEdit = async () => {
    if (!editing) return

    const holding = holdings.find(h => h.id === editing.id)
    if (!holding) return

    setLoading(editing.id)
    try {
      const updateData: any = {}
      
      if (editing.field === 'quantity') {
        updateData.quantity = Number(editing.value)
      } else if (editing.field === 'purchase_price') {
        updateData.purchase_price = Number(editing.value)
      } else if (editing.field === 'notes') {
        updateData.notes = String(editing.value)
      }

      await portfolioService.updateHolding(portfolioId, editing.id, updateData)
      toast.success('Holding updated successfully')
      onHoldingsUpdate()
      setEditing(null)
    } catch (error) {
      console.error('Error updating holding:', error)
      toast.error('Failed to update holding')
    } finally {
      setLoading(null)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      saveEdit()
    } else if (e.key === 'Escape') {
      cancelEditing()
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'MAD',
      minimumFractionDigits: 2
    }).format(value)
  }

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Holdings</h2>
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Stock
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Shares
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Avg Price
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Current Price
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Change
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Value
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {holdings.map((holding) => {
              const isEditing = editing?.id === holding.id
              const isFieldEditing = editing?.field
              const isLoading = loading === holding.id
              
              return (
                <tr key={holding.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {holding.ticker}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {holding.name}
                      </div>
                    </div>
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap">
                    {isEditing && isFieldEditing === 'quantity' ? (
                      <div className="flex items-center space-x-2">
                                                 <input
                           type="number"
                           value={editing?.value || ''}
                           onChange={(e) => editing && setEditing({ ...editing, value: e.target.value })}
                           onKeyDown={handleKeyPress}
                           className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-casablanca-blue focus:border-transparent"
                           autoFocus
                         />
                        <button
                          onClick={saveEdit}
                          disabled={isLoading}
                          className="text-green-600 hover:text-green-800"
                        >
                          <CheckIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={cancelEditing}
                          className="text-red-600 hover:text-red-800"
                        >
                          <XMarkIcon className="h-4 w-4" />
                        </button>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-900 dark:text-white">
                          {holding.quantity}
                        </span>
                        <button
                          onClick={() => startEditing(holding.id!, 'quantity', holding.quantity)}
                          className="text-gray-400 hover:text-gray-600"
                        >
                          <PencilIcon className="h-3 w-3" />
                        </button>
                      </div>
                    )}
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap">
                    {isEditing && isFieldEditing === 'purchase_price' ? (
                      <div className="flex items-center space-x-2">
                                                 <input
                           type="number"
                           step="0.01"
                           value={editing?.value || ''}
                           onChange={(e) => editing && setEditing({ ...editing, value: e.target.value })}
                           onKeyDown={handleKeyPress}
                           className="w-24 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-casablanca-blue focus:border-transparent"
                           autoFocus
                         />
                        <button
                          onClick={saveEdit}
                          disabled={isLoading}
                          className="text-green-600 hover:text-green-800"
                        >
                          <CheckIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={cancelEditing}
                          className="text-red-600 hover:text-red-800"
                        >
                          <XMarkIcon className="h-4 w-4" />
                        </button>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-900 dark:text-white">
                          {formatCurrency(holding.purchase_price)}
                        </span>
                        <button
                          onClick={() => startEditing(holding.id!, 'purchase_price', holding.purchase_price)}
                          className="text-gray-400 hover:text-gray-600"
                        >
                          <PencilIcon className="h-3 w-3" />
                        </button>
                      </div>
                    )}
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {holding.current_price ? formatCurrency(holding.current_price) : 'N/A'}
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap">
                    {holding.total_gain_loss_percent !== undefined && (
                      <span className={`text-sm font-medium ${
                        holding.total_gain_loss_percent >= 0 
                          ? 'text-green-600 dark:text-green-400' 
                          : 'text-red-600 dark:text-red-400'
                      }`}>
                        {formatPercent(holding.total_gain_loss_percent)}
                      </span>
                    )}
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {holding.current_value ? formatCurrency(holding.current_value) : 'N/A'}
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      {/* Quantity adjustment buttons */}
                      <button
                        onClick={() => handleQuantityAdjustment(holding.id!, 1)}
                        disabled={isLoading}
                        className="text-green-600 hover:text-green-800 disabled:opacity-50"
                        title="Add 1 share"
                      >
                        <PlusIcon className="h-4 w-4" />
                      </button>
                      
                      <button
                        onClick={() => handleQuantityAdjustment(holding.id!, -1)}
                        disabled={isLoading}
                        className="text-red-600 hover:text-red-800 disabled:opacity-50"
                        title="Remove 1 share"
                      >
                        <MinusIcon className="h-4 w-4" />
                      </button>
                      
                      {/* Delete button */}
                      <button
                        onClick={() => handleDeleteHolding(holding.id!)}
                        disabled={isLoading}
                        className="text-red-600 hover:text-red-800 disabled:opacity-50"
                        title="Remove holding"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      
      {holdings.length === 0 && (
        <div className="px-6 py-8 text-center">
          <p className="text-gray-500 dark:text-gray-400">
            No holdings yet. Add your first investment to start tracking your portfolio.
          </p>
        </div>
      )}
    </div>
  )
} 