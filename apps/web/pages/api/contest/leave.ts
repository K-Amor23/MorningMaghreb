import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        // Mock leaving contest
        // In a real implementation, this would update the contest entry status

        res.status(200).json({
            message: 'Successfully left the contest',
            timestamp: new Date().toISOString()
        })
    } catch (error) {
        console.error('Error leaving contest:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: 'Failed to leave contest'
        })
    }
} 