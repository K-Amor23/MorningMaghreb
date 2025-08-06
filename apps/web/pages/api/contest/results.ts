import type { NextApiRequest, NextApiResponse } from 'next'
import { supabase } from '@/lib/supabase'

interface ContestResult {
    contest_id: string
    winner: {
        user_id: string
        username: string
        total_return_percent: number
        total_return: number
        prize_amount: number
    }
    total_participants: number
    prize_distributed: boolean
    contest_end_date: string
    next_contest_start: string
}

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        const contest_id = Array.isArray(req.query.contest_id) ? req.query.contest_id[0] : req.query.contest_id || 'contest_2024_01'

        // Get user from auth header for admin checks
        const authHeader = req.headers.authorization
        let currentUserId = null
        let isAdmin = false

        if (authHeader && authHeader.startsWith('Bearer ')) {
            const token = authHeader.split(' ')[1]
            if (!supabase) {
                console.error('Supabase is not configured')
            } else {
                const { data: { user } } = await supabase.auth.getUser(token)
                currentUserId = user?.id

                // Check if user is admin
                if (currentUserId) {
                    const { data: profile } = await supabase
                        .from('profiles')
                        .select('tier')
                        .eq('id', currentUserId)
                        .single()

                    isAdmin = profile?.tier === 'admin'
                }
            }
        }

        // Fetch contest results
        if (!supabase) {
            return res.status(500).json({ error: 'Database not configured' })
        }

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
            .limit(1)

        if (error) {
            console.error('Database error:', error)
            return res.status(500).json({ error: 'Failed to fetch contest results' })
        }

        if (!entries || entries.length === 0) {
            return res.status(404).json({ error: 'No contest results found' })
        }

        const winner = entries[0]
        const prizeAmount = 100 // $100 monthly prize

        // Check if prize has been distributed
        let prizeDistribution = null
        if (!supabase) {
            console.error('Supabase is not configured')
        } else {
            const { data } = await supabase
                .from('contest_prizes')
                .select('*')
                .eq('contest_id', contest_id)
                .eq('winner_id', winner.user_id)
                .single()
            prizeDistribution = data
        }

        const result: ContestResult = {
            contest_id,
            winner: {
                user_id: winner.user_id,
                username: winner.username || `Trader_${winner.user_id.slice(-8)}`,
                total_return_percent: winner.total_return_percent || 0,
                total_return: winner.total_return || 0,
                prize_amount: prizeAmount
            },
            total_participants: entries.length,
            prize_distributed: !!prizeDistribution,
            contest_end_date: "2024-01-31T23:59:59Z",
            next_contest_start: "2024-02-01T00:00:00Z"
        }

        // If admin and prize not distributed, trigger distribution
        if (isAdmin && !prizeDistribution) {
            await distributePrize(contest_id as string, winner.user_id, prizeAmount)
            result.prize_distributed = true
        }

        res.status(200).json(result)
    } catch (error) {
        console.error('Error fetching contest results:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: 'Failed to fetch contest results'
        })
    }
}

async function distributePrize(contestId: string, winnerId: string, prizeAmount: number) {
    try {
        if (!supabase) {
            console.error('Supabase is not configured')
            return
        }

        // Record prize distribution
        await supabase
            .from('contest_prizes')
            .insert({
                contest_id: contestId,
                winner_id: winnerId,
                prize_amount: prizeAmount,
                distributed_at: new Date().toISOString(),
                status: 'distributed'
            })

        // Send notification to winner
        await supabase
            .from('contest_notifications')
            .insert({
                user_id: winnerId,
                contest_id: contestId,
                notification_type: 'prize_won',
                message: `Congratulations! You've won the monthly contest with a ${prizeAmount} USD prize!`,
                is_read: false,
                created_at: new Date().toISOString()
            })

        // Update contest status
        await supabase
            .from('contests')
            .update({
                status: 'completed',
                winner_id: winnerId,
                completed_at: new Date().toISOString()
            })
            .eq('contest_id', contestId)

        console.log(`Prize distributed to ${winnerId} for contest ${contestId}`)
    } catch (error) {
        console.error('Error distributing prize:', error)
        throw error
    }
} 