import { useRouter } from 'next/router'
import Head from 'next/head'
import Link from 'next/link'
import { ArrowLeftIcon, HomeIcon } from '@heroicons/react/24/outline'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

export default function Custom404() {
  const router = useRouter()

  return (
    <>
      <Head>
        <title>Page Not Found - Casablanca Insight</title>
        <meta name="description" content="The page you're looking for doesn't exist." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-dark-bg text-gray-900 dark:text-dark-text">
        <Header />
        
        <main className="flex items-center justify-center min-h-[calc(100vh-200px)] px-4">
          <div className="text-center max-w-md mx-auto">
            {/* 404 Icon */}
            <div className="mb-8">
              <div className="mx-auto h-24 w-24 bg-casablanca-blue/10 rounded-full flex items-center justify-center">
                <span className="text-4xl font-bold text-casablanca-blue">404</span>
              </div>
            </div>

            {/* Error Message */}
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Page Not Found
            </h1>
            
            <p className="text-gray-600 dark:text-gray-400 mb-8 text-lg">
              Sorry, we couldn't find the page you're looking for. It might have been moved, deleted, or you entered the wrong URL.
            </p>

            {/* Action Buttons */}
            <div className="space-y-4">
              <button
                onClick={() => router.back()}
                className="w-full flex items-center justify-center px-6 py-3 border border-gray-300 dark:border-dark-border rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-dark-hover transition-colors"
              >
                <ArrowLeftIcon className="h-5 w-5 mr-2" />
                Go Back
              </button>
              
              <Link
                href="/"
                className="w-full flex items-center justify-center px-6 py-3 bg-casablanca-blue text-white rounded-lg hover:bg-casablanca-blue/90 transition-colors"
              >
                <HomeIcon className="h-5 w-5 mr-2" />
                Go to Homepage
              </Link>
            </div>

            {/* Additional Help */}
            <div className="mt-8 pt-8 border-t border-gray-200 dark:border-dark-border">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                Looking for a specific company? Try searching:
              </p>
              <div className="space-y-2 text-sm">
                <Link href="/company/ATW" className="block text-casablanca-blue hover:underline">
                  ATW - Attijariwafa Bank
                </Link>
                <Link href="/company/IAM" className="block text-casablanca-blue hover:underline">
                  IAM - Maroc Telecom
                </Link>
                <Link href="/company/BCP" className="block text-casablanca-blue hover:underline">
                  BCP - Banque Centrale Populaire
                </Link>
              </div>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </>
  )
} 