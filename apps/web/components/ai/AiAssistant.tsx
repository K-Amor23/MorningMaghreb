import { useState, useRef, useEffect } from 'react'
import { PaperAirplaneIcon, SparklesIcon, ArrowPathIcon } from '@heroicons/react/24/outline'

interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
    timestamp: Date
    isLoading?: boolean
}

interface AiAssistantProps {
    portfolioId?: string
    selectedTickers?: string[]
    onPortfolioAnalysis?: (analysis: any) => void
}

export default function AiAssistant({
    portfolioId,
    selectedTickers,
    onPortfolioAnalysis
}: AiAssistantProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            role: 'assistant',
            content: "Hello! I'm your AI financial assistant. I can help you analyze companies, compare stocks, assess portfolio risk, and provide market insights. What would you like to know?",
            timestamp: new Date()
        }
    ])
    const [inputValue, setInputValue] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!inputValue.trim() || isLoading) return

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: inputValue,
            timestamp: new Date()
        }

        setMessages(prev => [...prev, userMessage])
        setInputValue('')
        setIsLoading(true)

        // Add loading message
        const loadingMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: '',
            timestamp: new Date(),
            isLoading: true
        }
        setMessages(prev => [...prev, loadingMessage])

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
                },
                body: JSON.stringify({
                    messages: [
                        ...messages.map(m => ({ role: m.role, content: m.content })),
                        { role: 'user', content: inputValue }
                    ],
                    context: {
                        portfolio_id: portfolioId,
                        tickers: selectedTickers,
                        portfolio_analysis: portfolioId ? true : false
                    }
                })
            })

            if (!response.ok) {
                throw new Error('Failed to get AI response')
            }

            const data = await response.json()

            // Remove loading message and add real response
            setMessages(prev => {
                const filtered = prev.filter(m => !m.isLoading)
                return [...filtered, {
                    id: Date.now().toString(),
                    role: 'assistant',
                    content: data.response,
                    timestamp: new Date()
                }]
            })

            // If this was a portfolio analysis request, trigger the callback
            if (portfolioId && inputValue.toLowerCase().includes('portfolio')) {
                try {
                    const portfolioResponse = await fetch('/api/ai/portfolio-analysis', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
                        },
                        body: JSON.stringify({ portfolio_id: portfolioId })
                    })

                    if (portfolioResponse.ok) {
                        const portfolioData = await portfolioResponse.json()
                        onPortfolioAnalysis?.(portfolioData)
                    }
                } catch (error) {
                    console.error('Portfolio analysis failed:', error)
                }
            }

        } catch (error) {
            console.error('AI Assistant error:', error)
            setMessages(prev => {
                const filtered = prev.filter(m => !m.isLoading)
                return [...filtered, {
                    id: Date.now().toString(),
                    role: 'assistant',
                    content: "I'm sorry, I encountered an error. Please try again or contact support if the issue persists.",
                    timestamp: new Date()
                }]
            })
        } finally {
            setIsLoading(false)
        }
    }

    const suggestedQuestions = [
        "Explain ATW's recent performance",
        "Compare BMCE vs Attijari",
        "Show me risk drivers for my portfolio",
        "What's the outlook for banking stocks?",
        "Analyze my portfolio diversification"
    ]

    const handleSuggestedQuestion = (question: string) => {
        setInputValue(question)
    }

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg h-96 flex flex-col">
            <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center space-x-2">
                    <SparklesIcon className="h-5 w-5 text-blue-500" />
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        AI Assistant
                    </h3>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${message.role === 'user'
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                                }`}
                        >
                            {message.isLoading ? (
                                <div className="flex items-center space-x-2">
                                    <ArrowPathIcon className="h-4 w-4 animate-spin" />
                                    <span>Thinking...</span>
                                </div>
                            ) : (
                                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                            )}
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            {messages.length === 1 && (
                <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700">
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                        Try asking:
                    </p>
                    <div className="flex flex-wrap gap-2">
                        {suggestedQuestions.map((question, index) => (
                            <button
                                key={index}
                                onClick={() => handleSuggestedQuestion(question)}
                                className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-3 py-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                            >
                                {question}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex space-x-2">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder="Ask about companies, portfolio analysis, or market insights..."
                        className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        disabled={!inputValue.trim() || isLoading}
                        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1"
                    >
                        <PaperAirplaneIcon className="h-4 w-4" />
                    </button>
                </div>
            </form>
        </div>
    )
} 