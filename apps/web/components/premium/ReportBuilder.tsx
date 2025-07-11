import React, { useState, useEffect } from 'react'
import { DocumentTextIcon, EyeIcon, ArrowDownTrayIcon, ClockIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline'
import { toast } from 'react-hot-toast'
import { checkPremiumAccess, isPremiumEnforced } from '@/lib/featureFlags'

interface Report {
  id: string
  company_ticker: string
  report_type: string
  status: string
  created_at: string
  download_count: number
  file_size_bytes?: number
}

interface ReportTemplate {
  id: string
  name: string
  description: string
  sections: string[]
  is_default: boolean
}

interface ReportBuilderProps {
  userSubscriptionTier: string
}

export default function ReportBuilder({ userSubscriptionTier }: ReportBuilderProps) {
  const [reports, setReports] = useState<Report[]>([])
  const [templates, setTemplates] = useState<ReportTemplate[]>([])
  const [loading, setLoading] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(false)

  const [newReport, setNewReport] = useState({
    company_ticker: '',
    report_type: 'investment_summary',
    include_charts: true,
    include_ai_summary: true,
    custom_sections: [] as string[]
  })

  const mockTickers = [
    { ticker: 'ATW', name: 'Attijariwafa Bank' },
    { ticker: 'IAM', name: 'Maroc Telecom' },
    { ticker: 'BCP', name: 'Banque Centrale Populaire' },
    { ticker: 'BMCE', name: 'BMCE Bank' },
    { ticker: 'WAA', name: 'Wafa Assurance' },
    { ticker: 'CIH', name: 'CIH Bank' },
    { ticker: 'CMT', name: 'Compagnie Minière de Touissit' },
    { ticker: 'CTM', name: 'CTM' }
  ]

  useEffect(() => {
    if (checkPremiumAccess(userSubscriptionTier)) {
      fetchReports()
      fetchTemplates()
    }
  }, [userSubscriptionTier])

  const fetchReports = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/reports', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setReports(data)
      } else {
        toast.error('Failed to fetch reports')
      }
    } catch (error) {
      console.error('Error fetching reports:', error)
      toast.error('Failed to fetch reports')
    } finally {
      setLoading(false)
    }
  }

  const fetchTemplates = async () => {
    try {
      const response = await fetch('/api/reports/templates', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setTemplates(data)
      }
    } catch (error) {
      console.error('Error fetching templates:', error)
    }
  }

  const createReport = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/reports', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        },
        body: JSON.stringify(newReport)
      })
      
      if (response.ok) {
        const reportData = await response.json()
        setReports([reportData, ...reports])
        setShowCreateForm(false)
        setNewReport({
          company_ticker: '',
          report_type: 'investment_summary',
          include_charts: true,
          include_ai_summary: true,
          custom_sections: []
        })
        toast.success('Report created successfully')
      } else {
        toast.error('Failed to create report')
      }
    } catch (error) {
      console.error('Error creating report:', error)
      toast.error('Failed to create report')
    } finally {
      setLoading(false)
    }
  }

  const downloadReport = async (reportId: string) => {
    try {
      const response = await fetch(`/api/reports/${reportId}/download`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        }
      })
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `report_${reportId}.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        toast.success('Report downloaded successfully')
      } else {
        toast.error('Failed to download report')
      }
    } catch (error) {
      console.error('Error downloading report:', error)
      toast.error('Failed to download report')
    }
  }

  const quickReport = async (ticker: string, type: string) => {
    try {
      setLoading(true)
      const response = await fetch(`/api/reports/quick/${ticker}?report_type=${type}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        }
      })
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${ticker}_${type}_${new Date().toISOString().split('T')[0]}.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        toast.success('Quick report downloaded successfully')
      } else {
        toast.error('Failed to download quick report')
      }
    } catch (error) {
      console.error('Error downloading quick report:', error)
      toast.error('Failed to download quick report')
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
      case 'generating':
      case 'pending':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />
    }
  }

  const getReportTypeLabel = (type: string) => {
    switch (type) {
      case 'investment_summary':
        return 'Investment Summary'
      case 'financial_analysis':
        return 'Financial Analysis'
      case 'risk_profile':
        return 'Risk Profile'
      default:
        return type
    }
  }

  if (!checkPremiumAccess(userSubscriptionTier)) {
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
                  ? 'Custom reports are available for Pro and Institutional tier subscribers. Upgrade your subscription to access this feature.'
                  : 'Custom reports are currently disabled. Contact support for access.'
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
          <h2 className="text-lg font-semibold text-gray-900">Custom Reports</h2>
          <p className="text-sm text-gray-600">
            Generate professional investment summaries and financial analysis reports
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <DocumentTextIcon className="h-4 w-4 mr-2" />
          Create Report
        </button>
      </div>

      {/* Quick Report Buttons */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Reports</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {mockTickers.slice(0, 4).map((company) => (
            <div key={company.ticker} className="space-y-2">
              <p className="text-xs font-medium text-gray-700">{company.name}</p>
              <div className="flex space-x-1">
                <button
                  onClick={() => quickReport(company.ticker, 'investment_summary')}
                  disabled={loading}
                  className="flex-1 inline-flex items-center justify-center px-2 py-1 border border-gray-300 rounded text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  Summary
                </button>
                <button
                  onClick={() => quickReport(company.ticker, 'financial_analysis')}
                  disabled={loading}
                  className="flex-1 inline-flex items-center justify-center px-2 py-1 border border-gray-300 rounded text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  Analysis
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Create Report Form */}
      {showCreateForm && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Create Custom Report</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Company
              </label>
              <select
                value={newReport.company_ticker}
                onChange={(e) => setNewReport({...newReport, company_ticker: e.target.value})}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Select a company</option>
                {mockTickers.map((company) => (
                  <option key={company.ticker} value={company.ticker}>
                    {company.ticker} - {company.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Report Type
              </label>
              <select
                value={newReport.report_type}
                onChange={(e) => setNewReport({...newReport, report_type: e.target.value})}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                {templates.map((template) => (
                  <option key={template.id} value={template.id}>
                    {template.name} - {template.description}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={newReport.include_charts}
                  onChange={(e) => setNewReport({...newReport, include_charts: e.target.checked})}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">Include charts and visualizations</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={newReport.include_ai_summary}
                  onChange={(e) => setNewReport({...newReport, include_ai_summary: e.target.checked})}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">Include AI-generated summary</span>
              </label>
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </button>
              <button
                onClick={createReport}
                disabled={loading || !newReport.company_ticker}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create Report'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reports List */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Report History</h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Your generated reports and their status
          </p>
        </div>
        
        {loading ? (
          <div className="p-6 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-600">Loading reports...</p>
          </div>
        ) : reports.length === 0 ? (
          <div className="p-6 text-center">
            <p className="text-sm text-gray-600">No reports found. Create your first report to get started.</p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {reports.map((report) => (
              <li key={report.id} className="px-4 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      {getStatusIcon(report.status)}
                    </div>
                    <div className="ml-4">
                      <div className="flex items-center">
                        <p className="text-sm font-medium text-gray-900">
                          {report.company_ticker} - {getReportTypeLabel(report.report_type)}
                        </p>
                        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          PDF
                        </span>
                      </div>
                      <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                        <span>Created: {formatDate(report.created_at)}</span>
                        <span>Downloads: {report.download_count}</span>
                        {report.file_size_bytes && (
                          <span>Size: {formatFileSize(report.file_size_bytes)}</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      report.status === 'completed' 
                        ? 'bg-green-100 text-green-800'
                        : report.status === 'failed'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
                    </span>
                    {report.status === 'completed' && (
                      <button
                        onClick={() => downloadReport(report.id)}
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

      {/* Report Templates Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-800 mb-2">Available Report Templates</h3>
        <div className="text-sm text-blue-700 space-y-1">
          <p>• <strong>Investment Summary:</strong> 1-page overview with key metrics, AI summary, and risk profile</p>
          <p>• <strong>Financial Analysis:</strong> Detailed financial analysis with ratios and trends</p>
          <p>• <strong>Risk Profile:</strong> Comprehensive risk assessment and mitigation strategies</p>
          <p>• Reports are generated as professional PDF documents</p>
          <p>• Include charts, tables, and AI-generated insights</p>
        </div>
      </div>
    </div>
  )
} 