import type { NextApiRequest, NextApiResponse } from 'next'
import { supabase } from '@/lib/supabase'

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

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        const { limit = 10, contest_id = 'contest_2024_01' } = req.query

        // Get user from auth header for personalized data
        const authHeader = req.headers.authorization
        let currentUserId = null

        if (authHeader && authHeader.startsWith('Bearer ')) {
            const token = authHeader.split(' ')[1]
            const { data: { user } } = await supabase.auth.getUser(token)
            currentUserId = user?.id
        }

        // Fetch contest rankings from database
        const { data: entries, error } = await supabase
            .from('contest_entries')
            .select(`
                *,
                paper_trading_accounts!inner(
                    current_balance,
                    initial_balance,
                    total_pnl,
                    total_pnl_percent
                )
            `)
            .eq('contest_id', contest_id)
            .eq('status', 'active')
            .order('total_return_percent', { ascending: false })
            .limit(parseInt(limit as string) || 10)

        if (error) {
            console.error('Database error:', error)
            return res.status(500).json({ error: 'Failed to fetch rankings' })
        }

        // Calculate rankings with prize distribution
        const rankings: ContestRanking[] = entries?.map((entry, index) => {
            const rank = index + 1
            const isWinner = rank === 1
            const prizeAmount = isWinner ? 100 : 0 // $100 monthly prize

            return {
                contest_id: entry.contest_id,
                user_id: entry.user_id,
                username: entry.username || `Trader_${entry.user_id.slice(-8)}`,
                rank,
                total_return_percent: entry.total_return_percent || 0,
                total_return: entry.total_return || 0,
                position_count: entry.position_count || 0,
                last_updated: entry.updated_at,
                is_winner: isWinner,
                prize_amount: prizeAmount
            }
        }) || []

        // Add current user's rank if they're not in top 10
        if (currentUserId && rankings.length > 0) {
            const userRanking = rankings.find(r => r.user_id === currentUserId)
            if (!userRanking) {
                // Get user's rank from database
                const { data: userEntry } = await supabase
                    .from('contest_entries')
                    .select('*')
                    .eq('contest_id', contest_id)
                    .eq('user_id', currentUserId)
                    .eq('status', 'active')
                    .single()

                if (userEntry) {
                    const userRank = {
                        contest_id: userEntry.contest_id,
                        user_id: userEntry.user_id,
                        username: userEntry.username || `Trader_${userEntry.user_id.slice(-8)}`,
                        rank: userEntry.rank || 0,
                        total_return_percent: userEntry.total_return_percent || 0,
                        total_return: userEntry.total_return || 0,
                        position_count: userEntry.position_count || 0,
                        last_updated: userEntry.updated_at,
                        is_winner: false,
                        prize_amount: 0
                    }
                    rankings.push(userRank)
                }
            }
        }

        // Add contest metadata
        const contestInfo = {
            contest_id,
            contest_name: "Monthly Portfolio Contest",
            prize_pool: 100, // $100 monthly prize
            total_participants: rankings.length,
            end_date: "2024-02-01T00:00:00Z", // Auto-reset at month end
            rules: {
                min_positions: 3,
                ranking_metric: "percentage_return",
                eligibility: "registered_users_with_minimum_positions"
            }
        }

        res.status(200).json({
            rankings,
            contest_info: contestInfo,
            current_user_id: currentUserId
        })
    } catch (error) {
        console.error('Error fetching contest rankings:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: 'Failed to fetch contest rankings'
        })
    }
} 