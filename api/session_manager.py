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

# Import config for session settings
from config import LOCATION_SESSION_DURATION, MAX_ENTRIES_PER_SESSION, LOCATION_WARNING_THRESHOLD

logger = logging.getLogger(__name__)

class MRSession:
    """Manages individual MR field session state"""
    
    def __init__(self, mr_id: int):
        self.mr_id = mr_id
        self.location_captured_at: Optional[float] = None
        self.gps_coords: Optional[Tuple[float, float]] = None
        self.address: Optional[str] = None
        self.entries_count = 0
        self.session_duration = LOCATION_SESSION_DURATION  # Use config value
        self.max_entries = MAX_ENTRIES_PER_SESSION  # Use config value
        
    def capture_location(self, lat: float, lon: float, address: str) -> bool:
        """Capture location and start/extend session timer"""
        current_time = time.time()
        
        # Check if we have an active session
        was_active = self.is_location_active()
        old_entries = self.entries_count
        
        if was_active:
            logger.info(f"SESSION_EXTEND: Extending active session for user {self.mr_id} (had {old_entries} entries)")
            self.location_captured_at = current_time
            self.gps_coords = (lat, lon)
            self.address = address
            # KEEP existing entries_count - this was the main bug!
            logger.info(f"SESSION_EXTENDED: Kept {self.entries_count} entries, session time reset")
        else:
            # Start new session only if previous expired or never existed
            logger.info(f"SESSION_NEW: Starting fresh session for user {self.mr_id} (previous had {old_entries} entries)")
            self.location_captured_at = current_time
            self.gps_coords = (lat, lon)
            self.address = address
            self.entries_count = 0  # Only reset on truly new session
            logger.info(f"SESSION_FRESH: New session started with 0 entries")
            
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
        return 0 < remaining <= LOCATION_WARNING_THRESHOLD  # Use config value
        
    def can_log_entry(self) -> bool:
        """Check if entry logging is allowed"""
        return (
            self.is_location_active() and 
            self.entries_count < self.max_entries  # Use dynamic max entries
        )
        
    def log_entry(self) -> bool:
        """Record an entry and increment counter"""
        if self.can_log_entry():
            old_count = self.entries_count
            self.entries_count += 1
            logger.info(f"ENTRY_LOGGED: User {self.mr_id} entries: {old_count} → {self.entries_count} (max: {self.max_entries})")
            return True
        else:
            remaining = self.time_remaining()
            logger.error(f"ENTRY_BLOCKED: User {self.mr_id} - Active: {self.is_location_active()}, Entries: {self.entries_count}/{self.max_entries}, Time: {remaining}s")
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
                duration_hours = session.session_duration // 3600
                logger.info(f"SESSION_CREATED: Active session for user {mr_id} - {duration_hours}h duration, max {session.max_entries} entries")
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
        remaining_time = session.time_remaining()
        
        status = {
            'active': session.is_location_active(),
            'time_remaining': remaining_time,
            'time_remaining_hours': remaining_time // 3600,
            'time_remaining_minutes': (remaining_time % 3600) // 60,
            'entries_count': session.entries_count,
            'max_entries': session.max_entries,
            'entries_remaining': session.max_entries - session.entries_count,
            'address': session.address,
            'needs_warning': session.needs_warning(),
            'gps_coords': session.gps_coords
        }
        
        logger.info(f"STATUS_CHECK: User {mr_id} - Active: {status['active']}, Entries: {status['entries_count']}/{status['max_entries']}, Time: {status['time_remaining_hours']}h{status['time_remaining_minutes']}m")
        return status
        
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

