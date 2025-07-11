import type { NextApiRequest, NextApiResponse } from 'next'

// Mock performance data
const mockPerformance = {
  total_return: -1500.00,
  total_return_percent: -1.50,
  best_performer: 'ATW',
  worst_performer: 'IAM',
  total_trades: 2,
  winning_trades: 1,
  losing_trades: 1,
  win_rate: 50.00
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { accountId } = req.query

  if (req.method === 'GET') {
    // Return mock performance data
    return res.status(200).json(mockPerformance)
  }

  return res.status(405).json({ error: 'Method not allowed' })
} 