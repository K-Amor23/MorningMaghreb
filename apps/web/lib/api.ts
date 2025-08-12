import axios from 'axios'
// import { BaseApiService } from '@casablanca-insight/shared'

// Create axios instance
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available (but don't require it for testing)
    const token = localStorage.getItem('supabase.auth.token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access - but don't redirect for testing
      console.warn('Unauthorized access - continuing without auth for testing')
    }
    return Promise.reject(error)
  }
)

// SWR fetcher function
export const fetcher = (url: string) => api.get(url).then((res) => res.data)

// Temporary API service without shared package
export const apiService = {
  get: (url: string) => api.get(url).then((res) => res.data),
  post: (url: string, data: any) => api.post(url, data).then((res) => res.data),
  put: (url: string, data: any) => api.put(url, data).then((res) => res.data),
  delete: (url: string) => api.delete(url).then((res) => res.data),

  // Sentiment methods (temporary implementation)
  getSentimentAggregate: async (ticker: string) => {
    return api.get(`/sentiment/aggregate/${ticker}`).then((res) => res.data)
  },
  getMySentimentVotes: async () => {
    return api.get('/sentiment/my-votes').then((res) => res.data)
  },
  voteSentiment: async (vote: any) => {
    return api.post('/sentiment/vote', vote).then((res) => res.data)
  }
}

export default api 