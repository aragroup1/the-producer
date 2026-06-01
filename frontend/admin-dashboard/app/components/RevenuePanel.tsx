'use client'

import { motion } from 'framer-motion'
import { DollarSign, ShoppingCart, TrendingUp, Download, CreditCard, Package } from 'lucide-react'
import { useDashboardStats } from '../lib/hooks'

export default function RevenuePanel() {
  const { data: stats, isLoading } = useDashboardStats()

  const revenue = stats?.revenue || 0
  const totalSales = stats?.total_sales || 0
  const avgOrder = totalSales > 0 ? revenue / totalSales : 0

  return (
    <div className="space-y-6">
      {/* Revenue Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-surface border border-border rounded-xl p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-success" />
            </div>
            <div>
              <p className="text-sm text-muted">Total Revenue</p>
              <p className="text-2xl font-bold text-white">£{revenue.toLocaleString()}</p>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="bg-surface border border-border rounded-xl p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <ShoppingCart className="w-5 h-5 text-primary" />
            </div>
            <div>
              <p className="text-sm text-muted">Total Sales</p>
              <p className="text-2xl font-bold text-white">{totalSales}</p>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="bg-surface border border-border rounded-xl p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-secondary/10 flex items-center justify-center">
              <CreditCard className="w-5 h-5 text-secondary" />
            </div>
            <div>
              <p className="text-sm text-muted">Avg Order</p>
              <p className="text-2xl font-bold text-white">£{avgOrder.toFixed(2)}</p>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="bg-surface border border-border rounded-xl p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-accent" />
            </div>
            <div>
              <p className="text-sm text-muted">Conversion</p>
              <p className="text-2xl font-bold text-white">{stats?.conversion_rate || 0}%</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* License Tiers */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="bg-surface border border-border rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Basic Lease</h3>
            <span className="text-lg font-bold text-white">£29.99</span>
          </div>
          <ul className="space-y-2 text-xs text-muted">
            <li className="flex items-center gap-2"><CheckIcon /> MP3 file</li>
            <li className="flex items-center gap-2"><CheckIcon /> 10,000 streams</li>
            <li className="flex items-center gap-2"><CheckIcon /> Non-exclusive</li>
            <li className="flex items-center gap-2"><CheckIcon /> Credit required</li>
          </ul>
          <div className="mt-4 pt-3 border-t border-border">
            <div className="flex justify-between text-sm">
              <span className="text-muted">Sold</span>
              <span className="text-white font-medium">0</span>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }} className="bg-surface border border-primary/30 rounded-xl p-5 relative">
          <div className="absolute -top-2 left-4 px-2 py-0.5 bg-primary text-white text-[10px] font-bold rounded">POPULAR</div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Premium</h3>
            <span className="text-lg font-bold text-primary">£79.99</span>
          </div>
          <ul className="space-y-2 text-xs text-muted">
            <li className="flex items-center gap-2"><CheckIcon /> WAV + Stems</li>
            <li className="flex items-center gap-2"><CheckIcon /> 100,000 streams</li>
            <li className="flex items-center gap-2"><CheckIcon /> Non-exclusive</li>
            <li className="flex items-center gap-2"><CheckIcon /> Radio play allowed</li>
          </ul>
          <div className="mt-4 pt-3 border-t border-border">
            <div className="flex justify-between text-sm">
              <span className="text-muted">Sold</span>
              <span className="text-white font-medium">0</span>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="bg-surface border border-border rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Exclusive</h3>
            <span className="text-lg font-bold text-white">£299.99</span>
          </div>
          <ul className="space-y-2 text-xs text-muted">
            <li className="flex items-center gap-2"><CheckIcon /> All files + stems</li>
            <li className="flex items-center gap-2"><CheckIcon /> Unlimited streams</li>
            <li className="flex items-center gap-2"><CheckIcon /> Full ownership</li>
            <li className="flex items-center gap-2"><CheckIcon /> Removed from store</li>
          </ul>
          <div className="mt-4 pt-3 border-t border-border">
            <div className="flex justify-between text-sm">
              <span className="text-muted">Sold</span>
              <span className="text-white font-medium">0</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Recent Sales */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }} className="bg-surface border border-border rounded-xl p-5">
        <h3 className="text-sm font-semibold text-white mb-4">Recent Sales</h3>
        <div className="text-center py-8 text-muted">
          <Package className="w-10 h-10 mx-auto mb-2 opacity-30" />
          <p className="text-sm">No sales yet</p>
          <p className="text-xs mt-1">Sales will appear here once you start selling beats</p>
        </div>
      </motion.div>
    </div>
  )
}

function CheckIcon() {
  return (
    <svg className="w-3 h-3 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  )
}
