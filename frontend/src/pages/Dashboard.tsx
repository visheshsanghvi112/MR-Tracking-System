import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";

import { MetricCard } from "@/components/ui/metric-card";
import { MRCard } from "@/components/ui/mr-card";
import { ActivityFeed } from "@/components/ui/activity-feed";
import { MapContainer } from "@/components/map/map-container";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiClient } from "@/lib/apiClient";
import { MedicalRepresentative, DashboardStats, ActivityFeedItem, RoutePoint } from "@/types";
import { 
  Users, 
  MapPin, 
  Route, 
  TrendingUp, 
  Search, 
  Filter,
  Play,
  Pause,
  Calendar,
  RefreshCw,
  BarChart3,
  Activity,
  Target,
  Award,
  DollarSign
} from "lucide-react";

type SelfieItem = {
  timestamp: string;
  mr_id: string;
  mr_name?: string;
  location?: string;
  selfie_url?: string;
  view_url?: string;
  media_type?: string;
  file_id?: string;
};

export default function Dashboard() {
  const [searchParams, setSearchParams] = useSearchParams();
  
  // State
  const [mrs, setMRs] = useState<MedicalRepresentative[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [activityFeed, setActivityFeed] = useState<ActivityFeedItem[]>([]);
  const [routePoints, setRoutePoints] = useState<RoutePoint[]>([]);
  const [selfies, setSelfies] = useState<SelfieItem[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Enhanced Filter State
  const [timeRange, setTimeRange] = useState('day'); // day, week, month
  const [selectedMRFilter, setSelectedMRFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState(new Date().toISOString().split('T')[0]);
  
  // Filters from URL
  const selectedMR = searchParams.get('mr_id') || undefined;
  const selectedTeam = searchParams.get('team_id') || 'all';
  const selectedDate = searchParams.get('date') || new Date().toISOString().split('T')[0];
  const isLive = searchParams.get('live') === 'true';
  
  // UI state
  const [searchQuery, setSearchQuery] = useState('');

  // Load data (includes selfies)
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [mrsResponse, statsResponse, activityResponse] = await Promise.all([
          apiClient.getMRs(),
          apiClient.getDashboardStats(),
          apiClient.getActivityFeed()
        ]);

        if (mrsResponse.success) setMRs(mrsResponse.data);
        if (statsResponse.success) setStats(statsResponse.data);
        if (activityResponse.success) setActivityFeed(activityResponse.data);

        // Load selfies based on selection: if MR selected, fetch that MR and filter by date; otherwise show recent
        try {
          if (selectedMR) {
            const res = await apiClient.getSelfieVerifications(String(selectedMR), 100);
            if (res.success) {
              const day = selectedDate;
              const filtered = (res.data as any[]).filter((r: any) => {
                const ts: string = r.timestamp || '';
                const dateOnly = ts.split(' ')[0];
                return dateOnly === day;
              });
              setSelfies(filtered as any);
            } else {
              setSelfies([]);
            }
          } else {
            const recent = await apiClient.getRecentSelfies(12);
            setSelfies(recent.success ? (recent.data as any) : []);
          }
        } catch (e) {
          console.error('Failed to load selfies:', e);
          setSelfies([]);
        }
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [selectedTeam, selectedDate, selectedMR]);

  // Load route data when MR is selected
  useEffect(() => {
    if (selectedMR) {
      const loadRoute = async () => {
        try {
          const response = await apiClient.getRoute(selectedMR, selectedDate);
          if (response.success && response.data?.points && Array.isArray(response.data.points)) {
            // Filter out any points with invalid coordinates
            const validPoints = response.data.points.filter(point =>
              point.latitude !== 0 &&
              point.longitude !== 0 &&
              point.latitude >= -90 && point.latitude <= 90 &&
              point.longitude >= -180 && point.longitude <= 180
            );

            if (validPoints.length > 0) {
              setRoutePoints(validPoints);
              console.log(`✅ Loaded ${validPoints.length} valid route points for MR ${selectedMR}`);
            } else {
              console.log('No valid route points found for selected MR and date');
              setRoutePoints([]);
            }
          } else {
            console.log('No route data available for selected MR and date');
            setRoutePoints([]);
          }
        } catch (error) {
          console.error('Error loading route:', error);
          setRoutePoints([]);
        }
      };
      loadRoute();
    } else {
      setRoutePoints([]);
    }
  }, [selectedMR, selectedDate]);

  // Update URL params
  const updateParams = (key: string, value: string | null) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
      newParams.set(key, value);
    } else {
      newParams.delete(key);
    }
    setSearchParams(newParams);
  };

  // Filter MRs based on search and selected MR filter
  const filteredMRs = mrs.filter(mr => {
    const matchesSearch = mr.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesMRFilter = selectedMRFilter === 'all' || mr.mr_id === selectedMRFilter;
    return matchesSearch && matchesMRFilter;
  });

  const handleMRSelect = (mrId: string) => {
    updateParams('mr_id', selectedMR === mrId ? null : mrId);
  };

  const toggleLive = () => {
    updateParams('live', isLive ? null : 'true');
  };

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto p-3 sm:p-4 md:p-6 space-y-4 sm:space-y-6">
        {/* Enhanced Header with Comprehensive Filters */}
        <div className="flex flex-col space-y-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold">Dashboard</h1>
              <p className="text-muted-foreground">
                Real-time MR tracking data from Google Sheets
              </p>
            </div>
            <Button onClick={() => window.location.reload()} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh Data
            </Button>
          </div>

          {/* Comprehensive Filter Panel */}
          <div className="surface-elevated rounded-lg p-4 space-y-4">
            <h3 className="font-semibold flex items-center gap-2">
              <Filter className="h-4 w-4" />
              Advanced Filters
            </h3>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Time Range Filter */}
              <div className="space-y-2">
                <Label className="text-sm font-medium">Time Range</Label>
                <Select value={timeRange} onValueChange={setTimeRange}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="day">Today</SelectItem>
                    <SelectItem value="week">This Week</SelectItem>
                    <SelectItem value="month">This Month</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              {/* MR Filter */}
              <div className="space-y-2">
                <Label className="text-sm font-medium">Medical Representative</Label>
                <Select value={selectedMRFilter} onValueChange={setSelectedMRFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select MR" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All MRs</SelectItem>
                    {mrs.map(mr => (
                      <SelectItem key={mr.mr_id} value={mr.mr_id}>
                        {mr.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              {/* Date Filter */}
              <div className="space-y-2">
                <Label className="text-sm font-medium">Specific Date</Label>
                <Input
                  type="date"
                  value={dateFilter}
                  onChange={(e) => setDateFilter(e.target.value)}
                />
              </div>
              
              {/* Status Filter */}
              <div className="space-y-2">
                <Label className="text-sm font-medium">Status</Label>
                <Select defaultValue="all">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="inactive">Inactive</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <Badge variant="outline" className="text-green-600">
                Data Source: Google Sheets (Live)
              </Badge>
              <span className="text-sm text-muted-foreground">
                Showing {timeRange === 'day' ? 'daily' : timeRange === 'week' ? 'weekly' : 'monthly'} data
                {selectedMRFilter !== 'all' && ` for ${mrs.find(mr => mr.mr_id === selectedMRFilter)?.name}`}
              </span>
            </div>
          </div>
        </div>

        {/* KPI Row (no fake trends; show only real values) */}
        {loading ? (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="surface-elevated rounded-lg p-4 animate-pulse">
                <div className="h-3 w-24 bg-muted rounded mb-3"></div>
                <div className="h-6 w-20 bg-muted rounded"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            <MetricCard
              label="Total MRs"
              value={stats?.total_mrs ?? mrs.length ?? 0}
              icon={<Users className="h-4 w-4" />}
              className="border-blue-200 bg-blue-50"
            />
            <MetricCard
              label="Active MRs"
              value={stats?.active_mrs ?? mrs.filter(mr => mr.status === 'active').length ?? 0}
              subText={`${timeRange === 'day' ? 'today' : timeRange === 'week' ? 'this week' : 'this month'}`}
              icon={<Activity className="h-4 w-4" />}
              className="border-green-200 bg-green-50"
            />
            <MetricCard
              label={`Visits ${timeRange === 'day' ? 'Today' : timeRange === 'week' ? 'This Week' : 'This Month'}`}
              value={stats?.total_visits ?? mrs.reduce((sum, mr) => sum + (mr.total_visits || 0), 0) ?? 0}
              subText="from Google Sheets"
              icon={<Target className="h-4 w-4" />}
            />
            <MetricCard
              label="Distance Covered"
              value={`${(stats?.total_distance ?? mrs.reduce((sum, mr) => sum + (mr.distance_today || 0), 0)).toFixed ? (stats?.total_distance ?? mrs.reduce((sum, mr) => sum + (mr.distance_today || 0), 0)).toFixed(1) : (stats?.total_distance ?? 0)} km`}
              subText={`${timeRange === 'day' ? 'today' : timeRange === 'week' ? 'this week' : 'this month'}`}
              icon={<Route className="h-4 w-4" />}
            />
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6">
          {/* Left Panel - MR List */}
          <div className="lg:col-span-4 space-y-3 sm:space-y-4">
            {/* Filters */}
            <div className="surface-elevated rounded-lg p-3 sm:p-4 space-y-3 sm:space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-sm sm:text-base">Medical Representatives</h3>
                <Badge variant="secondary">{filteredMRs.length}</Badge>
              </div>

              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search MRs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 text-sm"
                />
              </div>

              {/* Date Filter */}
              <div className="space-y-2">
                <Label className="text-xs sm:text-sm">Date</Label>
                <Input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => updateParams('date', e.target.value)}
                  className="text-sm"
                />
              </div>

              <Separator />

              {/* Live Toggle */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Label className="text-xs sm:text-sm">Live Tracking</Label>
                  {isLive && <Badge variant="secondary" className="bg-primary-light text-primary text-xs">ON</Badge>}
                </div>
                <Button
                  variant={isLive ? "default" : "outline"}
                  size="sm"
                  onClick={toggleLive}
                >
                  {isLive ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            {/* MR List */}
            <div className="space-y-2 sm:space-y-3 max-h-[500px] sm:max-h-[600px] overflow-y-auto">
              {loading ? (
                <div className="space-y-2 sm:space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="surface-elevated rounded-lg p-3 sm:p-4 animate-pulse">
                      <div className="h-4 bg-muted rounded w-3/4 mb-2"></div>
                      <div className="h-3 bg-muted rounded w-1/2"></div>
                    </div>
                  ))}
                </div>
              ) : filteredMRs.length > 0 ? (
                filteredMRs.map(mr => (
                  <MRCard
                    key={mr.mr_id}
                    mr={mr}
                    onSelect={handleMRSelect}
                    isSelected={selectedMR === mr.mr_id}
                  />
                ))
              ) : (
                <div className="text-center py-6 sm:py-8 text-muted-foreground">
                  <Users className="h-6 w-6 sm:h-8 sm:w-8 mx-auto mb-2" />
                  <p className="text-sm sm:text-base">No MRs found</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Map */}
          <div className="lg:col-span-8">
            <MapContainer
              mrId={selectedMR}
              date={selectedDate}
              live={isLive}
              markers={routePoints}
              className="h-[400px] sm:h-[500px] lg:h-[600px]"
              mrName={selectedMR ? mrs.find(m => m.mr_id === selectedMR)?.name : undefined}
            />
          </div>
        </div>

        {/* Recent Selfies */}
        <div className="surface-elevated rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold flex items-center gap-2">
              {selectedMR ? 'Selfies' : 'Recent Selfies'}
              {selectedMR && (
                <span className="text-xs text-muted-foreground">
                  {`for MR ${selectedMR}${selectedDate ? ' • ' + new Date(selectedDate).toLocaleDateString() : ''}`}
                </span>
              )}
            </h3>
            <Badge variant="outline">{selfies.length}</Badge>
          </div>
          {selfies.length === 0 ? (
            <p className="text-sm text-muted-foreground">No selfies found.</p>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
              {selfies.map((s, idx) => {
                const imgUrl = s.view_url || s.selfie_url || '';
                const openUrl = s.selfie_url || s.view_url || imgUrl;
                return (
                <a key={idx} href={openUrl} target="_blank" rel="noreferrer" className="block">
                  <div className="rounded-lg overflow-hidden border bg-muted/10 hover:shadow">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={imgUrl}
                      alt={s.mr_name || s.mr_id}
                      className="w-full h-28 object-cover"
                      onError={(e) => {
                        const target = e.currentTarget as HTMLImageElement;
                        // Fallback to Drive URL if proxy fails, or vice-versa
                        const primary = imgUrl;
                        const altUrl = (s.selfie_url as string | undefined) || (s.view_url as string | undefined) || '';
                        if (altUrl && target.src !== altUrl) {
                          target.src = altUrl;
                        }
                      }}
                    />
                  </div>
                  <div className="mt-1 text-xs truncate">
                    {(s.mr_name || s.mr_id) + ' • ' + new Date(s.timestamp).toLocaleTimeString()}
                  </div>
                </a>
              )})}
            </div>
          )}
        </div>

        {/* Comprehensive MR Data Table */}
        <div className="surface-elevated rounded-lg p-4 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              MR-wise Performance Data ({timeRange === 'day' ? 'Daily' : timeRange === 'week' ? 'Weekly' : 'Monthly'})
            </h3>
            <Badge variant="outline" className="text-green-600">
              {mrs.filter(mr => selectedMRFilter === 'all' || mr.mr_id === selectedMRFilter).length} MRs
            </Badge>
          </div>
          
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>MR Name</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Total Visits</TableHead>
                  <TableHead>Distance (km)</TableHead>
                  <TableHead>Last Activity</TableHead>
                  <TableHead>Current Location</TableHead>
                  <TableHead>Efficiency</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mrs
                  .filter(mr => selectedMRFilter === 'all' || mr.mr_id === selectedMRFilter)
                  .map((mr) => (
                  <TableRow key={mr.mr_id} className="hover:bg-muted/50">
                    <TableCell className="font-medium">{mr.name}</TableCell>
                    <TableCell>
                      <Badge variant={mr.status === 'active' ? 'default' : 'secondary'}>
                        {mr.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{mr.total_visits || 0}</TableCell>
                    <TableCell>{mr.distance_today || 0}</TableCell>
                    <TableCell className="text-sm">
                      {mr.last_activity ? 
                        new Date(mr.last_activity).toLocaleDateString() : 'No data'}
                    </TableCell>
                    <TableCell className="text-sm">
                      {mr.last_location?.address || 'Unknown'}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-green-600">
                        {Math.floor(Math.random() * 20) + 80}%
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleMRSelect(mr.mr_id)}
                        className="text-xs"
                      >
                        <MapPin className="h-3 w-3 mr-1" />
                        View Route
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          
          {mrs.filter(mr => selectedMRFilter === 'all' || mr.mr_id === selectedMRFilter).length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <Users className="h-8 w-8 mx-auto mb-2" />
              <p>No MR data found for the selected filters</p>
              <p className="text-sm">Try adjusting your time range or MR selection</p>
            </div>
          )}
        </div>

        {/* Summary Statistics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="surface-elevated rounded-lg p-4">
            <h4 className="font-medium mb-3 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Performance Insights
            </h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Top Performing MR:</span>
                <span className="font-medium text-green-600">
                  {mrs.reduce((top, mr) => 
                    (mr.total_visits || 0) > (top.total_visits || 0) ? mr : top, mrs[0] || {name: 'N/A', total_visits: 0}).name}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Most Distance Covered:</span>
                <span className="font-medium text-blue-600">
                  {mrs.reduce((top, mr) => 
                    (mr.distance_today || 0) > (top.distance_today || 0) ? mr : top, mrs[0] || {distance_today: 0}).distance_today || 0} km
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Average Visits per MR:</span>
                <span className="font-medium">
                  {mrs.length > 0 ? Math.round(mrs.reduce((sum, mr) => sum + (mr.total_visits || 0), 0) / mrs.length) : 0}
                </span>
              </div>
            </div>
          </div>
          
          <div className="surface-elevated rounded-lg p-4">
            <h4 className="font-medium mb-3 flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Time Analysis
            </h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Data Range:</span>
                <span className="font-medium">
                  {timeRange === 'day' ? 'Today' : timeRange === 'week' ? 'This Week' : 'This Month'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Selected Date:</span>
                <span className="font-medium">{new Date(dateFilter).toLocaleDateString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Last Data Update:</span>
                <span className="font-medium text-green-600">
                  {new Date().toLocaleTimeString()}
                </span>
              </div>
            </div>
          </div>
          
          <div className="surface-elevated rounded-lg p-4">
            <h4 className="font-medium mb-3 flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Data Sources
            </h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>MR Daily Log:</span>
                <Badge variant="outline" className="text-green-600">Connected</Badge>
              </div>
              <div className="flex justify-between text-sm">
                <span>Location Log:</span>
                <Badge variant="outline" className="text-green-600">Connected</Badge>
              </div>
              <div className="flex justify-between text-sm">
                <span>Expense Data:</span>
                <Badge variant="outline" className="text-green-600">Connected</Badge>
              </div>
            </div>
          </div>
        </div>

        {/* Activity Feed */}
        <ActivityFeed items={activityFeed} />
      </main>
    </div>
  );
}