import { NextApiRequest, NextApiResponse } from 'next'

// Mock portfolio holdings data
const mockHoldings = [
  {
    id: 'holding_1',
    ticker: 'ATW',
    name: 'Attijariwafa Bank',
    quantity: 100,
    purchase_price: 45.50,
    purchase_date: '2024-01-15',
    notes: 'Core banking position',
    current_price: 48.75,
    current_value: 4875.00,
    total_gain_loss: 325.00,
    total_gain_loss_percent: 7.14
  },
  {
    id: 'holding_2',
    ticker: 'BMCE',
    name: 'Bank of Africa',
    quantity: 50,
    purchase_price: 32.20,
    purchase_date: '2024-02-10',
    notes: 'Growth opportunity',
    current_price: 35.80,
    current_value: 1790.00,
    total_gain_loss: 180.00,
    total_gain_loss_percent: 11.18
  },
  {
    id: 'holding_3',
    ticker: 'CIH',
    name: 'CIH Bank',
    quantity: 75,
    purchase_price: 28.90,
    purchase_date: '2024-03-05',
    notes: 'Small cap exposure',
    current_price: 31.25,
    current_value: 2343.75,
    total_gain_loss: 176.25,
    total_gain_loss_percent: 8.13
  },
  {
    id: 'holding_4',
    ticker: 'IAM',
    name: 'Maroc Telecom',
    quantity: 200,
    purchase_price: 85.30,
    purchase_date: '2024-01-20',
    notes: 'Telecom leader',
    current_price: 89.45,
    current_value: 17890.00,
    total_gain_loss: 830.00,
    total_gain_loss_percent: 4.87
  }
]

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { method } = req
  const { portfolioId } = req.query

  // For now, return mock data since we're using mock backend
  // In production, this would proxy to the actual backend API
  
  switch (method) {
    case 'GET':
      // Return mock holdings for the portfolio
      res.status(200).json(mockHoldings)
      break
      
    case 'POST':
      // Add new holding
      const newHolding = {
        id: `holding_${mockHoldings.length + 1}`,
        ticker: req.body.ticker,
        name: `${req.body.ticker} Company`,
        quantity: req.body.quantity,
        purchase_price: req.body.purchase_price,
        purchase_date: req.body.purchase_date || new Date().toISOString().split('T')[0],
        notes: req.body.notes || '',
        current_price: req.body.purchase_price * 1.05, // Mock 5% gain
        current_value: req.body.quantity * (req.body.purchase_price * 1.05),
        total_gain_loss: req.body.quantity * (req.body.purchase_price * 0.05),
        total_gain_loss_percent: 5.0
      }
      
      mockHoldings.push(newHolding)
      res.status(201).json(newHolding)
      break
      
    default:
      res.setHeader('Allow', ['GET', 'POST'])
      res.status(405).end(`Method ${method} Not Allowed`)
  }
} 