import type { NextApiRequest, NextApiResponse } from 'next'

interface NewsletterSubscriber {
    id: string
    email: string
    status: 'active' | 'unsubscribed'
    subscribedAt: string
    lastEmailSent?: string
    language: 'en' | 'fr' | 'ar'
}

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        // Mock data for now - replace with actual database queries later
        const mockSubscribers: NewsletterSubscriber[] = [
            {
                id: '1',
                email: 'john.doe@example.com',
                status: 'active',
                subscribedAt: '2025-01-15T10:30:00Z',
                lastEmailSent: '2025-07-29T08:00:00Z',
                language: 'en'
            },
            {
                id: '2',
                email: 'marie.dupont@example.fr',
                status: 'active',
                subscribedAt: '2025-02-20T14:45:00Z',
                lastEmailSent: '2025-07-29T08:00:00Z',
                language: 'fr'
            },
            {
                id: '3',
                email: 'ahmed.benali@example.ma',
                status: 'active',
                subscribedAt: '2025-03-10T09:15:00Z',
                lastEmailSent: '2025-07-29T08:00:00Z',
                language: 'ar'
            },
            {
                id: '4',
                email: 'sarah.wilson@example.com',
                status: 'active',
                subscribedAt: '2025-04-05T16:20:00Z',
                lastEmailSent: '2025-07-22T08:00:00Z',
                language: 'en'
            },
            {
                id: '5',
                email: 'pierre.martin@example.fr',
                status: 'active',
                subscribedAt: '2025-05-12T11:30:00Z',
                lastEmailSent: '2025-07-22T08:00:00Z',
                language: 'fr'
            },
            {
                id: '6',
                email: 'fatima.aziz@example.ma',
                status: 'active',
                subscribedAt: '2025-06-18T13:45:00Z',
                lastEmailSent: '2025-07-15T08:00:00Z',
                language: 'ar'
            },
            {
                id: '7',
                email: 'mike.johnson@example.com',
                status: 'unsubscribed',
                subscribedAt: '2025-01-10T08:00:00Z',
                lastEmailSent: '2025-07-08T08:00:00Z',
                language: 'en'
            },
            {
                id: '8',
                email: 'sophie.lefevre@example.fr',
                status: 'active',
                subscribedAt: '2025-02-28T15:30:00Z',
                lastEmailSent: '2025-07-15T08:00:00Z',
                language: 'fr'
            },
            {
                id: '9',
                email: 'omar.khalil@example.ma',
                status: 'active',
                subscribedAt: '2025-03-25T12:15:00Z',
                lastEmailSent: '2025-07-08T08:00:00Z',
                language: 'ar'
            },
            {
                id: '10',
                email: 'emma.davis@example.com',
                status: 'active',
                subscribedAt: '2025-04-30T10:45:00Z',
                lastEmailSent: '2025-07-01T08:00:00Z',
                language: 'en'
            }
        ]

        const activeSubscribers = mockSubscribers.filter(s => s.status === 'active').length

        res.status(200).json({
            subscribers: mockSubscribers,
            total: mockSubscribers.length,
            active: activeSubscribers
        })
    } catch (error) {
        console.error('Error fetching newsletter subscribers:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: 'Failed to fetch newsletter subscribers'
        })
    }
} 