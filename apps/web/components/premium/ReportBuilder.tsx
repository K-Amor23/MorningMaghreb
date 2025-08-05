import React, { useState, useEffect } from 'react'
import { DocumentTextIcon, PlusIcon, TrashIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import { useLocalStorageGetter } from '@/lib/useClientOnly'

interface Report {
  id: string
  name: string
  type: string
  content: string
  status: 'draft' | 'published' | 'archived'
  created_at: string
  updated_at: string
  published_at?: string
}

export default function ReportBuilder() {
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newReport, setNewReport] = useState({
    name: '',
    type: 'financial_analysis',
    content: ''
  })
  const [showContent, setShowContent] = useState<string | null>(null)
  const { getItem, mounted } = useLocalStorageGetter()

  const reportTypes = [
    { value: 'financial_analysis', label: 'Financial Analysis' },
    { value: 'market_research', label: 'Market Research' },
    { value: 'portfolio_review', label: 'Portfolio Review' },
    { value: 'earnings_report', label: 'Earnings Report' },
    { value: 'custom_report', label: 'Custom Report' }
  ]

  useEffect(() => {
    if (mounted) {
      fetchReports()
    }
  }, [mounted])

  const fetchReports = async () => {
    try {
      const token = getItem('supabase.auth.token')
      const response = await fetch('/api/premium/reports', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setReports(data.reports || [])
      }
    } catch (error) {
      console.error('Error fetching reports:', error)
    } finally {
      setLoading(false)
    }
  }

  const createReport = async () => {
    if (!newReport.name.trim() || !newReport.content.trim()) return

    try {
      const token = getItem('supabase.auth.token')
      const response = await fetch('/api/premium/reports', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newReport)
      })

      if (response.ok) {
        const data = await response.json()
        setReports(prev => [...prev, data.report])
        setShowCreateForm(false)
        setNewReport({ name: '', type: 'financial_analysis', content: '' })
      }
    } catch (error) {
      console.error('Error creating report:', error)
    }
  }

  const deleteReport = async (reportId: string) => {
    if (!confirm('Are you sure you want to delete this report?')) return

    try {
      const token = getItem('supabase.auth.token')
      const response = await fetch(`/api/premium/reports/${reportId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        setReports(prev => prev.filter(report => report.id !== reportId))
      }
    } catch (error) {
      console.error('Error deleting report:', error)
    }
  }

  const exportReport = async (reportId: string, format: string) => {
    try {
      const token = getItem('supabase.auth.token')
      const response = await fetch(`/api/premium/reports/${reportId}/export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ format })
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `report_${reportId}_${new Date().toISOString().split('T')[0]}.${format}`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Error exporting report:', error)
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
            Report Builder
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Create and manage custom financial reports
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
        >
          <PlusIcon className="h-4 w-4" />
          <span>New Report</span>
        </button>
      </div>

      {showCreateForm && (
        <div className="mb-6 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Create New Report
          </h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Report Name
              </label>
              <input
                type="text"
                value={newReport.name}
                onChange={(e) => setNewReport(prev => ({ ...prev, name: e.target.value }))}
                placeholder="e.g., Q3 Financial Analysis, Market Overview"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Report Type
              </label>
              <select
                value={newReport.type}
                onChange={(e) => setNewReport(prev => ({ ...prev, type: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                {reportTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Report Content
              </label>
              <textarea
                value={newReport.content}
                onChange={(e) => setNewReport(prev => ({ ...prev, content: e.target.value }))}
                placeholder="Enter your report content here..."
                rows={8}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div className="flex space-x-3">
              <button
                onClick={createReport}
                disabled={!newReport.name.trim() || !newReport.content.trim()}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
              >
                Create Report
              </button>
              <button
                onClick={() => {
                  setShowCreateForm(false)
                  setNewReport({ name: '', type: 'financial_analysis', content: '' })
                }}
                className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

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
          {reports.length === 0 ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <DocumentTextIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No reports created yet</p>
              <p className="text-sm mt-1">Create your first report to get started</p>
            </div>
          ) : (
            reports.map(report => (
              <div key={report.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="font-medium text-gray-900 dark:text-white">
                        {report.name}
                      </h3>
                      <span className={`px-2 py-1 text-xs rounded-full ${report.status === 'published'
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : report.status === 'archived'
                          ? 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                          : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                        }`}>
                        {report.status}
                      </span>
                    </div>

                    <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      {reportTypes.find(type => type.value === report.type)?.label}
                    </div>

                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Created: {formatDate(report.created_at)}
                      {report.published_at && ` • Published: ${formatDate(report.published_at)}`}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setShowContent(showContent === report.id ? null : report.id)}
                      className="text-blue-600 hover:text-blue-800 dark:text-blue-400"
                    >
                      {showContent === report.id ? (
                        <EyeSlashIcon className="h-4 w-4" />
                      ) : (
                        <EyeIcon className="h-4 w-4" />
                      )}
                    </button>
                    <button
                      onClick={() => exportReport(report.id, 'pdf')}
                      className="text-green-600 hover:text-green-800 dark:text-green-400"
                    >
                      <DocumentTextIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => deleteReport(report.id)}
                      className="text-red-600 hover:text-red-800 dark:text-red-400"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {showContent === report.id && (
                  <div className="mt-2 p-2 bg-gray-100 dark:bg-gray-700 rounded text-sm">
                    {report.content}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
} 