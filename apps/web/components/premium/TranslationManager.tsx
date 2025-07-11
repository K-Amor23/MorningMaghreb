import React, { useState, useEffect } from 'react'
import { GlobeAltIcon, ArrowPathIcon, DocumentTextIcon, LanguageIcon } from '@heroicons/react/24/outline'
import { toast } from 'react-hot-toast'

interface Translation {
  id: string
  source_text: string
  source_language: string
  target_language: string
  translated_text: string
  status: 'pending' | 'completed' | 'failed'
  created_at: string
  word_count: number
}

interface TranslationRequest {
  text: string
  source_language: string
  target_language: string
  content_type: string
}

interface TranslationManagerProps {
  userSubscriptionTier: string
}

export default function TranslationManager({ userSubscriptionTier }: TranslationManagerProps) {
  const [translations, setTranslations] = useState<Translation[]>([])
  const [loading, setLoading] = useState(false)
  const [showTranslateForm, setShowTranslateForm] = useState(false)

  const [translationRequest, setTranslationRequest] = useState<TranslationRequest>({
    text: '',
    source_language: 'en',
    target_language: 'fr',
    content_type: 'report'
  })

  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'fr', name: 'French', flag: '🇫🇷' },
    { code: 'ar', name: 'Arabic', flag: '🇸🇦' },
    { code: 'es', name: 'Spanish', flag: '🇪🇸' },
    { code: 'de', name: 'German', flag: '🇩🇪' }
  ]

  const contentTypes = [
    { value: 'report', label: 'Financial Report', description: 'Company reports and analysis' },
    { value: 'summary', label: 'AI Summary', description: 'AI-generated content summaries' },
    { value: 'news', label: 'News Article', description: 'Financial news and updates' },
    { value: 'email', label: 'Email Content', description: 'Newsletter and email content' },
    { value: 'custom', label: 'Custom Text', description: 'Any other text content' }
  ]

  const sampleTexts = [
    {
      label: 'Financial Report Summary',
      text: 'Attijariwafa Bank reported strong Q3 2024 results with revenue growth of 12.5% year-over-year. Net income increased by 8.3% to MAD 2.1 billion, driven by improved operational efficiency and expanding market share in key segments.',
      type: 'report'
    },
    {
      label: 'Market Analysis',
      text: 'The Moroccan stock market showed resilience despite global economic uncertainties. The MASI index gained 2.3% this week, with banking and telecommunications sectors leading the gains.',
      type: 'summary'
    },
    {
      label: 'Economic Update',
      text: 'The Bank Al-Maghrib maintained its key policy rate at 3% during the latest monetary policy meeting, citing stable inflation expectations and moderate economic growth projections.',
      type: 'news'
    }
  ]

  useEffect(() => {
    if (userSubscriptionTier === 'pro' || userSubscriptionTier === 'institutional') {
      fetchTranslations()
    }
  }, [userSubscriptionTier])

  const fetchTranslations = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/translations', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setTranslations(data)
      } else {
        toast.error('Failed to fetch translations')
      }
    } catch (error) {
      console.error('Error fetching translations:', error)
      toast.error('Failed to fetch translations')
    } finally {
      setLoading(false)
    }
  }

  const translateText = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/translations/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        },
        body: JSON.stringify(translationRequest)
      })
      
      if (response.ok) {
        const translation = await response.json()
        setTranslations([translation, ...translations])
        setShowTranslateForm(false)
        setTranslationRequest({
          text: '',
          source_language: 'en',
          target_language: 'fr',
          content_type: 'report'
        })
        toast.success('Translation completed successfully')
      } else {
        toast.error('Failed to translate text')
      }
    } catch (error) {
      console.error('Error translating text:', error)
      toast.error('Failed to translate text')
    } finally {
      setLoading(false)
    }
  }

  const quickTranslate = async (text: string, sourceLang: string, targetLang: string) => {
    try {
      setLoading(true)
      const response = await fetch('/api/translations/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        },
        body: JSON.stringify({
          text,
          source_language: sourceLang,
          target_language: targetLang,
          content_type: 'custom'
        })
      })
      
      if (response.ok) {
        const translation = await response.json()
        setTranslations([translation, ...translations])
        toast.success('Quick translation completed')
      } else {
        toast.error('Failed to translate text')
      }
    } catch (error) {
      console.error('Error translating text:', error)
      toast.error('Failed to translate text')
    } finally {
      setLoading(false)
    }
  }

  const detectLanguage = async (text: string) => {
    try {
      const response = await fetch('/api/translations/detect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        },
        body: JSON.stringify({ text })
      })
      
      if (response.ok) {
        const result = await response.json()
        setTranslationRequest({
          ...translationRequest,
          source_language: result.detected_language
        })
        toast.success(`Detected language: ${result.detected_language.toUpperCase()}`)
      } else {
        toast.error('Failed to detect language')
      }
    } catch (error) {
      console.error('Error detecting language:', error)
      toast.error('Failed to detect language')
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getLanguageName = (code: string) => {
    const language = languages.find(lang => lang.code === code)
    return language ? `${language.flag} ${language.name}` : code.toUpperCase()
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100'
      case 'pending':
        return 'text-yellow-600 bg-yellow-100'
      case 'failed':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  if (userSubscriptionTier === 'free') {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <GlobeAltIcon className="h-5 w-5 text-yellow-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              Pro Tier Required
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>
                Multilingual features are available for Pro and Institutional tier subscribers. 
                Upgrade your subscription to access this feature.
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Multilingual Translation</h2>
          <p className="text-sm text-gray-600">
            AI-powered translation for financial content in multiple languages
          </p>
        </div>
        <button
          onClick={() => setShowTranslateForm(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <GlobeAltIcon className="h-4 w-4 mr-2" />
          Translate Text
        </button>
      </div>

      {/* Quick Translation Samples */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Translation Samples</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sampleTexts.map((sample, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">{sample.label}</h4>
              <p className="text-sm text-gray-600 mb-3 line-clamp-3">{sample.text}</p>
              <div className="flex space-x-2">
                <button
                  onClick={() => quickTranslate(sample.text, 'en', 'fr')}
                  className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200"
                >
                  🇫🇷 French
                </button>
                <button
                  onClick={() => quickTranslate(sample.text, 'en', 'ar')}
                  className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200"
                >
                  🇸🇦 Arabic
                </button>
                <button
                  onClick={() => quickTranslate(sample.text, 'en', 'es')}
                  className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded hover:bg-yellow-200"
                >
                  🇪🇸 Spanish
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Translation Form */}
      {showTranslateForm && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Translate Text</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Source Language
              </label>
              <select
                value={translationRequest.source_language}
                onChange={(e) => setTranslationRequest({...translationRequest, source_language: e.target.value})}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                {languages.map((language) => (
                  <option key={language.code} value={language.code}>
                    {language.flag} {language.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Target Language
              </label>
              <select
                value={translationRequest.target_language}
                onChange={(e) => setTranslationRequest({...translationRequest, target_language: e.target.value})}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                {languages.map((language) => (
                  <option key={language.code} value={language.code}>
                    {language.flag} {language.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Content Type
              </label>
              <select
                value={translationRequest.content_type}
                onChange={(e) => setTranslationRequest({...translationRequest, content_type: e.target.value})}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                {contentTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Text to Translate
              </label>
              <div className="mt-1 relative">
                <textarea
                  value={translationRequest.text}
                  onChange={(e) => setTranslationRequest({...translationRequest, text: e.target.value})}
                  rows={6}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="Enter text to translate..."
                />
                {translationRequest.text && (
                  <button
                    onClick={() => detectLanguage(translationRequest.text)}
                    className="absolute top-2 right-2 p-1 text-gray-400 hover:text-gray-600"
                    title="Detect language"
                  >
                    <LanguageIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
              <p className="mt-1 text-xs text-gray-500">
                {translationRequest.text.length} characters
              </p>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowTranslateForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </button>
              <button
                onClick={translateText}
                disabled={loading || !translationRequest.text}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Translating...' : 'Translate'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Translation History */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Translation History
          </h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Recent translations and their status
          </p>
        </div>
        <ul className="divide-y divide-gray-200">
          {translations.map((translation) => (
            <li key={translation.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3">
                      <GlobeAltIcon className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {getLanguageName(translation.source_language)} → {getLanguageName(translation.target_language)}
                        </p>
                        <p className="text-sm text-gray-500">
                          {translation.word_count} words • {formatDate(translation.created_at)}
                        </p>
                      </div>
                    </div>
                    <div className="mt-2">
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {translation.source_text}
                      </p>
                      {translation.status === 'completed' && (
                        <p className="text-sm text-gray-800 mt-1 line-clamp-2">
                          {translation.translated_text}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="ml-4 flex-shrink-0">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(translation.status)}`}>
                      {translation.status}
                    </span>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* Language Support Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-4">Supported Languages</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {languages.map((language) => (
            <div key={language.code} className="flex items-center space-x-2">
              <span className="text-lg">{language.flag}</span>
              <span className="text-sm font-medium text-blue-900">{language.name}</span>
            </div>
          ))}
        </div>
        <p className="mt-4 text-sm text-blue-700">
          AI-powered translation optimized for financial and business content. 
          Supports bidirectional translation between all supported languages.
        </p>
      </div>
    </div>
  )
} 