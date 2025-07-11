import Link from 'next/link'
import { ChartBarIcon } from '@heroicons/react/24/outline'

export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="xl:grid xl:grid-cols-3 xl:gap-8">
          <div className="space-y-6 xl:col-span-1">
            <div className="flex items-center space-x-2">
              <ChartBarIcon className="h-6 w-6 text-casablanca-blue" />
              <span className="text-lg font-bold text-casablanca-blue">
                Casablanca Insight
              </span>
            </div>
            <p className="text-gray-500 text-sm">
              Morocco-focused market research & analytics platform
            </p>
          </div>
          
          <div className="mt-8 grid grid-cols-2 gap-8 xl:mt-0 xl:col-span-2">
            <div className="md:grid md:grid-cols-2 md:gap-8">
              <div>
                <h3 className="text-sm font-semibold text-gray-400 tracking-wider uppercase">
                  Platform
                </h3>
                <ul className="mt-4 space-y-3">
                  <li>
                    <Link href="/dashboard" className="text-sm text-gray-500 hover:text-gray-900 transition-colors">
                      Dashboard
                    </Link>
                  </li>
                  <li>
                    <Link href="/markets" className="text-sm text-gray-500 hover:text-gray-900 transition-colors">
                      Markets
                    </Link>
                  </li>
                  <li>
                    <Link href="/portfolio" className="text-sm text-gray-500 hover:text-gray-900 transition-colors">
                      Portfolio
                    </Link>
                  </li>
                </ul>
              </div>
              <div className="mt-8 md:mt-0">
                <h3 className="text-sm font-semibold text-gray-400 tracking-wider uppercase">
                  Company
                </h3>
                <ul className="mt-4 space-y-3">
                  <li>
                    <Link href="/about" className="text-sm text-gray-500 hover:text-gray-900 transition-colors">
                      About
                    </Link>
                  </li>
                  <li>
                    <Link href="/contact" className="text-sm text-gray-500 hover:text-gray-900 transition-colors">
                      Contact
                    </Link>
                  </li>
                  <li>
                    <Link href="/privacy" className="text-sm text-gray-500 hover:text-gray-900 transition-colors">
                      Privacy
                    </Link>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        
        <div className="mt-8 border-t border-gray-200 pt-6">
          <p className="text-sm text-gray-400 text-center">
            &copy; 2024 Casablanca Insight. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
} 