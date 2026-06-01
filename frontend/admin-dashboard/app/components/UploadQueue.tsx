'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Youtube,
  Music2,
  Instagram,
  ShoppingBag,
  Cloud,
  Clock,
  CheckCircle2,
  XCircle,
  Loader2,
  Play,
  Pause,
  RotateCcw,
  Trash2,
  Filter,
  Search,
} from 'lucide-react'

interface UploadJob {
  id: string
  beatId: string
  title: string
  genre: string
  platform: string
  status: 'pending' | 'processing' | 'uploading' | 'completed' | 'failed'
  progress: number
  scheduledFor?: string
  completedAt?: string
  error?: string
  url?: string
}

const mockJobs: UploadJob[] = [
  {
    id: 'u1',
    beatId: 'trap_140_C_minor',
    title: 'Dark Trap Beat 140 BPM',
    genre: 'Trap',
    platform: 'youtube',
    status: 'completed',
    progress: 100,
    completedAt: '2026-05-11 14:30',
    url: 'https://youtube.com/watch?v=abc123',
  },
  {
    id: 'u2',
    beatId: 'drill_150_F_minor',
    title: 'UK Drill Type Beat 150 BPM',
    genre: 'Drill',
    platform: 'tiktok',
    status: 'uploading',
    progress: 67,
  },
  {
    id: 'u3',
    beatId: 'lofi_85_A_major',
    title: 'Chill Lo-Fi Beat 85 BPM',
    genre: 'Lo-Fi',
    platform: 'instagram',
    status: 'processing',
    progress: 34,
  },
  {
    id: 'u4',
    beatId: 'afro_120_G_minor',
    title: 'Afrobeats Instrumental 120 BPM',
    genre: 'Afrobeats',
    platform: 'beatstars',
    status: 'pending',
    progress: 0,
    scheduledFor: '2026-05-12 18:00',
  },
  {
    id: 'u5',
    beatId: 'rage_160_D_minor',
    title: 'Rage Type Beat 160 BPM',
    genre: 'Rage',
    platform: 'youtube',
    status: 'failed',
    progress: 45,
    error: 'Authentication expired',
  },
  {
    id: 'u6',
    beatId: 'trap_145_E_minor',
    title: 'Hard Trap Beat 145 BPM',
    genre: 'Trap',
    platform: 'airbit',
    status: 'pending',
    progress: 0,
    scheduledFor: '2026-05-12 20:00',
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
  youtube: 'text-danger',
  tiktok: 'text-secondary',
  instagram: 'text-accent',
  beatstars: 'text-primary',
  airbit: 'text-success',
}

const statusConfig: Record<string, { label: string; color: string; icon: React.ElementType }> = {
  pending: { label: 'Pending', color: 'text-muted', icon: Clock },
  processing: { label: 'Processing', color: 'text-primary', icon: Loader2 },
  uploading: { label: 'Uploading', color: 'text-secondary', icon: Loader2 },
  completed: { label: 'Completed', color: 'text-success', icon: CheckCircle2 },
  failed: { label: 'Failed', color: 'text-danger', icon: XCircle },
}

export default function UploadQueue() {
  const [jobs, setJobs] = useState<UploadJob[]>(mockJobs)
  const [filter, setFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedJobs, setSelectedJobs] = useState<Set<string>>(new Set())

  const filteredJobs = jobs.filter((job) => {
    const matchesFilter = filter === 'all' || job.status === filter
    const matchesSearch =
      job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.genre.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesFilter && matchesSearch
  })

  const toggleSelection = (id: string) => {
    const next = new Set(selectedJobs)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setSelectedJobs(next)
  }

  const retryJob = (id: string) => {
    setJobs((prev) =>
      prev.map((j) => (j.id === id ? { ...j, status: 'pending', progress: 0, error: undefined } : j))
    )
  }

  const deleteJob = (id: string) => {
    setJobs((prev) => prev.filter((j) => j.id !== id))
    setSelectedJobs((prev) => {
      const next = new Set(prev)
      next.delete(id)
      return next
    })
  }

  const stats = {
    total: jobs.length,
    pending: jobs.filter((j) => j.status === 'pending').length,
    processing: jobs.filter((j) => ['processing', 'uploading'].includes(j.status)).length,
    completed: jobs.filter((j) => j.status === 'completed').length,
    failed: jobs.filter((j) => j.status === 'failed').length,
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">Upload Queue</h3>
          <p className="text-sm text-muted">Manage content distribution</p>
        </div>
        <div className="flex items-center gap-3">
          {selectedJobs.size > 0 && (
            <motion.button
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex items-center gap-2 px-4 py-2 bg-danger/10 text-danger rounded-lg text-sm font-medium hover:bg-danger/20 transition-colors"
              onClick={() => {
                selectedJobs.forEach((id) => deleteJob(id))
              }}
            >
              <Trash2 className="w-4 h-4" />
              Delete {selectedJobs.size}
            </motion.button>
          )}
          <button className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-hover transition-colors">
            <Play className="w-4 h-4" />
            Process All
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-5 gap-3">
        {[
          { label: 'Total', value: stats.total, color: 'text-white' },
          { label: 'Pending', value: stats.pending, color: 'text-muted' },
          { label: 'Processing', value: stats.processing, color: 'text-primary' },
          { label: 'Completed', value: stats.completed, color: 'text-success' },
          { label: 'Failed', value: stats.failed, color: 'text-danger' },
        ].map((s) => (
          <div
            key={s.label}
            className="bg-surface border border-border rounded-lg p-3 text-center cursor-pointer hover:border-primary/30 transition-colors"
            onClick={() => setFilter(s.label.toLowerCase() === 'total' ? 'all' : s.label.toLowerCase())}
          >
            <div className={`text-xl font-bold ${s.color}`}>{s.value}</div>
            <div className="text-xs text-muted">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Search & Filter */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
          <input
            type="text"
            placeholder="Search by title or genre..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-surface border border-border rounded-lg text-sm text-white placeholder:text-muted focus:outline-none focus:border-primary"
          />
        </div>
        <div className="flex items-center gap-2 bg-surface border border-border rounded-lg p-1">
          {['all', 'pending', 'processing', 'completed', 'failed'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors capitalize ${
                filter === f ? 'bg-primary text-white' : 'text-muted hover:text-white'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Jobs List */}
      <div className="space-y-2">
        <AnimatePresence>
          {filteredJobs.map((job) => {
            const PlatformIcon = platformIcons[job.platform] || Cloud
            const status = statusConfig[job.status]
            const StatusIcon = status.icon

            return (
              <motion.div
                key={job.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className={`bg-surface border rounded-xl p-4 transition-colors ${
                  selectedJobs.has(job.id) ? 'border-primary' : 'border-border hover:border-border/80'
                }`}
              >
                <div className="flex items-center gap-4">
                  {/* Checkbox */}
                  <input
                    type="checkbox"
                    checked={selectedJobs.has(job.id)}
                    onChange={() => toggleSelection(job.id)}
                    className="w-4 h-4 rounded border-border bg-surface text-primary focus:ring-primary"
                  />

                  {/* Platform Icon */}
                  <div className={`w-10 h-10 rounded-lg bg-surface-hover flex items-center justify-center`}>
                    <PlatformIcon className={`w-5 h-5 ${platformColors[job.platform]}`} />
                  </div>

                  {/* Job Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-white truncate">{job.title}</span>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-surface-hover text-muted">
                        {job.genre}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 mt-1">
                      <span className={`text-xs flex items-center gap-1 ${status.color}`}>
                        <StatusIcon className={`w-3 h-3 ${job.status === 'processing' || job.status === 'uploading' ? 'animate-spin' : ''}`} />
                        {status.label}
                      </span>
                      {job.scheduledFor && (
                        <span className="text-xs text-muted flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {job.scheduledFor}
                        </span>
                      )}
                      {job.completedAt && (
                        <span className="text-xs text-muted">{job.completedAt}</span>
                      )}
                      {job.error && (
                        <span className="text-xs text-danger">{job.error}</span>
                      )}
                    </div>
                  </div>

                  {/* Progress */}
                  <div className="w-32">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-muted">Progress</span>
                      <span className="text-white">{job.progress}%</span>
                    </div>
                    <div className="w-full bg-surface-hover rounded-full h-1.5">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${job.progress}%` }}
                        transition={{ duration: 0.5 }}
                        className={`h-1.5 rounded-full ${
                          job.status === 'failed'
                            ? 'bg-danger'
                            : job.status === 'completed'
                            ? 'bg-success'
                            : 'bg-primary'
                        }`}
                      />
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-1">
                    {job.status === 'failed' && (
                      <button
                        onClick={() => retryJob(job.id)}
                        className="p-2 rounded-lg hover:bg-surface-hover text-muted hover:text-white transition-colors"
                        title="Retry"
                      >
                        <RotateCcw className="w-4 h-4" />
                      </button>
                    )}
                    {(job.status === 'processing' || job.status === 'uploading') && (
                      <button
                        className="p-2 rounded-lg hover:bg-surface-hover text-muted hover:text-white transition-colors"
                        title="Pause"
                      >
                        <Pause className="w-4 h-4" />
                      </button>
                    )}
                    <button
                      onClick={() => deleteJob(job.id)}
                      className="p-2 rounded-lg hover:bg-danger/10 text-muted hover:text-danger transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </AnimatePresence>

        {filteredJobs.length === 0 && (
          <div className="text-center py-12">
            <Filter className="w-8 h-8 text-muted mx-auto mb-3" />
            <p className="text-muted">No jobs match your filters</p>
          </div>
        )}
      </div>
    </div>
  )
}
