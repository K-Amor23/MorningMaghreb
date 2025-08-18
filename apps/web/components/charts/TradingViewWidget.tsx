import { useEffect, useRef } from 'react'

interface TradingViewWidgetProps {
    symbol: string
    interval: string
    style: 'candlestick' | 'line' | 'area'
    showVolume: boolean
    showIndicators: boolean
}

export default function TradingViewWidget({
    symbol,
    interval,
    style,
    showVolume,
    showIndicators
}: TradingViewWidgetProps) {
    const container = useRef<HTMLDivElement>(null)

    useEffect(() => {
        if (typeof window !== 'undefined' && container.current) {
            const script = document.createElement('script')
            script.src = 'https://s3.tradingview.com/tv.js'
            script.async = true
            script.onload = () => {
                if (window.TradingView && container.current) {
                    new window.TradingView.widget({
                        container_id: container.current.id,
                        symbol: symbol,
                        interval: interval,
                        timezone: 'Africa/Casablanca',
                        theme: 'light',
                        style: style === 'candlestick' ? '1' : style === 'line' ? '2' : '3',
                        locale: 'en',
                        toolbar_bg: '#f1f3f6',
                        enable_publishing: false,
                        allow_symbol_change: false,
                        hide_side_toolbar: false,
                        hide_legend: false,
                        save_image: false,
                        backgroundColor: 'rgba(255, 255, 255, 1)',
                        gridColor: 'rgba(240, 243, 250, 0)',
                        width: '100%',
                        height: '500',
                        studies: showIndicators ? [
                            'MAS@tv-basicstudies',
                            'RSI@tv-basicstudies',
                            'MACD@tv-basicstudies'
                        ] : [],
                        show_popup_button: true,
                        popup_width: '1000',
                        popup_height: '650',
                        volume: showVolume ? 'visible' : 'hidden'
                    })
                }
            }
            document.head.appendChild(script)

            return () => {
                if (script.parentNode) {
                    script.parentNode.removeChild(script)
                }
            }
        }
    }, [symbol, interval, style, showVolume, showIndicators])

    return (
        <div
            id={`tradingview_${symbol.replace(/[^a-zA-Z0-9]/g, '')}`}
            ref={container}
            className="w-full h-[500px]"
        />
    )
}

declare global {
    interface Window {
        TradingView: any
    }
}
