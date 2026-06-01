'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Save,
  Key,
  Database,
  Cloud,
  Music,
  Cpu,
  Bell,
  Shield,
} from 'lucide-react'

interface SettingSectionProps {
  title: string
  icon: React.ElementType
  children: React.ReactNode
  delay: number
}

function SettingSection({ title, icon: Icon, children, delay }: SettingSectionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="bg-surface border border-border rounded-xl p-6"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
          <Icon className="w-5 h-5 text-primary" />
        </div>
        <h3 className="text-lg font-semibold text-white">{title}</h3>
      </div>
      {children}
    </motion.div>
  )
}

interface InputFieldProps {
  label: string
  type?: string
  placeholder?: string
  defaultValue?: string
  description?: string
}

function InputField({ label, type = 'text', placeholder, defaultValue, description }: InputFieldProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-white">{label}</label>
      {description && (
        <p className="text-xs text-muted">{description}</p>
      )}
      <input
        type={type}
        defaultValue={defaultValue}
        placeholder={placeholder}
        className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-muted focus:outline-none focus:border-primary transition-colors"
      />
    </div>
  )
}

function ToggleField({ label, description, defaultChecked = false }: { label: string; description?: string; defaultChecked?: boolean }) {
  const [checked, setChecked] = useState(defaultChecked)

  return (
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-white">{label}</p>
        {description && (
          <p className="text-xs text-muted">{description}</p>
        )}
      </div>
      <button
        onClick={() => setChecked(!checked)}
        className={`relative w-11 h-6 rounded-full transition-colors ${
          checked ? 'bg-primary' : 'bg-muted/30'
        }`}
      >
        <div
          className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
            checked ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  )
}

export default function SettingsPanel() {
  return (
    <div className="space-y-6 max-w-4xl">
      {/* Save Button */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">System Settings</h2>
        <button className="flex items-center gap-2 bg-primary hover:bg-primary-hover text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          <Save className="w-4 h-4" />
          Save Changes
        </button>
      </div>

      {/* API Keys */}
      <SettingSection title="API Keys" icon={Key} delay={0}>
        <div className="space-y-4">
          <InputField
            label="Secret Key"
            type="password"
            defaultValue="dev-secret-key-change-in-production"
            description="Used for JWT token signing. Change in production."
          />
          <InputField
            label="Shopify API Key"
            placeholder="shpat_..."
            description="Your Shopify private app API key"
          />
          <InputField
            label="Shopify Store URL"
            placeholder="your-store.myshopify.com"
          />
        </div>
      </SettingSection>

      {/* Database */}
      <SettingSection title="Database" icon={Database} delay={0.1}>
        <div className="space-y-4">
          <InputField
            label="Database URL"
            defaultValue="postgresql://aimusic:password@localhost:5432/aimusic"
            description="PostgreSQL connection string"
          />
          <InputField
            label="Redis URL"
            defaultValue="redis://localhost:6379/0"
            description="Redis connection string for queues"
          />
          <ToggleField
            label="Enable Connection Pooling"
            description="Pool database connections for better performance"
            defaultChecked={true}
          />
        </div>
      </SettingSection>

      {/* Audio Settings */}
      <SettingSection title="Audio Settings" icon={Music} delay={0.2}>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <InputField
              label="Sample Rate"
              defaultValue="44100"
              description="Hz"
            />
            <InputField
              label="Bit Depth"
              defaultValue="24"
              description="bits"
            />
          </div>
          <InputField
            label="VST Path"
            defaultValue="./vsts"
            description="Directory containing VST plugins"
          />
          <InputField
            label="Soundfont Path"
            defaultValue="./soundfonts"
            description="Directory containing SF2 files"
          />
          <ToggleField
            label="Enable GPU Rendering"
            description="Use CUDA for AI model inference"
            defaultChecked={false}
          />
        </div>
      </SettingSection>

      {/* Generation Settings */}
      <SettingSection title="Generation Settings" icon={Cpu} delay={0.3}>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <InputField
              label="Default BPM Min"
              defaultValue="60"
            />
            <InputField
              label="Default BPM Max"
              defaultValue="200"
            />
          </div>
          <InputField
            label="Default Duration"
            defaultValue="180"
            description="Seconds"
          />
          <InputField
            label="Max Concurrent Jobs"
            defaultValue="10"
            description="Maximum parallel render jobs"
          />
          <ToggleField
            label="Auto-Approve High Quality"
            description="Automatically publish beats with QC score > 8.0"
            defaultChecked={false}
          />
          <ToggleField
            label="Auto-Upload to Shopify"
            description="Automatically upload approved beats to store"
            defaultChecked={false}
          />
        </div>
      </SettingSection>

      {/* Notifications */}
      <SettingSection title="Notifications" icon={Bell} delay={0.4}>
        <div className="space-y-4">
          <ToggleField
            label="Email on Sale"
            description="Send email when a beat is purchased"
            defaultChecked={true}
          />
          <ToggleField
            label="Email on QC Failure"
            description="Send email when a beat fails quality control"
            defaultChecked={true}
          />
          <ToggleField
            label="Daily Summary"
            description="Receive daily generation and sales summary"
            defaultChecked={false}
          />
        </div>
      </SettingSection>

      {/* Security */}
      <SettingSection title="Security" icon={Shield} delay={0.5}>
        <div className="space-y-4">
          <ToggleField
            label="Enable Rate Limiting"
            description="Limit API requests per IP"
            defaultChecked={true}
          />
          <InputField
            label="Rate Limit (requests/minute)"
            defaultValue="100"
          />
          <ToggleField
            label="Require Auth for API"
            description="All API endpoints require authentication"
            defaultChecked={true}
          />
        </div>
      </SettingSection>
    </div>
  )
}
