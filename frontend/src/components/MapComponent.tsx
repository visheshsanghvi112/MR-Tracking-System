'use client'

import { motion } from 'framer-motion'
import { Globe } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { useRouteData } from '@/hooks/useRouteData'

interface MapComponentProps {
  selectedMR: number
  selectedDate: string
}

export function MapComponent({ selectedMR, selectedDate }: MapComponentProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const [map, setMap] = useState<google.maps.Map | null>(null)
  const { routeData, loading, error } = useRouteData(selectedMR, selectedDate)

  useEffect(() => {
    if (mapRef.current && !map) {
      // Initialize Google Maps
      const initMap = async () => {
        const { Loader } = await import('@googlemaps/js-api-loader')
        const loader = new Loader({
          apiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
          version: 'weekly',
          libraries: ['geometry']
        })

        const google = await loader.load()
        const mapInstance = new google.maps.Map(mapRef.current!, {
          center: { lat: 23.0225, lng: 72.5714 }, // Ahmedabad
          zoom: 12,
          styles: [
            {
              featureType: "all",
              elementType: "geometry.fill",
              stylers: [{ color: "#1a1a2e" }]
            },
            {
              featureType: "water",
              elementType: "geometry",
              stylers: [{ color: "#16213e" }]
            }
          ]
        })
        setMap(mapInstance)
      }
      
      initMap()
    }
  }, [map])

  // Update map with route data
  useEffect(() => {
    if (map && routeData && routeData.length > 0) {
      // Clear existing markers
      // Add route visualization here
      console.log('Route data:', routeData)
    }
  }, [map, routeData])

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, delay: 0.8 }}
      className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl overflow-hidden shadow-2xl"
    >
      {/* Map Header */}
      <div className="bg-gradient-to-r from-blue-500/20 to-purple-600/20 px-6 py-4 border-b border-white/10">
        <div className="flex items-center justify-between">
          <h2 className="text-white text-xl font-semibold flex items-center">
            <Globe className="w-5 h-5 mr-2" />
            Live Route Tracking
          </h2>
          <div className="flex items-center text-green-400">
            <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse" />
            <span className="text-sm font-medium">Real-time</span>
          </div>
        </div>
      </div>

      {/* Map Container */}
      <div className="relative">
        <div ref={mapRef} className="w-full h-96" />
        
        {/* Loading Overlay */}
        {loading && (
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 text-white text-center">
              <div className="animate-spin w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full mx-auto mb-3" />
              <p>Loading route data...</p>
            </div>
          </div>
        )}

        {/* Error Overlay */}
        {error && (
          <div className="absolute inset-0 bg-red-500/20 flex items-center justify-center">
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 text-white text-center">
              <p className="text-red-300">Failed to load map data</p>
            </div>
          </div>
        )}

        {/* Route Info */}
        {routeData && (
          <div className="absolute top-4 left-4 bg-white/10 backdrop-blur-md rounded-xl p-4 text-white">
            <p className="text-sm font-medium">{routeData.length} locations tracked</p>
          </div>
        )}
      </div>
    </motion.div>
  )
}
