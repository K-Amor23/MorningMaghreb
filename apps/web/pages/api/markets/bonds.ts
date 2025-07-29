import { NextApiRequest, NextApiResponse } from 'next'
import fs from 'fs'
import path from 'path'

// Helper function to load JSON data
function loadJsonData(filePath: string) {
    try {
        const possiblePaths = [
            path.join(process.cwd(), filePath),
            path.join(process.cwd(), '..', filePath),
            path.join(process.cwd(), '..', '..', filePath),
            path.join(process.cwd(), '..', '..', '..', filePath)
        ]

        for (const fullPath of possiblePaths) {
            if (fs.existsSync(fullPath)) {
                const data = fs.readFileSync(fullPath, 'utf8')
                return JSON.parse(data)
            }
        }
        return null
    } catch (error) {
        console.error(`Error loading ${filePath}:`, error)
        return null
    }
}

export default function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        // Try to load real bond data
        let bondsData = loadJsonData('data/moroccan_bonds.json')

        // If no real data, generate mock data
        if (!bondsData) {
            bondsData = [
                {
                    id: "1",
                    name: "Morocco Government Bond 2025",
                    ticker: "MOR-GOV-2025",
                    isin: "MA0000012349",
                    issuer: "Government",
                    issuer_name: "Morocco Treasury",
                    bond_type: "government",
                    face_value: 10000.00,
                    coupon_rate: 0.0350,
                    maturity_date: "2025-12-31",
                    issue_size: 10000000000.00,
                    credit_rating: "BBB+",
                    price: 9850.00,
                    yield_to_maturity: 4.25,
                    current_yield: 3.55,
                    modified_duration: 1.2,
                    change_percent: 0.15
                },
                {
                    id: "2",
                    name: "Morocco Government Bond 2030",
                    ticker: "MOR-GOV-2030",
                    isin: "MA0000012350",
                    issuer: "Government",
                    issuer_name: "Morocco Treasury",
                    bond_type: "government",
                    face_value: 10000.00,
                    coupon_rate: 0.0400,
                    maturity_date: "2030-12-31",
                    issue_size: 15000000000.00,
                    credit_rating: "BBB+",
                    price: 9750.00,
                    yield_to_maturity: 4.50,
                    current_yield: 4.10,
                    modified_duration: 6.8,
                    change_percent: -0.25
                },
                {
                    id: "3",
                    name: "Attijariwafa Bank Bond 2026",
                    ticker: "ATW-BOND-2026",
                    isin: "MA0000012351",
                    issuer: "Corporate",
                    issuer_name: "Attijariwafa Bank",
                    bond_type: "corporate",
                    face_value: 10000.00,
                    coupon_rate: 0.0450,
                    maturity_date: "2026-06-30",
                    issue_size: 5000000000.00,
                    credit_rating: "A-",
                    price: 10150.00,
                    yield_to_maturity: 4.15,
                    current_yield: 4.43,
                    modified_duration: 1.8,
                    change_percent: 0.30
                },
                {
                    id: "4",
                    name: "BMCE Bank Bond 2027",
                    ticker: "BMCE-BOND-2027",
                    isin: "MA0000012352",
                    issuer: "Corporate",
                    issuer_name: "BMCE Bank",
                    bond_type: "corporate",
                    face_value: 10000.00,
                    coupon_rate: 0.0425,
                    maturity_date: "2027-12-31",
                    issue_size: 3000000000.00,
                    credit_rating: "A-",
                    price: 10025.00,
                    yield_to_maturity: 4.30,
                    current_yield: 4.24,
                    modified_duration: 3.2,
                    change_percent: 0.10
                }
            ]
        }

        // Add some random variation to make data more realistic
        const bondsWithVariation = bondsData.map((bond: any) => ({
            ...bond,
            price: bond.price + (Math.random() - 0.5) * 100,
            yield_to_maturity: bond.yield_to_maturity + (Math.random() - 0.5) * 0.5,
            change_percent: bond.change_percent + (Math.random() - 0.5) * 2
        }))

        res.status(200).json({
            success: true,
            bonds: bondsWithVariation,
            timestamp: new Date().toISOString()
        })

    } catch (error) {
        console.error('Error in bonds API:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: error instanceof Error ? error.message : 'Unknown error'
        })
    }
} 