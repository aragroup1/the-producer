'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Clock,
  CheckCircle2,
  XCircle,
  Loader2,
  RotateCcw,
  AlertTriangle,
  Zap,
} from 'lucide-react'

interface Job {
  id: string
  beatId: string
  beatTitle: string
  type: string
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'retrying'
  priority: number
  workerId: string | null
  progress: number
  startedAt: string | null
  duration: string | null
}

const mockJobs: Job[] = [
  { id: '1', beatId: 'b1', beatTitle: 'Dark Trap Beat #234', type: 'midi_generation', status: 'completed', priority: 5, workerId: 'midi-1', progress: 100, startedAt: '10:23', duration: '12s' },
  { id: '2', beatId: 'b1', beatTitle: 'Dark Trap Beat #234', type: 'sound_assignment', status: 'completed', priority: 5, workerId: 'sound-1', progress: 100, startedAt: '10:24', duration: '3s' },
  { id: '3', beatId: 'b1', beatTitle: 'Dark Trap Beat #234', type: 'vst_render', status: 'processing', priority: 5, workerId: 'sound-1', progress: 65, startedAt: '10:25', duration: null },
  { id: '4', beatId: 'b2', beatTitle: 'Melodic Drill #189', type: 'midi_generation', status: 'processing', priority: 5, workerId: 'midi-2', progress: 45, startedAt: '10:26', duration: null },
  { id: '5', beatId: 'b3', beatTitle: 'LoFi Chill #456', type: 'mixing', status: 'queued', priority: 3, workerId: null, progress: 0, startedAt: null, duration: null },
  { id: '6', beatId: 'b4', beatTitle: 'Afro Swing #321', type: 'mastering', status: 'queued', priority: 5, workerId: null, progress: 0, startedAt: null, duration: null },
  { id: '7', beatId: 'b5', beatTitle: 'Rage Type Beat', type: 'qc', status: 'failed', priority: 5, workerId: 'qc-1', progress: 0, startedAt: '10:20', duration: '8s' },
  { id: '8', beatId: 'b6', beatTitle: 'Cinematic Trap', type: 'export', status: 'queued', priority: 7, workerId: null, progress: 0, startedAt: null, duration: null },
]

export default function RenderQueue() {
  const [jobs, setJobs] = useState(mockJobs)

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-success" />
      case 'processing':
        return <Loader2 className="w-4 h-4 text-primary animate-spin" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-danger" />
      case 'retrying':
        return <RotateCcw className="w-4 h-4 text-warning animate-spin" />
      default:
        return <Clock className="w-4 h-4 text-muted" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-success/10 text-success border-success/20'
      case 'processing':
        return 'bg-primary/10 text-primary border-primary/20'
      case 'failed':
        return 'bg-danger/10 text-danger border-danger/20'
      case 'retrying':
        return 'bg-warning/10 text-warning border-warning/20'
      default:
        return 'bg-muted/10 text-muted border-muted/20'
    }
  }

  const stats = {
    queued: jobs.filter((j) => j.status === 'queued').length,
    processing: jobs.filter((j) => j.status === 'processing').length,
    completed: jobs.filter((j) => j.status === 'completed').length,
    failed: jobs.filter((j) => j.status === 'failed').length,
  }

  return (
    <div className="space-y-6">
      {/* Queue Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Queued', value: stats.queued, icon: Clock, color: 'text-muted' },
          { label: 'Processing', value: stats.processing, icon: Zap, color: 'text-primary' },
          { label: 'Completed', value: stats.completed, icon: CheckCircle2, color: 'text-success' },
          { label: 'Failed', value: stats.failed, icon: AlertTriangle, color: 'text-danger' },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="bg-surface border border-border rounded-xl p-4"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-white">{stat.value}</p>
                <p className="text-xs text-muted">{stat.label}</p>
              </div>
              <stat.icon className={`w-5 h-5 ${stat.color}`} />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Jobs Table */}
      <div className="bg-surface border border-border rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-border">
          <h3 className="text-lg font-semibold text-white">Active Jobs</h3>
        </div>

        <div className="divide-y divide-border">
          {jobs.map((job, index) => (
            <motion.div
              key={job.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: index * 0.05 }}
              className="px-6 py-4 hover:bg-surface-hover transition-colors"
            >
              <div className="flex items-center gap-4">
                {/* Status Icon */}
                <div className="w-8 flex justify-center">
                  {getStatusIcon(job.status)}
                </div>

                {/* Job Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-white">{job.beatTitle}</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(job.status)}`}>
                      {job.status}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 mt-1 text-xs text-muted">
                    <span className="capitalize">{job.type.replace('_', ' ')}</span>
                    <span>Priority: {job.priority}</span>
                    {job.workerId && <span>Worker: {job.workerId}</span>}
                    {job.startedAt && <span>Started: {job.startedAt}</span>}
                    {job.duration && <span>Duration: {job.duration}</span>}
                  </div>
                </div>

                {/* Progress */}
                {job.status === 'processing' && (
                  <div className="w-32">
                    <div className="flex items-center justify-between text-xs text-muted mb-1">
                      <span>Progress</span>
                      <span>{job.progress}%</span>
                    </div>
                    <div className="h-1.5 bg-background rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-primary rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${job.progress}%` }}
                        transition={{ duration: 1 }}
                      />
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center gap-2">
                  {job.status === 'failed' && (
                    <button className="p-1.5 text-warning hover:bg-warning/10 rounded-lg transition-colors">
                      <RotateCcw className="w-4 h-4" />
                    </button>
                  )}
                  {job.status === 'queued' && (
                    <button className="p-1.5 text-danger hover:bg-danger/10 rounded-lg transition-colors">
                      <XCircle className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
