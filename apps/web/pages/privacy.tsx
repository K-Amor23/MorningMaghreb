import Head from 'next/head'

export default function Privacy() {
    return (
        <>
            <Head>
                <title>Privacy Policy - Morning Maghreb</title>
            </Head>
            <main className="max-w-3xl mx-auto px-4 py-12 prose dark:prose-invert">
                <h1>Privacy Policy</h1>
                <p>Last updated: {new Date().toISOString().slice(0, 10)}</p>
                <h2>Overview</h2>
                <p>We respect your privacy. This policy explains how we collect, use, and protect your information.</p>
                <h2>Information We Collect</h2>
                <ul>
                    <li>Account data: email, name, and preferences you provide</li>
                    <li>Usage data: pages visited, actions to improve our service</li>
                    <li>Billing data: handled by Stripe; we store relevant subscription metadata</li>
                </ul>
                <h2>How We Use Information</h2>
                <ul>
                    <li>To provide and improve the Service</li>
                    <li>To send newsletters if you opt in (you can unsubscribe anytime)</li>
                    <li>To comply with legal obligations</li>
                </ul>
                <h2>Cookies</h2>
                <p>We use cookies for session management and analytics. You can control cookies via your browser.</p>
                <h2>Data Sharing</h2>
                <p>We do not sell personal data. We share data with processors (e.g., Stripe, Supabase) to operate the Service.</p>
                <h2>Data Retention</h2>
                <p>We retain data as long as necessary to provide the Service and meet legal obligations.</p>
                <h2>Your Rights</h2>
                <p>You may request access, correction, or deletion of your data by contacting support@morningmaghreb.com.</p>
                <h2>Contact</h2>
                <p>For privacy questions, email support@morningmaghreb.com.</p>
            </main>
        </>
    )
}








