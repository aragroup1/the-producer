'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import {
  TrendingUp,
  Eye,
  MousePointer,
  ShoppingCart,
  Youtube,
  Share2,
  Zap,
  Target,
} from 'lucide-react'

// Mock data - will be replaced with API calls
const ctrData = [
  { day: 'Mon', ctr: 4.2, impressions: 1200, clicks: 50 },
  { day: 'Tue', ctr: 5.1, impressions: 1500, clicks: 77 },
  { day: 'Wed', ctr: 3.8, impressions: 1100, clicks: 42 },
  { day: 'Thu', ctr: 6.2, impressions: 1800, clicks: 112 },
  { day: 'Fri', ctr: 7.5, impressions: 2000, clicks: 150 },
  { day: 'Sat', ctr: 5.8, impressions: 1600, clicks: 93 },
  { day: 'Sun', ctr: 4.9, impressions: 1400, clicks: 69 },
]

const retentionData = [
  { second: '0s', pct: 100 },
  { second: '5s', pct: 85 },
  { second: '10s', pct: 72 },
  { second: '15s', pct: 65 },
  { second: '30s', pct: 58 },
  { second: '60s', pct: 45 },
  { second: '90s', pct: 38 },
  { second: '120s', pct: 32 },
  { second: '180s', pct: 25 },
]

const conversionData = [
  { stage: 'Views', count: 15000, pct: 100 },
  { stage: 'Clicks', count: 825, pct: 5.5 },
  { stage: 'Cart', count: 165, pct: 1.1 },
  { stage: 'Purchase', count: 33, pct: 0.22 },
]

const platformData = [
  { name: 'YouTube', value: 45, color: '#ef4444' },
  { name: 'TikTok', value: 30, color: '#06b6d4' },
  { name: 'Instagram', value: 18, color: '#f59e0b' },
  { name: 'BeatStars', value: 5, color: '#8b5cf6' },
  { name: 'Airbit', value: 2, color: '#10b981' },
]

const abTestData = [
  { variant: 'A', impressions: 5000, ctr: 5.2, thumbnail: 'Neon Glow' },
  { variant: 'B', impressions: 5000, ctr: 6.8, thumbnail: 'Dark Vignette' },
  { variant: 'C', impressions: 3000, ctr: 4.1, thumbnail: 'Gradient Text' },
]

const stats = [
  {
    label: 'Total Views',
    value: '124.5K',
    change: '+12.3%',
    icon: Eye,
    color: 'text-primary',
    bg: 'bg-primary/10',
  },
  {
    label: 'Avg CTR',
    value: '5.5%',
    change: '+0.8%',
    icon: MousePointer,
    color: 'text-secondary',
    bg: 'bg-secondary/10',
  },
  {
    label: 'Conversions',
    value: '33',
    change: '+15.2%',
    icon: ShoppingCart,
    color: 'text-success',
    bg: 'bg-success/10',
  },
  {
    label: 'Videos Live',
    value: '47',
    change: '+3',
    icon: Youtube,
    color: 'text-danger',
    bg: 'bg-danger/10',
  },
]

