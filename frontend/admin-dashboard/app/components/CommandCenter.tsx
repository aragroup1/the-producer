'use client'

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
  Loader2,
  Zap,
  ArrowRight,
  Play,
  Pause,
  BarChart3,
  Eye,
  MousePointer,
  ShoppingCart,
  Youtube,
} from 'lucide-react'
import { useDashboardStats, useRecentBeats, useQueueStatus, useMarketingAnalytics } from '../lib/hooks'

interface StatCardProps {
  title: string
  value: string
  change: string
  changeType: 'positive' | 'negative' | 'neutral'
  icon: React.ElementType
  delay: number
  loading?: boolean
}

function StatCard({ title, value, change, changeType, icon: Icon, delay, loading }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="bg-surface border border-border rounded-xl p-5"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted">{title}</p>
          <h3 className="text-xl font-bold text-white mt-1">
            {loading ? <Loader2 className="w-5 h-5 animate-spin text-primary" /> : value}
          </h3>
        </div>
        <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
          <Icon className="w-4 h-4 text-primary" />
        </div>
      </div>
      <div className="mt-3 flex items-center gap-2">
        <span className={`text-xs font-medium ${changeType === 'positive' ? 'text-success' : changeType === 'negative' ? 'text-danger' : 'text-muted'}`}>
          {change}
        </span>
        <span className="text-xs text-muted">vs last week</span>
      </div>
    </motion.div>
  )
}

