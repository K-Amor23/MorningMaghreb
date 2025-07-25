import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import AdminLayout from '../../components/admin/AdminLayout'
import DashboardOverview from '../../components/admin/DashboardOverview'
import { useAuth } from '../../hooks/useAuth'

export default function AdminDashboard() {
    const { user, loading } = useAuth()
    const router = useRouter()

    // Check if user is admin
    useEffect(() => {
        if (!loading && (!user || user.role !== 'admin')) {
            router.push('/')
        }
    }, [user, loading, router])

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
                <title>Admin Dashboard - Casablanca Insight</title>
                <meta name="description" content="Admin dashboard for Casablanca Insight" />
            </Head>

            <AdminLayout>
                <DashboardOverview />
            </AdminLayout>
        </>
    )
} 