import { useState } from 'react'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Here you would call your backend or Supabase password reset
    setSubmitted(true)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-dark-bg px-4">
      <div className="max-w-md w-full bg-white dark:bg-dark-card p-8 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-6 text-center text-casablanca-blue">Reset your password</h2>
        {submitted ? (
          <div className="text-green-600 text-center">
            If an account with that email exists, a password reset link has been sent.
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-casablanca-blue focus:border-casablanca-blue sm:text-sm"
                placeholder="Enter your email"
              />
            </div>
            <button
              type="submit"
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-casablanca-blue hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-casablanca-blue"
            >
              Send reset link
            </button>
          </form>
        )}
      </div>
    </div>
  )
} 