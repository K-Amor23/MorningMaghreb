import React, { useState, useCallback } from 'react'
import { DragDropContext, Droppable, Draggable, DropResult } from 'react-beautiful-dnd'
import { PlusIcon, XMarkIcon, Cog6ToothIcon } from '@heroicons/react/24/outline'
import { useLocalStorage } from '@/lib/useClientOnly'
import { LazyPortfolioHoldings, LazyFinancialChart, LazyPriceAlerts } from './lazy'
import useSWR from 'swr'
import { fetcher } from '@/lib/api'

interface Widget {
  id: string
  type: string
  title: string
  size: 'small' | 'medium' | 'large'
  position: number
  config?: Record<string, any>
}

interface DashboardConfig {
  widgets: Widget[]
  layout: 'grid' | 'list'
  theme: 'light' | 'dark'
}

const DEFAULT_WIDGETS: Widget[] = [
  {
    id: 'market-overview',
    type: 'market-overview',
    title: 'Market Overview',
    size: 'large',
    position: 0
  },
  {
    id: 'portfolio-summary',
    type: 'portfolio-summary',
    title: 'Portfolio Summary',
    size: 'medium',
    position: 1
  },
  {
    id: 'watchlist',
    type: 'watchlist',
    title: 'Watchlist',
    size: 'medium',
    position: 2
  },
  {
    id: 'news-feed',
    type: 'news-feed',
    title: 'Latest News',
    size: 'small',
    position: 3
  }
]

const AVAILABLE_WIDGETS = [
  { type: 'market-overview', title: 'Market Overview', description: 'Real-time market data and indices' },
  { type: 'portfolio-summary', title: 'Portfolio Summary', description: 'Your portfolio performance and holdings' },
  { type: 'watchlist', title: 'Watchlist', description: 'Track your favorite stocks' },
  { type: 'news-feed', title: 'Latest News', description: 'Financial news and updates' },
  { type: 'price-alerts', title: 'Price Alerts', description: 'Manage your price alerts' },
  { type: 'trading-activity', title: 'Trading Activity', description: 'Recent trading activity and orders' },
  { type: 'economic-indicators', title: 'Economic Indicators', description: 'Key economic data and trends' },
  { type: 'sentiment-analysis', title: 'Market Sentiment', description: 'Market sentiment and social indicators' }
]

