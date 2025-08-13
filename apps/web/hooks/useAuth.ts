import { useState, useEffect } from 'react'

interface User {
    id: string
    email: string
    role: 'user' | 'admin'
    name?: string
}

export function useAuth() {
    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const env = process.env.NEXT_PUBLIC_ENV || 'production'

        // In development, keep the old behavior for local testing only
        if (env === 'development') {
            const mockUser: User = {
                id: '1',
                email: 'admin@morningmaghreb.com',
                role: 'admin',
                name: 'Admin User'
            }
            setUser(mockUser)
            setLoading(false)
            return
        }

        // In non-development, derive role from the lightweight cookie set by auth flow/middleware
        if (typeof document !== 'undefined') {
            const cookie = document.cookie || ''
            const match = cookie.split('; ').find((c) => c.startsWith('mm_tier='))
            const tier = match ? match.split('=')[1] : ''

            if (tier === 'admin') {
                setUser({ id: 'cookie-user', email: '', role: 'admin', name: 'Admin' })
            } else {
                setUser(null)
            }
        }

        setLoading(false)
    }, [])

    const login = async (email: string, password: string) => {
        // Mock login - replace with actual authentication
        if (email === 'admin@morningmaghreb.com' && password === 'admin123') {
            const user: User = {
                id: '1',
                email,
                role: 'admin',
                name: 'Admin User'
            }
            setUser(user)
            return { success: true }
        }
        return { success: false, error: 'Invalid credentials' }
    }

    const logout = () => {
        setUser(null)
    }

    return {
        user,
        loading,
        login,
        logout
    }
} 