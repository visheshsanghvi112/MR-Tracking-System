import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface AnimatedProgressProps {
  value: number;
  max?: number;
  className?: string;
  showValue?: boolean;
  gradient?: boolean;
  glowing?: boolean;
}

export const AnimatedProgress: React.FC<AnimatedProgressProps> = ({
  value,
  max = 100,
  className,
  showValue = false,
  gradient = true,
  glowing = false,
}) => {
  const percentage = Math.min((value / max) * 100, 100);

  return (
    <div className={cn('relative w-full', className)}>
      <div className="h-3 w-full rounded-full bg-muted overflow-hidden">
        <motion.div
          className={cn(
            'h-full rounded-full',
            gradient
              ? 'bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500'
              : 'bg-primary',
            glowing && 'shadow-lg shadow-primary/50'
          )}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
        />
      </div>
      {showValue && (
        <motion.span
          className="absolute top-0 right-0 -mt-6 text-sm font-medium"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.5 }}
        >
          {Math.round(percentage)}%
        </motion.span>
      )}
    </div>
  );
};

interface GlowingCardProps {
  children: React.ReactNode;
  className?: string;
  glowColor?: string;
  intensity?: 'low' | 'medium' | 'high';
}

export const GlowingCard: React.FC<GlowingCardProps> = ({
  children,
  className,
  glowColor = 'blue',
  intensity = 'medium',
}) => {
  const glowIntensity = {
    low: 'shadow-lg',
    medium: 'shadow-xl',
    high: 'shadow-2xl',
  };

  const glowColors = {
    blue: 'shadow-blue-500/25',
    purple: 'shadow-purple-500/25',
    green: 'shadow-green-500/25',
    orange: 'shadow-orange-500/25',
    pink: 'shadow-pink-500/25',
  };

  return (
    <motion.div
      className={cn(
        'relative rounded-lg border bg-card p-6',
        'transition-all duration-300',
        glowIntensity[intensity],
        glowColors[glowColor as keyof typeof glowColors],
        'hover:shadow-2xl hover:scale-105',
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      whileHover={{ scale: 1.02 }}
    >
      {children}
    </motion.div>
  );
};

interface ParticleBackgroundProps {
  className?: string;
  density?: number;
}

export const ParticleBackground: React.FC<ParticleBackgroundProps> = ({
  className,
  density = 50,
}) => {
  const particles = Array.from({ length: density }, (_, i) => i);

  return (
    <div className={cn('absolute inset-0 overflow-hidden', className)}>
      {particles.map((particle) => (
        <motion.div
          key={particle}
          className="absolute w-1 h-1 bg-primary/20 rounded-full"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            y: [-20, 20],
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: Math.random() * 3 + 2,
            repeat: Infinity,
            delay: Math.random() * 2,
          }}
        />
      ))}
    </div>
  );
};
