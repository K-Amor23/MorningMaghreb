import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import toast from 'react-hot-toast'

export default function TestAuth() {
  const [session, setSession] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [testResults, setTestResults] = useState<string[]>([])

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    setLoading(true)
    const results: string[] = []

    try {
      // Test 1: Check if Supabase is configured
      if (!supabase) {
        results.push('❌ Supabase client is not configured')
      } else {
        results.push('✅ Supabase client is configured')
      }

      // Test 2: Check environment variables
      const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
      const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

      if (!supabaseUrl || supabaseUrl === 'your_supabase_url') {
        results.push('❌ NEXT_PUBLIC_SUPABASE_URL is not set correctly')
      } else {
        results.push('✅ NEXT_PUBLIC_SUPABASE_URL is configured')
      }

      if (!supabaseKey || supabaseKey === 'your_supabase_anon_key') {
        results.push('❌ NEXT_PUBLIC_SUPABASE_ANON_KEY is not set correctly')
      } else {
        results.push('✅ NEXT_PUBLIC_SUPABASE_ANON_KEY is configured')
      }

      // Test 3: Check current session
      if (supabase) {
        const { data: { session }, error } = await supabase.auth.getSession()
        
        if (error) {
          results.push(`❌ Error getting session: ${error.message}`)
        } else if (session) {
          results.push('✅ User is authenticated')
          setSession(session)
        } else {
          results.push('ℹ️ No active session (user not logged in)')
        }
      }

      // Test 4: Test database connection
      if (supabase) {
        try {
          const { data, error } = await supabase
            .from('profiles')
            .select('count')
            .limit(1)
          
          if (error) {
            results.push(`❌ Database connection error: ${error.message}`)
          } else {
            results.push('✅ Database connection successful')
          }
        } catch (dbError: any) {
          results.push(`❌ Database test failed: ${dbError.message}`)
        }
      }

    } catch (error: any) {
      results.push(`❌ General error: ${error.message}`)
    }

    setTestResults(results)
    setLoading(false)
  }

  const testSignUp = async () => {
    const testEmail = `test-${Date.now()}@example.com`
    const testPassword = 'testpassword123'

    try {
      const { data, error } = await supabase.auth.signUp({
        email: testEmail,
        password: testPassword,
      })

      if (error) {
        toast.error(`Signup test failed: ${error.message}`)
      } else {
        toast.success('Test signup successful! Check your email for confirmation.')
      }
    } catch (error: any) {
      toast.error(`Signup test error: ${error.message}`)
    }
  }

  const testSignIn = async () => {
    const testEmail = 'test@example.com'
    const testPassword = 'testpassword123'

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: testEmail,
        password: testPassword,
      })

      if (error) {
        toast.error(`Signin test failed: ${error.message}`)
      } else {
        toast.success('Test signin successful!')
        checkAuth()
      }
    } catch (error: any) {
      toast.error(`Signin test error: ${error.message}`)
    }
  }

  const signOut = async () => {
    try {
      const { error } = await supabase.auth.signOut()
      if (error) {
        toast.error(`Signout failed: ${error.message}`)
      } else {
        toast.success('Signed out successfully')
        setSession(null)
        checkAuth()
      }
    } catch (error: any) {
      toast.error(`Signout error: ${error.message}`)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          Supabase Authentication Test
        </h1>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Configuration Test Results
          </h2>
          
          {loading ? (
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-2"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
            </div>
          ) : (
            <div className="space-y-2">
              {testResults.map((result, index) => (
                <div key={index} className="text-sm font-mono">
                  {result}
                </div>
              ))}
            </div>
          )}

          <button
            onClick={checkAuth}
            className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Refresh Tests
          </button>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Authentication Tests
          </h2>
          
          <div className="space-y-4">
            <button
              onClick={testSignUp}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 mr-4"
            >
              Test Sign Up
            </button>
            
            <button
              onClick={testSignIn}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 mr-4"
            >
              Test Sign In
            </button>
            
            {session && (
              <button
                onClick={signOut}
                className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
              >
                Sign Out
              </button>
            )}
          </div>
        </div>

        {session && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Current Session
            </h2>
            <pre className="bg-gray-100 dark:bg-gray-700 p-4 rounded text-sm overflow-auto">
              {JSON.stringify(session, null, 2)}
            </pre>
          </div>
        )}

        <div className="mt-6">
          <a
            href="/login"
            className="text-blue-500 hover:text-blue-600 underline"
          >
            Go to Login Page
          </a>
        </div>
      </div>
    </div>
  )
} 