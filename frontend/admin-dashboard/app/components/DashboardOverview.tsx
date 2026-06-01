'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Music,
  TrendingUp,
  DollarSign,
  Cpu,
  Activity,
  Clock,
  CheckCircle2,
  XCircle,
} from 'lucide-react'

interface StatCardProps {
  title: string
  value: string
  change: string
  changeType: 'positive' | 'negative' | 'neutral'
  icon: React.ElementType
  delay: number
}

function StatCard({ title, value, change, changeType, icon: Icon, delay }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="bg-surface border border-border rounded-xl p-6"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted">{title}</p>
          <h3 className="text-2xl font-bold text-white mt-1">{value}</h3>
        </div>
        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
          <Icon className="w-5 h-5 text-primary" />
        </div>
      </div>
      <div className="mt-4 flex items-center gap-2">
        <span
          className={`text-sm font-medium ${
            changeType === 'positive'
              ? 'text-success'
              : changeType === 'negative'
              ? 'text-danger'
              : 'text-muted'
          }`}
        >
          {change}
        </span>
        <span className="text-sm text-muted">vs last week</span>
      </div>
    </motion.div>
  )
}

export default function DashboardOverview() {
  const [stats, setStats] = useState({
    totalBeats: 0,
    generatedToday: 0,
    revenue: 0,
    avgQuality: 0,
    queueDepth: 0,
    successRate: 0,
  })

  useEffect(() => {
    // TODO: Fetch real stats from API
    setStats({
      totalBeats: 1247,
      generatedToday: 23,
      revenue: 3847.5,
      avgQuality: 7.8,
      queueDepth: 5,
      successRate: 94,
    })
  }, [])

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatCard
          title="Total Beats"
          value={stats.totalBeats.toLocaleString()}
          change="+12%"
          changeType="positive"
          icon={Music}
          delay={0}
        />
        <StatCard
          title="Generated Today"
          value={stats.generatedToday.toString()}
          change="+5"
          changeType="positive"
          icon={Activity}
          delay={0.1}
        />
        <StatCard
          title="Revenue"
          value={`£${stats.revenue.toLocaleString()}`}
          change="+8.2%"
          changeType="positive"
          icon={DollarSign}
          delay={0.2}
        />
        <StatCard
          title="Avg Quality Score"
          value={stats.avgQuality.toString()}
          change="+0.3"
          changeType="positive"
          icon={TrendingUp}
          delay={0.3}
        />
        <StatCard
          title="Queue Depth"
          value={stats.queueDepth.toString()}
          change="-2"
          changeType="positive"
          icon={Clock}
          delay={0.4}
        />
        <StatCard
          title="Success Rate"
          value={`${stats.successRate}%`}
          change="+2%"
          changeType="positive"
          icon={Cpu}
          delay={0.5}
        />
      </div>

      {/* Recent Activity & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Beats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-surface border border-border rounded-xl p-6"
        >
          <h3 className="text-lg font-semibold text-white mb-4">Recent Beats</h3>
          <div className="space-y-3">
            {[
              { title: 'Dark Trap Beat #234', genre: 'Trap', bpm: 140, status: 'published', quality: 8.5 },
              { title: 'Melodic Drill #189', genre: 'Drill', bpm: 145, status: 'approved', quality: 7.9 },
              { title: 'LoFi Chill #456', genre: 'Lo-Fi', bpm: 82, status: 'qc', quality: 8.2 },
              { title: 'Afro Swing #321', genre: 'Afrobeats', bpm: 105, status: 'mixing', quality: null },
            ].map((beat, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-3 bg-background rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <Music className="w-4 h-4 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">{beat.title}</p>
                    <p className="text-xs text-muted">
                      {beat.genre} • {beat.bpm} BPM
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {beat.quality && (
                    <span className="text-xs text-success">{beat.quality}/10</span>
                  )}
                  <StatusBadge status={beat.status} />
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* System Health */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="bg-surface border border-border rounded-xl p-6"
        >
          <h3 className="text-lg font-semibold text-white mb-4">System Health</h3>
          <div className="space-y-4">
            <HealthItem
              label="API Gateway"
              status="healthy"
              latency="12ms"
            />
            <HealthItem
              label="MIDI Workers"
              status="healthy"
              latency="45ms"
            />
            <HealthItem
              label="Sound Engine"
              status="healthy"
              latency="120ms"
            />
            <HealthItem
              label="Mix/Master"
              status="healthy"
              latency="89ms"
            />
            <HealthItem
              label="Database"
              status="healthy"
              latency="3ms"
            />
            <HealthItem
              label="Redis Queue"
              status="healthy"
              latency="1ms"
            />
          </div>
        </motion.div>
      </div>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    published: 'bg-success/10 text-success',
    approved: 'bg-success/10 text-success',
    qc: 'bg-warning/10 text-warning',
    mixing: 'bg-secondary/10 text-secondary',
    rendering: 'bg-primary/10 text-primary',
    failed: 'bg-danger/10 text-danger',
  }

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || 'bg-muted/10 text-muted'}`}>
      {status}
    </span>
  )
}

function HealthItem({ label, status, latency }: { label: string; status: string; latency: string }) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        {status === 'healthy' ? (
          <CheckCircle2 className="w-4 h-4 text-success" />
        ) : (
          <XCircle className="w-4 h-4 text-danger" />
        )}
        <span className="text-sm text-white">{label}</span>
      </div>
      <span className="text-xs text-muted">{latency}</span>
    </div>
  )
}
