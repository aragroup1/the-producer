'use client'

import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import DashboardOverview from './components/DashboardOverview'
import BeatBrowser from './components/BeatBrowser'
import RenderQueue from './components/RenderQueue'
import AnalyticsPanel from './components/AnalyticsPanel'
import MarketingDashboard from './components/MarketingDashboard'
import UploadQueue from './components/UploadQueue'
import ChannelAnalytics from './components/ChannelAnalytics'
import TrendMonitor from './components/TrendMonitor'
import RuleManager from './components/RuleManager'
import SettingsPanel from './components/SettingsPanel'

export default function Home() {
  const [activeTab, setActiveTab] = useState('overview')

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <DashboardOverview />
      case 'beats':
        return <BeatBrowser />
      case 'queue':
        return <RenderQueue />
      case 'analytics':
        return <AnalyticsPanel />
      case 'marketing':
        return <MarketingDashboard />
      case 'uploads':
        return <UploadQueue />
      case 'channels':
        return <ChannelAnalytics />
      case 'trends':
        return <TrendMonitor />
      case 'rules':
        return <RuleManager />
      case 'settings':
        return <SettingsPanel />
      default:
        return <DashboardOverview />
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
