import { 
  NewspaperIcon, 
  ClockIcon, 
  ArrowTopRightOnSquareIcon 
} from '@heroicons/react/24/outline'

interface NewsItem {
  id: string
  title: string
  summary: string
  source: string
  timestamp: string
  category: 'market' | 'company' | 'economic' | 'regulatory'
  url?: string
}

const mockNewsItems: NewsItem[] = [
  {
    id: '1',
    title: 'MASI Gains 0.36% on Banking Sector Strength',
    summary: 'The Moroccan All Shares Index closed higher today, led by strong performance in the banking sector. Attijariwafa Bank and BMCE Bank both posted gains above 1%, while trading volume reached 2.3 billion MAD.',
    source: 'CSE Market Report',
    timestamp: '2 hours ago',
    category: 'market'
  },
  {
    id: '2',
    title: 'Bank Al-Maghrib Maintains 3% Policy Rate',
    summary: 'The central bank kept its benchmark interest rate unchanged at 3% for the third consecutive meeting, citing stable inflation expectations and moderate economic growth projections.',
    source: 'Bank Al-Maghrib',
    timestamp: '4 hours ago',
    category: 'economic'
  },
  {
    id: '3',
    title: 'Attijariwafa Bank Reports Q3 Earnings Beat',
    summary: 'Morocco\'s largest bank reported quarterly earnings of 2.8 billion MAD, exceeding analyst expectations by 8%. Strong loan growth and improved asset quality drove the positive results.',
    source: 'Financial Times',
    timestamp: '6 hours ago',
    category: 'company',
    url: '#'
  },
  {
    id: '4',
    title: 'New ESG Reporting Requirements Announced',
    summary: 'The Moroccan Capital Market Authority (AMMC) introduced new mandatory ESG reporting standards for listed companies, effective January 2024.',
    source: 'AMMC',
    timestamp: '1 day ago',
    category: 'regulatory'
  }
]

const categoryColors = {
  market: 'bg-blue-100 text-blue-800',
  company: 'bg-green-100 text-green-800',
  economic: 'bg-purple-100 text-purple-800',
  regulatory: 'bg-orange-100 text-orange-800'
}

export default function NewsFeed() {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">News & Filings</h2>
        <div className="flex items-center text-sm text-gray-500">
          <ClockIcon className="h-4 w-4 mr-1" />
          AI-powered summaries
        </div>
      </div>
      
      <div className="space-y-4">
        {mockNewsItems.map((item) => (
          <article key={item.id} className="border-b border-gray-100 pb-4 last:border-b-0 last:pb-0">
            <div className="flex items-start space-x-3">
              <NewspaperIcon className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0" />
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <h3 className="text-sm font-medium text-gray-900 line-clamp-2">
                    {item.title}
                  </h3>
                  {item.url && (
                    <a 
                      href={item.url}
                      className="text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      <ArrowTopRightOnSquareIcon className="h-4 w-4" />
                    </a>
                  )}
                </div>
                
                <p className="text-sm text-gray-600 mb-2 line-clamp-3">
                  {item.summary}
                </p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${categoryColors[item.category]}`}>
                      {item.category}
                    </span>
                    <span className="text-xs text-gray-500">{item.source}</span>
                  </div>
                  <span className="text-xs text-gray-400">{item.timestamp}</span>
                </div>
              </div>
            </div>
          </article>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <button className="w-full text-sm text-casablanca-blue hover:text-blue-700 font-medium transition-colors">
          View all news →
        </button>
      </div>
    </div>
  )
} 