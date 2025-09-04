"""
Visit-Based Location Tracker
Captures location data during visit logging and builds route blueprints
No continuous tracking - only location capture during visits
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import sqlite3
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class VisitLocation:
    """Single visit location data"""
    visit_id: str
    mr_id: str
    location_name: str
    location_type: str  # hospital, pharmacy, clinic, etc.
    latitude: float
    longitude: float
    address: str
    visit_time: str
    visit_duration: int  # minutes
    visit_outcome: str
    session_id: str
    weather: Optional[str] = None
    area_type: Optional[str] = None
    notes: Optional[str] = None

@dataclass
class RouteBlueprint:
    """Route blueprint for an MR's day"""
    mr_id: str
    date: str
    total_visits: int
    total_distance: float  # km
    start_location: Dict
    end_location: Dict
    visit_locations: List[VisitLocation]
    route_efficiency: float  # 0-100 score
    time_spent_traveling: int  # minutes
    time_spent_visiting: int  # minutes
    coverage_areas: List[str]
    created_at: str

class VisitBasedLocationTracker:
    """
    Captures location data only when MRs log visits
    Builds comprehensive route blueprints and location history
    """
    
    def __init__(self):
        self.db_path = "visit_locations.db"
        self.blueprints_path = "route_blueprints"
        self.location_history_path = "location_history" 
        self.init_database()
        self.init_storage_dirs()
    
    def init_database(self):
        """Initialize SQLite database for visit locations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Visit locations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visit_locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                visit_id TEXT UNIQUE NOT NULL,
                mr_id TEXT NOT NULL,
                location_name TEXT NOT NULL,
                location_type TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                address TEXT NOT NULL,
                visit_time TEXT NOT NULL,
                visit_duration INTEGER NOT NULL,
                visit_outcome TEXT NOT NULL,
                session_id TEXT NOT NULL,
                weather TEXT,
                area_type TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Route blueprints table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS route_blueprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mr_id TEXT NOT NULL,
                date TEXT NOT NULL,
                total_visits INTEGER NOT NULL,
                total_distance REAL NOT NULL,
                route_efficiency REAL NOT NULL,
                time_spent_traveling INTEGER NOT NULL,
                time_spent_visiting INTEGER NOT NULL,
                blueprint_data TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(mr_id, date)
            )
        ''')
        
        # Location patterns table for analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS location_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mr_id TEXT NOT NULL,
                location_cluster TEXT NOT NULL,
                visit_frequency INTEGER NOT NULL,
                avg_visit_duration REAL NOT NULL,
                best_visit_time TEXT NOT NULL,
                success_rate REAL NOT NULL,
                last_visit TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("VISIT_TRACKER: Database initialized")
    
    def init_storage_dirs(self):
        """Initialize storage directories"""
        Path(self.blueprints_path).mkdir(exist_ok=True)
        Path(self.location_history_path).mkdir(exist_ok=True)
        logger.info("VISIT_TRACKER: Storage directories created")
    
    # ==================== VISIT LOCATION CAPTURE ====================
    
    async def capture_visit_location(self, visit_data: Dict) -> bool:
        """
        Capture location data when MR logs a visit
        Called from the main bot when location is shared during visit logging
        """
        
        try:
            # Create visit location object
            visit_location = VisitLocation(
                visit_id=visit_data.get('visit_id', f"visit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                mr_id=visit_data['mr_id'],
                location_name=visit_data.get('location_name', 'Unknown Location'),
                location_type=visit_data.get('location_type', 'general'),
                latitude=visit_data['latitude'],
                longitude=visit_data['longitude'], 
                address=visit_data.get('address', ''),
                visit_time=visit_data.get('visit_time', datetime.now().isoformat()),
                visit_duration=visit_data.get('visit_duration', 30),  # Default 30 min session
                visit_outcome=visit_data.get('visit_outcome', 'completed'),
                session_id=visit_data.get('session_id', ''),
                weather=visit_data.get('weather'),
                area_type=visit_data.get('area_type'),
                notes=visit_data.get('notes')
            )
            
            # Store in database
            success = await self.store_visit_location(visit_location)
            
            if success:
                logger.info(f"VISIT_LOCATION_CAPTURED: MR {visit_location.mr_id} at {visit_location.location_name}")
                
                # Update daily route blueprint
                await self.update_route_blueprint(visit_location.mr_id)
                
                # Update location patterns
                await self.update_location_patterns(visit_location)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"CAPTURE_VISIT_LOCATION: Error - {e}")
            return False
    
    async def store_visit_location(self, visit_location: VisitLocation) -> bool:
        """Store visit location in database"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO visit_locations 
                (visit_id, mr_id, location_name, location_type, latitude, longitude, 
                 address, visit_time, visit_duration, visit_outcome, session_id, 
                 weather, area_type, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                visit_location.visit_id,
                visit_location.mr_id,
                visit_location.location_name,
                visit_location.location_type,
                visit_location.latitude,
                visit_location.longitude,
                visit_location.address,
                visit_location.visit_time,
                visit_location.visit_duration,
                visit_location.visit_outcome,
                visit_location.session_id,
                visit_location.weather,
                visit_location.area_type,
                visit_location.notes
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"STORE_VISIT_LOCATION: Error - {e}")
            return False
    
    # ==================== ROUTE BLUEPRINT GENERATION ====================
    
    async def update_route_blueprint(self, mr_id: str, date: str = None) -> RouteBlueprint:
        """Generate/update route blueprint for MR's daily visits"""
        
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Get all visits for the day
            visits = await self.get_daily_visits(mr_id, date)
            
            if not visits:
                logger.info(f"ROUTE_BLUEPRINT: No visits found for MR {mr_id} on {date}")
                return None
            
            # Calculate route metrics
            total_distance = self.calculate_total_route_distance(visits)
            route_efficiency = self.calculate_route_efficiency(visits)
            travel_time, visit_time = self.calculate_time_distribution(visits)
            coverage_areas = self.identify_coverage_areas(visits)
            
            # Create route blueprint
            blueprint = RouteBlueprint(
                mr_id=mr_id,
                date=date,
                total_visits=len(visits),
                total_distance=total_distance,
                start_location=self.get_first_visit_location(visits),
                end_location=self.get_last_visit_location(visits),
                visit_locations=visits,
                route_efficiency=route_efficiency,
                time_spent_traveling=travel_time,
                time_spent_visiting=visit_time,
                coverage_areas=coverage_areas,
                created_at=datetime.now().isoformat()
            )
            
            # Store blueprint
            await self.store_route_blueprint(blueprint)
            
            # Save detailed blueprint file
            await self.save_blueprint_file(blueprint)
            
            logger.info(f"ROUTE_BLUEPRINT: Generated for MR {mr_id} - {len(visits)} visits, {total_distance:.2f}km")
            
            return blueprint
            
        except Exception as e:
            logger.error(f"UPDATE_ROUTE_BLUEPRINT: Error - {e}")
            return None
    
    async def get_daily_visits(self, mr_id: str, date: str) -> List[VisitLocation]:
        """Get all visits for a specific day"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM visit_locations 
            WHERE mr_id = ? AND DATE(visit_time) = ?
            ORDER BY visit_time
        ''', (mr_id, date))
        
        rows = cursor.fetchall()
        conn.close()
        
        visits = []
        for row in rows:
            visit = VisitLocation(
                visit_id=row[1],
                mr_id=row[2],
                location_name=row[3],
                location_type=row[4],
                latitude=row[5],
                longitude=row[6],
                address=row[7],
                visit_time=row[8],
                visit_duration=row[9],
                visit_outcome=row[10],
                session_id=row[11],
                weather=row[12],
                area_type=row[13],
                notes=row[14]
            )
            visits.append(visit)
        
        return visits
    
    def calculate_total_route_distance(self, visits: List[VisitLocation]) -> float:
        """Calculate total distance traveled between visits"""
        
        if len(visits) < 2:
            return 0.0
        
        total_distance = 0
        for i in range(1, len(visits)):
            distance = self.calculate_distance(
                visits[i-1].latitude, visits[i-1].longitude,
                visits[i].latitude, visits[i].longitude
            )
            total_distance += distance
        
        return round(total_distance / 1000, 2)  # Convert to km
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in meters"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371000  # Earth's radius in meters
        
        return c * r
    
    def calculate_route_efficiency(self, visits: List[VisitLocation]) -> float:
        """Calculate route efficiency score (0-100)"""
        
        if len(visits) < 2:
            return 100.0
        
        # Calculate actual vs optimal distance
        actual_distance = self.calculate_total_route_distance(visits)
        optimal_distance = self.calculate_optimal_route_distance(visits)
        
        if optimal_distance == 0:
            return 100.0
        
        efficiency = (optimal_distance / actual_distance) * 100
        return min(100.0, efficiency)
    
    def calculate_optimal_route_distance(self, visits: List[VisitLocation]) -> float:
        """Calculate optimal route distance using nearest neighbor approximation"""
        
        if len(visits) < 2:
            return 0.0
        
        # Simple nearest neighbor for optimal route approximation
        unvisited = visits[1:].copy()  # Start from first visit
        current = visits[0]
        total_distance = 0
        
        while unvisited:
            # Find nearest unvisited location
            nearest_idx = 0
            min_distance = float('inf')
            
            for i, visit in enumerate(unvisited):
                distance = self.calculate_distance(
                    current.latitude, current.longitude,
                    visit.latitude, visit.longitude
                )
                if distance < min_distance:
                    min_distance = distance
                    nearest_idx = i
            
            # Move to nearest location
            current = unvisited.pop(nearest_idx)
            total_distance += min_distance
        
        return total_distance / 1000  # Convert to km
    
    def calculate_time_distribution(self, visits: List[VisitLocation]) -> Tuple[int, int]:
        """Calculate time spent traveling vs visiting"""
        
        total_visit_time = sum(visit.visit_duration for visit in visits)
        
        # Estimate travel time based on distance (assume 30 km/h average speed)
        total_distance_km = self.calculate_total_route_distance(visits)
        estimated_travel_time = int((total_distance_km / 30) * 60)  # minutes
        
        return estimated_travel_time, total_visit_time
    
    def identify_coverage_areas(self, visits: List[VisitLocation]) -> List[str]:
        """Identify geographical areas covered"""
        
        areas = set()
        for visit in visits:
            # Extract area from address or use location type
            if visit.area_type:
                areas.add(visit.area_type)
            elif 'hospital' in visit.location_type.lower():
                areas.add('Hospital District')
            elif 'pharmacy' in visit.location_type.lower():
                areas.add('Pharmacy Area')
            elif 'clinic' in visit.location_type.lower():
                areas.add('Medical Complex')
            else:
                areas.add('General Area')
        
        return list(areas)
    
    def get_first_visit_location(self, visits: List[VisitLocation]) -> Dict:
        """Get first visit location details"""
        if not visits:
            return {}
        
        first = visits[0]
        return {
            'name': first.location_name,
            'time': first.visit_time,
            'lat': first.latitude,
            'lon': first.longitude
        }
    
    def get_last_visit_location(self, visits: List[VisitLocation]) -> Dict:
        """Get last visit location details"""
        if not visits:
            return {}
        
        last = visits[-1]
        return {
            'name': last.location_name, 
            'time': last.visit_time,
            'lat': last.latitude,
            'lon': last.longitude
        }
    
    # ==================== BLUEPRINT STORAGE ====================
    
    async def store_route_blueprint(self, blueprint: RouteBlueprint) -> bool:
        """Store route blueprint in database"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert visit locations to JSON for storage
            blueprint_data = {
                'start_location': blueprint.start_location,
                'end_location': blueprint.end_location,
                'visit_locations': [asdict(visit) for visit in blueprint.visit_locations],
                'coverage_areas': blueprint.coverage_areas
            }
            
            cursor.execute('''
                INSERT OR REPLACE INTO route_blueprints 
                (mr_id, date, total_visits, total_distance, route_efficiency,
                 time_spent_traveling, time_spent_visiting, blueprint_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                blueprint.mr_id,
                blueprint.date,
                blueprint.total_visits,
                blueprint.total_distance,
                blueprint.route_efficiency,
                blueprint.time_spent_traveling,
                blueprint.time_spent_visiting,
                json.dumps(blueprint_data)
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"STORE_ROUTE_BLUEPRINT: Error - {e}")
            return False
    
    async def save_blueprint_file(self, blueprint: RouteBlueprint):
        """Save detailed blueprint as JSON file"""
        
        try:
            filename = f"{blueprint.mr_id}_{blueprint.date}_blueprint.json"
            filepath = Path(self.blueprints_path) / filename
            
            blueprint_dict = asdict(blueprint)
            
            with open(filepath, 'w') as f:
                json.dump(blueprint_dict, f, indent=2, default=str)
            
            logger.info(f"BLUEPRINT_FILE: Saved {filepath}")
            
        except Exception as e:
            logger.error(f"SAVE_BLUEPRINT_FILE: Error - {e}")
    
    # ==================== LOCATION PATTERN ANALYSIS ====================
    
    async def update_location_patterns(self, visit_location: VisitLocation):
        """Update location patterns for ML and analytics"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Define location cluster (simplified geo-clustering)
            cluster = self.get_location_cluster(visit_location.latitude, visit_location.longitude)
            
            # Check if pattern exists
            cursor.execute('''
                SELECT visit_frequency, avg_visit_duration, success_rate, pattern_data
                FROM location_patterns 
                WHERE mr_id = ? AND location_cluster = ?
            ''', (visit_location.mr_id, cluster))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing pattern
                new_frequency = existing[0] + 1
                new_avg_duration = (existing[1] * existing[0] + visit_location.visit_duration) / new_frequency
                
                # Update success rate based on visit outcome
                outcome_score = 1.0 if visit_location.visit_outcome == 'successful' else 0.5
                new_success_rate = (existing[2] * existing[0] + outcome_score) / new_frequency
                
                pattern_data = json.loads(existing[3]) if existing[3] else {}
                pattern_data['last_visits'] = pattern_data.get('last_visits', [])
                pattern_data['last_visits'].append({
                    'time': visit_location.visit_time,
                    'duration': visit_location.visit_duration,
                    'outcome': visit_location.visit_outcome
                })
                
                # Keep only last 10 visits
                pattern_data['last_visits'] = pattern_data['last_visits'][-10:]
                
                cursor.execute('''
                    UPDATE location_patterns 
                    SET visit_frequency = ?, avg_visit_duration = ?, success_rate = ?,
                        last_visit = ?, pattern_data = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE mr_id = ? AND location_cluster = ?
                ''', (
                    new_frequency, new_avg_duration, new_success_rate,
                    visit_location.visit_time, json.dumps(pattern_data),
                    visit_location.mr_id, cluster
                ))
                
            else:
                # Create new pattern
                outcome_score = 1.0 if visit_location.visit_outcome == 'successful' else 0.5
                pattern_data = {
                    'first_visit': visit_location.visit_time,
                    'location_type': visit_location.location_type,
                    'last_visits': [{
                        'time': visit_location.visit_time,
                        'duration': visit_location.visit_duration,
                        'outcome': visit_location.visit_outcome
                    }]
                }
                
                cursor.execute('''
                    INSERT INTO location_patterns 
                    (mr_id, location_cluster, visit_frequency, avg_visit_duration,
                     best_visit_time, success_rate, last_visit, pattern_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    visit_location.mr_id, cluster, 1, visit_location.visit_duration,
                    datetime.fromisoformat(visit_location.visit_time).strftime('%H:%M'),
                    outcome_score, visit_location.visit_time, json.dumps(pattern_data)
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"LOCATION_PATTERNS: Updated for MR {visit_location.mr_id} at cluster {cluster}")
            
        except Exception as e:
            logger.error(f"UPDATE_LOCATION_PATTERNS: Error - {e}")
    
    def get_location_cluster(self, lat: float, lon: float) -> str:
        """Get location cluster identifier (simplified geo-clustering)"""
        
        # Round to 3 decimal places for clustering (~100m precision)
        cluster_lat = round(lat, 3)
        cluster_lon = round(lon, 3)
        
        return f"{cluster_lat}_{cluster_lon}"
    
    # ==================== DASHBOARD DATA API ====================
    
    async def get_route_blueprint(self, mr_id: str, date: str = None) -> Dict:
        """Get route blueprint for dashboard display"""
        
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM route_blueprints 
                WHERE mr_id = ? AND date = ?
            ''', (mr_id, date))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            blueprint_data = json.loads(row[8])
            
            return {
                'mr_id': row[1],
                'date': row[2],
                'total_visits': row[3],
                'total_distance': row[4],
                'route_efficiency': row[5],
                'time_spent_traveling': row[6],
                'time_spent_visiting': row[7],
                'start_location': blueprint_data['start_location'],
                'end_location': blueprint_data['end_location'],
                'visit_locations': blueprint_data['visit_locations'],
                'coverage_areas': blueprint_data['coverage_areas']
            }
            
        except Exception as e:
            logger.error(f"GET_ROUTE_BLUEPRINT: Error - {e}")
            return None
    
    async def get_location_history(self, mr_id: str, days: int = 7) -> List[Dict]:
        """Get location history for specified days"""
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DATE(visit_time) as date, COUNT(*) as visits,
                       AVG(visit_duration) as avg_duration,
                       GROUP_CONCAT(location_name) as locations
                FROM visit_locations 
                WHERE mr_id = ? AND visit_time BETWEEN ? AND ?
                GROUP BY DATE(visit_time)
                ORDER BY date DESC
            ''', (mr_id, start_date.isoformat(), end_date.isoformat()))
            
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                history.append({
                    'date': row[0],
                    'total_visits': row[1],
                    'avg_visit_duration': round(row[2], 1),
                    'locations_visited': row[3].split(',') if row[3] else []
                })
            
            return history
            
        except Exception as e:
            logger.error(f"GET_LOCATION_HISTORY: Error - {e}")
            return []
    
    async def get_location_analytics(self, mr_id: str) -> Dict:
        """Get comprehensive location analytics"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Most visited locations
            cursor.execute('''
                SELECT location_cluster, visit_frequency, avg_visit_duration, success_rate
                FROM location_patterns 
                WHERE mr_id = ? 
                ORDER BY visit_frequency DESC LIMIT 5
            ''', (mr_id,))
            
            top_locations = cursor.fetchall()
            
            # Recent performance
            cursor.execute('''
                SELECT date, route_efficiency, total_distance, total_visits
                FROM route_blueprints 
                WHERE mr_id = ? 
                ORDER BY date DESC LIMIT 7
            ''', (mr_id,))
            
            recent_performance = cursor.fetchall()
            
            conn.close()
            
            analytics = {
                'top_locations': [
                    {
                        'cluster': row[0],
                        'visit_count': row[1],
                        'avg_duration': row[2],
                        'success_rate': row[3]
                    } for row in top_locations
                ],
                'recent_performance': [
                    {
                        'date': row[0],
                        'efficiency': row[1],
                        'distance': row[2],
                        'visits': row[3]
                    } for row in recent_performance
                ]
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"GET_LOCATION_ANALYTICS: Error - {e}")
            return {}

# Global instance
visit_tracker = VisitBasedLocationTracker()

# Integration functions for existing bot
async def log_visit_with_location(mr_id: str, location_data: Dict, visit_data: Dict) -> bool:
    """
    Integration function to be called from main bot when MR logs a visit with location
    """
    
    combined_data = {
        **location_data,
        **visit_data,
        'mr_id': mr_id
    }
    
    success = await visit_tracker.capture_visit_location(combined_data)
    
    if success:
        logger.info(f"VISIT_WITH_LOCATION: Logged for MR {mr_id}")
        return True
    
    return False

async def get_mr_route_blueprint(mr_id: str, date: str = None) -> Dict:
    """Get route blueprint for dashboard"""
    return await visit_tracker.get_route_blueprint(mr_id, date)

async def get_mr_location_history(mr_id: str, days: int = 7) -> List[Dict]:
    """Get location history for dashboard"""
    return await visit_tracker.get_location_history(mr_id, days)

async def get_mr_location_analytics(mr_id: str) -> Dict:
    """Get location analytics for dashboard"""  
    return await visit_tracker.get_location_analytics(mr_id)