export default function CustomizableDashboard() {
  const [dashboardConfig, setDashboardConfig] = useLocalStorage<DashboardConfig>('dashboard-config', {
    widgets: DEFAULT_WIDGETS,
    layout: 'grid',
    theme: 'light'
  })
  const [isEditing, setIsEditing] = useState(false)
  const [showWidgetSelector, setShowWidgetSelector] = useState(false)

  // Save dashboard config to localStorage
  const saveDashboardConfig = useCallback((config: DashboardConfig) => {
    setDashboardConfig(config)
  }, [setDashboardConfig])

  // Handle drag and drop
  const handleDragEnd = useCallback((result: DropResult) => {
    if (!result.destination) return

    const widgets = Array.from(dashboardConfig.widgets)
    const [reorderedWidget] = widgets.splice(result.source.index, 1)
    widgets.splice(result.destination.index, 0, reorderedWidget)

    // Update positions
    const updatedWidgets = widgets.map((widget, index) => ({
      ...widget,
      position: index
    }))

    saveDashboardConfig({
      ...dashboardConfig,
      widgets: updatedWidgets
    })
  }, [dashboardConfig, saveDashboardConfig])

  // Add widget
  const addWidget = useCallback((widgetType: string) => {
    const widgetInfo = AVAILABLE_WIDGETS.find(w => w.type === widgetType)
    if (!widgetInfo) return

    const newWidget: Widget = {
      id: `${widgetType}-${Date.now()}`,
      type: widgetType,
      title: widgetInfo.title,
      size: 'medium',
      position: dashboardConfig.widgets.length
    }

    const updatedWidgets = [...dashboardConfig.widgets, newWidget]
    saveDashboardConfig({
      ...dashboardConfig,
      widgets: updatedWidgets
    })

    setShowWidgetSelector(false)
  }, [dashboardConfig, saveDashboardConfig])

  // Remove widget
  const removeWidget = useCallback((widgetId: string) => {
    const updatedWidgets = dashboardConfig.widgets
      .filter(w => w.id !== widgetId)
      .map((widget, index) => ({
        ...widget,
        position: index
      }))

    saveDashboardConfig({
      ...dashboardConfig,
      widgets: updatedWidgets
    })
  }, [dashboardConfig, saveDashboardConfig])

  // Resize widget
  const resizeWidget = useCallback((widgetId: string, newSize: Widget['size']) => {
    const updatedWidgets = dashboardConfig.widgets.map(widget =>
      widget.id === widgetId ? { ...widget, size: newSize } : widget
    )

    saveDashboardConfig({
      ...dashboardConfig,
      widgets: updatedWidgets
    })
  }, [dashboardConfig, saveDashboardConfig])

  // Render widget content
  const renderWidget = useCallback((widget: Widget) => {
    const commonProps = {
      className: 'h-full',
      'data-widget-id': widget.id
    }

    switch (widget.type) {
      case 'market-overview':
        return <MarketOverviewWidget {...commonProps} />
      case 'portfolio-summary':
        return <PortfolioSummaryWidget {...commonProps} />
      case 'watchlist':
        return <WatchlistWidget {...commonProps} />
      case 'news-feed':
        return <NewsFeedWidget {...commonProps} />
      case 'price-alerts':
        return <div className="p-4 text-gray-500">Price Alerts Widget</div>
      case 'trading-activity':
        return <TradingActivityWidget {...commonProps} />
      case 'economic-indicators':
        return <EconomicIndicatorsWidget {...commonProps} />
      case 'sentiment-analysis':
        return <SentimentAnalysisWidget {...commonProps} />
      default:
        return <div className="p-4 text-gray-500">Widget not found</div>
    }
  }, [])

  const getWidgetSizeClasses = (size: Widget['size']) => {
    switch (size) {
      case 'small':
        return 'col-span-1 row-span-1'
      case 'medium':
        return 'col-span-2 row-span-1'
      case 'large':
        return 'col-span-2 row-span-2'
      default:
        return 'col-span-1 row-span-1'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Dashboard Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              Dashboard
            </h1>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowWidgetSelector(!showWidgetSelector)}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-casablanca-blue dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:hover:bg-gray-600"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Add Widget
              </button>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className={`inline-flex items-center px-3 py-2 border shadow-sm text-sm leading-4 font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-casablanca-blue ${isEditing
                  ? 'border-casablanca-blue text-casablanca-blue bg-casablanca-blue bg-opacity-10'
                  : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:hover:bg-gray-600'
                  }`}
              >
                <Cog6ToothIcon className="h-4 w-4 mr-2" />
                {isEditing ? 'Done' : 'Edit'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Widget Selector */}
      {showWidgetSelector && (
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
          <div className="max-w-7xl mx-auto">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Add Widget
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {AVAILABLE_WIDGETS.map(widget => (
                <button
                  key={widget.type}
                  onClick={() => addWidget(widget.type)}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-casablanca-blue hover:bg-casablanca-blue hover:bg-opacity-5 transition-colors"
                >
                  <h4 className="font-medium text-gray-900 dark:text-white">{widget.title}</h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{widget.description}</p>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Dashboard Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <DragDropContext onDragEnd={handleDragEnd}>
          <Droppable droppableId="dashboard">
            {(provided) => (
              <div
                {...provided.droppableProps}
                ref={provided.innerRef}
                className={`grid gap-6 ${dashboardConfig.layout === 'grid'
                  ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
                  : 'grid-cols-1'
                  }`}
              >
                {dashboardConfig.widgets.map((widget, index) => (
                  <Draggable key={widget.id} draggableId={widget.id} index={index}>
                    {(provided, snapshot) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        className={`${getWidgetSizeClasses(widget.size)} ${snapshot.isDragging ? 'opacity-50' : ''
                          }`}
                      >
                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 h-full">
                          {/* Widget Header */}
                          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                              {widget.title}
                            </h3>
                            {isEditing && (
                              <div className="flex items-center space-x-2">
                                <select
                                  value={widget.size}
                                  onChange={(e) => resizeWidget(widget.id, e.target.value as Widget['size'])}
                                  className="text-sm border border-gray-300 rounded px-2 py-1 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                >
                                  <option value="small">Small</option>
                                  <option value="medium">Medium</option>
                                  <option value="large">Large</option>
                                </select>
                                <button
                                  onClick={() => removeWidget(widget.id)}
                                  className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                                  aria-label="Remove widget"
                                >
                                  <XMarkIcon className="h-4 w-4" />
                                </button>
                              </div>
                            )}
                          </div>

                          {/* Widget Content */}
                          <div className="p-4 h-full overflow-auto">
                            {renderWidget(widget)}
                          </div>
                        </div>
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>
      </div>
    </div>
  )
}

// Widget Components
const MarketOverviewWidget = (props: any) => (
  <div {...props}>
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900 dark:text-white">MASI</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">Morocco All Shares</div>
          <div className="text-lg font-semibold text-green-600">12,345.67</div>
          <div className="text-sm text-green-600">+1.23%</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900 dark:text-white">MADEX</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">Most Active Shares</div>
          <div className="text-lg font-semibold text-red-600">10,234.56</div>
          <div className="text-sm text-red-600">-0.45%</div>
        </div>
      </div>
    </div>
  </div>
)

const PortfolioSummaryWidget = (props: any) => (
  <div {...props}>
    <div className="space-y-4">
      <div className="text-center">
        <div className="text-3xl font-bold text-gray-900 dark:text-white">$125,430</div>
        <div className="text-sm text-gray-500 dark:text-gray-400">Total Value</div>
        <div className="text-lg font-semibold text-green-600">+$2,340 (1.89%)</div>
      </div>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <div className="text-gray-500 dark:text-gray-400">Today's Change</div>
          <div className="font-semibold text-green-600">+$1,234</div>
        </div>
        <div>
          <div className="text-gray-500 dark:text-gray-400">Holdings</div>
          <div className="font-semibold text-gray-900 dark:text-white">12</div>
        </div>
      </div>
    </div>
  </div>
)

const WatchlistWidget = (props: any) => (
  <div {...props}>
    <div className="space-y-2">
      {['ATW', 'CIH', 'BMCE', 'ATL'].map(ticker => (
        <div key={ticker} className="flex items-center justify-between">
          <div>
            <div className="font-medium text-gray-900 dark:text-white">{ticker}</div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Company Name</div>
          </div>
          <div className="text-right">
            <div className="font-medium text-gray-900 dark:text-white">$45.67</div>
            <div className="text-sm text-green-600">+2.34%</div>
          </div>
        </div>
      ))}
    </div>
  </div>
)

const NewsFeedWidget = (props: any) => (
  <div {...props}>
    <div className="space-y-3">
      {[1, 2, 3].map(i => (
        <div key={i} className="border-b border-gray-200 dark:border-gray-700 pb-2 last:border-b-0">
          <div className="text-sm font-medium text-gray-900 dark:text-white line-clamp-2">
            Market Update: Moroccan Stocks Show Mixed Performance
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">2 hours ago</div>
        </div>
      ))}
    </div>
  </div>
)

const TradingActivityWidget = (props: any) => (
  <div {...props}>
    <div className="space-y-2">
      {[1, 2, 3].map(i => (
        <div key={i} className="flex items-center justify-between text-sm">
          <div>
            <div className="font-medium text-gray-900 dark:text-white">Buy ATW</div>
            <div className="text-gray-500 dark:text-gray-400">100 shares @ $45.67</div>
          </div>
          <div className="text-right">
            <div className="text-gray-500 dark:text-gray-400">Today</div>
            <div className="text-green-600">Filled</div>
          </div>
        </div>
      ))}
    </div>
  </div>
)

const EconomicIndicatorsWidget = (props: any) => (
  <div {...props}>
    <div className="space-y-3">
      {[
        { name: 'Inflation Rate', value: '2.1%', change: '+0.1%' },
        { name: 'GDP Growth', value: '3.2%', change: '+0.3%' },
        { name: 'Unemployment', value: '9.8%', change: '-0.2%' }
      ].map(indicator => (
        <div key={indicator.name} className="flex items-center justify-between">
          <div>
            <div className="text-sm font-medium text-gray-900 dark:text-white">{indicator.name}</div>
            <div className="text-xs text-gray-500 dark:text-gray-400">{indicator.change}</div>
          </div>
          <div className="text-lg font-semibold text-gray-900 dark:text-white">{indicator.value}</div>
        </div>
      ))}
    </div>
  </div>
)

const SentimentAnalysisWidget = (props: any) => (
  <div {...props}>
    <div className="space-y-3">
      <div className="text-center">
        <div className="text-2xl font-bold text-gray-900 dark:text-white">Bullish</div>
        <div className="text-sm text-gray-500 dark:text-gray-400">Market Sentiment</div>
      </div>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="text-center">
          <div className="text-lg font-semibold text-green-600">65%</div>
          <div className="text-gray-500 dark:text-gray-400">Positive</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-semibold text-red-600">35%</div>
          <div className="text-gray-500 dark:text-gray-400">Negative</div>
        </div>
      </div>
    </div>
  </div>
) 