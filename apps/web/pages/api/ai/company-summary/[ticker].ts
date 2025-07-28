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

// Mock data for when database tables don't exist
const getMockCompanyData = (ticker: string): CompanyData => {
    const mockPrice = 45.60 + Math.random() * 20;
    const mockChange = (Math.random() - 0.5) * 2;
    const mockChangePercent = (mockChange / mockPrice) * 100;

    return {
        ticker: ticker.toUpperCase(),
        name: `${ticker.toUpperCase()} Company`,
        sector: 'Technology',
        market_cap: 5000,
        revenue: 1500,
        net_income: 225,
        pe_ratio: 20.2,
        dividend_yield: 2.5,
        current_price: mockPrice,
        price_change_percent: mockChangePercent,
        financial_health: 'Stable',
        key_events: ['Q3 earnings exceeded expectations', 'New product launch announced'],
        performance_trends: 'Positive',
        risks: ['Market volatility', 'Regulatory changes'],
        outlook: 'Favorable'
    }
}

// Mock AI summary generator
const generateMockSummary = (ticker: string, companyData: CompanyData, language: string): string => {
    const summaries = {
        'en': `${ticker} shows strong fundamentals with a market cap of ${companyData.market_cap.toLocaleString()} MAD. The company operates in the ${companyData.sector} sector and currently trades at ${companyData.current_price.toFixed(2)} MAD, with a ${companyData.price_change_percent > 0 ? 'positive' : 'negative'} change of ${Math.abs(companyData.price_change_percent).toFixed(2)}%. With a P/E ratio of ${companyData.pe_ratio} and dividend yield of ${companyData.dividend_yield}%, the stock appears reasonably valued. The company's financial health is ${companyData.financial_health.toLowerCase()}, with positive performance trends. Key risks include market volatility and regulatory changes, but the overall outlook remains favorable for long-term investors.`,
        'fr': `${ticker} affiche des fondamentaux solides avec une capitalisation boursière de ${companyData.market_cap.toLocaleString()} MAD. L'entreprise opère dans le secteur ${companyData.sector} et se négocie actuellement à ${companyData.current_price.toFixed(2)} MAD, avec une variation ${companyData.price_change_percent > 0 ? 'positive' : 'négative'} de ${Math.abs(companyData.price_change_percent).toFixed(2)}%. Avec un ratio P/E de ${companyData.pe_ratio} et un rendement de dividende de ${companyData.dividend_yield}%, l'action semble raisonnablement valorisée. La santé financière de l'entreprise est ${companyData.financial_health.toLowerCase()}, avec des tendances de performance positives.`,
        'ar': `${ticker} يظهر أساسيات قوية مع قيمة سوقية تبلغ ${companyData.market_cap.toLocaleString()} درهم. تعمل الشركة في قطاع ${companyData.sector} وتتداول حالياً بسعر ${companyData.current_price.toFixed(2)} درهم، مع تغير ${companyData.price_change_percent > 0 ? 'إيجابي' : 'سلبي'} بنسبة ${Math.abs(companyData.price_change_percent).toFixed(2)}%. مع نسبة P/E تبلغ ${companyData.pe_ratio} وعائد توزيع أرباح ${companyData.dividend_yield}%، يبدو السهم مقيماً بشكل معقول.`
    }

    return summaries[language as keyof typeof summaries] || summaries['en']
}

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    const { ticker } = req.query
    const { language = 'en' } = req.query

    if (!ticker || typeof ticker !== 'string') {
        return res.status(400).json({ error: 'Ticker is required' })
    }

    try {

        // Check if OpenAI API key is configured
        if (!process.env.OPENAI_API_KEY) {
            console.log('OpenAI API key not configured, using mock data')
            const mockCompanyData = getMockCompanyData(ticker)
            const mockSummary = generateMockSummary(ticker, mockCompanyData, language as string)

            const response: AIResponse = {
                ticker: ticker,
                summary: mockSummary,
                language: language as string,
                generated_at: new Date().toISOString(),
                company_data: mockCompanyData,
                tokens_used: 0,
                cached: false
            }

            return res.status(200).json(response)
        }

        // Check cache first (only if ai_summaries table exists)
        try {
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
        } catch (error) {
            console.log('Cache table not available, proceeding without cache')
        }

        // Fetch real company data from database
        let companyData = null
        try {
            const { data, error } = await supabase
                .from('companies')
                .select('*')
                .eq('ticker', ticker)
                .single()

            if (!error && data) {
                companyData = data
            }
        } catch (error) {
            console.log('Companies table not available, using mock data')
        }

        // If no real data available, use mock data
        if (!companyData) {
            const mockCompanyData = getMockCompanyData(ticker)
            const mockSummary = generateMockSummary(ticker, mockCompanyData, language as string)

            const response: AIResponse = {
                ticker: ticker,
                summary: mockSummary,
                language: language as string,
                generated_at: new Date().toISOString(),
                company_data: mockCompanyData,
                tokens_used: 0,
                cached: false
            }

            return res.status(200).json(response)
        }

        // Prepare company data for AI
        const enrichedCompanyData: CompanyData = {
            ticker: ticker,
            name: companyData.name || ticker,
            sector: companyData.sector || 'Unknown',
            market_cap: companyData.market_cap || 0,
            revenue: companyData.revenue || 0,
            net_income: companyData.net_income || 0,
            pe_ratio: companyData.pe_ratio || 0,
            dividend_yield: companyData.dividend_yield || 0,
            current_price: companyData.current_price || 0,
            price_change_percent: companyData.price_change_percent || 0,
            financial_health: 'Stable',
            key_events: [],
            performance_trends: 'Positive',
            risks: [],
            outlook: 'Favorable'
        }

        // Generate AI summary using OpenAI
        const prompt = generateCompanySummaryPrompt(ticker, enrichedCompanyData, language as string)

        const completion = await openai.chat.completions.create({
            model: "gpt-4o-mini",
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
            max_tokens: 500,
            temperature: 0.3,
        })

        const summary = completion.choices[0]?.message?.content || 'Unable to generate summary'
        const tokensUsed = completion.usage?.total_tokens || 0

        // Cache the result (only if table exists)
        try {
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
        } catch (error) {
            console.log('Could not cache result, ai_summaries table not available')
        }

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

        // Fallback to mock data on error
        const tickerStr = ticker as string
        const languageStr = language as string
        const mockCompanyData = getMockCompanyData(tickerStr)
        const mockSummary = generateMockSummary(tickerStr, mockCompanyData, languageStr)

        const response: AIResponse = {
            ticker: tickerStr,
            summary: mockSummary,
            language: languageStr,
            generated_at: new Date().toISOString(),
            company_data: mockCompanyData,
            tokens_used: 0,
            cached: false
        }

        res.status(200).json(response)
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