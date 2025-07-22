import { useState } from 'react'
import { EnvelopeIcon, CheckIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface NewsletterSignupProps {
  title?: string
  subtitle?: string
  cta?: string
}

export default function NewsletterSignup({ 
  title = "Stay Informed",
  subtitle = "Get the Morning Maghreb in your inbox",
  cta = "Sign Up Free"
}: NewsletterSignupProps) {
  const [email, setEmail] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    
    try {
      const response = await fetch('/api/newsletter/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email,
          name: '', // Optional name field
          preferences: {
            language: 'en',
            delivery_time: '08:00',
            frequency: 'daily',
          }
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        if (response.status === 409) {
          toast.error('This email is already subscribed!')
        } else {
          toast.error(data.error || 'Failed to subscribe. Please try again.')
        }
        return
      }

      toast.success('Successfully subscribed to Morning Maghreb!')
      setIsSubmitted(true)
      setEmail('')
      
      // Reset after 5 seconds
      setTimeout(() => setIsSubmitted(false), 5000)
      
    } catch (error) {
      console.error('Newsletter signup error:', error)
      toast.error('Failed to subscribe. Please check your connection and try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="bg-gradient-to-br from-casablanca-blue to-blue-600 rounded-lg shadow-sm p-6 text-white">
      <div className="text-center">
        <EnvelopeIcon className="h-8 w-8 mx-auto mb-3 text-blue-200" />
        <h3 className="text-lg font-semibold mb-2">{title}</h3>
        <p className="text-sm text-blue-200 mb-4">{subtitle}</p>
      </div>

      {!isSubmitted ? (
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label htmlFor="email" className="sr-only">
              Email address
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-transparent placeholder-gray-400 bg-white/10 rounded-md text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white/20 focus:border-white/20"
              placeholder="Enter your email"
            />
          </div>
          
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-morocco-red hover:bg-red-600 disabled:bg-red-400 border border-transparent rounded-md py-2 px-4 flex items-center justify-center text-sm font-medium text-white transition-colors"
          >
            {isSubmitting ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Signing up...
              </div>
            ) : (
              cta
            )}
          </button>
        </form>
      ) : (
        <div className="text-center">
          <CheckIcon className="h-8 w-8 mx-auto mb-3 text-green-300" />
          <p className="text-sm text-blue-200">
            Thanks for subscribing! Check your email for confirmation.
          </p>
        </div>
      )}

      <div className="mt-4 text-xs text-blue-200 text-center">
        <p>Daily market insights, top movers, and AI-powered analysis</p>
        <p className="mt-1">Unsubscribe anytime. No spam.</p>
      </div>
    </div>
  )
} 