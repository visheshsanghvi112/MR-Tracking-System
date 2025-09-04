'use client';

import React, { useEffect, useRef, useState } from 'react';
// Types from '@/lib/types' not needed directly here

interface MapContainerProps {
  mrId: string;
  date?: string;
  className?: string;
}

const MapContainer: React.FC<MapContainerProps> = ({ mrId, date, className = '' }) => {
  const mapRef = useRef<HTMLDivElement>(null);
  type TransformedRoute = {
    center: { lat: number; lng: number };
    markers: Array<{
      id: number | string;
      position: { lat: number; lng: number };
      title: string;
      info?: {
        type: string;
        time?: string;
        duration?: string;
        outcome?: string;
      };
    }>;
    route: Array<{ lat: number; lng: number }>;
    stats: { total_visits: number; total_distance: number; efficiency: number };
  } | null;

  const [routeData, setRouteData] = useState<TransformedRoute>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [leafletLoaded, setLeafletLoaded] = useState(false);

  // Load Leaflet dynamically
  useEffect(() => {
    const loadLeaflet = async () => {
      try {
        // Load Leaflet CSS
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
        document.head.appendChild(link);

        // Load Leaflet JS
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
        script.onload = () => setLeafletLoaded(true);
        document.head.appendChild(script);
      } catch (err) {
        console.error('Error loading Leaflet:', err);
        setError('Failed to load map library');
      }
    };

    if (!window.L) {
      loadLeaflet();
    } else {
      setLeafletLoaded(true);
    }
  }, []);

  // Fetch route data
  useEffect(() => {
    const fetchData = async () => {
      if (!mrId) return;

      setLoading(true);
      setError(null);

      try {
        // Use our visit-based tracking API
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const endpoint = date 
          ? `${apiUrl}/api/v2/route-blueprint/${mrId}?date=${date}`
          : `${apiUrl}/api/v2/route-blueprint/${mrId}`;
        
        const response = await fetch(endpoint);
        
        if (!response.ok) {
          throw new Error(`API Error: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success && result.data) {
          // Transform the data to match our map format
          const blueprint = result.data;
          const transformedData: TransformedRoute = {
            center: {
              lat: blueprint.visit_locations?.length > 0 
                ? blueprint.visit_locations.reduce((sum: number, visit: { latitude: number }) => sum + visit.latitude, 0) / blueprint.visit_locations.length
                : 19.0760,
              lng: blueprint.visit_locations?.length > 0
                ? blueprint.visit_locations.reduce((sum: number, visit: { longitude: number }) => sum + visit.longitude, 0) / blueprint.visit_locations.length
                : 72.8777
            },
            markers: blueprint.visit_locations?.map((visit: { latitude: number; longitude: number; location_name: string; location_type: string; visit_time?: string; visit_duration?: number; visit_outcome?: string }, index: number) => ({
              id: index,
              position: { lat: visit.latitude, lng: visit.longitude },
              title: visit.location_name,
              info: {
                type: visit.location_type,
                time: visit.visit_time,
                duration: typeof visit.visit_duration === 'number' ? `${visit.visit_duration} min` : undefined,
                outcome: visit.visit_outcome
              }
            })) || [],
            route: blueprint.visit_locations?.map((visit: { latitude: number; longitude: number }) => ({
              lat: visit.latitude,
              lng: visit.longitude
            })) || [],
            stats: {
              total_visits: blueprint.total_visits || 0,
              total_distance: blueprint.total_distance || 0,
              efficiency: blueprint.route_efficiency || 0
            }
          };
          
          setRouteData(transformedData);
        } else {
          setError(result.message || 'No route data available for this MR');
        }
      } catch (err) {
        console.error('Error fetching route data:', err);
        setError('Failed to load route data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [mrId, date]);

  // Initialize map when Leaflet is loaded
  useEffect(() => {
    if (!leafletLoaded || !mapRef.current || !routeData) return;

    type LeafletNamespace = {
      map: (...args: unknown[]) => unknown;
      tileLayer: (
        template: string,
        options: { attribution?: string }
      ) => { addTo: (map: unknown) => unknown };
      marker: (
        latLng: [number, number],
        options: { icon?: unknown }
      ) => { addTo: (map: unknown) => unknown; bindPopup: (html: string) => unknown };
      divIcon: (options: { className: string; html: string; iconSize: [number, number]; iconAnchor: [number, number] }) => unknown;
      featureGroup: new (layers: unknown[]) => { getBounds: () => { pad: (n: number) => unknown } };
      polyline: (
        latLngs: Array<[number, number]>,
        options: { color?: string; weight?: number; opacity?: number; dashArray?: string }
      ) => { addTo: (map: unknown) => unknown };
    };

    const L = (window as unknown as { L: LeafletNamespace }).L;
    
    // Clear any existing map
    if (mapRef.current) {
      mapRef.current.innerHTML = '';
    }

    // Create map
    const map = L.map(mapRef.current, {
      center: [routeData.center?.lat || 19.0760, routeData.center?.lng || 72.8777],
      zoom: 12,
      zoomControl: true,
      scrollWheelZoom: true,
    }) as unknown as { fitBounds: (b: unknown) => void; remove: () => void };

    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Add visit markers
    const markers: object[] = [];
    if (routeData.markers) {
      type Marker = NonNullable<TransformedRoute>['markers'][number];
      routeData.markers.forEach((marker: Marker, index: number) => {
        const icon = L.divIcon({
          className: 'custom-marker',
          html: `
            <div style="
              width: 30px; 
              height: 30px; 
              border-radius: 50%; 
              border: 3px solid white; 
              box-shadow: 0 4px 8px rgba(0,0,0,0.2);
              display: flex; 
              align-items: center; 
              justify-content: center; 
              font-weight: 600; 
              font-size: 12px; 
              color: white;
              cursor: pointer;
              background-color: ${getMarkerColor(marker.info?.type || 'general')};
            ">
              ${index + 1}
            </div>
          `,
          iconSize: [30, 30],
          iconAnchor: [15, 15]
        });

        type LeafletMarker = { bindPopup: (html: string) => unknown } & object;
        const leafletMarker = L.marker([marker.position.lat, marker.position.lng], { icon }).addTo(map) as unknown as LeafletMarker;

        // Add popup
        const popupContent = `
          <div style="padding: 12px; min-width: 200px;">
            <h3 style="font-weight: bold; color: #2563eb; margin-bottom: 8px;">${marker.title}</h3>
            <div style="font-size: 14px;">
              <div style="margin-bottom: 4px;">
                <strong>Type:</strong> 
                <span style="background: #dbeafe; color: #1d4ed8; padding: 2px 8px; border-radius: 4px; font-size: 12px;">
                  ${marker.info?.type || 'general'}
                </span>
              </div>
              <div style="margin-bottom: 4px;">
                <strong>Time:</strong> ${marker.info?.time ? new Date(marker.info.time).toLocaleTimeString() : 'N/A'}
              </div>
              <div style="margin-bottom: 4px;">
                <strong>Duration:</strong> ${marker.info?.duration || 'N/A'}
              </div>
              <div>
                <strong>Outcome:</strong> 
                <span style="background: ${getOutcomeBg(marker.info?.outcome || 'unknown')}; padding: 2px 8px; border-radius: 4px; font-size: 12px;">
                  ${marker.info?.outcome?.replace('_', ' ') || 'Unknown'}
                </span>
              </div>
            </div>
          </div>
        `;

        leafletMarker.bindPopup(popupContent);
        markers.push(leafletMarker);
      });
    }

    // Add route path
    if (routeData.route && routeData.route.length > 1) {
      const routePath: [number, number][] = routeData.route.map((point: { lat: number; lng: number }): [number, number] => [point.lat, point.lng]);

      L.polyline(routePath as unknown as Array<[number, number]>, {
        color: '#2563eb',
        weight: 4,
        opacity: 0.8,
        dashArray: '5, 10'
      }).addTo(map);
    }

    // Fit map to markers
    if (markers.length > 0) {
      const group = (L as unknown as { featureGroup: (layers: object[]) => { getBounds: () => { pad: (n: number) => unknown } } }).featureGroup(markers);
      map.fitBounds(group.getBounds().pad(0.1));
    }

    return () => {
      map.remove();
    };
  }, [leafletLoaded, routeData]);

  const getMarkerColor = (type: string): string => {
    switch (type.toLowerCase()) {
      case 'hospital': return '#dc2626';
      case 'pharmacy': return '#2563eb';
      case 'clinic': return '#059669';
      default: return '#6b7280';
    }
  };

  // Removed unused getLocationIcon to satisfy lint rules

  const getOutcomeBg = (outcome: string): string => {
    switch (outcome.toLowerCase()) {
      case 'successful': return '#dcfce7; color: #15803d';
      case 'no_order': return '#fee2e2; color: #dc2626';
      case 'follow_up': return '#fef3c7; color: #d97706';
      default: return '#f3f4f6; color: #374151';
    }
  };

  return (
    <div className={`relative ${className}`}>
      {/* Map Container */}
      <div 
        ref={mapRef} 
        className="w-full h-full rounded-lg overflow-hidden shadow-lg bg-gray-100"
        style={{ minHeight: '400px' }}
      />

      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-lg">
          <div className="text-center">
            <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-3"></div>
            <p className="text-gray-600 font-medium">Loading route data...</p>
          </div>
        </div>
      )}

      {/* Error Overlay */}
      {error && (
        <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center rounded-lg">
          <div className="text-center p-6">
            <div className="text-red-500 text-4xl mb-3">⚠️</div>
            <h3 className="font-bold text-gray-900 mb-2">Unable to Load Map</h3>
            <p className="text-gray-600 text-sm mb-4">{error}</p>
            <button 
              onClick={() => window.location.reload()} 
              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Route Stats Overlay */}
      {routeData && !loading && (
        <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-4 min-w-64">
          <h3 className="font-bold text-gray-900 mb-3">Route Statistics</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Visits:</span>
              <span className="font-medium">{routeData.stats?.total_visits || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Distance:</span>
              <span className="font-medium">{routeData.stats?.total_distance || 0} km</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Efficiency:</span>
              <span className="font-medium text-green-600">{(routeData.stats?.efficiency || 0).toFixed(1)}%</span>
            </div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-3">
        <h4 className="font-medium text-gray-900 mb-2 text-sm">Visit Types</h4>
        <div className="space-y-1 text-xs">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-600 rounded-full"></div>
            <span>Hospital</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-blue-600 rounded-full"></div>
            <span>Pharmacy</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-600 rounded-full"></div>
            <span>Clinic</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-gray-600 rounded-full"></div>
            <span>General</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapContainer;
