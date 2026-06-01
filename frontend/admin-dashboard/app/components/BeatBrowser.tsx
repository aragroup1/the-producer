'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Music,
  Play,
  Pause,
  Download,
  CheckCircle2,
  XCircle,
  Filter,
  Search,
  SlidersHorizontal,
} from 'lucide-react'

interface Beat {
  id: string
  title: string
  genre: string
  bpm: number
  key: string
  duration: string
  quality: number | null
  status: string
  createdAt: string
}

const mockBeats: Beat[] = [
  { id: '1', title: 'Dark Trap Beat #001', genre: 'Trap', bpm: 140, key: 'C min', duration: '2:45', quality: 8.5, status: 'published', createdAt: '2024-01-15' },
  { id: '2', title: 'Melodic Drill #045', genre: 'Drill', bpm: 145, key: 'D min', duration: '3:12', quality: 7.9, status: 'published', createdAt: '2024-01-14' },
  { id: '3', title: 'LoFi Study Session', genre: 'Lo-Fi', bpm: 82, key: 'A min', duration: '2:30', quality: 8.2, status: 'approved', createdAt: '2024-01-14' },
  { id: '4', title: 'Afro Swing Vibe', genre: 'Afrobeats', bpm: 105, key: 'F maj', duration: '2:58', quality: 7.5, status: 'qc', createdAt: '2024-01-13' },
  { id: '5', title: 'Rage Type Beat', genre: 'Rage', bpm: 150, key: 'C min', duration: '2:20', quality: null, status: 'mixing', createdAt: '2024-01-13' },
  { id: '6', title: 'Cinematic Trap', genre: 'Cinematic', bpm: 135, key: 'G min', duration: '3:05', quality: null, status: 'rendering', createdAt: '2024-01-12' },
  { id: '7', title: 'Emotional Guitar', genre: 'Trap', bpm: 138, key: 'E min', duration: '2:50', quality: 6.8, status: 'rejected', createdAt: '2024-01-12' },
  { id: '8', title: 'UK Drill Hard', genre: 'Drill', bpm: 142, key: 'F min', duration: '2:35', quality: 8.8, status: 'published', createdAt: '2024-01-11' },
]

export default function BeatBrowser() {
  const [playingId, setPlayingId] = useState<string | null>(null)
  const [filterGenre, setFilterGenre] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  const filteredBeats = mockBeats.filter((beat) => {
    if (filterGenre !== 'all' && beat.genre !== filterGenre) return false
    if (filterStatus !== 'all' && beat.status !== filterStatus) return false
    if (searchQuery && !beat.title.toLowerCase().includes(searchQuery.toLowerCase())) return false
    return true
  })

  const genres = ['all', ...Array.from(new Set(mockBeats.map((b) => b.genre)))]
  const statuses = ['all', ...Array.from(new Set(mockBeats.map((b) => b.status)))]

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
          <input
            type="text"
            placeholder="Search beats..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-surface border border-border rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder:text-muted focus:outline-none focus:border-primary"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-muted" />
          <select
            value={filterGenre}
            onChange={(e) => setFilterGenre(e.target.value)}
            className="bg-surface border border-border rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-primary"
          >
            {genres.map((g) => (
              <option key={g} value={g}>
                {g === 'all' ? 'All Genres' : g}
              </option>
            ))}
          </select>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="bg-surface border border-border rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-primary"
          >
            {statuses.map((s) => (
              <option key={s} value={s}>
                {s === 'all' ? 'All Statuses' : s}
              </option>
            ))}
          </select>
        </div>

        <button className="flex items-center gap-2 text-sm text-muted hover:text-white transition-colors">
          <SlidersHorizontal className="w-4 h-4" />
          Advanced
        </button>
      </div>

      {/* Beat Grid */}
      <div className="grid grid-cols-1 gap-3">
        {filteredBeats.map((beat, index) => (
          <motion.div
            key={beat.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className="bg-surface border border-border rounded-xl p-4 hover:border-primary/30 transition-colors"
          >
            <div className="flex items-center gap-4">
              {/* Play Button */}
              <button
                onClick={() => setPlayingId(playingId === beat.id ? null : beat.id)}
                className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center hover:bg-primary/20 transition-colors"
              >
                {playingId === beat.id ? (
                  <Pause className="w-5 h-5 text-primary" />
                ) : (
                  <Play className="w-5 h-5 text-primary ml-0.5" />
                )}
              </button>

              {/* Beat Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3">
                  <h3 className="text-sm font-medium text-white truncate">{beat.title}</h3>
                  <StatusBadge status={beat.status} />
                </div>
                <div className="flex items-center gap-4 mt-1 text-xs text-muted">
                  <span>{beat.genre}</span>
                  <span>{beat.bpm} BPM</span>
                  <span>Key: {beat.key}</span>
                  <span>{beat.duration}</span>
                  <span>{beat.createdAt}</span>
                </div>
              </div>

              {/* Quality Score */}
              {beat.quality !== null && (
                <div className="flex items-center gap-2">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold ${
                    beat.quality >= 8 ? 'bg-success/10 text-success' :
                    beat.quality >= 6 ? 'bg-warning/10 text-warning' :
                    'bg-danger/10 text-danger'
                  }`}>
                    {beat.quality}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center gap-2">
                <button className="p-2 text-muted hover:text-white transition-colors">
                  <Download className="w-4 h-4" />
                </button>
                {beat.status === 'qc' && (
                  <>
                    <button className="p-2 text-success hover:text-success/80 transition-colors">
                      <CheckCircle2 className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-danger hover:text-danger/80 transition-colors">
                      <XCircle className="w-4 h-4" />
                    </button>
                  </>
                )}
              </div>
            </div>

            {/* Waveform Placeholder */}
            {playingId === beat.id && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 60, opacity: 1 }}
                className="mt-3 bg-background rounded-lg overflow-hidden"
              >
                <div className="h-full flex items-center justify-center text-muted text-xs">
                  Waveform visualization would appear here
                </div>
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    published: 'bg-success/10 text-success border-success/20',
    approved: 'bg-success/10 text-success border-success/20',
    qc: 'bg-warning/10 text-warning border-warning/20',
    mixing: 'bg-secondary/10 text-secondary border-secondary/20',
    rendering: 'bg-primary/10 text-primary border-primary/20',
    rejected: 'bg-danger/10 text-danger border-danger/20',
  }

  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${styles[status] || 'bg-muted/10 text-muted border-muted/20'}`}>
      {status}
    </span>
  )
}
