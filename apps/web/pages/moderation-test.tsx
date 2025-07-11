import { useState } from 'react'
import Head from 'next/head'
import { 
  ShieldCheckIcon, 
  ExclamationTriangleIcon,
  XCircleIcon,
  CheckCircleIcon,
  InformationCircleIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'

interface ModerationResponse {
  is_safe: boolean
  moderation_level: string
  moderated_text?: string
  sensitive_topics: string[]
  confidence_score: number
  flagged_phrases: string[]
  suggestions: string[]
  can_proceed: boolean
}

const contentTypes = [
  { value: 'market_summary', label: 'Market Summary' },
  { value: 'company_analysis', label: 'Company Analysis' },
  { value: 'news_digest', label: 'News Digest' },
  { value: 'report_summary', label: 'Report Summary' },
  { value: 'sentiment_analysis', label: 'Sentiment Analysis' }
]

const sampleTexts = [
  {
    name: "Safe Market Summary",
    text: "The MASI index closed at 12,450 points today, up 1.2% from yesterday. Trading volume was strong at 2.3 billion MAD. The banking sector led gains with Attijariwafa Bank rising 2.1%.",
    type: "market_summary"
  },
  {
    name: "Sensitive Content (Monarchy)",
    text: "The king's economic policies have influenced market performance. The royal family's investments in the banking sector show strong returns.",
    type: "market_summary"
  },
  {
    name: "Sensitive Content (Government)",
    text: "The government's new fiscal policy is affecting market sentiment. The Prime Minister's announcement caused volatility in the stock market.",
    type: "news_digest"
  },
  {
    name: "Sensitive Content (Religion)",
    text: "Islamic banking principles are driving growth in the financial sector. Halal investment products are gaining popularity among Muslim investors.",
    type: "company_analysis"
  },
  {
    name: "Mixed Sensitive Content",
    text: "The king's government announced new economic policies. The Prime Minister's Islamic banking initiatives are supported by the royal family.",
    type: "news_digest"
  }
]

export default function ModerationTest() {
  const [selectedContentType, setSelectedContentType] = useState('market_summary')
  const [inputText, setInputText] = useState('')
  const [moderationResult, setModerationResult] = useState<ModerationResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [selectedSample, setSelectedSample] = useState('')

  const testModeration = async () => {
    if (!inputText.trim()) return
    
    setLoading(true)
    try {
      const response = await fetch('/api/moderation/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          content_type: selectedContentType
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setModerationResult(data.moderation_result)
      } else {
        console.error('Moderation test failed')
      }
    } catch (error) {
      console.error('Error testing moderation:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadSampleText = (sample: typeof sampleTexts[0]) => {
    setInputText(sample.text)
    setSelectedContentType(sample.type)
    setSelectedSample(sample.name)
  }

  const getModerationLevelColor = (level: string) => {
    switch (level) {
      case 'safe':
        return 'text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-200'
      case 'flagged':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-200'
      case 'requires_review':
        return 'text-orange-600 bg-orange-100 dark:bg-orange-900 dark:text-orange-200'
      case 'blocked':
        return 'text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-200'
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-900 dark:text-gray-200'
    }
  }

  const getModerationIcon = (level: string) => {
    switch (level) {
      case 'safe':
        return <CheckCircleIcon className="h-6 w-6 text-green-600" />
      case 'flagged':
        return <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600" />
      case 'requires_review':
        return <ExclamationTriangleIcon className="h-6 w-6 text-orange-600" />
      case 'blocked':
        return <XCircleIcon className="h-6 w-6 text-red-600" />
      default:
        return <InformationCircleIcon className="h-6 w-6 text-gray-600" />
    }
  }

  return (
    <>
      <Head>
        <title>AI Moderation Test | Casablanca Insights</title>
        <meta name="description" content="Test the AI content moderation system with Moroccan cultural guardrails." />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center mb-4">
              <ShieldCheckIcon className="h-12 w-12 text-blue-600 mr-4" />
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
                AI Content Moderation Test
              </h1>
            </div>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Test the AI moderation system with Moroccan cultural sensitivity guardrails
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Input Section */}
            <div className="space-y-6">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                  Test Content
                </h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Content Type
                    </label>
                    <select
                      value={selectedContentType}
                      onChange={(e) => setSelectedContentType(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    >
                      {contentTypes.map(type => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Content Text
                    </label>
                    <textarea
                      value={inputText}
                      onChange={(e) => setInputText(e.target.value)}
                      rows={8}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                      placeholder="Enter text to test for cultural sensitivity..."
                    />
                  </div>
                  
                  <button
                    onClick={testModeration}
                    disabled={loading || !inputText.trim()}
                    className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-md transition-colors"
                  >
                    {loading ? 'Testing...' : 'Test Moderation'}
                  </button>
                </div>
              </div>

              {/* Sample Texts */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Sample Texts
                </h3>
                <div className="space-y-2">
                  {sampleTexts.map((sample, index) => (
                    <button
                      key={index}
                      onClick={() => loadSampleText(sample)}
                      className={`w-full text-left p-3 rounded-md border transition-colors ${
                        selectedSample === sample.name
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                      }`}
                    >
                      <div className="font-medium text-gray-900 dark:text-white">
                        {sample.name}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                        {sample.text.substring(0, 80)}...
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Results Section */}
            <div className="space-y-6">
              {moderationResult && (
                <>
                  {/* Moderation Level */}
                  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                        Moderation Result
                      </h2>
                      {getModerationIcon(moderationResult.moderation_level)}
                    </div>
                    
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-700 dark:text-gray-300">Status:</span>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getModerationLevelColor(moderationResult.moderation_level)}`}>
                          {moderationResult.moderation_level.toUpperCase()}
                        </span>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-gray-700 dark:text-gray-300">Safe to Proceed:</span>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          moderationResult.can_proceed 
                            ? 'text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-200'
                            : 'text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-200'
                        }`}>
                          {moderationResult.can_proceed ? 'YES' : 'NO'}
                        </span>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-gray-700 dark:text-gray-300">Confidence:</span>
                        <span className="text-gray-900 dark:text-white font-medium">
                          {(moderationResult.confidence_score * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Sensitive Topics */}
                  {moderationResult.sensitive_topics.length > 0 && (
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                        Sensitive Topics Detected
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {moderationResult.sensitive_topics.map((topic, index) => (
                          <span
                            key={index}
                            className="px-3 py-1 bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded-full text-sm font-medium"
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Flagged Phrases */}
                  {moderationResult.flagged_phrases.length > 0 && (
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                        Flagged Phrases
                      </h3>
                      <div className="space-y-2">
                        {moderationResult.flagged_phrases.map((phrase, index) => (
                          <div
                            key={index}
                            className="p-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-md"
                          >
                            <span className="text-yellow-800 dark:text-yellow-200 font-medium">
                              "{phrase}"
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Suggestions */}
                  {moderationResult.suggestions.length > 0 && (
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                        Suggestions
                      </h3>
                      <ul className="space-y-2">
                        {moderationResult.suggestions.map((suggestion, index) => (
                          <li
                            key={index}
                            className="flex items-start"
                          >
                            <InformationCircleIcon className="h-5 w-5 text-blue-500 mt-0.5 mr-2 flex-shrink-0" />
                            <span className="text-gray-700 dark:text-gray-300">
                              {suggestion}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Moderated Text */}
                  {moderationResult.moderated_text && (
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                        Safe Version
                      </h3>
                      <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-md">
                        <p className="text-gray-800 dark:text-gray-200 leading-relaxed">
                          {moderationResult.moderated_text}
                        </p>
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* Guidelines Info */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Cultural Guidelines
                </h3>
                <div className="space-y-3 text-sm text-gray-600 dark:text-gray-300">
                  <p>• Avoid references to monarchy, royal family, or royal institutions</p>
                  <p>• Focus on business aspects rather than government activities</p>
                  <p>• Keep content secular and business-focused</p>
                  <p>• Avoid political commentary or analysis</p>
                  <p>• Use neutral, factual, and professional tone</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
} 