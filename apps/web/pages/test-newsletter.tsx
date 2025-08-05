import { useState } from 'react'
import Head from 'next/head'

export default function TestNewsletter() {
    const [generating, setGenerating] = useState<string | null>(null)
    const [result, setResult] = useState<string>('')

    const generateNewsletter = async (language: string) => {
        try {
            console.log('Generating newsletter for language:', language)
            setGenerating(language)
            setResult('')

            const response = await fetch('/api/newsletter/weekly-recap/preview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    include_macro: true,
                    include_sectors: true,
                    include_top_movers: true,
                    language
                })
            })

            console.log('Generate response status:', response.status)

            if (response.ok) {
                const data = await response.json()
                console.log('Generated newsletter data:', data)
                setResult(`✅ Newsletter generated successfully!\nSubject: ${data.subject}\nContent length: ${data.content.length} characters\n\nContent preview:\n${data.content.substring(0, 200)}...`)
            } else {
                const errorData = await response.text()
                console.error('Failed to generate newsletter:', errorData)
                setResult(`❌ Failed to generate newsletter: ${errorData}`)
            }
        } catch (error) {
            console.error('Error generating newsletter:', error)
            setResult(`❌ Error generating newsletter: ${error}`)
        } finally {
            setGenerating(null)
        }
    }

    return (
        <>
            <Head>
                <title>Test Newsletter Generation</title>
            </Head>

            <div className="min-h-screen bg-gray-50 p-8">
                <div className="max-w-4xl mx-auto">
                    <h1 className="text-3xl font-bold text-gray-900 mb-8">Test Newsletter Generation</h1>

                    <div className="bg-white rounded-lg shadow p-6 mb-8">
                        <h2 className="text-xl font-semibold mb-4">Generate Newsletter</h2>

                        <div className="flex space-x-4 mb-6">
                            <button
                                onClick={() => generateNewsletter('en')}
                                disabled={generating === 'en'}
                                className={`px-6 py-3 rounded-md font-medium ${generating === 'en'
                                        ? 'bg-gray-400 cursor-not-allowed'
                                        : 'bg-blue-600 hover:bg-blue-700'
                                    } text-white`}
                            >
                                {generating === 'en' ? 'Generating...' : 'Generate EN'}
                            </button>

                            <button
                                onClick={() => generateNewsletter('fr')}
                                disabled={generating === 'fr'}
                                className={`px-6 py-3 rounded-md font-medium ${generating === 'fr'
                                        ? 'bg-gray-400 cursor-not-allowed'
                                        : 'bg-purple-600 hover:bg-purple-700'
                                    } text-white`}
                            >
                                {generating === 'fr' ? 'Generating...' : 'Generate FR'}
                            </button>

                            <button
                                onClick={() => generateNewsletter('ar')}
                                disabled={generating === 'ar'}
                                className={`px-6 py-3 rounded-md font-medium ${generating === 'ar'
                                        ? 'bg-gray-400 cursor-not-allowed'
                                        : 'bg-green-600 hover:bg-green-700'
                                    } text-white`}
                            >
                                {generating === 'ar' ? 'Generating...' : 'Generate AR'}
                            </button>
                        </div>

                        {result && (
                            <div className="mt-6">
                                <h3 className="text-lg font-medium mb-2">Result:</h3>
                                <pre className="bg-gray-100 p-4 rounded-md text-sm overflow-auto max-h-96">
                                    {result}
                                </pre>
                            </div>
                        )}
                    </div>

                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-xl font-semibold mb-4">Test API Endpoints</h2>

                        <div className="space-y-4">
                            <div>
                                <button
                                    onClick={async () => {
                                        try {
                                            const response = await fetch('/api/admin/newsletter/campaigns')
                                            const data = await response.json()
                                            setResult(`✅ Campaigns API: ${JSON.stringify(data, null, 2)}`)
                                        } catch (error) {
                                            setResult(`❌ Campaigns API Error: ${error}`)
                                        }
                                    }}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                                >
                                    Test Campaigns API
                                </button>
                            </div>

                            <div>
                                <button
                                    onClick={async () => {
                                        try {
                                            const response = await fetch('/api/admin/newsletter/subscribers')
                                            const data = await response.json()
                                            setResult(`✅ Subscribers API: ${JSON.stringify(data, null, 2)}`)
                                        } catch (error) {
                                            setResult(`❌ Subscribers API Error: ${error}`)
                                        }
                                    }}
                                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                                >
                                    Test Subscribers API
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
} 