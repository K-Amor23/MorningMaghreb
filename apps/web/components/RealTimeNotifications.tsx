import React, { useState, useEffect, useCallback } from 'react'
import { BellIcon, XMarkIcon, ExclamationTriangleIcon, ChartBarIcon } from '@heroicons/react/24/outline'
import { useLiveAlerts, useLiveWatchlist } from '@/lib/websocket'
import toast from 'react-hot-toast'
import { useLocalStorage } from '@/lib/useClientOnly'

interface RealTimeNotificationsProps {
    watchlistId?: string
    onAlertClick?: (alert: any) => void
}

export default function RealTimeNotifications({ watchlistId, onAlertClick }: RealTimeNotificationsProps) {
    const [showNotifications, setShowNotifications] = useState(false)
    const [unreadCount, setUnreadCount] = useState(0)
    const { alerts, clearAlerts, isConnected } = useLiveAlerts()
    const { updates, clearUpdates, isConnected: watchlistConnected } = useLiveWatchlist(watchlistId)

    // Combine alerts and updates
    const allNotifications = [
        ...alerts.map(alert => ({ ...alert, type: 'alert' as const })),
        ...updates.map(update => ({ ...update, type: 'watchlist' as const }))
    ].sort((a, b) => {
        const aTime = new Date((a as any).timestamp || (a as any).triggered_at || (a as any).created_at || Date.now()).getTime()
        const bTime = new Date((b as any).timestamp || (b as any).triggered_at || (b as any).created_at || Date.now()).getTime()
        return bTime - aTime
    })

    useEffect(() => {
        // Show toast for new alerts
        alerts.forEach(alert => {
            if (alert.ticker && alert.current_value) {
                toast.success(
                    `Alert: ${alert.ticker} hit ${alert.alert_type} target!`,
                    {
                        duration: 5000,
                        icon: '🔔',
                        style: {
                            background: '#10B981',
                            color: '#fff',
                        },
                    }
                )
            }
        })
    }, [alerts])

    useEffect(() => {
        // Update unread count
        setUnreadCount(allNotifications.length)
    }, [allNotifications])

    const handleNotificationClick = (notification: any) => {
        if (notification.type === 'alert' && onAlertClick) {
            onAlertClick(notification)
        }
        // Mark as read by removing from list
        if (notification.type === 'alert') {
            // This would typically update the alert status in the backend
            console.log('Marking alert as read:', notification.alert_id)
        }
    }

    const handleClearAll = () => {
        clearAlerts()
        clearUpdates()
        setUnreadCount(0)
    }

    const getNotificationIcon = (type: 'alert' | 'watchlist') => {
        if (type === 'alert') {
            return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
        }
        return <ChartBarIcon className="h-5 w-5 text-green-500" />
    }

    const getNotificationTitle = (notification: any) => {
        if (notification.type === 'alert') {
            return `Alert: ${notification.ticker} ${notification.alert_type}`
        }
        return `Watchlist: ${notification.watchlist_name}`
    }

    const getNotificationMessage = (notification: any) => {
        if (notification.type === 'alert') {
            return `${notification.ticker} hit ${notification.alert_type} target of $${notification.target_value.toFixed(2)} (Current: $${notification.current_value.toFixed(2)})`
        }
        return `${notification.action} ${notification.ticker} to ${notification.watchlist_name}`
    }

    const getNotificationTime = (notification: any) => {
        const timestamp = (notification as any).timestamp || (notification as any).triggered_at || (notification as any).created_at
        if (!timestamp) return 'Just now'

        const date = new Date(timestamp)
        const now = new Date()
        const diffMs = now.getTime() - date.getTime()
        const diffMins = Math.floor(diffMs / 60000)
        const diffHours = Math.floor(diffMs / 3600000)
        const diffDays = Math.floor(diffMs / 86400000)

        if (diffMins < 1) return 'Just now'
        if (diffMins < 60) return `${diffMins}m ago`
        if (diffHours < 24) return `${diffHours}h ago`
        return `${diffDays}d ago`
    }

    return (
        <div className="relative">
            {/* Notification Bell */}
            <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="relative p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 transition-colors"
            >
                <BellIcon className="h-6 w-6" />
                {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                        {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                )}
            </button>

            {/* Connection Status */}
            {!isConnected && !watchlistConnected && (
                <div className="absolute -bottom-8 right-0 text-xs text-gray-500">
                    Offline
                </div>
            )}

            {/* Notifications Panel */}
            {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
                    <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                        <div className="flex justify-between items-center">
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                                Notifications
                            </h3>
                            <div className="flex items-center space-x-2">
                                {unreadCount > 0 && (
                                    <button
                                        onClick={handleClearAll}
                                        className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                                    >
                                        Clear all
                                    </button>
                                )}
                                <button
                                    onClick={() => setShowNotifications(false)}
                                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                                >
                                    <XMarkIcon className="h-4 w-4" />
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="max-h-96 overflow-y-auto">
                        {allNotifications.length === 0 ? (
                            <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                                <BellIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
                                <p>No notifications yet</p>
                                <p className="text-sm">You'll see alerts and updates here</p>
                            </div>
                        ) : (
                            <div className="divide-y divide-gray-200 dark:divide-gray-700">
                                {allNotifications.map((notification, index) => (
                                    <div
                                        key={`${notification.type}-${index}`}
                                        onClick={() => handleNotificationClick(notification)}
                                        className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                                    >
                                        <div className="flex items-start space-x-3">
                                            <div className="flex-shrink-0 mt-0.5">
                                                {getNotificationIcon(notification.type)}
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm font-medium text-gray-900 dark:text-white">
                                                    {getNotificationTitle(notification)}
                                                </p>
                                                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                                    {getNotificationMessage(notification)}
                                                </p>
                                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                                                    {getNotificationTime(notification)}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Footer */}
                    <div className="p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 rounded-b-lg">
                        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                            <span>
                                {isConnected || watchlistConnected ? 'Connected' : 'Disconnected'}
                            </span>
                            <span>
                                {allNotifications.length} notification{allNotifications.length !== 1 ? 's' : ''}
                            </span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

// Hook for managing notification preferences
export function useNotificationPreferences() {
    const [preferences, setPreferences] = useLocalStorage('notification-preferences', {
        emailAlerts: true,
        pushNotifications: true,
        soundEnabled: true,
        alertTypes: {
            price_above: true,
            price_below: true,
            percent_change: true
        }
    })

    const updatePreferences = (newPreferences: Partial<typeof preferences>) => {
        const updated = { ...preferences, ...newPreferences }
        setPreferences(updated)
    }

    return {
        preferences,
        updatePreferences
    }
} 