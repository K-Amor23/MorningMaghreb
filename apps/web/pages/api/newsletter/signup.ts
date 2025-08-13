import type { NextApiRequest, NextApiResponse } from 'next'
import { supabase, isSupabaseConfigured, isSupabaseAvailable } from '@/lib/supabase'
import { getResendClient, isResendConfigured, getFromEmail, getReplyToEmail } from '@/lib/resend'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    // Check if Supabase is properly configured
    if (!isSupabaseConfigured()) {
      console.error('Supabase not configured - missing environment variables')
      return res.status(500).json({
        error: 'Database not configured',
        message: 'Supabase credentials are missing. Please check your environment variables.',
        details: 'NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY must be set'
      })
    }

    if (!isSupabaseAvailable()) {
      console.error('Supabase client not available')
      return res.status(500).json({
        error: 'Database connection failed',
        message: 'Unable to connect to the database. Please check your Supabase configuration.'
      })
    }

    const { email, name, preferences } = req.body

    // Validate input
    if (!email || !email.includes('@')) {
      return res.status(400).json({ error: 'Valid email is required' })
    }

    // Check if email already exists
    const { data: existing, error: checkError } = await supabase!
      .from('newsletter_subscribers')
      .select('email')
      .eq('email', email)
      .single()

    if (checkError && checkError.code !== 'PGRST116') { // PGRST116 is "not found"
      console.error('Error checking existing email:', checkError)
      return res.status(500).json({
        error: 'Database error',
        message: 'Failed to check existing subscription'
      })
    }

    if (existing) {
      return res.status(409).json({ error: 'Email already subscribed' })
    }

    // Insert new subscriber
    const { data, error } = await supabase!
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

      // Check if it's a table not found error
      if (error.code === '42P01') {
        return res.status(500).json({
          error: 'Database table missing',
          message: 'Newsletter subscribers table does not exist. Please run the database setup.',
          details: 'Run: python scripts/deploy_master_pipeline_tables.py'
        })
      }

      return res.status(500).json({
        error: 'Failed to subscribe',
        message: 'Database error occurred while processing your subscription.',
        details: error.message
      })
    }

    // Send welcome email via Resend (if configured)
    try {
      if (isResendConfigured()) {
        const resend = getResendClient()
        const from = getFromEmail()
        const replyTo = getReplyToEmail()
        const recipientName = name ? String(name) : 'there'

        const subject = 'Welcome to Casablanca Insights Newsletter'
        const html = `
          <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <h2>Welcome, ${recipientName} 👋</h2>
            <p>Thanks for subscribing to the Casablanca Insights newsletter.</p>
            <p>We’ll send you concise market summaries, company spotlights, and curated news.</p>
            <p style="margin-top:24px; font-size:12px; color:#6b7280;">If you didn’t sign up, you can ignore this email.</p>
          </div>
        `

        await resend.emails.send({
          from,
          to: [email],
          subject,
          html,
          ...(replyTo ? { reply_to: replyTo } : {}),
        } as any)
      }
    } catch (e) {
      console.error('Failed to send welcome email via Resend:', e)
      // Do not fail the signup because of email issues
    }

    res.status(201).json({
      success: true,
      message: 'Successfully subscribed to newsletter',
      data: data[0],
    })
  } catch (error) {
    console.error('Newsletter signup error:', error)
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to process newsletter signup',
      details: error instanceof Error ? error.message : 'Unknown error'
    })
  }
}