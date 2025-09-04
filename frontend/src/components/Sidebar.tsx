'use client'

import { motion } from 'framer-motion'
import { Navigation, Zap } from 'lucide-react'
import { useRouteData } from '@/hooks/useRouteData'

interface SidebarProps {
  selectedMR: number
  selectedDate: string
}

export function Sidebar({ selectedMR, selectedDate }: SidebarProps) {
  const { routeData, stats, loading } = useRouteData(selectedMR, selectedDate)

  return (
    <motion.div 
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6, delay: 1 }}
      className="space-y-6"
    >
      {/* Route Summary */}
      <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
        <h3 className="text-white text-lg font-semibold mb-4 flex items-center">
          <Navigation className="w-5 h-5 mr-2" />
          Route Summary
        </h3>
        
        {loading ? (
          <div className="space-y-3">
            {[1,2,3,4].map(i => (
              <div key={i} className="h-4 bg-white/10 rounded animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-white/70">Total Distance</span>
              <span className="text-white font-semibold">
                {stats ? `${stats.distance_km.toFixed(1)} km` : '0 km'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-white/70">Active Hours</span>
              <span className="text-white font-semibold">
                {stats ? `${stats.active_hours.toFixed(1)}h` : '0h'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-white/70">Visits</span>
              <span className="text-green-400 font-semibold">
                {stats ? stats.visits : 0}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-white/70">Total Points</span>
              <span className="text-white font-semibold">
                {stats ? stats.total_points : 0}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Recent Activity */}
      <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
        <h3 className="text-white text-lg font-semibold mb-4 flex items-center">
          <Zap className="w-5 h-5 mr-2" />
          Recent Activity
        </h3>
        
        <div className="space-y-3">
          {routeData && routeData.slice(0, 5).map((point, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 1.2 + index * 0.1 }}
              className="flex items-center gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
            >
              <div className={`w-2 h-2 rounded-full ${
                point.type === 'visit' ? 'bg-green-400' :
                point.type === 'current' ? 'bg-blue-400' :
                'bg-gray-400'
              }`} />
              <div className="flex-1">
                <p className="text-white text-sm font-medium">{point.details}</p>
                <p className="text-white/60 text-xs">{point.location}</p>
              </div>
              <span className="text-white/60 text-xs">
                {new Date(point.timestamp).toLocaleTimeString('en-US', { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </span>
            </motion.div>
          ))}
          
          {(!routeData || routeData.length === 0) && !loading && (
            <div className="text-center text-white/60 py-8">
              <p>No activity data available</p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}
