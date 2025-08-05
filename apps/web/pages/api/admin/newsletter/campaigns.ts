import type { NextApiRequest, NextApiResponse } from 'next'

interface NewsletterCampaign {
    id: string
    subject: string
    status: 'draft' | 'scheduled' | 'sent'
    recipientCount: number
    openRate: number
    clickRate: number
    sentAt?: string
    scheduledFor?: string
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
        const mockCampaigns: NewsletterCampaign[] = [
            {
                id: '1',
                subject: 'Weekly Market Recap - July 29, 2025',
                status: 'sent',
                recipientCount: 1250,
                openRate: 68.5,
                clickRate: 12.3,
                sentAt: '2025-07-29T08:00:00Z',
                language: 'en'
            },
            {
                id: '2',
                subject: 'Récapitulatif Hebdomadaire - 29 Juillet 2025',
                status: 'sent',
                recipientCount: 890,
                openRate: 72.1,
                clickRate: 15.7,
                sentAt: '2025-07-29T08:00:00Z',
                language: 'fr'
            },
            {
                id: '3',
                subject: 'Market Alert: ATW Earnings Surprise',
                status: 'draft',
                recipientCount: 0,
                openRate: 0,
                clickRate: 0,
                language: 'en'
            },
            {
                id: '4',
                subject: 'Weekly Market Recap - July 22, 2025',
                status: 'sent',
                recipientCount: 1180,
                openRate: 65.2,
                clickRate: 11.8,
                sentAt: '2025-07-22T08:00:00Z',
                language: 'en'
            },
            {
                id: '5',
                subject: 'Monthly Macro Update - July 2025',
                status: 'scheduled',
                recipientCount: 1400,
                openRate: 0,
                clickRate: 0,
                scheduledFor: '2025-08-01T08:00:00Z',
                language: 'en'
            }
        ]

        res.status(200).json({
            campaigns: mockCampaigns,
            total: mockCampaigns.length
        })
    } catch (error) {
        console.error('Error fetching newsletter campaigns:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: 'Failed to fetch newsletter campaigns'
        })
    }
} 