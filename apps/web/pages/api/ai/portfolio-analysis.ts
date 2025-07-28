import type { NextApiRequest, NextApiResponse } from 'next'
import OpenAI from 'openai'
import { supabase } from '@/lib/supabase'

// Initialize OpenAI client
const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
})

interface PortfolioHolding {
    ticker: string
    name: string
    quantity: number
    purchase_price: number
    current_price: number
    current_value: number
    total_gain_loss: number
    total_gain_loss_percent: number
    sector: string
    market_cap: number
}

interface PortfolioAnalysis {
    total_value: number
    total_cost: number
    total_pnl: number
    total_pnl_percent: number
    diversification_score: number
    risk_assessment: string
    sector_allocation: Record<string, number>
    top_performers: PortfolioHolding[]
    underperformers: PortfolioHolding[]
    recommendations: string[]
    ai_insights: string
}

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        // Get user from auth header
        const authHeader = req.headers.authorization
        if (!authHeader || !authHeader.startsWith('Bearer ')) {
            return res.status(401).json({ error: 'Unauthorized' })
        }

        const token = authHeader.split(' ')[1]
        const { data: { user }, error: authError } = await supabase.auth.getUser(token)

        if (authError || !user) {
            return res.status(401).json({ error: 'Invalid token' })
        }

        const { portfolio_id } = req.body

        if (!portfolio_id) {
            return res.status(400).json({ error: 'Portfolio ID is required' })
        }

        // Fetch portfolio holdings
        const { data: holdings, error: holdingsError } = await supabase
            .from('portfolio_holdings')
            .select(`
                *,
                companies!inner(
                    name,
                    sector,
                    market_cap
                )
            `)
            .eq('portfolio_id', portfolio_id)

        if (holdingsError) {
            console.error('Database error:', holdingsError)
            return res.status(500).json({ error: 'Failed to fetch portfolio holdings' })
        }

        if (!holdings || holdings.length === 0) {
            return res.status(404).json({ error: 'No holdings found for this portfolio' })
        }

        // Fetch current market prices
        const tickers = holdings.map(h => h.ticker)
        const { data: marketData } = await supabase
            .from('market_data')
            .select('ticker, price, change_percent')
            .in('ticker', tickers)

        // Create market price lookup
        const priceLookup = new Map()
        marketData?.forEach(item => {
            priceLookup.set(item.ticker, {
                price: item.price,
                change_percent: item.change_percent
            })
        })

        // Calculate portfolio metrics
        const portfolioHoldings: PortfolioHolding[] = holdings.map(holding => {
            const marketInfo = priceLookup.get(holding.ticker)
            const currentPrice = marketInfo?.price || holding.average_price
            const currentValue = holding.shares * currentPrice
            const totalGainLoss = currentValue - (holding.shares * holding.average_price)
            const totalGainLossPercent = ((currentValue / (holding.shares * holding.average_price)) - 1) * 100

            return {
                ticker: holding.ticker,
                name: holding.companies?.name || holding.ticker,
                quantity: holding.shares,
                purchase_price: holding.average_price,
                current_price: currentPrice,
                current_value: currentValue,
                total_gain_loss: totalGainLoss,
                total_gain_loss_percent: totalGainLossPercent,
                sector: holding.companies?.sector || 'Unknown',
                market_cap: holding.companies?.market_cap || 0
            }
        })

        // Calculate portfolio totals
        const totalValue = portfolioHoldings.reduce((sum, h) => sum + h.current_value, 0)
        const totalCost = portfolioHoldings.reduce((sum, h) => sum + (h.quantity * h.purchase_price), 0)
        const totalPnl = totalValue - totalCost
        const totalPnlPercent = totalCost > 0 ? (totalPnl / totalCost) * 100 : 0

        // Calculate sector allocation
        const sectorAllocation: Record<string, number> = {}
        portfolioHoldings.forEach(holding => {
            const sector = holding.sector
            sectorAllocation[sector] = (sectorAllocation[sector] || 0) + holding.current_value
        })

        // Calculate diversification score (0-100)
        const sectors = Object.keys(sectorAllocation)
        const diversificationScore = Math.min(100, sectors.length * 20) // 20 points per sector, max 100

        // Identify top performers and underperformers
        const sortedHoldings = [...portfolioHoldings].sort((a, b) => b.total_gain_loss_percent - a.total_gain_loss_percent)
        const topPerformers = sortedHoldings.slice(0, 3)
        const underperformers = sortedHoldings.slice(-3).reverse()

        // Generate AI insights
        const aiPrompt = generatePortfolioAnalysisPrompt(portfolioHoldings, {
            totalValue,
            totalCost,
            totalPnl,
            totalPnlPercent,
            diversificationScore,
            sectorAllocation,
            topPerformers,
            underperformers
        })

        const completion = await openai.chat.completions.create({
            model: "gpt-4o-mini",
            messages: [
                {
                    role: "system",
                    content: "You are a financial advisor specializing in Moroccan markets. Provide practical, actionable insights for portfolio analysis."
                },
                {
                    role: "user",
                    content: aiPrompt
                }
            ],
            max_tokens: 600,
            temperature: 0.3,
        })

        const aiInsights = completion.choices[0]?.message?.content || 'Unable to generate insights'

        // Generate recommendations
        const recommendations = generateRecommendations(portfolioHoldings, diversificationScore, sectorAllocation)

        const analysis: PortfolioAnalysis = {
            total_value: totalValue,
            total_cost: totalCost,
            total_pnl: totalPnl,
            total_pnl_percent: totalPnlPercent,
            diversification_score: diversificationScore,
            risk_assessment: assessRisk(portfolioHoldings, diversificationScore),
            sector_allocation: sectorAllocation,
            top_performers: topPerformers,
            underperformers: underperformers,
            recommendations: recommendations,
            ai_insights: aiInsights
        }

        res.status(200).json(analysis)
    } catch (error) {
        console.error('Error analyzing portfolio:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: 'Failed to analyze portfolio'
        })
    }
}

