import type { NextApiRequest, NextApiResponse } from 'next'

// Mock data for orders
const mockOrders = [
  {
    id: 'order-1',
    account_id: 'mock-account-1',
    ticker: 'ATW',
    order_type: 'buy',
    order_status: 'filled',
    quantity: 100,
    price: 410.00,
    total_amount: 41000.00,
    commission: 41.00,
    filled_quantity: 100,
    filled_price: 410.00,
    filled_at: new Date().toISOString(),
    notes: 'Initial position',
    created_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
    updated_at: new Date(Date.now() - 86400000).toISOString()
  },
  {
    id: 'order-2',
    account_id: 'mock-account-1',
    ticker: 'IAM',
    order_type: 'buy',
    order_status: 'filled',
    quantity: 200,
    price: 158.00,
    total_amount: 31600.00,
    commission: 31.60,
    filled_quantity: 200,
    filled_price: 158.00,
    filled_at: new Date().toISOString(),
    notes: 'Telecom position',
    created_at: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
    updated_at: new Date(Date.now() - 172800000).toISOString()
  }
]

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { accountId } = req.query
  const { status } = req.query

  if (req.method === 'GET') {
    // Filter orders by status if provided
    let filteredOrders = mockOrders
    if (status && status !== 'all') {
      filteredOrders = mockOrders.filter(order => order.order_status === status)
    }

    // Calculate statistics
    const total_orders = mockOrders.length
    const filled_orders = mockOrders.filter(o => o.order_status === 'filled').length
    const pending_orders = mockOrders.filter(o => o.order_status === 'pending').length
    const cancelled_orders = mockOrders.filter(o => o.order_status === 'cancelled').length

    return res.status(200).json({
      orders: filteredOrders,
      total_orders,
      filled_orders,
      pending_orders,
      cancelled_orders
    })
  }

  if (req.method === 'POST') {
    const { ticker, order_type, quantity, price, notes } = req.body

    // Create a new mock order
    const newOrder = {
      id: `order-${Date.now()}`,
      account_id: accountId as string,
      ticker,
      order_type,
      order_status: 'filled', // Mock immediate execution
      quantity,
      price,
      total_amount: quantity * price,
      commission: quantity * price * 0.001, // 0.1% commission
      filled_quantity: quantity,
      filled_price: price,
      filled_at: new Date().toISOString(),
      notes: notes || null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }

    mockOrders.unshift(newOrder) // Add to beginning of array
    return res.status(201).json(newOrder)
  }

  return res.status(405).json({ error: 'Method not allowed' })
} 