const CACHE_NAME = 'morningmaghreb-v1'
const STATIC_CACHE_NAME = 'casablanca-static-v1'
const DYNAMIC_CACHE_NAME = 'casablanca-dynamic-v1'

// Static assets to cache
const STATIC_ASSETS = [
    '/',
    '/manifest.json',
    '/icons/icon-192x192.png',
    '/icons/icon-512x512.png',
    '/styles/globals.css',
    '/api/health',
    '/api/markets/quotes',
    '/api/data-quality'
]

// API endpoints to cache
const API_CACHE_PATTERNS = [
    /\/api\/markets\/quotes/,
    /\/api\/search\/companies/,
    /\/api\/companies\/.*\/summary/,
    /\/api\/data-quality/
]

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...')
    event.waitUntil(
        caches.open(STATIC_CACHE_NAME)
            .then((cache) => {
                console.log('Caching static assets')
                return cache.addAll(STATIC_ASSETS)
            })
            .then(() => {
                console.log('Service Worker installed')
                return self.skipWaiting()
            })
            .catch((error) => {
                console.error('Service Worker install failed:', error)
            })
    )
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker activating...')
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== STATIC_CACHE_NAME && cacheName !== DYNAMIC_CACHE_NAME) {
                            console.log('Deleting old cache:', cacheName)
                            return caches.delete(cacheName)
                        }
                    })
                )
            })
            .then(() => {
                console.log('Service Worker activated')
                return self.clients.claim()
            })
    )
})

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
    const { request } = event
    const url = new URL(request.url)

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return
    }

    // Handle API requests
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(handleApiRequest(request))
        return
    }

    // Handle static assets
    if (isStaticAsset(request)) {
        event.respondWith(handleStaticAsset(request))
        return
    }

    // Handle navigation requests
    if (request.mode === 'navigate') {
        event.respondWith(handleNavigation(request))
        return
    }

    // Default: network first, fallback to cache
    event.respondWith(
        fetch(request)
            .then((response) => {
                // Cache successful responses
                if (response.status === 200) {
                    const responseClone = response.clone()
                    caches.open(DYNAMIC_CACHE_NAME)
                        .then((cache) => {
                            cache.put(request, responseClone)
                        })
                }
                return response
            })
            .catch(() => {
                // Fallback to cache
                return caches.match(request)
            })
    )
})

// Handle API requests with cache-first strategy
async function handleApiRequest(request) {
    const cache = await caches.open(DYNAMIC_CACHE_NAME)

    try {
        // Try network first
        const networkResponse = await fetch(request)

        // Cache successful responses
        if (networkResponse.status === 200) {
            const responseClone = networkResponse.clone()
            cache.put(request, responseClone)
        }

        return networkResponse
    } catch (error) {
        // Fallback to cache
        const cachedResponse = await cache.match(request)
        if (cachedResponse) {
            return cachedResponse
        }

        // Return offline response for API requests
        return new Response(
            JSON.stringify({
                error: 'No internet connection',
                offline: true
            }),
            {
                status: 503,
                headers: { 'Content-Type': 'application/json' }
            }
        )
    }
}

// Handle static assets with cache-first strategy
async function handleStaticAsset(request) {
    const cache = await caches.open(STATIC_CACHE_NAME)
    const cachedResponse = await cache.match(request)

    if (cachedResponse) {
        return cachedResponse
    }

    try {
        const networkResponse = await fetch(request)
        if (networkResponse.status === 200) {
            const responseClone = networkResponse.clone()
            cache.put(request, responseClone)
        }
        return networkResponse
    } catch (error) {
        return new Response('Offline', { status: 503 })
    }
}

// Handle navigation requests
async function handleNavigation(request) {
    try {
        const networkResponse = await fetch(request)
        return networkResponse
    } catch (error) {
        // Return cached home page for navigation requests
        const cache = await caches.open(STATIC_CACHE_NAME)
        const cachedResponse = await cache.match('/')
        return cachedResponse || new Response('Offline', { status: 503 })
    }
}

// Check if request is for a static asset
function isStaticAsset(request) {
    const url = new URL(request.url)
    return (
        url.pathname.startsWith('/icons/') ||
        url.pathname.startsWith('/styles/') ||
        url.pathname.startsWith('/manifest.json') ||
        url.pathname === '/'
    )
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
    console.log('Background sync triggered:', event.tag)

    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync())
    }
})

// Handle push notifications
self.addEventListener('push', (event) => {
    console.log('Push notification received:', event)

    const options = {
        body: event.data ? event.data.text() : 'New update available',
        icon: '/icons/icon-192x192.png',
        badge: '/icons/icon-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View',
                icon: '/icons/icon-72x72.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/icons/icon-72x72.png'
            }
        ]
    }

    event.waitUntil(
        self.registration.showNotification('Casablanca Insights', options)
    )
})

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
    console.log('Notification clicked:', event)

    event.notification.close()

    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        )
    }
})

// Background sync function
async function doBackgroundSync() {
    try {
        // Sync any pending data
        console.log('Performing background sync...')

        // Example: sync watchlist changes
        const pendingChanges = await getPendingChanges()
        if (pendingChanges.length > 0) {
            await syncPendingChanges(pendingChanges)
        }

        console.log('Background sync completed')
    } catch (error) {
        console.error('Background sync failed:', error)
    }
}

// Get pending changes from IndexedDB
async function getPendingChanges() {
    // This would typically read from IndexedDB
    // For now, return empty array
    return []
}

// Sync pending changes to server
async function syncPendingChanges(changes) {
    // This would typically send changes to the server
    console.log('Syncing changes:', changes)
}

// Message handling for communication with main thread
self.addEventListener('message', (event) => {
    console.log('Service Worker received message:', event.data)

    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting()
    }

    if (event.data && event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({ version: CACHE_NAME })
    }
}) 