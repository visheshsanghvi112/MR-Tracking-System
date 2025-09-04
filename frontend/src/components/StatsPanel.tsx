'use client'

import { RouteStats } from '@/hooks/useRouteData'
import { MapPin, Clock, TrendingUp, DollarSign } from 'lucide-react'

interface StatsPanelProps {
  stats: RouteStats | null
  loading: boolean
}

export function StatsPanel({ stats, loading }: StatsPanelProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Today&apos;s Summary</h3>
        <div className="grid grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-gray-50 p-3 rounded-lg animate-pulse">
              <div className="h-4 bg-gray-200 rounded mb-2"></div>
              <div className="h-6 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="text-center text-gray-500 py-8">
        <MapPin className="h-12 w-12 mx-auto mb-4 text-gray-300" />
        <p>Select an MR to view statistics</p>
      </div>
    )
  }

  const statItems = [
    {
      label: 'Distance',
      value: `${stats.distance_km} km`,
      icon: TrendingUp,
      color: 'text-blue-600'
    },
    {
      label: 'Visits',
      value: stats.visits.toString(),
      icon: MapPin,
      color: 'text-green-600'
    },
    {
      label: 'Active Hours',
      value: `${stats.active_hours}h`,
      icon: Clock,
      color: 'text-purple-600'
    },
    {
      label: 'Expenses',
      value: `₹${stats.expenses_total}`,
      icon: DollarSign,
      color: 'text-red-600'
    }
  ]

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Today&apos;s Summary</h3>
      
      <div className="grid grid-cols-2 gap-4">
        {statItems.map((item) => (
          <div key={item.label} className="bg-gray-50 p-3 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <item.icon className={`h-4 w-4 ${item.color}`} />
              <span className="text-sm text-gray-600">{item.label}</span>
            </div>
            <div className="text-xl font-bold text-gray-900">{item.value}</div>
          </div>
        ))}
      </div>

      {stats.first_location && stats.last_location && (
        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <div className="text-sm text-gray-600 mb-1">Route</div>
          <div className="text-sm">
            <span className="font-medium">{stats.first_location}</span>
            <span className="text-gray-400 mx-2">→</span>
            <span className="font-medium">{stats.last_location}</span>
          </div>
        </div>
      )}
    </div>
  )
}
