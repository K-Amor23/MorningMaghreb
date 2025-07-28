import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        const { account_id } = req.body

        if (!account_id) {
            return res.status(400).json({ error: 'Account ID is required' })
        }

        // Mock contest entry creation
        const contestEntry = {
            id: "entry_" + Date.now(),
            contest_id: "contest_2024_01",
            user_id: "user_123", // This would come from auth
            account_id: account_id,
            username: "Trader_" + Math.random().toString(36).substr(2, 8),
            initial_balance: 100000.00,
            current_balance: 105000.00,
            total_return: 5000.00,
            total_return_percent: 5.00,
            position_count: 4,
            status: "active",
            rank: 11, // Would be calculated based on performance
            joined_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
        }

        res.status(200).json(contestEntry)
    } catch (error) {
        console.error('Error joining contest:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: 'Failed to join contest'
        })
    }
} 