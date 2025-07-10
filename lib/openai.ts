import OpenAI from 'openai'

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export async function generateFinancialSummary(
  ticker: string,
  ifrsData: any,
  gaapData: any
): Promise<string> {
  try {
    const prompt = `
    As a financial analyst, provide a 3-4 sentence summary of the IFRS to GAAP conversion for ${ticker}.
    
    IFRS Data: ${JSON.stringify(ifrsData, null, 2)}
    GAAP Data: ${JSON.stringify(gaapData, null, 2)}
    
    Focus on:
    - Key adjustments made
    - Impact on key metrics (revenue, profit, ratios)
    - Investment implications
    
    Keep it concise and professional.
    `

    const response = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        {
          role: 'system',
          content: 'You are a financial analyst specializing in IFRS to GAAP conversions for Moroccan companies.',
        },
        {
          role: 'user',
          content: prompt,
        },
      ],
      max_tokens: 300,
      temperature: 0.3,
    })

    return response.choices[0]?.message?.content || ''
  } catch (error) {
    console.error('Error generating financial summary:', error)
    throw new Error('Failed to generate financial summary')
  }
}

export async function handleChatQuery(
  messages: ChatMessage[],
  context?: any
): Promise<string> {
  try {
    const systemMessage: ChatMessage = {
      role: 'system',
      content: `You are an AI assistant for Casablanca Insight, a Morocco-focused financial research platform. 
      You help investors analyze Moroccan market data, financials, and economic indicators.
      
      Available context: ${context ? JSON.stringify(context, null, 2) : 'None'}
      
      Guidelines:
      - Provide accurate, data-driven responses
      - Focus on Moroccan market specifics
      - Reference CSE (Casablanca Stock Exchange) when relevant
      - Explain IFRS to GAAP conversions when asked
      - Be concise but informative
      - If you don't have specific data, say so clearly`,
    }

    const response = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [systemMessage, ...messages],
      max_tokens: 500,
      temperature: 0.4,
    })

    return response.choices[0]?.message?.content || ''
  } catch (error) {
    console.error('Error handling chat query:', error)
    throw new Error('Failed to process chat query')
  }
}

export async function generateNewsletterContent(
  marketData: any,
  financialUpdates: any,
  macroData: any
): Promise<string> {
  try {
    const prompt = `
    Generate content for the "Morning Maghreb" newsletter with the following data:
    
    Market Data: ${JSON.stringify(marketData, null, 2)}
    Financial Updates: ${JSON.stringify(financialUpdates, null, 2)}
    Macro Data: ${JSON.stringify(macroData, null, 2)}
    
    Structure:
    1. Market Overview (2-3 sentences)
    2. Top Movers (highlight 2-3 significant moves)
    3. Corporate Actions (if any)
    4. Macro Highlights (Bank Al Maghrib, economic indicators)
    5. Key Insight (1 analytical observation)
    
    Keep it professional, concise, and focused on actionable insights.
    `

    const response = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        {
          role: 'system',
          content: 'You are a financial newsletter writer specializing in Moroccan markets.',
        },
        {
          role: 'user',
          content: prompt,
        },
      ],
      max_tokens: 800,
      temperature: 0.5,
    })

    return response.choices[0]?.message?.content || ''
  } catch (error) {
    console.error('Error generating newsletter content:', error)
    throw new Error('Failed to generate newsletter content')
  }
}