import Head from 'next/head'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import TickerBar from '@/components/TickerBar'
import MarketOverview from '@/components/MarketOverview'
import MoversTable from '@/components/MoversTable'
import MacroStats from '@/components/MacroStats'
import NewsletterSignup from '@/components/NewsletterSignup'
import NewsFeed from '@/components/NewsFeed'
import MiniChart from '@/components/MiniChart'

export default function Home() {
  return (
    <>
      <Head>
        <title>Casablanca Insight - Morocco Market Research & Analytics</title>
        <meta 
          name="description" 
          content="Real-time Morocco market data, CSE quotes, MASI/MADEX indices, top movers, macro indicators, and AI-powered insights with Morning Maghreb newsletter." 
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-dark-bg text-gray-900 dark:text-dark-text">
        <Header />
        <TickerBar />

        <main className="px-4 py-6 max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
          <section className="lg:col-span-2 space-y-6">
            <MarketOverview />
            <MoversTable />
            <NewsFeed />
          </section>

          <aside className="space-y-6">
            <MacroStats />
            <MiniChart />
            <NewsletterSignup />
          </aside>
        </main>

        <Footer />
      </div>
    </>
  )
}