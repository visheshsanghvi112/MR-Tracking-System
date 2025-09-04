'use client'

import { RoutePoint } from '@/hooks/useRouteData'
import { Clock, MapPin, DollarSign, Navigation } from 'lucide-react'

interface TimelineProps {
  routeData: RoutePoint[]
  loading: boolean
}

export function Timeline({ routeData, loading }: TimelineProps) {
  if (loading) {
    return (
      <div className="p-4">
        <h3 className="text-lg font-semibold mb-4">Activity Timeline</h3>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex gap-3 animate-pulse">
              <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-3/4"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!routeData.length) {
    return (
      <div className="p-4 text-center text-gray-500">
        <Clock className="h-12 w-12 mx-auto mb-4 text-gray-300" />
        <p>No activity data available</p>
      </div>
    )
  }

  const getIcon = (type: string) => {
    switch (type) {
      case 'start':
        return <Navigation className="h-5 w-5 text-green-600" />
      case 'visit':
        return <MapPin className="h-5 w-5 text-purple-600" />
      case 'expense':
        return <DollarSign className="h-5 w-5 text-red-600" />
      case 'current':
        return <div className="w-5 h-5 bg-yellow-400 rounded-full animate-pulse" />
      default:
        return <div className="w-5 h-5 bg-blue-400 rounded-full" />
    }
  }

  const getBackgroundColor = (type: string) => {
    switch (type) {
      case 'start':
        return 'bg-green-50 border-green-200'
      case 'visit':
        return 'bg-purple-50 border-purple-200'
      case 'expense':
        return 'bg-red-50 border-red-200'
      case 'current':
        return 'bg-yellow-50 border-yellow-200'
      default:
        return 'bg-blue-50 border-blue-200'
    }
  }

  // Sort by time (most recent first)
  const sortedData = [...routeData].reverse()

  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold mb-4">Activity Timeline</h3>
      
      <div className="space-y-3">
        {sortedData.map((point, index) => (
          <div
            key={`${point.timestamp}-${index}`}
            className={`p-3 rounded-lg border ${getBackgroundColor(point.type)} transition-all hover:shadow-md`}
          >
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 p-2 rounded-full bg-white">
                {getIcon(point.type)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium text-gray-900">
                    {point.time}
                  </span>
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full
                    ${point.type === 'start' ? 'bg-green-100 text-green-800' :
                      point.type === 'visit' ? 'bg-purple-100 text-purple-800' :
                      point.type === 'expense' ? 'bg-red-100 text-red-800' :
                      point.type === 'current' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}
                  >
                    {point.type.charAt(0).toUpperCase() + point.type.slice(1)}
                  </span>
                </div>
                
                <h4 className="text-sm font-semibold text-gray-900 mb-1">
                  {point.location}
                </h4>
                
                <p className="text-sm text-gray-600 mb-2">
                  {point.details}
                </p>
                
                <div className="text-xs text-gray-500">
                  📍 {point.lat.toFixed(4)}, {point.lng.toFixed(4)}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {sortedData.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <Clock className="h-8 w-8 mx-auto mb-2 text-gray-300" />
          <p>No timeline data available</p>
        </div>
      )}
    </div>
  )
}
