import useSWR from 'swr'
import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || 'mr-tracking-2025'

const fetcher = async (url: string) => {
  const response = await axios.get(url, {
    headers: {
      'X-API-Key': API_KEY
    }
  })
  return response.data
}

export interface RoutePoint {
  time: string
  lat: number
  lng: number
  type: 'start' | 'movement' | 'visit' | 'expense' | 'current'
  location: string
  details: string
  timestamp: string
}

export interface RouteStats {
  distance_km: number
  visits: number
  expenses_total: number
  active_hours: number
  total_points: number
  first_location?: string
  last_location?: string
}

export interface RouteData {
  success: boolean
  mr_id: number
  date: string
  points: RoutePoint[]
  stats: RouteStats
  generated_at: string
}

export function useRouteData(mrId: number | null, date: string) {
  const shouldFetch = mrId !== null && date !== ''
  
  const { data, error, isLoading, mutate } = useSWR<RouteData>(
    shouldFetch ? `${API_BASE}/api/route?mr_id=${mrId}&date=${date}` : null,
    fetcher,
    {
      refreshInterval: 30000, // Refresh every 30 seconds
      revalidateOnFocus: true,
      errorRetryCount: 3
    }
  )

  return {
    routeData: data?.points || [],
    stats: data?.stats || null,
    loading: isLoading,
    error,
    refetch: mutate
  }
}

export function useMRList() {
  const { data, error, isLoading } = useSWR(
    `${API_BASE}/api/mrs`,
    fetcher
  )

  return {
    mrs: data?.mrs || [],
    loading: isLoading,
    error
  }
}

export function useLiveLocation(mrId: number | null) {
  const { data, error, isLoading } = useSWR(
    mrId ? `${API_BASE}/api/live?mr_id=${mrId}` : null,
    fetcher,
    {
      refreshInterval: 15000 // Refresh every 15 seconds for live data
    }
  )

  return {
    liveData: data,
    loading: isLoading,
    error
  }
}
