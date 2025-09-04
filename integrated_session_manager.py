"""
Enhanced Session Manager Integration
Bridges the basic Telegram session manager with the enhanced API system
"""
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime

from telegram_api_bridge import telegram_api_bridge

logger = logging.getLogger(__name__)

class IntegratedSessionManager:
    """Session manager that integrates Telegram bot with enhanced API"""
    
    def __init__(self, basic_session_manager):
        self.basic_manager = basic_session_manager
        self.api_bridge = telegram_api_bridge
        self.integration_enabled = True
        
    def capture_location(self, mr_id: int, lat: float, lon: float, address: str, user_data: Dict = None) -> bool:
        """Capture location with enhanced API integration"""
        try:
            # First, use the basic session manager (for Telegram bot compatibility)
            basic_success = self.basic_manager.capture_location(mr_id, lat, lon, address)
            
            if basic_success and self.integration_enabled:
                # Send to enhanced API asynchronously
                asyncio.create_task(self._send_to_enhanced_api(mr_id, lat, lon, address, user_data))
            
            return basic_success
            
        except Exception as e:
            logger.error(f"INTEGRATED_CAPTURE_ERROR: {e}")
            return False
    
    async def _send_to_enhanced_api(self, mr_id: int, lat: float, lon: float, address: str, user_data: Dict = None):
        """Send location to enhanced API in background"""
        try:
            # Validate API connection first
            if not await self.api_bridge.validate_api_connection():
                logger.warning("INTEGRATION_WARNING: Enhanced API not available, using basic mode only")
                return
            
            # Send location update
            success = await self.api_bridge.send_location_update(mr_id, lat, lon, address, user_data)
            
            if success:
                logger.info(f"INTEGRATION_SUCCESS: Location sent to enhanced API for MR {mr_id}")
            else:
                logger.error(f"INTEGRATION_FAILED: Could not send to enhanced API for MR {mr_id}")
                
        except Exception as e:
            logger.error(f"INTEGRATION_API_ERROR: {e}")
    
    def get_location_status(self, mr_id: int) -> Dict:
        """Get location status with enhanced data when available"""
        try:
            # Always get basic status first
            basic_status = self.basic_manager.get_location_status(mr_id)
            
            # Try to enhance with API data if available
            if self.integration_enabled:
                asyncio.create_task(self._enhance_status_with_api(mr_id, basic_status))
            
            return basic_status
            
        except Exception as e:
            logger.error(f"INTEGRATED_STATUS_ERROR: {e}")
            return self.basic_manager.get_location_status(mr_id)
    
    async def _enhance_status_with_api(self, mr_id: int, basic_status: Dict):
        """Enhance status with API data (for future use)"""
        try:
            api_status = await self.api_bridge.get_live_status(mr_id)
            
            if api_status:
                # Could merge enhanced data here
                logger.info(f"INTEGRATION_ENHANCED: Got enhanced status for MR {mr_id}")
            
        except Exception as e:
            logger.error(f"INTEGRATION_ENHANCE_ERROR: {e}")
    
    async def get_enhanced_analytics(self, mr_id: int) -> Optional[Dict]:
        """Get enhanced analytics from API"""
        try:
            if not self.integration_enabled:
                return None
                
            analytics = await self.api_bridge.get_mr_analytics(mr_id)
            
            if analytics:
                logger.info(f"ANALYTICS_SUCCESS: Retrieved enhanced analytics for MR {mr_id}")
                return analytics
            else:
                logger.warning(f"ANALYTICS_FAILED: No enhanced analytics for MR {mr_id}")
                return None
                
        except Exception as e:
            logger.error(f"ANALYTICS_ERROR: {e}")
            return None
    
    # Delegate other methods to basic manager
    def can_log_entry(self, mr_id: int) -> bool:
        return self.basic_manager.can_log_entry(mr_id)
        
    def log_entry(self, mr_id: int) -> bool:
        return self.basic_manager.log_entry(mr_id)
        
    def clear_expired_sessions(self):
        return self.basic_manager.clear_expired_sessions()
        
    def save_sessions(self):
        return self.basic_manager.save_sessions()
        
    def load_sessions(self):
        return self.basic_manager.load_sessions()
        
    @property
    def sessions(self):
        return self.basic_manager.sessions
    
    def enable_integration(self):
        """Enable enhanced API integration"""
        self.integration_enabled = True
        logger.info("INTEGRATION_ENABLED: Enhanced API integration activated")
    
    def disable_integration(self):
        """Disable enhanced API integration (fallback to basic mode)"""
        self.integration_enabled = False
        logger.info("INTEGRATION_DISABLED: Fallback to basic mode")
