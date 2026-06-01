'use client'

import { Bell, Search, Plus } from 'lucide-react'

interface HeaderProps {
  activeTab: string
}

const tabTitles: Record<string, string> = {
  overview: 'Dashboard Overview',
  beats: 'Beat Browser',
  queue: 'Render Queue',
  analytics: 'Analytics & Insights',
  marketing: 'Marketing Analytics',
  uploads: 'Upload Queue',
  channels: 'Channel Analytics',
  trends: 'Trend Monitor',
  rules: 'Automation Rules',
  settings: 'System Settings',
}

export default function Header({ activeTab }: HeaderProps) {
  return (
    <header className="h-16 bg-surface border-b border-border flex items-center justify-between px-6">
      <h2 className="text-xl font-semibold text-white">
        {tabTitles[activeTab] || 'Dashboard'}
      </h2>

      <div className="flex items-center gap-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
          <input
            type="text"
            placeholder="Search beats..."
            className="w-64 bg-background border border-border rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder:text-muted focus:outline-none focus:border-primary"
          />
        </div>

        {/* Generate Button */}
        <button className="flex items-center gap-2 bg-primary hover:bg-primary-hover text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" />
          Generate Beat
        </button>

        {/* Notifications */}
        <button className="relative p-2 text-muted hover:text-white transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full" />
        </button>

        {/* User Avatar */}
        <div className="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center text-primary font-medium text-sm">
          AP
        </div>
      </div>
    </header>
  )
}
