'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  Route, 
  Clock, 
  TrendingUp, 
  Download, 
  Filter,
  Calendar,
  Activity,
  Globe,
  Navigation
} from 'lucide-react';
import { MapView } from './MapView';
import { useRouteData } from '../hooks/useRouteData';

// Removed unused MR interface

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.6 }
  }
};

const cardHoverVariants = {
  rest: { scale: 1, y: 0 },
  hover: { 
    scale: 1.02, 
    y: -5
  }
};

import type { LucideIcon } from 'lucide-react';

const StatCard = ({ 
  icon: Icon, 
  title, 
  value, 
  change, 
  color = "from-blue-500 to-purple-600" 
}: {
  icon: LucideIcon;
  title: string;
  value: string;
  change?: string;
  color?: string;
}) => (
  <motion.div
    variants={itemVariants}
    whileHover="hover"
    initial="rest"
    className="relative overflow-hidden"
  >
    <motion.div
      variants={cardHoverVariants}
      className="glass rounded-2xl p-6 relative overflow-hidden group cursor-pointer"
    >
      {/* Gradient overlay */}
      <div className={`absolute inset-0 bg-gradient-to-br ${color} opacity-10 group-hover:opacity-20 transition-opacity duration-300`} />
      
      {/* Floating particles effect */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-2 right-2 w-2 h-2 bg-white rounded-full animate-ping" />
        <div className="absolute bottom-4 left-4 w-1 h-1 bg-white rounded-full float" />
      </div>
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <div className={`p-3 rounded-xl bg-gradient-to-br ${color} shadow-lg`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
          {change && (
            <span className="text-green-400 text-sm font-medium flex items-center">
              <TrendingUp className="w-4 h-4 mr-1" />
              {change}
            </span>
          )}
        </div>
        <h3 className="text-white/70 text-sm font-medium mb-1">{title}</h3>
        <p className="text-white text-2xl font-bold">{value}</p>
      </div>
    </motion.div>
  </motion.div>
);

export function MRDashboard() {
  const [selectedMR, setSelectedMR] = useState<number>(1201911108);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const { routeData, stats, loading, error } = useRouteData(selectedMR, selectedDate);

  // Animated background particles
  useEffect(() => {
    const particles = document.querySelectorAll('.particle');
    particles.forEach((particle, index) => {
      (particle as HTMLElement).style.animationDelay = `${index * 0.5}s`;
    });
  }, []);

  const handleExport = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/export/gpx?mr_id=${selectedMR}&date=${selectedDate}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `mr-route-${selectedMR}-${selectedDate}.gpx`;
      a.click();
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated background elements */}
      <div className="fixed inset-0 pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="particle absolute w-2 h-2 bg-white/10 rounded-full float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDuration: `${3 + Math.random() * 4}s`,
              animationDelay: `${Math.random() * 2}s`
            }}
          />
        ))}
      </div>

      <motion.div 
        className="relative z-10 p-6 max-w-7xl mx-auto"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Header Section */}
        <motion.div variants={itemVariants} className="mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold mb-2">
                <span className="gradient-text">MR Tracking</span>
                <span className="text-white/80 ml-3">Dashboard</span>
              </h1>
              <p className="text-white/60 text-lg">Real-time location intelligence and route analytics</p>
            </div>
            
            <motion.div 
              className="flex items-center gap-3"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className="glass rounded-full p-3 pulse-glow">
                <Activity className="w-6 h-6 text-green-400" />
              </div>
              <div>
                <p className="text-white/60 text-sm">System Status</p>
                <p className="text-green-400 font-semibold flex items-center">
                  <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse" />
                  Online
                </p>
              </div>
            </motion.div>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <motion.div 
          variants={itemVariants}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          <StatCard
            icon={Users}
            title="Active MRs"
            value="12"
            change="+3"
            color="from-blue-500 to-cyan-500"
          />
          <StatCard
            icon={MapPin}
            title="Total Visits"
            value="248"
            change="+12%"
            color="from-green-500 to-emerald-500"
          />
          <StatCard
            icon={Route}
            title="Distance Covered"
            value="1,247 km"
            change="+8.2%"
            color="from-purple-500 to-pink-500"
          />
          <StatCard
            icon={Clock}
            title="Avg Response Time"
            value="2.4 min"
            change="-15%"
            color="from-orange-500 to-red-500"
          />
        </motion.div>

        {/* Controls Section */}
        <motion.div 
          variants={itemVariants}
          className="glass rounded-2xl p-6 mb-8"
        >
          <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
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
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white focus:border-blue-400 focus:outline-none transition-all duration-300"
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
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white focus:border-blue-400 focus:outline-none transition-all duration-300"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleExport}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300"
              >
                <Download className="w-4 h-4" />
                Export GPX
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex items-center gap-2 px-6 py-3 glass text-white rounded-xl font-medium hover:bg-white/20 transition-all duration-300"
              >
                <Filter className="w-4 h-4" />
                Filters
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* Map and Timeline Section */}
        <motion.div 
          variants={itemVariants}
          className="grid grid-cols-1 lg:grid-cols-3 gap-8"
        >
          {/* Map */}
          <motion.div 
            className="lg:col-span-2"
            whileHover={{ scale: 1.01 }}
            transition={{ type: "spring", stiffness: 100 }}
          >
            <div className="glass rounded-2xl overflow-hidden shadow-2xl">
              <div className="bg-gradient-to-r from-blue-500/20 to-purple-600/20 px-6 py-4 border-b border-white/10">
                <h2 className="text-white text-xl font-semibold flex items-center">
                  <Globe className="w-5 h-5 mr-2" />
                  Live Route Tracking
                  <div className="ml-auto flex items-center text-green-400">
                    <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse" />
                    <span className="text-sm">Real-time</span>
                  </div>
                </h2>
              </div>
              <div className="h-96">
                <MapView routeData={routeData} selectedMR={selectedMR} loading={loading} error={error} />
              </div>
            </div>
          </motion.div>

          {/* Side Panel */}
          <motion.div className="space-y-6">
            {/* Route Summary */}
            <div className="glass rounded-2xl p-6">
              <h3 className="text-white text-lg font-semibold mb-4 flex items-center">
                <Navigation className="w-5 h-5 mr-2" />
                Route Summary
              </h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-white/70">Total Distance</span>
                  <span className="text-white font-semibold">{stats ? `${stats.distance_km.toFixed(1)} km` : '24.8 km'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/70">Active Time</span>
                  <span className="text-white font-semibold">{stats ? `${stats.active_hours.toFixed(1)}h` : '6h 32m'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/70">Visits Completed</span>
                  <span className="text-green-400 font-semibold">{stats ? `${stats.visits}` : '8'}/10</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/70">Total Points</span>
                  <span className="text-white font-semibold">{stats ? `${stats.total_points}` : '124'}</span>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="glass rounded-2xl p-6">
              <h3 className="text-white text-lg font-semibold mb-4 flex items-center">
                <Activity className="w-5 h-5 mr-2" />
                Recent Activity
              </h3>
              <div className="space-y-3">
                {[
                  { time: '14:32', action: 'Visit completed', location: 'Apollo Pharmacy' },
                  { time: '13:45', action: 'En route', location: 'To City Hospital' },
                  { time: '12:20', action: 'Break started', location: 'Central Plaza' },
                  { time: '11:30', action: 'Visit completed', location: 'Max Healthcare' },
                ].map((activity, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                  >
                    <div className="w-2 h-2 bg-blue-400 rounded-full" />
                    <div className="flex-1">
                      <p className="text-white text-sm font-medium">{activity.action}</p>
                      <p className="text-white/60 text-xs">{activity.location}</p>
                    </div>
                    <span className="text-white/60 text-xs">{activity.time}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </motion.div>
      </motion.div>
    </div>
  );
}
