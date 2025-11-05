// API client with swappable adapters (mock vs real)
import { MedicalRepresentative, RoutePoint, DashboardStats, ActivityFeedItem, Blueprint } from '@/types';
import { 
  mockMRs, 
  mockRoutePoints, 
  mockDashboardStats, 
  mockActivityFeed, 
  mockBlueprint 
} from './mockData';

// API response wrapper
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

// Abstract API adapter interface
export interface ApiAdapter {
  getMRs(): Promise<ApiResponse<MedicalRepresentative[]>>;
  getRoute(mrId: string, date: string): Promise<ApiResponse<{ points: RoutePoint[]; stats: any }>>;
  getBlueprint(mrId: string, date: string): Promise<ApiResponse<Blueprint>>;
  getDashboardStats(): Promise<ApiResponse<DashboardStats>>;
  getActivityFeed(): Promise<ApiResponse<ActivityFeedItem[]>>;
  getMRDetail(mrId: string): Promise<ApiResponse<MedicalRepresentative>>;
  getRecentSelfies(limit?: number): Promise<ApiResponse<any[]>>;
  // Optional legacy-friendly alias used by Dashboard
  getSelfieVerifications?(mrId?: string, limit?: number): Promise<ApiResponse<any[]>>;
}

// Mock adapter for development
export class MockApiAdapter implements ApiAdapter {
  private delay(ms: number = 500): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async getMRs(): Promise<ApiResponse<MedicalRepresentative[]>> {
    await this.delay();
    return { success: true, data: mockMRs };
  }

  async getRoute(mrId: string, date: string): Promise<ApiResponse<{ points: RoutePoint[]; stats: any }>> {
    await this.delay();
    return { 
      success: true, 
      data: { 
        points: mockRoutePoints,
        stats: {
          total_distance: 45.2,
          total_visits: 8,
          active_hours: 6.5,
          efficiency_score: 87.3
        }
      }
    };
  }

  async getBlueprint(mrId: string, date: string): Promise<ApiResponse<Blueprint>> {
    await this.delay();
    return { success: true, data: mockBlueprint };
  }

  async getDashboardStats(): Promise<ApiResponse<DashboardStats>> {
    await this.delay();
    return { success: true, data: mockDashboardStats };
  }

  async getActivityFeed(): Promise<ApiResponse<ActivityFeedItem[]>> {
    await this.delay();
    return { success: true, data: mockActivityFeed };
  }

  async getMRDetail(mrId: string): Promise<ApiResponse<MedicalRepresentative>> {
    await this.delay();
    const mr = mockMRs.find(m => m.mr_id === mrId);
    if (!mr) {
      return { success: false, data: {} as MedicalRepresentative, message: 'MR not found' };
    }
    return { success: true, data: mr };
  }

  async getRecentSelfies(limit: number = 12): Promise<ApiResponse<any[]>> {
    await this.delay();
    return { success: true, data: [] };
  }

  async getSelfieVerifications(mrId?: string, limit: number = 50): Promise<ApiResponse<any[]>> {
    // Mirror recent selfies; filter by mrId if provided
    const base = await this.getRecentSelfies(limit);
    if (!base.success) return base;
    if (mrId) {
      return { success: true, data: base.data.filter((i: any) => String(i.mr_id) === String(mrId)) };
    }
    return base;
  }
}

