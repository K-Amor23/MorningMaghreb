import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        // Mock user contest entry
        // In a real implementation, this would fetch from database based on user ID
        const userEntry = {
            id: "entry_123456",
            contest_id: "contest_2024_01",
            user_id: "user_123",
            account_id: "account_456",
            username: "Trader_12345678",
            initial_balance: 100000.00,
            current_balance: 105000.00,
            total_return: 5000.00,
            total_return_percent: 5.00,
            position_count: 4,
            status: "active",
            rank: 11,
            joined_at: "2024-01-15T09:00:00Z",
            updated_at: "2024-01-15T10:30:00Z"
        }

        res.status(200).json(userEntry)
    } catch (error) {
        console.error('Error fetching user contest entry:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: 'Failed to fetch user contest entry'
        })
    }
} 