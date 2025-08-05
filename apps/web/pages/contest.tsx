import { useState, useEffect } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import { useUser } from '@/lib/useUser'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import ContestLeaderboard from '@/components/contest/ContestLeaderboard'
import ContestInfo from '@/components/contest/ContestInfo'
import ContestNotifications from '@/components/contest/ContestNotifications'
import JoinContestForm from '@/components/contest/JoinContestForm'
import toast from 'react-hot-toast'

interface ContestEntry {
    id: string
    contest_id: string
    user_id: string
    account_id: string
    username: string
    initial_balance: number
    current_balance: number
    total_return: number
    total_return_percent: number
    position_count: number
    status: string
    rank?: number
    joined_at: string
    updated_at: string
}

interface ContestRanking {
    contest_id: string
    user_id: string
    username: string
    rank: number
    total_return_percent: number
    total_return: number
    position_count: number
    last_updated: string
}

interface Contest {
    id: string
    name: string
    description: string
    start_date: string
    end_date: string
    status: string
    prize_amount: number
    min_positions: number
    max_participants?: number
    created_at: string
    updated_at: string
}

interface ContestNotification {
    id: string
    contest_id: string
    user_id: string
    notification_type: string
    message: string
    is_read: boolean
    created_at: string
}

export default function ContestPage() {
    const { user, loading } = useUser()
    const [activeContest, setActiveContest] = useState<Contest | null>(null)
    const [rankings, setRankings] = useState<ContestRanking[]>([])
    const [myEntry, setMyEntry] = useState<ContestEntry | null>(null)
    const [notifications, setNotifications] = useState<ContestNotification[]>([])
    const [showJoinForm, setShowJoinForm] = useState(false)
    const [loadingData, setLoadingData] = useState(true)
    const [refreshing, setRefreshing] = useState(false)

    useEffect(() => {
        if (!loading) {
            loadContestData()
        }
    }, [loading, user])

    const loadContestData = async () => {
        try {
            setLoadingData(true)

            // Load active contest
            const contestResponse = await fetch('/api/contest/active')
            if (contestResponse.ok) {
                const contest = await contestResponse.json()
                setActiveContest(contest)
            }

            // Load rankings
            const rankingsResponse = await fetch('/api/contest/rankings')
            if (rankingsResponse.ok) {
                const rankingsData = await rankingsResponse.json()
                setRankings(rankingsData)
            }

            // Load user's entry if authenticated
            if (user) {
                const entryResponse = await fetch('/api/contest/my-entry', {
                    headers: {
                        'Authorization': `Bearer ${user.id}`
                    }
                })
                if (entryResponse.ok) {
                    const entry = await entryResponse.json()
                    setMyEntry(entry)
                } else if (entryResponse.status === 404) {
                    setMyEntry(null)
                }

                // Load notifications
                const notificationsResponse = await fetch('/api/contest/notifications', {
                    headers: {
                        'Authorization': `Bearer ${user.id}`
                    }
                })
                if (notificationsResponse.ok) {
                    const notificationsData = await notificationsResponse.json()
                    setNotifications(notificationsData)
                }
            }
        } catch (error) {
            console.error('Error loading contest data:', error)
            toast.error('Failed to load contest data')
        } finally {
            setLoadingData(false)
        }
    }

    const handleJoinContest = async (accountId: string) => {
        try {
            setRefreshing(true)

            const response = await fetch('/api/contest/join', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${user?.id}`
                },
                body: JSON.stringify({ account_id: accountId })
            })

            if (response.ok) {
                const entry = await response.json()
                setMyEntry(entry)
                setShowJoinForm(false)
                toast.success('Successfully joined the contest!')

                // Reload rankings
                await loadContestData()
            } else {
                const error = await response.json()
                toast.error(error.detail || 'Failed to join contest')
            }
        } catch (error) {
            console.error('Error joining contest:', error)
            toast.error('Failed to join contest')
        } finally {
            setRefreshing(false)
        }
    }

    const handleLeaveContest = async () => {
        try {
            setRefreshing(true)

            const response = await fetch('/api/contest/leave', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${user?.id}`
                }
            })

            if (response.ok) {
                setMyEntry(null)
                toast.success('Successfully left the contest')

                // Reload data
                await loadContestData()
            } else {
                const error = await response.json()
                toast.error(error.detail || 'Failed to leave contest')
            }
        } catch (error) {
            console.error('Error leaving contest:', error)
            toast.error('Failed to leave contest')
        } finally {
            setRefreshing(false)
        }
    }

    const handleRefresh = async () => {
        setRefreshing(true)
        await loadContestData()
        setRefreshing(false)
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

    if (loading || loadingData) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
                <Header />
                <main className="container mx-auto px-4 py-8">
                    <div className="animate-pulse">
                        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-8"></div>
                        <div className="space-y-4">
                            <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded"></div>
                            <div className="h-96 bg-gray-200 dark:bg-gray-700 rounded"></div>
                        </div>
                    </div>
                </main>
                <Footer />
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <Head>
                <title>Portfolio Contest - Casablanca Insights</title>
                <meta name="description" content="Monthly portfolio contest with $100 prize" />
            </Head>

            <Header />

            <main className="container mx-auto px-4 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                        Monthly Portfolio Contest
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400">
                        Compete with other traders for the $100 monthly prize
                    </p>
                </div>

                {activeContest ? (
                    <div className="space-y-8">
                        {/* Contest Information */}
                        <ContestInfo contest={activeContest} />

                        {/* User Actions */}
                        {user && (
                            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                                    Your Contest Status
                                </h2>

                                {myEntry ? (
                                    <div className="space-y-4">
                                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                                                <p className="text-sm text-blue-600 dark:text-blue-400">Current Rank</p>
                                                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                                                    #{myEntry.rank || 'N/A'}
                                                </p>
                                            </div>
                                            <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                                                <p className="text-sm text-green-600 dark:text-green-400">Total Return</p>
                                                <p className={`text-2xl font-bold ${getColorForChange(myEntry.total_return_percent)}`}>
                                                    {formatPercent(myEntry.total_return_percent)}
                                                </p>
                                            </div>
                                            <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                                                <p className="text-sm text-purple-600 dark:text-purple-400">Positions</p>
                                                <p className="text-2xl font-bold text-purple-900 dark:text-purple-100">
                                                    {myEntry.position_count}
                                                </p>
                                            </div>
                                            <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                                                <p className="text-sm text-orange-600 dark:text-orange-400">Account Value</p>
                                                <p className="text-2xl font-bold text-orange-900 dark:text-orange-100">
                                                    {formatCurrency(myEntry.current_balance)}
                                                </p>
                                            </div>
                                        </div>

                                        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
                                            <button
                                                onClick={handleRefresh}
                                                disabled={refreshing}
                                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                                            >
                                                {refreshing ? 'Refreshing...' : 'Refresh Data'}
                                            </button>
                                            <Link
                                                href="/paper-trading"
                                                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-center"
                                            >
                                                Manage Portfolio
                                            </Link>
                                            <button
                                                onClick={handleLeaveContest}
                                                disabled={refreshing}
                                                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                                            >
                                                Leave Contest
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="text-center">
                                        <div className="mb-6">
                                            <div className="text-6xl mb-4">🏆</div>
                                            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                                                Ready to Compete?
                                            </h3>
                                            <p className="text-gray-600 dark:text-gray-400 mb-4">
                                                Join the monthly trading contest and compete for the $100 prize!
                                                Use your paper trading portfolio to showcase your skills.
                                            </p>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                                            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                                                <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">📈 Paper Trading</h4>
                                                <p className="text-sm text-blue-700 dark:text-blue-300">
                                                    Practice with virtual money and build your portfolio
                                                </p>
                                            </div>
                                            <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                                                <h4 className="font-semibold text-green-900 dark:text-green-100 mb-2">🏆 Win Prizes</h4>
                                                <p className="text-sm text-green-700 dark:text-green-300">
                                                    Compete for monthly prizes and recognition
                                                </p>
                                            </div>
                                        </div>

                                        <div className="flex flex-col sm:flex-row gap-3 justify-center">
                                            <button
                                                onClick={() => setShowJoinForm(true)}
                                                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold"
                                            >
                                                Join Contest Now
                                            </button>
                                            <Link
                                                href="/paper-trading"
                                                className="px-6 py-3 border-2 border-green-600 text-green-600 rounded-lg hover:bg-green-50 font-semibold text-center"
                                            >
                                                Start Paper Trading
                                            </Link>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Leaderboard */}
                        <ContestLeaderboard
                            rankings={rankings}
                            myEntry={myEntry}
                            onRefresh={handleRefresh}
                            refreshing={refreshing}
                        />

                        {/* Notifications */}
                        {user && notifications.length > 0 && (
                            <ContestNotifications
                                notifications={notifications}
                                onMarkRead={async (notificationId: string) => {
                                    try {
                                        const response = await fetch(`/api/contest/notifications/${notificationId}/read`, {
                                            method: 'POST',
                                            headers: {
                                                'Authorization': `Bearer ${user.id}`
                                            }
                                        })
                                        if (response.ok) {
                                            setNotifications(prev =>
                                                prev.map(n =>
                                                    n.id === notificationId ? { ...n, is_read: true } : n
                                                )
                                            )
                                        }
                                    } catch (error) {
                                        console.error('Error marking notification read:', error)
                                    }
                                }}
                            />
                        )}
                    </div>
                ) : (
                    <div className="text-center py-12">
                        <div className="text-gray-400 dark:text-gray-500 text-6xl mb-4">🏆</div>
                        <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
                            No Active Contest
                        </h2>
                        <p className="text-gray-600 dark:text-gray-400">
                            There is currently no active contest. Check back soon for the next competition!
                        </p>
                    </div>
                )}

                {/* Join Contest Modal */}
                {showJoinForm && activeContest && (
                    <JoinContestForm
                        contest={activeContest}
                        onJoin={handleJoinContest}
                    />
                )}
            </main>

            <Footer />
        </div>
    )
} 