import { OSMMap } from "./osm-map";
import { RoutePoint } from "@/types";

interface MapContainerProps {
  mrId?: string | null;
  date: string;
  live?: boolean;
  markers?: RoutePoint[];
  className?: string;
}

export function MapContainerNew(props: MapContainerProps) {
  // Use the free OpenStreetMap component
  return <OSMMap {...props} />;
}
