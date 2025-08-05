import React, { useState, useEffect } from 'react'
import { DocumentArrowDownIcon, TableCellsIcon, ChartBarIcon } from '@heroicons/react/24/outline'
import { useLocalStorageGetter } from '@/lib/useClientOnly'

interface ExportData {
  type: string
  format: string
  dateRange: {
    start: string
    end: string
  }
  filters: {
    companies?: string[]
    sectors?: string[]
    dataTypes?: string[]
  }
}

export default function DataExporter() {
  const [exportHistory, setExportHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)
  const [exportConfig, setExportConfig] = useState<ExportData>({
    type: 'market_data',
    format: 'csv',
    dateRange: {
      start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0]
    },
    filters: {}
  })
  const { getItem, mounted } = useLocalStorageGetter()

  useEffect(() => {
    if (mounted) {
      fetchExportHistory()
    }
  }, [mounted])

  const fetchExportHistory = async () => {
    try {
      const token = getItem('supabase.auth.token')
      const response = await fetch('/api/premium/data-exports', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setExportHistory(data.exports || [])
      }
    } catch (error) {
      console.error('Error fetching export history:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    setExporting(true)
    try {
      const token = getItem('supabase.auth.token')
      const response = await fetch('/api/premium/data-exports', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(exportConfig)
      })

      if (response.ok) {
        const data = await response.json()

        // Trigger download
        const a = document.createElement('a')
        a.href = data.download_url
        a.download = `quick_export_${exportConfig.type}_${new Date().toISOString().split('T')[0]}.${exportConfig.format}`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)

        // Refresh export history
        await fetchExportHistory()
      }
    } catch (error) {
      console.error('Error creating export:', error)
    } finally {
      setExporting(false)
    }
  }

  const downloadExport = async (exportId: string, filename: string) => {
    try {
      const token = getItem('supabase.auth.token')
      const response = await fetch(`/api/premium/data-exports/${exportId}/download`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Error downloading export:', error)
    }
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

  if (!mounted) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-6"></div>
          <div className="space-y-3">
            <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Data Exporter
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Export market data, financial reports, and analytics
          </p>
        </div>
        <DocumentArrowDownIcon className="h-8 w-8 text-blue-500" />
      </div>

      {/* Export Configuration */}
      <div className="mb-6 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Export Configuration
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Data Type
            </label>
            <select
              value={exportConfig.type}
              onChange={(e) => setExportConfig(prev => ({ ...prev, type: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="market_data">Market Data</option>
              <option value="financial_reports">Financial Reports</option>
              <option value="analytics">Analytics</option>
              <option value="portfolio">Portfolio Data</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Format
            </label>
            <select
              value={exportConfig.format}
              onChange={(e) => setExportConfig(prev => ({ ...prev, format: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="csv">CSV</option>
              <option value="xlsx">Excel</option>
              <option value="json">JSON</option>
              <option value="pdf">PDF</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Start Date
            </label>
            <input
              type="date"
              value={exportConfig.dateRange.start}
              onChange={(e) => setExportConfig(prev => ({
                ...prev,
                dateRange: { ...prev.dateRange, start: e.target.value }
              }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              End Date
            </label>
            <input
              type="date"
              value={exportConfig.dateRange.end}
              onChange={(e) => setExportConfig(prev => ({
                ...prev,
                dateRange: { ...prev.dateRange, end: e.target.value }
              }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
        </div>

        <div className="mt-4">
          <button
            onClick={handleExport}
            disabled={exporting}
            className="w-full px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            {exporting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Exporting...</span>
              </>
            ) : (
              <>
                <DocumentArrowDownIcon className="h-4 w-4" />
                <span>Export Data</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Export History */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Export History
        </h3>

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="animate-pulse">
                <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {exportHistory.length === 0 ? (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                <DocumentArrowDownIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>No exports created yet</p>
                <p className="text-sm mt-1">Create your first export to see it here</p>
              </div>
            ) : (
              exportHistory.map(exportItem => (
                <div key={exportItem.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h4 className="font-medium text-gray-900 dark:text-white">
                          {exportItem.type.replace('_', ' ').toUpperCase()}
                        </h4>
                        <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded">
                          {exportItem.format.toUpperCase()}
                        </span>
                      </div>

                      <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                        {formatDate(exportItem.created_at)}
                      </div>

                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {exportItem.record_count} records • {exportItem.file_size}
                      </div>
                    </div>

                    <button
                      onClick={() => downloadExport(exportItem.id, exportItem.filename)}
                      className="text-blue-600 hover:text-blue-800 dark:text-blue-400"
                    >
                      <DocumentArrowDownIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  )
} 