/**
 * Shared API Service for Casablanca Insights
 * 
 * This service provides consistent API access for both web and mobile applications.
 * All API calls are centralized here to ensure consistency across platforms.
 */

export interface Company {
    id: string;
    ticker: string;
    name: string;
    sector: string;
    industry: string;
    market_cap_billion: number;
    price: number;
    change_1d_percent: number;
    change_ytd_percent: number;
    size_category: string;
    sector_group: string;
    exchange: string;
    country: string;
    company_url: string;
    ir_url: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface PriceData {
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
    adjusted_close: number;
}

export interface CompanySummary {
    company: {
        ticker: string;
        name: string;
        sector: string;
        marketCap: number;
        currentPrice: number;
        priceChange: number;
        priceChangePercent: number;
        lastUpdated: string;
    };
    priceData: {
        last90Days: PriceData[];
        currentPrice: number;
        priceChange: number;
        priceChangePercent: number;
    };
    sentiment?: {
        bullishPercentage: number;
        bearishPercentage: number;
        neutralPercentage: number;
        totalVotes: number;
        averageConfidence: number;
    };
    metadata: {
        dataQuality: string;
        lastUpdated: string;
        sources: string[];
        recordCount: number;
    };
}

export interface TradingData {
    company: {
        ticker: string;
        name: string;
        sector: string;
        currentPrice: number;
        priceChange: number;
        priceChangePercent: number;
        lastUpdated: string;
    };
    priceData: {
        last90Days: PriceData[];
        currentPrice: number;
        priceChange: number;
        priceChangePercent: number;
    };
    sentiment?: {
        bullishPercentage: number;
        bearishPercentage: number;
        neutralPercentage: number;
        totalVotes: number;
        averageConfidence: number;
    };
    metadata: {
        dataQuality: string;
        lastUpdated: string;
        sources: string[];
        recordCount: number;
    };
}

export interface FinancialReport {
    id: string;
    title: string;
    type: string;
    date: string;
    year: string;
    quarter: string;
    url: string;
    filename: string;
    scrapedAt: string;
}

export interface ReportsData {
    company: {
        ticker: string;
        name: string;
        sector: string;
        irUrl: string;
    };
    reports: {
        all: FinancialReport[];
        byType: {
            annual_reports: FinancialReport[];
            quarterly_reports: FinancialReport[];
            financial_statements: FinancialReport[];
            earnings: FinancialReport[];
            other: FinancialReport[];
        };
        totalCount: number;
    };
    metadata: {
        lastUpdated: string;
        sources: string[];
        dataQuality: string;
    };
}

export interface NewsItem {
    id: string;
    headline: string;
    source: string;
    publishedAt: string;
    sentiment: string;
    sentimentScore: number;
    url: string;
    contentPreview: string;
}

export interface NewsData {
    company: {
        ticker: string;
        name: string;
        sector: string;
    };
    news: {
        items: NewsItem[];
        sentimentDistribution: {
            positive: number;
            negative: number;
            neutral: number;
            total: number;
        };
        totalCount: number;
    };
    sentiment?: {
        bullishPercentage: number;
        bearishPercentage: number;
        neutralPercentage: number;
        totalVotes: number;
        averageConfidence: number;
    };
    metadata: {
        lastUpdated: string;
        sources: string[];
        dataQuality: string;
        limit: number;
    };
}

export interface AnalyticsData {
    ticker: string;
    date: string;
    close_price: number;
    volume: number;
    sma_10: number;
    sma_30: number;
    ema_12: number;
    ema_26: number;
    rsi: number;
    macd_line: number;
    macd_signal: number;
    macd_histogram: number;
    bb_upper: number;
    bb_middle: number;
    bb_lower: number;
    volume_sma: number;
    pvt: number;
    obv: number;
    signal: string;
    signal_strength: number;
    computed_at: string;
    data_points: number;
}

export interface Watchlist {
    id: string;
    user_id: string;
    name: string;
    description: string;
    is_public: boolean;
    created_at: string;
    items: WatchlistItem[];
    item_count: number;
}

export interface WatchlistItem {
    id: string;
    ticker: string;
    company_name: string;
    sector: string;
    market_cap_billion: number;
    current_price: number;
    price_change_percent: number;
    added_at: string;
    notes: string;
    target_price: number;
}

export interface Alert {
    id: string;
    user_id: string;
    ticker: string;
    alert_type: string;
    condition_value: number;
    condition_operator: string;
    is_active: boolean;
    is_triggered: boolean;
    triggered_at: string;
    notification_method: string;
    created_at: string;
    company_name: string;
    sector: string;
    current_price: number;
    price_change_percent: number;
}

export interface DataQualityMetrics {
    company: {
        ticker: string;
        name: string;
        sector: string;
        dataQuality: string;
        completenessScore: number;
    };
    metrics: {
        ohlcv: {
            coverageDays: number;
            latestDate: string;
            status: string;
        };
        reports: {
            count: number;
            latestDate: string;
            types: string[];
            status: string;
        };
        news: {
            count7d: number;
            latestDate: string;
            sentimentDistribution: {
                positive: number;
                negative: number;
                neutral: number;
            };
            status: string;
        };
    };
    summary: {
        overallQuality: string;
        completenessScore: number;
        lastUpdated: string;
        recommendations: string[];
    };
}

export class CasablancaAPI {
    private baseUrl: string;

