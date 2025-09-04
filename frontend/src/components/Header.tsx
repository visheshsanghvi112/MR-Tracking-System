'use client'

import { motion } from 'framer-motion'
import { MapPin, Activity } from 'lucide-react'

export function Header() {
  return (
    <motion.header 
      initial={{ opacity: 0, y: -50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="bg-white/10 backdrop-blur-md border-b border-white/20 p-6"
    >
      <div className="container mx-auto flex items-center justify-between">
        {/* Logo & Title */}
        <div className="flex items-center gap-4">
          <motion.div 
            whileHover={{ rotate: 360 }}
            transition={{ duration: 0.5 }}
            className="bg-gradient-to-r from-blue-500 to-purple-600 p-3 rounded-xl shadow-lg"
          >
            <MapPin className="w-8 h-8 text-white" />
          </motion.div>
          <div>
            <h1 className="text-3xl font-bold text-white">
              MR Tracking
            </h1>
            <p className="text-white/70">Real-time Location Intelligence</p>
          </div>
        </div>

        {/* Status Indicator */}
        <motion.div 
          whileHover={{ scale: 1.05 }}
          className="bg-green-500/20 border border-green-500/30 rounded-full px-6 py-3 flex items-center gap-3"
        >
          <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse" />
          <div>
            <p className="text-green-400 font-semibold">System Online</p>
            <p className="text-white/60 text-sm">All services active</p>
          </div>
          <Activity className="w-5 h-5 text-green-400" />
        </motion.div>
      </div>
    </motion.header>
  )
}
