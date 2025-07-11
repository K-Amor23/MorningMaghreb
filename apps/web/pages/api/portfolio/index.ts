import { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { method } = req

  // For now, return mock data since we're using mock backend
  // In production, this would proxy to the actual backend API
  
  switch (method) {
    case 'GET':
      // Return mock portfolio list
      res.status(200).json([
        {
          id: 'portfolio_1',
          name: 'My Portfolio',
          description: 'Main investment portfolio'
        }
      ])
      break
      
    case 'POST':
      // Create new portfolio
      res.status(201).json({
        id: 'portfolio_2',
        name: req.body.name,
        description: req.body.description,
        message: 'Portfolio created successfully'
      })
      break
      
    default:
      res.setHeader('Allow', ['GET', 'POST'])
      res.status(405).end(`Method ${method} Not Allowed`)
  }
} 