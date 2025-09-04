'use client'

import { useEffect, useRef } from 'react'
import { Loader } from '@googlemaps/js-api-loader'
import { RoutePoint } from '@/hooks/useRouteData'
import { MapPin, Loader2 } from 'lucide-react'

interface MapViewProps {
  routeData: RoutePoint[]
  selectedMR: number | null
  loading: boolean
  error?: unknown
}

export function MapView({ routeData, selectedMR, loading, error }: MapViewProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<google.maps.Map | null>(null)
  const markersRef = useRef<google.maps.Marker[]>([])
  const pathRef = useRef<google.maps.Polyline | null>(null)

  useEffect(() => {
    const initMap = async () => {
      const loader = new Loader({
        apiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
        version: 'weekly',
        libraries: ['geometry']
      })

      try {
        await loader.load()
        
        if (mapRef.current && !mapInstanceRef.current) {
          mapInstanceRef.current = new google.maps.Map(mapRef.current, {
            zoom: 12,
            center: { lat: 19.0760, lng: 72.8777 }, // Mumbai default
            styles: [
              {
                featureType: 'poi',
                elementType: 'labels',
                stylers: [{ visibility: 'off' }]
              }
            ]
          })
        }
      } catch (error) {
        console.error('Error loading Google Maps:', error)
      }
    }

    initMap()
  }, [])

  useEffect(() => {
    if (!mapInstanceRef.current || !routeData.length) return

    // Clear existing markers and path
    markersRef.current.forEach(marker => marker.setMap(null))
    markersRef.current = []
    if (pathRef.current) {
      pathRef.current.setMap(null)
    }

    const bounds = new google.maps.LatLngBounds()
    const pathCoords: google.maps.LatLngLiteral[] = []

    // Create markers and collect path coordinates
    routeData.forEach((point) => {
      const position = { lat: point.lat, lng: point.lng }
      pathCoords.push(position)
      bounds.extend(position)

      // Determine marker color based on type
      let markerColor = '#007bff'

      switch (point.type) {
        case 'start':
          markerColor = '#28a745'
          break
        case 'visit':
          markerColor = '#6f42c1'
          break
        case 'expense':
          markerColor = '#dc3545'
          break
        case 'current':
          markerColor = '#ffc107'
          break
        default:
          markerColor = '#007bff'
      }

      const marker = new google.maps.Marker({
        position,
        map: mapInstanceRef.current,
        title: `${point.time} - ${point.location}`,
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          fillColor: markerColor,
          fillOpacity: 1,
          strokeColor: 'white',
          strokeWeight: 2,
          scale: point.type === 'current' ? 10 : 8
        }
      })

      // Info window
      const infoWindow = new google.maps.InfoWindow({
        content: `
          <div style="padding: 8px;">
            <h4 style="margin: 0 0 4px 0; color: #333;">${point.location}</h4>
            <p style="margin: 0; color: #666; font-size: 14px;"><strong>Time:</strong> ${point.time}</p>
            <p style="margin: 2px 0 0 0; color: #666; font-size: 14px;">${point.details}</p>
            <p style="margin: 2px 0 0 0; color: #999; font-size: 12px;">
              ${point.lat.toFixed(6)}, ${point.lng.toFixed(6)}
            </p>
          </div>
        `
      })

      marker.addListener('click', () => {
        infoWindow.open(mapInstanceRef.current, marker)
      })

      markersRef.current.push(marker)
    })

    // Draw path
    if (pathCoords.length > 1) {
      pathRef.current = new google.maps.Polyline({
        path: pathCoords,
        geodesic: true,
        strokeColor: '#007bff',
        strokeOpacity: 0.8,
        strokeWeight: 4
      })
      pathRef.current.setMap(mapInstanceRef.current)
    }

    // Fit map to show all points
    if (!bounds.isEmpty()) {
      mapInstanceRef.current.fitBounds(bounds)
    }
  }, [routeData])

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading route data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <MapPin className="h-12 w-12 text-red-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Failed to load map</h3>
          <p className="text-gray-600 mb-4">Unable to fetch route data</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (!selectedMR) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Select an MR</h3>
          <p className="text-gray-600">Choose an MR from the dropdown to view their route</p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative h-full">
      <div ref={mapRef} className="w-full h-full" />
      
      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white p-3 rounded-lg shadow-lg">
        <h4 className="font-semibold text-sm mb-2">Legend</h4>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span>Start Location</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-purple-600 rounded-full"></div>
            <span>Visit</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span>Movement</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span>Expense</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span>Current Position</span>
          </div>
        </div>
      </div>
      
      {/* Route info */}
      {routeData.length > 0 && (
        <div className="absolute top-4 right-4 bg-white p-3 rounded-lg shadow-lg">
          <div className="text-sm text-gray-600">
            <span className="font-semibold text-green-600">{routeData.length}</span> locations tracked
          </div>
        </div>
      )}
    </div>
  )
}
