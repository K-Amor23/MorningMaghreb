import { useState, useEffect } from 'react'
import { useUser } from '@/lib/useUser'
import { ShareIcon, EyeIcon, EyeSlashIcon, ChartBarIcon } from '@heroicons/react/24/outline'
import Link from 'next/link'

interface PortfolioShareProps {
    className?: string
}

interface PaperTradingAccount {
    id: string
    account_name: string
    current_balance: number
    total_pnl: number
    total_pnl_percent: number
    position_count: number
    is_public: boolean
}

export default function PortfolioShare({ className = '' }: PortfolioShareProps) {
    const { user } = useUser()
    const [accounts, setAccounts] = useState<PaperTradingAccount[]>([])
    const [loading, setLoading] = useState(true)
    const [updating, setUpdating] = useState<string | null>(null)

    useEffect(() => {
        if (user) {
            loadAccounts()
        }
    }, [user])

    const loadAccounts = async () => {
        try {
            setLoading(true)
            const response = await fetch('/api/paper-trading/accounts', {
                headers: {
                    'Authorization': `Bearer ${user?.id}`
                }
            })

            if (response.ok) {
                const data = await response.json()
                setAccounts(data)
            }
        } catch (error) {
            console.error('Error loading accounts:', error)
        } finally {
            setLoading(false)
        }
    }

    const togglePublic = async (accountId: string, isPublic: boolean) => {
        try {
            setUpdating(accountId)
            const response = await fetch(`/api/paper-trading/accounts/${accountId}/visibility`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${user?.id}`
                },
                body: JSON.stringify({ is_public: !isPublic })
            })

            if (response.ok) {
                setAccounts(prev =>
                    prev.map(account =>
                        account.id === accountId
                            ? { ...account, is_public: !isPublic }
                            : account
                    )
                )
            }
        } catch (error) {
            console.error('Error updating visibility:', error)
        } finally {
            setUpdating(null)
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

    if (!user) {
        return null
    }

    if (loading) {
        return (
            <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-6 ${className}`}>
                <div className="animate-pulse">
                    <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
                    <div className="space-y-3">
                        <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
                        <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-6 ${className}`}>
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Share Your Portfolio
                </h3>
                <ShareIcon className="h-5 w-5 text-gray-400" />
            </div>

            <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                Make your paper trading portfolio public to showcase your skills and compete in contests.
            </p>

            {accounts.length === 0 ? (
                <div className="text-center py-8">
                    <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                        No paper trading accounts found
                    </p>
                    <Link
                        href="/paper-trading"
                        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                    >
                        Create Paper Trading Account
                    </Link>
                </div>
            ) : (
                <div className="space-y-4">
                    {accounts.map((account) => (
                        <div key={account.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-3">
                                <div>
                                    <h4 className="font-medium text-gray-900 dark:text-white">
                                        {account.account_name}
                                    </h4>
                                    <p className="text-sm text-gray-500 dark:text-gray-400">
                                        {account.position_count} positions
                                    </p>
                                </div>
                                <button
                                    onClick={() => togglePublic(account.id, account.is_public)}
                                    disabled={updating === account.id}
                                    className={`flex items-center px-3 py-1 rounded-full text-sm font-medium transition-colors ${account.is_public
                                            ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                                            : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'
                                        }`}
                                >
                                    {updating === account.id ? (
                                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                                    ) : account.is_public ? (
                                        <EyeIcon className="h-4 w-4 mr-1" />
                                    ) : (
                                        <EyeSlashIcon className="h-4 w-4 mr-1" />
                                    )}
                                    {account.is_public ? 'Public' : 'Private'}
                                </button>
                            </div>

                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <p className="text-gray-500 dark:text-gray-400">Balance</p>
                                    <p className="font-medium text-gray-900 dark:text-white">
                                        {formatCurrency(account.current_balance)}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-gray-500 dark:text-gray-400">Total P&L</p>
                                    <p className={`font-medium ${getColorForChange(account.total_pnl_percent)}`}>
                                        {formatPercent(account.total_pnl_percent)}
                                    </p>
                                </div>
                            </div>

                            {account.is_public && (
                                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                                    <p className="text-xs text-green-600 dark:text-green-400">
                                        ✓ Portfolio is public and visible in contests
                                    </p>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-2">
                    Why Share Your Portfolio?
                </h4>
                <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                    <li>• Compete in monthly trading contests</li>
                    <li>• Showcase your trading skills</li>
                    <li>• Connect with other traders</li>
                    <li>• Get feedback on your strategies</li>
                </ul>
            </div>
        </div>
    )
} 