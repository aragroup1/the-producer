'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
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
  Music,
  DollarSign,
  Target,
} from 'lucide-react'

const generationData = [
  { day: 'Mon', beats: 12, quality: 7.5 },
  { day: 'Tue', beats: 18, quality: 7.8 },
  { day: 'Wed', beats: 15, quality: 8.0 },
  { day: 'Thu', beats: 22, quality: 7.6 },
  { day: 'Fri', beats: 28, quality: 8.2 },
  { day: 'Sat', beats: 20, quality: 7.9 },
  { day: 'Sun', beats: 16, quality: 8.1 },
]

const salesData = [
  { day: 'Mon', revenue: 120, sales: 4 },
  { day: 'Tue', revenue: 180, sales: 6 },
  { day: 'Wed', revenue: 90, sales: 3 },
  { day: 'Thu', revenue: 240, sales: 8 },
  { day: 'Fri', revenue: 300, sales: 10 },
  { day: 'Sat', revenue: 210, sales: 7 },
  { day: 'Sun', revenue: 150, sales: 5 },
]

const genreData = [
  { name: 'Trap', value: 35, color: '#8b5cf6' },
  { name: 'Drill', value: 25, color: '#06b6d4' },
  { name: 'Lo-Fi', value: 15, color: '#10b981' },
  { name: 'Afrobeats', value: 12, color: '#f59e0b' },
  { name: 'Rage', value: 8, color: '#ef4444' },
  { name: 'Other', value: 5, color: '#6b7280' },
]

const qualityDistribution = [
  { range: '9-10', count: 45 },
  { range: '8-9', count: 120 },
  { range: '7-8', count: 200 },
  { range: '6-7', count: 150 },
  { range: '5-6', count: 80 },
  { range: '<5', count: 25 },
]

export default function AnalyticsPanel() {
  const [timeRange, setTimeRange] = useState('7d')

  return (
    <div className="space-y-6">
      {/* Time Range Selector */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Analytics & Insights</h3>
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

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Generation Trend */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-surface border border-border rounded-xl p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <Music className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h4 className="text-sm font-medium text-white">Generation Trend</h4>
              <p className="text-xs text-muted">Beats generated over time</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={generationData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
              <XAxis dataKey="day" stroke="#6b7280" fontSize={12} />
              <YAxis stroke="#6b7280" fontSize={12} />
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
                dataKey="beats"
                stroke="#8b5cf6"
                strokeWidth={2}
                dot={{ fill: '#8b5cf6', strokeWidth: 0 }}
              />
              <Line
                type="monotone"
                dataKey="quality"
                stroke="#06b6d4"
                strokeWidth={2}
                dot={{ fill: '#06b6d4', strokeWidth: 0 }}
                yAxisId={1}
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Revenue Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-surface border border-border rounded-xl p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-success" />
            </div>
            <div>
              <h4 className="text-sm font-medium text-white">Revenue</h4>
              <p className="text-xs text-muted">Sales performance</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={salesData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
              <XAxis dataKey="day" stroke="#6b7280" fontSize={12} />
              <YAxis stroke="#6b7280" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#12121a',
                  border: '1px solid #2a2a3a',
                  borderRadius: '8px',
                  color: '#fff',
                }}
              />
              <Bar dataKey="revenue" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="sales" fill="#06b6d4" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Genre Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-surface border border-border rounded-xl p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
              <Target className="w-5 h-5 text-accent" />
            </div>
            <div>
              <h4 className="text-sm font-medium text-white">Genre Distribution</h4>
              <p className="text-xs text-muted">Beats by genre</p>
            </div>
          </div>
          <div className="flex items-center">
            <ResponsiveContainer width="60%" height={250}>
              <PieChart>
                <Pie
                  data={genreData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {genreData.map((entry, index) => (
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
            <div className="flex-1 space-y-2">
              {genreData.map((genre) => (
                <div key={genre.name} className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: genre.color }}
                  />
                  <span className="text-sm text-white flex-1">{genre.name}</span>
                  <span className="text-sm text-muted">{genre.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Quality Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-surface border border-border rounded-xl p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-secondary/10 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-secondary" />
            </div>
            <div>
              <h4 className="text-sm font-medium text-white">Quality Distribution</h4>
              <p className="text-xs text-muted">QC score breakdown</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={qualityDistribution} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
              <XAxis type="number" stroke="#6b7280" fontSize={12} />
              <YAxis dataKey="range" type="category" stroke="#6b7280" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#12121a',
                  border: '1px solid #2a2a3a',
                  borderRadius: '8px',
                  color: '#fff',
                }}
              />
              <Bar dataKey="count" fill="#10b981" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
    </div>
  )
}
