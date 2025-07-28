import React, { useState, useEffect } from 'react'
import { ArrowDownTrayIcon, DocumentArrowDownIcon, ClockIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline'
import { toast } from 'react-hot-toast'
import { checkPremiumAccess, isPremiumEnforced } from '@/lib/featureFlags'

interface Export {
  id: string
  export_type: string
  file_format: string
  status: string
  created_at: string
  download_count: number
  file_size_bytes?: number
}

interface DataExporterProps {
  userSubscriptionTier: string
}

export default function DataExporter({ userSubscriptionTier }: DataExporterProps) {
  const [exports, setExports] = useState<Export[]>([])
  const [loading, setLoading] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(false)

  const [newExport, setNewExport] = useState({
    export_type: 'financials',
    file_format: 'csv',
    filters: {
      tickers: [] as string[],
      period: '',
      include_ratios: true,
      include_gaap_adjustments: true
    },
    include_metadata: true
  })

  const exportTypes = [
    { value: 'financials', label: 'Financial Data', description: 'Income statements, balance sheets, cash flows' },
    { value: 'macro', label: 'Macro Data', description: 'Economic indicators and time-series data' },
    { value: 'portfolio', label: 'Portfolio Data', description: 'Your portfolio holdings and performance' },
    { value: 'custom', label: 'Custom Export', description: 'Custom filtered data export' }
  ]

  const fileFormats = [
    { value: 'csv', label: 'CSV', description: 'Comma-separated values' },
    { value: 'xlsx', label: 'Excel', description: 'Microsoft Excel format' },
    { value: 'json', label: 'JSON', description: 'Structured data format' }
  ]

  const mockTickers = ['ATW', 'IAM', 'BCP', 'BMCE', 'WAA', 'CIH', 'CMT', 'CTM']

  useEffect(() => {
    if (checkPremiumAccess('PREMIUM_FEATURES')) {
      fetchExports()
    }
  }, [userSubscriptionTier])

  const fetchExports = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/exports', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setExports(data)
      } else {
        toast.error('Failed to fetch exports')
      }
    } catch (error) {
      console.error('Error fetching exports:', error)
      toast.error('Failed to fetch exports')
    } finally {
      setLoading(false)
    }
  }

  const createExport = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/exports', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        },
        body: JSON.stringify(newExport)
      })

      if (response.ok) {
        const exportData = await response.json()
        setExports([exportData, ...exports])
        setShowCreateForm(false)
        setNewExport({
          export_type: 'financials',
          file_format: 'csv',
          filters: {
            tickers: [],
            period: '',
            include_ratios: true,
            include_gaap_adjustments: true
          },
          include_metadata: true
        })
        toast.success('Export created successfully')
      } else {
        toast.error('Failed to create export')
      }
    } catch (error) {
      console.error('Error creating export:', error)
      toast.error('Failed to create export')
    } finally {
      setLoading(false)
    }
  }

  const downloadExport = async (exportId: string) => {
    try {
      const response = await fetch(`/api/exports/${exportId}/download`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        }
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `export_${exportId}.${newExport.file_format}`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        toast.success('Export downloaded successfully')
      } else {
        toast.error('Failed to download export')
      }
    } catch (error) {
      console.error('Error downloading export:', error)
      toast.error('Failed to download export')
    }
  }

  const quickExport = async (type: string, format: string) => {
    try {
      setLoading(true)
      let url = ''

      if (type === 'financials') {
        url = `/api/exports/financials/quick?tickers=ATW,IAM,BCP&period=2024-Q3&format=${format}`
      } else if (type === 'macro') {
        url = `/api/exports/macro/quick?series_codes=cpi,gdp,policy_rate&start_date=2024-01-01&end_date=2024-12-31&format=${format}`
      }

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        }
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `quick_export_${type}_${new Date().toISOString().split('T')[0]}.${format}`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        toast.success('Quick export downloaded successfully')
      } else {
        toast.error('Failed to download quick export')
      }
    } catch (error) {
      console.error('Error downloading quick export:', error)
      toast.error('Failed to download quick export')
    } finally {
      setLoading(false)
    }
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'Unknown'
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />
      case 'processing':
      case 'pending':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />
    }
  }

  if (!checkPremiumAccess('PREMIUM_FEATURES')) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              {isPremiumEnforced() ? 'Pro Tier Required' : 'Feature Disabled'}
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>
                {isPremiumEnforced()
                  ? 'Data exports are available for Pro and Institutional tier subscribers. Upgrade your subscription to access this feature.'
                  : 'Data exports are currently disabled. Contact support for access.'
                }
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Data Exports</h2>
          <p className="text-sm text-gray-600">
            Export financial data, macro indicators, and portfolio information in various formats
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
          Create Export
        </button>
      </div>

      {/* Quick Export Buttons */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Exports</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button
            onClick={() => quickExport('financials', 'csv')}
            disabled={loading}
            className="flex items-center justify-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
            Financials CSV
          </button>
          <button
            onClick={() => quickExport('financials', 'xlsx')}
            disabled={loading}
            className="flex items-center justify-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
            Financials Excel
          </button>
          <button
            onClick={() => quickExport('macro', 'csv')}
            disabled={loading}
            className="flex items-center justify-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
            Macro CSV
          </button>
          <button
            onClick={() => quickExport('macro', 'xlsx')}
            disabled={loading}
            className="flex items-center justify-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
            Macro Excel
          </button>
        </div>
      </div>

      {/* Create Export Form */}
      {showCreateForm && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Create Custom Export</h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Export Type
              </label>
              <select
                value={newExport.export_type}
                onChange={(e) => setNewExport({ ...newExport, export_type: e.target.value })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                {exportTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label} - {type.description}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                File Format
              </label>
              <select
                value={newExport.file_format}
                onChange={(e) => setNewExport({ ...newExport, file_format: e.target.value })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                {fileFormats.map((format) => (
                  <option key={format.value} value={format.value}>
                    {format.label} - {format.description}
                  </option>
                ))}
              </select>
            </div>

            {newExport.export_type === 'financials' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Companies (Tickers)
                  </label>
                  <div className="mt-1 flex flex-wrap gap-2">
                    {mockTickers.map((ticker) => (
                      <label key={ticker} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={newExport.filters.tickers.includes(ticker)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setNewExport({
                                ...newExport,
                                filters: {
                                  ...newExport.filters,
                                  tickers: [...newExport.filters.tickers, ticker]
                                }
                              })
                            } else {
                              setNewExport({
                                ...newExport,
                                filters: {
                                  ...newExport.filters,
                                  tickers: newExport.filters.tickers.filter(t => t !== ticker)
                                }
                              })
                            }
                          }}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <span className="ml-2 text-sm text-gray-700">{ticker}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Period
                  </label>
                  <select
                    value={newExport.filters.period}
                    onChange={(e) => setNewExport({
                      ...newExport,
                      filters: { ...newExport.filters, period: e.target.value }
                    })}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  >
                    <option value="">All periods</option>
                    <option value="2024-Q3">2024 Q3</option>
                    <option value="2024-Q2">2024 Q2</option>
                    <option value="2024-Q1">2024 Q1</option>
                    <option value="2023-Q4">2023 Q4</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={newExport.filters.include_ratios}
                      onChange={(e) => setNewExport({
                        ...newExport,
                        filters: { ...newExport.filters, include_ratios: e.target.checked }
                      })}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Include financial ratios</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={newExport.filters.include_gaap_adjustments}
                      onChange={(e) => setNewExport({
                        ...newExport,
                        filters: { ...newExport.filters, include_gaap_adjustments: e.target.checked }
                      })}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Include GAAP adjustments</span>
                  </label>
                </div>
              </div>
            )}

            <div className="flex justify-end space-x-3 pt-4">
              <button
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </button>
              <button
                onClick={createExport}
                disabled={loading}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create Export'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Exports List */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Export History</h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Your recent data exports and their status
          </p>
        </div>

        {loading ? (
          <div className="p-6 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-600">Loading exports...</p>
          </div>
        ) : exports.length === 0 ? (
          <div className="p-6 text-center">
            <p className="text-sm text-gray-600">No exports found. Create your first export to get started.</p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {exports.map((exportItem) => (
              <li key={exportItem.id} className="px-4 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      {getStatusIcon(exportItem.status)}
                    </div>
                    <div className="ml-4">
                      <div className="flex items-center">
                        <p className="text-sm font-medium text-gray-900">
                          {exportItem.export_type.charAt(0).toUpperCase() + exportItem.export_type.slice(1)} Export
                        </p>
                        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          {exportItem.file_format.toUpperCase()}
                        </span>
                      </div>
                      <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                        <span>Created: {formatDate(exportItem.created_at)}</span>
                        <span>Downloads: {exportItem.download_count}</span>
                        {exportItem.file_size_bytes && (
                          <span>Size: {formatFileSize(exportItem.file_size_bytes)}</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${exportItem.status === 'completed'
                      ? 'bg-green-100 text-green-800'
                      : exportItem.status === 'failed'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                      }`}>
                      {exportItem.status.charAt(0).toUpperCase() + exportItem.status.slice(1)}
                    </span>
                    {exportItem.status === 'completed' && (
                      <button
                        onClick={() => downloadExport(exportItem.id)}
                        className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                        Download
                      </button>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
} 