export default function MarketingDashboard() {
  const [timeRange, setTimeRange] = useState('7d')
  const [activeMetric, setActiveMetric] = useState('ctr')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">Marketing Analytics</h3>
          <p className="text-sm text-muted">Performance across all platforms</p>
        </div>
        <div className="flex items-center gap-2 bg-surface border border-border rounded-lg p-1">
          {['24h', '7d', '30d', '90d'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                timeRange === range
                  ? 'bg-primary text-white'
                  : 'text-muted hover:text-white'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="bg-surface border border-border rounded-xl p-5"
            >
              <div className="flex items-center justify-between mb-3">
                <div className={`w-10 h-10 rounded-lg ${stat.bg} flex items-center justify-center`}>
                  <Icon className={`w-5 h-5 ${stat.color}`} />
                </div>
                <span className="text-xs font-medium text-success">{stat.change}</span>
              </div>
              <div className="text-2xl font-bold text-white">{stat.value}</div>
              <div className="text-sm text-muted">{stat.label}</div>
            </motion.div>
          )
        })}
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CTR Trend */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-surface border border-border rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <Target className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h4 className="text-sm font-medium text-white">Click-Through Rate</h4>
                <p className="text-xs text-muted">Daily CTR performance</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-white">5.5%</div>
              <div className="text-xs text-success">+0.8% vs last week</div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={ctrData}>
              <defs>
                <linearGradient id="ctrGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
              <XAxis dataKey="day" stroke="#6b7280" fontSize={12} />
              <YAxis stroke="#6b7280" fontSize={12} unit="%" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#12121a',
                  border: '1px solid #2a2a3a',
                  borderRadius: '8px',
                  color: '#fff',
                }}
              />
              <Area
                type="monotone"
                dataKey="ctr"
                stroke="#8b5cf6"
                strokeWidth={2}
                fill="url(#ctrGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Retention Curve */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-surface border border-border rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-secondary/10 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-secondary" />
              </div>
              <div>
                <h4 className="text-sm font-medium text-white">Audience Retention</h4>
                <p className="text-xs text-muted">Avg watch time: 1:42</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-white">32%</div>
              <div className="text-xs text-muted">At 2min mark</div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={retentionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
              <XAxis dataKey="second" stroke="#6b7280" fontSize={12} />
              <YAxis stroke="#6b7280" fontSize={12} unit="%" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#12121a',
                  border: '1px solid #2a2a3a',
                  borderRadius: '8px',
                  color: '#fff',
                }}
              />
              <Line
                type="monotone"
                dataKey="pct"
                stroke="#06b6d4"
                strokeWidth={2}
                dot={{ fill: '#06b6d4', strokeWidth: 0, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Second Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Conversion Funnel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-surface border border-border rounded-xl p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
              <Zap className="w-5 h-5 text-success" />
            </div>
            <div>
              <h4 className="text-sm font-medium text-white">Conversion Funnel</h4>
              <p className="text-xs text-muted">View to purchase</p>
            </div>
          </div>
          <div className="space-y-3">
            {conversionData.map((stage, i) => (
              <div key={stage.stage}>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-white">{stage.stage}</span>
                  <span className="text-muted">{stage.count.toLocaleString()} ({stage.pct}%)</span>
                </div>
                <div className="w-full bg-surface-hover rounded-full h-2.5">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${stage.pct}%` }}
                    transition={{ delay: 0.5 + i * 0.1, duration: 0.8 }}
                    className="h-2.5 rounded-full"
                    style={{
                      backgroundColor: ['#8b5cf6', '#06b6d4', '#f59e0b', '#10b981'][i],
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-4 border-t border-border">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted">Conversion Rate</span>
              <span className="text-success font-semibold">0.22%</span>
            </div>
          </div>
        </motion.div>

        {/* Platform Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-surface border border-border rounded-xl p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
              <Share2 className="w-5 h-5 text-accent" />
            </div>
            <div>
              <h4 className="text-sm font-medium text-white">Platform Split</h4>
              <p className="text-xs text-muted">Views by platform</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={platformData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={3}
                dataKey="value"
              >
                {platformData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#12121a',
                  border: '1px solid #2a2a3a',
                  borderRadius: '8px',
                  color: '#fff',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-2 gap-2 mt-2">
            {platformData.map((p) => (
              <div key={p.name} className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: p.color }} />
                <span className="text-xs text-muted">{p.name}</span>
                <span className="text-xs text-white ml-auto">{p.value}%</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* A/B Test Results */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-surface border border-border rounded-xl p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <Target className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h4 className="text-sm font-medium text-white">A/B Tests</h4>
              <p className="text-xs text-muted">Active thumbnail tests</p>
            </div>
          </div>
          <div className="space-y-4">
            {abTestData.map((test) => (
              <div
                key={test.variant}
                className={`p-3 rounded-lg border ${
                  test.ctr === Math.max(...abTestData.map((t) => t.ctr))
                    ? 'border-success/30 bg-success/5'
                    : 'border-border bg-surface-hover'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-white">Variant {test.variant}</span>
                    {test.ctr === Math.max(...abTestData.map((t) => t.ctr)) && (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-success/20 text-success">
                        Winner
                      </span>
                    )}
                  </div>
                  <span className="text-sm font-bold text-white">{test.ctr}%</span>
                </div>
                <div className="text-xs text-muted mb-2">{test.thumbnail}</div>
                <div className="w-full bg-surface rounded-full h-1.5">
                  <div
                    className="h-1.5 rounded-full bg-primary"
                    style={{ width: `${(test.ctr / 8) * 100}%` }}
                  />
                </div>
                <div className="text-xs text-muted mt-1">
                  {test.impressions.toLocaleString()} impressions
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
