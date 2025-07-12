import { z } from 'zod'
import type {
  MarketData,
  MacroData,
  NewsItem,
  SentimentData,
  SentimentVote,
  PortfolioHolding,
  PortfolioSummary,
  CreatePortfolioRequest,
  UpdateHoldingRequest,
  AddHoldingRequest,
  ApiResponse,
  PaginatedResponse
} from '../types'

// Validation schemas
export const SentimentVoteSchema = z.object({
  ticker: z.string().min(1).max(10),
  sentiment: z.enum(['bullish', 'neutral', 'bearish']),
  confidence: z.number().min(1).max(5)
})

export const AddHoldingSchema = z.object({
  ticker: z.string().min(1).max(10),
  quantity: z.number().positive(),
  purchase_price: z.number().positive(),
  purchase_date: z.string().optional(),
  notes: z.string().optional()
})

// Base API service class
export abstract class BaseApiService {
  protected baseUrl: string
  protected getAuthHeaders: () => Promise<Record<string, string>>

  constructor(baseUrl: string, getAuthHeaders: () => Promise<Record<string, string>>) {
    this.baseUrl = baseUrl
    this.getAuthHeaders = getAuthHeaders
  }

  protected async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const headers = await this.getAuthHeaders()
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...headers,
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `API request failed: ${response.status}`)
    }

    return response.json()
  }

  // Market Data
  async getMarketData(): Promise<MarketData[]> {
    return this.request<MarketData[]>('/api/markets/quotes')
  }

  async getMacroData(): Promise<MacroData[]> {
    return this.request<MacroData[]>('/api/macro/indicators')
  }

  async getNews(): Promise<NewsItem[]> {
    return this.request<NewsItem[]>('/api/news')
  }

  // Sentiment
  async getSentimentAggregate(ticker: string): Promise<SentimentData> {
    return this.request<SentimentData>(`/api/sentiment/aggregate/${ticker}`)
  }

  async getMySentimentVotes(): Promise<SentimentVote[]> {
    return this.request<SentimentVote[]>('/api/sentiment/my-votes')
  }

  async voteSentiment(vote: SentimentVote): Promise<void> {
    const validatedVote = SentimentVoteSchema.parse(vote)
    return this.request<void>('/api/sentiment/vote', {
      method: 'POST',
      body: JSON.stringify(validatedVote),
    })
  }

  // Portfolio
  async getUserPortfolios(): Promise<PaginatedResponse<any>> {
    return this.request<PaginatedResponse<any>>('/api/portfolio/')
  }

  async createPortfolio(request: CreatePortfolioRequest): Promise<any> {
    return this.request<any>('/api/portfolio/', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getPortfolioHoldings(portfolioId: string): Promise<PortfolioHolding[]> {
    return this.request<PortfolioHolding[]>(`/api/portfolio/${portfolioId}/holdings`)
  }

  async getPortfolioSummary(portfolioId: string): Promise<PortfolioSummary> {
    return this.request<PortfolioSummary>(`/api/portfolio/${portfolioId}/summary`)
  }

  async addHolding(portfolioId: string, request: AddHoldingRequest): Promise<PortfolioHolding> {
    const validatedRequest = AddHoldingSchema.parse(request)
    return this.request<PortfolioHolding>(`/api/portfolio/${portfolioId}/holdings`, {
      method: 'POST',
      body: JSON.stringify(validatedRequest),
    })
  }

  async updateHolding(
    portfolioId: string,
    holdingId: string,
    request: UpdateHoldingRequest
  ): Promise<PortfolioHolding> {
    return this.request<PortfolioHolding>(`/api/portfolio/${portfolioId}/holdings/${holdingId}`, {
      method: 'PUT',
      body: JSON.stringify(request),
    })
  }

  async deleteHolding(portfolioId: string, holdingId: string): Promise<void> {
    return this.request<void>(`/api/portfolio/${portfolioId}/holdings/${holdingId}`, {
      method: 'DELETE',
    })
  }

  // Newsletter
  async signupNewsletter(email: string): Promise<ApiResponse<{ success: boolean }>> {
    return this.request<ApiResponse<{ success: boolean }>>('/api/newsletter/signup', {
      method: 'POST',
      body: JSON.stringify({ email }),
    })
  }

  // Paper Trading
  async getTradingAccounts(): Promise<any[]> {
    return this.request<any[]>('/api/paper-trading/accounts')
  }

  async getTradingPositions(accountId: string): Promise<any[]> {
    return this.request<any[]>(`/api/paper-trading/accounts/${accountId}/positions`)
  }

  async getTradingOrders(accountId: string): Promise<any[]> {
    return this.request<any[]>(`/api/paper-trading/accounts/${accountId}/orders`)
  }

  async placeTradeOrder(accountId: string, order: any): Promise<any> {
    return this.request<any>(`/api/paper-trading/accounts/${accountId}/orders`, {
      method: 'POST',
      body: JSON.stringify(order),
    })
  }
} 