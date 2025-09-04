'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MapPin, TrendingUp, Navigation, Clock, Route, Activity,
  Zap, Target, BarChart3, Download, RefreshCw
} from 'lucide-react';
import { 
  GlassCard, 
  MetricCard, 
  PulsingDot, 
  GradientButton, 
  StatusBadge, 
  ProgressRing,
  AnimatedCounter 
} from '@/components/ui/ModernComponents';

// Floating Animation Component
const FloatingElement: React.FC<{ children: React.ReactNode; delay?: number }> = ({ children, delay = 0 }) => (
  <motion.div
    animate={{ 
      y: [-10, 10, -10],
      rotate: [-1, 1, -1]
    }}
    transition={{ 
      duration: 6, 
      repeat: Infinity, 
      delay,
      ease: "easeInOut"
    }}
  >
    {children}
  </motion.div>
);

// Advanced Map Component with Beautiful Placeholders
const StunningMapView: React.FC<{ mrNumber: number; date: string }> = ({ mrNumber, date }) => {
  const [loading, setLoading] = useState(true);

  React.useEffect(() => {
    // Simulate data loading
    const timer = setTimeout(() => {
      setLoading(false);
    }, 2000);
    return () => clearTimeout(timer);
  }, [mrNumber, date]);

  return (
    <GlassCard className="h-[600px] relative overflow-hidden group" gradient>
      {/* Header */}
      <div className="absolute top-6 left-6 right-6 z-20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-xl backdrop-blur-sm">
              <MapPin className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h3 className="text-white text-xl font-bold">Live Route Intelligence</h3>
              <p className="text-white/70 text-sm">MR {mrNumber} • {new Date(date).toLocaleDateString()}</p>
            </div>
          </div>
          <StatusBadge status="online" text="Live Tracking" />
        </div>
      </div>

      {/* Map Content */}
      <div className="absolute inset-0 pt-20">
        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="h-full flex items-center justify-center"
            >
              <div className="text-center">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                  className="w-16 h-16 border-4 border-white/20 border-t-blue-400 rounded-full mx-auto mb-4"
                />
                <p className="text-white/80 text-lg font-medium">Loading Route Data...</p>
                <p className="text-white/60 text-sm mt-1">Analyzing {mrNumber} movements</p>
              </div>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8 }}
              className="h-full relative"
            >
              {/* Beautiful Map Placeholder with Animations */}
              <div className="h-full bg-gradient-to-br from-indigo-900/30 via-blue-800/30 to-purple-900/30 
                              rounded-2xl border border-white/10 relative overflow-hidden">
                
                {/* Animated Route Paths */}
                <div className="absolute inset-0">
                  {[...Array(5)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="absolute"
                      style={{
                        left: `${15 + i * 20}%`,
                        top: `${20 + i * 15}%`,
                        width: '60px',
                        height: '4px',
                      }}
                      initial={{ scaleX: 0, opacity: 0 }}
                      animate={{ scaleX: 1, opacity: 0.7 }}
                      transition={{ delay: i * 0.3, duration: 1 }}
                    >
                      <div className="w-full h-full bg-gradient-to-r from-blue-400 to-purple-500 rounded-full" />
                    </motion.div>
                  ))}
                </div>

                {/* Animated Location Pins */}
                <div className="absolute inset-0">
                  {[...Array(8)].map((_, i) => (
                    <FloatingElement key={i} delay={i * 0.2}>
                      <motion.div
                        className="absolute"
                        style={{
                          left: `${20 + (i % 3) * 30}%`,
                          top: `${25 + Math.floor(i / 3) * 20}%`,
                        }}
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ delay: 1 + i * 0.2, type: 'spring' }}
                      >
                        <div className="relative">
                          <div className="w-4 h-4 bg-green-400 rounded-full shadow-lg shadow-green-400/50" />
                          <div className="absolute inset-0 bg-green-400 rounded-full animate-ping opacity-75" />
                        </div>
                      </motion.div>
                    </FloatingElement>
                  ))}
                </div>

                {/* Center Statistics */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <GlassCard className="p-6 text-center">
                    <ProgressRing progress={94} size={120} color="#3b82f6" />
                    <p className="text-white/80 text-sm mt-4 font-medium">Route Efficiency</p>
                  </GlassCard>
                </div>
              </div>

              {/* Floating Mini Stats */}
              <div className="absolute bottom-4 left-4 right-4">
                <div className="grid grid-cols-3 gap-3">
                  <GlassCard className="p-3 text-center">
                    <p className="text-blue-400 text-2xl font-bold"><AnimatedCounter value={8} /></p>
                    <p className="text-white/70 text-xs">Visits</p>
                  </GlassCard>
                  <GlassCard className="p-3 text-center">
                    <p className="text-green-400 text-2xl font-bold"><AnimatedCounter value={142} suffix="km" /></p>
                    <p className="text-white/70 text-xs">Distance</p>
                  </GlassCard>
                  <GlassCard className="p-3 text-center">
                    <p className="text-purple-400 text-2xl font-bold"><AnimatedCounter value={94} suffix="%" /></p>
                    <p className="text-white/70 text-xs">Efficiency</p>
                  </GlassCard>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </GlassCard>
  );
};

