import Head from 'next/head'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { useTranslation } from 'react-i18next'
import AuthForm from '@/components/AuthForm'

export default function SignUp() {
  const { t } = useTranslation()
  const router = useRouter()

  const handleSuccess = () => {
    router.push('/dashboard')
  }

  return (
    <>
      <Head>
        <title>Sign Up - Casablanca Insight</title>
        <meta name="description" content="Create your Casablanca Insight account" />
      </Head>

      <div className="min-h-screen bg-casablanca-light dark:bg-dark-bg flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        {/* Back button */}
        <div className="absolute top-4 left-4">
          <button
            onClick={() => router.back()}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back
          </button>
        </div>
        
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <Link href="/" className="flex justify-center">
            <h1 className="text-3xl font-bold text-casablanca-blue">
              Casablanca Insight
            </h1>
          </Link>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-dark-text">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-dark-text-secondary">
            Or{' '}
            <Link
              href="/login"
              className="font-medium text-casablanca-blue hover:text-blue-500"
            >
              sign in to your existing account
            </Link>
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white dark:bg-dark-card py-8 px-4 shadow sm:rounded-lg sm:px-10">
            <AuthForm mode="signup" onSuccess={handleSuccess} />

            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">
                    By signing up, you agree to our Terms of Service and Privacy Policy
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}