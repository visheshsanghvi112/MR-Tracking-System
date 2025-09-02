"""
MR Session Manager
Handles location-based sessions for field representatives
"""
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import json
import os
import logging

logger = logging.getLogger(__name__)

class MRSession:
    """Manages individual MR field session state"""
    
    def __init__(self, mr_id: int):
        self.mr_id = mr_id
        self.location_captured_at: Optional[float] = None
        self.gps_coords: Optional[Tuple[float, float]] = None
        self.address: Optional[str] = None
        self.entries_count = 0
        self.session_duration = 300  # 5 minutes default
        
    def capture_location(self, lat: float, lon: float, address: str) -> bool:
        """Capture location and start session timer"""
        self.location_captured_at = time.time()
        self.gps_coords = (lat, lon)
        self.address = address
        self.entries_count = 0
        return True
        
    def is_location_active(self) -> bool:
        """Check if location session is still active"""
        if not self.location_captured_at:
            return False
        elapsed = time.time() - self.location_captured_at
        return elapsed < self.session_duration
        
    def time_remaining(self) -> int:
        """Get remaining seconds in current session"""
        if not self.location_captured_at:
            return 0
        elapsed = time.time() - self.location_captured_at
        remaining = max(0, self.session_duration - elapsed)
        return int(remaining)
        
    def needs_warning(self) -> bool:
        """Check if session expiry warning needed"""
        remaining = self.time_remaining()
        return 0 < remaining <= 60  # Warn in last minute
        
    def can_log_entry(self) -> bool:
        """Check if entry logging is allowed"""
        return (
            self.is_location_active() and 
            self.entries_count < 10  # Max 10 entries per session
        )
        
    def log_entry(self) -> bool:
        """Record an entry and increment counter"""
        if self.can_log_entry():
            self.entries_count += 1
            return True
        return False
        
    def clear_session(self):
        """Clear current location session"""
        self.location_captured_at = None
        self.gps_coords = None
        self.address = None
        self.entries_count = 0


class SessionManager:
    """Manages sessions for all MRs"""
    
    def __init__(self):
        self.sessions: Dict[int, MRSession] = {}
        self.session_file = "mr_bot/data/active_sessions.json"
        self.load_sessions()
        
    def get_session(self, mr_id: int) -> MRSession:
        """Get or create session for MR"""
        if mr_id not in self.sessions:
            self.sessions[mr_id] = MRSession(mr_id)
        return self.sessions[mr_id]
        
    def capture_location(self, mr_id: int, lat: float, lon: float, address: str) -> bool:
        """Capture location for MR and start session"""
        try:
            logger.info(f"SESSION_REQUEST: User {mr_id} requesting location capture")
            logger.info(f"COORDINATES: Lat={lat:.6f}, Lon={lon:.6f}")
            logger.info(f"ADDRESS_RESOLVED: {address}")
            
            session = self.get_session(mr_id)
            success = session.capture_location(lat, lon, address)
            
            if success:
                self.save_sessions()
                logger.info(f"SESSION_CREATED: Active session for user {mr_id} - 5min duration, max 10 entries")
                logger.info(f"LOCATION_LOCKED: {address}")
            else:
                logger.error(f"SESSION_FAILED: Could not create session for user {mr_id}")
                logger.error(f"FAILURE_CONTEXT: Invalid coords or other session error")
                
            return success
            
        except Exception as e:
            logger.error(f"SESSION_EXCEPTION: Critical error for user {mr_id}: {str(e)}")
            return False
        
    def can_log_entry(self, mr_id: int) -> bool:
        """Check if MR can log entry"""
        session = self.get_session(mr_id)
        return session.can_log_entry()
        
    def log_entry(self, mr_id: int) -> bool:
        """Log entry for MR"""
        session = self.get_session(mr_id)
        success = session.log_entry()
        if success:
            self.save_sessions()
        return success
        
    def get_location_status(self, mr_id: int) -> Dict:
        """Get current location status for MR"""
        session = self.get_session(mr_id)
        return {
            'active': session.is_location_active(),
            'time_remaining': session.time_remaining(),
            'entries_count': session.entries_count,
            'address': session.address,
            'needs_warning': session.needs_warning()
        }
        
    def clear_expired_sessions(self):
        """Clean up expired sessions"""
        expired_mrs = []
        for mr_id, session in self.sessions.items():
            if not session.is_location_active():
                expired_mrs.append(mr_id)
                
        for mr_id in expired_mrs:
            self.sessions[mr_id].clear_session()
            
        if expired_mrs:
            self.save_sessions()
            
    def save_sessions(self):
        """Save active sessions to file"""
        try:
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            session_data = {}
            
            for mr_id, session in self.sessions.items():
                if session.is_location_active():
                    session_data[str(mr_id)] = {
                        'location_captured_at': session.location_captured_at,
                        'gps_coords': session.gps_coords,
                        'address': session.address,
                        'entries_count': session.entries_count
                    }
                    
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f)
        except Exception as e:
            print(f"Error saving sessions: {e}")
            
    def load_sessions(self):
        """Load active sessions from file"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                    
                for mr_id_str, data in session_data.items():
                    mr_id = int(mr_id_str)
                    session = MRSession(mr_id)
                    session.location_captured_at = data['location_captured_at']
                    session.gps_coords = tuple(data['gps_coords']) if data['gps_coords'] else None
                    session.address = data['address']
                    session.entries_count = data['entries_count']
                    self.sessions[mr_id] = session
                    
        except Exception as e:
            print(f"Error loading sessions: {e}")

# Global session manager instance
session_manager = SessionManager()