    constructor(baseUrl: string = 'http://localhost:3000/api') {
        this.baseUrl = baseUrl;
    }

    // Health check
    async healthCheck(): Promise<any> {
        return this.get('/health');
    }

    // Companies
    async getCompanies(): Promise<Company[]> {
        return this.get('/companies');
    }

    async getCompanySummary(ticker: string): Promise<CompanySummary> {
        return this.get(`/companies/${ticker}/summary`);
    }

    async getCompanyTrading(ticker: string): Promise<TradingData> {
        return this.get(`/companies/${ticker}/trading`);
    }

    async getCompanyReports(ticker: string): Promise<ReportsData> {
        return this.get(`/companies/${ticker}/reports`);
    }

    async getCompanyNews(ticker: string, limit: number = 10, sentiment?: string): Promise<NewsData> {
        const params = new URLSearchParams();
        params.append('limit', limit.toString());
        if (sentiment) params.append('sentiment', sentiment);
        return this.get(`/companies/${ticker}/news?${params.toString()}`);
    }

    async getCompanyAnalytics(ticker: string): Promise<AnalyticsData> {
        return this.get(`/companies/${ticker}/analytics`);
    }

    // Data Quality
    async getDataQuality(ticker?: string): Promise<DataQualityMetrics | any> {
        if (ticker) {
            return this.get(`/data-quality?ticker=${ticker}`);
        }
        return this.get('/data-quality');
    }

    // Watchlists
    async getWatchlists(userId: string): Promise<{ watchlists: Watchlist[]; total_watchlists: number; total_items: number }> {
        return this.get(`/watchlists?user_id=${userId}`);
    }

    async createWatchlist(userId: string, name: string, description?: string, isPublic: boolean = false): Promise<{ watchlist: Watchlist; message: string }> {
        return this.post('/watchlists', {
            user_id: userId,
            name,
            description,
            is_public: isPublic
        });
    }

    async getWatchlist(watchlistId: string, userId: string): Promise<{ watchlist: Watchlist }> {
        return this.get(`/watchlists/${watchlistId}?user_id=${userId}`);
    }

    async updateWatchlist(watchlistId: string, userId: string, updates: Partial<Watchlist>): Promise<{ watchlist: Watchlist; message: string }> {
        return this.put(`/watchlists/${watchlistId}`, {
            user_id: userId,
            ...updates
        });
    }

    async deleteWatchlist(watchlistId: string, userId: string): Promise<{ message: string }> {
        return this.delete(`/watchlists/${watchlistId}?user_id=${userId}`);
    }

    async getWatchlistItems(watchlistId: string, userId: string): Promise<{ items: WatchlistItem[]; total_items: number }> {
        return this.get(`/watchlists/${watchlistId}/items?user_id=${userId}`);
    }

    async addWatchlistItem(watchlistId: string, userId: string, ticker: string, notes?: string, targetPrice?: number): Promise<{ item: WatchlistItem; message: string }> {
        return this.post(`/watchlists/${watchlistId}/items`, {
            user_id: userId,
            ticker,
            notes,
            target_price: targetPrice
        });
    }

    // Alerts
    async getAlerts(userId: string, status: 'all' | 'active' | 'triggered' = 'all'): Promise<{ alerts: Alert[]; total_alerts: number; active_alerts: number; triggered_alerts: number }> {
        return this.get(`/alerts?user_id=${userId}&status=${status}`);
    }

    async createAlert(userId: string, ticker: string, alertType: string, conditionValue: number, conditionOperator: string = '=', notificationMethod: string = 'email', notificationUrl?: string): Promise<{ alert: Alert; message: string }> {
        return this.post('/alerts', {
            user_id: userId,
            ticker,
            alert_type: alertType,
            condition_value: conditionValue,
            condition_operator: conditionOperator,
            notification_method: notificationMethod,
            notification_url: notificationUrl
        });
    }

    // Search
    async searchCompanies(query: string): Promise<Company[]> {
        return this.get(`/search/companies?query=${encodeURIComponent(query)}`);
    }

    // Market data
    async getMarketQuotes(search?: string): Promise<any> {
        const params = search ? `?search=${encodeURIComponent(search)}` : '';
        return this.get(`/market-data/quotes${params}`);
    }

    // Private methods
    private async get(endpoint: string): Promise<any> {
        const response = await fetch(`${this.baseUrl}${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    private async post(endpoint: string, data: any): Promise<any> {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    private async put(endpoint: string, data: any): Promise<any> {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    private async delete(endpoint: string): Promise<any> {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'DELETE',
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }
}

// Export default instance
export const api = new CasablancaAPI();

// Export for use in different environments
export const createAPI = (baseUrl: string) => new CasablancaAPI(baseUrl); 