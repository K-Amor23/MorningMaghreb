import { CalendarIcon, CurrencyDollarIcon, UserGroupIcon, ChartBarIcon } from '@heroicons/react/24/outline'

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

interface ContestInfoProps {
    contest: Contest
}

export default function ContestInfo({ contest }: ContestInfoProps) {
    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(amount)
    }

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        })
    }

    const getDaysRemaining = () => {
        const endDate = new Date(contest.end_date)
        const today = new Date()
        const diffTime = endDate.getTime() - today.getTime()
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
        return Math.max(0, diffDays)
    }

    const getProgressPercentage = () => {
        const startDate = new Date(contest.start_date)
        const endDate = new Date(contest.end_date)
        const today = new Date()

        const totalDuration = endDate.getTime() - startDate.getTime()
        const elapsed = today.getTime() - startDate.getTime()

        return Math.min(100, Math.max(0, (elapsed / totalDuration) * 100))
    }

    const daysRemaining = getDaysRemaining()
    const progressPercentage = getProgressPercentage()

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    Contest Information
                </h2>
            </div>

            <div className="p-6 space-y-6">
                {/* Contest Overview */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                        <div className="flex items-center">
                            <CurrencyDollarIcon className="h-8 w-8 text-blue-600 dark:text-blue-400" />
                            <div className="ml-3">
                                <p className="text-sm text-blue-600 dark:text-blue-400">Prize Pool</p>
                                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                                    {formatCurrency(contest.prize_amount)}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                        <div className="flex items-center">
                            <ChartBarIcon className="h-8 w-8 text-green-600 dark:text-green-400" />
                            <div className="ml-3">
                                <p className="text-sm text-green-600 dark:text-green-400">Min Positions</p>
                                <p className="text-2xl font-bold text-green-900 dark:text-green-100">
                                    {contest.min_positions}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                        <div className="flex items-center">
                            <CalendarIcon className="h-8 w-8 text-purple-600 dark:text-purple-400" />
                            <div className="ml-3">
                                <p className="text-sm text-purple-600 dark:text-purple-400">Days Left</p>
                                <p className="text-2xl font-bold text-purple-900 dark:text-purple-100">
                                    {daysRemaining}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                        <div className="flex items-center">
                            <UserGroupIcon className="h-8 w-8 text-orange-600 dark:text-orange-400" />
                            <div className="ml-3">
                                <p className="text-sm text-orange-600 dark:text-orange-400">Max Participants</p>
                                <p className="text-2xl font-bold text-orange-900 dark:text-orange-100">
                                    {contest.max_participants || '∞'}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Contest Timeline */}
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                        Contest Timeline
                    </h3>

                    <div className="relative">
                        <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
                            <span>Start: {formatDate(contest.start_date)}</span>
                            <span>End: {formatDate(contest.end_date)}</span>
                        </div>

                        <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                            <div
                                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${progressPercentage}%` }}
                            ></div>
                        </div>

                        <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                            <span>0%</span>
                            <span>{Math.round(progressPercentage)}%</span>
                            <span>100%</span>
                        </div>
                    </div>
                </div>

                {/* Contest Rules */}
                <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-yellow-900 dark:text-yellow-100 mb-3">
                        Contest Rules
                    </h3>

                    <ul className="space-y-2 text-sm text-yellow-800 dark:text-yellow-200">
                        <li className="flex items-start">
                            <span className="text-yellow-600 dark:text-yellow-400 mr-2">•</span>
                            <span>Must have at least {contest.min_positions} positions in your paper trading account</span>
                        </li>
                        <li className="flex items-start">
                            <span className="text-yellow-600 dark:text-yellow-400 mr-2">•</span>
                            <span>Ranking is based on total return percentage over the contest period</span>
                        </li>
                        <li className="flex items-start">
                            <span className="text-yellow-600 dark:text-yellow-400 mr-2">•</span>
                            <span>Only one account per user can participate</span>
                        </li>
                        <li className="flex items-start">
                            <span className="text-yellow-600 dark:text-yellow-400 mr-2">•</span>
                            <span>Winner receives {formatCurrency(contest.prize_amount)} prize</span>
                        </li>
                        <li className="flex items-start">
                            <span className="text-yellow-600 dark:text-yellow-400 mr-2">•</span>
                            <span>Contest automatically ends on {formatDate(contest.end_date)}</span>
                        </li>
                    </ul>
                </div>

                {/* Contest Description */}
                <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                        About This Contest
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                        {contest.description}
                    </p>
                </div>

                {/* Important Notes */}
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                    <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-2">
                        Important Notes
                    </h4>
                    <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                        <li>• All trading is done with paper money - no real funds are at risk</li>
                        <li>• Rankings are updated in real-time based on current portfolio performance</li>
                        <li>• You can leave the contest at any time, but you won't be able to rejoin</li>
                        <li>• The winner will be contacted via email for prize distribution</li>
                        <li>• Contest results are final and binding</li>
                    </ul>
                </div>
            </div>
        </div>
    )
} 