'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts'
import {
  Youtube,
  Music2,
  Instagram,
  ShoppingBag,
  Cloud,
  TrendingUp,
  TrendingDown,
  Users,
  Eye,
  Heart,
  MessageSquare,
  Share2,
  Calendar,
  Clock,
} from 'lucide-react'

interface Channel {
  id: string
  name: string
  platform: string
  subscribers: number
  totalViews: number
  avgCtr: number
  avgRetention: number
  uploadsThisWeek: number
  growthRate: number
  status: 'active' | 'paused' | 'limited'
  lastUpload: string
  avatar?: string
}

const channels: Channel[] = [
  {
    id: 'ch1',
    name: 'The Producer - Main',
    platform: 'youtube',
    subscribers: 45200,
    totalViews: 1245000,
    avgCtr: 6.2,
    avgRetention: 38,
    uploadsThisWeek: 7,
    growthRate: 12.3,
    status: 'active',
    lastUpload: '2 hours ago',
  },
  {
    id: 'ch2',
    name: 'The Producer - Shorts',
    platform: 'youtube',
    subscribers: 18900,
    totalViews: 890000,
    avgCtr: 8.5,
    avgRetention: 72,
    uploadsThisWeek: 14,
    growthRate: 28.7,
    status: 'active',
    lastUpload: '4 hours ago',
  },
  {
    id: 'ch3',
    name: '@theproducer',
    platform: 'tiktok',
    subscribers: 32100,
    totalViews: 2100000,
    avgCtr: 4.8,
    avgRetention: 65,
    uploadsThisWeek: 21,
    growthRate: 45.2,
    status: 'active',
    lastUpload: '1 hour ago',
  },
  {
    id: 'ch4',
    name: '@theproducer',
    platform: 'instagram',
    subscribers: 15800,
    totalViews: 456000,
    avgCtr: 3.2,
    avgRetention: 45,
    uploadsThisWeek: 10,
    growthRate: 8.1,
    status: 'active',
    lastUpload: '6 hours ago',
  },
  {
    id: 'ch5',
    name: 'The Producer Store',
    platform: 'beatstars',
    subscribers: 5400,
    totalViews: 89000,
    avgCtr: 2.1,
    avgRetention: 15,
    uploadsThisWeek: 5,
    growthRate: -2.3,
    status: 'limited',
    lastUpload: '1 day ago',
  },
]

const platformIcons: Record<string, React.ElementType> = {
  youtube: Youtube,
  tiktok: Music2,
  instagram: Instagram,
  beatstars: ShoppingBag,
  airbit: Cloud,
}

const platformColors: Record<string, string> = {
  youtube: '#ef4444',
  tiktok: '#06b6d4',
  instagram: '#f59e0b',
  beatstars: '#8b5cf6',
  airbit: '#10b981',
}

const weeklyUploads = [
  { day: 'Mon', youtube: 2, tiktok: 4, instagram: 2, beatstars: 1 },
  { day: 'Tue', youtube: 1, tiktok: 3, instagram: 1, beatstars: 1 },
  { day: 'Wed', youtube: 2, tiktok: 4, instagram: 2, beatstars: 0 },
  { day: 'Thu', youtube: 1, tiktok: 3, instagram: 2, beatstars: 1 },
  { day: 'Fri', youtube: 1, tiktok: 4, instagram: 2, beatstars: 1 },
  { day: 'Sat', youtube: 0, tiktok: 2, instagram: 1, beatstars: 1 },
  { day: 'Sun', youtube: 0, tiktok: 1, instagram: 0, beatstars: 0 },
]

const subscriberGrowth = [
  { week: 'W1', youtube: 42000, tiktok: 28000, instagram: 14200 },
  { week: 'W2', youtube: 43100, tiktok: 29500, instagram: 14600 },
  { week: 'W3', youtube: 44100, tiktok: 30800, instagram: 15100 },
  { week: 'W4', youtube: 45200, tiktok: 32100, instagram: 15800 },
]

