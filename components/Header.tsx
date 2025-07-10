import Link from 'next/link'
import { useTranslation } from 'react-i18next'
import { 
  ChartBarIcon, 
  GlobeAltIcon,
  BellIcon,
  UserCircleIcon
} from '@heroicons/react/24/outline'

export default function Header() {
  const { t } = useTranslation()

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <ChartBarIcon className="h-8 w-8 text-casablanca-blue" />
              <span className="text-xl font-bold text-casablanca-blue">
                Casablanca Insight
              </span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link 
              href="/dashboard" 
              className="text-gray-700 hover:text-casablanca-blue px-3 py-2 text-sm font-medium transition-colors"
            >
              Dashboard
            </Link>
            <Link 
              href="/markets" 
              className="text-gray-700 hover:text-casablanca-blue px-3 py-2 text-sm font-medium transition-colors"
            >
              Markets
            </Link>
            <Link 
              href="/portfolio" 
              className="text-gray-700 hover:text-casablanca-blue px-3 py-2 text-sm font-medium transition-colors"
            >
              Portfolio
            </Link>
            <Link 
              href="/news" 
              className="text-gray-700 hover:text-casablanca-blue px-3 py-2 text-sm font-medium transition-colors"
            >
              News
            </Link>
          </nav>

          {/* Right side actions */}
          <div className="flex items-center space-x-4">
            {/* Language selector */}
            <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
              <GlobeAltIcon className="h-5 w-5" />
            </button>
            
            {/* Notifications */}
            <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors relative">
              <BellIcon className="h-5 w-5" />
              <span className="absolute top-1 right-1 h-2 w-2 bg-morocco-red rounded-full"></span>
            </button>
            
            {/* User menu */}
            <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
              <UserCircleIcon className="h-6 w-6" />
            </button>
          </div>
        </div>
      </div>
    </header>
  )
} 