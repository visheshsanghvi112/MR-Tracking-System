// Core types for MR Tracking application

export interface MedicalRepresentative {
  mr_id: string;
  name: string;
  status: 'active' | 'offline' | 'idle';
  team_id?: string;
  team_name?: string;
  last_seen?: string;
  visits_today?: number;
  distance_today?: number;
  active_hours?: number;
  expenses_today?: number;
  last_location?: {
    lat: number;
    lng: number;
    address?: string;
  };
  last_activity?: string;
  total_visits?: number;
}

export interface RoutePoint {
  id: string;
  latitude: number;
  longitude: number;
  timestamp: string;
  type: 'visit' | 'travel' | 'current';
  location_name?: string;
  address?: string;
  visit_type?: 'hospital' | 'pharmacy' | 'clinic' | 'other';
  duration?: number;
  outcome?: string;
  contact_name?: string;
  orders?: string;
}

export interface RouteStats {
  total_distance: number;
  total_visits: number;
  active_hours: number;
  efficiency_score: number;
}

export interface VisitLocation {
  id: string;
  name: string;
  type: 'hospital' | 'pharmacy' | 'clinic' | 'other';
  latitude: number;
  longitude: number;
  address: string;
}

export interface Blueprint {
  total_visits: number;
  total_distance: number;
  visit_locations: VisitLocation[];
}

export interface DashboardStats {
  total_mrs: number;
  active_mrs: number;
  total_visits: number;
  total_distance: number;
  avg_visits_per_mr: number;
  top_performer: string;
  performance_trend: 'up' | 'down';
}

export interface ActivityFeedItem {
  id: string;
  timestamp: string;
  mr_id?: string;
  mr_name?: string;
  type: 'visit' | 'status_change' | 'route_start' | 'route_end';
  message: string;
}

export interface TeamFilter {
  team_id: string;
  team_name: string;
  mr_count: number;
}

export interface WebSocketMessage {
  type: 'location' | 'visit' | 'status';
  payload: {
    mr_id: string;
    timestamp: string;
    data: Record<string, unknown>;
  };
}