export default function ChannelAnalytics() {
  const [selectedChannel, setSelectedChannel] = useState<string | null>(null)

  const totalSubscribers = channels.reduce((sum, ch) => sum + ch.subscribers, 0)
  const totalViews = channels.reduce((sum, ch) => sum + ch.totalViews, 0)
  const avgCtr = channels.reduce((sum, ch) => sum + ch.avgCtr, 0) / channels.length
  const totalUploads = channels.reduce((sum, ch) => sum + ch.uploadsThisWeek, 0)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">Channel Analytics</h3>
          <p className="text-sm text-muted">Performance across all channels</p>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Subscribers', value: totalSubscribers.toLocaleString(), icon: Users, color: 'text-primary' },
          { label: 'Total Views', value: `${(totalViews / 1000000).toFixed(1)}M`, icon: Eye, color: 'text-secondary' },
          { label: 'Avg CTR', value: `${avgCtr.toFixed(1)}%`, icon: TrendingUp, color: 'text-success' },
          { label: 'Uploads This Week', value: totalUploads.toString(), icon: Calendar, color: 'text-accent' },
        ].map((stat, i) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="bg-surface border border-border rounded-xl p-5"
            >
              <div className="flex items-center gap-3 mb-2">
                <Icon className={`w-5 h-5 ${stat.color}`} />
                <span className="text-sm text-muted">{stat.label}</span>
              </div>
              <div className="text-2xl font-bold text-white">{stat.value}</div>
            </motion.div>
          )
        })}
      </div>

      {/* Channels List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {channels.map((channel, i) => {
          const PlatformIcon = platformIcons[channel.platform]
          const isSelected = selectedChannel === channel.id

          return (
            <motion.div
              key={channel.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => setSelectedChannel(isSelected ? null : channel.id)}
              className={`bg-surface border rounded-xl p-5 cursor-pointer transition-all ${
                isSelected ? 'border-primary' : 'border-border hover:border-primary/30'
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div
                    className="w-12 h-12 rounded-xl flex items-center justify-center"
                    style={{ backgroundColor: `${platformColors[channel.platform]}15` }}
                  >
                    <PlatformIcon
                      className="w-6 h-6"
                      style={{ color: platformColors[channel.platform] }}
                    />
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-white">{channel.name}</h4>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span
                        className={`w-2 h-2 rounded-full ${
                          channel.status === 'active'
                            ? 'bg-success'
                            : channel.status === 'paused'
                            ? 'bg-warning'
                            : 'bg-danger'
                        }`}
                      />
                      <span className="text-xs text-muted capitalize">{channel.status}</span>
                      <span className="text-xs text-muted">{channel.lastUpload}</span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-1">
                    {channel.growthRate >= 0 ? (
                      <TrendingUp className="w-3 h-3 text-success" />
                    ) : (
                      <TrendingDown className="w-3 h-3 text-danger" />
                    )}
                    <span
                      className={`text-xs font-medium ${
                        channel.growthRate >= 0 ? 'text-success' : 'text-danger'
                      }`}
                    >
                      {channel.growthRate >= 0 ? '+' : ''}
                      {channel.growthRate}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-4 gap-3">
                <div>
                  <div className="text-xs text-muted mb-1">Subscribers</div>
                  <div className="text-sm font-semibold text-white">
                    {channel.subscribers >= 1000
                      ? `${(channel.subscribers / 1000).toFixed(1)}K`
                      : channel.subscribers}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-muted mb-1">Views</div>
                  <div className="text-sm font-semibold text-white">
                    {channel.totalViews >= 1000000
                      ? `${(channel.totalViews / 1000000).toFixed(1)}M`
                      : channel.totalViews >= 1000
                      ? `${(channel.totalViews / 1000).toFixed(0)}K`
                      : channel.totalViews}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-muted mb-1">CTR</div>
                  <div className="text-sm font-semibold text-white">{channel.avgCtr}%</div>
                </div>
                <div>
                  <div className="text-xs text-muted mb-1">Retention</div>
                  <div className="text-sm font-semibold text-white">{channel.avgRetention}%</div>
                </div>
              </div>

              {/* Expanded Detail */}
              {isSelected && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="mt-4 pt-4 border-t border-border"
                >
                  <div className="grid grid-cols-3 gap-3">
                    <div className="bg-surface-hover rounded-lg p-3 text-center">
                      <Heart className="w-4 h-4 text-danger mx-auto mb-1" />
                      <div className="text-sm font-semibold text-white">4.2%</div>
                      <div className="text-xs text-muted">Like Rate</div>
                    </div>
                    <div className="bg-surface-hover rounded-lg p-3 text-center">
                      <MessageSquare className="w-4 h-4 text-primary mx-auto mb-1" />
                      <div className="text-sm font-semibold text-white">1.8%</div>
                      <div className="text-xs text-muted">Comment Rate</div>
                    </div>
                    <div className="bg-surface-hover rounded-lg p-3 text-center">
                      <Share2 className="w-4 h-4 text-secondary mx-auto mb-1" />
                      <div className="text-sm font-semibold text-white">0.9%</div>
                      <div className="text-xs text-muted">Share Rate</div>
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          )
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Uploads */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-surface border border-border rounded-xl p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <Calendar className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h4 className="text-sm font-medium text-white">Weekly Uploads</h4>
              <p className="text-xs text-muted">Posts per platform</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={weeklyUploads}>
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
              <Bar dataKey="youtube" fill="#ef4444" radius={[2, 2, 0, 0]} />
              <Bar dataKey="tiktok" fill="#06b6d4" radius={[2, 2, 0, 0]} />
              <Bar dataKey="instagram" fill="#f59e0b" radius={[2, 2, 0, 0]} />
              <Bar dataKey="beatstars" fill="#8b5cf6" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Subscriber Growth */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-surface border border-border rounded-xl p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
              <Users className="w-5 h-5 text-success" />
            </div>
            <div>
              <h4 className="text-sm font-medium text-white">Subscriber Growth</h4>
              <p className="text-xs text-muted">4-week trend</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={subscriberGrowth}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
              <XAxis dataKey="week" stroke="#6b7280" fontSize={12} />
              <YAxis stroke="#6b7280" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#12121a',
                  border: '1px solid #2a2a3a',
                  borderRadius: '8px',
                  color: '#fff',
                }}
              />
              <Line type="monotone" dataKey="youtube" stroke="#ef4444" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="tiktok" stroke="#06b6d4" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="instagram" stroke="#f59e0b" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
    </div>
  )
}
