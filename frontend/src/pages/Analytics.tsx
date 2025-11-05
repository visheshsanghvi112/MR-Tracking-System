import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricCard } from "@/components/ui/metric-card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiClient } from "@/lib/apiClient";
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Users, 
  MapPin, 
  Route,
  Calendar,
  Download,
  Award,
  Activity,
  Target,
  Clock,
  RefreshCw,
  ArrowUp,
  ArrowDown
} from "lucide-react";

interface AnalyticsData {
  overview: {
    total_mrs: number;
    active_mrs: number;
    total_visits: number;
    avg_efficiency: number;
    total_distance: number;
  };
  top_performers: Array<{
    rank: number;
    name: string;
    mr_id: string;
    efficiency: number;
    visits: number;
    distance: number;
    team: string;
  }>;
  weekly_trend: Array<{
    period: string;
    efficiency: number;
    visits: number;
    distance: number;
  }>;
  team_performance: Array<{
    team: string;
    members: number;
    avg_efficiency: number;
    total_visits: number;
    total_distance: number;
  }>;
  recent_activity?: Array<{
    mr_name: string;
    location?: string;
    timestamp?: string;
    activity_type?: string;
    gps_coordinates?: string;
  }>;
}

export default function Analytics() {
  const [selectedPeriod, setSelectedPeriod] = useState("weekly");
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load analytics data
  useEffect(() => {
    loadAnalytics();
  }, [selectedPeriod]);

  const loadAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get dashboard stats and activity feed from real API
      const [statsResponse, activityResponse] = await Promise.all([
        apiClient.getDashboardStats(),
        apiClient.getActivityFeed()
      ]);

      if (statsResponse.success && activityResponse.success) {
        // Transform real data into analytics format
        const stats = statsResponse.data;
        const activities = activityResponse.data;

        const analyticsData: AnalyticsData = {
          overview: {
            total_mrs: stats.total_mrs || 0,
            active_mrs: stats.active_mrs || 0,
            total_visits: stats.total_visits || 0,
            avg_efficiency: (stats as any).efficiency_avg || 0,
            total_distance: stats.total_distance || 0
          },
          top_performers: [],
          weekly_trend: [],
          team_performance: [],
          recent_activity: activities.slice(0, 10).map(activity => ({
            mr_name: activity.mr_name || 'Unknown MR',
            location: activity.message || 'Unknown Location', // Use message as location
            timestamp: activity.timestamp,
            activity_type: activity.type || 'activity',
            gps_coordinates: '' // Not available in ActivityFeedItem
          }))
        };

        setAnalyticsData(analyticsData);
      } else {
        setError("Failed to load analytics data");
      }
    } catch (err) {
      setError("Error connecting to API");
      console.error("Analytics error:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-6">
        <Card>
          <CardContent className="p-6 text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={loadAnalytics}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
          <p className="text-muted-foreground">
            Performance insights and team analytics
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="daily">Daily</SelectItem>
              <SelectItem value="weekly">Weekly</SelectItem>
              <SelectItem value="monthly">Monthly</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={loadAnalytics} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Overview Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard
          label="Total MRs"
          value={analyticsData?.overview.total_mrs.toString() || "0"}
          icon={<Users className="h-4 w-4" />}
        />
        <MetricCard
          label="Active MRs"
          value={analyticsData?.overview.active_mrs.toString() || "0"}
          icon={<Activity className="h-4 w-4" />}
          className="border-green-200 bg-green-50"
        />
        <MetricCard
          label="Total Visits"
          value={analyticsData?.overview.total_visits.toString() || "0"}
          icon={<Target className="h-4 w-4" />}
        />
        <MetricCard
          label="Distance (km)"
          value={analyticsData?.overview.total_distance.toString() || "0"}
          icon={<Route className="h-4 w-4" />}
        />
        <MetricCard
          label="Avg Efficiency"
          value={`${analyticsData?.overview.avg_efficiency.toString() || "0"}%`}
          icon={<Award className="h-4 w-4" />}
          className="border-blue-200 bg-blue-50"
        />
      </div>

      <Tabs defaultValue="performance" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="activity">Recent Activity</TabsTrigger>
        </TabsList>

        <TabsContent value="performance" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Performers */}
            {analyticsData?.top_performers && analyticsData.top_performers.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="h-5 w-5" />
                  Top Performers
                </CardTitle>
                <CardDescription>
                  Highest performing MRs this {selectedPeriod}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analyticsData?.top_performers.map((performer, index) => (
                    <div key={performer.mr_id} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <Badge variant={index === 0 ? "default" : "secondary"}>
                          #{performer.rank}
                        </Badge>
                        <div>
                          <p className="font-medium">{performer.name}</p>
                          <p className="text-sm text-muted-foreground">{performer.team}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{performer.efficiency}%</p>
                        <p className="text-sm text-muted-foreground">{performer.visits} visits</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="h-5 w-5" />
                    Top Performers
                  </CardTitle>
                  <CardDescription>Not available</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-muted-foreground">No ranking data available from backend.</div>
                </CardContent>
              </Card>
            )}

            {/* Team Performance */}
            {analyticsData?.team_performance && analyticsData.team_performance.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Team Performance
                </CardTitle>
                <CardDescription>
                  Performance by team
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analyticsData?.team_performance.map((team, index) => (
                    <div key={team.team} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">{team.team}</p>
                          <p className="text-sm text-muted-foreground">{team.members} members</p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">{team.avg_efficiency}%</p>
                          <p className="text-sm text-muted-foreground">{team.total_visits} visits</p>
                        </div>
                      </div>
                      <Progress value={team.avg_efficiency} className="h-2" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    Team Performance
                  </CardTitle>
                  <CardDescription>Not available</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-muted-foreground">No team aggregates available from backend.</div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="activity" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Recent Activity
              </CardTitle>
              <CardDescription>
                Latest field activities from your team
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>MR Name</TableHead>
                    <TableHead>Activity</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Time</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {analyticsData?.recent_activity?.map((activity, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">{activity.mr_name}</TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {activity.activity_type || 'Field Activity'}
                        </Badge>
                      </TableCell>
                      <TableCell>{activity.location || 'Unknown'}</TableCell>
                      <TableCell>
                        {activity.timestamp ? 
                          new Date(activity.timestamp).toLocaleTimeString() : 
                          'N/A'
                        }
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Trends tab removed until real series data is available */}
      </Tabs>
    </div>
  );
}
