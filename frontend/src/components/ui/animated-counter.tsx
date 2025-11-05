import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

interface AnimatedCounterProps {
  value: number;
  duration?: number;
  className?: string;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  separator?: string;
}

export function AnimatedCounter({
  value,
  duration = 1000,
  className,
  prefix = "",
  suffix = "",
  decimals = 0,
  separator = ","
}: AnimatedCounterProps) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = value;
    const increment = end / (duration / 16); // 60fps

    const animate = () => {
      start += increment;
      if (start < end) {
        setCount(start);
        requestAnimationFrame(animate);
      } else {
        setCount(end);
      }
    };

    animate();
  }, [value, duration]);

  const formatNumber = (num: number) => {
    const fixedNum = num.toFixed(decimals);
    return fixedNum.replace(/\B(?=(\d{3})+(?!\d))/g, separator);
  };

  return (
    <span className={cn("font-mono tabular-nums", className)}>
      {prefix}{formatNumber(count)}{suffix}
    </span>
  );
}

interface AnimatedProgressProps {
  value: number;
  max?: number;
  className?: string;
  indicatorClassName?: string;
  showValue?: boolean;
  animated?: boolean;
  duration?: number;
}

export function AnimatedProgress({
  value,
  max = 100,
  className,
  indicatorClassName,
  showValue = false,
  animated = true,
  duration = 1000
}: AnimatedProgressProps) {
  const [progress, setProgress] = useState(0);
  const percentage = Math.min((value / max) * 100, 100);

  useEffect(() => {
    if (!animated) {
      setProgress(percentage);
      return;
    }

    let start = 0;
    const increment = percentage / (duration / 16);

    const animate = () => {
      start += increment;
      if (start < percentage) {
        setProgress(start);
        requestAnimationFrame(animate);
      } else {
        setProgress(percentage);
      }
    };

    animate();
  }, [percentage, animated, duration]);

  return (
    <div className={cn("relative w-full", className)}>
      <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
        <div
          className={cn(
            "h-full transition-all duration-300 ease-out rounded-full gradient-primary",
            indicatorClassName
          )}
          style={{ width: `${progress}%` }}
        />
      </div>
      {showValue && (
        <div className="absolute inset-0 flex items-center justify-center text-xs font-medium">
          <AnimatedCounter value={value} suffix={`/${max}`} />
        </div>
      )}
    </div>
  );
}