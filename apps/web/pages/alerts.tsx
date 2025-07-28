import React from 'react'
import Head from 'next/head'
import AlertManager from '@/components/AlertManager'
import RealTimeNotifications from '@/components/RealTimeNotifications'
import { usePWA } from '@/components/PWAInstaller'
import { useWebSocket } from '@/lib/websocket'

export default function AlertsPage() {
    const { isPWA } = usePWA()
    const { isConnected } = useWebSocket()

    return (
        <>
            <Head>
                <title>Price Alerts - Casablanca Insights</title>
                <meta name="description" content="Manage price alerts and get notified of important movements" />
            </Head>

            <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
                {/* Header */}
                <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <div className="flex justify-between items-center py-6">
                            <div>
                                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                                    Price Alerts
                                </h1>
                                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                                    Set up alerts for price movements and get real-time notifications
                                </p>
                            </div>

                            <div className="flex items-center space-x-4">
                                {/* Connection Status */}
                                <div className="flex items-center space-x-2">
                                    <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                                    <span className="text-sm text-gray-600 dark:text-gray-400">
                                        {isConnected ? 'Connected' : 'Disconnected'}
                                    </span>
                                </div>

                                {/* PWA Status */}
                                {isPWA && (
                                    <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                                        <span>📱 PWA</span>
                                    </div>
                                )}

                                {/* Real-time Notifications */}
                                <RealTimeNotifications />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Main Content */}
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <AlertManager
                        onAlertUpdate={() => {
                            // Trigger any necessary updates
                            console.log('Alert updated')
                        }}
                    />
                </div>
            </div>
        </>
    )
} 