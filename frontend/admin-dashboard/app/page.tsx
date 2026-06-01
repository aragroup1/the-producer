'use client'

import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import CommandCenter from './components/CommandCenter'
import BeatBrowser from './components/BeatBrowser'
import MarketingDashboard from './components/MarketingDashboard'
import RevenuePanel from './components/RevenuePanel'
import TrendMonitor from './components/TrendMonitor'
import AnalyticsPanel from './components/AnalyticsPanel'
import ChannelAnalytics from './components/ChannelAnalytics'
import SettingsPanel from './components/SettingsPanel'

export default function Home() {
  const [activeTab, setActiveTab] = useState('overview')

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <CommandCenter />
      case 'beats':
        return <BeatBrowser />
      case 'marketing':
        return <MarketingDashboard />
      case 'revenue':
        return <RevenuePanel />
      case 'trends':
        return <TrendMonitor />
      case 'analytics':
        return <AnalyticsPanel />
      case 'channels':
        return <ChannelAnalytics />
      case 'settings':
        return <SettingsPanel />
      default:
        return <CommandCenter />
    }
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header activeTab={activeTab} />
        <main className="flex-1 overflow-auto p-6">
          {renderContent()}
        </main>
      </div>
    </div>
  )
}
