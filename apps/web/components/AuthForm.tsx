import { useState } from 'react'
import { supabase, isSupabaseConfigured } from '@/lib/supabase'
import toast from 'react-hot-toast'
import GoogleAuthButton from './GoogleAuthButton'

interface AuthFormProps {
  mode: 'login' | 'signup'
  onSuccess: () => void
}

export default function AuthForm({ mode, onSuccess }: AuthFormProps) {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    newsletter: true,
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Check if Supabase is configured
      if (!isSupabaseConfigured()) {
        toast.error('Authentication is not configured. Please set up Supabase credentials.')
        return
      }

      if (!supabase) {
        toast.error('Authentication service is not available.')
        return
      }

      // Validation
      if (mode === 'signup') {
        if (formData.password !== formData.confirmPassword) {
          toast.error('Passwords do not match')
          return
        }

        if (formData.password.length < 6) {
          toast.error('Password must be at least 6 characters')
          return
        }
      }

      if (mode === 'login') {
        // Sign in with Supabase
        const { data, error } = await supabase.auth.signInWithPassword({
          email: formData.email,
          password: formData.password,
        })

        if (error) {
          toast.error(error.message)
          return
        }

        if (data.user) {
          toast.success('Welcome back!')
          onSuccess()
        }
      } else {
        // Sign up with Supabase
        const { data, error } = await supabase.auth.signUp({
          email: formData.email,
          password: formData.password,
          options: {
            data: {
              newsletter_opt_in: formData.newsletter,
            },
          },
        })

        if (error) {
          toast.error(error.message)
          return
        }

        if (data.user) {
          toast.success('Account created successfully! Please check your email for verification.')
          onSuccess()
        }
      }
    } catch (error) {
      toast.error('An error occurred. Please try again.')
      console.error('Auth error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          Email address
        </label>
        <div className="mt-1">
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            value={formData.email}
            onChange={handleChange}
            className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-casablanca-blue focus:border-casablanca-blue sm:text-sm"
            placeholder="Enter your email"
          />
        </div>
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700">
          Password
        </label>
        <div className="mt-1">
          <input
            id="password"
            name="password"
            type="password"
            autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            required
            value={formData.password}
            onChange={handleChange}
            className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-casablanca-blue focus:border-casablanca-blue sm:text-sm"
            placeholder="Enter your password"
          />
        </div>
      </div>

      {mode === 'signup' && (
        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
            Confirm Password
          </label>
          <div className="mt-1">
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              autoComplete="new-password"
              required
              value={formData.confirmPassword}
              onChange={handleChange}
              className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-casablanca-blue focus:border-casablanca-blue sm:text-sm"
              placeholder="Confirm your password"
            />
          </div>
        </div>
      )}

      {mode === 'login' && (
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <input
              id="remember-me"
              name="remember-me"
              type="checkbox"
              className="h-4 w-4 text-casablanca-blue focus:ring-casablanca-blue border-gray-300 rounded"
            />
            <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
              Remember me
            </label>
          </div>

          <div className="text-sm">
            <a href="#" className="font-medium text-casablanca-blue hover:text-blue-500">
              Forgot your password?
            </a>
          </div>
        </div>
      )}

      {mode === 'signup' && (
        <div className="flex items-center">
          <input
            id="newsletter"
            name="newsletter"
            type="checkbox"
            checked={formData.newsletter}
            onChange={handleChange}
            className="h-4 w-4 text-casablanca-blue focus:ring-casablanca-blue border-gray-300 rounded"
          />
          <label htmlFor="newsletter" className="ml-2 block text-sm text-gray-900">
            Subscribe to Morning Maghreb newsletter
          </label>
        </div>
      )}

      <div>
        <button
          type="submit"
          disabled={loading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-casablanca-blue hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-casablanca-blue disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <div className="loading-spinner h-5 w-5" />
          ) : (
            mode === 'login' ? 'Sign In' : 'Create Account'
          )}
        </button>
      </div>

      <div className="mt-6">
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">
              Or continue with
            </span>
          </div>
        </div>

        <div className="mt-6">
          <GoogleAuthButton mode={mode} onSuccess={onSuccess} />
        </div>
      </div>
    </form>
  )
} 