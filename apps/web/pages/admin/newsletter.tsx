import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import AdminLayout from '../../components/admin/AdminLayout'
import { useAuth } from '../../hooks/useAuth'
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

export default function AdminNewsletter() {
    const { user, loading } = useAuth()
    const router = useRouter()
    const [campaigns, setCampaigns] = useState<NewsletterCampaign[]>([])
    const [subscribers, setSubscribers] = useState<NewsletterSubscriber[]>([])
    const [stats, setStats] = useState({
        totalSubscribers: 0,
        activeSubscribers: 0,
        totalCampaigns: 0,
        averageOpenRate: 0
    })

    // Check if user is admin
    useEffect(() => {
        if (!loading && (!user || user.role !== 'admin')) {
            router.push('/')
        }
    }, [user, loading, router])

    useEffect(() => {
        // Fetch data from API
        const fetchData = async () => {
            try {
                // Fetch campaigns
                const campaignsResponse = await fetch('/api/admin/newsletter/campaigns')
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

            if (response.ok) {
                const data = await response.json()
                alert(`Newsletter generated successfully!\nSubject: ${data.subject}\nContent length: ${data.content.length} characters`)
            } else {
                alert('Failed to generate newsletter')
            }
        } catch (error) {
            console.error('Error generating newsletter:', error)
            alert('Error generating newsletter')
        }
    }

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-casablanca-blue"></div>
            </div>
        )
    }

    if (!user || user.role !== 'admin') {
        return null
    }

    return (
        <>
            <Head>
                <title>Newsletter Management - Admin Dashboard</title>
                <meta name="description" content="Manage newsletter campaigns and subscribers" />
            </Head>

            <AdminLayout>
                <div className="space-y-6">
                    {/* Header */}
                    <div className="flex justify-between items-center">
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">Newsletter Management</h1>
                            <p className="mt-1 text-sm text-gray-500">
                                Manage newsletter campaigns, subscribers, and AI-generated content
                            </p>
                        </div>
                        <div className="flex space-x-2">
                            <button
                                onClick={() => generateNewsletter('en')}
                                className="bg-casablanca-blue text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center"
                            >
                                <DocumentTextIcon className="h-4 w-4 mr-2" />
                                Generate EN
                            </button>
                            <button
                                onClick={() => generateNewsletter('fr')}
                                className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 flex items-center"
                            >
                                <DocumentTextIcon className="h-4 w-4 mr-2" />
                                Generate FR
                            </button>
                            <button
                                onClick={() => generateNewsletter('ar')}
                                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 flex items-center"
                            >
                                <DocumentTextIcon className="h-4 w-4 mr-2" />
                                Generate AR
                            </button>
                        </div>
                    </div>

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
                                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Actions
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
                                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                <div className="flex justify-end space-x-2">
                                                    <button className="text-blue-600 hover:text-blue-900">
                                                        <EyeIcon className="h-4 w-4" />
                                                    </button>
                                                    {campaign.status === 'draft' && (
                                                        <button className="text-green-600 hover:text-green-900">
                                                            <PlayIcon className="h-4 w-4" />
                                                        </button>
                                                    )}
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Subscribers */}
                    <div className="bg-white shadow rounded-lg">
                        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                            <h3 className="text-lg font-medium text-gray-900">Subscribers ({subscribers.length})</h3>
                            <button className="bg-gray-600 text-white px-3 py-1 rounded text-sm hover:bg-gray-700 flex items-center">
                                <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                                Export CSV
                            </button>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Email
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Status
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Subscribed
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Last Email
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Language
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {subscribers.map((subscriber) => (
                                        <tr key={subscriber.id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {subscriber.email}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${subscriber.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                                    }`}>
                                                    {subscriber.status}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {new Date(subscriber.subscribedAt).toLocaleDateString()}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {subscriber.lastEmailSent ? new Date(subscriber.lastEmailSent).toLocaleDateString() : 'Never'}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${subscriber.language === 'en' ? 'bg-blue-100 text-blue-800' :
                                                    subscriber.language === 'fr' ? 'bg-purple-100 text-purple-800' :
                                                        'bg-green-100 text-green-800'
                                                    }`}>
                                                    {subscriber.language.toUpperCase()}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </AdminLayout>
        </>
    )
} 