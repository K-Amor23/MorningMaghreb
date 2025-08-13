import { useEffect, useMemo, useRef, useState } from 'react'
import dynamic from 'next/dynamic'

// Lightweight-charts is client-only; import types lazily
const createChartDynamic = dynamic(async () => (await import('lightweight-charts')).createChart as any, { ssr: false }) as unknown as typeof import('lightweight-charts').createChart

export type Candle = { time: string; open: number; high: number; low: number; close: number; volume?: number }
export type LinePoint = { time: string; value: number }

type ChartStyle = 'line' | 'candlestick' | 'area' | 'bar' | 'ohlc' | 'heikin'
type Timeframe = '1D' | '5D' | '1M' | '6M' | '1Y' | '5Y' | 'Max'

export interface InteractiveChartProps {
  ticker: string
  candles?: Candle[]
    compareTickers?: string[]
    onLoadCompareData?: (ticker: string, timeframe: Timeframe) => Promise<Candle[] | LinePoint[]>
    corporateEvents?: { date: string; type: 'earnings' | 'dividend' | 'news'; label?: string }[]
    initialStyle?: ChartStyle
    onClose?: () => void
    dark?: boolean
}

function toLine(c: Candle[]): LinePoint[] {
    return c.map((k) => ({ time: k.time, value: k.close }))
}

function sma(data: LinePoint[], period: number): LinePoint[] {
    const out: LinePoint[] = []
    let sum = 0
    for (let i = 0; i < data.length; i++) {
        sum += data[i].value
        if (i >= period) sum -= data[i - period].value
        if (i >= period - 1) out.push({ time: data[i].time, value: sum / period })
    }
    return out
}

function ema(data: LinePoint[], period: number): LinePoint[] {
    const out: LinePoint[] = []
    const k = 2 / (period + 1)
    let prev = data[0]?.value || 0
    for (let i = 0; i < data.length; i++) {
        const val = i === 0 ? data[i].value : data[i].value * k + prev * (1 - k)
        out.push({ time: data[i].time, value: val })
        prev = val
    }
    return out
}

