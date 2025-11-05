import { useEffect, useRef, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RoutePoint } from "@/types";
import { cn } from "@/lib/utils";
import { Loader } from "@googlemaps/js-api-loader";
import { 
  ZoomIn, 
  ZoomOut, 
  Maximize2, 
  MapPin, 
  Navigation,
  Layers,
  Info,
  Loader2
} from "lucide-react";

interface GoogleMapProps {
  mrId?: string | null;
  date: string;
  live?: boolean;
  markers?: RoutePoint[];
  className?: string;
}

export function GoogleMap({ 
  mrId, 
  date, 
  live = false, 
  markers = [], 
  className 
}: GoogleMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const googleMapRef = useRef<google.maps.Map | null>(null);
  const markersRef = useRef<google.maps.Marker[]>([]);
  const polylineRef = useRef<google.maps.Polyline | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [mapError, setMapError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize Google Maps
  useEffect(() => {
    const initMap = async () => {
      if (!mapRef.current) return;

      try {
        setIsLoading(true);
        const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
        
        if (!apiKey) {
          throw new Error('Google Maps API key not found');
        }

        const loader = new Loader({
          apiKey,
          version: "weekly",
          libraries: ["marker", "geometry"]
        });

        const { Map } = await loader.importLibrary("maps");
        
        // Default center (Delhi, India)
        const defaultCenter = { lat: 28.6139, lng: 77.2090 };
        
        const mapOptions: google.maps.MapOptions = {
          center: defaultCenter,
          zoom: 12,
          mapTypeId: google.maps.MapTypeId.ROADMAP,
          styles: [
            {
              featureType: "poi",
              elementType: "labels",
              stylers: [{ visibility: "off" }]
            },
            {
              featureType: "transit",
              elementType: "labels",
              stylers: [{ visibility: "off" }]
            }
          ],
          zoomControl: false,
          mapTypeControl: false,
          scaleControl: true,
          streetViewControl: false,
          rotateControl: false,
          fullscreenControl: false
        };

        googleMapRef.current = new Map(mapRef.current, mapOptions);
        setMapLoaded(true);
        setIsLoading(false);
        console.log('Google Maps initialized successfully for MR:', mrId);
        
      } catch (error) {
        console.error('Error loading Google Maps:', error);
        setMapError(error instanceof Error ? error.message : 'Failed to load Google Maps');
        setIsLoading(false);
      }
    };

    initMap();
  }, [mrId]);

  // Filter out markers with invalid coordinates
  const validMarkers = markers.filter(marker =>
    marker.latitude !== 0 &&
    marker.longitude !== 0 &&
    marker.latitude >= -90 && marker.latitude <= 90 &&
    marker.longitude >= -180 && marker.longitude <= 180
  );

  // Update markers and route when markers prop changes
  useEffect(() => {
    if (!googleMapRef.current || !mapLoaded || isLoading) return;

    // Clear existing markers and polyline
    markersRef.current.forEach(marker => marker.setMap(null));
    markersRef.current = [];

    if (polylineRef.current) {
      polylineRef.current.setMap(null);
      polylineRef.current = null;
    }

    if (validMarkers.length === 0) {
      console.log('No valid markers to display on map');
      return;
    }

    // Create path for route line
    const path: google.maps.LatLng[] = [];

    // Add new markers
    validMarkers.forEach((point, index) => {
      const position = { lat: point.latitude, lng: point.longitude };
      path.push(new google.maps.LatLng(position.lat, position.lng));

      const marker = new google.maps.Marker({
        position,
        map: googleMapRef.current,
        title: point.location_name || `Point ${index + 1}`,
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          scale: point.type === 'current' ? 12 : 8,
          fillColor: getMarkerColor(point.type),
          fillOpacity: 0.9,
          strokeColor: '#ffffff',
          strokeWeight: 2,
        },
        zIndex: point.type === 'current' ? 1000 : 100
      });

      // Add info window
      const infoWindow = new google.maps.InfoWindow({
        content: `
          <div class="p-3 min-w-[200px]">
            <h3 class="font-semibold text-lg mb-2">${point.location_name || 'Location'}</h3>
            <div class="space-y-1 text-sm">
              <p><span class="font-medium">Type:</span> ${point.type}</p>
              <p><span class="font-medium">Time:</span> ${new Date(point.timestamp).toLocaleString()}</p>
              ${point.visit_type ? `<p><span class="font-medium">Visit:</span> ${point.visit_type}</p>` : ''}
              ${point.duration ? `<p><span class="font-medium">Duration:</span> ${point.duration} min</p>` : ''}
              ${point.outcome ? `<p><span class="font-medium">Outcome:</span> ${point.outcome}</p>` : ''}
            </div>
          </div>
        `
      });

      marker.addListener('click', () => {
        infoWindow.open(googleMapRef.current, marker);
      });

      markersRef.current.push(marker);
    });

    // Draw route line if we have multiple points
    if (path.length > 1) {
      polylineRef.current = new google.maps.Polyline({
        path,
        geodesic: true,
        strokeColor: '#3B82F6',
        strokeOpacity: 0.8,
        strokeWeight: 3,
        map: googleMapRef.current
      });
    }

    // Fit map to show all markers
    if (validMarkers.length > 0) {
      const bounds = new google.maps.LatLngBounds();
      validMarkers.forEach(point => {
        bounds.extend({ lat: point.latitude, lng: point.longitude });
      });

      googleMapRef.current.fitBounds(bounds);

      // Don't zoom in too much for single markers
      google.maps.event.addListenerOnce(googleMapRef.current, 'bounds_changed', () => {
        if (validMarkers.length === 1 && googleMapRef.current) {
          const zoom = googleMapRef.current.getZoom();
          if (zoom && zoom > 15) {
            googleMapRef.current.setZoom(15);
          }
        }
      });
    }
  }, [markers, mapLoaded, isLoading]);

  const getMarkerColor = (type: string) => {
    switch (type) {
      case 'visit': return '#3B82F6'; // Blue
      case 'current': return '#EF4444'; // Red
      case 'travel': return '#10B981'; // Green
      default: return '#6B7280'; // Gray
    }
  };

  const handleZoomIn = () => {
    if (googleMapRef.current) {
      const currentZoom = googleMapRef.current.getZoom() || 12;
      googleMapRef.current.setZoom(Math.min(currentZoom + 1, 20));
    }
  };

  const handleZoomOut = () => {
    if (googleMapRef.current) {
      const currentZoom = googleMapRef.current.getZoom() || 12;
      googleMapRef.current.setZoom(Math.max(currentZoom - 1, 1));
    }
  };

  const handleFitBounds = () => {
    if (googleMapRef.current && markers.length > 0) {
      const bounds = new google.maps.LatLngBounds();
      markers.forEach(point => {
        if (point.latitude !== 0 && point.longitude !== 0) {
          bounds.extend({ lat: point.latitude, lng: point.longitude });
        }
      });
      googleMapRef.current.fitBounds(bounds);
    }
  };

  if (mapError) {
    return (
      <Card className={cn("h-96", className)}>
        <CardContent className="p-6 flex items-center justify-center h-full">
          <div className="text-center">
            <MapPin className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-lg font-medium text-muted-foreground mb-2">Map Error</p>
            <p className="text-sm text-muted-foreground">{mapError}</p>
            <p className="text-xs text-muted-foreground mt-2">
              Please check your Google Maps API configuration
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("relative overflow-hidden", className)}>
      <CardContent className="p-0 relative">
        {/* Loading overlay */}
        {isLoading && (
          <div className="absolute inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
            <div className="flex items-center gap-2">
              <Loader2 className="h-6 w-6 animate-spin" />
              <span className="text-sm font-medium">Loading map...</span>
            </div>
          </div>
        )}

        {/* Map container */}
        <div ref={mapRef} className="w-full h-96" />

        {/* Map controls */}
        {mapLoaded && (
          <div className="absolute top-4 right-4 flex flex-col gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={handleZoomIn}
              className="bg-background/90 backdrop-blur-sm"
            >
              <ZoomIn className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={handleZoomOut}
              className="bg-background/90 backdrop-blur-sm"
            >
              <ZoomOut className="h-4 w-4" />
            </Button>
            {validMarkers.length > 1 && (
              <Button
                size="sm"
                variant="outline"
                onClick={handleFitBounds}
                className="bg-background/90 backdrop-blur-sm"
                title="Fit all markers"
              >
                <Maximize2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        )}

        {/* Map info */}
        {mapLoaded && (
          <div className="absolute bottom-4 left-4 flex gap-2">
            {live && (
              <Badge variant="default" className="bg-green-500">
                <div className="w-2 h-2 bg-white rounded-full mr-1 animate-pulse" />
                Live
              </Badge>
            )}
            {validMarkers.length > 0 && (
              <Badge variant="outline" className="bg-background/90 backdrop-blur-sm">
                {validMarkers.length} point{validMarkers.length !== 1 ? 's' : ''}
              </Badge>
            )}
            {mrId && (
              <Badge variant="outline" className="bg-background/90 backdrop-blur-sm">
                MR {mrId}
              </Badge>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Export as MapContainer for compatibility
export { GoogleMap as MapContainer };
