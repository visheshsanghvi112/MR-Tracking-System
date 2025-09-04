'use client'

import { motion } from 'framer-motion'
import { Users, MapPin, Route, Clock, TrendingUp } from 'lucide-react'

import type { LucideIcon } from 'lucide-react'

interface StatCardProps {
  icon: LucideIcon
  title: string
  value: string
  change?: string
  color: string
  delay: number
}

function StatCard({ icon: Icon, title, value, change, color, delay }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      whileHover={{ scale: 1.05, y: -10 }}
      className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6 relative overflow-hidden group"
    >
      {/* Background gradient */}
      <div className={`absolute inset-0 bg-gradient-to-br ${color} opacity-20 group-hover:opacity-30 transition-opacity`} />
      
      {/* Content */}
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <div className={`p-3 rounded-xl bg-gradient-to-br ${color} shadow-lg`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
          {change && (
            <div className="flex items-center text-green-400 text-sm font-medium">
              <TrendingUp className="w-4 h-4 mr-1" />
              {change}
            </div>
          )}
        </div>
        
        <h3 className="text-white/70 text-sm font-medium mb-1">{title}</h3>
        <p className="text-white text-2xl font-bold">{value}</p>
      </div>
    </motion.div>
  )
}

export function StatsGrid() {
  const stats = [
    {
      icon: Users,
      title: "Active MRs",
      value: "12",
      change: "+3",
      color: "from-blue-500 to-blue-600",
      delay: 0.1
    },
    {
      icon: MapPin,
      title: "Total Visits",
      value: "248",
      change: "+12%",
      color: "from-green-500 to-green-600",
      delay: 0.2
    },
    {
      icon: Route,
      title: "Distance Covered",
      value: "1,247 km",
      change: "+8.2%",
      color: "from-purple-500 to-purple-600",
      delay: 0.3
    },
    {
      icon: Clock,
      title: "Avg Response Time",
      value: "2.4 min",
      change: "-15%",
      color: "from-orange-500 to-orange-600",
      delay: 0.4
    }
  ]

  return (
    <div className="container mx-auto px-6 py-8">
      <motion.h2 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="text-2xl font-bold text-white mb-6"
      >
        Performance Overview
      </motion.h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <StatCard key={index} {...stat} />
        ))}
      </div>
    </div>
  )
}
