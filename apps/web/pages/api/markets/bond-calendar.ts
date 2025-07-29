import { NextApiRequest, NextApiResponse } from 'next'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        // Mock bond issuance calendar data
        const calendar = [
            {
                id: "1",
                issuer: "Government",
                bond_name: "Morocco Government Bond 2028",
                expected_issue_date: "2024-09-15",
                expected_maturity_date: "2028-09-15",
                expected_size: 8000000000.00,
                expected_coupon_rate: 0.0425,
                expected_rating: "BBB+",
                status: "announced"
            },
            {
                id: "2",
                issuer: "Corporate",
                bond_name: "Maroc Telecom Bond 2029",
                expected_issue_date: "2024-10-01",
                expected_maturity_date: "2029-10-01",
                expected_size: 3000000000.00,
                expected_coupon_rate: 0.0475,
                expected_rating: "A",
                status: "announced"
            },
            {
                id: "3",
                issuer: "Corporate",
                bond_name: "Attijariwafa Bank Bond 2027",
                expected_issue_date: "2024-11-15",
                expected_maturity_date: "2027-11-15",
                expected_size: 4000000000.00,
                expected_coupon_rate: 0.0450,
                expected_rating: "A-",
                status: "announced"
            },
            {
                id: "4",
                issuer: "Government",
                bond_name: "Morocco Government Bond 2032",
                expected_issue_date: "2024-12-01",
                expected_maturity_date: "2032-12-01",
                expected_size: 12000000000.00,
                expected_coupon_rate: 0.0500,
                expected_rating: "BBB+",
                status: "announced"
            }
        ]

        res.status(200).json({
            success: true,
            calendar: calendar,
            timestamp: new Date().toISOString()
        })

    } catch (error) {
        console.error('Error in bond calendar API:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: error instanceof Error ? error.message : 'Unknown error'
        })
    }
} 