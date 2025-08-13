import type { NextApiRequest, NextApiResponse } from 'next'
import Stripe from 'stripe'
import { supabase } from '@/lib/supabase'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || '', {
    apiVersion: '2023-10-16',
})

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        const { priceId, userId, successUrl, cancelUrl, trialDays, promotionCode } = req.body || {}
        if (!priceId) {
            return res.status(400).json({ error: 'priceId is required' })
        }

        if (!process.env.STRIPE_SECRET_KEY) {
            return res.status(500).json({ error: 'Stripe is not configured' })
        }

        // Ensure a Stripe customer exists for this user
        let customerId: string | undefined
        if (userId && supabase) {
            const { data: existing } = await supabase
                .from('billing_customers')
                .select('stripe_customer_id')
                .eq('user_id', userId)
                .single()
            customerId = existing?.stripe_customer_id as string | undefined
            if (!customerId) {
                const customer = await stripe.customers.create({ metadata: { user_id: userId } })
                customerId = customer.id
                await supabase.from('billing_customers').upsert({ user_id: userId, stripe_customer_id: customerId })
            }
        }

        // If a promotion code string is provided (e.g., "FreeTrial"), look up its Stripe ID
        let discounts: Stripe.Checkout.SessionCreateParams.Discount[] | undefined
        if (promotionCode && typeof promotionCode === 'string') {
            try {
                const promos = await stripe.promotionCodes.list({ code: promotionCode, active: true, limit: 1 })
                const promo = promos.data?.[0]
                if (promo?.id) {
                    discounts = [{ promotion_code: promo.id }]
                }
            } catch (e) {
                // Non-fatal: if lookup fails, continue without auto-applying
                // Customers can still enter the code at checkout because allow_promotion_codes is enabled
                console.warn('Promotion code lookup failed:', e)
            }
        }

        const session = await stripe.checkout.sessions.create({
            mode: 'subscription',
            customer: customerId,
            line_items: [{ price: priceId, quantity: 1 }],
            subscription_data: {
                trial_period_days: typeof trialDays === 'number' ? trialDays : 7,
                metadata: userId ? { user_id: userId } : undefined,
            },
            discounts,
            success_url: successUrl || `${process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'}/account?billing=success`,
            cancel_url: cancelUrl || `${process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'}/pricing?billing=cancel`,
            allow_promotion_codes: true,
        })

        return res.status(200).json({ id: session.id, url: session.url })
    } catch (err: any) {
        console.error('create-checkout-session error:', err)
        return res.status(500).json({ error: 'Failed to create checkout session', details: err?.message || String(err) })
    }
}


