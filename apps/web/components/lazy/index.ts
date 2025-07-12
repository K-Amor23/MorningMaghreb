import dynamic from 'next/dynamic'

// Lazy load heavy components
export const LazyPortfolioHoldings = dynamic(() => import('../PortfolioHoldings'), { ssr: false })
export const LazyFinancialChart = dynamic(() => import('../company/FinancialChart'), { ssr: false })
export const LazyPriceAlerts = dynamic(() => import('../PriceAlerts'), { ssr: false })
export const LazyTradingInterface = dynamic(() => import('../paper-trading/TradingInterface'), { ssr: false })
export const LazyAdvancedFeatures = dynamic(() => import('../advanced/CompanyComparison'), { ssr: false }) 