import { useState } from 'react'
import Link from 'next/link'
import { useUser } from '@/lib/useUser'
import { TrophyIcon, UserPlusIcon, ChartBarIcon, ArrowRightIcon } from '@heroicons/react/24/outline'

interface ContestPromoProps {
    className?: string
}

export default function ContestPromo({ className = '' }: ContestPromoProps) {
    const { user } = useUser()
    const [isHovered, setIsHovered] = useState(false)

    const features = [
        {
            icon: TrophyIcon,
            title: '$100 Monthly Prize',
            description: 'Compete for real money prizes'
        },
        {
            icon: ChartBarIcon,
            title: 'Paper Trading Portfolio',
            description: 'Show off your trading skills'
        },
        {
            icon: UserPlusIcon,
            title: 'Join the Community',
            description: 'Connect with other traders'
        }
    ]

    return (
        <div className={`bg-gradient-to-br from-yellow-400 via-yellow-500 to-orange-500 rounded-lg shadow-lg p-6 text-white ${className}`}>
            <div className="flex items-start justify-between mb-6">
                <div className="flex-1">
                    <div className="flex items-center mb-2">
                        <TrophyIcon className="h-6 w-6 mr-2" />
                        <h3 className="text-xl font-bold">Monthly Trading Contest</h3>
                    </div>
                    <p className="text-yellow-100 text-sm">
                        Join our monthly portfolio contest and compete for the $100 prize!
                        {!user && ' Create an account and start paper trading to participate.'}
                    </p>
                </div>
                <div className="text-right">
                    <div className="text-2xl font-bold">$100</div>
                    <div className="text-yellow-100 text-sm">Prize Pool</div>
                </div>
            </div>

            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                {features.map((feature, index) => (
                    <div key={index} className="flex items-center space-x-3">
                        <feature.icon className="h-5 w-5 text-yellow-200" />
                        <div>
                            <div className="font-semibold text-sm">{feature.title}</div>
                            <div className="text-yellow-100 text-xs">{feature.description}</div>
                        </div>
                    </div>
                ))}
            </div>

            {/* CTA Button */}
            <div className="flex flex-col sm:flex-row gap-3">
                {user ? (
                    <Link
                        href="/contest"
                        className="flex items-center justify-center px-6 py-3 bg-white text-yellow-600 font-semibold rounded-lg hover:bg-yellow-50 transition-colors group"
                        onMouseEnter={() => setIsHovered(true)}
                        onMouseLeave={() => setIsHovered(false)}
                    >
                        Join Contest Now
                        <ArrowRightIcon className={`h-4 w-4 ml-2 transition-transform ${isHovered ? 'translate-x-1' : ''}`} />
                    </Link>
                ) : (
                    <>
                        <Link
                            href="/signup"
                            className="flex items-center justify-center px-6 py-3 bg-white text-yellow-600 font-semibold rounded-lg hover:bg-yellow-50 transition-colors group"
                            onMouseEnter={() => setIsHovered(true)}
                            onMouseLeave={() => setIsHovered(false)}
                        >
                            Create Account
                            <ArrowRightIcon className={`h-4 w-4 ml-2 transition-transform ${isHovered ? 'translate-x-1' : ''}`} />
                        </Link>
                        <Link
                            href="/login"
                            className="flex items-center justify-center px-6 py-3 border-2 border-white text-white font-semibold rounded-lg hover:bg-white hover:text-yellow-600 transition-colors"
                        >
                            Sign In
                        </Link>
                    </>
                )}
            </div>

            {/* Contest Stats */}
            <div className="mt-4 pt-4 border-t border-yellow-300/30">
                <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                        <div className="text-lg font-bold">47</div>
                        <div className="text-yellow-100 text-xs">Participants</div>
                    </div>
                    <div>
                        <div className="text-lg font-bold">12</div>
                        <div className="text-yellow-100 text-xs">Days Left</div>
                    </div>
                    <div>
                        <div className="text-lg font-bold">+15.2%</div>
                        <div className="text-yellow-100 text-xs">Top Return</div>
                    </div>
                </div>
            </div>
        </div>
    )
} 