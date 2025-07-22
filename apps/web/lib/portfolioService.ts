// Portfolio service for managing user portfolios

export interface PortfolioHolding {
  id?: string
  ticker: string
  name: string
  quantity: number
  purchase_price: number
  purchase_date?: string
  notes?: string
  current_price?: number
  current_value?: number
  total_gain_loss?: number
  total_gain_loss_percent?: number
}

export interface PortfolioSummary {
  total_value: number
  total_cost: number
  total_gain_loss: number
  total_gain_loss_percent: number
  holdings_count: number
  last_updated: string
}

export interface CreatePortfolioRequest {
  name: string
  description?: string
}

export interface UpdateHoldingRequest {
  quantity?: number
  purchase_price?: number
  purchase_date?: string
  notes?: string
}

export interface AddHoldingRequest {
  ticker: string
  quantity: number
  purchase_price: number
  purchase_date?: string
  notes?: string
}

class PortfolioService {
  private baseUrl = '' // Use frontend API routes (no double /api)

  private async getAuthHeaders() {
    // For now, return basic headers since we're using mock data
    // In production, this would include proper authentication
    return {
      'Content-Type': 'application/json',
    }
  }

  async getUserPortfolios() {
    try {
      const headers = await this.getAuthHeaders()
      const response = await fetch(`/api/portfolio/`, {
        headers,
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch portfolios')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error fetching portfolios:', error)
      throw error
    }
  }

  async createPortfolio(request: CreatePortfolioRequest) {
    try {
      const headers = await this.getAuthHeaders()
      const response = await fetch(`/api/portfolio/`, {
        method: 'POST',
        headers,
        body: JSON.stringify(request),
      })
      
      if (!response.ok) {
        throw new Error('Failed to create portfolio')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error creating portfolio:', error)
      throw error
    }
  }

  async getPortfolioHoldings(portfolioId: string): Promise<PortfolioHolding[]> {
    try {
      const headers = await this.getAuthHeaders()
      const response = await fetch(`/api/portfolio/${portfolioId}/holdings`, {
        headers,
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch holdings')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error fetching holdings:', error)
      throw error
    }
  }

  async getPortfolioSummary(portfolioId: string): Promise<PortfolioSummary> {
    try {
      const headers = await this.getAuthHeaders()
      const response = await fetch(`/api/portfolio/${portfolioId}/summary`, {
        headers,
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch portfolio summary')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error fetching portfolio summary:', error)
      throw error
    }
  }

  async addHolding(portfolioId: string, request: AddHoldingRequest): Promise<PortfolioHolding> {
    try {
      const headers = await this.getAuthHeaders()
      const response = await fetch(`/api/portfolio/${portfolioId}/holdings`, {
        method: 'POST',
        headers,
        body: JSON.stringify(request),
      })
      
      if (!response.ok) {
        throw new Error('Failed to add holding')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error adding holding:', error)
      throw error
    }
  }

  async updateHolding(
    portfolioId: string, 
    holdingId: string, 
    request: UpdateHoldingRequest
  ): Promise<PortfolioHolding> {
    try {
      const headers = await this.getAuthHeaders()
      const response = await fetch(`/api/portfolio/${portfolioId}/holdings/${holdingId}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(request),
      })
      
      if (!response.ok) {
        throw new Error('Failed to update holding')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error updating holding:', error)
      throw error
    }
  }

  async deleteHolding(portfolioId: string, holdingId: string) {
    try {
      const headers = await this.getAuthHeaders()
      const response = await fetch(`/api/portfolio/${portfolioId}/holdings/${holdingId}`, {
        method: 'DELETE',
        headers,
      })
      
      if (!response.ok) {
        throw new Error('Failed to delete holding')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error deleting holding:', error)
      throw error
    }
  }

  async adjustHoldingQuantity(portfolioId: string, holdingId: string, adjustment: number) {
    try {
      const headers = await this.getAuthHeaders()
      const response = await fetch(`/api/portfolio/${portfolioId}/holdings/${holdingId}/adjust?adjustment=${adjustment}`, {
        method: 'POST',
        headers,
      })
      
      if (!response.ok) {
        throw new Error('Failed to adjust holding quantity')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error adjusting holding quantity:', error)
      throw error
    }
  }

  async getPortfolioPerformance(portfolioId: string, period: string = '1M') {
    try {
      const headers = await this.getAuthHeaders()
      const response = await fetch(`/api/portfolio/${portfolioId}/performance?period=${period}`, {
        headers,
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch portfolio performance')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error fetching portfolio performance:', error)
      throw error
    }
  }
}

export const portfolioService = new PortfolioService() 