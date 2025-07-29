import { NextApiRequest, NextApiResponse } from 'next'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        // Mock yield curve data
        const yieldCurve = [
            { maturity_months: 3, yield: 3.25, date: new Date().toISOString() },
            { maturity_months: 6, yield: 3.45, date: new Date().toISOString() },
            { maturity_months: 12, yield: 3.75, date: new Date().toISOString() },
            { maturity_months: 24, yield: 4.10, date: new Date().toISOString() },
            { maturity_months: 36, yield: 4.35, date: new Date().toISOString() },
            { maturity_months: 60, yield: 4.80, date: new Date().toISOString() },
            { maturity_months: 120, yield: 5.25, date: new Date().toISOString() },
            { maturity_months: 180, yield: 5.50, date: new Date().toISOString() },
            { maturity_months: 240, yield: 5.75, date: new Date().toISOString() }
        ]

        // Add some random variation
        const yieldCurveWithVariation = yieldCurve.map(point => ({
            ...point,
            yield: point.yield + (Math.random() - 0.5) * 0.2
        }))

        res.status(200).json({
            success: true,
            yield_curve: yieldCurveWithVariation,
            timestamp: new Date().toISOString()
        })

    } catch (error) {
        console.error('Error in yield curve API:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: error instanceof Error ? error.message : 'Unknown error'
        })
    }
} 