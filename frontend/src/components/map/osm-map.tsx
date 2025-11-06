import { useEffect, useRef, useState, useMemo } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RoutePoint } from "@/types";
import { cn } from "@/lib/utils";
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
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

// ENHANCED: Custom marker icons - cleaner with start/end labels
const createCustomIcon = (
  type: 'visit' | 'travel' | 'current',
  index?: number,
  opts?: { isFirst?: boolean; isLast?: boolean }
) => {
  // Google Maps familiar colors
  const colors = {
    visit: '#1A73E8',    // Blue
    current: '#EA4335',  // Red
    travel: '#34A853',   // Green
  } as const;
  
  // ENHANCED: Larger sizes for better visibility
  const size = type === 'current' ? 30 : type === 'visit' ? 22 : 14;
  const showNumber = type === 'visit' && index !== undefined;
  const numberText = showNumber ? String((index || 0) + 1) : '';
  const showSEBadge = type === 'visit' && (opts?.isFirst || opts?.isLast);
  
  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div style="
        width: ${size}px;
        height: ${size}px;
        background: radial-gradient(circle, ${colors[type]}, ${colors[type]}dd);
        border: 3px solid white;
        border-radius: 50%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4), 0 0 0 1px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: ${type === 'visit' ? '12px' : '10px'};
        font-weight: 900;
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
        ${type === 'current' ? 'animation: pulse 2s infinite;' : ''}
        position: relative;
        z-index: ${type === 'current' ? 1000 : type === 'visit' ? 500 : 100};
      " onmouseover="this.style.transform='scale(1.2)'" 
         onmouseout="this.style.transform='scale(1)'"
      >${numberText}</div>
      ${showSEBadge ? `
        <div style="
          position: absolute;
          top: -6px;
          left: -6px;
          background: ${opts?.isFirst ? '#1557B0' : '#C0352A'};
          color: white;
          font-size: 10px;
          font-weight: 900;
          border-radius: 6px;
          padding: 1px 3px;
          border: 2px solid white;
          box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        ">
          ${opts?.isFirst ? 'S' : 'E'}
        </div>
      ` : ''}
      ${type === 'current' ? `
        <div style="
          width: ${size + 8}px;
          height: ${size + 8}px;
          border: 3px solid ${colors[type]};
          border-radius: 50%;
          position: absolute;
          top: -6px;
          left: -6px;
          opacity: 0.6;
          animation: ping 2s ease-out infinite;
        "></div>
      ` : ''}
      ${type === 'visit' ? `
        <div style="
          width: ${size + 4}px;
          height: ${size + 4}px;
          border: 2px solid ${colors[type]}40;
          border-radius: 50%;
          position: absolute;
          top: -4px;
          left: -4px;
          opacity: 0.3;
        "></div>
      ` : ''}
    `,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2 - 5],
  });
};

interface OSMMapProps {
  mrId?: string | null;
  date: string;
  live?: boolean;
  markers?: RoutePoint[];
  className?: string;
  centerOn?: { lat: number; lng: number; zoom?: number } | null;
  mrName?: string; // ENHANCED: Show MR name on map
}

// Custom component to handle map updates
function MapUpdater({ markers }: { markers: RoutePoint[] }) {
  const map = useMap();
  const hasInitialized = useRef(false);
  const previousMarkerCount = useRef(0);

  useEffect(() => {
    // Only fit bounds if:
    // 1. This is the first load, OR
    // 2. The number of markers has changed significantly
    const markerCountChanged = markers.length !== previousMarkerCount.current;
    
    if (markers.length > 0 && (!hasInitialized.current || markerCountChanged)) {
      const bounds = L.latLngBounds(markers.map(m => [m.latitude, m.longitude]));
      map.fitBounds(bounds, { 
        padding: [50, 50],
        animate: !hasInitialized.current, // Only animate on first load
        duration: 0.5 // Short animation
      });
      
      hasInitialized.current = true;
      previousMarkerCount.current = markers.length;
    }
  }, [markers.length, map]); // Only depend on markers.length, not the whole array

  return null;
}

// NEW: Custom component to handle centering map on specific location
function MapCentre({ centerOn }: { centerOn: { lat: number; lng: number; zoom?: number } | null }) {
  const map = useMap();

  useEffect(() => {
    if (centerOn) {
      console.log(`🎯 Centering map on: ${centerOn.lat}, ${centerOn.lng}`);
      map.flyTo(  // ENHANCED: Use flyTo for smoother animation
        [centerOn.lat, centerOn.lng],
        centerOn.zoom || 16,
        { animate: true, duration: 1.5, easeLinearity: 0.25 }
      );
    }
  }, [centerOn, map]);

  return null;
}

// ENHANCED: Smooth follow when MR changes
function MRFollower({ markers, mrId }: { markers: RoutePoint[]; mrId?: string | null }) {
  const map = useMap();
  const previousMRRef = useRef<string | null>(null);

  useEffect(() => {
    // When MR changes, smoothly fly to their route
    if (mrId && mrId !== previousMRRef.current && markers.length > 0) {
      console.log(`✈️ Flying to MR ${mrId}'s route`);
      const bounds = L.latLngBounds(markers.map(m => [m.latitude, m.longitude]));
      map.flyToBounds(bounds, {
        padding: [80, 80],
        duration: 1.5,
        easeLinearity: 0.25,
        maxZoom: 15
      });
      previousMRRef.current = mrId;
    }
  }, [mrId, markers, map]);

  return null;
}

