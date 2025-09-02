"""
Location Handler for MR Bot
Handles GPS location capture and geocoding
"""
import asyncio
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class LocationHandler:
    """Handles location-related operations"""
    
    def __init__(self):
        self.geocoding_api_key = None  # Will be set from config
        
    async def get_address(self, latitude: float, longitude: float) -> str:
        """Get address from GPS coordinates using reverse geocoding"""
        try:
            # For now, return a basic format
            # Can be enhanced with Google Geocoding API later
            return f"Lat: {latitude:.6f}, Lon: {longitude:.6f}"
            
        except Exception as e:
            logger.error(f"Error getting address: {e}")
            return f"Location: {latitude:.4f}, {longitude:.4f}"
            
    def validate_location_accuracy(self, accuracy: float) -> bool:
        """Validate if location accuracy is acceptable"""
        # GPS accuracy in meters - lower is better
        return accuracy <= 100  # Accept if accuracy is within 100 meters
        
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two GPS points in meters"""
        import math
        
        # Haversine formula
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) * math.sin(delta_lat / 2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) * math.sin(delta_lon / 2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance
        
    def is_location_significantly_different(self, 
                                          old_lat: float, old_lon: float,
                                          new_lat: float, new_lon: float,
                                          threshold: float = 50) -> bool:
        """Check if new location is significantly different from old one"""
        distance = self.calculate_distance(old_lat, old_lon, new_lat, new_lon)
        return distance > threshold  # More than 50 meters apart
        
    async def enhance_location_with_geocoding(self, latitude: float, longitude: float) -> dict:
        """Get detailed location information using geocoding API"""
        try:
            # This is a placeholder for geocoding API integration
            # Can be enhanced with Google Geocoding API, OpenStreetMap, etc.
            
            # For now, return basic info
            return {
                'formatted_address': f"Lat: {latitude:.6f}, Lon: {longitude:.6f}",
                'city': 'Unknown City',
                'state': 'Unknown State',
                'country': 'Unknown Country',
                'postal_code': 'Unknown',
                'accuracy': 'high'
            }
            
        except Exception as e:
            logger.error(f"Error enhancing location: {e}")
            return {
                'formatted_address': f"Location: {latitude:.4f}, {longitude:.4f}",
                'accuracy': 'low'
            }
