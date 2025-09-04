"""
Telegram Bot to API Bridge
Connects the Telegram bot location capture to the enhanced API backend
"""
import aiohttp
import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class TelegramAPIBridge:
    """Bridge between Telegram bot and Enhanced API"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.api_key = "mr-tracking-2025"
        self.session = None
        
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def _make_api_request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """Make request to enhanced API"""
        try:
            session = await self._get_session()
            headers = {
                'x-api-key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            url = f"{self.api_base_url}{endpoint}"
            
            async with session.request(method, url, headers=headers, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API request failed: {response.status} - {await response.text()}")
                    return None
                    
        except Exception as e:
            logger.error(f"API Bridge Error: {e}")
            return None
    
    async def send_location_update(self, mr_id: int, lat: float, lon: float, 
                                 address: str = "", user_data: Dict = None) -> bool:
        """Send location update to enhanced API"""
        try:
            # Prepare enhanced location data
            location_data = {
                "mr_id": mr_id,
                "lat": lat,
                "lon": lon,
                "address": address,
                "accuracy": 10.0,  # Default GPS accuracy
                "speed": 0.0,      # Static when captured via Telegram
                "heading": 0.0,    # Not available from Telegram
                "battery_level": None,  # Can be added later
                "source": "telegram_bot",
                "user_data": user_data or {}
            }
            
            logger.info(f"BRIDGE: Sending location update for MR {mr_id} to enhanced API")
            logger.info(f"LOCATION: {lat:.6f}, {lon:.6f} - {address}")
            
            response = await self._make_api_request("POST", "/api/location/update", location_data)
            
            if response and response.get("success"):
                logger.info(f"BRIDGE_SUCCESS: Location update sent to enhanced API")
                logger.info(f"API_RESPONSE: {response.get('message', 'Unknown')}")
                return True
            else:
                logger.error(f"BRIDGE_FAILED: API did not accept location update")
                return False
                
        except Exception as e:
            logger.error(f"BRIDGE_ERROR: Failed to send location update: {e}")
            return False
    
    async def get_live_status(self, mr_id: int) -> Optional[Dict]:
        """Get live status from enhanced API"""
        try:
            logger.info(f"BRIDGE: Getting live status for MR {mr_id}")
            
            response = await self._make_api_request("GET", f"/api/location/live/{mr_id}")
            
            if response and response.get("success"):
                logger.info(f"BRIDGE_SUCCESS: Retrieved live status from API")
                return response.get("location", {})
            else:
                logger.error(f"BRIDGE_FAILED: Could not get live status")
                return None
                
        except Exception as e:
            logger.error(f"BRIDGE_ERROR: Failed to get live status: {e}")
            return None
    
    async def get_mr_analytics(self, mr_id: int) -> Optional[Dict]:
        """Get MR analytics from enhanced API"""
        try:
            logger.info(f"BRIDGE: Getting analytics for MR {mr_id}")
            
            response = await self._make_api_request("GET", f"/api/analytics/{mr_id}")
            
            if response and response.get("success"):
                logger.info(f"BRIDGE_SUCCESS: Retrieved analytics from API")
                return response.get("analytics", {})
            else:
                logger.error(f"BRIDGE_FAILED: Could not get analytics")
                return None
                
        except Exception as e:
            logger.error(f"BRIDGE_ERROR: Failed to get analytics: {e}")
            return None
    
    async def send_continuous_location_updates(self, mr_id: int, location_stream):
        """Send continuous location updates (for future live tracking)"""
        try:
            logger.info(f"BRIDGE: Starting continuous location updates for MR {mr_id}")
            
            async for location_data in location_stream:
                success = await self.send_location_update(
                    mr_id,
                    location_data['lat'],
                    location_data['lon'],
                    location_data.get('address', ''),
                    location_data.get('user_data', {})
                )
                
                if success:
                    logger.info(f"CONTINUOUS_UPDATE: Location sent for MR {mr_id}")
                else:
                    logger.error(f"CONTINUOUS_ERROR: Failed to send location for MR {mr_id}")
                
                # Wait before next update
                await asyncio.sleep(30)  # 30 second intervals
                
        except Exception as e:
            logger.error(f"CONTINUOUS_STREAM_ERROR: {e}")
    
    async def validate_api_connection(self) -> bool:
        """Test if enhanced API is accessible"""
        try:
            response = await self._make_api_request("GET", "/api/health")
            
            if response and response.get("status") == "healthy":
                logger.info("BRIDGE_VALIDATION: Enhanced API is accessible")
                return True
            else:
                logger.error("BRIDGE_VALIDATION: Enhanced API not responding properly")
                return False
                
        except Exception as e:
            logger.error(f"BRIDGE_VALIDATION_ERROR: {e}")
            return False
    
    async def close(self):
        """Close the bridge session"""
        if self.session:
            await self.session.close()
            self.session = None

# Global bridge instance
telegram_api_bridge = TelegramAPIBridge()
