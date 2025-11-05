import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "./status-badge";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MedicalRepresentative } from "@/types";
import { cn, formatIndianCurrency } from "@/lib/utils";
import { MapPin, Clock, Route, DollarSign } from "lucide-react";

interface MRCardProps {
  mr: MedicalRepresentative;
  onSelect?: (mrId: string) => void;
  isSelected?: boolean;
  className?: string;
}

export function MRCard({ mr, onSelect, isSelected, className }: MRCardProps) {
  const formatLastSeen = (timestamp?: string) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <Card 
      className={cn(
        "surface-elevated cursor-pointer transition-all hover:shadow-md",
        isSelected && "ring-2 ring-primary ring-offset-2",
        className
      )}
      onClick={() => onSelect?.(mr.mr_id)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-base">{mr.name}</CardTitle>
            <CardDescription className="text-sm">
              {mr.team_name}
            </CardDescription>
          </div>
          <StatusBadge status={mr.status} />
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">Last seen:</span>
          </div>
          <div className="text-right font-medium">
            {formatLastSeen(mr.last_activity || mr.last_seen)}
          </div>

          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">Visits:</span>
          </div>
          <div className="text-right font-medium">
            {mr.total_visits || mr.visits_today || 0}
          </div>

          <div className="flex items-center gap-2">
            <Route className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">Distance:</span>
          </div>
          <div className="text-right font-medium">
            {mr.distance_today ? `${mr.distance_today} km` : '0 km'}
          </div>

          {mr.expenses_today && (
            <>
              <div className="flex items-center gap-2">
                <DollarSign className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">Expenses:</span>
              </div>
              <div className="text-right font-medium">
                {formatIndianCurrency(mr.expenses_today)}
              </div>
            </>
          )}
        </div>

        {/* Real GPS Location Display */}
        {mr.last_location && mr.last_location.lat !== 0 && mr.last_location.lng !== 0 && (
          <div className="mt-3 pt-3 border-t">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <MapPin className="h-3 w-3 text-red-500" />
                <span className="text-muted-foreground">Current Location:</span>
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse ml-auto"></div>
              </div>
              <div className="text-xs font-mono bg-muted/50 p-2 rounded border">
                {mr.last_location.lat.toFixed(4)}, {mr.last_location.lng.toFixed(4)}
              </div>
              {mr.last_location.address && (
                <div className="text-xs text-muted-foreground">
                  {mr.last_location.address}
                </div>
              )}
            </div>
          </div>
        )}

        {mr.active_hours && (
          <div className="mt-3 pt-3 border-t">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Active Hours:</span>
              <span className="font-medium">{mr.active_hours}h</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}