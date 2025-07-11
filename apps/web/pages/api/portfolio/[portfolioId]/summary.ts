import { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { method } = req
  const { portfolioId } = req.query

  // For now, return mock data since we're using mock backend
  // In production, this would proxy to the actual backend API
  
  switch (method) {
    case 'GET':
      // Calculate mock portfolio summary
      const mockHoldings = [
        { current_value: 4875.00, quantity: 100, purchase_price: 45.50 },
        { current_value: 1790.00, quantity: 50, purchase_price: 32.20 },
        { current_value: 2343.75, quantity: 75, purchase_price: 28.90 },
        { current_value: 17890.00, quantity: 200, purchase_price: 85.30 }
      ]
      
      const totalValue = mockHoldings.reduce((sum, holding) => sum + holding.current_value, 0)
      const totalCost = mockHoldings.reduce((sum, holding) => sum + (holding.quantity * holding.purchase_price), 0)
      const totalGainLoss = totalValue - totalCost
      const totalGainLossPercent = (totalGainLoss / totalCost) * 100
      
      const summary = {
        total_value: totalValue,
        total_cost: totalCost,
        total_gain_loss: totalGainLoss,
        total_gain_loss_percent: totalGainLossPercent,
        holdings_count: mockHoldings.length,
        last_updated: new Date().toISOString()
      }
      
      res.status(200).json(summary)
      break
      
    default:
      res.setHeader('Allow', ['GET'])
      res.status(405).end(`Method ${method} Not Allowed`)
  }
} 