'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  TrendingUp,
  TrendingDown,
  Flame,
  Search,
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight,
  Music,
  Hash,
  Clock,
  Filter,
} from 'lucide-react'

interface Trend {
  id: string
  keyword: string
  genre: string
  platform: string
  growthRate: number
  volume: number
  competition: 'low' | 'medium' | 'high'
  sentiment: 'positive' | 'neutral' | 'negative'
  lastUpdated: string
  isNew: boolean
  related: string[]
}

const mockTrends: Trend[] = [
  {
    id: 't1',
    keyword: 'drill type beat 2026',
    genre: 'Drill',
    platform: 'youtube',
    growthRate: 145,
    volume: 52000,
    competition: 'medium',
    sentiment: 'positive',
    lastUpdated: '10 min ago',
    isNew: true,
    related: ['uk drill', 'ny drill', 'dark drill'],
  },
  {
    id: 't2',
    keyword: 'afrobeats instrumental',
    genre: 'Afrobeats',
    platform: 'youtube',
    growthRate: 89,
    volume: 38000,
    competition: 'low',
    sentiment: 'positive',
    lastUpdated: '25 min ago',
    isNew: true,
    related: ['amapiano', 'afrofusion', 'nigerian beats'],
  },
  {
    id: 't3',
    keyword: 'rage type beat',
    genre: 'Rage',
    platform: 'tiktok',
    growthRate: 234,
    volume: 89000,
    competition: 'high',
    sentiment: 'positive',
    lastUpdated: '1 hour ago',
    isNew: false,
    related: ['hyperpop', 'trap rage', 'destroy lonely type'],
  },
  {
    id: 't4',
    keyword: 'lofi study beats',
    genre: 'Lo-Fi',
    platform: 'youtube',
    growthRate: -12,
    volume: 120000,
    competition: 'high',
    sentiment: 'neutral',
    lastUpdated: '2 hours ago',
    isNew: false,
    related: ['chillhop', 'jazzhop', 'ambient'],
  },
  {
    id: 't5',
    keyword: 'jersey club remix',
    genre: 'Jersey Club',
    platform: 'tiktok',
    growthRate: 312,
    volume: 67000,
    competition: 'medium',
    sentiment: 'positive',
    lastUpdated: '30 min ago',
    isNew: true,
    related: ['baltimore club', 'philly club', 'baile funk'],
  },
  {
    id: 't6',
    keyword: 'pluggnb type beat',
    genre: 'Pluggnb',
    platform: 'youtube',
    growthRate: 67,
    volume: 24000,
    competition: 'low',
    sentiment: 'positive',
    lastUpdated: '3 hours ago',
    isNew: false,
    related: ['summrs type', 'autumn type', 'sofaygo type'],
  },
  {
    id: 't7',
    keyword: 'phonk drift',
    genre: 'Phonk',
    platform: 'tiktok',
    growthRate: 178,
    volume: 95000,
    competition: 'high',
    sentiment: 'positive',
    lastUpdated: '15 min ago',
    isNew: true,
    related: ['drift phonk', 'brazilian phonk', 'cowbell phonk'],
  },
  {
    id: 't8',
    keyword: 'emo rap beat',
    genre: 'Emo Rap',
    platform: 'youtube',
    growthRate: -8,
    volume: 45000,
    competition: 'medium',
    sentiment: 'neutral',
    lastUpdated: '4 hours ago',
    isNew: false,
    related: ['juice wrld type', 'xxxtentacion type', 'sad trap'],
  },
]

const competitionColors = {
  low: 'text-success',
  medium: 'text-accent',
  high: 'text-danger',
}

const competitionBg = {
  low: 'bg-success/10',
  medium: 'bg-accent/10',
  high: 'bg-danger/10',
}

