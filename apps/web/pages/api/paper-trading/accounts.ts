import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        // Mock paper trading accounts data
        const accounts = [
            {
                id: "account_1",
                user_id: "user_123",
                account_name: "Main Trading Account",
                initial_balance: 100000.00,
                current_balance: 105000.00,
                total_pnl: 5000.00,
                total_pnl_percent: 5.00,
                is_active: true,
                created_at: "2024-01-01T00:00:00Z",
                updated_at: "2024-01-15T10:30:00Z"
            },
            {
                id: "account_2",
                user_id: "user_123",
                account_name: "Conservative Portfolio",
                initial_balance: 50000.00,
                current_balance: 52000.00,
                total_pnl: 2000.00,
                total_pnl_percent: 4.00,
                is_active: true,
                created_at: "2024-01-05T00:00:00Z",
                updated_at: "2024-01-15T10:25:00Z"
            }
        ]

        res.status(200).json(accounts)
    } catch (error) {
        console.error('Error fetching paper trading accounts:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: 'Failed to fetch paper trading accounts'
        })
    }
} 