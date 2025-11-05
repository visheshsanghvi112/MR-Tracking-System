import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { ActivityFeedItem } from "@/types";
import { cn } from "@/lib/utils";
import { MapPin, Users, Route, Clock } from "lucide-react";

interface ActivityFeedProps {
  items: ActivityFeedItem[];
  className?: string;
}

export function ActivityFeed({ items, className }: ActivityFeedProps) {
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'visit':
        return <MapPin className="h-4 w-4 text-primary" />;
      case 'status_change':
        return <Users className="h-4 w-4 text-warning" />;
      case 'route_start':
      case 'route_end':
        return <Route className="h-4 w-4 text-success" />;
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'visit':
        return <Badge variant="secondary" className="bg-primary-light text-primary">Visit</Badge>;
      case 'status_change':
        return <Badge variant="secondary" className="bg-warning-light text-warning">Status</Badge>;
      case 'route_start':
        return <Badge variant="secondary" className="bg-success-light text-success">Start</Badge>;
      case 'route_end':
        return <Badge variant="secondary" className="bg-success-light text-success">End</Badge>;
      default:
        return <Badge variant="secondary">Event</Badge>;
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  const formatRelativeTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <Card className={cn("surface-elevated", className)}>
      <CardHeader>
        <CardTitle className="text-lg">Recent Activity</CardTitle>
        <CardDescription>Live updates from the field</CardDescription>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[300px] px-6">
          <div className="space-y-4 pb-6">
            {items.map((item, index) => (
              <div key={item.id} className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-1">
                  {getTypeIcon(item.type)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    {getTypeBadge(item.type)}
                    <span className="text-xs text-muted-foreground">
                      {formatTime(item.timestamp)}
                    </span>
                  </div>
                  
                  <p className="text-sm text-foreground mb-1">
                    {item.message}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    {item.mr_name && (
                      <span className="text-xs text-muted-foreground">
                        {item.mr_name}
                      </span>
                    )}
                    <span className="text-xs text-muted-foreground">
                      {formatRelativeTime(item.timestamp)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
            
            {items.length === 0 && (
              <div className="text-center py-8">
                <Clock className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">No recent activity</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}