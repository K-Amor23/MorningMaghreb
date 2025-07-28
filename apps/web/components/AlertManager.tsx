import React, { useState, useEffect } from 'react'
import { PlusIcon, TrashIcon, PencilIcon, BellIcon, CheckIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import { authService } from '@/lib/auth'

interface Alert {
    id: string
    ticker: string
    company_name: string
    alert_type: 'price_above' | 'price_below' | 'percent_change'
    target_value: number
    current_value: number
    is_active: boolean
    is_triggered: boolean
    triggered_at?: string
    created_at: string
    updated_at: string
}

interface AlertManagerProps {
    onAlertUpdate?: () => void
}

export default function AlertManager({ onAlertUpdate }: AlertManagerProps) {
    const [alerts, setAlerts] = useState<Alert[]>([])
    const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null)
    const [isCreating, setIsCreating] = useState(false)
    const [isEditing, setIsEditing] = useState(false)
    const [loading, setLoading] = useState(true)
    const [formData, setFormData] = useState({
        ticker: '',
        alert_type: 'price_above' as 'price_above' | 'price_below' | 'percent_change',
        target_value: 0,
        is_active: true
    })

    useEffect(() => {
        fetchAlerts()
    }, [])

    const fetchAlerts = async () => {
        try {
            const token = authService.getAccessToken()
            if (!token) {
                toast.error('Please log in to manage alerts')
                return
            }

            const response = await fetch('/api/alerts', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            if (response.ok) {
                const data = await response.json()
                setAlerts(data.alerts || [])
            } else {
                toast.error('Failed to fetch alerts')
            }
        } catch (error) {
            console.error('Error fetching alerts:', error)
            toast.error('Failed to fetch alerts')
        } finally {
            setLoading(false)
        }
    }

    const createAlert = async () => {
        try {
            const token = authService.getAccessToken()
            if (!token) {
                toast.error('Please log in to create alerts')
                return
            }

            const response = await fetch('/api/alerts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            })

            if (response.ok) {
                const data = await response.json()
                setAlerts([...alerts, data.alert])
                setIsCreating(false)
                setFormData({ ticker: '', alert_type: 'price_above', target_value: 0, is_active: true })
                toast.success('Alert created successfully')
                onAlertUpdate?.()
            } else {
                const error = await response.json()
                toast.error(error.error || 'Failed to create alert')
            }
        } catch (error) {
            console.error('Error creating alert:', error)
            toast.error('Failed to create alert')
        }
    }

    const updateAlert = async () => {
        if (!selectedAlert) return

        try {
            const token = authService.getAccessToken()
            if (!token) {
                toast.error('Please log in to update alerts')
                return
            }

            const response = await fetch(`/api/alerts/${selectedAlert.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            })

            if (response.ok) {
                const data = await response.json()
                setAlerts(alerts.map(a => a.id === selectedAlert.id ? data.alert : a))
                setSelectedAlert(data.alert)
                setIsEditing(false)
                toast.success('Alert updated successfully')
                onAlertUpdate?.()
            } else {
                const error = await response.json()
                toast.error(error.error || 'Failed to update alert')
            }
        } catch (error) {
            console.error('Error updating alert:', error)
            toast.error('Failed to update alert')
        }
    }

    const deleteAlert = async (alertId: string) => {
        if (!confirm('Are you sure you want to delete this alert?')) return

        try {
            const token = authService.getAccessToken()
            if (!token) {
                toast.error('Please log in to delete alerts')
                return
            }

            const response = await fetch(`/api/alerts/${alertId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            if (response.ok) {
                setAlerts(alerts.filter(a => a.id !== alertId))
                if (selectedAlert?.id === alertId) {
                    setSelectedAlert(null)
                }
                toast.success('Alert deleted successfully')
                onAlertUpdate?.()
            } else {
                const error = await response.json()
                toast.error(error.error || 'Failed to delete alert')
            }
        } catch (error) {
            console.error('Error deleting alert:', error)
            toast.error('Failed to delete alert')
        }
    }

    const toggleAlertStatus = async (alertId: string, isActive: boolean) => {
        try {
            const token = authService.getAccessToken()
            if (!token) {
                toast.error('Please log in to update alerts')
                return
            }

            const response = await fetch(`/api/alerts/${alertId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ is_active: isActive })
            })

            if (response.ok) {
                const data = await response.json()
                setAlerts(alerts.map(a => a.id === alertId ? data.alert : a))
                if (selectedAlert?.id === alertId) {
                    setSelectedAlert(data.alert)
                }
                toast.success(`Alert ${isActive ? 'activated' : 'deactivated'} successfully`)
                onAlertUpdate?.()
            } else {
                const error = await response.json()
                toast.error(error.error || 'Failed to update alert')
            }
        } catch (error) {
            console.error('Error updating alert status:', error)
            toast.error('Failed to update alert status')
        }
    }

    const handleEdit = (alert: Alert) => {
        setSelectedAlert(alert)
        setFormData({
            ticker: alert.ticker,
            alert_type: alert.alert_type,
            target_value: alert.target_value,
            is_active: alert.is_active
        })
        setIsEditing(true)
    }

    const getAlertTypeLabel = (type: string) => {
        switch (type) {
            case 'price_above':
                return 'Price Above'
            case 'price_below':
                return 'Price Below'
            case 'percent_change':
                return 'Percent Change'
            default:
                return type
        }
    }

    const getAlertStatusColor = (alert: Alert) => {
        if (alert.is_triggered) return 'text-red-600'
        if (!alert.is_active) return 'text-gray-400'
        return 'text-green-600'
    }

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-casablanca-blue"></div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Price Alerts</h2>
                <button
                    onClick={() => setIsCreating(true)}
                    className="bg-casablanca-blue text-white px-4 py-2 rounded-lg hover:bg-casablanca-blue-dark flex items-center space-x-2"
                >
                    <PlusIcon className="h-5 w-5" />
                    <span>New Alert</span>
                </button>
            </div>

            {/* Create/Edit Modal */}
            {(isCreating || isEditing) && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
                        <h3 className="text-lg font-semibold mb-4">
                            {isCreating ? 'Create New Alert' : 'Edit Alert'}
                        </h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Ticker Symbol
                                </label>
                                <input
                                    type="text"
                                    value={formData.ticker}
                                    onChange={(e) => setFormData({ ...formData, ticker: e.target.value.toUpperCase() })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-casablanca-blue"
                                    placeholder="e.g., BCP"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Alert Type
                                </label>
                                <select
                                    value={formData.alert_type}
                                    onChange={(e) => setFormData({ ...formData, alert_type: e.target.value as any })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-casablanca-blue"
                                >
                                    <option value="price_above">Price Above</option>
                                    <option value="price_below">Price Below</option>
                                    <option value="percent_change">Percent Change</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Target Value
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    value={formData.target_value}
                                    onChange={(e) => setFormData({ ...formData, target_value: parseFloat(e.target.value) || 0 })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-casablanca-blue"
                                    placeholder="Enter target value"
                                />
                            </div>
                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    id="is_active"
                                    checked={formData.is_active}
                                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                                    className="h-4 w-4 text-casablanca-blue focus:ring-casablanca-blue border-gray-300 rounded"
                                />
                                <label htmlFor="is_active" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                                    Active alert
                                </label>
                            </div>
                        </div>
                        <div className="flex justify-end space-x-3 mt-6">
                            <button
                                onClick={() => {
                                    setIsCreating(false)
                                    setIsEditing(false)
                                    setFormData({ ticker: '', alert_type: 'price_above', target_value: 0, is_active: true })
                                }}
                                className="px-4 py-2 text-gray-600 hover:text-gray-800"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={isCreating ? createAlert : updateAlert}
                                disabled={!formData.ticker.trim() || formData.target_value <= 0}
                                className="bg-casablanca-blue text-white px-4 py-2 rounded-lg hover:bg-casablanca-blue-dark disabled:opacity-50"
                            >
                                {isCreating ? 'Create' : 'Update'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Alerts List */}
            <div className="space-y-4">
                {alerts.map((alert) => (
                    <div
                        key={alert.id}
                        className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg transition-shadow"
                    >
                        <div className="flex justify-between items-start mb-4">
                            <div className="flex-1">
                                <div className="flex items-center space-x-3 mb-2">
                                    <span className="font-bold text-lg text-gray-900 dark:text-white">
                                        {alert.ticker}
                                    </span>
                                    <span className="text-sm text-gray-600 dark:text-gray-400">
                                        {alert.company_name}
                                    </span>
                                    {alert.is_triggered && (
                                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                            <CheckIcon className="h-3 w-3 mr-1" />
                                            Triggered
                                        </span>
                                    )}
                                </div>
                                <div className="flex items-center space-x-4 text-sm">
                                    <span className="text-gray-600 dark:text-gray-400">
                                        {getAlertTypeLabel(alert.alert_type)}: ${alert.target_value.toFixed(2)}
                                    </span>
                                    <span className="text-gray-600 dark:text-gray-400">
                                        Current: ${alert.current_value?.toFixed(2) || 'N/A'}
                                    </span>
                                </div>
                            </div>
                            <div className="flex items-center space-x-2">
                                <button
                                    onClick={() => toggleAlertStatus(alert.id, !alert.is_active)}
                                    className={`p-2 rounded-lg ${alert.is_active
                                        ? 'bg-green-100 text-green-600 hover:bg-green-200'
                                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                        }`}
                                    title={alert.is_active ? 'Deactivate' : 'Activate'}
                                >
                                    <BellIcon className="h-4 w-4" />
                                </button>
                                <button
                                    onClick={() => handleEdit(alert)}
                                    className="p-2 text-gray-400 hover:text-casablanca-blue rounded-lg"
                                    title="Edit"
                                >
                                    <PencilIcon className="h-4 w-4" />
                                </button>
                                <button
                                    onClick={() => deleteAlert(alert.id)}
                                    className="p-2 text-gray-400 hover:text-red-500 rounded-lg"
                                    title="Delete"
                                >
                                    <TrashIcon className="h-4 w-4" />
                                </button>
                            </div>
                        </div>

                        <div className="flex justify-between items-center text-sm">
                            <span className={`font-medium ${getAlertStatusColor(alert)}`}>
                                {alert.is_triggered ? 'Triggered' : alert.is_active ? 'Active' : 'Inactive'}
                            </span>
                            <span className="text-gray-500">
                                Created {new Date(alert.created_at).toLocaleDateString()}
                            </span>
                        </div>

                        {alert.is_triggered && alert.triggered_at && (
                            <div className="mt-2 p-2 bg-red-50 dark:bg-red-900/20 rounded-lg">
                                <p className="text-sm text-red-700 dark:text-red-400">
                                    Alert triggered on {new Date(alert.triggered_at).toLocaleString()}
                                </p>
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {alerts.length === 0 && (
                <div className="text-center py-12">
                    <div className="text-gray-400 dark:text-gray-500 mb-4">
                        <BellIcon className="mx-auto h-12 w-12" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No alerts yet</h3>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                        Create your first price alert to get notified about important price movements
                    </p>
                    <button
                        onClick={() => setIsCreating(true)}
                        className="bg-casablanca-blue text-white px-4 py-2 rounded-lg hover:bg-casablanca-blue-dark"
                    >
                        Create Alert
                    </button>
                </div>
            )}

            {/* Alert Statistics */}
            {alerts.length > 0 && (
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 dark:text-white mb-3">Alert Summary</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                            <span className="text-gray-600 dark:text-gray-400">Total Alerts:</span>
                            <span className="ml-2 font-medium">{alerts.length}</span>
                        </div>
                        <div>
                            <span className="text-gray-600 dark:text-gray-400">Active:</span>
                            <span className="ml-2 font-medium text-green-600">
                                {alerts.filter(a => a.is_active && !a.is_triggered).length}
                            </span>
                        </div>
                        <div>
                            <span className="text-gray-600 dark:text-gray-400">Triggered:</span>
                            <span className="ml-2 font-medium text-red-600">
                                {alerts.filter(a => a.is_triggered).length}
                            </span>
                        </div>
                        <div>
                            <span className="text-gray-600 dark:text-gray-400">Inactive:</span>
                            <span className="ml-2 font-medium text-gray-600">
                                {alerts.filter(a => !a.is_active).length}
                            </span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
} 