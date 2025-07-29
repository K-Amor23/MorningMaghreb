import React, { useState, useEffect } from 'react'
import { DevicePhoneMobileIcon, ComputerDesktopIcon } from '@heroicons/react/24/outline'

interface PWAInstallerProps {
    onInstall?: () => void
}

export default function PWAInstaller({ onInstall }: PWAInstallerProps) {
    const [deferredPrompt, setDeferredPrompt] = useState<any>(null)
    const [isInstalled, setIsInstalled] = useState(false)
    const [showInstallPrompt, setShowInstallPrompt] = useState(false)
    const [swRegistration, setSwRegistration] = useState<ServiceWorkerRegistration | null>(null)
    const [mounted, setMounted] = useState(false)

    useEffect(() => {
        setMounted(true)
    }, [])

    useEffect(() => {
        // Only run in browser environment and after mounting
        if (typeof window === 'undefined' || !mounted) {
            return
        }

        // Check if app is already installed
        if (window.matchMedia('(display-mode: standalone)').matches) {
            setIsInstalled(true)
            return
        }

        // Listen for beforeinstallprompt event
        const handleBeforeInstallPrompt = (e: Event) => {
            e.preventDefault()
            setDeferredPrompt(e)
            setShowInstallPrompt(true)
        }

        // Listen for appinstalled event
        const handleAppInstalled = () => {
            setIsInstalled(true)
            setShowInstallPrompt(false)
            onInstall?.()
        }

        // Register service worker
        registerServiceWorker()

        window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
        window.addEventListener('appinstalled', handleAppInstalled)

        return () => {
            window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
            window.removeEventListener('appinstalled', handleAppInstalled)
        }
    }, [onInstall, mounted])

    const registerServiceWorker = async () => {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/sw.js')
                setSwRegistration(registration)
                console.log('Service Worker registered:', registration)

                // Check for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing
                    if (newWorker) {
                        newWorker.addEventListener('statechange', () => {
                            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                // New service worker available
                                showUpdateNotification()
                            }
                        })
                    }
                })
            } catch (error) {
                console.error('Service Worker registration failed:', error)
            }
        }
    }

    const showUpdateNotification = () => {
        if (confirm('A new version is available. Would you like to update?')) {
            swRegistration?.waiting?.postMessage({ type: 'SKIP_WAITING' })
            window.location.reload()
        }
    }

    const handleInstallClick = async () => {
        if (!deferredPrompt) return

        // Show the install prompt
        deferredPrompt.prompt()

        // Wait for the user to respond to the prompt
        const { outcome } = await deferredPrompt.userChoice

        if (outcome === 'accepted') {
            console.log('User accepted the install prompt')
            setIsInstalled(true)
            setShowInstallPrompt(false)
            onInstall?.()
        } else {
            console.log('User dismissed the install prompt')
        }

        // Clear the deferredPrompt
        setDeferredPrompt(null)
    }

    const handleDismiss = () => {
        setShowInstallPrompt(false)
        setDeferredPrompt(null)
    }

    if (isInstalled) {
        return null
    }

    if (!showInstallPrompt) {
        return null
    }

    return (
        <div className="fixed bottom-4 right-4 z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4 max-w-sm">
                <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                        <div className="w-10 h-10 bg-casablanca-blue rounded-lg flex items-center justify-center">
                            <DevicePhoneMobileIcon className="h-6 w-6 text-white" />
                        </div>
                    </div>
                    <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                            Install Casablanca Insights
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            Get quick access to market data and alerts on your device
                        </p>
                        <div className="flex space-x-2 mt-3">
                            <button
                                onClick={handleInstallClick}
                                className="bg-casablanca-blue text-white px-3 py-1.5 rounded-md text-sm font-medium hover:bg-casablanca-blue-dark transition-colors"
                            >
                                Install
                            </button>
                            <button
                                onClick={handleDismiss}
                                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 px-3 py-1.5 text-sm"
                            >
                                Not now
                            </button>
                        </div>
                    </div>
                    <button
                        onClick={handleDismiss}
                        className="flex-shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    >
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    )
}

// Hook for PWA functionality
export function usePWA() {
    const [isOnline, setIsOnline] = useState(true)
    const [isStandalone, setIsStandalone] = useState(false)
    const [mounted, setMounted] = useState(false)

    useEffect(() => {
        setMounted(true)
    }, [])

    useEffect(() => {
        // Only run in browser environment and after mounting
        if (typeof window === 'undefined' || !mounted) {
            return
        }

        // Check online status
        const handleOnline = () => setIsOnline(true)
        const handleOffline = () => setIsOnline(false)

        window.addEventListener('online', handleOnline)
        window.addEventListener('offline', handleOffline)

        // Check if app is in standalone mode
        setIsStandalone(window.matchMedia('(display-mode: standalone)').matches)

        return () => {
            window.removeEventListener('online', handleOnline)
            window.removeEventListener('offline', handleOffline)
        }
    }, [mounted])

    return {
        isOnline,
        isStandalone,
        isPWA: mounted && typeof window !== 'undefined' && (isStandalone || (window.navigator as any).standalone)
    }
} 