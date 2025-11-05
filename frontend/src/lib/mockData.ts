// Mock data for development and testing
import { MedicalRepresentative, RoutePoint, DashboardStats, ActivityFeedItem, TeamFilter, Blueprint } from '@/types';

export const mockMRs: MedicalRepresentative[] = [
  {
    mr_id: '1',
    name: 'Sarah Johnson',
    status: 'active',
    team_id: 'team-north',
    team_name: 'North Territory',
    last_seen: '2025-09-04T14:30:00Z',
    visits_today: 8,
    distance_today: 45.2,
    active_hours: 6.5,
    expenses_today: 125.50
  },
  {
    mr_id: '2',
    name: 'Michael Chen',
    status: 'active',
    team_id: 'team-south',
    team_name: 'South Territory',
    last_seen: '2025-09-04T14:45:00Z',
    visits_today: 6,
    distance_today: 38.7,
    active_hours: 5.8,
    expenses_today: 98.25
  },
  {
    mr_id: '3',
    name: 'Emma Rodriguez',
    status: 'idle',
    team_id: 'team-east',
    team_name: 'East Territory',
    last_seen: '2025-09-04T13:15:00Z',
    visits_today: 4,
    distance_today: 22.1,
    active_hours: 4.2,
    expenses_today: 67.80
  },
  {
    mr_id: '4',
    name: 'David Wilson',
    status: 'offline',
    team_id: 'team-west',
    team_name: 'West Territory',
    last_seen: '2025-09-04T11:20:00Z',
    visits_today: 3,
    distance_today: 15.6,
    active_hours: 2.5,
    expenses_today: 45.30
  }
];

export const mockRoutePoints: RoutePoint[] = [
  {
    id: '1',
    latitude: 40.7128,
    longitude: -74.0060,
    timestamp: '2025-09-04T09:00:00Z',
    type: 'visit',
    location_name: 'City General Hospital',
    visit_type: 'hospital',
    duration: 45,
    outcome: 'Meeting completed'
  },
  {
    id: '2',
    latitude: 40.7589,
    longitude: -73.9851,
    timestamp: '2025-09-04T10:30:00Z',
    type: 'visit',
    location_name: 'Central Pharmacy',
    visit_type: 'pharmacy',
    duration: 30,
    outcome: 'Product demo given'
  },
  {
    id: '3',
    latitude: 40.7831,
    longitude: -73.9712,
    timestamp: '2025-09-04T12:00:00Z',
    type: 'visit',
    location_name: 'Northside Clinic',
    visit_type: 'clinic',
    duration: 25,
    outcome: 'Follow-up scheduled'
  },
  {
    id: '4',
    latitude: 40.7505,
    longitude: -73.9934,
    timestamp: '2025-09-04T14:30:00Z',
    type: 'current',
    location_name: 'Current Location'
  }
];

export const mockDashboardStats: DashboardStats = {
  active_mrs: 12,
  visits_today: 47,
  distance_today: 234.5,
  efficiency_avg: 87.3
};

export const mockActivityFeed: ActivityFeedItem[] = [
  {
    id: '1',
    timestamp: '2025-09-04T14:45:00Z',
    mr_id: '2',
    mr_name: 'Michael Chen',
    type: 'visit',
    message: 'Completed visit at Downtown Medical Center'
  },
  {
    id: '2',
    timestamp: '2025-09-04T14:30:00Z',
    mr_id: '1',
    mr_name: 'Sarah Johnson',
    type: 'visit',
    message: 'Started visit at City General Hospital'
  },
  {
    id: '3',
    timestamp: '2025-09-04T13:15:00Z',
    mr_id: '3',
    mr_name: 'Emma Rodriguez',
    type: 'status_change',
    message: 'Status changed to idle'
  },
  {
    id: '4',
    timestamp: '2025-09-04T12:45:00Z',
    mr_id: '4',
    mr_name: 'David Wilson',
    type: 'route_end',
    message: 'Route completed for the day'
  }
];

export const mockTeams: TeamFilter[] = [
  { team_id: 'team-north', team_name: 'North Territory', mr_count: 4 },
  { team_id: 'team-south', team_name: 'South Territory', mr_count: 3 },
  { team_id: 'team-east', team_name: 'East Territory', mr_count: 3 },
  { team_id: 'team-west', team_name: 'West Territory', mr_count: 2 }
];

export const mockBlueprint: Blueprint = {
  total_visits: 8,
  total_distance: 45.2,
  visit_locations: [
    {
      id: '1',
      name: 'City General Hospital',
      type: 'hospital',
      latitude: 40.7128,
      longitude: -74.0060,
      address: '123 Main St, New York, NY 10001'
    },
    {
      id: '2',
      name: 'Central Pharmacy',
      type: 'pharmacy',
      latitude: 40.7589,
      longitude: -73.9851,
      address: '456 Broadway, New York, NY 10013'
    },
    {
      id: '3',
      name: 'Northside Clinic',
      type: 'clinic',
      latitude: 40.7831,
      longitude: -73.9712,
      address: '789 Park Ave, New York, NY 10075'
    }
  ]
};