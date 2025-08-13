import type { NextApiRequest, NextApiResponse } from 'next'
import Stripe from 'stripe'
import { supabase } from '@/lib/supabase'

export const config = {
  api: {
    bodyParser: false,
  },
}

function buffer(req: NextApiRequest): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    const chunks: Uint8Array[] = []
    req.on('data', (chunk) => chunks.push(chunk))
    req.on('end', () => resolve(Buffer.concat(chunks)))
    req.on('error', reject)
  })
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end('Method Not Allowed')
  const sig = req.headers['stripe-signature'] as string
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || '', { apiVersion: '2023-10-16' })

  try {
    const buf = await buffer(req)
    let event: Stripe.Event
    if (webhookSecret) {
      event = stripe.webhooks.constructEvent(buf, sig, webhookSecret)
    } else {
      event = JSON.parse(buf.toString())
    }

    // Idempotency log
    try {
      await supabase!.from('billing_events').insert({
        stripe_event_id: event.id,
        type: event.type,
        payload: event as any,
      })
    } catch (_) { }

    switch (event.type) {
      case 'customer.subscription.created':
      case 'customer.subscription.updated':
      case 'customer.subscription.deleted': {
        const sub = event.data.object as Stripe.Subscription
        const userId = sub.metadata?.user_id || (sub.customer as string) // expect metadata.user_id set via app, fallback by lookup

        // Optional: map price to billing_prices
        const priceId = (sub.items.data[0]?.price?.id as string) || null
        let priceRowId: string | null = null
        if (priceId) {
          const { data: priceRow } = await supabase!
            .from('billing_prices')
            .select('id')
            .eq('stripe_price_id', priceId)
            .single()
          priceRowId = priceRow?.id || null
        }

        await supabase!.from('billing_subscriptions').upsert({
          user_id: userId,
          stripe_subscription_id: sub.id,
          status: sub.status,
          price_id: priceRowId,
          current_period_start: sub.current_period_start ? new Date(sub.current_period_start * 1000).toISOString() : null,
          current_period_end: sub.current_period_end ? new Date(sub.current_period_end * 1000).toISOString() : null,
          cancel_at_period_end: sub.cancel_at_period_end || false,
          canceled_at: sub.canceled_at ? new Date(sub.canceled_at * 1000).toISOString() : null,
        })
        break
      }
      case 'invoice.paid':
      case 'invoice.payment_succeeded': {
        const inv = event.data.object as Stripe.Invoice
        const userId = inv.metadata?.user_id || (inv.customer as string)
        await supabase!.from('billing_invoices').upsert({
          user_id: userId,
          stripe_invoice_id: inv.id,
          status: inv.status || null,
          amount_due: inv.amount_due || null,
          amount_paid: inv.amount_paid || null,
          currency: inv.currency || null,
          hosted_invoice_url: inv.hosted_invoice_url || null,
        })
        break
      }
      default:
        break
    }

    return res.status(200).json({ received: true })
  } catch (err: any) {
    console.error('Stripe webhook error:', err)
    return res.status(400).send(`Webhook Error: ${err.message}`)
  }
}