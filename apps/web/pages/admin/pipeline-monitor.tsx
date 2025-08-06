import { useState, useEffect } from 'react'
import { useUser } from '@/lib/useUser'
import { supabase } from '@/lib/supabase'

export default function PipelineMonitor() {
  const { user, profile } = useUser()
  const [pipelineStatus, setPipelineStatus] = useState<any>(null)
  const [lastRun, setLastRun] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPipelineStatus()
  }, [])

  const fetchPipelineStatus = async () => {
    try {
      // Get latest pipeline notification
      const { data: notifications } = await supabase
        .from('pipeline_notifications')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(1)

      // Get latest data quality log
      const { data: qualityLogs } = await supabase
        .from('data_quality_logs')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(1)

      setPipelineStatus({
        lastNotification: notifications?.[0],
        lastQualityLog: qualityLogs?.[0]
      })
    } catch (error) {
      console.error('Error fetching pipeline status:', error)
    } finally {
      setLoading(false)
    }
  }

  const triggerPipeline = async () => {
    try {
      const response = await fetch('/api/cron/pipeline', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        alert('Pipeline triggered successfully!')
        fetchPipelineStatus()
      } else {
        alert('Failed to trigger pipeline')
      }
    } catch (error) {
      console.error('Error triggering pipeline:', error)
      alert('Error triggering pipeline')
    }
  }

  // Only allow admin users
  if (!user || profile?.tier !== 'admin') {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white">Access Denied</h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            You need admin privileges to access this page.
          </p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-6">
              Pipeline Monitor
            </h3>

            {/* Pipeline Status */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                <h4 className="text-sm font-medium text-blue-900 dark:text-blue-400 mb-2">
                  Last Pipeline Run
                </h4>
                {pipelineStatus?.lastNotification ? (
                  <div>
                    <p className="text-sm text-blue-800 dark:text-blue-300">
                      {new Date(pipelineStatus.lastNotification.created_at).toLocaleString()}
                    </p>
                    <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                      {pipelineStatus.lastNotification.message}
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-blue-600 dark:text-blue-400">No recent runs</p>
                )}
              </div>

              <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                <h4 className="text-sm font-medium text-green-900 dark:text-green-400 mb-2">
                  Data Quality
                </h4>
                {pipelineStatus?.lastQualityLog ? (
                  <div>
                    <p className="text-sm text-green-800 dark:text-green-300">
                      {pipelineStatus.lastQualityLog.validation_passed ? '✅ Passed' : '❌ Failed'}
                    </p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                      {pipelineStatus.lastQualityLog.total_records} records processed
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-green-600 dark:text-green-400">No quality data</p>
                )}
              </div>
            </div>

            {/* Manual Trigger */}
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg mb-6">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                Manual Pipeline Trigger
              </h4>
              <button
                onClick={triggerPipeline}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Trigger Pipeline Now
              </button>
            </div>

            {/* Automation Status */}
            <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg">
              <h4 className="text-sm font-medium text-yellow-900 dark:text-yellow-400 mb-2">
                Automation Status
              </h4>
              <ul className="text-sm text-yellow-800 dark:text-yellow-300 space-y-1">
                <li>✅ GitHub Actions: Every 6 hours</li>
                <li>✅ Vercel Cron: Every 6 hours</li>
                <li>✅ Supabase Edge Functions: Real-time triggers</li>
                <li>✅ Monitoring: Real-time dashboard</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 