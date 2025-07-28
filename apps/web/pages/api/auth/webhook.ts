import type { NextApiRequest, NextApiResponse } from 'next'
import { buffer } from 'micro'
import { supabase, isSupabaseConfigured } from '@/lib/supabase'
import Stripe from 'stripe'

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

  try {
    const body = await buffer(req)
    const signature = req.headers['stripe-signature'] as string

    const event = JSON.parse(body.toString()) as Stripe.Event

    // Handle different event types
    switch (event.type) {
      case 'checkout.session.completed':
        await handleCheckoutCompleted(event.data.object)
        break

      case 'invoice.payment_succeeded':
        await handlePaymentSucceeded(event.data.object)
        break

      case 'invoice.payment_failed':
        await handlePaymentFailed(event.data.object)
        break

      case 'customer.subscription.updated':
        await handleSubscriptionUpdated(event.data.object)
        break

      case 'customer.subscription.deleted':
        await handleSubscriptionDeleted(event.data.object)
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

async function handleCheckoutCompleted(session: any) {
  const { customer, subscription, metadata } = session

  if (!metadata?.userId) {
    console.error('No userId in checkout session metadata')
    return
  }

  if (!isSupabaseConfigured() || !supabase) {
    console.error('Supabase not configured')
    return
  }

  // Update user subscription status
  const { error } = await supabase
    .from('user_profiles')
    .update({
      subscription_tier: 'pro',
      stripe_customer_id: customer,
      stripe_subscription_id: subscription,
      subscription_status: 'active',
      updated_at: new Date().toISOString(),
    })
    .eq('user_id', metadata.userId)

  if (error) {
    console.error('Error updating user subscription:', error)
  }
}

async function handlePaymentSucceeded(invoice: any) {
  const { customer, subscription } = invoice

  if (!isSupabaseConfigured() || !supabase) {
    console.error('Supabase not configured')
    return
  }

  // Update subscription status
  const { error } = await supabase
    .from('user_profiles')
    .update({
      subscription_status: 'active',
      updated_at: new Date().toISOString(),
    })
    .eq('stripe_customer_id', customer)

  if (error) {
    console.error('Error updating subscription status:', error)
  }
}

async function handlePaymentFailed(invoice: any) {
  const { customer } = invoice

  if (!isSupabaseConfigured() || !supabase) {
    console.error('Supabase not configured')
    return
  }

  // Update subscription status
  const { error } = await supabase
    .from('user_profiles')
    .update({
      subscription_status: 'past_due',
      updated_at: new Date().toISOString(),
    })
    .eq('stripe_customer_id', customer)

  if (error) {
    console.error('Error updating subscription status:', error)
  }
}

async function handleSubscriptionUpdated(subscription: any) {
  const { customer, status } = subscription

  if (!isSupabaseConfigured() || !supabase) {
    console.error('Supabase not configured')
    return
  }

  // Update subscription status
  const { error } = await supabase
    .from('user_profiles')
    .update({
      subscription_status: status,
      updated_at: new Date().toISOString(),
    })
    .eq('stripe_customer_id', customer)

  if (error) {
    console.error('Error updating subscription:', error)
  }
}

async function handleSubscriptionDeleted(subscription: any) {
  const { customer } = subscription

  if (!isSupabaseConfigured() || !supabase) {
    console.error('Supabase not configured')
    return
  }

  // Downgrade to free tier
  const { error } = await supabase
    .from('user_profiles')
    .update({
      subscription_tier: 'free',
      subscription_status: 'canceled',
      stripe_subscription_id: null,
      updated_at: new Date().toISOString(),
    })
    .eq('stripe_customer_id', customer)

  if (error) {
    console.error('Error handling subscription deletion:', error)
  }
}