// Enhanced popup styles with higher specificity - MOVED TO TOP!
const enhancedPopupStyles = `
  .enhanced-popup .leaflet-popup-content-wrapper {
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(20px) !important;
    border-radius: 16px !important;
    box-shadow: 
      0 25px 50px -12px rgba(0, 0, 0, 0.15),
      0 0 0 1px rgba(255, 255, 255, 0.2),
      inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    padding: 0 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    overflow: visible !important;
  }
  
  .enhanced-popup .leaflet-popup-content {
    margin: 0 !important;
    padding: 0 !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
    border-radius: 16px !important;
    overflow: hidden !important;
    max-width: none !important;
    width: auto !important;
  }
  
  .enhanced-popup .leaflet-popup-tip {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(248, 250, 252, 0.95)) !important;
    border: none !important;
    box-shadow: 
      0 8px 25px rgba(0,0,0,0.1),
      0 0 0 1px rgba(255, 255, 255, 0.2) !important;
    backdrop-filter: blur(10px) !important;
  }
  
  .enhanced-popup .leaflet-popup-close-button {
    background: rgba(0, 0, 0, 0.05) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 50% !important;
    width: 24px !important;
    height: 24px !important;
    margin: 8px !important;
    text-align: center !important;
    line-height: 24px !important;
    color: rgba(0, 0, 0, 0.6) !important;
    font-weight: bold !important;
    transition: all 0.2s ease !important;
  }
  
  .enhanced-popup .leaflet-popup-close-button:hover {
    background: rgba(239, 68, 68, 0.1) !important;
    color: rgb(239, 68, 68) !important;
    transform: scale(1.1) !important;
  }
`;

// Immediately inject styles when module loads
if (typeof document !== 'undefined') {
  const styleId = 'enhanced-popup-styles-immediate';
  if (!document.getElementById(styleId)) {
    const styleElement = document.createElement('style');
    styleElement.id = styleId;
    styleElement.textContent = enhancedPopupStyles;
    document.head.appendChild(styleElement);
    console.log('🚀 Enhanced popup styles injected IMMEDIATELY!');
  }
}

