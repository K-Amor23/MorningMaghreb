import Stripe from 'stripe'
import { supabase } from './supabase'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
    apiVersion: '2023-10-16',
})

export async function handleWebhook(
    event: Stripe.Event,
    signature: string
): Promise<void> {
    try {
        // Verify the event signature
        const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET!
        const verifiedEvent = stripe.webhooks.constructEvent(
            JSON.stringify(event),
            signature,
            endpointSecret
        )

        switch (verifiedEvent.type) {
            case 'customer.subscription.created':
            case 'customer.subscription.updated':
                await handleSubscriptionChange(verifiedEvent.data.object as Stripe.Subscription)
                break
            case 'customer.subscription.deleted':
                await handleSubscriptionCancellation(verifiedEvent.data.object as Stripe.Subscription)
                break
            case 'invoice.payment_succeeded':
                await handlePaymentSucceeded(verifiedEvent.data.object as Stripe.Invoice)
                break
            case 'invoice.payment_failed':
                await handlePaymentFailed(verifiedEvent.data.object as Stripe.Invoice)
                break
            default:
                console.log(`Unhandled event type: ${verifiedEvent.type}`)
        }
    } catch (error) {
        console.error('Error handling webhook:', error)
        throw error
    }
}

async function handleSubscriptionChange(subscription: Stripe.Subscription): Promise<void> {
    try {
        const customerId = subscription.customer as string
        const status = subscription.status
        const priceId = subscription.items.data[0]?.price.id

        // Update user profile with subscription status
        if (!supabase) {
            console.error('Supabase is not configured')
            return
        }

        const { error } = await supabase
            .from('profiles')
            .update({
                subscription_status: status,
                subscription_id: subscription.id,
                price_id: priceId,
                updated_at: new Date().toISOString()
            })
            .eq('stripe_customer_id', customerId)

        if (error) {
            console.error('Error updating profile:', error)
        }
    } catch (error) {
        console.error('Error handling subscription change:', error)
    }
}

async function handleSubscriptionCancellation(subscription: Stripe.Subscription): Promise<void> {
    try {
        const customerId = subscription.customer as string

        // Update user profile to reflect cancellation
        if (!supabase) {
            console.error('Supabase is not configured')
            return
        }

        const { error } = await supabase
            .from('profiles')
            .update({
                subscription_status: 'canceled',
                updated_at: new Date().toISOString()
            })
            .eq('stripe_customer_id', customerId)

        if (error) {
            console.error('Error updating profile:', error)
        }
    } catch (error) {
        console.error('Error handling subscription cancellation:', error)
    }
}

async function handlePaymentSucceeded(invoice: Stripe.Invoice): Promise<void> {
    try {
        const customerId = invoice.customer as string

        // Update user profile with successful payment
        if (!supabase) {
            console.error('Supabase is not configured')
            return
        }

        const { error } = await supabase
            .from('profiles')
            .update({
                last_payment_date: new Date().toISOString(),
                updated_at: new Date().toISOString()
            })
            .eq('stripe_customer_id', customerId)

        if (error) {
            console.error('Error updating profile:', error)
        }
    } catch (error) {
        console.error('Error handling payment succeeded:', error)
    }
}

async function handlePaymentFailed(invoice: Stripe.Invoice): Promise<void> {
    try {
        const customerId = invoice.customer as string

        // Update user profile with failed payment
        if (!supabase) {
            console.error('Supabase is not configured')
            return
        }

        const { error } = await supabase
            .from('profiles')
            .update({
                subscription_status: 'past_due',
                updated_at: new Date().toISOString()
            })
            .eq('stripe_customer_id', customerId)

        if (error) {
            console.error('Error updating profile:', error)
        }
    } catch (error) {
        console.error('Error handling payment failed:', error)
    }
}

export { stripe } 