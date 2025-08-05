import Head from 'next/head'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import TickerBar from '@/components/TickerBar'
import NewsFeed from '@/components/NewsFeed'

export default function News() {
  // Mock news categories
  const categories = ['All', 'Markets', 'Companies', 'Economy', 'Regulation', 'Technology', 'International']

  // Mock featured news
  const featuredNews = [
    {
      id: 1,
      title: 'MASI Index Reaches New High as Banking Sector Leads Gains',
      excerpt: 'The Casablanca Stock Exchange main index surged 2.3% today, driven by strong performance in the banking sector...',
      category: 'Markets',
      publishedAt: '2 hours ago',
      readTime: '3 min read',
      image: '/api/placeholder/400/200',
      featured: true
    },
    {
      id: 2,
      title: 'Attijariwafa Bank Reports Strong Q3 Results',
      excerpt: 'Morocco\'s largest bank by market capitalization reported a 15% increase in net profit for the third quarter...',
      category: 'Companies',
      publishedAt: '4 hours ago',
      readTime: '4 min read',
      image: '/api/placeholder/400/200',
      featured: true
    }
  ]

  // Mock regular news
  const regularNews = [
    {
      id: 3,
      title: 'Morocco\'s GDP Growth Forecast Revised Upward',
      excerpt: 'The International Monetary Fund has revised its growth forecast for Morocco\'s economy to 3.2% for 2024...',
      category: 'Economy',
      publishedAt: '6 hours ago',
      readTime: '2 min read'
    },
    {
      id: 4,
      title: 'New Regulations for Digital Banking Services',
      excerpt: 'Bank Al-Maghrib has announced new regulatory framework for digital banking and fintech services...',
      category: 'Regulation',
      publishedAt: '8 hours ago',
      readTime: '5 min read'
    },
    {
      id: 5,
      title: 'Renewable Energy Investments Surge in Morocco',
      excerpt: 'Morocco continues to lead North Africa in renewable energy investments with new solar and wind projects...',
      category: 'Technology',
      publishedAt: '10 hours ago',
      readTime: '3 min read'
    },
    {
      id: 6,
      title: 'Trade Relations Strengthen with European Union',
      excerpt: 'Morocco and the EU have signed new trade agreements that will boost exports and investment flows...',
      category: 'International',
      publishedAt: '12 hours ago',
      readTime: '4 min read'
    }
  ]

  return (
    <>
      <Head>
        <title>News - Morning Maghreb</title>
        <meta 
          name="description" 
          content="Latest financial news, market updates, and AI-powered insights about the Moroccan economy and Casablanca Stock Exchange." 
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50 text-gray-900">
        <Header />
        <TickerBar />

        <main className="px-4 py-6 max-w-7xl mx-auto">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">News & Insights</h1>
            <p className="text-gray-600 mt-2">Stay informed with the latest market news and AI-powered analysis</p>
          </div>

          {/* Category Filter */}
          <div className="mb-6">
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <button
                  key={category}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                    category === 'All' 
                      ? 'bg-casablanca-blue text-white' 
                      : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <section className="lg:col-span-2 space-y-6">
              {/* Featured News */}
              <div className="space-y-6">
                <h2 className="text-xl font-semibold">Featured Stories</h2>
                {featuredNews.map((article) => (
                  <article key={article.id} className="bg-white rounded-lg shadow overflow-hidden">
                    <div className="md:flex">
                      <div className="md:flex-shrink-0">
                        <div className="h-48 w-full md:w-48 bg-gray-200 flex items-center justify-center">
                          <span className="text-gray-500">Image</span>
                        </div>
                      </div>
                      <div className="p-6">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {article.category}
                          </span>
                          <span className="text-sm text-gray-500">{article.publishedAt}</span>
                          <span className="text-sm text-gray-500">•</span>
                          <span className="text-sm text-gray-500">{article.readTime}</span>
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">
                          {article.title}
                        </h3>
                        <p className="text-gray-600 mb-4">
                          {article.excerpt}
                        </p>
                        <button className="text-casablanca-blue hover:text-blue-700 font-medium">
                          Read more →
                        </button>
                      </div>
                    </div>
                  </article>
                ))}
              </div>

              {/* Regular News */}
              <div className="space-y-6">
                <h2 className="text-xl font-semibold">Latest News</h2>
                <div className="space-y-4">
                  {regularNews.map((article) => (
                    <article key={article.id} className="bg-white rounded-lg shadow p-6">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          {article.category}
                        </span>
                        <span className="text-sm text-gray-500">{article.publishedAt}</span>
                        <span className="text-sm text-gray-500">•</span>
                        <span className="text-sm text-gray-500">{article.readTime}</span>
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {article.title}
                      </h3>
                      <p className="text-gray-600 mb-4">
                        {article.excerpt}
                      </p>
                      <button className="text-casablanca-blue hover:text-blue-700 font-medium">
                        Read more →
                      </button>
                    </article>
                  ))}
                </div>
              </div>

              {/* Load More */}
              <div className="text-center">
                <button className="bg-white border border-gray-300 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-50 transition-colors">
                  Load More Articles
                </button>
              </div>
            </section>

            <aside className="space-y-6">
              {/* AI Insights */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">AI Market Insights</h3>
                <div className="space-y-4">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <div className="text-sm font-medium text-blue-900 mb-1">Market Sentiment</div>
                    <div className="text-2xl font-bold text-blue-600">Bullish</div>
                    <div className="text-xs text-blue-700 mt-1">Based on recent news and technical indicators</div>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg">
                    <div className="text-sm font-medium text-green-900 mb-1">Top Sector</div>
                    <div className="text-lg font-bold text-green-600">Banking</div>
                    <div className="text-xs text-green-700 mt-1">+2.4% today, strong fundamentals</div>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <div className="text-sm font-medium text-purple-900 mb-1">Risk Level</div>
                    <div className="text-lg font-bold text-purple-600">Low</div>
                    <div className="text-xs text-purple-700 mt-1">Stable market conditions</div>
                  </div>
                </div>
              </div>

              {/* Trending Topics */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">Trending Topics</h3>
                <div className="space-y-2">
                  {['#MASI', '#Banking', '#RenewableEnergy', '#Trade', '#DigitalBanking', '#MoroccoEconomy'].map((topic) => (
                    <div key={topic} className="flex justify-between items-center p-2 hover:bg-gray-50 rounded cursor-pointer">
                      <span className="text-blue-600">{topic}</span>
                      <span className="text-sm text-gray-500">1.2K</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Newsletter Signup */}
              <div className="bg-gradient-to-r from-casablanca-blue to-blue-600 rounded-lg shadow p-6 text-white">
                <h3 className="text-lg font-semibold mb-2">Morning Maghreb</h3>
                <p className="text-blue-100 mb-4">Get daily market insights delivered to your inbox</p>
                <div className="space-y-3">
                  <input
                    type="email"
                    placeholder="Enter your email"
                    className="w-full px-3 py-2 rounded text-gray-900 placeholder-gray-500"
                  />
                  <button className="w-full bg-white text-casablanca-blue py-2 px-4 rounded font-medium hover:bg-gray-100 transition-colors">
                    Subscribe
                  </button>
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