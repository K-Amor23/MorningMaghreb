import { useState, useEffect } from 'react'
import { authService } from './auth'

export interface WebSocketMessage {
    type: string
    data?: any
    timestamp: string
    client_id?: string
}

export interface QuoteUpdate {
    ticker: string
    price: number
    change: number
    change_percent: number
    volume: number
    high: number
    low: number
    open: number
    previous_close: number
    timestamp: string
    market_cap?: number
    pe_ratio?: number
    dividend_yield?: number
}

export interface AlertNotification {
    alert_id: string
    ticker: string
    company_name: string
    alert_type: string
    target_value: number
    current_value: number
    triggered_at: string
}

export interface WatchlistUpdate {
    watchlist_id: string
    watchlist_name: string
    action: 'add' | 'remove' | 'update'
    ticker: string
    company_name: string
}

class WebSocketClient {
    private ws: WebSocket | null = null
    private reconnectAttempts = 0
    private maxReconnectAttempts = 5
    private reconnectDelay = 1000
    private heartbeatInterval: NodeJS.Timeout | null = null
    private messageHandlers: Map<string, ((data: any) => void)[]> = new Map()
    private isConnecting = false
    private url: string
    private isBrowser: boolean

    constructor() {
        this.url = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'
        this.isBrowser = typeof window !== 'undefined'
    }

    connect(): Promise<void> {
        return new Promise((resolve, reject) => {
            if (!this.isBrowser) {
                resolve()
                return
            }

            if (this.ws?.readyState === WebSocket.OPEN) {
                resolve()
                return
            }

            if (this.isConnecting) {
                return
            }

            this.isConnecting = true

            try {
                this.ws = new WebSocket(this.url)

                this.ws.onopen = () => {
                    console.log('WebSocket connected')
                    this.isConnecting = false
                    this.reconnectAttempts = 0
                    this.startHeartbeat()
                    this.authenticate()
                    resolve()
                }

                this.ws.onmessage = (event) => {
                    try {
                        const message: WebSocketMessage = JSON.parse(event.data)
                        this.handleMessage(message)
                    } catch (error) {
                        console.error('Error parsing WebSocket message:', error)
                    }
                }

                this.ws.onclose = (event) => {
                    console.log('WebSocket disconnected:', event.code, event.reason)
                    this.isConnecting = false
                    this.stopHeartbeat()

                    if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
                        this.scheduleReconnect()
                    }
                }

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error)
                    this.isConnecting = false
                    reject(error)
                }
            } catch (error) {
                this.isConnecting = false
                reject(error)
            }
        })
    }

    private authenticate() {
        const token = authService.getAccessToken()
        if (token && this.ws?.readyState === WebSocket.OPEN) {
            this.send({
                type: 'authenticate',
                data: { token },
                timestamp: new Date().toISOString()
            })
        }
    }

    private startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.ws?.readyState === WebSocket.OPEN) {
                this.send({
                    type: 'heartbeat',
                    data: { timestamp: new Date().toISOString() },
                    timestamp: new Date().toISOString()
                })
            }
        }, 30000) // Send heartbeat every 30 seconds
    }

    private stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval)
            this.heartbeatInterval = null
        }
    }

    private scheduleReconnect() {
        this.reconnectAttempts++
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)

        console.log(`Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`)

        setTimeout(() => {
            this.connect().catch(error => {
                console.error('Reconnect failed:', error)
            })
        }, delay)
    }

    private handleMessage(message: WebSocketMessage) {
        console.log('WebSocket message received:', message)

        // Handle system messages
        switch (message.type) {
            case 'connection_established':
                console.log('Connection established with client ID:', message.client_id)
                break

            case 'heartbeat_ack':
                // Heartbeat acknowledged
                break

            case 'error':
                console.error('WebSocket error:', message.data)
                break

            default:
                // Handle custom message types
                const handlers = this.messageHandlers.get(message.type)
                if (handlers) {
                    handlers.forEach(handler => handler(message.data))
                }
        }
    }

    send(message: WebSocketMessage) {
        if (!this.isBrowser || this.ws?.readyState !== WebSocket.OPEN) {
            console.warn('WebSocket not connected, message not sent:', message)
            return
        }
        this.ws.send(JSON.stringify(message))
    }

    subscribeToTicker(ticker: string) {
        this.send({
            type: 'subscribe',
            data: { ticker },
            timestamp: new Date().toISOString()
        })
    }

    unsubscribeFromTicker(ticker: string) {
        this.send({
            type: 'unsubscribe',
            data: { ticker },
            timestamp: new Date().toISOString()
        })
    }

    subscribeToWatchlist(watchlistId: string) {
        this.send({
            type: 'subscribe_watchlist',
            data: { watchlist_id: watchlistId },
            timestamp: new Date().toISOString()
        })
    }

    unsubscribeFromWatchlist(watchlistId: string) {
        this.send({
            type: 'unsubscribe_watchlist',
            data: { watchlist_id: watchlistId },
            timestamp: new Date().toISOString()
        })
    }

    subscribeToAlerts() {
        this.send({
            type: 'subscribe_alerts',
            data: {},
            timestamp: new Date().toISOString()
        })
    }

    unsubscribeFromAlerts() {
        this.send({
            type: 'unsubscribe_alerts',
            data: {},
            timestamp: new Date().toISOString()
        })
    }

    // Message handlers
    on(event: string, handler: (data: any) => void) {
        if (!this.messageHandlers.has(event)) {
            this.messageHandlers.set(event, [])
        }
        this.messageHandlers.get(event)!.push(handler)
    }

    off(event: string, handler?: (data: any) => void) {
        if (!handler) {
            this.messageHandlers.delete(event)
        } else {
            const handlers = this.messageHandlers.get(event)
            if (handlers) {
                const index = handlers.indexOf(handler)
                if (index > -1) {
                    handlers.splice(index, 1)
                }
            }
        }
    }

    disconnect() {
        this.stopHeartbeat()
        if (this.isBrowser && this.ws) {
            this.ws.close(1000, 'Client disconnecting')
            this.ws = null
        }
    }

    isConnected(): boolean {
        if (!this.isBrowser) return false
        return this.ws?.readyState === WebSocket.OPEN
    }
}

