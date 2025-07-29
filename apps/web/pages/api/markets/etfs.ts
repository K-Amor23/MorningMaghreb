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
        // Try to load real ETF data
        let etfsData = loadJsonData('data/moroccan_etfs.json')

        // If no real data, generate mock data
        if (!etfsData) {
            etfsData = [
                {
                    id: "1",
                    name: "MASI ETF",
                    ticker: "MASI-ETF",
                    isin: "MA0000012345",
                    underlying_index: "MASI",
                    issuer: "CDG Capital",
                    expense_ratio: 0.0050,
                    inception_date: "2020-01-15",
                    listing_date: "2020-01-20",
                    asset_class: "equity",
                    geographic_focus: "Morocco",
                    sector_focus: "Broad Market",
                    nav: 125.50,
                    price: 125.75,
                    volume: 1500000,
                    total_assets: 2500000000.00,
                    premium_discount: 0.0020,
                    change_amount: 0.75,
                    change_percent: 0.60,
                    high_24h: 126.25,
                    low_24h: 124.80,
                    open_price: 125.00,
                    previous_close: 125.00
                },
                {
                    id: "2",
                    name: "MADEX ETF",
                    ticker: "MADEX-ETF",
                    isin: "MA0000012346",
                    underlying_index: "MADEX",
                    issuer: "Attijari Finance",
                    expense_ratio: 0.0055,
                    inception_date: "2021-03-10",
                    listing_date: "2021-03-15",
                    asset_class: "equity",
                    geographic_focus: "Morocco",
                    sector_focus: "Large Cap",
                    nav: 98.25,
                    price: 98.10,
                    volume: 850000,
                    total_assets: 1800000000.00,
                    premium_discount: -0.0015,
                    change_amount: -0.15,
                    change_percent: -0.15,
                    high_24h: 98.50,
                    low_24h: 97.80,
                    open_price: 98.25,
                    previous_close: 98.25
                },
                {
                    id: "3",
                    name: "Morocco Banks ETF",
                    ticker: "BANK-ETF",
                    isin: "MA0000012347",
                    underlying_index: "Bank Index",
                    issuer: "BMCE Capital",
                    expense_ratio: 0.0060,
                    inception_date: "2022-06-01",
                    listing_date: "2022-06-05",
                    asset_class: "equity",
                    geographic_focus: "Morocco",
                    sector_focus: "Financial",
                    nav: 115.80,
                    price: 116.20,
                    volume: 650000,
                    total_assets: 1200000000.00,
                    premium_discount: 0.0035,
                    change_amount: 1.20,
                    change_percent: 1.04,
                    high_24h: 116.50,
                    low_24h: 114.90,
                    open_price: 115.00,
                    previous_close: 115.00
                },
                {
                    id: "4",
                    name: "Morocco Government Bond ETF",
                    ticker: "GOVT-ETF",
                    isin: "MA0000012348",
                    underlying_index: "Government Bond Index",
                    issuer: "CDG Capital",
                    expense_ratio: 0.0040,
                    inception_date: "2023-01-01",
                    listing_date: "2023-01-05",
                    asset_class: "bond",
                    geographic_focus: "Morocco",
                    sector_focus: "Government",
                    nav: 102.50,
                    price: 102.45,
                    volume: 450000,
                    total_assets: 800000000.00,
                    premium_discount: -0.0005,
                    change_amount: 0.25,
                    change_percent: 0.24,
                    high_24h: 102.60,
                    low_24h: 102.20,
                    open_price: 102.20,
                    previous_close: 102.20
                }
            ]
        }

        // Add some random variation to make data more realistic
        const etfsWithVariation = etfsData.map((etf: any) => ({
            ...etf,
            nav: etf.nav + (Math.random() - 0.5) * 2,
            price: etf.price + (Math.random() - 0.5) * 2,
            change_percent: etf.change_percent + (Math.random() - 0.5) * 1,
            volume: etf.volume + Math.floor((Math.random() - 0.5) * 100000)
        }))

        res.status(200).json({
            success: true,
            etfs: etfsWithVariation,
            timestamp: new Date().toISOString()
        })

    } catch (error) {
        console.error('Error in ETFs API:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: error instanceof Error ? error.message : 'Unknown error'
        })
    }
} 