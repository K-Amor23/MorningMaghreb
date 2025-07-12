import * as LocalAuthentication from 'expo-local-authentication'
import * as SecureStore from 'expo-secure-store'
import { supabase } from './supabase'
import { Platform } from 'react-native'

export interface AuthUser {
  id: string
  email: string
  name?: string
  tier?: 'free' | 'pro' | 'admin'
}

export interface AuthState {
  user: AuthUser | null
  isAuthenticated: boolean
  isLoading: boolean
  biometricEnabled: boolean
}

class AuthService {
  private biometricSupported: boolean = false
  private biometricEnrolled: boolean = false

  constructor() {
    this.checkBiometricSupport()
  }

  async checkBiometricSupport() {
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync()
      const isEnrolled = await LocalAuthentication.isEnrolledAsync()
      
      this.biometricSupported = hasHardware
      this.biometricEnrolled = isEnrolled
      
      return { hasHardware, isEnrolled }
    } catch (error) {
      console.error('Error checking biometric support:', error)
      return { hasHardware: false, isEnrolled: false }
    }
  }

  async signInWithEmail(email: string, password: string): Promise<AuthUser | null> {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) throw error

      if (data.user) {
        const user: AuthUser = {
          id: data.user.id,
          email: data.user.email!,
          name: data.user.user_metadata?.full_name,
          tier: data.user.user_metadata?.tier || 'free',
        }

        // Store auth token securely
        await SecureStore.setItemAsync('auth_token', data.session?.access_token || '')
        await SecureStore.setItemAsync('user_data', JSON.stringify(user))

        return user
      }

      return null
    } catch (error) {
      console.error('Sign in error:', error)
      throw error
    }
  }

  async signUpWithEmail(email: string, password: string, name?: string): Promise<AuthUser | null> {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: name,
            tier: 'free',
          },
        },
      })

      if (error) throw error

      if (data.user) {
        const user: AuthUser = {
          id: data.user.id,
          email: data.user.email!,
          name: name || data.user.user_metadata?.full_name,
          tier: 'free',
        }

        // Store auth token securely
        await SecureStore.setItemAsync('auth_token', data.session?.access_token || '')
        await SecureStore.setItemAsync('user_data', JSON.stringify(user))

        return user
      }

      return null
    } catch (error) {
      console.error('Sign up error:', error)
      throw error
    }
  }

  async signInWithBiometric(): Promise<AuthUser | null> {
    try {
      if (!this.biometricSupported || !this.biometricEnrolled) {
        throw new Error('Biometric authentication not available')
      }

      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Authenticate to access your account',
        fallbackLabel: 'Use passcode',
        cancelLabel: 'Cancel',
        disableDeviceFallback: false,
      })

      if (result.success) {
        // Retrieve stored user data
        const userData = await SecureStore.getItemAsync('user_data')
        const token = await SecureStore.getItemAsync('auth_token')

        if (userData && token) {
          const user = JSON.parse(userData) as AuthUser
          
          // Verify token is still valid
          const { data: { user: currentUser }, error } = await supabase.auth.getUser(token)
          
          if (error || !currentUser) {
            // Token expired, need to re-authenticate
            await this.signOut()
            throw new Error('Session expired. Please sign in again.')
          }

          return user
        }
      }

      return null
    } catch (error) {
      console.error('Biometric authentication error:', error)
      throw error
    }
  }

  async enableBiometric(): Promise<boolean> {
    try {
      if (!this.biometricSupported || !this.biometricEnrolled) {
        throw new Error('Biometric authentication not available')
      }

      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Authenticate to enable biometric login',
        fallbackLabel: 'Use passcode',
        cancelLabel: 'Cancel',
        disableDeviceFallback: false,
      })

      if (result.success) {
        await SecureStore.setItemAsync('biometric_enabled', 'true')
        return true
      }

      return false
    } catch (error) {
      console.error('Enable biometric error:', error)
      return false
    }
  }

  async disableBiometric(): Promise<boolean> {
    try {
      await SecureStore.deleteItemAsync('biometric_enabled')
      return true
    } catch (error) {
      console.error('Disable biometric error:', error)
      return false
    }
  }

  async isBiometricEnabled(): Promise<boolean> {
    try {
      const enabled = await SecureStore.getItemAsync('biometric_enabled')
      return enabled === 'true'
    } catch (error) {
      console.error('Check biometric enabled error:', error)
      return false
    }
  }

  async getCurrentUser(): Promise<AuthUser | null> {
    try {
      const token = await SecureStore.getItemAsync('auth_token')
      if (!token) return null

      const { data: { user }, error } = await supabase.auth.getUser(token)
      
      if (error || !user) {
        await this.signOut()
        return null
      }

      const userData = await SecureStore.getItemAsync('user_data')
      if (userData) {
        return JSON.parse(userData) as AuthUser
      }

      return null
    } catch (error) {
      console.error('Get current user error:', error)
      return null
    }
  }

  async signOut(): Promise<void> {
    try {
      await supabase.auth.signOut()
      await SecureStore.deleteItemAsync('auth_token')
      await SecureStore.deleteItemAsync('user_data')
    } catch (error) {
      console.error('Sign out error:', error)
    }
  }

  async resetPassword(email: string): Promise<void> {
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: 'casablanca-insight://reset-password',
      })

      if (error) throw error
    } catch (error) {
      console.error('Reset password error:', error)
      throw error
    }
  }

  async updatePassword(newPassword: string): Promise<void> {
    try {
      const { error } = await supabase.auth.updateUser({
        password: newPassword,
      })

      if (error) throw error
    } catch (error) {
      console.error('Update password error:', error)
      throw error
    }
  }

  async updateProfile(updates: { name?: string; email?: string }): Promise<AuthUser | null> {
    try {
      const { data, error } = await supabase.auth.updateUser({
        email: updates.email,
        data: {
          full_name: updates.name,
        },
      })

      if (error) throw error

      if (data.user) {
        const user: AuthUser = {
          id: data.user.id,
          email: data.user.email!,
          name: updates.name || data.user.user_metadata?.full_name,
          tier: data.user.user_metadata?.tier || 'free',
        }

        await SecureStore.setItemAsync('user_data', JSON.stringify(user))
        return user
      }

      return null
    } catch (error) {
      console.error('Update profile error:', error)
      throw error
    }
  }

  getBiometricType(): string {
    if (Platform.OS === 'ios') {
      return 'FaceID'
    } else {
      return 'Fingerprint'
    }
  }

  isBiometricSupported(): boolean {
    return this.biometricSupported
  }

  isBiometricEnrolled(): boolean {
    return this.biometricEnrolled
  }
}

export const authService = new AuthService() 