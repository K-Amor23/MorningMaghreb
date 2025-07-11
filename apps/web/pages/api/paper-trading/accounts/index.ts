import type { NextApiRequest, NextApiResponse } from 'next'
import { supabase } from '@/lib/supabase'

// Mock data for paper trading accounts
const mockAccounts = [
  {
    id: 'mock-account-1',
    user_id: 'mock-user-id',
    account_name: 'My Paper Trading Account',
    initial_balance: 100000.00,
    current_balance: 100000.00,
    total_pnl: 0.00,
    total_pnl_percent: 0.00,
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
]

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === 'GET') {
    // Return mock accounts
    return res.status(200).json(mockAccounts)
  }

  if (req.method === 'POST') {
    const { account_name, initial_balance } = req.body

    // Create a new mock account
    const newAccount = {
      id: `mock-account-${Date.now()}`,
      user_id: 'mock-user-id',
      account_name: account_name || 'My Paper Trading Account',
      initial_balance: initial_balance || 100000.00,
      current_balance: initial_balance || 100000.00,
      total_pnl: 0.00,
      total_pnl_percent: 0.00,
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }

    mockAccounts.push(newAccount)
    return res.status(201).json(newAccount)
  }

  return res.status(405).json({ error: 'Method not allowed' })
} 