// Real Backend API adapter - UNCOMMENTED AND WORKING VERSION
export class RealBackendApiAdapter implements ApiAdapter {
  private getBaseUrl(): string {
    try {
      const saved = localStorage.getItem('mr-tracking-admin-settings');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.apiUrl) return parsed.apiUrl;
      }
    } catch {}
    return (import.meta.env.VITE_API_URL as string) || 'http://localhost:8000';
  }

  private getHeaders(): Record<string, string> {
    let apiKey = (import.meta.env.VITE_API_KEY as string) || 'mr-tracking-2025';
    try {
      const saved = localStorage.getItem('mr-tracking-admin-settings');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.apiKey) apiKey = parsed.apiKey;
      }
    } catch {}
    return {
      'X-API-Key': apiKey,
      'Content-Type': 'application/json'
    };
  }

  async getMRs(): Promise<ApiResponse<MedicalRepresentative[]>> {
    try {
      const response = await fetch(`${this.getBaseUrl()}/api/mrs`, {
        headers: this.getHeaders()
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      if (result.success && result.mrs) {
        // Transform backend MR data to frontend format
        const mrs = result.mrs.map((mr: any) => ({
          mr_id: mr.mr_id,
          name: mr.name,
          status: mr.status,
          team_id: `team_${mr.mr_id}`,
          team_name: 'Field Team',
          last_seen: mr.last_activity,
          last_activity: mr.last_activity,
          total_visits: mr.total_visits,
          visits_today: mr.total_visits,
          distance_today: mr.distance_today || 0,
          active_hours: 8,
          expenses_today: 2500,
          last_location: mr.last_location ? {
            lat: mr.last_location.lat || mr.last_location.latitude || 0,
            lng: mr.last_location.lng || mr.last_location.longitude || 0,
            address: mr.last_location.address || 'Unknown Location'
          } : {
            lat: 0,
            lng: 0,
            address: 'No location data'
          }
        }));

        console.log('✅ Loaded MRs with real GPS data:', mrs);
        return { success: true, data: mrs };
      } else {
        throw new Error('Invalid MR data format');
      }
    } catch (error) {
      console.error('❌ Failed to fetch MRs:', error);
      return {
        success: false,
        data: [],
        message: `API Error: ${error}`
      };
    }
  }

  async getRoute(mrId: string, date: string): Promise<ApiResponse<{ points: RoutePoint[]; stats: any }>> {
   try {
     console.log(`🔍 Fetching route data for MR ${mrId} on ${date}`);
     const response = await fetch(`${this.getBaseUrl()}/api/route?mr_id=${mrId}&date=${date}`, {
       headers: this.getHeaders()
     });

     if (!response.ok) {
       throw new Error(`HTTP ${response.status}: ${response.statusText}`);
     }

     const result = await response.json();
     console.log('📦 Raw backend response:', result);

     // Transform backend data to frontend format
     if (result.success && result.points && Array.isArray(result.points)) {
       const transformedPoints: RoutePoint[] = result.points.map((point: any, index: number) => {
         // Backend returns: {time, lat, lng, type, location, details, timestamp, accuracy, speed, heading}
         // Frontend expects: {id, latitude, longitude, timestamp, type, location_name, visit_type, duration, outcome}
         
         // Map backend type to frontend type
         let frontendType: 'visit' | 'travel' | 'current' = 'visit';
         if (point.type === 'start') frontendType = 'visit';
         else if (point.type === 'visit') frontendType = 'visit';
         else if (point.type === 'movement') frontendType = 'travel';
         else if (point.type === 'current') frontendType = 'current';
         
         const transformed: RoutePoint = {
           id: point.id || `${mrId}_${date}_${index}_${point.time || Date.now()}`,
           latitude: Number(point.lat || point.latitude || 0),
           longitude: Number(point.lng || point.longitude || 0),
           timestamp: point.timestamp || new Date().toISOString(),
           type: frontendType,
           location_name: point.location || point.location_name || `Location ${index + 1}`,
           address: point.address || point.location || undefined,
           visit_type: point.visit_type || (frontendType === 'visit' ? 'other' : undefined),
           duration: point.duration || undefined,
           outcome: point.outcome || point.details || undefined,
           contact_name: point.contact_name || undefined,
           orders: point.orders || undefined
         };
         
        console.log(`  📍 Point ${index + 1}:`, {
          raw_backend: { lat: point.lat, lng: point.lng, latitude: point.latitude, longitude: point.longitude },
          transformed: { lat: transformed.latitude, lng: transformed.longitude },
          location: transformed.location_name,
          contact_name: transformed.contact_name || '(no contact)',
          orders: transformed.orders || '(no orders)',
          visit_type: transformed.visit_type || '(no visit_type)'
        });
         return transformed;
       });

       console.log(`✅ Transformed ${transformedPoints.length} route points for MR ${mrId}`);
       
       // Filter out invalid coordinates
       const validPoints = transformedPoints.filter(point => 
         point.latitude !== 0 &&
         point.longitude !== 0 &&
         point.latitude >= -90 && point.latitude <= 90 &&
         point.longitude >= -180 && point.longitude <= 180
       );
       
       if (validPoints.length < transformedPoints.length) {
         console.warn(`⚠️ Filtered out ${transformedPoints.length - validPoints.length} invalid points`);
       }

       return {
         success: true,
         data: {
           points: validPoints,
           stats: result.stats || result.data?.stats || {
             total_distance: 0,
             total_visits: validPoints.filter(p => p.type === 'visit').length,
             active_hours: 0,
             efficiency_score: 0
           }
         }
       };
     }

     console.warn('⚠️ No valid route data in backend response');
     return { success: false, data: { points: [], stats: {} }, message: 'No route data available' };
   } catch (error) {
     console.error('❌ Failed to fetch route from backend:', error);
     // Return empty data instead of mock data
     return {
       success: false,
       data: {
         points: [],
         stats: {
           total_distance: 0,
           total_visits: 0,
           active_hours: 0,
           efficiency_score: 0
         }
       },
       message: `Failed to fetch route data: ${error}`
     };
   }
 }

  async getBlueprint(mrId: string, date: string): Promise<ApiResponse<Blueprint>> {
    try {
      console.log(`🗺️ Fetching blueprint for MR ${mrId} on ${date}`);
      const response = await fetch(`${this.getBaseUrl()}/api/v2/route-blueprint/${mrId}?date=${date}`, {
        headers: this.getHeaders()
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('📦 Raw blueprint response:', result);

      if (result.success && result.blueprint) {
        const blueprint = result.blueprint;
        
        // Transform backend blueprint to frontend format
        const transformedBlueprint: Blueprint = {
          total_visits: blueprint.total_visits || 0,
          total_distance: blueprint.total_distance_km || 0,
          visit_locations: (blueprint.visit_locations || []).map((v: any) => ({
            id: `visit_${v.sequence || Math.random()}`,
            name: v.location_name || 'Unknown',
            type: v.visit_type || 'other',
            latitude: v.latitude || 0,
            longitude: v.longitude || 0,
            address: v.details || ''
          }))
        };

        console.log(`✅ Blueprint loaded: ${transformedBlueprint.total_visits} visits`);
        return { success: true, data: transformedBlueprint };
      }

      console.warn('⚠️ No blueprint data in response');
      return {
        success: false,
        data: { total_visits: 0, total_distance: 0, visit_locations: [] },
        message: result.error || 'No blueprint data available'
      };
    } catch (error) {
      console.error('❌ Failed to fetch blueprint:', error);
      return {
        success: false,
        data: { total_visits: 0, total_distance: 0, visit_locations: [] },
        message: `Failed to fetch blueprint: ${error}`
      };
    }
  }

  async getDashboardStats(): Promise<ApiResponse<DashboardStats>> {
    try {
      const response = await fetch(`${this.getBaseUrl()}/api/analytics`, {
        headers: this.getHeaders()
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();

      if (result.success && result.data) {
        return {
          success: true,
          data: {
            total_mrs: result.data.total_mrs || 0,
            active_mrs: result.data.active_mrs || 0,
            total_visits: result.data.total_visits || 0,
            total_distance: result.data.total_distance || 0,
            avg_visits_per_mr: result.data.avg_visits_per_mr || 0,
            top_performer: 'Field Team Leader',
            performance_trend: 'up' as const
          }
        };
      } else {
        throw new Error('Invalid analytics data');
      }
    } catch (error) {
      console.error('Failed to fetch dashboard stats from backend:', error);
      return {
        success: false,
        data: {
          total_mrs: 0,
          active_mrs: 0,
          total_visits: 0,
          total_distance: 0,
          avg_visits_per_mr: 0,
          top_performer: 'No data',
          performance_trend: 'down' as const
        },
        message: 'Failed to fetch dashboard stats from Google Sheets'
      };
    }
  }

  async getActivityFeed(): Promise<ApiResponse<ActivityFeedItem[]>> {
    try {
      const response = await fetch(`${this.getBaseUrl()}/api/activity?limit=10`, {
        headers: this.getHeaders()
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();

      if (result.success && result.activities) {
        const activities = result.activities.map((activity: any) => ({
          id: activity.id,
          timestamp: activity.timestamp,
          mr_id: activity.mr_id || 'unknown',
          mr_name: activity.mr_name || 'Unknown MR',
          type: activity.action === 'visit_completed' ? 'visit' as const : 'status_change' as const,
          message: activity.details || activity.message || 'Activity',
          location: activity.location,
          gps_coordinates: activity.gps_coordinates
        }));

        console.log('✅ Loaded activity feed with real data:', activities);
        return { success: true, data: activities };
      } else {
        throw new Error('Invalid activity data');
      }
    } catch (error) {
      console.error('Failed to fetch activity feed from backend:', error);
      return {
        success: false,
        data: [],
        message: 'Failed to fetch activity feed from Google Sheets'
      };
    }
  }

  async getMRDetail(mrId: string): Promise<ApiResponse<MedicalRepresentative>> {
    try {
      const response = await fetch(`${this.getBaseUrl()}/api/mrs`, {
        headers: this.getHeaders()
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success && result.mrs) {
        const mr = result.mrs.find((mr: any) => mr.mr_id === mrId);
        
        if (!mr) {
          return {
            success: false,
            data: {} as MedicalRepresentative,
            message: 'MR not found'
          };
        }

        return {
          success: true,
          data: {
            mr_id: mr.mr_id,
            name: mr.name,
            status: mr.status,
            team_id: `team_${mr.mr_id}`,
            team_name: 'Field Team',
            last_seen: mr.last_activity,
            last_activity: mr.last_activity,
            total_visits: mr.total_visits,
            visits_today: mr.total_visits,
            distance_today: mr.distance_today || 0,
            active_hours: 8,
            expenses_today: 2500,
            last_location: mr.last_location ? {
              lat: mr.last_location.lat || mr.last_location.latitude || 0,
              lng: mr.last_location.lng || mr.last_location.longitude || 0,
              address: mr.last_location.address || 'Unknown Location'
            } : {
              lat: 0,
              lng: 0,
              address: 'No location data'
            }
          }
        };
      } else {
        throw new Error('Backend API error');
      }
    } catch (error) {
      console.error('Failed to fetch MR detail from backend:', error);
      return {
        success: false,
        data: {} as MedicalRepresentative,
        message: 'Backend API error'
      };
    }
  }

  async getRecentSelfies(limit: number = 12): Promise<ApiResponse<any[]>> {
    try {
      const base = this.getBaseUrl();
      const response = await fetch(`${base}/api/verification/selfies?limit=${limit}`, {
        headers: this.getHeaders()
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const result = await response.json();
      if (result.success && Array.isArray(result.items)) {
        // Ensure a usable view URL exists for each item
        const apiKey = this.getHeaders()['X-API-Key'];
        const toDrivePreview = (url: string | undefined) => {
          if (!url) return undefined;
          try {
            // Convert https://drive.google.com/file/d/{id}/view?... to direct preview URL
            const m = url.match(/https?:\/\/drive\.google\.com\/file\/d\/([^/]+)\//);
            if (m && m[1]) {
              const id = m[1];
              return `https://drive.google.com/uc?export=view&id=${id}`;
            }
          } catch {}
          return url;
        };
        const items = result.items.map((i: any) => {
          const proxyUrl = i.file_id ? `${base}/api/verification/selfies/${i.file_id}/download?key=${encodeURIComponent(apiKey)}` : undefined;
          const drivePreview = toDrivePreview(i.selfie_url);
          // Prefer proxy (always accessible if token ok); fall back to Drive preview
          return { ...i, view_url: proxyUrl || drivePreview };
        });
        return { success: true, data: items };
      }
      return { success: false, data: [], message: 'No selfie data' };
    } catch (error) {
      console.error('❌ Failed to fetch selfies:', error);
      return { success: false, data: [], message: `API Error: ${error}` };
    }
  }

  async getSelfieVerifications(mrId?: string, limit: number = 50): Promise<ApiResponse<any[]>> {
    try {
      const base = this.getBaseUrl();
      const apiKey = this.getHeaders()['X-API-Key'];
      const url = `${base}/api/verification/selfies?limit=${limit}${mrId ? `&mr_id=${mrId}` : ''}`;
      const response = await fetch(url, { headers: this.getHeaders() });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const result = await response.json();
      if (result.success && Array.isArray(result.items)) {
        const toDrivePreview = (u: string | undefined) => {
          if (!u) return undefined;
          try {
            const m = u.match(/https?:\/\/drive\.google\.com\/file\/d\/([^/]+)\//);
            if (m && m[1]) return `https://drive.google.com/uc?export=view&id=${m[1]}`;
          } catch {}
          return u;
        };
        const items = result.items.map((i: any) => {
          const drivePreview = toDrivePreview(i.selfie_url);
          const proxyUrl = i.file_id ? `${base}/api/verification/selfies/${i.file_id}/download?key=${encodeURIComponent(apiKey)}` : undefined;
          // Prefer proxy first for universal access; fall back to Drive
          return { ...i, view_url: proxyUrl || drivePreview };
        });
        return { success: true, data: items };
      }
      return { success: false, data: [], message: 'No selfie data' };
    } catch (error) {
      console.error('❌ Failed to fetch selfie verifications:', error);
      return { success: false, data: [], message: `API Error: ${error}` };
    }
  }
}

// API client with swappable adapter
class ApiClient {
  private adapter: ApiAdapter;

  constructor(adapter: ApiAdapter) {
    this.adapter = adapter;
  }

  setAdapter(adapter: ApiAdapter) {
    this.adapter = adapter;
  }

  getMRs() { return this.adapter.getMRs(); }
  getRoute(mrId: string, date: string) { return this.adapter.getRoute(mrId, date); }
  getBlueprint(mrId: string, date: string) { return this.adapter.getBlueprint(mrId, date); }
  getDashboardStats() { return this.adapter.getDashboardStats(); }
  getActivityFeed() { return this.adapter.getActivityFeed(); }
  getMRDetail(mrId: string) { return this.adapter.getMRDetail(mrId); }
  getRecentSelfies(limit?: number) { return this.adapter.getRecentSelfies(limit); }
  // Legacy-friendly wrapper used by Dashboard.tsx
  getSelfieVerifications(mrId?: string, limit: number = 50) {
    if (typeof this.adapter.getSelfieVerifications === 'function') {
      return this.adapter.getSelfieVerifications(mrId, limit);
    }
    // Fallback to recent selfies and filter client-side
    return this.adapter.getRecentSelfies(limit).then(res => {
      if (!res.success) return res;
      if (mrId) {
        return { success: true, data: res.data.filter((i: any) => String(i.mr_id) === String(mrId)) };
      }
      return res;
    });
  }
}

// Default client - use Real Backend API adapter to get real data from Google Sheets
const realBackendAdapter = new RealBackendApiAdapter();
const client = new ApiClient(realBackendAdapter);
export const apiClient = client;

// WebSocket manager (mock implementation)
export class WebSocketManager {
  private ws: WebSocket | null = null;
  private listeners: ((message: any) => void)[] = [];

  connect(mrId?: string) {
    // Mock WebSocket behavior
    console.log('WebSocket connected (mock)', mrId);
    
    // Simulate periodic location updates
    setInterval(() => {
      this.listeners.forEach(listener => {
        listener({
          type: 'location',
          payload: {
            mr_id: mrId || '1',
            timestamp: new Date().toISOString(),
            data: {
              latitude: 40.7128 + (Math.random() - 0.5) * 0.01,
              longitude: -74.0060 + (Math.random() - 0.5) * 0.01
            }
          }
        });
      });
    }, 5000);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  onMessage(callback: (message: any) => void) {
    this.listeners.push(callback);
  }

  removeListener(callback: (message: any) => void) {
    const index = this.listeners.indexOf(callback);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }
}

export const wsManager = new WebSocketManager();