# Enhanced MR Session Manager for API
class MRSessionManager(SessionManager):
    """Enhanced session manager with live tracking capabilities"""
    
    def __init__(self):
        super().__init__()
        self.live_locations = {}  # Real-time location cache
        self.location_history = {}  # Location history for analytics
        self.geofences = {}  # Geofenced areas for automatic check-ins
        
    def update_live_location(self, mr_id: int, lat: float, lon: float, 
                           address: str = "", accuracy: float = 0, 
                           speed: float = 0, heading: float = 0):
        """Update real-time location with enhanced data"""
        timestamp = datetime.now().isoformat()
        
        location_data = {
            'mr_id': mr_id,
            'lat': lat,
            'lon': lon, 
            'address': address,
            'accuracy': accuracy,
            'speed': speed,
            'heading': heading,
            'timestamp': timestamp,
            'battery_level': None,  # Can be added from mobile app
            'network_type': None    # Can be added from mobile app
        }
        
        # Update live cache
        self.live_locations[mr_id] = location_data
        
        # Add to history
        if mr_id not in self.location_history:
            self.location_history[mr_id] = []
        self.location_history[mr_id].append(location_data)
        
        # Keep only last 100 locations in memory
        if len(self.location_history[mr_id]) > 100:
            self.location_history[mr_id] = self.location_history[mr_id][-100:]
            
        return True
        
    def get_live_location(self, mr_id: int) -> dict:
        """Get current live location with session status"""
        base_status = self.get_location_status(mr_id)
        
        if mr_id in self.live_locations:
            live_data = self.live_locations[mr_id]
            # Check if location is recent (within 5 minutes)
            location_time = datetime.fromisoformat(live_data['timestamp'].replace('Z', ''))
            is_recent = (datetime.now() - location_time).total_seconds() < 300
            
            return {
                **base_status,
                'lat': live_data['lat'],
                'lon': live_data['lon'],
                'address': live_data['address'],
                'accuracy': live_data['accuracy'],
                'speed': live_data['speed'],
                'heading': live_data['heading'],
                'last_update': live_data['timestamp'],
                'location_fresh': is_recent,
                'session_start': live_data['timestamp'] if base_status['active'] else None,
                'last_activity': live_data['timestamp']
            }
        else:
            return {
                **base_status,
                'lat': 0,
                'lon': 0,
                'address': 'Location not available',
                'accuracy': 0,
                'speed': 0, 
                'heading': 0,
                'last_update': None,
                'location_fresh': False,
                'session_start': None,
                'last_activity': None
            }
            
    def get_location_trail(self, mr_id: int, hours: int = 8) -> list:
        """Get location trail for specific time period"""
        if mr_id not in self.location_history:
            return []
            
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        trail = []
        for location in self.location_history[mr_id]:
            location_time = datetime.fromisoformat(location['timestamp'].replace('Z', ''))
            if location_time >= cutoff_time:
                trail.append(location)
                
        return trail
        
    def calculate_distance_traveled(self, mr_id: int, hours: int = 8) -> float:
        """Calculate total distance traveled in specified hours"""
        trail = self.get_location_trail(mr_id, hours)
        
        if len(trail) < 2:
            return 0.0
            
        total_distance = 0
        for i in range(1, len(trail)):
            from geopy.distance import geodesic
            prev_point = (trail[i-1]['lat'], trail[i-1]['lon'])
            curr_point = (trail[i]['lat'], trail[i]['lon'])
            
            distance = geodesic(prev_point, curr_point).kilometers
            total_distance += distance
            
        return round(total_distance, 2)
        
    def get_mr_analytics(self, mr_id: int) -> dict:
        """Get comprehensive MR analytics"""
        session = self.get_session(mr_id)
        location_status = self.get_live_location(mr_id)
        
        return {
            'mr_id': mr_id,
            'session_active': session.is_location_active(),
            'current_location': {
                'lat': location_status['lat'],
                'lon': location_status['lon'],
                'address': location_status['address'],
                'last_update': location_status['last_update']
            },
            'today_stats': {
                'distance_traveled': self.calculate_distance_traveled(mr_id, 12),
                'locations_visited': len(self.get_location_trail(mr_id, 12)),
                'active_time': self._calculate_active_time(mr_id),
                'entries_logged': session.entries_count
            },
            'performance': {
                'avg_speed': self._calculate_avg_speed(mr_id),
                'location_accuracy': location_status['accuracy'],
                'coverage_area': self._calculate_coverage_area(mr_id)
            }
        }
        
    def _calculate_active_time(self, mr_id: int) -> float:
        """Calculate active field time in hours"""
        trail = self.get_location_trail(mr_id, 12)
        if len(trail) < 2:
            return 0.0
            
        first_time = datetime.fromisoformat(trail[0]['timestamp'].replace('Z', ''))
        last_time = datetime.fromisoformat(trail[-1]['timestamp'].replace('Z', ''))
        
        return round((last_time - first_time).total_seconds() / 3600, 2)
        
    def _calculate_avg_speed(self, mr_id: int) -> float:
        """Calculate average movement speed"""
        trail = self.get_location_trail(mr_id, 12)
        if not trail:
            return 0.0
            
        speeds = [loc['speed'] for loc in trail if loc['speed'] > 0]
        return round(sum(speeds) / len(speeds), 2) if speeds else 0.0
        
    def _calculate_coverage_area(self, mr_id: int) -> dict:
        """Calculate geographical coverage area"""
        trail = self.get_location_trail(mr_id, 12)
        if len(trail) < 2:
            return {'area_km2': 0, 'bounds': None}
            
        lats = [loc['lat'] for loc in trail]
        lons = [loc['lon'] for loc in trail]
        
        return {
            'area_km2': 0,  # Complex calculation - simplified for now
            'bounds': {
                'north': max(lats),
                'south': min(lats), 
                'east': max(lons),
                'west': min(lons)
            }
        }

# Global session managers
session_manager = SessionManager()
mr_session_manager = MRSessionManager()
