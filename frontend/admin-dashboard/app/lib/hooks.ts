'use client'

import useSWR from 'swr'
import { analyticsApi, beatsApi, jobsApi, marketingApi } from './api'

const fetcher = async (fn: () => Promise<any>) => {
  const res = await fn()
  return res.data
}

export function useDashboardStats() {
  return useSWR('dashboard-stats', () => fetcher(analyticsApi.dashboard), {
    refreshInterval: 30000,
    fallbackData: {
      total_beats: 0,
      generated_today: 0,
      revenue: 0,
      avg_quality: 0,
      queue_depth: 0,
      success_rate: 0,
    },
  })
}

export function useRecentBeats(limit = 10) {
  return useSWR(
    ['recent-beats', limit],
    () => fetcher(() => beatsApi.list({ limit, sort: '-created_at' })),
    { refreshInterval: 30000, fallbackData: { items: [] } }
  )
}

export function useQueueStatus() {
  return useSWR('queue-status', () => fetcher(jobsApi.queueStatus), {
    refreshInterval: 10000,
    fallbackData: { queued: 0, processing: 0, completed: 0, failed: 0 },
  })
}

export function useMarketingAnalytics() {
  return useSWR('marketing-analytics', () => fetcher(marketingApi.analytics), {
    refreshInterval: 60000,
    fallbackData: {
      total_views: 0,
      avg_ctr: 0,
      conversions: 0,
      videos_live: 0,
    },
  })
}
