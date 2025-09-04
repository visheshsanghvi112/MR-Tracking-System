'use client';

import React from 'react';
import { motion } from 'framer-motion';
// Icons are imported at usage sites to avoid unused warnings

export const GlassCard: React.FC<{ 
  children: React.ReactNode; 
  className?: string;
  hover?: boolean;
  gradient?: boolean;
}> = ({ children, className = '', hover = true, gradient = false }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
    className={`
      ${gradient 
        ? 'bg-gradient-to-br from-blue-600/20 via-purple-600/20 to-indigo-700/20' 
        : 'bg-white/10'
      } 
      backdrop-blur-xl border border-white/20 rounded-2xl shadow-2xl
      ${hover ? 'hover:bg-white/20 hover:scale-[1.02] hover:shadow-3xl' : ''}
      transition-all duration-500 ease-out
      ${className}
    `}
    whileHover={hover ? { y: -5 } : {}}
  >
    {children}
  </motion.div>
);

export const AnimatedCounter: React.FC<{
  value: number;
  suffix?: string;
  prefix?: string;
  duration?: number;
}> = ({ value, suffix = '', prefix = '', duration = 2 }) => {
  const [count, setCount] = React.useState(0);

  React.useEffect(() => {
    let start = 0;
    const end = value;
    const increment = end / (duration * 60); // 60fps

    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, 1000 / 60);

    return () => clearInterval(timer);
  }, [value, duration]);

  return (
    <span className="font-bold">
      {prefix}{count}{suffix}
    </span>
  );
};

export const MetricCard: React.FC<{
  icon: React.ReactNode;
  title: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  subtitle?: string;
  color: string;
}> = ({ icon, title, value, change, changeType = 'neutral', subtitle, color }) => (
  <GlassCard className="p-6 group">
    <div className="flex items-start justify-between">
      <div className="flex-1">
        <div className="flex items-center gap-3 mb-3">
          <div className={`p-3 rounded-xl ${color} bg-opacity-20 group-hover:bg-opacity-30 transition-all duration-300`}>
            {icon}
          </div>
          <div>
            <p className="text-white/70 text-sm font-medium">{title}</p>
            {subtitle && <p className="text-white/50 text-xs">{subtitle}</p>}
          </div>
        </div>
        
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-white">
            {typeof value === 'number' ? (
              <AnimatedCounter value={value} />
            ) : (
              value
            )}
          </span>
          {change && (
            <span className={`text-sm font-medium ${
              changeType === 'positive' ? 'text-green-400' : 
              changeType === 'negative' ? 'text-red-400' : 'text-gray-400'
            }`}>
              {change}
            </span>
          )}
        </div>
      </div>
    </div>
  </GlassCard>
);

export const PulsingDot: React.FC<{ color?: string; size?: 'sm' | 'md' | 'lg' }> = ({ 
  color = 'bg-green-400', 
  size = 'md' 
}) => {
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  };

  return (
    <div className="relative">
      <div className={`${color} ${sizeClasses[size]} rounded-full animate-pulse`} />
      <div className={`absolute inset-0 ${color} ${sizeClasses[size]} rounded-full animate-ping opacity-75`} />
    </div>
  );
};

export const LoadingSpinner: React.FC<{ size?: 'sm' | 'md' | 'lg' }> = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  return (
    <motion.div
      className={`${sizeClasses[size]} border-2 border-white/30 border-t-white rounded-full`}
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
    />
  );
};

export const GradientButton: React.FC<{
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'success' | 'warning';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
}> = ({ 
  children, 
  onClick, 
  variant = 'primary', 
  size = 'md', 
  disabled = false,
  loading = false 
}) => {
  const variants = {
    primary: 'from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700',
    secondary: 'from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700',
    success: 'from-green-500 to-teal-600 hover:from-green-600 hover:to-teal-700',
    warning: 'from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700'
  };

  const sizes = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg'
  };

  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        bg-gradient-to-r ${variants[variant]} 
        text-white font-medium rounded-xl 
        shadow-lg hover:shadow-xl
        transition-all duration-300
        disabled:opacity-50 disabled:cursor-not-allowed
        ${sizes[size]}
        flex items-center justify-center gap-2
      `}
    >
      {loading ? <LoadingSpinner size="sm" /> : children}
    </motion.button>
  );
};

export const StatusBadge: React.FC<{
  status: 'online' | 'offline' | 'away' | 'busy';
  text: string;
}> = ({ status, text }) => {
  const statusColors = {
    online: 'bg-green-500/20 text-green-400 border-green-400/30',
    offline: 'bg-gray-500/20 text-gray-400 border-gray-400/30',
    away: 'bg-yellow-500/20 text-yellow-400 border-yellow-400/30',
    busy: 'bg-red-500/20 text-red-400 border-red-400/30'
  };

  return (
    <div className={`flex items-center gap-2 px-3 py-1 rounded-full border ${statusColors[status]}`}>
      <PulsingDot color={`bg-${status === 'online' ? 'green' : status === 'away' ? 'yellow' : status === 'busy' ? 'red' : 'gray'}-400`} size="sm" />
      <span className="text-sm font-medium">{text}</span>
    </div>
  );
};

export const ProgressRing: React.FC<{
  progress: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
}> = ({ progress, size = 100, strokeWidth = 8, color = '#3b82f6' }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <div className="relative">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(255,255,255,0.1)"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          fill="transparent"
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
          style={{
            strokeDasharray: circumference,
          }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-white font-bold text-lg">{progress}%</span>
      </div>
    </div>
  );
};
