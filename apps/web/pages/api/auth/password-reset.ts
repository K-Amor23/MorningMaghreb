import { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        const { email } = req.body

        if (!email) {
            return res.status(400).json({ error: 'Email is required' })
        }

        // Call backend auth service
        const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000'
        const response = await fetch(`${backendUrl}/api/auth/password/reset-request`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email }),
        })

        const data = await response.json()

        if (!response.ok) {
            return res.status(response.status).json({ error: data.detail || 'Password reset request failed' })
        }

        // Return success response
        return res.status(200).json({
            message: 'Password reset email sent successfully',
            ...data
        })
    } catch (error) {
        console.error('Password reset API error:', error)
        return res.status(500).json({ error: 'Internal server error' })
    }
} 