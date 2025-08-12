// Mock OpenAI implementation for development
// In production, this would use the actual OpenAI SDK

export async function handleChatQuery(
    message: string,
    context?: string
): Promise<string> {
    try {
        // Mock response for development
        const mockResponses = [
            "Based on the current market data, I can see that the Casablanca Stock Exchange is showing mixed signals. The MASI index is currently trading at 13,456.78 with a positive change of 2.34 points.",
            "Looking at the market context, I notice that the banking sector is performing well, with ATW showing strong gains. This could be attributed to the current monetary policy environment.",
            "The market analysis suggests that investors are cautiously optimistic about the Moroccan economy, with key indicators showing stability in the financial sector."
        ]

        const randomResponse = mockResponses[Math.floor(Math.random() * mockResponses.length)]
        return randomResponse
    } catch (error) {
        console.error('Mock OpenAI API error:', error)
        return 'Sorry, I encountered an error while processing your request.'
    }
}

export async function generateCompanySummary(
    companyData: any,
    marketData: any
): Promise<string> {
    try {
        // Mock company summary for development
        const companyName = companyData?.name || 'Unknown Company'
        const sector = companyData?.sector || 'Unknown Sector'
        const price = marketData?.price || 'Unknown'

        return `${companyName} (${sector}) is currently trading at ${price}. The company shows stable performance in the current market environment. Key financial metrics indicate a solid foundation for potential investors.`
    } catch (error) {
        console.error('Mock OpenAI API error:', error)
        return 'Unable to generate company summary due to an error.'
    }
} 