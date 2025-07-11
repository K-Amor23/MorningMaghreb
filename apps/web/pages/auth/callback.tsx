import { useEffect } from 'react'
import { useRouter } from 'next/router'
import { supabase } from '@/lib/supabase'
import toast from 'react-hot-toast'

export default function AuthCallback() {
  const router = useRouter()

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        if (!supabase) {
          toast.error('Authentication service is not available.')
          router.replace('/login')
          return
        }

        const result = await supabase.auth.getSession()
        
        if (result.error) {
          console.error('Auth callback error:', result.error)
          toast.error('Authentication failed. Please try again.')
          router.replace('/login')
          return
        }

        if (result.data?.session) {
          toast.success('Successfully authenticated!')
          router.replace('/dashboard')
        } else {
          router.replace('/login')
        }
      } catch (error) {
        console.error('Auth callback error:', error)
        toast.error('An error occurred during authentication.')
        router.replace('/login')
      }
    }

    handleAuthCallback()
  }, [router])

  return (
    <div className="min-h-screen bg-casablanca-light flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-casablanca-blue mx-auto"></div>
        <h2 className="mt-4 text-xl font-semibold text-gray-900">
          Completing authentication...
        </h2>
        <p className="mt-2 text-gray-600">
          Please wait while we complete your sign-in.
        </p>
      </div>
    </div>
  )
} 