function PipelineStage({ stage, status, count, delay }: { stage: string; status: string; count: number; delay: number }) {
  const colors: Record<string, string> = {
    active: 'bg-primary border-primary text-white',
    waiting: 'bg-surface-hover border-border text-muted',
    done: 'bg-success/10 border-success/30 text-success',
    error: 'bg-danger/10 border-danger/30 text-danger',
  }
  
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
      className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-xs font-medium ${colors[status] || colors.waiting}`}
    >
      {status === 'active' && <Loader2 className="w-3 h-3 animate-spin" />}
      {status === 'done' && <CheckCircle2 className="w-3 h-3" />}
      {status === 'error' && <XCircle className="w-3 h-3" />}
      {status === 'waiting' && <Clock className="w-3 h-3" />}
      <span>{stage}</span>
      {count > 0 && <span className="ml-auto bg-background/50 px-1.5 py-0.5 rounded">{count}</span>}
    </motion.div>
  )
}

export default function CommandCenter() {
  const { data: stats, isLoading: statsLoading } = useDashboardStats()
  const { data: beatsData, isLoading: beatsLoading } = useRecentBeats(5)
  const { data: queue, isLoading: queueLoading } = useQueueStatus()
  const { data: marketing, isLoading: marketingLoading } = useMarketingAnalytics()

  const recentBeats = beatsData?.items || []

  return (
    <div className="space-y-6">
      {/* Top Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <StatCard title="Total Beats" value={stats?.total_beats?.toLocaleString() || '0'} change="+12%" changeType="positive" icon={Music} delay={0} loading={statsLoading} />
        <StatCard title="Revenue" value={`£${(stats?.revenue || 0).toLocaleString()}`} change="+8.2%" changeType="positive" icon={DollarSign} delay={0.05} loading={statsLoading} />
        <StatCard title="Avg Quality" value={(stats?.avg_quality || 0).toFixed(1)} change="+0.3" changeType="positive" icon={TrendingUp} delay={0.1} loading={statsLoading} />
        <StatCard title="Queue" value={((queue?.queued || 0) + (queue?.processing || 0)).toString()} change="-2" changeType="positive" icon={Clock} delay={0.15} loading={queueLoading} />
        <StatCard title="Views" value={marketing?.total_views?.toLocaleString() || '0'} change="+12.3%" changeType="positive" icon={Eye} delay={0.2} loading={marketingLoading} />
        <StatCard title="CTR" value={`${marketing?.avg_ctr || 0}%`} change="+0.8%" changeType="positive" icon={MousePointer} delay={0.25} loading={marketingLoading} />
      </div>

      {/* Main Content: 3-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* LEFT: Production Pipeline */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-surface border border-border rounded-xl p-5"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Production Pipeline</h3>
            <span className="text-xs text-muted">Live</span>
          </div>
          
          <div className="space-y-2">
            <PipelineStage stage="MIDI Composition" status="done" count={queue?.completed || 0} delay={0.35} />
            <PipelineStage stage="Sound Rendering" status={queue?.processing > 0 ? 'active' : 'waiting'} count={queue?.processing || 0} delay={0.38} />
            <PipelineStage stage="Mixing" status="waiting" count={0} delay={0.41} />
            <PipelineStage stage="Mastering" status="waiting" count={0} delay={0.44} />
            <PipelineStage stage="Quality Control" status="waiting" count={0} delay={0.47} />
            <PipelineStage stage="Export & Publish" status="waiting" count={0} delay={0.5} />
          </div>

          {/* Quick Generate */}
          <div className="mt-4 pt-4 border-t border-border">
            <button className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary/90 transition-colors">
              <Zap className="w-4 h-4" />
              Generate 10 Beats
            </button>
            <div className="grid grid-cols-2 gap-2 mt-2">
              <button className="px-3 py-2 rounded-lg bg-surface-hover text-muted text-xs hover:text-white transition-colors">
                Trap ×5
              </button>
              <button className="px-3 py-2 rounded-lg bg-surface-hover text-muted text-xs hover:text-white transition-colors">
                Afrobeats ×5
              </button>
            </div>
          </div>
        </motion.div>

        {/* CENTER: Recent Beats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="bg-surface border border-border rounded-xl p-5"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Recent Beats</h3>
            <button className="text-xs text-primary hover:text-primary/80">View All</button>
          </div>
          
          {beatsLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : recentBeats.length === 0 ? (
            <div className="text-center py-8 text-muted">
              <Music className="w-10 h-10 mx-auto mb-2 opacity-30" />
              <p className="text-sm">No beats yet</p>
              <p className="text-xs mt-1">Generate your first beat</p>
            </div>
          ) : (
            <div className="space-y-2">
              {recentBeats.map((beat: any, i: number) => (
                <div key={beat.id || i} className="flex items-center gap-3 p-2.5 bg-background rounded-lg hover:bg-background/80 transition-colors group cursor-pointer">
                  <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20">
                    <Play className="w-3 h-3 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">{beat.title || `Beat #${beat.id?.slice(0, 6)}`}</p>
                    <p className="text-xs text-muted">{beat.genre?.name || beat.genre_id} • {beat.bpm} BPM</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {beat.quality_score && <span className="text-xs text-success">{beat.quality_score.toFixed(1)}</span>}
                    <StatusBadge status={beat.status} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        {/* RIGHT: Marketing & Sales */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="space-y-4"
        >
          {/* Marketing Stats */}
          <div className="bg-surface border border-border rounded-xl p-5">
            <h3 className="text-sm font-semibold text-white mb-3">Marketing Performance</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="text-center p-3 bg-background rounded-lg">
                <div className="text-lg font-bold text-white">{marketing?.videos_live || 0}</div>
                <div className="text-xs text-muted">Videos Live</div>
              </div>
              <div className="text-center p-3 bg-background rounded-lg">
                <div className="text-lg font-bold text-white">{marketing?.conversions || 0}</div>
                <div className="text-xs text-muted">Conversions</div>
              </div>
            </div>
            <div className="mt-3 space-y-2">
              <PlatformBar platform="YouTube" value={45} color="bg-danger" />
              <PlatformBar platform="TikTok" value={30} color="bg-secondary" />
              <PlatformBar platform="Instagram" value={18} color="bg-accent" />
              <PlatformBar platform="BeatStars" value={5} color="bg-primary" />
            </div>
          </div>

          {/* Trending Alert */}
          <div className="bg-surface border border-border rounded-xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="w-4 h-4 text-success" />
              <h3 className="text-sm font-semibold text-white">Trending Now</h3>
            </div>
            <div className="space-y-2">
              <TrendAlert genre="Afrobeats" growth="+23%" action="Generate 5 beats" />
              <TrendAlert genre="Drill" growth="+15%" action="Generate 3 beats" />
              <TrendAlert genre="R&B" growth="+8%" action="Generate 2 beats" />
            </div>
          </div>

          {/* System Health */}
          <div className="bg-surface border border-border rounded-xl p-5">
            <h3 className="text-sm font-semibold text-white mb-3">System Health</h3>
            <div className="space-y-2">
              <HealthItem label="API Gateway" status="healthy" latency="12ms" />
              <HealthItem label="Sound Engine" status="healthy" latency="120ms" />
              <HealthItem label="Database" status="healthy" latency="3ms" />
              <HealthItem label="Redis Queue" status="healthy" latency="1ms" />
            </div>
          </div>
        </motion.div>
      </div>

      {/* Bottom Row: Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-surface border border-border rounded-xl p-5"
        >
          <h3 className="text-sm font-semibold text-white mb-4">Generation Activity</h3>
          <div className="h-40 flex items-end gap-2">
            {[40, 65, 45, 80, 55, 90, 70, 85, 60, 75, 50, 95].map((h, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <div 
                  className="w-full bg-primary/20 rounded-t" 
                  style={{ height: `${h}%` }}
                />
                <span className="text-[10px] text-muted">{['J','F','M','A','M','J','J','A','S','O','N','D'][i]}</span>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.55 }}
          className="bg-surface border border-border rounded-xl p-5"
        >
          <h3 className="text-sm font-semibold text-white mb-4">Revenue Trend</h3>
          <div className="h-40 flex items-end gap-2">
            {[20, 35, 30, 55, 45, 70, 60, 85, 75, 90, 80, 100].map((h, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <div 
                  className="w-full bg-success/20 rounded-t" 
                  style={{ height: `${h}%` }}
                />
                <span className="text-[10px] text-muted">{['J','F','M','A','M','J','J','A','S','O','N','D'][i]}</span>
              </div>
            ))}
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
    mastering: 'bg-secondary/10 text-secondary',
    rendering: 'bg-primary/10 text-primary',
    draft: 'bg-muted/10 text-muted',
    failed: 'bg-danger/10 text-danger',
  }
  return <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${styles[status] || 'bg-muted/10 text-muted'}`}>{status}</span>
}

function PlatformBar({ platform, value, color }: { platform: string; value: number; color: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-muted w-16">{platform}</span>
      <div className="flex-1 bg-background rounded-full h-1.5">
        <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${value}%` }} />
      </div>
      <span className="text-xs text-white w-8 text-right">{value}%</span>
    </div>
  )
}

function TrendAlert({ genre, growth, action }: { genre: string; growth: string; action: string }) {
  return (
    <div className="flex items-center justify-between p-2.5 bg-background rounded-lg">
      <div>
        <span className="text-sm font-medium text-white">{genre}</span>
        <span className="text-xs text-success ml-2">{growth}</span>
      </div>
      <button className="text-xs text-primary hover:text-primary/80 flex items-center gap-1">
        {action}
        <ArrowRight className="w-3 h-3" />
      </button>
    </div>
  )
}

function HealthItem({ label, status, latency }: { label: string; status: string; latency: string }) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        {status === 'healthy' ? <CheckCircle2 className="w-3 h-3 text-success" /> : <XCircle className="w-3 h-3 text-danger" />}
        <span className="text-xs text-white">{label}</span>
      </div>
      <span className="text-xs text-muted">{latency}</span>
    </div>
  )
}
