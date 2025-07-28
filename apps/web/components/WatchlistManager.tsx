import React, { useState, useEffect } from 'react'
import { PlusIcon, TrashIcon, PencilIcon, EyeIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import { authService } from '@/lib/auth'

interface WatchlistItem {
    ticker: string
    company_name: string
    current_price: number
    change_percent: number
    added_at: string
}

interface Watchlist {
    id: string
    name: string
    description?: string
    is_public: boolean
    created_at: string
    updated_at: string
    items: WatchlistItem[]
}

interface WatchlistManagerProps {
    onWatchlistUpdate?: () => void
}

export default function WatchlistManager({ onWatchlistUpdate }: WatchlistManagerProps) {
    const [watchlists, setWatchlists] = useState<Watchlist[]>([])
    const [selectedWatchlist, setSelectedWatchlist] = useState<Watchlist | null>(null)
    const [isCreating, setIsCreating] = useState(false)
    const [isEditing, setIsEditing] = useState(false)
    const [loading, setLoading] = useState(true)
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        is_public: false
    })

    useEffect(() => {
        fetchWatchlists()
    }, [])

    const fetchWatchlists = async () => {
        try {
            const token = authService.getAccessToken()
            if (!token) {
                toast.error('Please log in to manage watchlists')
                return
            }

            const response = await fetch('/api/watchlists', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            if (response.ok) {
                const data = await response.json()
                setWatchlists(data.watchlists || [])
            } else {
                toast.error('Failed to fetch watchlists')
            }
        } catch (error) {
            console.error('Error fetching watchlists:', error)
            toast.error('Failed to fetch watchlists')
        } finally {
            setLoading(false)
        }
    }

    const createWatchlist = async () => {
        try {
            const token = authService.getAccessToken()
            if (!token) {
                toast.error('Please log in to create watchlists')
                return
            }

            const response = await fetch('/api/watchlists', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            })

            if (response.ok) {
                const data = await response.json()
                setWatchlists([...watchlists, data.watchlist])
                setIsCreating(false)
                setFormData({ name: '', description: '', is_public: false })
                toast.success('Watchlist created successfully')
                onWatchlistUpdate?.()
            } else {
                const error = await response.json()
                toast.error(error.error || 'Failed to create watchlist')
            }
        } catch (error) {
            console.error('Error creating watchlist:', error)
            toast.error('Failed to create watchlist')
        }
    }

    const updateWatchlist = async () => {
        if (!selectedWatchlist) return

        try {
            const token = authService.getAccessToken()
            if (!token) {
                toast.error('Please log in to update watchlists')
                return
            }

            const response = await fetch(`/api/watchlists/${selectedWatchlist.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            })

            if (response.ok) {
                const data = await response.json()
                setWatchlists(watchlists.map(w => w.id === selectedWatchlist.id ? data.watchlist : w))
                setSelectedWatchlist(data.watchlist)
                setIsEditing(false)
                toast.success('Watchlist updated successfully')
                onWatchlistUpdate?.()
            } else {
                const error = await response.json()
                toast.error(error.error || 'Failed to update watchlist')
            }
        } catch (error) {
            console.error('Error updating watchlist:', error)
            toast.error('Failed to update watchlist')
        }
    }

    const deleteWatchlist = async (watchlistId: string) => {
        if (!confirm('Are you sure you want to delete this watchlist?')) return

        try {
            const token = authService.getAccessToken()
            if (!token) {
                toast.error('Please log in to delete watchlists')
                return
            }

            const response = await fetch(`/api/watchlists/${watchlistId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            if (response.ok) {
                setWatchlists(watchlists.filter(w => w.id !== watchlistId))
                if (selectedWatchlist?.id === watchlistId) {
                    setSelectedWatchlist(null)
                }
                toast.success('Watchlist deleted successfully')
                onWatchlistUpdate?.()
            } else {
                const error = await response.json()
                toast.error(error.error || 'Failed to delete watchlist')
            }
        } catch (error) {
            console.error('Error deleting watchlist:', error)
            toast.error('Failed to delete watchlist')
        }
    }

    const addTickerToWatchlist = async (watchlistId: string, ticker: string) => {
        try {
            const token = authService.getAccessToken()
            if (!token) {
                toast.error('Please log in to add tickers')
                return
            }

            const response = await fetch(`/api/watchlists/${watchlistId}/items`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ ticker })
            })

            if (response.ok) {
                const data = await response.json()
                // Update the watchlist with new item
                setWatchlists(watchlists.map(w =>
                    w.id === watchlistId
                        ? { ...w, items: [...w.items, data.item] }
                        : w
                ))
                if (selectedWatchlist?.id === watchlistId) {
                    setSelectedWatchlist({ ...selectedWatchlist, items: [...selectedWatchlist.items, data.item] })
                }
                toast.success(`${ticker} added to watchlist`)
                onWatchlistUpdate?.()
            } else {
                const error = await response.json()
                toast.error(error.error || 'Failed to add ticker')
            }
        } catch (error) {
            console.error('Error adding ticker:', error)
            toast.error('Failed to add ticker')
        }
    }

    const removeTickerFromWatchlist = async (watchlistId: string, ticker: string) => {
        try {
            const token = authService.getAccessToken()
            if (!token) {
                toast.error('Please log in to remove tickers')
                return
            }

            const response = await fetch(`/api/watchlists/${watchlistId}/items/${ticker}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            if (response.ok) {
                // Update the watchlist by removing the item
                setWatchlists(watchlists.map(w =>
                    w.id === watchlistId
                        ? { ...w, items: w.items.filter(item => item.ticker !== ticker) }
                        : w
                ))
                if (selectedWatchlist?.id === watchlistId) {
                    setSelectedWatchlist({
                        ...selectedWatchlist,
                        items: selectedWatchlist.items.filter(item => item.ticker !== ticker)
                    })
                }
                toast.success(`${ticker} removed from watchlist`)
                onWatchlistUpdate?.()
            } else {
                const error = await response.json()
                toast.error(error.error || 'Failed to remove ticker')
            }
        } catch (error) {
            console.error('Error removing ticker:', error)
            toast.error('Failed to remove ticker')
        }
    }

    const handleEdit = (watchlist: Watchlist) => {
        setSelectedWatchlist(watchlist)
        setFormData({
            name: watchlist.name,
            description: watchlist.description || '',
            is_public: watchlist.is_public
        })
        setIsEditing(true)
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
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Watchlists</h2>
                <button
                    onClick={() => setIsCreating(true)}
                    className="bg-casablanca-blue text-white px-4 py-2 rounded-lg hover:bg-casablanca-blue-dark flex items-center space-x-2"
                >
                    <PlusIcon className="h-5 w-5" />
                    <span>New Watchlist</span>
                </button>
            </div>

            {/* Create/Edit Modal */}
            {(isCreating || isEditing) && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
                        <h3 className="text-lg font-semibold mb-4">
                            {isCreating ? 'Create New Watchlist' : 'Edit Watchlist'}
                        </h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Name
                                </label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-casablanca-blue"
                                    placeholder="Enter watchlist name"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Description
                                </label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-casablanca-blue"
                                    placeholder="Enter description (optional)"
                                    rows={3}
                                />
                            </div>
                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    id="is_public"
                                    checked={formData.is_public}
                                    onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                                    className="h-4 w-4 text-casablanca-blue focus:ring-casablanca-blue border-gray-300 rounded"
                                />
                                <label htmlFor="is_public" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                                    Make this watchlist public
                                </label>
                            </div>
                        </div>
                        <div className="flex justify-end space-x-3 mt-6">
                            <button
                                onClick={() => {
                                    setIsCreating(false)
                                    setIsEditing(false)
                                    setFormData({ name: '', description: '', is_public: false })
                                }}
                                className="px-4 py-2 text-gray-600 hover:text-gray-800"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={isCreating ? createWatchlist : updateWatchlist}
                                disabled={!formData.name.trim()}
                                className="bg-casablanca-blue text-white px-4 py-2 rounded-lg hover:bg-casablanca-blue-dark disabled:opacity-50"
                            >
                                {isCreating ? 'Create' : 'Update'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Watchlists Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {watchlists.map((watchlist) => (
                    <div
                        key={watchlist.id}
                        className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg transition-shadow"
                    >
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                                    {watchlist.name}
                                </h3>
                                {watchlist.description && (
                                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                        {watchlist.description}
                                    </p>
                                )}
                            </div>
                            <div className="flex space-x-2">
                                <button
                                    onClick={() => handleEdit(watchlist)}
                                    className="text-gray-400 hover:text-casablanca-blue"
                                >
                                    <PencilIcon className="h-4 w-4" />
                                </button>
                                <button
                                    onClick={() => deleteWatchlist(watchlist.id)}
                                    className="text-gray-400 hover:text-red-500"
                                >
                                    <TrashIcon className="h-4 w-4" />
                                </button>
                            </div>
                        </div>

                        <div className="space-y-3">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600 dark:text-gray-400">Items:</span>
                                <span className="font-medium">{watchlist.items.length}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600 dark:text-gray-400">Visibility:</span>
                                <span className={`font-medium ${watchlist.is_public ? 'text-green-600' : 'text-gray-600'}`}>
                                    {watchlist.is_public ? 'Public' : 'Private'}
                                </span>
                            </div>
                        </div>

                        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                            <button
                                onClick={() => setSelectedWatchlist(watchlist)}
                                className="w-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-4 py-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 flex items-center justify-center space-x-2"
                            >
                                <EyeIcon className="h-4 w-4" />
                                <span>View Details</span>
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {watchlists.length === 0 && (
                <div className="text-center py-12">
                    <div className="text-gray-400 dark:text-gray-500 mb-4">
                        <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No watchlists yet</h3>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                        Create your first watchlist to start tracking your favorite stocks
                    </p>
                    <button
                        onClick={() => setIsCreating(true)}
                        className="bg-casablanca-blue text-white px-4 py-2 rounded-lg hover:bg-casablanca-blue-dark"
                    >
                        Create Watchlist
                    </button>
                </div>
            )}

            {/* Watchlist Details Modal */}
            {selectedWatchlist && (
                <WatchlistDetails
                    watchlist={selectedWatchlist}
                    onClose={() => setSelectedWatchlist(null)}
                    onAddTicker={addTickerToWatchlist}
                    onRemoveTicker={removeTickerFromWatchlist}
                />
            )}
        </div>
    )
}

interface WatchlistDetailsProps {
    watchlist: Watchlist
    onClose: () => void
    onAddTicker: (watchlistId: string, ticker: string) => Promise<void>
    onRemoveTicker: (watchlistId: string, ticker: string) => Promise<void>
}

function WatchlistDetails({ watchlist, onClose, onAddTicker, onRemoveTicker }: WatchlistDetailsProps) {
    const [newTicker, setNewTicker] = useState('')

    const handleAddTicker = async () => {
        if (!newTicker.trim()) return
        await onAddTicker(watchlist.id, newTicker.trim().toUpperCase())
        setNewTicker('')
    }

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                        {watchlist.name}
                    </h3>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600"
                    >
                        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {watchlist.description && (
                    <p className="text-gray-600 dark:text-gray-400 mb-6">{watchlist.description}</p>
                )}

                {/* Add Ticker Form */}
                <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex space-x-3">
                        <input
                            type="text"
                            value={newTicker}
                            onChange={(e) => setNewTicker(e.target.value)}
                            placeholder="Enter ticker symbol (e.g., BCP)"
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-casablanca-blue"
                            onKeyPress={(e) => e.key === 'Enter' && handleAddTicker()}
                        />
                        <button
                            onClick={handleAddTicker}
                            disabled={!newTicker.trim()}
                            className="bg-casablanca-blue text-white px-4 py-2 rounded-lg hover:bg-casablanca-blue-dark disabled:opacity-50"
                        >
                            Add
                        </button>
                    </div>
                </div>

                {/* Watchlist Items */}
                <div className="space-y-3">
                    <h4 className="font-medium text-gray-900 dark:text-white">Items ({watchlist.items.length})</h4>
                    {watchlist.items.length === 0 ? (
                        <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                            No items in this watchlist yet. Add some tickers to get started.
                        </p>
                    ) : (
                        <div className="space-y-2">
                            {watchlist.items.map((item) => (
                                <div
                                    key={item.ticker}
                                    className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                                >
                                    <div className="flex-1">
                                        <div className="flex items-center space-x-3">
                                            <span className="font-medium text-gray-900 dark:text-white">
                                                {item.ticker}
                                            </span>
                                            <span className="text-sm text-gray-600 dark:text-gray-400">
                                                {item.company_name}
                                            </span>
                                        </div>
                                        <div className="flex items-center space-x-4 mt-1 text-sm">
                                            <span className="text-gray-600 dark:text-gray-400">
                                                ${item.current_price?.toFixed(2) || 'N/A'}
                                            </span>
                                            <span className={`font-medium ${item.change_percent > 0 ? 'text-green-600' :
                                                    item.change_percent < 0 ? 'text-red-600' : 'text-gray-600'
                                                }`}>
                                                {item.change_percent > 0 ? '+' : ''}{item.change_percent?.toFixed(2) || '0'}%
                                            </span>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => onRemoveTicker(watchlist.id, item.ticker)}
                                        className="text-red-500 hover:text-red-700 ml-4"
                                    >
                                        <TrashIcon className="h-4 w-4" />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
} 