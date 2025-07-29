import { NextApiRequest, NextApiResponse } from 'next'
import path from 'path'
import fs from 'fs'

// Types for macro data
interface MacroIndicator {
    indicator: string
    value: number
    unit: string
    period: string
    source: string
    previous_value?: number
    change?: number
    change_percent?: number
    description?: string
    category?: string
}

interface MacroData {
    indicators: MacroIndicator[]
    historical_data: {
        gdp_growth: Array<{ year: number, value: number, growth: number }>
        inflation_rate: Array<{ month: string, headline: number, core: number, food: number, energy: number }>
        exchange_rates: Array<{ date: string, usd: number, eur: number, gbp: number, cny: number }>
        trade_balance: Array<{ month: string, exports: number, imports: number, balance: number }>
    }
    scraped_at: string
    summary: {
        total_indicators: number
        sources: string[]
        categories: string[]
    }
}

// Mock data as fallback
const mockMacroData: MacroData = {
    indicators: [
        {
            indicator: "policy_rate",
            value: 3.00,
            unit: "%",
            period: "2024-07",
            source: "Bank Al-Maghrib",
            previous_value: 3.00,
            change: 0.00,
            change_percent: 0.00,
            description: "Central bank benchmark rate",
            category: "monetary"
        },
        {
            indicator: "inflation_rate",
            value: 2.8,
            unit: "%",
            period: "2024-06",
            source: "HCP",
            previous_value: 2.9,
            change: -0.1,
            change_percent: -3.4,
            description: "Consumer price index YoY",
            category: "prices"
        },
        {
            indicator: "gdp_growth",
            value: 3.5,
            unit: "%",
            period: "2023",
            source: "HCP",
            previous_value: 3.2,
            change: 0.3,
            change_percent: 9.4,
            description: "Annual GDP growth rate",
            category: "growth"
        },
        {
            indicator: "fx_reserves",
            value: 34.2,
            unit: "Billion USD",
            period: "2024-06",
            source: "Bank Al-Maghrib",
            previous_value: 33.4,
            change: 0.8,
            change_percent: 2.4,
            description: "Foreign exchange reserves",
            category: "external"
        },
        {
            indicator: "trade_balance",
            value: -2.1,
            unit: "Billion USD",
            period: "2024-06",
            source: "Customs Administration",
            previous_value: -1.8,
            change: -0.3,
            change_percent: -16.7,
            description: "Monthly trade deficit",
            category: "external"
        },
        {
            indicator: "mad_usd_rate",
            value: 9.85,
            unit: "MAD/USD",
            period: "2024-07-24",
            source: "Bank Al-Maghrib",
            previous_value: 9.90,
            change: -0.05,
            change_percent: -0.51,
            description: "Dirham to US Dollar exchange rate",
            category: "external"
        },
        {
            indicator: "unemployment_rate",
            value: 11.8,
            unit: "%",
            period: "2024-Q1",
            source: "HCP",
            previous_value: 12.1,
            change: -0.3,
            change_percent: -2.5,
            description: "National unemployment rate",
            category: "labor"
        },
        {
            indicator: "government_debt",
            value: 69.7,
            unit: "% of GDP",
            period: "2023",
            source: "Ministry of Finance",
            previous_value: 70.2,
            change: -0.5,
            change_percent: -0.7,
            description: "Central government debt",
            category: "fiscal"
        }
    ],
    historical_data: {
        gdp_growth: [
            { year: 2019, value: 119.7, growth: 2.6 },
            { year: 2020, value: 114.7, growth: -7.2 },
            { year: 2021, value: 132.7, growth: 7.9 },
            { year: 2022, value: 129.6, growth: 1.3 },
            { year: 2023, value: 134.2, growth: 3.5 }
        ],
        inflation_rate: [
            { month: "2024-01", headline: 3.1, core: 2.8, food: 3.5, energy: 2.1 },
            { month: "2024-02", headline: 3.0, core: 2.7, food: 3.4, energy: 2.0 },
            { month: "2024-03", headline: 2.9, core: 2.6, food: 3.3, energy: 1.9 },
            { month: "2024-04", headline: 2.9, core: 2.6, food: 3.2, energy: 1.9 },
            { month: "2024-05", headline: 2.9, core: 2.5, food: 3.2, energy: 1.8 },
            { month: "2024-06", headline: 2.8, core: 2.5, food: 3.2, energy: 1.8 }
        ],
        exchange_rates: [
            { date: "2024-01", usd: 9.90, eur: 10.80, gbp: 12.60, cny: 1.38 },
            { date: "2024-02", usd: 9.88, eur: 10.78, gbp: 12.55, cny: 1.37 },
            { date: "2024-03", usd: 9.87, eur: 10.77, gbp: 12.52, cny: 1.37 },
            { date: "2024-04", usd: 9.86, eur: 10.76, gbp: 12.48, cny: 1.36 },
            { date: "2024-05", usd: 9.85, eur: 10.75, gbp: 12.45, cny: 1.36 },
            { date: "2024-06", usd: 9.84, eur: 10.74, gbp: 12.42, cny: 1.35 },
            { date: "2024-07", usd: 9.85, eur: 10.75, gbp: 12.45, cny: 1.36 }
        ],
        trade_balance: [
            { month: "2024-01", exports: 31.2, imports: 33.8, balance: -2.6 },
            { month: "2024-02", exports: 30.8, imports: 33.2, balance: -2.4 },
            { month: "2024-03", exports: 31.5, imports: 33.5, balance: -2.0 },
            { month: "2024-04", exports: 32.1, imports: 34.1, balance: -2.0 },
            { month: "2024-05", exports: 32.5, imports: 34.5, balance: -2.0 },
            { month: "2024-06", exports: 32.8, imports: 34.9, balance: -2.1 }
        ]
    },
    scraped_at: new Date().toISOString(),
    summary: {
        total_indicators: 8,
        sources: ["Bank Al-Maghrib", "HCP", "Customs Administration", "Ministry of Finance"],
        categories: ["monetary", "prices", "growth", "external", "labor", "fiscal"]
    }
}