export default function TrendMonitor() {
  const [trends, setTrends] = useState<Trend[]>(mockTrends)
  const [filter, setFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'growth' | 'volume'>('growth')
  const [isRefreshing, setIsRefreshing] = useState(false)

  const filteredTrends = trends
    .filter((t) => {
      const matchesFilter = filter === 'all' || t.platform === filter
      const matchesSearch =
        t.keyword.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.genre.toLowerCase().includes(searchQuery.toLowerCase())
      return matchesFilter && matchesSearch
    })
    .sort((a, b) => (sortBy === 'growth' ? b.growthRate - a.growthRate : b.volume - a.volume))

  const handleRefresh = () => {
    setIsRefreshing(true)
    setTimeout(() => setIsRefreshing(false), 1500)
  }

  const stats = {
    total: trends.length,
    trending: trends.filter((t) => t.growthRate > 50).length,
    declining: trends.filter((t) => t.growthRate < 0).length,
    new: trends.filter((t) => t.isNew).length,
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">Trend Monitor</h3>
          <p className="text-sm text-muted">Real-time trend detection across platforms</p>
        </div>
        <button
          onClick={handleRefresh}
          className={`flex items-center gap-2 px-4 py-2 bg-surface border border-border rounded-lg text-sm text-white hover:border-primary transition-colors ${
            isRefreshing ? 'opacity-70' : ''
          }`}
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-3">
        {[
          { label: 'Total Trends', value: stats.total, icon: Hash, color: 'text-primary' },
          { label: 'Hot', value: stats.trending, icon: Flame, color: 'text-danger' },
          { label: 'Declining', value: stats.declining, icon: TrendingDown, color: 'text-muted' },
          { label: 'New', value: stats.new, icon: Clock, color: 'text-success' },
        ].map((s) => {
          const Icon = s.icon
          return (
            <div key={s.label} className="bg-surface border border-border rounded-lg p-4 text-center">
              <Icon className={`w-5 h-5 ${s.color} mx-auto mb-2`} />
              <div className="text-xl font-bold text-white">{s.value}</div>
              <div className="text-xs text-muted">{s.label}</div>
            </div>
          )
        })}
      </div>

      {/* Search & Filter */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
          <input
            type="text"
            placeholder="Search trends..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-surface border border-border rounded-lg text-sm text-white placeholder:text-muted focus:outline-none focus:border-primary"
          />
        </div>
        <div className="flex items-center gap-2 bg-surface border border-border rounded-lg p-1">
          {[
            { id: 'all', label: 'All' },
            { id: 'youtube', label: 'YouTube' },
            { id: 'tiktok', label: 'TikTok' },
          ].map((f) => (
            <button
              key={f.id}
              onClick={() => setFilter(f.id)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                filter === f.id ? 'bg-primary text-white' : 'text-muted hover:text-white'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted">Sort:</span>
          <button
            onClick={() => setSortBy('growth')}
            className={`text-xs px-2 py-1 rounded ${
              sortBy === 'growth' ? 'bg-primary/20 text-primary' : 'text-muted'
            }`}
          >
            Growth
          </button>
          <button
            onClick={() => setSortBy('volume')}
            className={`text-xs px-2 py-1 rounded ${
              sortBy === 'volume' ? 'bg-primary/20 text-primary' : 'text-muted'
            }`}
          >
            Volume
          </button>
        </div>
      </div>

      {/* Trends Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <AnimatePresence>
          {filteredTrends.map((trend, i) => (
            <motion.div
              key={trend.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ delay: i * 0.03 }}
              className="bg-surface border border-border rounded-xl p-5 hover:border-primary/20 transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  {trend.isNew && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-success/20 text-success font-medium">
                      New
                    </span>
                  )}
                  <span className="text-xs px-2 py-0.5 rounded-full bg-surface-hover text-muted capitalize">
                    {trend.platform}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  {trend.growthRate >= 0 ? (
                    <ArrowUpRight className="w-4 h-4 text-success" />
                  ) : (
                    <ArrowDownRight className="w-4 h-4 text-danger" />
                  )}
                  <span
                    className={`text-sm font-bold ${
                      trend.growthRate >= 0 ? 'text-success' : 'text-danger'
                    }`}
                  >
                    {trend.growthRate >= 0 ? '+' : ''}
                    {trend.growthRate}%
                  </span>
                </div>
              </div>

              <h4 className="text-base font-semibold text-white mb-1">{trend.keyword}</h4>

              <div className="flex items-center gap-3 mb-3">
                <span className="text-xs text-muted flex items-center gap-1">
                  <Music className="w-3 h-3" />
                  {trend.genre}
                </span>
                <span className="text-xs text-muted">
                  {trend.volume >= 1000 ? `${(trend.volume / 1000).toFixed(0)}K` : trend.volume} searches
                </span>
                <span
                  className={`text-xs px-2 py-0.5 rounded-full ${competitionBg[trend.competition]} ${competitionColors[trend.competition]}`}
                >
                  {trend.competition} competition
                </span>
              </div>

              {/* Related Keywords */}
              <div className="flex flex-wrap gap-1.5">
                {trend.related.map((rel) => (
                  <span
                    key={rel}
                    className="text-xs px-2 py-1 rounded-md bg-surface-hover text-muted hover:text-white cursor-pointer transition-colors"
                  >
                    {rel}
                  </span>
                ))}
              </div>

              <div className="mt-3 pt-3 border-t border-border flex items-center justify-between">
                <span className="text-xs text-muted">{trend.lastUpdated}</span>
                <button className="text-xs text-primary hover:text-primary-hover font-medium transition-colors">
                  Generate Beat
                </button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {filteredTrends.length === 0 && (
        <div className="text-center py-12">
          <Filter className="w-8 h-8 text-muted mx-auto mb-3" />
          <p className="text-muted">No trends match your filters</p>
        </div>
      )}
    </div>
  )
}
