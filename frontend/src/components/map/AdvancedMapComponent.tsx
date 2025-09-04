'use client'

import { useEffect, useRef, useState } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

interface RouteData {
  locations: Array<{
    lat: number
    lng: number
    timestamp: string
    visit_type: string
    location_name?: string
  }>
  total_distance: number
  total_visits: number
  route_efficiency: number
}

interface AdvancedMapProps {
  mrNumber: number
  date: string
  className?: string
}

// Custom marker icons
const createMarkerIcon = (color: string) => {
  return L.divIcon({
    html: `<div style="background-color: ${color}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 4px rgba(0,0,0,0.3);"></div>`,
    className: 'custom-marker',
    iconSize: [16, 16],
    iconAnchor: [8, 8]
  })
}

const markerColors = {
  start: '#22c55e',
  visit: '#3b82f6',
  break: '#f59e0b',
  end: '#ef4444'
}

export function AdvancedMapComponent({ mrNumber, date, className = '' }: AdvancedMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<L.Map | null>(null)
  const [routeData, setRouteData] = useState<RouteData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch route data
  useEffect(() => {
    const fetchRouteData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const response = await fetch(`http://localhost:8000/api/v2/route-blueprint?mr_number=${mrNumber}&date=${date}`)
        
        if (!response.ok) {
          throw new Error(`Failed to fetch route data: ${response.status}`)
        }
        
        const data = await response.json()
        setRouteData(data)
      } catch (err) {
        console.error('Error fetching route data:', err)
        setError(err instanceof Error ? err.message : 'Failed to load route data')
      } finally {
        setLoading(false)
      }
    }

    if (mrNumber && date) {
      fetchRouteData()
    }
  }, [mrNumber, date])

  // Initialize map
  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return

    const map = L.map(mapRef.current, {
      center: [28.6139, 77.2090], // Default to Delhi
      zoom: 10,
      zoomControl: false,
      attributionControl: false
    })

    // Add custom zoom control
    L.control.zoom({
      position: 'bottomright'
    }).addTo(map)

    // Add tile layer with modern styling
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map)

    mapInstanceRef.current = map

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [])

  // Update map with route data
  useEffect(() => {
    if (!mapInstanceRef.current || !routeData?.locations?.length) return

    const map = mapInstanceRef.current
    
    // Clear existing layers
    map.eachLayer((layer) => {
      if (layer instanceof L.Marker || layer instanceof L.Polyline) {
        map.removeLayer(layer)
      }
    })

    const locations = routeData.locations
    const latLngs: L.LatLng[] = []

    // Add markers for each location
    locations.forEach((location, index) => {
      const latLng = L.latLng(location.lat, location.lng)
      latLngs.push(latLng)

      // Determine marker type
      let markerType: keyof typeof markerColors = 'visit'
      if (index === 0) markerType = 'start'
      else if (index === locations.length - 1) markerType = 'end'
      else if (location.visit_type === 'break') markerType = 'break'

      const marker = L.marker(latLng, {
        icon: createMarkerIcon(markerColors[markerType])
      }).addTo(map)

      // Add popup with visit details
      const popupContent = `
        <div class="p-2 min-w-[200px]">
          <div class="font-semibold text-gray-800 mb-1">
            ${markerType === 'start' ? '🚗 Route Start' : 
              markerType === 'end' ? '🏁 Route End' :
              markerType === 'break' ? '☕ Break' : '🏥 Visit'}
          </div>
          <div class="text-sm text-gray-600 mb-1">
            <strong>Time:</strong> ${new Date(location.timestamp).toLocaleTimeString()}
          </div>
          ${location.location_name ? `
            <div class="text-sm text-gray-600 mb-1">
              <strong>Location:</strong> ${location.location_name}
            </div>
          ` : ''}
          <div class="text-xs text-gray-500">
            ${location.lat.toFixed(6)}, ${location.lng.toFixed(6)}
          </div>
        </div>
      `
      
      marker.bindPopup(popupContent)
    })

    // Draw route line
    if (latLngs.length > 1) {
      const polyline = L.polyline(latLngs, {
        color: '#3b82f6',
        weight: 4,
        opacity: 0.8,
        smoothFactor: 1
      }).addTo(map)

      // Fit map to route bounds with padding
      const group = L.featureGroup([polyline])
      map.fitBounds(group.getBounds().pad(0.1))
    } else if (latLngs.length === 1) {
      // Single location - center on it
      map.setView(latLngs[0], 14)
    }
  }, [routeData])

  if (loading) {
    return (
      <div className={`bg-white rounded-xl shadow-lg ${className}`}>
        <div className="p-6">
          <div className="flex items-center justify-center h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading route data...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`bg-white rounded-xl shadow-lg ${className}`}>
        <div className="p-6">
          <div className="flex items-center justify-center h-[400px]">
            <div className="text-center">
              <div className="text-red-500 mb-2">⚠️</div>
              <p className="text-gray-600">Error loading route data</p>
              <p className="text-sm text-gray-500 mt-1">{error}</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-xl shadow-lg overflow-hidden ${className}`}>
      {/* Map Header */}
      <div className="p-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white">
        <h3 className="font-semibold text-lg">Route Blueprint</h3>
        <p className="text-blue-100 text-sm">
          MR {mrNumber} • {new Date(date).toLocaleDateString()}
        </p>
      </div>

      {/* Route Stats */}
      {routeData && (
        <div className="p-4 bg-gray-50 border-b">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">{routeData.total_visits}</div>
              <div className="text-xs text-gray-600">Total Visits</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {routeData.total_distance.toFixed(1)}km
              </div>
              <div className="text-xs text-gray-600">Distance</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-600">
                {(routeData.route_efficiency * 100).toFixed(0)}%
              </div>
              <div className="text-xs text-gray-600">Efficiency</div>
            </div>
          </div>
        </div>
      )}

      {/* Map Container */}
      <div className="relative">
        <div ref={mapRef} className="h-[400px] w-full" />
        
        {/* Legend */}
        <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-3 text-xs">
          <div className="font-semibold text-gray-800 mb-2">Legend</div>
          <div className="space-y-1">
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: markerColors.start }}></div>
              <span>Start</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: markerColors.visit }}></div>
              <span>Visit</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: markerColors.break }}></div>
              <span>Break</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: markerColors.end }}></div>
              <span>End</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
