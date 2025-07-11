import type { NextApiRequest, NextApiResponse } from 'next'
import { supabase } from '@/lib/supabase'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const { email, name, preferences } = req.body

    // Validate input
    if (!email || !email.includes('@')) {
      return res.status(400).json({ error: 'Valid email is required' })
    }

    // Check if email already exists
    const { data: existing, error: checkError } = await supabase
      .from('newsletter_subscribers')
      .select('email')
      .eq('email', email)
      .single()

    if (existing) {
      return res.status(409).json({ error: 'Email already subscribed' })
    }

    // Insert new subscriber
    const { data, error } = await supabase
      .from('newsletter_subscribers')
      .insert([
        {
          email,
          name: name || '',
          preferences: preferences || {
            language: 'en',
            delivery_time: '08:00',
            frequency: 'daily',
          },
          status: 'active',
          subscribed_at: new Date().toISOString(),
        },
      ])
      .select()

    if (error) {
      console.error('Newsletter signup error:', error)
      return res.status(500).json({ error: 'Failed to subscribe' })
    }

    // TODO: Send welcome email via SendGrid
    // TODO: Add to mailing list

    res.status(201).json({
      success: true,
      message: 'Successfully subscribed to newsletter',
      data: data[0],
    })
  } catch (error) {
    console.error('Newsletter signup error:', error)
    res.status(500).json({ 
      error: 'Internal server error',
      message: 'Failed to process newsletter signup'
    })
  }
}