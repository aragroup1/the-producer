'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Zap,
  ToggleLeft,
  ToggleRight,
  Clock,
  Activity,
  TrendingUp,
  Calendar,
  AlertTriangle,
  Pause,
  Play,
  Plus,
  Trash2,
  Edit3,
  ChevronDown,
  ChevronUp,
  Shield,
  Flame,
} from 'lucide-react'

interface RuleCondition {
  metric: string
  operator: string
  value: any
}

interface Rule {
  id: string
  name: string
  description: string
  conditions: RuleCondition[]
  logicalOp: 'and' | 'or'
  action: string
  enabled: boolean
  triggerCount: number
  lastTriggered: string | null
  cooldownHours: number
}

const mockRules: Rule[] = [
  {
    id: 'rule1',
    name: 'High CTR Boost',
    description: 'When CTR exceeds 8%, increase upload frequency',
    conditions: [
      { metric: 'ctr', operator: '>', value: 8 },
      { metric: 'views_per_hour', operator: '>', value: 100 },
    ],
    logicalOp: 'and',
    action: 'increase_upload_frequency',
    enabled: true,
    triggerCount: 12,
    lastTriggered: '2 hours ago',
    cooldownHours: 6,
  },
  {
    id: 'rule2',
    name: 'Trend Spike',
    description: 'When a trend grows >100%, create urgent content',
    conditions: [
      { metric: 'trend_growth', operator: '>', value: 100 },
    ],
    logicalOp: 'and',
    action: 'create_urgent_content',
    enabled: true,
    triggerCount: 5,
    lastTriggered: '1 day ago',
    cooldownHours: 12,
  },
  {
    id: 'rule3',
    name: 'Weekend Boost',
    description: 'Increase promotion on weekends',
    conditions: [
      { metric: 'day_of_week', operator: 'in', value: [5, 6] },
    ],
    logicalOp: 'and',
    action: 'boost_promotion',
    enabled: true,
    triggerCount: 28,
    lastTriggered: '12 hours ago',
    cooldownHours: 24,
  },
  {
    id: 'rule4',
    name: 'New Genre Alert',
    description: 'When a new trending genre is detected',
    conditions: [
      { metric: 'trend_keyword', operator: 'contains', value: 'new' },
    ],
    logicalOp: 'and',
    action: 'notify_discord',
    enabled: false,
    triggerCount: 0,
    lastTriggered: null,
    cooldownHours: 24,
  },
  {
    id: 'rule5',
    name: 'Low Performer Pause',
    description: 'Pause uploads when CTR drops below 2%',
    conditions: [
      { metric: 'ctr', operator: '<', value: 2 },
      { metric: 'impressions', operator: '>', value: 500 },
    ],
    logicalOp: 'and',
    action: 'pause_uploads',
    enabled: true,
    triggerCount: 3,
    lastTriggered: '3 days ago',
    cooldownHours: 48,
  },
  {
    id: 'rule6',
    name: 'Viral Thumbnail',
    description: 'When A/B test finds a winning thumbnail',
    conditions: [
      { metric: 'ab_test_confidence', operator: '>', value: 0.95 },
      { metric: 'ab_test_ctr_improvement', operator: '>', value: 15 },
    ],
    logicalOp: 'and',
    action: 'apply_winner_globally',
    enabled: true,
    triggerCount: 8,
    lastTriggered: '5 hours ago',
    cooldownHours: 24,
  },
]

const actionLabels: Record<string, string> = {
  increase_upload_frequency: 'Increase Uploads',
  create_urgent_content: 'Create Content',
  boost_promotion: 'Boost Promotion',
  notify_discord: 'Send Notification',
  pause_uploads: 'Pause Uploads',
  apply_winner_globally: 'Apply Winner',
}

const actionColors: Record<string, string> = {
  increase_upload_frequency: 'text-success',
  create_urgent_content: 'text-danger',
  boost_promotion: 'text-primary',
  notify_discord: 'text-secondary',
  pause_uploads: 'text-warning',
  apply_winner_globally: 'text-accent',
}

