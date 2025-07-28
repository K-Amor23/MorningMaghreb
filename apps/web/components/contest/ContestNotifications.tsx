import { BellIcon, CheckIcon, XMarkIcon } from '@heroicons/react/24/outline'

interface ContestNotification {
    id: string
    contest_id: string
    user_id: string
    notification_type: string
    message: string
    is_read: boolean
    created_at: string
}

interface ContestNotificationsProps {
    notifications: ContestNotification[]
    onMarkRead: (notificationId: string) => void
}

export default function ContestNotifications({
    notifications,
    onMarkRead
}: ContestNotificationsProps) {
    const getNotificationIcon = (type: string) => {
        switch (type) {
            case 'rank_change':
                return '📈'
            case 'winner_announcement':
                return '🏆'
            case 'contest_join':
                return '✅'
            case 'contest_leave':
                return '👋'
            default:
                return '🔔'
        }
    }

    const getNotificationColor = (type: string) => {
        switch (type) {
            case 'rank_change':
                return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
            case 'winner_announcement':
                return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
            case 'contest_join':
                return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
            case 'contest_leave':
                return 'bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600'
            default:
                return 'bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600'
        }
    }

    const formatDate = (dateString: string) => {
        const date = new Date(dateString)
        const now = new Date()
        const diffTime = now.getTime() - date.getTime()
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
        const diffHours = Math.floor(diffTime / (1000 * 60 * 60))
        const diffMinutes = Math.floor(diffTime / (1000 * 60))

        if (diffDays > 0) {
            return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
        } else if (diffHours > 0) {
            return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
        } else if (diffMinutes > 0) {
            return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`
        } else {
            return 'Just now'
        }
    }

    const unreadCount = notifications.filter(n => !n.is_read).length

    if (notifications.length === 0) {
        return null
    }

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <BellIcon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                            Contest Notifications
                        </h2>
                        {unreadCount > 0 && (
                            <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                                {unreadCount}
                            </span>
                        )}
                    </div>
                </div>
            </div>

            <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {notifications.map((notification) => (
                    <div
                        key={notification.id}
                        className={`p-4 ${getNotificationColor(notification.notification_type)} ${!notification.is_read ? 'border-l-4 border-blue-500' : ''
                            }`}
                    >
                        <div className="flex items-start space-x-3">
                            <div className="flex-shrink-0">
                                <span className="text-2xl">
                                    {getNotificationIcon(notification.notification_type)}
                                </span>
                            </div>

                            <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between">
                                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                                        {notification.message}
                                    </p>
                                    <div className="flex items-center space-x-2">
                                        <span className="text-xs text-gray-500 dark:text-gray-400">
                                            {formatDate(notification.created_at)}
                                        </span>
                                        {!notification.is_read && (
                                            <button
                                                onClick={() => onMarkRead(notification.id)}
                                                className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                                                title="Mark as read"
                                            >
                                                <CheckIcon className="h-4 w-4" />
                                            </button>
                                        )}
                                    </div>
                                </div>

                                <div className="mt-1">
                                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200">
                                        {notification.notification_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {unreadCount > 0 && (
                <div className="px-6 py-3 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600">
                    <button
                        onClick={() => {
                            notifications
                                .filter(n => !n.is_read)
                                .forEach(n => onMarkRead(n.id))
                        }}
                        className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                    >
                        Mark all as read
                    </button>
                </div>
            )}
        </div>
    )
} 