export function OSMMap({ 
  mrId, 
  date, 
  live = false, 
  markers = [], 
  className,
  centerOn = null,
  mrName
}: OSMMapProps) {
  
  // Inject enhanced popup styles on component mount
  useEffect(() => {
    const styleId = 'enhanced-popup-styles';
    
    // Remove old styles first
    const existingStyle = document.getElementById(styleId);
    if (existingStyle) {
      existingStyle.remove();
    }
    
    // Inject new styles
    const styleElement = document.createElement('style');
    styleElement.id = styleId;
    styleElement.textContent = enhancedPopupStyles;
    document.head.appendChild(styleElement);
    console.log('🎨 Enhanced popup styles injected!', styleElement);
    
    // Also log the popup styles to verify content
    console.log('📝 Popup styles content:', enhancedPopupStyles.substring(0, 200) + '...');
    
  }, []);
  const mapRef = useRef<L.Map | null>(null);
  const [zoom, setZoom] = useState(12);
  const [mapError, setMapError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Debug logging
  useEffect(() => {
    console.log('🗺️ OSMMap Component Loaded');
    console.log(`  MR ID: ${mrId}, Date: ${date}, Live: ${live}`);
    console.log(`  Markers count: ${markers.length}`);
    if (markers.length > 0) {
      console.log(`  First marker:`, markers[0]);
      console.log(`  Last marker:`, markers[markers.length - 1]);
    }
  }, [mrId, date, live, markers]);

  // Default center (Mumbai, India - more relevant for this app)
  const defaultCenter: [number, number] = [19.0760, 72.8777];
  
  // Filter valid markers - memoized to prevent unnecessary re-renders
  const validMarkers = useMemo(() => markers.filter(m => 
    m.latitude !== 0 && 
    m.longitude !== 0 &&
    !isNaN(m.latitude) && 
    !isNaN(m.longitude)
  ), [markers]);
  
  const center = useMemo(() => 
    validMarkers.length > 0 
      ? [validMarkers[0].latitude, validMarkers[0].longitude] as [number, number]
      : defaultCenter
  , [validMarkers]);

  // Create path from markers for polyline - memoized
  const path = useMemo(() => 
    validMarkers.map(m => [m.latitude, m.longitude] as [number, number])
  , [validMarkers]);

  // Use dotted line for historical (blueprint-style) dates
  const isHistorical = useMemo(() => {
    try {
      const today = new Date();
      const y = today.getFullYear();
      const m = String(today.getMonth() + 1).padStart(2, '0');
      const d = String(today.getDate()).padStart(2, '0');
      const todayStr = `${y}-${m}-${d}`;
      return date !== todayStr;
    } catch {
      return false;
    }
  }, [date]);

  // Pre-computed counts for UI
  const visitCount = useMemo(() => validMarkers.filter(m => m.type === 'visit').length, [validMarkers]);
  const travelCount = useMemo(() => validMarkers.filter(m => m.type === 'travel').length, [validMarkers]);
  const liveCount = useMemo(() => validMarkers.filter(m => m.type === 'current').length, [validMarkers]);

  useEffect(() => {
    // Map is loaded when component mounts
    setIsLoading(false);
    console.log(`✅ Map loaded with ${validMarkers.length} valid markers`);
  }, [validMarkers.length]);

  const handleZoomIn = () => {
    if (mapRef.current) {
      mapRef.current.zoomIn();
    }
  };

  const handleZoomOut = () => {
    if (mapRef.current) {
      mapRef.current.zoomOut();
    }
  };

  const handleFullscreen = () => {
    const mapContainer = document.querySelector('.leaflet-container');
    if (mapContainer) {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        mapContainer.requestFullscreen();
      }
    }
  };

  if (mapError) {
    return (
      <Card className={cn("w-full h-[600px]", className)}>
        <CardContent className="flex items-center justify-center h-full">
          <div className="text-center space-y-4">
            <div className="text-red-500 text-lg font-semibold">
              Failed to load map
            </div>
            <p className="text-muted-foreground">{mapError}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("w-full h-[600px] relative overflow-hidden", className)}>
      <CardContent className="p-0 h-full relative">
        {/* ENHANCED: MR Info Panel - Larger and More Informative */}
        {/* No Data Message */}
        {mrId && validMarkers.length === 0 && !isLoading && (
          <div className="absolute inset-0 z-[1000] flex items-center justify-center pointer-events-none p-4">
            <Card className="bg-background/95 backdrop-blur-md border-2 border-orange-300/50 shadow-2xl pointer-events-auto max-w-sm w-full">
              <CardContent className="p-4 sm:p-6 text-center">
                <div className="text-3xl sm:text-4xl mb-3 sm:mb-4">📭</div>
                <h3 className="text-base sm:text-lg font-bold mb-2 text-orange-600">No Data Available</h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-1">
                  No location data found for <strong>{mrName || `MR ${mrId}`}</strong>
                </p>
                <p className="text-[10px] sm:text-xs text-muted-foreground">
                  Date: <strong>{date}</strong>
                </p>
                <p className="text-[10px] sm:text-xs text-muted-foreground mt-2">
                  This MR hasn't logged any visits or locations on this date.
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {mrId && validMarkers.length > 0 && (
          <div className="absolute top-2 left-2 right-2 sm:top-4 sm:left-4 sm:right-auto z-[1000]">
            <Card className="bg-background/98 backdrop-blur-md border-2 border-primary/20 shadow-2xl">
              <CardContent className="p-2 sm:p-4 space-y-2">
                <div className="flex items-center gap-2 sm:gap-3">
                  <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                    <MapPin className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="font-bold text-sm sm:text-lg truncate">{mrName || `MR ${mrId}`}</div>
                    <div className="text-[10px] sm:text-xs text-muted-foreground">
                      {new Date(date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                    </div>
                  </div>
                </div>
                
                <div className="flex flex-wrap gap-1 sm:gap-2 pt-1 sm:pt-2">
                  {live && (
                    <div className="flex items-center gap-1 sm:gap-2 rounded-full px-2 sm:px-3 py-0.5 sm:py-1 border shadow-sm"
                         style={{
                           borderColor:'#2C8E52',
                           backgroundColor:'#34A853',
                           color:'#ffffff'
                         }}>
                      <span className="w-1.5 h-1.5 sm:w-2.5 sm:h-2.5 rounded-full animate-pulse bg-white/90"></span>
                      <span className="text-[10px] sm:text-xs font-semibold">Live</span>
                    </div>
                  )}
                  <div className="flex items-center gap-1 sm:gap-2 rounded-full px-2 sm:px-3 py-0.5 sm:py-1 border shadow-sm"
                       style={{
                         borderColor:'#1558B0',
                         backgroundColor:'#1A73E8',
                         color:'#ffffff'
                       }}>
                    <span className="w-1.5 h-1.5 sm:w-2.5 sm:h-2.5 rounded-full bg-white/90"></span>
                    <span className="text-[10px] sm:text-xs font-semibold whitespace-nowrap">
                      {validMarkers.length} Point{validMarkers.length !== 1 ? 's' : ''}
                    </span>
                  </div>
                  <div className="flex items-center gap-1 sm:gap-2 rounded-full px-2 sm:px-3 py-0.5 sm:py-1 border shadow-sm"
                       style={{
                         borderColor:'#1558B0',
                         backgroundColor:'#1A73E8',
                         color:'#ffffff'
                       }}>
                    <span className="w-1.5 h-1.5 sm:w-2.5 sm:h-2.5 rounded-full bg-white/90"></span>
                    <span className="text-[10px] sm:text-xs font-semibold whitespace-nowrap">
                      {validMarkers.filter(m => m.type === 'visit').length} Visit{validMarkers.filter(m => m.type === 'visit').length !== 1 ? 's' : ''}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Map Controls */}
        <div className="absolute top-2 right-2 sm:top-4 sm:right-4 z-[1000] flex flex-col gap-1 sm:gap-2">
          <Button
            size="icon"
            variant="secondary"
            onClick={handleZoomIn}
            className="shadow-lg h-8 w-8 sm:h-10 sm:w-10"
          >
            <ZoomIn className="w-3 h-3 sm:w-4 sm:h-4" />
          </Button>
          <Button
            size="icon"
            variant="secondary"
            onClick={handleZoomOut}
            className="shadow-lg h-8 w-8 sm:h-10 sm:w-10"
          >
            <ZoomOut className="w-3 h-3 sm:w-4 sm:h-4" />
          </Button>
          <Button
            size="icon"
            variant="secondary"
            onClick={handleFullscreen}
            className="shadow-lg h-8 w-8 sm:h-10 sm:w-10"
          >
            <Maximize2 className="w-3 h-3 sm:w-4 sm:h-4" />
          </Button>
        </div>

        {/* Loading Overlay */}
        {isLoading && (
          <div className="absolute inset-0 z-[1001] bg-background/80 backdrop-blur-sm flex items-center justify-center">
            <div className="flex flex-col items-center gap-2">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <p className="text-sm text-muted-foreground">Loading map...</p>
            </div>
          </div>
        )}

        {/* OpenStreetMap */}
        <MapContainer
          center={center}
          zoom={zoom}
          className="w-full h-full"
          ref={mapRef}
        >
          {/* OpenStreetMap Tiles - Completely FREE */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Markers with custom colors based on type */}
          {validMarkers.map((marker, index) => {
            // DEBUG: Log coordinates to verify
            if (index === 0) {
              console.log(`🗺️ Creating marker ${index + 1}:`, {
                id: marker.id,
                lat: marker.latitude,
                lng: marker.longitude,
                position: [marker.latitude, marker.longitude],
                location_name: marker.location_name
              });
            }
            const isFirst = index === 0;
            const isLast = index === validMarkers.length - 1;
            return (
            <Marker 
              key={marker.id || `${marker.latitude}-${marker.longitude}-${index}`}
              position={[marker.latitude, marker.longitude]}
              icon={createCustomIcon(
                marker.type,
                marker.type === 'visit' ? index : undefined,
                { isFirst, isLast }
              )}
            >
              <Popup
                closeButton={true}
                className="enhanced-popup"
                maxWidth={380}
                autoPan={false}
              >
                <div className="p-0 space-y-0 min-w-[320px] bg-gradient-to-br from-white via-slate-50/50 to-blue-50/30 rounded-xl overflow-hidden shadow-2xl border-0">
                  {/* Stunning Header with Gradient */}
                  <div className="relative bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 p-5">
                    {/* Decorative Background Elements */}
                    <div className="absolute inset-0 bg-black/10"></div>
                    <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-8 translate-x-16 blur-xl"></div>
                    <div className="absolute bottom-0 left-0 w-20 h-20 bg-white/5 rounded-full translate-y-8 -translate-x-8 blur-lg"></div>
                    
                    <div className="relative flex items-center gap-4">
                      <div className="flex-shrink-0">
                        <div 
                          className="w-12 h-12 rounded-2xl flex items-center justify-center text-white font-bold text-lg shadow-2xl backdrop-blur-sm border border-white/30"
                          style={{
                            background: `linear-gradient(135deg, ${marker.type === 'visit' ? '#1A73E8' : marker.type === 'current' ? '#EA4335' : '#34A853'}, ${marker.type === 'visit' ? '#1557B0' : marker.type === 'current' ? '#D93025' : '#2D7D32'})`,
                            boxShadow: '0 8px 32px rgba(0,0,0,0.3), inset 0 2px 4px rgba(255,255,255,0.2)'
                          }}
                        >
                          <span className="drop-shadow-sm">
                            {marker.type === 'visit' ? (index + 1) : marker.type === 'current' ? '📍' : '→'}
                          </span>
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-bold text-lg leading-tight text-white drop-shadow-md truncate">
                          {marker.location_name || `Location ${index + 1}`}
                        </h3>
                        <div className="flex items-center gap-2 mt-2">
                          <span className="capitalize font-medium text-white/90 text-sm bg-white/20 px-2 py-1 rounded-full backdrop-blur-sm">
                            {marker.type}
                          </span>
                          {marker.visit_type && marker.visit_type !== 'other' && (
                            <span className="px-3 py-1 bg-gradient-to-r from-white/25 to-white/15 backdrop-blur-md text-white rounded-full text-xs font-semibold border border-white/30 shadow-lg">
                              🏷️ {marker.visit_type}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Beautiful Details Grid */}
                  <div className="p-4 space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-gradient-to-br from-blue-50 to-blue-100/50 p-3 rounded-xl border border-blue-200/50 shadow-sm">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-blue-600">⏰</span>
                          <span className="text-xs font-semibold text-blue-700 uppercase tracking-wide">Time</span>
                        </div>
                        <div className="font-bold text-slate-800 text-base">
                          {new Date(marker.timestamp).toLocaleString('en-IN', {
                            timeZone: 'Asia/Kolkata',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </div>
                      </div>
                      <div className="bg-gradient-to-br from-emerald-50 to-emerald-100/50 p-3 rounded-xl border border-emerald-200/50 shadow-sm">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-emerald-600">📅</span>
                          <span className="text-xs font-semibold text-emerald-700 uppercase tracking-wide">Date</span>
                        </div>
                        <div className="font-bold text-slate-800 text-base">
                          {new Date(marker.timestamp).toLocaleDateString('en-IN', {
                            day: 'numeric',
                            month: 'short'
                          })}
                        </div>
                      </div>
                    </div>
                  
                    {/* Beautiful Info Cards */}
                    <div className="space-y-3">
                      {marker.duration && (
                        <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200/60 rounded-xl p-3 shadow-sm hover:shadow-md transition-all duration-200">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center text-white text-sm font-bold shadow-sm">⏱️</div>
                            <div>
                              <div className="text-xs font-semibold text-amber-700 uppercase tracking-wide">Duration</div>
                              <div className="font-bold text-amber-900 text-sm">{marker.duration} minutes</div>
                            </div>
                          </div>
                        </div>
                      )}

                      {marker.contact_name && marker.contact_name.trim() !== '' && (
                        <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200/60 rounded-xl p-3 shadow-sm hover:shadow-md transition-all duration-200">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center text-white text-sm shadow-sm">👨‍⚕️</div>
                            <div className="flex-1 min-w-0">
                              <div className="text-xs font-semibold text-purple-700 uppercase tracking-wide">Contact</div>
                              <div className="font-bold text-purple-900 text-sm truncate">{marker.contact_name}</div>
                            </div>
                          </div>
                        </div>
                      )}
                      

                      {marker.orders && marker.orders.trim() !== '' && marker.orders !== 'Field session started' && (
                        <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200/60 rounded-xl p-3 shadow-sm hover:shadow-md transition-all duration-200">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center text-white text-sm shadow-sm">💊</div>
                            <div className="flex-1 min-w-0">
                              <div className="text-xs font-semibold text-green-700 uppercase tracking-wide">Orders</div>
                              <div className="font-bold text-green-900 text-sm">{marker.orders}</div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  
                    {marker.outcome && (
                      <div className="bg-gradient-to-r from-slate-50 to-gray-100 border border-slate-200/60 rounded-xl p-3 shadow-sm">
                        <div className="flex items-start gap-3">
                          <div className="w-8 h-8 bg-slate-500 rounded-lg flex items-center justify-center text-white text-sm shadow-sm">📝</div>
                          <div className="flex-1">
                            <div className="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-1">Details</div>
                            <div className="text-slate-800 text-sm leading-relaxed">{marker.outcome}</div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* GPS & Address Section */}
                  <div className="px-4 pb-4 space-y-3">
                    <div className="bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-200/60 rounded-xl p-3 shadow-sm">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-6 h-6 bg-indigo-500 rounded-lg flex items-center justify-center text-white text-xs">🌐</div>
                        <span className="text-xs font-semibold text-indigo-700 uppercase tracking-wide">GPS Coordinates</span>
                      </div>
                      <div className="font-mono text-sm bg-indigo-100/50 rounded-lg px-3 py-2 border border-indigo-200/30 text-indigo-900 select-all">
                        Lat: {marker.latitude.toFixed(6)}, Lng: {marker.longitude.toFixed(6)}
                      </div>
                    </div>
                    
                    {marker.address && marker.address !== marker.location_name && (
                      <div className="bg-gradient-to-r from-gray-50 to-slate-50 border border-gray-200/60 rounded-xl p-3 shadow-sm">
                        <div className="flex items-start gap-3">
                          <div className="w-6 h-6 bg-gray-500 rounded-lg flex items-center justify-center text-white text-xs mt-0.5">📍</div>
                          <div>
                            <div className="text-xs font-semibold text-gray-700 uppercase tracking-wide mb-1">Address</div>
                            <div className="text-gray-800 text-sm leading-relaxed">{marker.address}</div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </Popup>
            </Marker>
            );
          })}

          {/* ENHANCED: Route Polyline; dotted when historical (blueprint style) */}
          {path.length > 1 && (
            <>
              {/* Shadow/outline for depth */}
              <Polyline
                positions={path}
                color="#000000"
                weight={5}
                opacity={0.15}
              />
              {/* Main route line */}
              <Polyline
                positions={path}
                color="#1A73E8"
                weight={4}
                opacity={0.9}
                dashArray={isHistorical ? "6 8" : undefined}
              />
            </>
          )}

          {/* Auto-fit bounds when markers change */}
          <MapUpdater markers={validMarkers} />
          
          {/* Center map on specific location when requested */}
          <MapCentre centerOn={centerOn} />
          
          {/* ENHANCED: Smooth follow when MR changes */}
          <MRFollower markers={validMarkers} mrId={mrId} />
        </MapContainer>

        {/* ENHANCED: Legend + Route Statistics Combined */}
        {validMarkers.length > 0 && (
          <div className="absolute bottom-2 left-2 right-2 sm:bottom-4 sm:left-4 sm:right-auto z-[1000] space-y-2">
            {/* Route Stats Card */}
            <Card className="bg-background/98 backdrop-blur-md shadow-xl border-2 border-primary/10">
              <CardContent className="p-2 sm:p-3 space-y-1 sm:space-y-2">
                <div className="text-[10px] sm:text-xs font-bold mb-1 sm:mb-2 text-primary">Route Information</div>
                
                {/* Stats */}
                <div className="space-y-0.5 sm:space-y-1">
                  <div className="flex justify-between text-xs sm:text-sm">
                    <span className="text-muted-foreground">Total Points:</span>
                    <span className="font-bold">{validMarkers.length}</span>
                  </div>
                  <div className="flex justify-between text-xs sm:text-sm">
                    <span className="text-muted-foreground">Visits:</span>
                    <span className="font-bold" style={{color:'#1A73E8'}}>{visitCount}</span>
                  </div>
                  {travelCount > 0 && (
                    <div className="flex justify-between text-xs sm:text-sm">
                      <span className="text-muted-foreground">Travel:</span>
                      <span className="font-bold" style={{color:'#34A853'}}>{travelCount}</span>
                    </div>
                  )}
                </div>
                
                {/* Legend - Hide on very small screens, show on sm+ */}
                <div className="hidden sm:block pt-2 border-top border-border/40 space-y-2">
                  <div className="text-xs font-semibold text-muted-foreground">Legend</div>
                  <div className="flex flex-wrap gap-2">
                    {visitCount > 0 && (
                      <div className="flex items-center gap-2 rounded-full px-2.5 py-1 border shadow-sm"
                           style={{
                             borderColor:'#1558B0',
                             backgroundColor:'#1A73E8',
                             color:'#ffffff'
                           }}>
                        <span className="w-3 h-3 rounded-full bg-white/90"></span>
                        <span className="text-xs font-medium">Visit</span>
                        <span className="text-[10px] leading-none px-1.5 py-0.5 rounded-full font-semibold bg-white/20">#{visitCount}</span>
                      </div>
                    )}
                    {travelCount > 0 && (
                      <div className="flex items-center gap-2 rounded-full px-2.5 py-1 border shadow-sm"
                           style={{
                             borderColor:'#2C8E52',
                             backgroundColor:'#34A853',
                             color:'#ffffff'
                           }}>
                        <span className="w-3 h-3 rounded-full bg-white/90"></span>
                        <span className="text-xs font-medium">Travel</span>
                        <span className="text-[10px] leading-none px-1.5 py-0.5 rounded-full font-semibold bg-white/20">#{travelCount}</span>
                      </div>
                    )}
                    {liveCount > 0 && (
                      <div className="flex items-center gap-2 rounded-full px-2.5 py-1 border shadow-sm"
                           style={{
                             borderColor:'#C0352A',
                             backgroundColor:'#EA4335',
                             color:'#ffffff'
                           }}>
                        <span className="w-3 h-3 rounded-full bg-white/90 animate-pulse"></span>
                        <span className="text-xs font-medium">Live</span>
                        <span className="text-[10px] leading-none px-1.5 py-0.5 rounded-full font-semibold bg-white/20">#{liveCount}</span>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Free Map Notice */}
        <div className="absolute bottom-2 right-2 sm:bottom-4 sm:right-4 z-[1000]">
          <Badge variant="outline" className="bg-background/95 backdrop-blur flex items-center gap-1 sm:gap-2 text-[10px] sm:text-xs px-1.5 py-0.5 sm:px-2 sm:py-1">
            <Info className="w-2 h-2 sm:w-3 sm:h-3" />
            <span className="hidden sm:inline">Free OpenStreetMap</span>
            <span className="sm:hidden">OSM</span>
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
}