export default function RuleManager() {
  const [rules, setRules] = useState<Rule[]>(mockRules)
  const [expandedRule, setExpandedRule] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [filterEnabled, setFilterEnabled] = useState<'all' | 'enabled' | 'disabled'>('all')

  const toggleRule = (id: string) => {
    setRules((prev) =>
      prev.map((r) => (r.id === id ? { ...r, enabled: !r.enabled } : r))
    )
  }

  const deleteRule = (id: string) => {
    setRules((prev) => prev.filter((r) => r.id !== id))
  }

  const filteredRules = rules.filter((r) => {
    if (filterEnabled === 'enabled') return r.enabled
    if (filterEnabled === 'disabled') return !r.enabled
    return true
  })

  const stats = {
    total: rules.length,
    enabled: rules.filter((r) => r.enabled).length,
    triggered: rules.reduce((sum, r) => sum + r.triggerCount, 0),
    active: rules.filter((r) => r.enabled && r.lastTriggered && r.lastTriggered.includes('hour')).length,
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">Automation Rules</h3>
          <p className="text-sm text-muted">IF/THEN rules for autonomous marketing</p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-hover transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Rule
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-3">
        {[
          { label: 'Total Rules', value: stats.total, icon: Shield, color: 'text-primary' },
          { label: 'Enabled', value: stats.enabled, icon: Play, color: 'text-success' },
          { label: 'Total Triggers', value: stats.triggered, icon: Zap, color: 'text-accent' },
          { label: 'Recently Active', value: stats.active, icon: Flame, color: 'text-danger' },
        ].map((s) => {
          const Icon = s.icon
          return (
            <div key={s.label} className="bg-surface border border-border rounded-lg p-4 text-center">
              <Icon className={`w-5 h-5 ${s.color} mx-auto mb-2`} />
              <div className="text-xl font-bold text-white">{s.value}</div>
              <div className="text-xs text-muted">{s.label}</div>
            </div>
          )
        })}
      </div>

      {/* Filter */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted">Filter:</span>
        {(['all', 'enabled', 'disabled'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilterEnabled(f)}
            className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-colors capitalize ${
              filterEnabled === f ? 'bg-primary text-white' : 'bg-surface text-muted hover:text-white border border-border'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Create Form (placeholder) */}
      <AnimatePresence>
        {showCreateForm && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-surface border border-primary/30 rounded-xl p-6"
          >
            <h4 className="text-sm font-medium text-white mb-4">Create New Rule</h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-muted mb-1 block">Rule Name</label>
                <input
                  type="text"
                  placeholder="e.g., High CTR Boost"
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm text-white placeholder:text-muted focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="text-xs text-muted mb-1 block">Action</label>
                <select className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm text-white focus:outline-none focus:border-primary">
                  {Object.entries(actionLabels).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="mt-4 flex items-center gap-3">
              <button
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 bg-surface-hover text-white rounded-lg text-sm hover:bg-surface transition-colors"
              >
                Cancel
              </button>
              <button className="px-4 py-2 bg-primary text-white rounded-lg text-sm hover:bg-primary-hover transition-colors">
                Create Rule
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Rules List */}
      <div className="space-y-3">
        <AnimatePresence>
          {filteredRules.map((rule) => {
            const isExpanded = expandedRule === rule.id
            const ToggleIcon = rule.enabled ? ToggleRight : ToggleLeft

            return (
              <motion.div
                key={rule.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className={`bg-surface border rounded-xl transition-colors ${
                  rule.enabled ? 'border-border' : 'border-border/50 opacity-70'
                }`}
              >
                {/* Rule Header */}
                <div
                  className="p-4 flex items-center gap-4 cursor-pointer"
                  onClick={() => setExpandedRule(isExpanded ? null : rule.id)}
                >
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      toggleRule(rule.id)
                    }}
                    className={`${rule.enabled ? 'text-success' : 'text-muted'}`}
                  >
                    <ToggleIcon className="w-6 h-6" />
                  </button>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-white">{rule.name}</span>
                      {rule.triggerCount > 10 && (
                        <span className="text-xs px-1.5 py-0.5 rounded bg-accent/20 text-accent">
                          {rule.triggerCount}x
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-muted truncate">{rule.description}</p>
                  </div>

                  <div className="flex items-center gap-4">
                    <span className={`text-xs font-medium ${actionColors[rule.action] || 'text-muted'}`}>
                      {actionLabels[rule.action] || rule.action}
                    </span>
                    {rule.lastTriggered && (
                      <span className="text-xs text-muted flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {rule.lastTriggered}
                      </span>
                    )}
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-muted" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-muted" />
                    )}
                  </div>
                </div>

                {/* Expanded Details */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="border-t border-border"
                    >
                      <div className="p-4 space-y-4">
                        {/* Conditions */}
                        <div>
                          <h5 className="text-xs font-medium text-muted mb-2 uppercase tracking-wider">
                            Conditions ({rule.logicalOp.toUpperCase()})
                          </h5>
                          <div className="space-y-2">
                            {rule.conditions.map((cond, i) => (
                              <div
                                key={i}
                                className="flex items-center gap-2 text-sm bg-surface-hover rounded-lg px-3 py-2"
                              >
                                <span className="text-primary font-medium">{cond.metric}</span>
                                <span className="text-muted">{cond.operator}</span>
                                <span className="text-white">{JSON.stringify(cond.value)}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Action */}
                        <div>
                          <h5 className="text-xs font-medium text-muted mb-2 uppercase tracking-wider">
                            Action
                          </h5>
                          <div className="flex items-center gap-2 text-sm bg-surface-hover rounded-lg px-3 py-2">
                            <Zap className="w-4 h-4 text-accent" />
                            <span className="text-white">{actionLabels[rule.action] || rule.action}</span>
                          </div>
                        </div>

                        {/* Meta */}
                        <div className="grid grid-cols-3 gap-3">
                          <div className="bg-surface-hover rounded-lg p-3 text-center">
                            <div className="text-lg font-bold text-white">{rule.triggerCount}</div>
                            <div className="text-xs text-muted">Times Triggered</div>
                          </div>
                          <div className="bg-surface-hover rounded-lg p-3 text-center">
                            <div className="text-lg font-bold text-white">{rule.cooldownHours}h</div>
                            <div className="text-xs text-muted">Cooldown</div>
                          </div>
                          <div className="bg-surface-hover rounded-lg p-3 text-center">
                            <div className="text-lg font-bold text-white">
                              {rule.lastTriggered || 'Never'}
                            </div>
                            <div className="text-xs text-muted">Last Triggered</div>
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-2 pt-2">
                          <button className="flex items-center gap-2 px-3 py-2 bg-surface-hover rounded-lg text-sm text-muted hover:text-white transition-colors">
                            <Edit3 className="w-4 h-4" />
                            Edit
                          </button>
                          <button
                            onClick={() => deleteRule(rule.id)}
                            className="flex items-center gap-2 px-3 py-2 bg-danger/10 rounded-lg text-sm text-danger hover:bg-danger/20 transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                            Delete
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>

      {filteredRules.length === 0 && (
        <div className="text-center py-12">
          <Shield className="w-8 h-8 text-muted mx-auto mb-3" />
          <p className="text-muted">No rules match your filter</p>
        </div>
      )}
    </div>
  )
}
