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
        // For now, create a mock admin user
        // In production, this would check for JWT token and validate with backend
        const mockUser: User = {
            id: '1',
            email: 'admin@morningmaghreb.com',
            role: 'admin',
            name: 'Admin User'
        }

        setUser(mockUser)
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