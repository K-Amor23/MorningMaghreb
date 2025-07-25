import React, { useState, useMemo } from 'react'
import {
    FunnelIcon,
    MagnifyingGlassIcon,
    ArrowsUpDownIcon,
    XMarkIcon,
    AdjustmentsHorizontalIcon
} from '@heroicons/react/24/outline'

interface Company {
    ticker: string
    name: string
    sector: string
    market_cap_billion: number
    price: number
    change_1d_percent: number
    data_quality: 'Partial' | 'Complete'
}

interface CompanyFilterPanelProps {
    companies: Company[]
    onFilterChange: (filteredCompanies: Company[]) => void
    className?: string
}

interface FilterState {
    search: string
    sector: string
    marketCapRange: [number, number]
    priceRange: [number, number]
    dataQuality: string
    sortBy: string
    sortOrder: 'asc' | 'desc'
}

const CompanyFilterPanel: React.FC<CompanyFilterPanelProps> = ({
    companies,
    onFilterChange,
    className = ''
}) => {
    const [isOpen, setIsOpen] = useState(false)
    const [filters, setFilters] = useState<FilterState>({
        search: '',
        sector: '',
        marketCapRange: [0, 1000],
        priceRange: [0, 1000],
        dataQuality: '',
        sortBy: 'ticker',
        sortOrder: 'asc'
    })

    // Get unique sectors
    const sectors = useMemo(() => {
        const uniqueSectors = Array.from(new Set(companies.map(c => c.sector))).filter(Boolean)
        return uniqueSectors.sort()
    }, [companies])

    // Get market cap and price ranges
    const ranges = useMemo(() => {
        const marketCaps = companies.map(c => c.market_cap_billion).filter(Boolean)
        const prices = companies.map(c => c.price).filter(Boolean)

        return {
            marketCap: {
                min: Math.min(...marketCaps),
                max: Math.max(...marketCaps)
            },
            price: {
                min: Math.min(...prices),
                max: Math.max(...prices)
            }
        }
    }, [companies])

    // Apply filters and sorting
    const filteredCompanies = useMemo(() => {
        let filtered = [...companies]

        // Search filter
        if (filters.search) {
            const searchLower = filters.search.toLowerCase()
            filtered = filtered.filter(company =>
                company.ticker.toLowerCase().includes(searchLower) ||
                company.name.toLowerCase().includes(searchLower)
            )
        }

        // Sector filter
        if (filters.sector) {
            filtered = filtered.filter(company => company.sector === filters.sector)
        }

        // Market cap range filter
        filtered = filtered.filter(company =>
            company.market_cap_billion >= filters.marketCapRange[0] &&
            company.market_cap_billion <= filters.marketCapRange[1]
        )

        // Price range filter
        filtered = filtered.filter(company =>
            company.price >= filters.priceRange[0] &&
            company.price <= filters.priceRange[1]
        )

        // Data quality filter
        if (filters.dataQuality) {
            filtered = filtered.filter(company => company.data_quality === filters.dataQuality)
        }

        // Sorting
        filtered.sort((a, b) => {
            let aValue: any
            let bValue: any

            switch (filters.sortBy) {
                case 'ticker':
                    aValue = a.ticker
                    bValue = b.ticker
                    break
                case 'name':
                    aValue = a.name
                    bValue = b.name
                    break
                case 'sector':
                    aValue = a.sector
                    bValue = b.sector
                    break
                case 'market_cap':
                    aValue = a.market_cap_billion
                    bValue = b.market_cap_billion
                    break
                case 'price':
                    aValue = a.price
                    bValue = b.price
                    break
                case 'change_1d':
                    aValue = a.change_1d_percent
                    bValue = b.change_1d_percent
                    break
                case 'data_quality':
                    aValue = a.data_quality
                    bValue = b.data_quality
                    break
                default:
                    aValue = a.ticker
                    bValue = b.ticker
            }

            if (typeof aValue === 'string') {
                aValue = aValue.toLowerCase()
                bValue = bValue.toLowerCase()
            }

            if (filters.sortOrder === 'asc') {
                return aValue > bValue ? 1 : -1
            } else {
                return aValue < bValue ? 1 : -1
            }
        })

        return filtered
    }, [companies, filters])

    // Update parent component when filters change
    React.useEffect(() => {
        onFilterChange(filteredCompanies)
    }, [filteredCompanies, onFilterChange])

    const clearFilters = () => {
        setFilters({
            search: '',
            sector: '',
            marketCapRange: [ranges.marketCap.min, ranges.marketCap.max],
            priceRange: [ranges.price.min, ranges.price.max],
            dataQuality: '',
            sortBy: 'ticker',
            sortOrder: 'asc'
        })
    }

    const hasActiveFilters = filters.search || filters.sector || filters.dataQuality ||
        filters.marketCapRange[0] !== ranges.marketCap.min ||
        filters.marketCapRange[1] !== ranges.marketCap.max ||
        filters.priceRange[0] !== ranges.price.min ||
        filters.priceRange[1] !== ranges.price.max

    return (
        <div className={`bg-white border border-gray-200 rounded-lg shadow-sm ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
                <div className="flex items-center gap-2">
                    <AdjustmentsHorizontalIcon className="w-5 h-5 text-gray-600" />
                    <h3 className="text-lg font-semibold text-gray-900">Filter & Sort Companies</h3>
                    {hasActiveFilters && (
                        <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                            {filteredCompanies.length} of {companies.length}
                        </span>
                    )}
                </div>
                <div className="flex items-center gap-2">
                    {hasActiveFilters && (
                        <button
                            onClick={clearFilters}
                            className="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors"
                        >
                            <XMarkIcon className="w-4 h-4" />
                            Clear
                        </button>
                    )}
                    <button
                        onClick={() => setIsOpen(!isOpen)}
                        className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
                    >
                        <FunnelIcon className="w-4 h-4" />
                        {isOpen ? 'Hide' : 'Show'} Filters
                    </button>
                </div>
            </div>

            {/* Filter Panel */}
            {isOpen && (
                <div className="p-4 space-y-6">
                    {/* Search */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Search Companies
                        </label>
                        <div className="relative">
                            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Search by ticker or company name..."
                                value={filters.search}
                                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>
                    </div>

                    {/* Sector Filter */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Sector
                        </label>
                        <select
                            value={filters.sector}
                            onChange={(e) => setFilters(prev => ({ ...prev, sector: e.target.value }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                            <option value="">All Sectors</option>
                            {sectors.map(sector => (
                                <option key={sector} value={sector}>{sector}</option>
                            ))}
                        </select>
                    </div>

                    {/* Market Cap Range */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Market Cap (Billion MAD)
                        </label>
                        <div className="flex items-center gap-4">
                            <input
                                type="number"
                                placeholder="Min"
                                value={filters.marketCapRange[0]}
                                onChange={(e) => setFilters(prev => ({
                                    ...prev,
                                    marketCapRange: [parseFloat(e.target.value) || 0, prev.marketCapRange[1]]
                                }))}
                                className="w-1/2 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            />
                            <span className="text-gray-500">to</span>
                            <input
                                type="number"
                                placeholder="Max"
                                value={filters.marketCapRange[1]}
                                onChange={(e) => setFilters(prev => ({
                                    ...prev,
                                    marketCapRange: [prev.marketCapRange[0], parseFloat(e.target.value) || 1000]
                                }))}
                                className="w-1/2 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>
                    </div>

                    {/* Price Range */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Price Range (MAD)
                        </label>
                        <div className="flex items-center gap-4">
                            <input
                                type="number"
                                placeholder="Min"
                                value={filters.priceRange[0]}
                                onChange={(e) => setFilters(prev => ({
                                    ...prev,
                                    priceRange: [parseFloat(e.target.value) || 0, prev.priceRange[1]]
                                }))}
                                className="w-1/2 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            />
                            <span className="text-gray-500">to</span>
                            <input
                                type="number"
                                placeholder="Max"
                                value={filters.priceRange[1]}
                                onChange={(e) => setFilters(prev => ({
                                    ...prev,
                                    priceRange: [prev.priceRange[0], parseFloat(e.target.value) || 1000]
                                }))}
                                className="w-1/2 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>
                    </div>

                    {/* Data Quality Filter */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Data Quality
                        </label>
                        <select
                            value={filters.dataQuality}
                            onChange={(e) => setFilters(prev => ({ ...prev, dataQuality: e.target.value }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                            <option value="">All Quality Levels</option>
                            <option value="Complete">Complete Data</option>
                            <option value="Partial">Partial Data</option>
                        </select>
                    </div>

                    {/* Sorting */}
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Sort By
                            </label>
                            <select
                                value={filters.sortBy}
                                onChange={(e) => setFilters(prev => ({ ...prev, sortBy: e.target.value }))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option value="ticker">Ticker</option>
                                <option value="name">Company Name</option>
                                <option value="sector">Sector</option>
                                <option value="market_cap">Market Cap</option>
                                <option value="price">Price</option>
                                <option value="change_1d">1-Day Change</option>
                                <option value="data_quality">Data Quality</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Order
                            </label>
                            <select
                                value={filters.sortOrder}
                                onChange={(e) => setFilters(prev => ({ ...prev, sortOrder: e.target.value as 'asc' | 'desc' }))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option value="asc">Ascending</option>
                                <option value="desc">Descending</option>
                            </select>
                        </div>
                    </div>

                    {/* Active Filters Summary */}
                    {hasActiveFilters && (
                        <div className="pt-4 border-t border-gray-200">
                            <h4 className="text-sm font-medium text-gray-700 mb-2">Active Filters:</h4>
                            <div className="flex flex-wrap gap-2">
                                {filters.search && (
                                    <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                                        Search: "{filters.search}"
                                    </span>
                                )}
                                {filters.sector && (
                                    <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                                        Sector: {filters.sector}
                                    </span>
                                )}
                                {filters.dataQuality && (
                                    <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                                        Quality: {filters.dataQuality}
                                    </span>
                                )}
                                <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                                    Sort: {filters.sortBy} ({filters.sortOrder})
                                </span>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}

export default CompanyFilterPanel 