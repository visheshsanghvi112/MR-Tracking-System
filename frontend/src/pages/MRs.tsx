import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

import { MRCard } from "@/components/ui/mr-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { apiClient } from "@/lib/apiClient";
import { MedicalRepresentative } from "@/types";
import { 
  Search, 
  Users, 
  MapPin, 
  Clock,
  Route,
  Eye,
  Navigation,
  Grid3X3,
  List,
  Activity,
  Phone
} from "lucide-react";

export default function MRs() {
  const [mrs, setMRs] = useState<MedicalRepresentative[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const loadMRs = async () => {
      setLoading(true);
      try {
        const response = await apiClient.getMRs();
        if (response.success) {
          setMRs(response.data);
        }
      } catch (error) {
        console.error('Failed to load MRs:', error);
      } finally {
        setLoading(false);
      }
    };

    loadMRs();
  }, []);

  // Filter MRs - simplified to just search
  const filteredMRs = mrs.filter(mr => {
    const matchesSearch = mr.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         mr.mr_id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

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
    <div className="min-h-screen bg-background">
      <main className="container mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Field Representatives</h1>
            <p className="text-muted-foreground">
              Monitor your field team activities and performance
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('grid')}
            >
              <Grid3X3 className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'table' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('table')}
            >
              <List className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Search MRs</CardTitle>
            <CardDescription>Find medical representatives by name or ID</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Search */}
              <div className="space-y-2">
                <Label>Search</Label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search by name or ID..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
              </div>

              {/* Quick Stats */}
              <div className="space-y-2">
                <Label>Total MRs</Label>
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-blue-500" />
                  <span className="text-lg font-semibold">{mrs.length}</span>
                  <span className="text-sm text-muted-foreground">registered</span>
                </div>
              </div>

              {/* Results Count */}
              <div className="flex items-end">
                <Badge variant="secondary" className="h-10 px-4 flex items-center">
                  <Users className="h-4 w-4 mr-2" />
                  {filteredMRs.length} results
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="surface-elevated rounded-lg p-4 animate-pulse">
                <div className="h-4 bg-muted rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-muted rounded w-1/2 mb-4"></div>
                <div className="space-y-2">
                  <div className="h-3 bg-muted rounded"></div>
                  <div className="h-3 bg-muted rounded w-2/3"></div>
                </div>
              </div>
            ))}
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredMRs.map(mr => (
              <MRCard key={mr.mr_id} mr={mr} />
            ))}
            {filteredMRs.length === 0 && (
              <div className="col-span-full text-center py-12">
                <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No representatives found</h3>
                <p className="text-muted-foreground">
                  Try adjusting your search terms or check back later
                </p>
              </div>
            )}
          </div>
        ) : (
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Representative</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Last Activity</TableHead>
                    <TableHead>Current Location</TableHead>
                    <TableHead>Visit Stats</TableHead>
                    <TableHead>Contact</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredMRs.length > 0 ? filteredMRs.map(mr => (
                    <TableRow key={mr.mr_id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Avatar className="h-10 w-10">
                            <AvatarFallback>
                              {mr.name.split(' ').map(n => n[0]).join('').slice(0,2)}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <div className="font-medium">{mr.name}</div>
                            <div className="text-sm text-muted-foreground">ID: {mr.mr_id}</div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={mr.status} />
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2 text-sm">
                          <Clock className="h-4 w-4 text-muted-foreground" />
                          {formatLastSeen(mr.last_activity || mr.last_seen)}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1 text-sm">
                          {mr.last_location && mr.last_location.lat !== 0 && mr.last_location.lng !== 0 ? (
                            <>
                              <div className="flex items-center gap-2">
                                <MapPin className="h-3 w-3 text-red-500" />
                                <span className="font-mono text-xs">
                                  {mr.last_location.lat.toFixed(4)}, {mr.last_location.lng.toFixed(4)}
                                </span>
                              </div>
                              {mr.last_location.address && (
                                <div className="text-xs text-muted-foreground max-w-40 truncate">
                                  {mr.last_location.address}
                                </div>
                              )}
                              <div className="flex items-center gap-1">
                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                <span className="text-xs text-green-600">Live GPS</span>
                              </div>
                            </>
                          ) : (
                            <div className="flex items-center gap-2">
                              <MapPin className="h-3 w-3 text-gray-400" />
                              <span className="text-xs text-muted-foreground">No GPS data</span>
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1 text-sm">
                          <div className="flex items-center gap-2">
                            <MapPin className="h-3 w-3 text-blue-500" />
                            <span className="font-medium">{mr.total_visits || mr.visits_today || 0} visits</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Route className="h-3 w-3 text-green-500" />
                            <span>{mr.distance_today || 0} km covered</span>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Phone className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">+91 {mr.mr_id.slice(-4)}-{mr.mr_id.slice(-6, -4)}-{mr.mr_id.slice(-8, -6)}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Link to={`/mr/${mr.mr_id}`}>
                            <Button variant="outline" size="sm">
                              <Eye className="h-4 w-4 mr-1" />
                              View
                            </Button>
                          </Link>
                          <Link to={`/dashboard?mr_id=${mr.mr_id}&live=true`}>
                            <Button variant="default" size="sm">
                              <Navigation className="h-4 w-4 mr-1" />
                              Track
                            </Button>
                          </Link>
                        </div>
                      </TableCell>
                    </TableRow>
                  )) : (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-12">
                        <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                        <h3 className="text-lg font-semibold mb-2">No representatives found</h3>
                        <p className="text-muted-foreground">
                          Try adjusting your search terms or check back later
                        </p>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}