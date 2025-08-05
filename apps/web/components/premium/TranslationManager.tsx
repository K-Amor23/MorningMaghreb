import React, { useState, useEffect } from 'react'
import { LanguageIcon, PlusIcon, TrashIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import { useLocalStorageGetter } from '@/lib/useClientOnly'

interface Translation {
  id: string
  source_language: string
  target_language: string
  content: string
  translated_content: string
  status: 'pending' | 'completed' | 'failed'
  created_at: string
  completed_at?: string
}

export default function TranslationManager() {
  const [translations, setTranslations] = useState<Translation[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newTranslation, setNewTranslation] = useState({
    source_language: 'en',
    target_language: 'fr',
    content: ''
  })
  const [showTranslated, setShowTranslated] = useState<string | null>(null)
  const { getItem, mounted } = useLocalStorageGetter()

  const availableLanguages = [
    { code: 'en', name: 'English' },
    { code: 'fr', name: 'French' },
    { code: 'ar', name: 'Arabic' },
    { code: 'es', name: 'Spanish' },
    { code: 'de', name: 'German' },
    { code: 'zh', name: 'Chinese' }
  ]

  useEffect(() => {
    if (mounted) {
      fetchTranslations()
    }
  }, [mounted])

  const fetchTranslations = async () => {
    try {
      const token = getItem('supabase.auth.token')
      const response = await fetch('/api/premium/translations', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setTranslations(data.translations || [])
      }
    } catch (error) {
      console.error('Error fetching translations:', error)
    } finally {
      setLoading(false)
    }
  }

  const createTranslation = async () => {
    if (!newTranslation.content.trim()) return

    try {
      const token = getItem('supabase.auth.token')
      const response = await fetch('/api/premium/translations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newTranslation)
      })

      if (response.ok) {
        const data = await response.json()
        setTranslations(prev => [...prev, data.translation])
        setShowCreateForm(false)
        setNewTranslation({ source_language: 'en', target_language: 'fr', content: '' })
      }
    } catch (error) {
      console.error('Error creating translation:', error)
    }
  }

  const deleteTranslation = async (translationId: string) => {
    if (!confirm('Are you sure you want to delete this translation?')) return

    try {
      const token = getItem('supabase.auth.token')
      const response = await fetch(`/api/premium/translations/${translationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        setTranslations(prev => prev.filter(translation => translation.id !== translationId))
      }
    } catch (error) {
      console.error('Error deleting translation:', error)
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
    return availableLanguages.find(lang => lang.code === code)?.name || code
  }

  if (!mounted) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-6"></div>
          <div className="space-y-3">
            <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Translation Manager
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Manage multilingual content and translations
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
        >
          <PlusIcon className="h-4 w-4" />
          <span>New Translation</span>
        </button>
      </div>

      {showCreateForm && (
        <div className="mb-6 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Create New Translation
          </h3>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Source Language
                </label>
                <select
                  value={newTranslation.source_language}
                  onChange={(e) => setNewTranslation(prev => ({ ...prev, source_language: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  {availableLanguages.map(lang => (
                    <option key={lang.code} value={lang.code}>
                      {lang.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Target Language
                </label>
                <select
                  value={newTranslation.target_language}
                  onChange={(e) => setNewTranslation(prev => ({ ...prev, target_language: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  {availableLanguages.map(lang => (
                    <option key={lang.code} value={lang.code}>
                      {lang.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Content to Translate
              </label>
              <textarea
                value={newTranslation.content}
                onChange={(e) => setNewTranslation(prev => ({ ...prev, content: e.target.value }))}
                placeholder="Enter the text you want to translate..."
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div className="flex space-x-3">
              <button
                onClick={createTranslation}
                disabled={!newTranslation.content.trim()}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
              >
                Create Translation
              </button>
              <button
                onClick={() => {
                  setShowCreateForm(false)
                  setNewTranslation({ source_language: 'en', target_language: 'fr', content: '' })
                }}
                className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="animate-pulse">
              <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {translations.length === 0 ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <LanguageIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No translations created yet</p>
              <p className="text-sm mt-1">Create your first translation to get started</p>
            </div>
          ) : (
            translations.map(translation => (
              <div key={translation.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="font-medium text-gray-900 dark:text-white">
                        {getLanguageName(translation.source_language)} → {getLanguageName(translation.target_language)}
                      </h3>
                      <span className={`px-2 py-1 text-xs rounded-full ${translation.status === 'completed'
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : translation.status === 'failed'
                          ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                          : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                        }`}>
                        {translation.status}
                      </span>
                    </div>

                    <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      {translation.content.substring(0, 100)}...
                    </div>

                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Created: {formatDate(translation.created_at)}
                      {translation.completed_at && ` • Completed: ${formatDate(translation.completed_at)}`}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    {translation.translated_content && (
                      <button
                        onClick={() => setShowTranslated(showTranslated === translation.id ? null : translation.id)}
                        className="text-blue-600 hover:text-blue-800 dark:text-blue-400"
                      >
                        {showTranslated === translation.id ? (
                          <EyeSlashIcon className="h-4 w-4" />
                        ) : (
                          <EyeIcon className="h-4 w-4" />
                        )}
                      </button>
                    )}
                    <button
                      onClick={() => deleteTranslation(translation.id)}
                      className="text-red-600 hover:text-red-800 dark:text-red-400"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {showTranslated === translation.id && translation.translated_content && (
                  <div className="mt-2 p-2 bg-gray-100 dark:bg-gray-700 rounded text-sm">
                    {translation.translated_content}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
} 