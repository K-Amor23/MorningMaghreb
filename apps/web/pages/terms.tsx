import Head from 'next/head'

export default function Terms() {
    return (
        <>
            <Head>
                <title>Terms of Service - Morning Maghreb</title>
            </Head>
            <main className="max-w-3xl mx-auto px-4 py-12 prose dark:prose-invert">
                <h1>Terms of Service</h1>
                <p>Last updated: {new Date().toISOString().slice(0, 10)}</p>
                <p>
                    By accessing or using Morning Maghreb, you agree to be bound by these Terms of Service. If you do not agree,
                    do not use the Service.
                </p>
                <h2>Accounts</h2>
                <p>You are responsible for maintaining the security of your account and for all activities that occur under it.</p>
                <h2>Subscriptions</h2>
                <p>Paid plans renew automatically unless canceled. You may cancel at any time; access remains until the end of the current period.</p>
                <h2>Use of Content</h2>
                <p>Content is provided for informational purposes only and does not constitute financial advice.</p>
                <h2>Acceptable Use</h2>
                <p>No scraping, reselling, or misuse of the Service. We may suspend accounts that violate these Terms.</p>
                <h2>Limitation of Liability</h2>
                <p>To the maximum extent permitted by law, Morning Maghreb is not liable for indirect or consequential damages.</p>
                <h2>Changes</h2>
                <p>We may update these Terms. Continued use after changes constitutes acceptance.</p>
                <h2>Contact</h2>
                <p>Questions? Contact support@morningmaghreb.com.</p>
            </main>
        </>
    )
}