export default function InteractiveChart({ ticker, candles, compareTickers = [], onLoadCompareData, corporateEvents = [], initialStyle = 'candlestick', onClose, dark }: InteractiveChartProps) {
    const containerRef = useRef<HTMLDivElement>(null)
    const chartRef = useRef<any>(null)
    const mainSeriesRef = useRef<any>(null)
  const [chartReady, setChartReady] = useState(false)
  const [loadedCandles, setLoadedCandles] = useState<Candle[]>([])
    const [style, setStyle] = useState<ChartStyle>(initialStyle)
    const [timeframe, setTimeframe] = useState<Timeframe>('6M')
    const [showSMA, setShowSMA] = useState(true)
    const [smaLen, setSmaLen] = useState(20)
    const [showEMA, setShowEMA] = useState(false)
    const [emaLen, setEmaLen] = useState(50)
    const [showBB, setShowBB] = useState(false)
    const [compareData, setCompareData] = useState<Record<string, LinePoint[]>>({})

    // Filter candles by timeframe (basic implementation using last N days)
  const sourceCandles = (candles && candles.length > 0) ? candles : loadedCandles
  const filteredCandles = useMemo(() => {
        const map: Record<Timeframe, number> = { '1D': 1, '5D': 5, '1M': 22, '6M': 132, '1Y': 264, '5Y': 1320, 'Max': Number.MAX_SAFE_INTEGER }
        const take = map[timeframe]
    return take >= sourceCandles.length ? sourceCandles : sourceCandles.slice(-take)
  }, [sourceCandles, timeframe])

  // Load price candles if not provided
  useEffect(() => {
    let abort = false
    if (!candles || candles.length === 0) {
      ;(async () => {
        try {
          const r = await fetch(`/api/companies/${encodeURIComponent(ticker)}/trading?days=365`)
          if (!r.ok) return
          const d = await r.json()
          const arr = (d?.priceData?.last90Days || []) as Array<{ date: string; open: number; high: number; low: number; close: number; volume?: number }>
          const mapped: Candle[] = arr.map(p => ({ time: p.date, open: p.open, high: p.high, low: p.low, close: p.close, volume: p.volume }))
          if (!abort) setLoadedCandles(mapped)
        } catch {}
      })()
    }
    return () => { abort = true }
  }, [ticker, candles])

    useEffect(() => {
        if (!containerRef.current) return
        let disposed = false
            ; (async () => {
                const createChart = (await import('lightweight-charts')).createChart
                if (disposed) return
                const chart = createChart(containerRef.current!, {
                    layout: { background: { color: 'transparent' }, textColor: dark ? '#e5e7eb' : '#111827' },
                    rightPriceScale: { borderVisible: false },
                    timeScale: { borderVisible: false },
                    grid: { horzLines: { color: dark ? '#1f2937' : '#e5e7eb' }, vertLines: { color: dark ? '#1f2937' : '#e5e7eb' } },
                    crosshair: { mode: 1 },
                    autoSize: true,
                })
                chartRef.current = chart
                setChartReady(true)
            })()
        return () => {
            disposed = true
            if (chartRef.current) {
                chartRef.current.remove()
                chartRef.current = null
            }
        }
    }, [dark])

    // Render main series when chart ready or style/timeframe changes
    useEffect(() => {
        if (!chartReady || !chartRef.current) return
        // clear previous series
        chartRef.current.getSeries?.().forEach((s: any) => chartRef.current.removeSeries(s))
        let series: any
        const lwc = require('lightweight-charts') as typeof import('lightweight-charts')
        switch (style) {
            case 'line':
                series = chartRef.current.addLineSeries({ color: '#2563eb', lineWidth: 2 })
                series.setData(toLine(filteredCandles))
                break
            case 'area':
                series = chartRef.current.addAreaSeries({ lineColor: '#2563eb', topColor: 'rgba(37,99,235,0.3)', bottomColor: 'rgba(37,99,235,0.0)' })
                series.setData(toLine(filteredCandles))
                break
            case 'bar':
                series = chartRef.current.addBarSeries({ upColor: '#16a34a', downColor: '#dc2626' })
                series.setData(filteredCandles)
                break
      case 'ohlc':
        // Use bar series to emulate OHLC bars
        series = chartRef.current.addBarSeries({ upColor: '#16a34a', downColor: '#dc2626' })
        series.setData(filteredCandles)
        break
            case 'heikin': {
                // Simple Heikin Ashi transform
                const ha: Candle[] = []
                let prev: { open: number; close: number } | null = null
                for (const c of filteredCandles) {
                    const haClose: number = (c.open + c.high + c.low + c.close) / 4
                    const haOpen: number = prev ? (prev.open + prev.close) / 2 : (c.open + c.close) / 2
                    const haHigh: number = Math.max(c.high, haOpen, haClose)
                    const haLow: number = Math.min(c.low, haOpen, haClose)
                    ha.push({ time: c.time, open: haOpen, high: haHigh, low: haLow, close: haClose, volume: c.volume })
                    prev = { open: haOpen, close: haClose }
                }
                series = chartRef.current.addCandlestickSeries({ upColor: '#16a34a', downColor: '#dc2626', borderVisible: false, wickUpColor: '#16a34a', wickDownColor: '#dc2626' })
                series.setData(ha)
                break
            }
            default:
                series = chartRef.current.addCandlestickSeries({ upColor: '#16a34a', downColor: '#dc2626', borderVisible: false, wickUpColor: '#16a34a', wickDownColor: '#dc2626' })
                series.setData(filteredCandles)
        }
        mainSeriesRef.current = series

        // Indicators
        if (showSMA) {
            const data = toLine(filteredCandles)
            const s = chartRef.current.addLineSeries({ color: '#f59e0b', lineWidth: 1 })
            s.setData(sma(data, Math.max(2, smaLen)))
        }
        if (showEMA) {
            const data = toLine(filteredCandles)
            const s = chartRef.current.addLineSeries({ color: '#10b981', lineWidth: 1 })
            s.setData(ema(data, Math.max(2, emaLen)))
        }

        // Corporate events as markers
        if (corporateEvents?.length && mainSeriesRef.current?.setMarkers) {
            const markers = corporateEvents.map((e) => ({ time: e.date, position: 'aboveBar', color: e.type === 'earnings' ? '#0ea5e9' : e.type === 'dividend' ? '#f59e0b' : '#a855f7', shape: 'circle', text: e.label || e.type }))
            try { mainSeriesRef.current.setMarkers(markers) } catch { }
        }

        // Comparison overlays
        ; (async () => {
            if (!onLoadCompareData) return
            for (const ct of compareTickers) {
                try {
                    const d = await onLoadCompareData(ct, timeframe)
                    const lineData: LinePoint[] = Array.isArray(d) && 'value' in (d[0] || {}) ? (d as LinePoint[]) : toLine((d as Candle[]))
                    const s = chartRef.current.addLineSeries({ color: '#6b7280', lineWidth: 1 })
                    s.setData(lineData)
                    setCompareData((prev) => ({ ...prev, [ct]: lineData }))
                } catch { }
            }
        })()

        chartRef.current.timeScale().fitContent()
    }, [chartReady, style, timeframe, filteredCandles, showSMA, smaLen, showEMA, emaLen, corporateEvents, compareTickers, onLoadCompareData])

    return (
        <div className="fixed inset-0 bg-black/50 z-[400] flex items-center justify-center" onClick={onClose}>
            <div className="bg-white dark:bg-gray-900 rounded-lg w-[95vw] h-[85vh] shadow-xl" onClick={(e) => e.stopPropagation()}>
                {/* Toolbar */}
                <div className="p-3 border-b border-gray-200 dark:border-gray-700 flex flex-wrap items-center gap-3">
                    <div className="font-semibold text-gray-900 dark:text-white">{ticker} Interactive Chart</div>
                    <select value={style} onChange={(e) => setStyle(e.target.value as ChartStyle)} className="text-sm border rounded px-2 py-1 dark:bg-gray-800 dark:text-gray-100">
                        <option value="line">Line</option>
                        <option value="area">Area</option>
                        <option value="candlestick">Candlestick</option>
                        <option value="bar">Bar</option>
                        <option value="ohlc">OHLC</option>
                        <option value="heikin">Heikin Ashi</option>
                    </select>
                    <select value={timeframe} onChange={(e) => setTimeframe(e.target.value as Timeframe)} className="text-sm border rounded px-2 py-1 dark:bg-gray-800 dark:text-gray-100">
                        {(['1D', '5D', '1M', '6M', '1Y', '5Y', 'Max'] as Timeframe[]).map(tf => <option key={tf} value={tf}>{tf}</option>)}
                    </select>
                    <label className="text-sm flex items-center gap-1"><input type="checkbox" checked={showSMA} onChange={(e) => setShowSMA(e.target.checked)} /> SMA</label>
                    {showSMA && <input type="number" min={2} max={400} value={smaLen} onChange={(e) => setSmaLen(parseInt(e.target.value || '20', 10))} className="w-16 text-sm border rounded px-2 py-1 dark:bg-gray-800 dark:text-gray-100" />}
                    <label className="text-sm flex items-center gap-1"><input type="checkbox" checked={showEMA} onChange={(e) => setShowEMA(e.target.checked)} /> EMA</label>
                    {showEMA && <input type="number" min={2} max={400} value={emaLen} onChange={(e) => setEmaLen(parseInt(e.target.value || '50', 10))} className="w-16 text-sm border rounded px-2 py-1 dark:bg-gray-800 dark:text-gray-100" />}
                    <button onClick={onClose} className="ml-auto text-sm px-3 py-1 border rounded hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-800">Close</button>
                </div>

                {/* Chart container */}
                <div ref={containerRef} className="w-full h-[calc(85vh-56px)]" />
            </div>
        </div>
    )
}


