import { cn } from "@/lib/utils";

interface LoadingSkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "card" | "text" | "avatar" | "button";
  lines?: number;
  animated?: boolean;
}

export function LoadingSkeleton({ 
  className, 
  variant = "default", 
  lines = 3,
  animated = true,
  ...props 
}: LoadingSkeletonProps) {
  const baseClasses = "rounded-md bg-muted";
  const animationClasses = animated ? "loading-shimmer" : "";

  const variants = {
    default: "h-4 w-full",
    card: "h-32 w-full",
    text: "h-4",
    avatar: "h-12 w-12 rounded-full",
    button: "h-10 w-24"
  };

  if (variant === "text" && lines > 1) {
    return (
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={cn(
              baseClasses,
              animationClasses,
              variants.text,
              i === lines - 1 ? "w-3/4" : "w-full",
              className
            )}
            {...props}
          />
        ))}
      </div>
    );
  }

  return (
    <div
      className={cn(
        baseClasses,
        animationClasses,
        variants[variant],
        className
      )}
      {...props}
    />
  );
}

export function LoadingCard() {
  return (
    <div className="p-6 space-y-4 border rounded-xl">
      <div className="flex items-center space-x-4">
        <LoadingSkeleton variant="avatar" />
        <div className="space-y-2 flex-1">
          <LoadingSkeleton className="h-4 w-1/2" />
          <LoadingSkeleton className="h-3 w-1/3" />
        </div>
      </div>
      <LoadingSkeleton variant="text" lines={3} />
      <div className="flex justify-between">
        <LoadingSkeleton variant="button" />
        <LoadingSkeleton variant="button" />
      </div>
    </div>
  );
}

export function LoadingTable({ rows = 5, columns = 4 }: { rows?: number; columns?: number }) {
  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
        {Array.from({ length: columns }).map((_, i) => (
          <LoadingSkeleton key={i} className="h-6 w-full" />
        ))}
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
          {Array.from({ length: columns }).map((_, colIndex) => (
            <LoadingSkeleton key={colIndex} className="h-8 w-full" />
          ))}
        </div>
      ))}
    </div>
  );
}