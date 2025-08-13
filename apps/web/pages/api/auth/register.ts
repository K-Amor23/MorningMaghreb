import { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        const { email, password, full_name, language_preference, marketing_consent } = req.body

        if (!email || !password || !full_name) {
            return res.status(400).json({ error: 'Email, password, and full name are required' })
        }

        // Call backend auth service
        const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000'
        const response = await fetch(`${backendUrl}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email,
                password,
                full_name,
                language_preference: language_preference || 'en',
                marketing_consent: Boolean(marketing_consent),
                terms_accepted_at: new Date().toISOString(),
            }),
        })

        const data = await response.json()

        if (!response.ok) {
            return res.status(response.status).json({ error: data.detail || 'Registration failed' })
        }

        // Return the auth response from backend
        return res.status(200).json(data)
    } catch (error) {
        console.error('Registration API error:', error)
        return res.status(500).json({ error: 'Internal server error' })
    }
} 