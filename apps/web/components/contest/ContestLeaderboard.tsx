import { useState } from 'react'
import { TrophyIcon, UserIcon, ChartBarIcon, GiftIcon, ClockIcon } from '@heroicons/react/24/outline'

interface ContestRanking {
    contest_id: string
    user_id: string
    username: string
    rank: number
    total_return_percent: number
    total_return: number
    position_count: number
    last_updated: string
    is_winner?: boolean
    prize_amount?: number
}

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

interface ContestInfo {
    contest_id: string
    contest_name: string
    prize_pool: number
    total_participants: number
    end_date: string
    rules: {
        min_positions: number
        ranking_metric: string
        eligibility: string
    }
}

interface ContestLeaderboardProps {
    rankings: ContestRanking[]
    myEntry: ContestEntry | null
    contestInfo?: ContestInfo
    onRefresh: () => void
    refreshing: boolean
}

export default function ContestLeaderboard({
    rankings,
    myEntry,
    contestInfo,
    onRefresh,
    refreshing
}: ContestLeaderboardProps) {
    const [showAll, setShowAll] = useState(false)

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0
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

    const getBgColorForChange = (value: number) => {
        if (value > 0) return 'bg-green-50 dark:bg-green-900/20'
        if (value < 0) return 'bg-red-50 dark:bg-red-900/20'
        return 'bg-gray-50 dark:bg-gray-700'
    }

    const getRankIcon = (rank: number) => {
        if (rank === 1) return '🥇'
        if (rank === 2) return '🥈'
        if (rank === 3) return '🥉'
        return `#${rank}`
    }

    const getRankColor = (rank: number) => {
        if (rank === 1) return 'text-yellow-600 dark:text-yellow-400'
        if (rank === 2) return 'text-gray-600 dark:text-gray-400'
        if (rank === 3) return 'text-orange-600 dark:text-orange-400'
        return 'text-gray-500 dark:text-gray-400'
    }

    const getTimeUntilEnd = () => {
        if (!contestInfo?.end_date) return null
        const endDate = new Date(contestInfo.end_date)
        const now = new Date()
        const diff = endDate.getTime() - now.getTime()

        if (diff <= 0) return 'Contest ended'

        const days = Math.floor(diff / (1000 * 60 * 60 * 24))
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))

        if (days > 0) return `${days}d ${hours}h remaining`
        return `${hours}h remaining`
    }

    const displayedRankings = showAll ? rankings : rankings.slice(0, 10)

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <TrophyIcon className="h-6 w-6 text-yellow-500" />
                        <div>
                            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                                {contestInfo?.contest_name || 'Monthly Contest'}
                            </h2>
                            {contestInfo && (
                                <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
                                    <div className="flex items-center space-x-1">
                                        <GiftIcon className="h-4 w-4" />
                                        <span>${contestInfo.prize_pool} Prize</span>
                                    </div>
                                    <div className="flex items-center space-x-1">
                                        <UserIcon className="h-4 w-4" />
                                        <span>{contestInfo.total_participants} Participants</span>
                                    </div>
                                    <div className="flex items-center space-x-1">
                                        <ClockIcon className="h-4 w-4" />
                                        <span>{getTimeUntilEnd()}</span>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                    <button
                        onClick={onRefresh}
                        disabled={refreshing}
                        className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                        {refreshing ? 'Refreshing...' : 'Refresh'}
                    </button>
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Rank
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Trader
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Return %
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Return
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Positions
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Prize
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Updated
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                        {displayedRankings.map((ranking) => {
                            const isMyEntry = myEntry && myEntry.user_id === ranking.user_id
                            const isWinner = ranking.is_winner || ranking.rank === 1
                            return (
                                <tr
                                    key={ranking.user_id}
                                    className={`${getBgColorForChange(ranking.total_return_percent)} ${isMyEntry ? 'ring-2 ring-blue-500' : ''
                                        } ${isWinner ? 'bg-yellow-50 dark:bg-yellow-900/20' : ''}`}
                                >
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <span className={`text-lg font-bold ${getRankColor(ranking.rank)}`}>
                                                {getRankIcon(ranking.rank)}
                                            </span>
                                            {isMyEntry && (
                                                <span className="ml-2 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded">
                                                    You
                                                </span>
                                            )}
                                            {isWinner && (
                                                <span className="ml-2 text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 px-2 py-1 rounded">
                                                    Winner
                                                </span>
                                            )}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <UserIcon className="h-5 w-5 text-gray-400 mr-2" />
                                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                                {ranking.username}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`text-sm font-semibold ${getColorForChange(ranking.total_return_percent)}`}>
                                            {formatPercent(ranking.total_return_percent)}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`text-sm ${getColorForChange(ranking.total_return)}`}>
                                            {formatCurrency(ranking.total_return)}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <ChartBarIcon className="h-4 w-4 text-gray-400 mr-1" />
                                            <span className="text-sm text-gray-900 dark:text-white">
                                                {ranking.position_count}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        {ranking.prize_amount && ranking.prize_amount > 0 ? (
                                            <div className="flex items-center">
                                                <GiftIcon className="h-4 w-4 text-yellow-500 mr-1" />
                                                <span className="text-sm font-semibold text-yellow-600 dark:text-yellow-400">
                                                    {formatCurrency(ranking.prize_amount)}
                                                </span>
                                            </div>
                                        ) : (
                                            <span className="text-sm text-gray-400">-</span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                        {new Date(ranking.last_updated).toLocaleDateString()}
                                    </td>
                                </tr>
                            )
                        })}
                    </tbody>
                </table>
            </div>

            {rankings.length > 10 && (
                <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
                    <button
                        onClick={() => setShowAll(!showAll)}
                        className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                    >
                        {showAll ? 'Show Top 10' : `Show All ${rankings.length} Participants`}
                    </button>
                </div>
            )}

            {rankings.length === 0 && (
                <div className="px-6 py-8 text-center">
                    <TrophyIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500 dark:text-gray-400">
                        No participants yet. Be the first to join!
                    </p>
                </div>
            )}
        </div>
    )
} 