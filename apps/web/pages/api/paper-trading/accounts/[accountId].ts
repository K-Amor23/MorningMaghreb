import type { NextApiRequest, NextApiResponse } from 'next'

// Mock data for account summary
const mockAccountSummary = {
  account: {
    id: 'mock-account-1',
    user_id: 'mock-user-id',
    account_name: 'My Paper Trading Account',
    initial_balance: 100000.00,
    current_balance: 98500.00,
    total_pnl: -1500.00,
    total_pnl_percent: -1.50,
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  positions: [
    {
      id: 'pos-1',
      account_id: 'mock-account-1',
      ticker: 'ATW',
      quantity: 100,
      avg_cost: 410.00,
      total_cost: 41000.00,
      current_value: 41100.00,
      unrealized_pnl: 100.00,
      unrealized_pnl_percent: 0.24,
      last_updated: new Date().toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: 'pos-2',
      account_id: 'mock-account-1',
      ticker: 'IAM',
      quantity: 200,
      avg_cost: 158.00,
      total_cost: 31600.00,
      current_value: 31260.00,
      unrealized_pnl: -340.00,
      unrealized_pnl_percent: -1.08,
      last_updated: new Date().toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ],
  total_positions_value: 72360.00,
  total_unrealized_pnl: -240.00,
  total_unrealized_pnl_percent: -0.33,
  available_cash: 98500.00,
  total_account_value: 170860.00
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { accountId } = req.query

  if (req.method === 'GET') {
    // Return mock account summary
    return res.status(200).json(mockAccountSummary)
  }

  return res.status(405).json({ error: 'Method not allowed' })
} 