"""
Location Handler for MR Bot
Handles GPS location capture and geocoding
"""
import asyncio
import logging
import requests
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class LocationHandler:
    """Handles location-related operations"""
    
    def __init__(self):
        self.geocoding_api_key = None  # Will be set from config
        
    async def get_address(self, latitude: float, longitude: float) -> str:
        """Get address from GPS coordinates using free Nominatim API"""
        try:
            # Use OpenStreetMap Nominatim API (completely free)
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}&zoom=18&addressdetails=1"
            headers = {
                'User-Agent': 'MRBot/1.0 (contact@mrbot.app)'  # Required by Nominatim
            }
            
            # Make the request with timeout
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'display_name' in data:
                    address = data['display_name']
                    
                    # Clean up and shorten the address if too long
                    if len(address) > 150:
                        address = address[:150] + "..."
                    
                    logger.info(f"NOMINATIM_SUCCESS: {address}")
                    return address
                elif 'error' in data:
                    logger.warning(f"NOMINATIM_ERROR: {data['error']}")
            else:
                logger.warning(f"NOMINATIM_HTTP_ERROR: Status {response.status_code}")
            
            # Fallback to coordinates if API fails
            logger.warning("Nominatim API failed, using coordinates")
            return f"📍 {latitude:.6f}, {longitude:.6f}"
            
        except requests.exceptions.Timeout:
            logger.warning("Nominatim API timeout, using coordinates")
            return f"📍 {latitude:.6f}, {longitude:.6f}"
        except requests.exceptions.RequestException as e:
            logger.error(f"NOMINATIM_REQUEST_ERROR: {e}")
            return f"📍 {latitude:.6f}, {longitude:.6f}"
        except Exception as e:
            logger.error(f"GEOCODING_ERROR: {e}")
            return f"📍 {latitude:.4f}, {longitude:.4f}"
            
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
        """Get detailed location information using Nominatim API"""
        try:
            # Use OpenStreetMap Nominatim API for detailed location info
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}&zoom=18&addressdetails=1"
            headers = {
                'User-Agent': 'MRBot/1.0 (contact@mrbot.app)'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'display_name' in data:
                    # Extract detailed address components
                    address_parts = data.get('address', {})
                    
                    return {
                        'formatted_address': data.get('display_name', f"📍 {latitude:.6f}, {longitude:.6f}"),
                        'city': (address_parts.get('city') or 
                                address_parts.get('town') or 
                                address_parts.get('village') or 
                                'Unknown City'),
                        'state': (address_parts.get('state') or 
                                 address_parts.get('province') or 
                                 'Unknown State'),
                        'country': address_parts.get('country', 'Unknown Country'),
                        'postal_code': address_parts.get('postcode', 'Unknown'),
                        'accuracy': 'high',
                        'source': 'nominatim'
                    }
            
            # Fallback if API fails
            logger.warning("Nominatim enhance API failed, using basic info")
            return {
                'formatted_address': f"📍 {latitude:.6f}, {longitude:.6f}",
                'city': 'Unknown City',
                'state': 'Unknown State',
                'country': 'Unknown Country',
                'postal_code': 'Unknown',
                'accuracy': 'low',
                'source': 'coordinates'
            }
            
        except Exception as e:
            logger.error(f"Error enhancing location: {e}")
            return {
                'formatted_address': f"📍 {latitude:.4f}, {longitude:.4f}",
                'accuracy': 'low',
                'source': 'fallback'
            }
