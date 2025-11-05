import { OSMMap } from "./osm-map";
import { RoutePoint } from "@/types";

interface MapContainerProps {
  mrId?: string | null;
  date: string;
  live?: boolean;
  markers?: RoutePoint[];
  className?: string;
  centerOn?: { lat: number; lng: number; zoom?: number } | null;
  mrName?: string; // ENHANCED: Display MR name on map
}

export function MapContainer(props: MapContainerProps) {
  // Use the free OpenStreetMap component
  return <OSMMap {...props} />;
}
