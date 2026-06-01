'use client'

import {
  LayoutDashboard,
  Music,
  ListOrdered,
  BarChart3,
  Settings,
  Sparkles,
  Megaphone,
  Upload,
  Radio,
  TrendingUp,
  Shield,
} from 'lucide-react'
import { motion } from 'framer-motion'

interface SidebarProps {
  activeTab: string
  onTabChange: (tab: string) => void
}

const navItems = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'beats', label: 'Beat Browser', icon: Music },
  { id: 'queue', label: 'Render Queue', icon: ListOrdered },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  { id: 'marketing', label: 'Marketing', icon: Megaphone },
  { id: 'uploads', label: 'Upload Queue', icon: Upload },
  { id: 'channels', label: 'Channels', icon: Radio },
  { id: 'trends', label: 'Trends', icon: TrendingUp },
  { id: 'rules', label: 'Rules', icon: Shield },
  { id: 'settings', label: 'Settings', icon: Settings },
]

export default function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  return (
    <aside className="w-64 bg-surface border-r border-border flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-white">AI Producer</h1>
            <p className="text-xs text-muted">Music Production System</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = activeTab === item.id

          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`relative w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'text-white'
                  : 'text-muted hover:text-white hover:bg-surface-hover'
              }`}
            >
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute inset-0 bg-primary/10 rounded-lg border border-primary/20"
                  transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                />
              )}
              <Icon className="w-5 h-5 relative z-10" />
              <span className="relative z-10">{item.label}</span>
            </button>
          )
        })}
      </nav>

      {/* Status */}
      <div className="p-4 border-t border-border">
        <div className="flex items-center gap-2 text-xs text-muted">
          <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
          System Online
        </div>
        <div className="mt-2 text-xs text-muted">
          v1.0.0 — Local Mode
        </div>
      </div>
    </aside>
  )
}
