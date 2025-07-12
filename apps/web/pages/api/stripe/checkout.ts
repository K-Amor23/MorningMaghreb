import { NextApiRequest, NextApiResponse } from 'next'
import Stripe from 'stripe'

// Check if Stripe is configured
const stripeSecretKey = process.env.STRIPE_SECRET_KEY
if (!stripeSecretKey) {
  console.warn('STRIPE_SECRET_KEY is not configured. Stripe checkout will not work.')
}

const stripe = stripeSecretKey ? new Stripe(stripeSecretKey, {
  apiVersion: '2023-10-16',
}) : null

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  // Check if Stripe is configured
  if (!stripe) {
    console.error('Stripe is not configured. Please set STRIPE_SECRET_KEY environment variable.')
    return res.status(500).json({ 
      error: 'Payment processing is not configured',
      message: 'Please contact support to set up payment processing.'
    })
  }

  try {
    const { priceId, successUrl, cancelUrl } = req.body

    if (!priceId || !successUrl || !cancelUrl) {
      return res.status(400).json({ error: 'Missing required parameters' })
    }

    // Create Stripe checkout session
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      mode: 'subscription',
      success_url: successUrl,
      cancel_url: cancelUrl,
      metadata: {
        // Add any additional metadata you need
        product: 'premium_subscription',
      },
    })

    res.status(200).json({ url: session.url })
  } catch (error) {
    console.error('Stripe checkout error:', error)
    res.status(500).json({ error: 'Failed to create checkout session' })
  }
} 