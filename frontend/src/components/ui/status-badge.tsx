import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: 'active' | 'offline' | 'idle';
  label?: string;
  className?: string;
}

export function StatusBadge({ status, label, className }: StatusBadgeProps) {
  const getStatusVariant = () => {
    switch (status) {
      case 'active':
        return 'bg-success text-success-foreground';
      case 'offline':
        return 'bg-muted text-muted-foreground';
      case 'idle':
        return 'bg-warning text-warning-foreground';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  const getStatusDot = () => {
    const dotClass = cn(
      "w-2 h-2 rounded-full mr-2",
      status === 'active' && 'bg-success',
      status === 'offline' && 'bg-muted-foreground',
      status === 'idle' && 'bg-warning'
    );

    return <div className={dotClass} />;
  };

  return (
    <Badge 
      variant="secondary" 
      className={cn(
        "flex items-center gap-1 text-xs font-medium",
        getStatusVariant(),
        className
      )}
    >
      {getStatusDot()}
      {label || status.charAt(0).toUpperCase() + status.slice(1)}
    </Badge>
  );
}