function loadMacroData(): MacroData {
    try {
        // Try to load from backend data directory
        const dataPath = path.join(process.cwd(), '..', 'backend', 'data', 'macro')
        const files = fs.readdirSync(dataPath)

        if (files.length > 0) {
            // Get the most recent file
            const latestFile = files
                .filter(file => file.endsWith('.json'))
                .sort()
                .pop()

            if (latestFile) {
                const filePath = path.join(dataPath, latestFile)
                const data = fs.readFileSync(filePath, 'utf-8')
                return JSON.parse(data)
            }
        }
    } catch (error) {
        console.warn('Could not load macro data from file, using mock data:', error)
    }

    return mockMacroData
}

export default function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        const { category, indicator } = req.query

        const macroData = loadMacroData()

        // Filter by category if specified
        if (category && typeof category === 'string') {
            macroData.indicators = macroData.indicators.filter(
                ind => ind.category === category
            )
        }

        // Filter by specific indicator if specified
        if (indicator && typeof indicator === 'string') {
            macroData.indicators = macroData.indicators.filter(
                ind => ind.indicator === indicator
            )
        }

        // Update summary
        macroData.summary.total_indicators = macroData.indicators.length
        macroData.summary.sources = Array.from(new Set(macroData.indicators.map(ind => ind.source)))
        macroData.summary.categories = Array.from(new Set(macroData.indicators.map(ind => ind.category).filter((cat): cat is string => Boolean(cat))))

        res.status(200).json({
            success: true,
            data: macroData
        })

    } catch (error) {
        console.error('Error in macro API:', error)
        res.status(500).json({
            success: false,
            error: 'Internal server error',
            data: mockMacroData // Fallback to mock data
        })
    }
} 