import React, { useState, useEffect } from 'react'
import { TrophyIcon, UserIcon, CalendarIcon } from '@heroicons/react/24/outline'
import { useLocalStorageGetter } from '@/lib/useClientOnly'

interface Contest {
    id: string
    name: string
    description: string
    start_date: string
    end_date: string
    prize_pool: number
    max_participants: number
    current_participants: number
    entry_fee: number
    status: 'upcoming' | 'active' | 'ended'
}

interface JoinContestFormProps {
    contest: Contest
    onJoin?: (contestId: string) => void
}

export default function JoinContestForm({ contest, onJoin }: JoinContestFormProps) {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [success, setSuccess] = useState(false)
    const { getItem, mounted } = useLocalStorageGetter()

    const handleJoinContest = async () => {
        if (!mounted) return

        setLoading(true)
        setError(null)

        try {
            const token = getItem('access_token')
            const response = await fetch(`/api/contest/${contest.id}/join`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            })

            if (response.ok) {
                setSuccess(true)
                onJoin?.(contest.id)
            } else {
                const data = await response.json()
                setError(data.message || 'Failed to join contest')
            }
        } catch (error) {
            console.error('Error joining contest:', error)
            setError('Failed to join contest. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        })
    }

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'MAD',
            minimumFractionDigits: 0
        }).format(amount)
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
            <div className="flex items-center space-x-3 mb-4">
                <TrophyIcon className="h-8 w-8 text-yellow-500" />
                <div>
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                        Join Contest
                    </h2>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                        {contest.name}
                    </p>
                </div>
            </div>

            <div className="space-y-4 mb-6">
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                        {contest.description}
                    </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center space-x-2">
                        <CalendarIcon className="h-4 w-4 text-gray-400" />
                        <div>
                            <p className="text-xs text-gray-500 dark:text-gray-400">Start Date</p>
                            <p className="text-sm font-medium text-gray-900 dark:text-white">
                                {formatDate(contest.start_date)}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center space-x-2">
                        <CalendarIcon className="h-4 w-4 text-gray-400" />
                        <div>
                            <p className="text-xs text-gray-500 dark:text-gray-400">End Date</p>
                            <p className="text-sm font-medium text-gray-900 dark:text-white">
                                {formatDate(contest.end_date)}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center space-x-2">
                        <TrophyIcon className="h-4 w-4 text-yellow-500" />
                        <div>
                            <p className="text-xs text-gray-500 dark:text-gray-400">Prize Pool</p>
                            <p className="text-sm font-medium text-gray-900 dark:text-white">
                                {formatCurrency(contest.prize_pool)}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center space-x-2">
                        <UserIcon className="h-4 w-4 text-blue-500" />
                        <div>
                            <p className="text-xs text-gray-500 dark:text-gray-400">Participants</p>
                            <p className="text-sm font-medium text-gray-900 dark:text-white">
                                {contest.current_participants}/{contest.max_participants}
                            </p>
                        </div>
                    </div>
                </div>

                {contest.entry_fee > 0 && (
                    <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
                        <p className="text-sm text-blue-700 dark:text-blue-300">
                            Entry Fee: {formatCurrency(contest.entry_fee)}
                        </p>
                    </div>
                )}
            </div>

            {error && (
                <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                    <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
                </div>
            )}

            {success && (
                <div className="mb-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                    <p className="text-sm text-green-700 dark:text-green-300">
                        Successfully joined the contest!
                    </p>
                </div>
            )}

            <button
                onClick={handleJoinContest}
                disabled={loading || success || contest.status !== 'active'}
                className="w-full px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
                {loading ? (
                    <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Joining...</span>
                    </>
                ) : success ? (
                    <>
                        <TrophyIcon className="h-4 w-4" />
                        <span>Joined!</span>
                    </>
                ) : contest.status !== 'active' ? (
                    <>
                        <CalendarIcon className="h-4 w-4" />
                        <span>Contest {contest.status}</span>
                    </>
                ) : (
                    <>
                        <TrophyIcon className="h-4 w-4" />
                        <span>Join Contest</span>
                    </>
                )}
            </button>

            {contest.status !== 'active' && (
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
                    {contest.status === 'upcoming'
                        ? 'This contest has not started yet.'
                        : 'This contest has ended.'
                    }
                </p>
            )}
        </div>
    )
} 