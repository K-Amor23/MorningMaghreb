import Script from 'next/script'

export default function Pricing() {
    const pricingTableId = process.env.NEXT_PUBLIC_STRIPE_PRICING_TABLE_ID
    const publishableKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY

    return (
        <>
            <Script src="https://js.stripe.com/v3/pricing-table.js" strategy="afterInteractive" />
            <div className="min-h-screen bg-white dark:bg-dark-bg">
                <main className="max-w-5xl mx-auto px-4 py-12">
                    <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">Choose your plan</h1>

                    {!pricingTableId || !publishableKey ? (
                        <div className="rounded-md border border-yellow-300 bg-yellow-50 text-yellow-800 p-4">
                            <p className="font-medium">Stripe pricing table is not configured.</p>
                            <p className="text-sm mt-1">Set NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY and NEXT_PUBLIC_STRIPE_PRICING_TABLE_ID in apps/web/.env.local</p>
                        </div>
                    ) : (
                        // @ts-ignore - custom web component provided by Stripe script
                        <stripe-pricing-table
                            pricing-table-id={pricingTableId}
                            publishable-key={publishableKey}
                        />
                    )}
                </main>
            </div>
        </>
    )
}








