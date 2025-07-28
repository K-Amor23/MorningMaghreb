import { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        const { token, new_password } = req.body

        if (!token || !new_password) {
            return res.status(400).json({ error: 'Token and new password are required' })
        }

        // Call backend auth service
        const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000'
        const response = await fetch(`${backendUrl}/api/auth/password/reset`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token, new_password }),
        })

        const data = await response.json()

        if (!response.ok) {
            return res.status(response.status).json({ error: data.detail || 'Password reset failed' })
        }

        // Return success response
        return res.status(200).json({
            message: 'Password reset successfully',
            ...data
        })
    } catch (error) {
        console.error('Reset password API error:', error)
        return res.status(500).json({ error: 'Internal server error' })
    }
} 