import Head from 'next/head'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import TickerBar from '@/components/TickerBar'
import MarketOverview from '@/components/MarketOverview'
import MoversTable from '@/components/MoversTable'
import MiniChart from '@/components/MiniChart'

export default function Markets() {
  return (
    <>
      <Head>
        <title>Markets - Morning Maghreb</title>
        <meta 
          name="description" 
          content="Detailed market data, charts, and analysis for the Casablanca Stock Exchange (CSE), MASI and MADEX indices." 
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50 text-gray-900">
        <Header />
        <TickerBar />

        <main className="px-4 py-6 max-w-7xl mx-auto">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Markets</h1>
            <p className="text-gray-600 mt-2">Real-time Casablanca Stock Exchange data and analysis</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <section className="lg:col-span-2 space-y-6">
              <MarketOverview />
              <MoversTable />
              
              {/* Additional market sections */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Market Sectors</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {['Banks', 'Insurance', 'Real Estate', 'Industry', 'Mining', 'Energy', 'Transport', 'Services'].map((sector) => (
                    <div key={sector} className="text-center p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                      <div className="text-sm font-medium text-gray-900">{sector}</div>
                      <div className="text-lg font-bold text-green-600">+2.4%</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Trading Volume</h2>
                <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
                  <p className="text-gray-500">Volume chart coming soon</p>
                </div>
              </div>
            </section>

            <aside className="space-y-6">
              <MiniChart />
              
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">Market Statistics</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Market Cap</span>
                    <span className="font-medium">MAD 650.2B</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Daily Volume</span>
                    <span className="font-medium">MAD 245.8M</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Active Stocks</span>
                    <span className="font-medium">78</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Advancers</span>
                    <span className="font-medium text-green-600">45</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Decliners</span>
                    <span className="font-medium text-red-600">23</span>
                  </div>
                </div>
              </div>
            </aside>
          </div>
        </main>

        <Footer />
      </div>
    </>
  )
} 