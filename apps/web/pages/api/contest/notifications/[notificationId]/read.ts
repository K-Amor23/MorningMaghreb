import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        const { notificationId } = req.query

        if (!notificationId) {
            return res.status(400).json({ error: 'Notification ID is required' })
        }

        // Mock marking notification as read
        // In a real implementation, this would update the notification in the database

        res.status(200).json({
            message: 'Notification marked as read',
            notification_id: notificationId,
            timestamp: new Date().toISOString()
        })
    } catch (error) {
        console.error('Error marking notification read:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: 'Failed to mark notification as read'
        })
    }
} 