import { NextApiRequest, NextApiResponse } from 'next'
import Stripe from 'stripe'
import { buffer } from 'micro'
import { supabase } from '@/lib/supabase'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
})

const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET!

export const config = {
  api: {
    bodyParser: false,
  },
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const buf = await buffer(req)
  const sig = req.headers['stripe-signature']!

  let event: Stripe.Event

  try {
    event = stripe.webhooks.constructEvent(buf, sig, endpointSecret)
  } catch (err) {
    console.error('Webhook signature verification failed:', err)
    return res.status(400).json({ error: 'Invalid signature' })
  }

  try {
    switch (event.type) {
      case 'checkout.session.completed':
        const session = event.data.object as Stripe.Checkout.Session
        
        // Update user subscription tier
        if (session.customer && session.subscription && supabase) {
          const { error } = await supabase
            .from('profiles')
            .update({ 
              tier: 'pro',
              stripe_customer_id: session.customer as string,
              stripe_subscription_id: session.subscription as string,
              updated_at: new Date().toISOString()
            })
            .eq('stripe_customer_id', session.customer)

          if (error) {
            console.error('Error updating user profile:', error)
          }
        }
        break

      case 'customer.subscription.deleted':
        const subscription = event.data.object as Stripe.Subscription
        
        // Downgrade user to free tier
        if (subscription.customer && supabase) {
          const { error } = await supabase
            .from('profiles')
            .update({ 
              tier: 'free',
              stripe_subscription_id: null,
              updated_at: new Date().toISOString()
            })
            .eq('stripe_customer_id', subscription.customer)

          if (error) {
            console.error('Error downgrading user:', error)
          }
        }
        break

      case 'invoice.payment_failed':
        const invoice = event.data.object as Stripe.Invoice
        
        // Handle failed payments
        if (invoice.customer) {
          console.log('Payment failed for customer:', invoice.customer)
          // You might want to send an email notification here
        }
        break

      default:
        console.log(`Unhandled event type: ${event.type}`)
    }

    res.status(200).json({ received: true })
  } catch (error) {
    console.error('Webhook error:', error)
    res.status(500).json({ error: 'Webhook processing failed' })
  }
} 