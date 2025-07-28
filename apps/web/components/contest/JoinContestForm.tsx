import { useState, useEffect } from 'react'
import { XMarkIcon, CheckIcon } from '@heroicons/react/24/outline'

interface PaperTradingAccount {
    id: string
    user_id: string
    account_name: string
    initial_balance: number
    current_balance: number
    total_pnl: number
    total_pnl_percent: number
    is_active: boolean
    created_at: string
    updated_at: string
}

interface JoinContestFormProps {
    onJoin: (accountId: string) => void
    onCancel: () => void
    loading: boolean
}

export default function JoinContestForm({ onJoin, onCancel, loading }: JoinContestFormProps) {
    const [accounts, setAccounts] = useState<PaperTradingAccount[]>([])
    const [selectedAccount, setSelectedAccount] = useState<string>('')
    const [loadingAccounts, setLoadingAccounts] = useState(true)

    useEffect(() => {
        loadAccounts()
    }, [])

    const loadAccounts = async () => {
        try {
            setLoadingAccounts(true)
            const response = await fetch('/api/paper-trading/accounts', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            })

            if (response.ok) {
                const accountsData = await response.json()
                setAccounts(accountsData)
            }
        } catch (error) {
            console.error('Error loading accounts:', error)
        } finally {
            setLoadingAccounts(false)
        }
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (selectedAccount) {
            onJoin(selectedAccount)
        }
    }

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'MAD',
            minimumFractionDigits: 2
        }).format(amount)
    }

    const formatPercent = (percent: number) => {
        return `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`
    }

    const getColorForChange = (value: number) => {
        if (value > 0) return 'text-green-600 dark:text-green-400'
        if (value < 0) return 'text-red-600 dark:text-red-400'
        return 'text-gray-600 dark:text-gray-400'
    }

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                    <div className="flex items-center justify-between">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                            Join Contest
                        </h3>
                        <button
                            onClick={onCancel}
                            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                        >
                            <XMarkIcon className="h-6 w-6" />
                        </button>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="p-6">
                    <div className="mb-6">
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                            Select a paper trading account to join the contest. Make sure your account has at least 3 positions.
                        </p>

                        {loadingAccounts ? (
                            <div className="space-y-3">
                                {[1, 2, 3].map((i) => (
                                    <div key={i} className="animate-pulse">
                                        <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                                    </div>
                                ))}
                            </div>
                        ) : accounts.length === 0 ? (
                            <div className="text-center py-8">
                                <div className="text-gray-400 dark:text-gray-500 text-4xl mb-4">📊</div>
                                <p className="text-gray-600 dark:text-gray-400 mb-4">
                                    No paper trading accounts found
                                </p>
                                <p className="text-sm text-gray-500 dark:text-gray-500">
                                    Create a paper trading account first to join the contest
                                </p>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {accounts.map((account) => (
                                    <label
                                        key={account.id}
                                        className={`block cursor-pointer p-4 border rounded-lg transition-colors ${selectedAccount === account.id
                                                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                                                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                                            }`}
                                    >
                                        <div className="flex items-center">
                                            <input
                                                type="radio"
                                                name="account"
                                                value={account.id}
                                                checked={selectedAccount === account.id}
                                                onChange={(e) => setSelectedAccount(e.target.value)}
                                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                                            />
                                            <div className="ml-3 flex-1">
                                                <div className="flex items-center justify-between">
                                                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                                                        {account.account_name}
                                                    </span>
                                                    {selectedAccount === account.id && (
                                                        <CheckIcon className="h-5 w-5 text-blue-600" />
                                                    )}
                                                </div>
                                                <div className="mt-1 grid grid-cols-2 gap-2 text-xs text-gray-500 dark:text-gray-400">
                                                    <div>
                                                        <span className="font-medium">Balance:</span> {formatCurrency(account.current_balance)}
                                                    </div>
                                                    <div>
                                                        <span className="font-medium">P&L:</span>
                                                        <span className={getColorForChange(account.total_pnl_percent)}>
                                                            {' '}{formatPercent(account.total_pnl_percent)}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </label>
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 mb-6">
                        <h4 className="text-sm font-semibold text-yellow-900 dark:text-yellow-100 mb-2">
                            Contest Requirements
                        </h4>
                        <ul className="text-sm text-yellow-800 dark:text-yellow-200 space-y-1">
                            <li>• Account must have at least 3 positions</li>
                            <li>• Only one account per user can participate</li>
                            <li>• You cannot change accounts once joined</li>
                            <li>• Contest ranking is based on total return percentage</li>
                        </ul>
                    </div>

                    <div className="flex space-x-3">
                        <button
                            type="button"
                            onClick={onCancel}
                            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={!selectedAccount || loading}
                            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Joining...' : 'Join Contest'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
} 