import { useState } from 'react'
import { PlusIcon } from '@heroicons/react/24/outline'
import { AddHoldingRequest, portfolioService } from '@/lib/portfolioService'
import toast from 'react-hot-toast'

interface AddHoldingFormProps {
  portfolioId: string
  onHoldingAdded: () => void
}

export default function AddHoldingForm({ portfolioId, onHoldingAdded }: AddHoldingFormProps) {
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState<AddHoldingRequest>({
    ticker: '',
    quantity: 0,
    purchase_price: 0,
    purchase_date: new Date().toISOString().split('T')[0],
    notes: ''
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.ticker || formData.quantity <= 0 || formData.purchase_price <= 0) {
      toast.error('Please fill in all required fields correctly')
      return
    }

    setLoading(true)
    try {
      await portfolioService.addHolding(portfolioId, formData)
      toast.success('Holding added successfully')
      onHoldingAdded()
      setShowForm(false)
      setFormData({
        ticker: '',
        quantity: 0,
        purchase_price: 0,
        purchase_date: new Date().toISOString().split('T')[0],
        notes: ''
      })
    } catch (error) {
      console.error('Error adding holding:', error)
      toast.error('Failed to add holding')
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (field: keyof AddHoldingRequest, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  if (!showForm) {
    return (
      <button
        onClick={() => setShowForm(true)}
        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-casablanca-blue hover:bg-casablanca-blue-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-casablanca-blue"
      >
        <PlusIcon className="h-4 w-4 mr-2" />
        Add Holding
      </button>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
        Add New Holding
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="ticker" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Ticker Symbol *
            </label>
            <input
              type="text"
              id="ticker"
              value={formData.ticker}
              onChange={(e) => handleInputChange('ticker', e.target.value.toUpperCase())}
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-casablanca-blue focus:border-casablanca-blue dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder="e.g., ATW"
              required
            />
          </div>
          
          <div>
            <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Number of Shares *
            </label>
            <input
              type="number"
              id="quantity"
              value={formData.quantity}
              onChange={(e) => handleInputChange('quantity', Number(e.target.value))}
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-casablanca-blue focus:border-casablanca-blue dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder="100"
              min="1"
              step="1"
              required
            />
          </div>
          
          <div>
            <label htmlFor="purchase_price" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Purchase Price (MAD) *
            </label>
            <input
              type="number"
              id="purchase_price"
              value={formData.purchase_price}
              onChange={(e) => handleInputChange('purchase_price', Number(e.target.value))}
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-casablanca-blue focus:border-casablanca-blue dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder="45.50"
              min="0.01"
              step="0.01"
              required
            />
          </div>
          
          <div>
            <label htmlFor="purchase_date" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Purchase Date
            </label>
            <input
              type="date"
              id="purchase_date"
              value={formData.purchase_date}
              onChange={(e) => handleInputChange('purchase_date', e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-casablanca-blue focus:border-casablanca-blue dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>
        </div>
        
        <div>
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Notes
          </label>
          <textarea
            id="notes"
            value={formData.notes}
            onChange={(e) => handleInputChange('notes', e.target.value)}
            rows={3}
            className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-casablanca-blue focus:border-casablanca-blue dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder="Optional notes about this investment..."
          />
        </div>
        
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => setShowForm(false)}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-casablanca-blue"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-casablanca-blue hover:bg-casablanca-blue-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-casablanca-blue disabled:opacity-50"
          >
            {loading ? 'Adding...' : 'Add Holding'}
          </button>
        </div>
      </form>
    </div>
  )
} 