'use client'

import { motion } from 'framer-motion'
import { Calendar, Users, Download, Filter } from 'lucide-react'
import { useState } from 'react'

export function ControlsPanel() {
  const [selectedMR, setSelectedMR] = useState<number>(1201911108)
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0])

  const handleExport = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/export/gpx?mr_id=${selectedMR}&date=${selectedDate}`)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `mr-route-${selectedMR}-${selectedDate}.gpx`
      a.click()
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.6 }}
      className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6 mx-6 mb-8"
    >
      <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
        {/* Left Controls */}
        <div className="flex flex-col md:flex-row gap-4 flex-1">
          {/* MR Selector */}
          <div className="min-w-64">
            <label className="block text-white/70 text-sm font-medium mb-2 flex items-center">
              <Users className="w-4 h-4 mr-2" />
              Medical Representative
            </label>
            <motion.select
              whileFocus={{ scale: 1.02 }}
              value={selectedMR}
              onChange={(e) => setSelectedMR(Number(e.target.value))}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white focus:border-blue-400 focus:outline-none transition-all backdrop-blur-sm"
            >
              <option value={1201911108} className="bg-gray-800">Vishesh Sanghvi</option>
              <option value={987654321} className="bg-gray-800">John Doe</option>
              <option value={123456789} className="bg-gray-800">Jane Smith</option>
            </motion.select>
          </div>

          {/* Date Selector */}
          <div className="min-w-48">
            <label className="block text-white/70 text-sm font-medium mb-2 flex items-center">
              <Calendar className="w-4 h-4 mr-2" />
              Date
            </label>
            <motion.input
              whileFocus={{ scale: 1.02 }}
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white focus:border-blue-400 focus:outline-none transition-all backdrop-blur-sm"
            />
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex gap-3">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleExport}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all"
          >
            <Download className="w-4 h-4" />
            Export GPX
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-2 px-6 py-3 bg-white/10 border border-white/20 text-white rounded-xl font-medium hover:bg-white/20 transition-all backdrop-blur-sm"
          >
            <Filter className="w-4 h-4" />
            Filters
          </motion.button>
        </div>
      </div>
    </motion.div>
  )
}
