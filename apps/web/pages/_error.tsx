import { NextPageContext } from 'next'
import Head from 'next/head'
import Link from 'next/link'
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'

interface ErrorProps {
  statusCode?: number
  hasGetInitialPropsRun?: boolean
  err?: Error
}

function Error({ statusCode, hasGetInitialPropsRun, err }: ErrorProps) {
  if (!hasGetInitialPropsRun && err) {
    // getInitialProps is not called in case of
    // https://github.com/vercel/next.js/issues/8592. As a workaround, we pass
    // err via _app.js so it can be captured
    // eslint-disable-next-line no-unused-vars
    // err = err
  }

  return (
    <>
      <Head>
        <title>Error {statusCode} - Casablanca Insight</title>
        <meta name="description" content="An error occurred" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="mb-8">
            <ExclamationTriangleIcon className="mx-auto h-16 w-16 text-red-500" />
          </div>
          
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            {statusCode ? `${statusCode}` : 'Error'}
          </h1>
          
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
            {statusCode === 404
              ? 'The page you are looking for does not exist.'
              : 'Something went wrong. Please try again later.'}
          </p>
          
          <div className="space-y-4">
            <Link
              href="/"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-casablanca-blue hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Go back home
            </Link>
            
            <button
              onClick={() => window.location.reload()}
              className="block w-full mt-4 px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Try again
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

Error.getInitialProps = ({ res, err }: NextPageContext) => {
  const statusCode = res ? res.statusCode : err ? err.statusCode : 404
  return { statusCode, hasGetInitialPropsRun: true, err }
}

export default Error 