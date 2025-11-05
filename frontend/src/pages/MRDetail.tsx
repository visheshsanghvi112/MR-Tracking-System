import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";

import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { MapContainer } from "@/components/map/map-container";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { apiClient } from "@/lib/apiClient";
import { MedicalRepresentative, RoutePoint } from "@/types";
import { formatIndianCurrency } from "@/lib/utils";
import { 
  ArrowLeft, 
  MapPin, 
  Clock, 
  Route, 
  DollarSign,
  Phone,
  Mail,
  Calendar,
  TrendingUp,
  Navigation
} from "lucide-react";

export default function MRDetail() {
  const { id } = useParams<{ id: string }>();
  const [mr, setMR] = useState<MedicalRepresentative | null>(null);
  const [routePoints, setRoutePoints] = useState<RoutePoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [centerOn, setCenterOn] = useState<{ lat: number; lng: number; zoom?: number } | null>(null); // NEW: For centering map

  const currentDate = new Date().toISOString().split('T')[0];

  useEffect(() => {
    if (!id) return;

    const loadData = async () => {
      setLoading(true);
      try {
        const [mrResponse, routeResponse] = await Promise.all([
          apiClient.getMRDetail(id),
          apiClient.getRoute(id, currentDate)
        ]);

        if (mrResponse.success) setMR(mrResponse.data);
        if (routeResponse.success && routeResponse.data?.points && Array.isArray(routeResponse.data.points)) {
          // Filter out any points with invalid coordinates
          const validPoints = routeResponse.data.points.filter(point =>
            point.latitude !== 0 &&
            point.longitude !== 0 &&
            point.latitude >= -90 && point.latitude <= 90 &&
            point.longitude >= -180 && point.longitude <= 180
          );

          if (validPoints.length > 0) {
            setRoutePoints(validPoints);
            console.log(`✅ Loaded ${validPoints.length} valid route points for MR ${id}`);
          } else {
            console.log('No valid route points found for MR:', id);
            setRoutePoints([]);
          }
        } else {
          console.log('No route data available for MR:', id);
          setRoutePoints([]);
        }
      } catch (error) {
        console.error('Failed to load MR details:', error);
        setRoutePoints([]);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [id, currentDate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <main className="container mx-auto p-6">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-muted rounded w-1/4"></div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-24 bg-muted rounded"></div>
              ))}
            </div>
            <div className="h-[500px] bg-muted rounded"></div>
          </div>
        </main>
      </div>
    );
  }

  if (!mr) {
    return (
      <div className="min-h-screen bg-background">
        <main className="container mx-auto p-6">
          <div className="text-center py-12">
            <h1 className="text-2xl font-bold mb-4">MR Not Found</h1>
            <p className="text-muted-foreground mb-6">The medical representative you're looking for doesn't exist.</p>
            <Link to="/dashboard">
              <Button>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
            </Link>
          </div>
        </main>
      </div>
    );
  }

  const visits = routePoints.filter(point => point.type === 'visit');

  // NEW: Function to jump to location on map
  const jumpToLocation = (latitude: number, longitude: number) => {
    console.log(`📍 Jumping to location: ${latitude}, ${longitude}`);
    setCenterOn({ lat: latitude, lng: longitude, zoom: 17 });
    
    // Scroll to map smoothly
    const mapElement = document.getElementById('route-map');
    if (mapElement) {
      mapElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto p-6 space-y-6">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Link to="/dashboard" className="hover:text-foreground">Dashboard</Link>
          <span>/</span>
          <Link to="/mrs" className="hover:text-foreground">MRs</Link>
          <span>/</span>
          <span className="text-foreground">{mr.name}</span>
        </div>

        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <Avatar className="h-16 w-16">
              <AvatarImage
                src={`/placeholder.svg`}
                alt={mr.name}
                onError={(e) => { (e.currentTarget as HTMLImageElement).src = '/placeholder.svg'; }}
              />
              <AvatarFallback className="text-lg">
                {mr.name.split(' ').map(n => n[0]).join('')}
              </AvatarFallback>
            </Avatar>
            
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold">{mr.name}</h1>
                <StatusBadge status={mr.status} />
              </div>
              
              <div className="space-y-1 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <Badge variant="outline">{mr.team_name}</Badge>
                  <span>•</span>
                  <span>ID: {mr.mr_id}</span>
                </div>
                
                {mr.last_seen && (
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    <span>Last seen: {new Date(mr.last_seen).toLocaleString()}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            <Button variant="outline">
              <Phone className="h-4 w-4 mr-2" />
              Call
            </Button>
            <Button variant="outline">
              <Mail className="h-4 w-4 mr-2" />
              Message
            </Button>
            <Link to={`/dashboard?mr_id=${mr.mr_id}&live=true`}>
              <Button>
                <Navigation className="h-4 w-4 mr-2" />
                Track Live
              </Button>
            </Link>
          </div>
        </div>

        {/* Today's Performance */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Today's Performance</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              label="Visits"
              value={mr.visits_today || 0}
              trend="up"
              trendValue="+2"
              subText="from yesterday"
              icon={<MapPin className="h-4 w-4" />}
            />
            <MetricCard
              label="Distance"
              value={mr.distance_today ? `${mr.distance_today} km` : '0 km'}
              trend="up"
              trendValue="+8%"
              subText="from yesterday"
              icon={<Route className="h-4 w-4" />}
            />
            <MetricCard
              label="Active Hours"
              value={mr.active_hours ? `${mr.active_hours}h` : '0h'}
              trend="up"
              trendValue="+0.5h"
              subText="from yesterday"
              icon={<Clock className="h-4 w-4" />}
            />
            <MetricCard
              label="Expenses"
              value={mr.expenses_today ? formatIndianCurrency(mr.expenses_today) : formatIndianCurrency(0)}
              trend="down"
              trendValue="-12%"
              subText="from yesterday"
              icon={<DollarSign className="h-4 w-4" />}
            />
          </div>
        </div>

        {/* Route Visualization */}
        <div id="route-map">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Today's Route</h2>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">
                {new Date(currentDate).toLocaleDateString()}
              </span>
            </div>
          </div>
          
          <MapContainer
            mrId={mr.mr_id}
            date={currentDate}
            markers={routePoints}
            className="h-[500px]"
            centerOn={centerOn}
            mrName={mr.name}
          />
        </div>

        {/* Visit History */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Visit History</h2>
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Time</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Duration</TableHead>
                    <TableHead>Outcome</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {visits.length > 0 ? visits.map((visit) => (
                    <TableRow 
                      key={visit.id}
                      className="cursor-pointer hover:bg-muted/50 transition-colors"
                      onClick={() => jumpToLocation(visit.latitude, visit.longitude)}
                      title="Click to view on map"
                    >
                      <TableCell className="font-medium">
                        {new Date(visit.timestamp).toLocaleTimeString('en-US', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <MapPin className="h-4 w-4 text-blue-500 flex-shrink-0" />
                          <div>
                            <div className="font-medium">{visit.location_name}</div>
                            <div className="text-sm text-muted-foreground">
                              {visit.latitude.toFixed(4)}, {visit.longitude.toFixed(4)}
                            </div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {visit.visit_type?.charAt(0).toUpperCase() + visit.visit_type?.slice(1) || 'Unknown'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {visit.duration ? `${visit.duration} min` : '-'}
                      </TableCell>
                      <TableCell>
                        <span className="text-sm">
                          {visit.outcome || 'No outcome recorded'}
                        </span>
                      </TableCell>
                    </TableRow>
                  )) : (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                        <MapPin className="h-8 w-8 mx-auto mb-2" />
                        <p>No visits recorded for today</p>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}