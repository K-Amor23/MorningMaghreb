import { jwtDecode } from 'jwt-decode'

export interface User {
    id: string
    email: string
    full_name: string
    tier: 'free' | 'pro' | 'admin'
    status: 'active' | 'inactive' | 'suspended'
    language_preference: string
    newsletter_frequency: string
    preferences: Record<string, any>
    stripe_customer_id?: string
    stripe_subscription_id?: string
    created_at: string
    updated_at: string
}

export interface AuthResponse {
    user: User
    access_token: string
    refresh_token: string
    token_type: string
    expires_in: number
}

export interface LoginCredentials {
    email: string
    password: string
}

export interface RegisterData {
    email: string
    password: string
    full_name: string
    language_preference?: string
}

export interface ProfileUpdate {
    full_name?: string
    language_preference?: string
    newsletter_frequency?: string
    preferences?: Record<string, any>
}

class AuthService {
    private baseUrl: string
    private accessToken: string | null = null
    private refreshToken: string | null = null

    constructor() {
        this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        this.loadTokens()
    }

    private loadTokens() {
        if (typeof window !== 'undefined') {
            this.accessToken = localStorage.getItem('access_token')
            this.refreshToken = localStorage.getItem('refresh_token')
        }
    }

    private saveTokens(accessToken: string, refreshToken: string) {
        if (typeof window !== 'undefined') {
            localStorage.setItem('access_token', accessToken)
            localStorage.setItem('refresh_token', refreshToken)
            this.accessToken = accessToken
            this.refreshToken = refreshToken
        }
    }

    private clearTokens() {
        if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            this.accessToken = null
            this.refreshToken = null
        }
    }

    private async makeRequest(endpoint: string, options: RequestInit = {}) {
        const url = `${this.baseUrl}${endpoint}`

        const config: RequestInit = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        }

        // Add auth header if token exists
        if (this.accessToken) {
            config.headers = {
                ...config.headers,
                'Authorization': `Bearer ${this.accessToken}`,
            }
        }

        const response = await fetch(url, config)

        if (response.status === 401 && this.refreshToken) {
            // Try to refresh token
            const refreshed = await this.refreshAccessToken()
            if (refreshed) {
                // Retry the original request
                if (this.accessToken) {
                    config.headers = {
                        ...config.headers,
                        'Authorization': `Bearer ${this.accessToken}`,
                    }
                }
                const retryResponse = await fetch(url, config)
                return retryResponse
            }
        }

        return response
    }

    async register(data: RegisterData): Promise<AuthResponse> {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.error || 'Registration failed')
        }

        const authData = await response.json()
        this.saveTokens(authData.access_token, authData.refresh_token)
        return authData
    }

    async login(credentials: LoginCredentials): Promise<AuthResponse> {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(credentials),
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.error || 'Login failed')
        }

        const authData = await response.json()
        this.saveTokens(authData.access_token, authData.refresh_token)
        // Set a lightweight cookie for middleware checks (not security-critical)
        if (typeof document !== 'undefined') {
            try {
                const profileResp = await fetch('/api/auth/profile')
                if (profileResp.ok) {
                    const user = (await profileResp.json()) as User
                    document.cookie = `mm_tier=${user.tier}; Path=/; SameSite=Lax`;
                }
            } catch {}
        }
        return authData
    }

    async logout(): Promise<void> {
        if (this.accessToken) {
            try {
                await this.makeRequest('/api/auth/logout', {
                    method: 'POST',
                })
            } catch (error) {
                console.error('Logout error:', error)
            }
        }
        this.clearTokens()
        if (typeof document !== 'undefined') {
            document.cookie = 'mm_tier=; Max-Age=0; Path=/; SameSite=Lax'
        }
    }

    async getProfile(): Promise<User> {
        const response = await this.makeRequest('/api/auth/profile')

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Failed to get profile')
        }

        return response.json()
    }

    async updateProfile(data: ProfileUpdate): Promise<User> {
        const response = await this.makeRequest('/api/auth/profile', {
            method: 'PUT',
            body: JSON.stringify(data),
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Failed to update profile')
        }

        return response.json()
    }

    async checkAuthStatus(): Promise<{ is_authenticated: boolean; user?: User }> {
        const response = await this.makeRequest('/api/auth/status')

        if (!response.ok) {
            return { is_authenticated: false }
        }

        return response.json()
    }

    async refreshAccessToken(): Promise<boolean> {
        if (!this.refreshToken) {
            return false
        }

        try {
            const response = await fetch(`${this.baseUrl}/api/auth/token/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh_token: this.refreshToken }),
            })

            if (response.ok) {
                const data = await response.json()
                this.saveTokens(data.access_token, data.refresh_token)
                return true
            }
        } catch (error) {
            console.error('Token refresh failed:', error)
        }

        this.clearTokens()
        return false
    }

    async requestPasswordReset(email: string): Promise<void> {
        const response = await fetch('/api/auth/password-reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email }),
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.error || 'Failed to request password reset')
        }
    }

    async resetPassword(token: string, newPassword: string): Promise<void> {
        const response = await fetch('/api/auth/reset-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token, new_password: newPassword }),
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.error || 'Failed to reset password')
        }
    }

    async verifyEmail(token: string): Promise<void> {
        const response = await this.makeRequest('/api/auth/email/verify', {
            method: 'POST',
            body: JSON.stringify({ token }),
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Failed to verify email')
        }
    }

    isAuthenticated(): boolean {
        if (!this.accessToken) {
            return false
        }

        try {
            const decoded = jwtDecode(this.accessToken)
            const currentTime = Date.now() / 1000

            if (decoded.exp && decoded.exp < currentTime) {
                this.clearTokens()
                return false
            }

            return true
        } catch (error) {
            console.error('Token decode error:', error)
            this.clearTokens()
            return false
        }
    }

    getAccessToken(): string | null {
        return this.accessToken
    }

    getCurrentUser(): User | null {
        if (!this.accessToken) {
            return null
        }

        try {
            const decoded = jwtDecode(this.accessToken) as any
            return decoded.user || null
        } catch (error) {
            console.error('Failed to decode user from token:', error)
            return null
        }
    }
}

// Create singleton instance
export const authService = new AuthService() 