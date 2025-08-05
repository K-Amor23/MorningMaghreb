import { useState, useEffect } from 'react'
import Head from 'next/head'
import {
    EnvelopeIcon,
    DocumentTextIcon,
    ChartBarIcon,
    ArrowDownTrayIcon,
    PlayIcon,
    EyeIcon
} from '@heroicons/react/24/outline'

interface NewsletterCampaign {
    id: string
    subject: string
    status: 'draft' | 'scheduled' | 'sent'
    recipientCount: number
    openRate: number
    clickRate: number
    sentAt?: string
    scheduledFor?: string
    language: 'en' | 'fr' | 'ar'
}

interface NewsletterSubscriber {
    id: string
    email: string
    status: 'active' | 'unsubscribed'
    subscribedAt: string
    lastEmailSent?: string
    language: 'en' | 'fr' | 'ar'
}

export default function AdminNewsletterSimple() {
    const [campaigns, setCampaigns] = useState<NewsletterCampaign[]>([])
    const [subscribers, setSubscribers] = useState<NewsletterSubscriber[]>([])
    const [stats, setStats] = useState({
        totalSubscribers: 0,
        activeSubscribers: 0,
        totalCampaigns: 0,
        averageOpenRate: 0
    })
    const [generating, setGenerating] = useState<string | null>(null)
    const [result, setResult] = useState<string>('')

    useEffect(() => {
        // Fetch data from API
        const fetchData = async () => {
            try {
                console.log('Fetching newsletter data...')

                // Fetch campaigns
                const campaignsResponse = await fetch('/api/admin/newsletter/campaigns')
                console.log('Campaigns response:', campaignsResponse.status)
                if (campaignsResponse.ok) {
                    const campaignsData = await campaignsResponse.json()
                    const apiCampaigns: NewsletterCampaign[] = campaignsData.campaigns.map((c: any) => ({
                        id: c.id,
                        subject: c.subject,
                        status: c.status,
                        recipientCount: c.recipientCount,
                        openRate: c.openRate,
                        clickRate: c.clickRate,
                        sentAt: c.sentAt,
                        scheduledFor: c.scheduledFor,
                        language: c.language
                    }))
                    setCampaigns(apiCampaigns)
                }

                // Fetch subscribers
                const subscribersResponse = await fetch('/api/admin/newsletter/subscribers')
                console.log('Subscribers response:', subscribersResponse.status)
                if (subscribersResponse.ok) {
                    const subscribersData = await subscribersResponse.json()
                    const apiSubscribers: NewsletterSubscriber[] = subscribersData.subscribers.map((s: any) => ({
                        id: s.id,
                        email: s.email,
                        status: s.status,
                        subscribedAt: s.subscribedAt,
                        lastEmailSent: s.lastEmailSent,
                        language: s.language
                    }))
                    setSubscribers(apiSubscribers)
                }

                // Calculate stats
                const campaignsData = await campaignsResponse.json()
                const subscribersData = await subscribersResponse.json()
                setStats({
                    totalSubscribers: subscribersData.total,
                    activeSubscribers: subscribersData.active,
                    totalCampaigns: campaignsData.total,
                    averageOpenRate: campaignsData.campaigns.filter((c: any) => c.status === 'sent').reduce((acc: any, c: any) => acc + c.openRate, 0) / campaignsData.campaigns.filter((c: any) => c.status === 'sent').length || 0
                })
            } catch (error) {
                console.error('Error fetching newsletter data:', error)
            }
        }

        fetchData()
    }, [])

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
                setResult(`✅ Newsletter generated successfully!\nSubject: ${data.subject}\nContent length: ${data.content.length} characters\n\nContent preview:\n${data.content.substring(0, 300)}...`)
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
                <title>Newsletter Management - Admin Dashboard</title>
                <meta name="description" content="Manage newsletter campaigns and subscribers" />
            </Head>

            <div className="min-h-screen bg-gray-50">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
                    <div className="space-y-6">
                        {/* Header */}
                        <div className="flex justify-between items-center">
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">Newsletter Management (Simple)</h1>
                                <p className="mt-1 text-sm text-gray-500">
                                    Manage newsletter campaigns, subscribers, and AI-generated content
                                </p>
                            </div>
                            <div className="flex space-x-2">
                                <button
                                    onClick={() => generateNewsletter('en')}
                                    disabled={generating === 'en'}
                                    className={`px-4 py-2 rounded-md flex items-center ${generating === 'en'
                                            ? 'bg-gray-400 cursor-not-allowed'
                                            : 'bg-blue-600 hover:bg-blue-700'
                                        } text-white`}
                                >
                                    <DocumentTextIcon className="h-4 w-4 mr-2" />
                                    {generating === 'en' ? 'Generating...' : 'Generate EN'}
                                </button>
                                <button
                                    onClick={() => generateNewsletter('fr')}
                                    disabled={generating === 'fr'}
                                    className={`px-4 py-2 rounded-md flex items-center ${generating === 'fr'
                                            ? 'bg-gray-400 cursor-not-allowed'
                                            : 'bg-purple-600 hover:bg-purple-700'
                                        } text-white`}
                                >
                                    <DocumentTextIcon className="h-4 w-4 mr-2" />
                                    {generating === 'fr' ? 'Generating...' : 'Generate FR'}
                                </button>
                                <button
                                    onClick={() => generateNewsletter('ar')}
                                    disabled={generating === 'ar'}
                                    className={`px-4 py-2 rounded-md flex items-center ${generating === 'ar'
                                            ? 'bg-gray-400 cursor-not-allowed'
                                            : 'bg-green-600 hover:bg-green-700'
                                        } text-white`}
                                >
                                    <DocumentTextIcon className="h-4 w-4 mr-2" />
                                    {generating === 'ar' ? 'Generating...' : 'Generate AR'}
                                </button>
                            </div>
                        </div>

                        {/* Result Display */}
                        {result && (
                            <div className="bg-white rounded-lg shadow p-6">
                                <h3 className="text-lg font-medium mb-4">Generation Result:</h3>
                                <pre className="bg-gray-100 p-4 rounded-md text-sm overflow-auto max-h-96 whitespace-pre-wrap">
                                    {result}
                                </pre>
                            </div>
                        )}

                        {/* Stats Cards */}
                        <div className="grid grid-cols-1 gap-5 sm:grid-cols-4">
                            <div className="bg-white overflow-hidden shadow rounded-lg">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                                                <EnvelopeIcon className="w-5 h-5 text-white" />
                                            </div>
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">Total Subscribers</dt>
                                                <dd className="text-lg font-medium text-gray-900">{stats.totalSubscribers}</dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="bg-white overflow-hidden shadow rounded-lg">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                                                <EnvelopeIcon className="w-5 h-5 text-white" />
                                            </div>
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">Active Subscribers</dt>
                                                <dd className="text-lg font-medium text-gray-900">{stats.activeSubscribers}</dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="bg-white overflow-hidden shadow rounded-lg">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                                                <DocumentTextIcon className="w-5 h-5 text-white" />
                                            </div>
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">Total Campaigns</dt>
                                                <dd className="text-lg font-medium text-gray-900">{stats.totalCampaigns}</dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="bg-white overflow-hidden shadow rounded-lg">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <div className="w-8 h-8 bg-orange-500 rounded-md flex items-center justify-center">
                                                <ChartBarIcon className="w-5 h-5 text-white" />
                                            </div>
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">Avg Open Rate</dt>
                                                <dd className="text-lg font-medium text-gray-900">{stats.averageOpenRate.toFixed(1)}%</dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Campaigns */}
                        <div className="bg-white shadow rounded-lg">
                            <div className="px-6 py-4 border-b border-gray-200">
                                <h3 className="text-lg font-medium text-gray-900">Recent Campaigns</h3>
                            </div>
                            <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Campaign
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Status
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Recipients
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Open Rate
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Click Rate
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Language
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {campaigns.map((campaign) => (
                                            <tr key={campaign.id} className="hover:bg-gray-50">
                                                <td className="px-6 py-4">
                                                    <div>
                                                        <div className="text-sm font-medium text-gray-900">{campaign.subject}</div>
                                                        <div className="text-sm text-gray-500">
                                                            {campaign.sentAt ? `Sent: ${new Date(campaign.sentAt).toLocaleDateString()}` :
                                                                campaign.scheduledFor ? `Scheduled: ${new Date(campaign.scheduledFor).toLocaleDateString()}` :
                                                                    'Draft'}
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${campaign.status === 'sent' ? 'bg-green-100 text-green-800' :
                                                        campaign.status === 'scheduled' ? 'bg-yellow-100 text-yellow-800' :
                                                            'bg-gray-100 text-gray-800'
                                                        }`}>
                                                        {campaign.status}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                    {campaign.recipientCount.toLocaleString()}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                    {campaign.openRate > 0 ? `${campaign.openRate}%` : '-'}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                    {campaign.clickRate > 0 ? `${campaign.clickRate}%` : '-'}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${campaign.language === 'en' ? 'bg-blue-100 text-blue-800' :
                                                        campaign.language === 'fr' ? 'bg-purple-100 text-purple-800' :
                                                            'bg-green-100 text-green-800'
                                                        }`}>
                                                        {campaign.language.toUpperCase()}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
} 