// Enhanced Activity Feed
const LiveActivityFeed: React.FC<{ mrNumber: number }> = ({ mrNumber }) => {
  const [activities] = useState([
    { id: 1, time: '09:15 AM', action: 'Route Started', location: 'Delhi Central', type: 'start', icon: Zap },
    { id: 2, time: '10:30 AM', action: 'Visit Completed', location: 'Apollo Hospital', type: 'visit', icon: Target },
    { id: 3, time: '11:45 AM', action: 'Break Time', location: 'Coffee Point', type: 'break', icon: Clock },
    { id: 4, time: '01:20 PM', action: 'Visit Completed', location: 'Max Healthcare', type: 'visit', icon: Target },
    { id: 5, time: '02:45 PM', action: 'En Route', location: 'Fortis Hospital', type: 'travel', icon: Navigation },
    { id: 6, time: '03:15 PM', action: 'Visit in Progress', location: 'Fortis Hospital', type: 'active', icon: Activity },
  ]);

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'start': return 'text-green-400 bg-green-500/20';
      case 'visit': return 'text-blue-400 bg-blue-500/20';
      case 'break': return 'text-yellow-400 bg-yellow-500/20';
      case 'travel': return 'text-purple-400 bg-purple-500/20';
      case 'active': return 'text-orange-400 bg-orange-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  return (
    <GlassCard className="h-[600px] overflow-hidden">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500/20 rounded-xl">
              <Activity className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <h3 className="text-white text-xl font-bold">Live Activity Stream</h3>
              <p className="text-white/70 text-sm">Real-time updates for MR {mrNumber}</p>
            </div>
          </div>
          <PulsingDot color="bg-green-400" size="lg" />
        </div>
        
        <div className="space-y-4 overflow-y-auto h-[450px] custom-scrollbar">
          {activities.map((activity, index) => {
            const IconComponent = activity.icon;
            return (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="group"
              >
                <GlassCard className="p-4 hover:bg-white/20 transition-all duration-300">
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-xl ${getActivityColor(activity.type)} group-hover:scale-110 transition-transform duration-300`}>
                      <IconComponent className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <p className="text-white font-medium">{activity.action}</p>
                        <span className="text-white/60 text-sm">{activity.time}</span>
                      </div>
                      <p className="text-white/70 text-sm mt-1">{activity.location}</p>
                    </div>
                    {activity.type === 'active' && (
                      <PulsingDot color="bg-orange-400" />
                    )}
                  </div>
                </GlassCard>
              </motion.div>
            );
          })}
        </div>
      </div>
    </GlassCard>
  );
};

// Main Dashboard Component
const SuperModernDashboard: React.FC = () => {
  const [selectedMR, setSelectedMR] = useState<number>(1201911108);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [mrList] = useState([1201911108, 1201911109, 1201911110, 1201911111, 1201911112]);
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    setRefreshing(false);
  };

  return (
    <>
      <div className="min-h-screen relative overflow-hidden">
        {/* Dynamic Background */}
        <div className="fixed inset-0 bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_80%,rgba(120,119,198,0.3),transparent_50%)]" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(255,119,198,0.3),transparent_50%)]" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_40%_40%,rgba(99,102,241,0.2),transparent_50%)]" />
        </div>

        {/* Animated Particles */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          {[...Array(40)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-white/10 rounded-full"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
              }}
              animate={{
                y: [-30, -120],
                opacity: [0, 0.8, 0],
                scale: [0.5, 1, 0.5],
              }}
              transition={{
                duration: Math.random() * 4 + 3,
                repeat: Infinity,
                delay: Math.random() * 3,
                ease: 'easeOut',
              }}
            />
          ))}
        </div>

        <div className="relative z-10 p-6">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="mb-8"
          >
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent mb-2">
                  MR Intelligence Hub
                </h1>
                <p className="text-white/70 text-lg">Advanced location intelligence & route optimization</p>
              </div>
              <div className="flex items-center gap-4">
                <StatusBadge status="online" text="System Active" />
                <GradientButton
                  onClick={handleRefresh}
                  loading={refreshing}
                  variant="primary"
                  size="md"
                >
                  <RefreshCw className="w-4 h-4" />
                  Refresh
                </GradientButton>
              </div>
            </div>
          </motion.div>

          {/* Controls */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
          >
            <GlassCard className="p-6">
              <label className="text-white/90 text-sm font-medium block mb-3">Medical Representative</label>
              <select
                value={selectedMR}
                onChange={(e) => setSelectedMR(Number(e.target.value))}
                className="w-full px-4 py-3 bg-white/10 backdrop-blur-md border border-white/20 
                           rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-400 
                           focus:border-transparent hover:bg-white/20 transition-all duration-200"
              >
                {mrList.map((option) => (
                  <option key={option} value={option} className="bg-gray-800 text-white">
                    MR {option}
                  </option>
                ))}
              </select>
            </GlassCard>

            <GlassCard className="p-6">
              <label className="text-white/90 text-sm font-medium block mb-3">Select Date</label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="w-full px-4 py-3 bg-white/10 backdrop-blur-md border border-white/20 
                           rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-400 
                           focus:border-transparent hover:bg-white/20 transition-all duration-200"
              />
            </GlassCard>

            <GradientButton variant="success" size="lg">
              <Download className="w-4 h-4" />
              Export Report
            </GradientButton>

            <GradientButton variant="warning" size="lg">
              <BarChart3 className="w-4 h-4" />
              Analytics
            </GradientButton>
          </motion.div>

          {/* Metrics Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
          >
            <MetricCard
              icon={<Route className="w-6 h-6 text-blue-400" />}
              title="Total Distance"
              value="142.5 km"
              change="+12%"
              changeType="positive"
              subtitle="Today's journey"
              color="bg-blue-500"
            />
            <MetricCard
              icon={<Target className="w-6 h-6 text-green-400" />}
              title="Visits Completed"
              value={8}
              change="8/12"
              changeType="positive"
              subtitle="Progress today"
              color="bg-green-500"
            />
            <MetricCard
              icon={<Clock className="w-6 h-6 text-purple-400" />}
              title="Active Time"
              value="6h 24m"
              change="75%"
              changeType="positive"
              subtitle="Productivity"
              color="bg-purple-500"
            />
            <MetricCard
              icon={<TrendingUp className="w-6 h-6 text-orange-400" />}
              title="Efficiency Score"
              value="94%"
              change="+5%"
              changeType="positive"
              subtitle="Route optimization"
              color="bg-orange-500"
            />
          </motion.div>

          {/* Main Content Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-6"
          >
            {/* Map - Takes 2 columns */}
            <div className="lg:col-span-2">
              <StunningMapView mrNumber={selectedMR} date={selectedDate} />
            </div>
            
            {/* Activity Feed - Takes 1 column */}
            <div className="lg:col-span-1">
              <LiveActivityFeed mrNumber={selectedMR} />
            </div>
          </motion.div>
        </div>
      </div>
    </>
  );
};

export default SuperModernDashboard;
