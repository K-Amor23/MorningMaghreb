import type { NextApiRequest, NextApiResponse } from 'next'
import OpenAI from 'openai'
import { supabase } from '@/lib/supabase'

// Initialize OpenAI client
const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
})

interface CompanyData {
    ticker: string
    name: string
    sector: string
    market_cap: number
    revenue: number
    net_income: number
    pe_ratio: number
    dividend_yield: number
    current_price: number
    price_change_percent: number
    financial_health: string
    key_events: string[]
    performance_trends: string
    risks: string[]
    outlook: string
}

interface AIResponse {
    ticker: string
    summary: string
    language: string
    generated_at: string
    company_data: CompanyData
    tokens_used: number
    cached: boolean
}

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        const { ticker } = req.query
        const { language = 'en' } = req.query

        if (!ticker || typeof ticker !== 'string') {
            return res.status(400).json({ error: 'Ticker is required' })
        }

        // Check cache first
        const cacheKey = `ai_summary:${ticker}:${language}`
        const { data: cachedSummary } = await supabase
            .from('ai_summaries')
            .select('*')
            .eq('ticker', ticker)
            .eq('language', language)
            .gte('created_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()) // 24 hour cache
            .single()

        if (cachedSummary) {
            return res.status(200).json({
                ticker: ticker,
                summary: cachedSummary.summary,
                language: language,
                generated_at: cachedSummary.created_at,
                company_data: cachedSummary.company_data,
                tokens_used: cachedSummary.tokens_used || 0,
                cached: true
            })
        }

        // Fetch real company data from database
        const { data: companyData, error: companyError } = await supabase
            .from('companies')
            .select('*')
            .eq('ticker', ticker)
            .single()

        if (companyError || !companyData) {
            return res.status(404).json({ error: 'Company not found' })
        }

        // Fetch financial data
        const { data: financialData } = await supabase
            .from('financials_gaap')
            .select('*')
            .eq('company', ticker)
            .order('year', { ascending: false })
            .order('quarter', { ascending: false })
            .limit(1)

        // Fetch market data
        const { data: marketData } = await supabase
            .from('market_data')
            .select('*')
            .eq('ticker', ticker)
            .order('timestamp', { ascending: false })
            .limit(1)

        // Prepare company data for AI
        const enrichedCompanyData: CompanyData = {
            ticker: ticker,
            name: companyData.name || ticker,
            sector: companyData.sector || 'Unknown',
            market_cap: companyData.market_cap || 0,
            revenue: financialData?.[0]?.json_data?.revenue || 0,
            net_income: financialData?.[0]?.json_data?.net_income || 0,
            pe_ratio: marketData?.[0]?.pe_ratio || 0,
            dividend_yield: marketData?.[0]?.dividend_yield || 0,
            current_price: marketData?.[0]?.price || 0,
            price_change_percent: marketData?.[0]?.change_percent || 0,
            financial_health: 'Stable', // Would be calculated based on ratios
            key_events: [], // Would be fetched from news/events
            performance_trends: 'Positive', // Would be calculated from historical data
            risks: [], // Would be identified from analysis
            outlook: 'Favorable' // Would be AI-generated
        }

        // Generate AI summary using OpenAI
        const prompt = generateCompanySummaryPrompt(ticker, enrichedCompanyData, language as string)

        const completion = await openai.chat.completions.create({
            model: "gpt-4o-mini", // Use cost-effective model
            messages: [
                {
                    role: "system",
                    content: "You are a financial analyst specializing in Moroccan companies. Provide clear, concise analysis in the requested language."
                },
                {
                    role: "user",
                    content: prompt
                }
            ],
            max_tokens: 500, // Limit tokens for cost control
            temperature: 0.3, // Lower temperature for more consistent output
        })

        const summary = completion.choices[0]?.message?.content || 'Unable to generate summary'
        const tokensUsed = completion.usage?.total_tokens || 0

        // Cache the result
        await supabase
            .from('ai_summaries')
            .insert({
                ticker: ticker,
                language: language as string,
                summary: summary,
                company_data: enrichedCompanyData,
                tokens_used: tokensUsed,
                created_at: new Date().toISOString()
            })

        const response: AIResponse = {
            ticker: ticker,
            summary: summary,
            language: language as string,
            generated_at: new Date().toISOString(),
            company_data: enrichedCompanyData,
            tokens_used: tokensUsed,
            cached: false
        }

        res.status(200).json(response)
    } catch (error) {
        console.error('Error generating company summary:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: 'Failed to generate company summary'
        })
    }
}

function generateCompanySummaryPrompt(ticker: string, companyData: CompanyData, language: string): string {
    const languageMap = {
        'en': 'English',
        'fr': 'French',
        'ar': 'Arabic'
    }

    return `Analyze ${ticker} (${companyData.name}) and provide a comprehensive summary in ${languageMap[language as keyof typeof languageMap] || 'English'}.

Company Information:
- Sector: ${companyData.sector}
- Market Cap: ${companyData.market_cap.toLocaleString()} MAD
- Current Price: ${companyData.current_price} MAD
- Price Change: ${companyData.price_change_percent}%
- P/E Ratio: ${companyData.pe_ratio}
- Dividend Yield: ${companyData.dividend_yield}%

Financial Data:
- Revenue: ${companyData.revenue.toLocaleString()} MAD
- Net Income: ${companyData.net_income.toLocaleString()} MAD

Please provide a summary covering:
1. Financial health assessment
2. Key performance trends
3. Main risks and challenges
4. Investment outlook
5. Sector-specific considerations

Keep the summary concise (200-300 words) and suitable for retail investors. Focus on practical insights rather than technical jargon.`
} 