import Head from 'next/head'
import useSWR from 'swr'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

type Status = {
    ok: boolean
    market_status: any | null
    counts: { comprehensive_market_data: number; company_news: number }
    timestamp: string
}

const fetcher = (url: string) => fetch(url).then(r => r.json())

export default function PipelineStatusPage() {
    const { data, error, isLoading } = useSWR<Status>('/api/pipeline/status', fetcher, { refreshInterval: 30000 })

    return (
        <>
            <Head>
                <title>Pipeline Status | Casablanca Insights</title>
            </Head>
            <div className="min-h-screen bg-gray-50 dark:bg-dark-bg text-gray-900 dark:text-dark-text">
                <Header />
                <main className="px-4 py-8 max-w-5xl mx-auto">
                    <h1 className="text-2xl font-semibold mb-6">Pipeline Status</h1>

                    {isLoading && <div className="text-gray-500">Loading...</div>}
                    {error && <div className="text-red-600">Failed to load status</div>}

                    {data && data.ok && (
                        <div className="space-y-6">
                            <section className="bg-white dark:bg-dark-card p-6 rounded-lg border border-gray-200 dark:border-dark-border">
                                <h2 className="text-lg font-semibold mb-4">Market Status</h2>
                                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                                    <div>
                                        <div className="text-gray-500">Status</div>
                                        <div className="font-medium">{data.market_status?.status ?? 'unknown'}</div>
                                    </div>
                                    <div>
                                        <div className="text-gray-500">Local Time</div>
                                        <div className="font-medium">{data.market_status?.current_time_local ?? '-'}</div>
                                    </div>
                                    <div>
                                        <div className="text-gray-500">Trading Hours</div>
                                        <div className="font-medium">{data.market_status?.trading_hours ?? '-'}</div>
                                    </div>
                                </div>
                            </section>

                            <section className="bg-white dark:bg-dark-card p-6 rounded-lg border border-gray-200 dark:border-dark-border">
                                <h2 className="text-lg font-semibold mb-4">Today&apos;s Ingest</h2>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                                    <div>
                                        <div className="text-gray-500">comprehensive_market_data</div>
                                        <div className="font-medium">{data.counts.comprehensive_market_data}</div>
                                    </div>
                                    <div>
                                        <div className="text-gray-500">company_news</div>
                                        <div className="font-medium">{data.counts.company_news}</div>
                                    </div>
                                </div>
                                <div className="text-xs text-gray-500 mt-3">Updated: {new Date(data.timestamp).toLocaleString()}</div>
                            </section>
                        </div>
                    )}
                </main>
                <Footer />
            </div>
        </>
    )
}