function generatePortfolioAnalysisPrompt(holdings: PortfolioHolding[], metrics: any): string {
    return `Analyze this Moroccan portfolio and provide insights:

Portfolio Overview:
- Total Value: ${metrics.totalValue.toLocaleString()} MAD
- Total Cost: ${metrics.totalCost.toLocaleString()} MAD
- Total P&L: ${metrics.totalPnl.toLocaleString()} MAD (${metrics.totalPnlPercent.toFixed(2)}%)
- Diversification Score: ${metrics.diversificationScore}/100

Sector Allocation:
${Object.entries(metrics.sectorAllocation).map(([sector, value]) =>
        `- ${sector}: ${(((value as number) / metrics.totalValue) * 100).toFixed(1)}%`
    ).join('\n')}

Top Performers:
${metrics.topPerformers.map((h: PortfolioHolding) =>
        `- ${h.ticker}: ${h.total_gain_loss_percent.toFixed(2)}%`
    ).join('\n')}

Underperformers:
${metrics.underperformers.map((h: PortfolioHolding) =>
        `- ${h.ticker}: ${h.total_gain_loss_percent.toFixed(2)}%`
    ).join('\n')}

Provide insights on:
1. Portfolio health and risk assessment
2. Diversification opportunities
3. Sector-specific considerations
4. Actionable recommendations
5. Market timing considerations

Keep insights practical and focused on Moroccan market context.`
}

function generateRecommendations(holdings: PortfolioHolding[], diversificationScore: number, sectorAllocation: Record<string, number>): string[] {
    const recommendations: string[] = []

    // Diversification recommendations
    if (diversificationScore < 60) {
        recommendations.push("Consider diversifying across more sectors to reduce concentration risk")
    }

    // Sector-specific recommendations
    const bankingWeight = sectorAllocation['Banking'] || 0
    const totalValue = holdings.reduce((sum, h) => sum + h.current_value, 0)

    if ((bankingWeight / totalValue) > 0.4) {
        recommendations.push("High banking sector exposure - consider rebalancing for sector diversification")
    }

    // Performance-based recommendations
    const negativeHoldings = holdings.filter(h => h.total_gain_loss_percent < 0)
    if (negativeHoldings.length > holdings.length * 0.5) {
        recommendations.push("Review underperforming positions and consider stop-loss strategies")
    }

    // Market cap diversification
    const largeCapWeight = holdings.filter(h => h.market_cap > 10000000000).reduce((sum, h) => sum + h.current_value, 0)
    if ((largeCapWeight / totalValue) > 0.8) {
        recommendations.push("Consider adding mid-cap stocks for growth potential")
    }

    return recommendations
}

function assessRisk(holdings: PortfolioHolding[], diversificationScore: number): string {
    if (diversificationScore < 40) {
        return "High Risk - Low diversification"
    } else if (diversificationScore < 70) {
        return "Medium Risk - Moderate diversification"
    } else {
        return "Low Risk - Well diversified"
    }
} 