// Create singleton instance
export const websocketClient = new WebSocketClient()

// React hook for WebSocket
export function useWebSocket() {
    const [isConnected, setIsConnected] = useState(false)
    const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)

    useEffect(() => {
        const handleConnect = () => setIsConnected(true)
        const handleDisconnect = () => setIsConnected(false)
        const handleMessage = (message: WebSocketMessage) => setLastMessage(message)

        // Connect to WebSocket
        websocketClient.connect().then(() => {
            setIsConnected(true)
        })

        // Listen for connection events
        websocketClient.on('connection_established', handleConnect)
        websocketClient.on('error', handleDisconnect)

        return () => {
            websocketClient.off('connection_established', handleConnect)
            websocketClient.off('error', handleDisconnect)
        }
    }, [])

    return {
        isConnected,
        lastMessage,
        send: websocketClient.send.bind(websocketClient),
        subscribeToTicker: websocketClient.subscribeToTicker.bind(websocketClient),
        unsubscribeFromTicker: websocketClient.unsubscribeFromTicker.bind(websocketClient),
        subscribeToWatchlist: websocketClient.subscribeToWatchlist.bind(websocketClient),
        unsubscribeFromWatchlist: websocketClient.unsubscribeFromWatchlist.bind(websocketClient),
        subscribeToAlerts: websocketClient.subscribeToAlerts.bind(websocketClient),
        unsubscribeFromAlerts: websocketClient.unsubscribeFromAlerts.bind(websocketClient),
        on: websocketClient.on.bind(websocketClient),
        off: websocketClient.off.bind(websocketClient)
    }
}

// Hook for real-time quotes
export function useLiveQuotes(tickers: string[] = []) {
    const [quotes, setQuotes] = useState<Map<string, QuoteUpdate>>(new Map())
    const { isConnected, subscribeToTicker, unsubscribeFromTicker, on, off } = useWebSocket()

    useEffect(() => {
        const handleQuoteUpdate = (data: QuoteUpdate) => {
            setQuotes(prev => new Map(prev).set(data.ticker, data))
        }

        on('quote_update', handleQuoteUpdate)

        return () => {
            off('quote_update', handleQuoteUpdate)
        }
    }, [on, off])

    useEffect(() => {
        if (!isConnected) return

        // Subscribe to new tickers
        tickers.forEach(ticker => {
            subscribeToTicker(ticker)
        })

        return () => {
            // Unsubscribe from tickers
            tickers.forEach(ticker => {
                unsubscribeFromTicker(ticker)
            })
        }
    }, [isConnected, tickers, subscribeToTicker, unsubscribeFromTicker])

    return {
        quotes: Array.from(quotes.values()),
        getQuote: (ticker: string) => quotes.get(ticker),
        isConnected
    }
}

// Hook for real-time alerts
export function useLiveAlerts() {
    const [alerts, setAlerts] = useState<AlertNotification[]>([])
    const { isConnected, subscribeToAlerts, unsubscribeFromAlerts, on, off } = useWebSocket()

    useEffect(() => {
        const handleAlertNotification = (data: AlertNotification) => {
            setAlerts(prev => [data, ...prev.slice(0, 9)]) // Keep last 10 alerts
        }

        on('alert_notification', handleAlertNotification)

        return () => {
            off('alert_notification', handleAlertNotification)
        }
    }, [on, off])

    useEffect(() => {
        if (!isConnected) return

        subscribeToAlerts()

        return () => {
            unsubscribeFromAlerts()
        }
    }, [isConnected, subscribeToAlerts, unsubscribeFromAlerts])

    return {
        alerts,
        clearAlerts: () => setAlerts([]),
        isConnected
    }
}

// Hook for real-time watchlist updates
export function useLiveWatchlist(watchlistId?: string) {
    const [updates, setUpdates] = useState<WatchlistUpdate[]>([])
    const { isConnected, subscribeToWatchlist, unsubscribeFromWatchlist, on, off } = useWebSocket()

    useEffect(() => {
        const handleWatchlistUpdate = (data: WatchlistUpdate) => {
            setUpdates(prev => [data, ...prev.slice(0, 9)]) // Keep last 10 updates
        }

        on('watchlist_update', handleWatchlistUpdate)

        return () => {
            off('watchlist_update', handleWatchlistUpdate)
        }
    }, [on, off])

    useEffect(() => {
        if (!isConnected || !watchlistId) return

        subscribeToWatchlist(watchlistId)

        return () => {
            unsubscribeFromWatchlist(watchlistId)
        }
    }, [isConnected, watchlistId, subscribeToWatchlist, unsubscribeFromWatchlist])

    return {
        updates,
        clearUpdates: () => setUpdates([]),
        isConnected
    }
} 