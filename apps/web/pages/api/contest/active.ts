import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        // Mock active contest data
        const activeContest = {
            id: "contest_2024_01",
            name: "January 2024 Portfolio Contest",
            description: "Compete with other traders for the $100 monthly prize. Show off your trading skills and win big!",
            start_date: "2024-01-01",
            end_date: "2024-01-31",
            status: "active",
            prize_amount: 100.00,
            min_positions: 3,
            max_participants: null,
            created_at: "2024-01-01T00:00:00Z",
            updated_at: "2024-01-01T00:00:00Z"
        }

        res.status(200).json(activeContest)
    } catch (error) {
        console.error('Error fetching active contest:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: 'Failed to fetch active contest'
        })
    }
} 