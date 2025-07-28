import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        const { limit = 20 } = req.query

        // Mock notifications data
        const notifications = [
            {
                id: "notif_1",
                contest_id: "contest_2024_01",
                user_id: "user_123",
                notification_type: "contest_join",
                message: "You have successfully joined the monthly portfolio contest!",
                is_read: false,
                created_at: "2024-01-15T09:00:00Z"
            },
            {
                id: "notif_2",
                contest_id: "contest_2024_01",
                user_id: "user_123",
                notification_type: "rank_change",
                message: "Congratulations! You moved up to #11 in the contest!",
                is_read: false,
                created_at: "2024-01-15T10:30:00Z"
            },
            {
                id: "notif_3",
                contest_id: "contest_2024_01",
                user_id: "user_123",
                notification_type: "rank_change",
                message: "You are now ranked #12 in the contest.",
                is_read: true,
                created_at: "2024-01-15T10:25:00Z"
            }
        ]

        const limitNum = parseInt(limit as string) || 20
        const limitedNotifications = notifications.slice(0, limitNum)

        res.status(200).json(limitedNotifications)
    } catch (error) {
        console.error('Error fetching contest notifications:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: 'Failed to fetch contest notifications'
        })
    }
} 