/** API client for the admin dashboard. */

import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ─── Beats ─────────────────────────────────────────────────────────

export const beatsApi = {
  list: (params?: Record<string, any>) => api.get('/beats', { params }),
  get: (id: string) => api.get(`/beats/${id}`),
  generate: (data: any) => api.post('/beats/generate', data),
  batchGenerate: (data: any) => api.post('/beats/batch-generate', data),
  update: (id: string, data: any) => api.patch(`/beats/${id}`, data),
  delete: (id: string) => api.delete(`/beats/${id}`),
  approve: (id: string) => api.post(`/beats/${id}/approve`),
  reject: (id: string, reason?: string) => api.post(`/beats/${id}/reject`, { reason }),
  download: (id: string, format: string) => api.get(`/beats/${id}/download/${format}`),
  preview: (id: string) => api.get(`/beats/${id}/preview`),
}

// ─── Genres ────────────────────────────────────────────────────────

export const genresApi = {
  list: () => api.get('/genres'),
  get: (id: string) => api.get(`/genres/${id}`),
  trends: (id: string) => api.get(`/genres/${id}/trends`),
}

// ─── Jobs ──────────────────────────────────────────────────────────

export const jobsApi = {
  list: (params?: Record<string, any>) => api.get('/jobs', { params }),
  queueStatus: () => api.get('/jobs/queue-status'),
  workers: () => api.get('/jobs/workers'),
  retry: (id: string) => api.post(`/jobs/${id}/retry`),
  cancel: (id: string) => api.post(`/jobs/${id}/cancel`),
}

// ─── Analytics ─────────────────────────────────────────────────────

export const analyticsApi = {
  dashboard: () => api.get('/analytics/dashboard'),
  generation: (params?: Record<string, any>) => api.get('/analytics/generation', { params }),
  sales: (params?: Record<string, any>) => api.get('/analytics/sales', { params }),
  quality: () => api.get('/analytics/quality'),
  aiLearning: () => api.get('/analytics/ai-learning'),
}

// ─── Trends ────────────────────────────────────────────────────────

export const trendsApi = {
  current: (params?: Record<string, any>) => api.get('/trends/current', { params }),
  research: (keyword: string) => api.get('/trends/research', { params: { keyword } }),
  refresh: () => api.post('/trends/refresh'),
  profitableGenres: () => api.get('/trends/profitable-genres'),
}

// ─── Shopify ───────────────────────────────────────────────────────

export const shopifyApi = {
  sync: (beatId: string) => api.post('/shopify/sync', { beat_id: beatId }),
  batchSync: (params?: Record<string, any>) => api.post('/shopify/batch-sync', params),
  products: (params?: Record<string, any>) => api.get('/shopify/products', { params }),
  orders: (params?: Record<string, any>) => api.get('/shopify/orders', { params }),
}

// ─── Marketing ─────────────────────────────────────────────────────

export const marketingApi = {
  // Pipeline
  processBeat: (data: any) => api.post('/marketing/pipeline/process', data),
  batchProcess: (data: any) => api.post('/marketing/pipeline/batch', data),
  pipelineStats: () => api.get('/marketing/pipeline/stats'),
  
  // Video
  generateVideo: (data: any) => api.post('/marketing/video/generate', data),
  generateShorts: (data: any) => api.post('/marketing/video/shorts', data),
  
  // Thumbnails
  generateThumbnail: (data: any) => api.post('/marketing/thumbnail/generate', data),
  thumbnailABTest: (data: any) => api.post('/marketing/thumbnail/ab-test', data),
  
  // SEO
  generateSEO: (data: any) => api.post('/marketing/seo/generate', data),
  researchKeywords: (genre: string) => api.get('/marketing/seo/keywords', { params: { genre } }),
  
  // Upload
  uploadYouTube: (data: any) => api.post('/marketing/upload/youtube', data),
  uploadTikTok: (data: any) => api.post('/marketing/upload/tiktok', data),
  uploadInstagram: (data: any) => api.post('/marketing/upload/instagram', data),
  
  // Channels
  channels: () => api.get('/marketing/channels'),
  channelStats: () => api.get('/marketing/channels/stats'),
  assignBeat: (data: any) => api.post('/marketing/channels/assign', data),
  
  // Trends
  trends: (source?: string) => api.get('/marketing/trends', { params: { source } }),
  refreshTrends: () => api.post('/marketing/trends/refresh'),
  
  // Analytics
  analytics: () => api.get('/marketing/analytics'),
  ctrData: () => api.get('/marketing/analytics/ctr'),
  retentionData: () => api.get('/marketing/analytics/retention'),
  conversionData: () => api.get('/marketing/analytics/conversion'),
  topPerformers: (limit?: number) => api.get('/marketing/analytics/top-performers', { params: { limit } }),
  
  // Rules
  rules: () => api.get('/marketing/rules'),
  evaluateRules: (data: any) => api.post('/marketing/rules/evaluate', data),
  
  // Schedule
  schedule: () => api.get('/marketing/schedule'),
  readyPosts: () => api.get('/marketing/schedule/ready'),
}

// ─── Auth ──────────────────────────────────────────────────────────

export const authApi = {
  login: (data: { email: string; password: string }) => api.post('/auth/login', data),
  register: (data: { email: string; password: string; full_name?: string }) =>
    api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
}

export default api
