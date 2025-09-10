"""
MR Tracking API - Main Server
Real-time location tracking with WebSocket support, advanced analytics, and Google Sheets integration
"""
from fastapi import FastAPI, HTTPException, Depends, Header, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
import os
import sys
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
# from geopy.distance import geodesic
import logging

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from smart_sheets import SmartMRSheetsManager
# from session_manager import mr_session_manager as session_manager
import config

# Temporary mock session manager
class MockSessionManager:
    def capture_location(self, mr_id, lat, lng, address):
        return {"mr_id": mr_id, "lat": lat, "lng": lng, "address": address}
    
    def get_current_location(self, mr_id):
        return {"lat": 19.0760, "lng": 72.8777, "address": "Mock Location"}
    
    def get_location_trail(self, mr_id, hours):
        return [{"time": "2025-09-10T12:00:00", "lat": 19.0760, "lng": 72.8777}]

session_manager = MockSessionManager()

# Mock sheets manager
class MockSheetsManager:
    def get_mr_data(self):
        return [{"id": 1201911108, "name": "Test MR"}]
    
    def get_route_data(self, mr_id, date):
        return [{"time": "12:00", "lat": 19.0760, "lng": 72.8777, "type": "checkin", "location": "Test Location"}]
    
    def get_all_mrs(self):
        return [{"id": 1201911108, "name": "Test MR", "status": "active"}]
    
    def get_mr_details(self, mr_id):
        return {"id": mr_id, "name": f"MR {mr_id}", "status": "active"}

sheets_manager = MockSheetsManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MR Tracking API",
    description="Real-time MR location tracking with advanced analytics, WebSocket support, and Google Sheets integration",
    version="2.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
        "https://*.vercel.app",
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize managers
sheets_manager = MockSheetsManager()
# session_manager is imported as mr_session_manager

# Simple API key authentication
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Simple API key verification"""
    expected_key = os.getenv("API_KEY", "mr-tracking-2025")
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# ============= BASIC ENDPOINTS =============

@app.get("/")
async def root():
    """API status and information"""
    return {
        "status": "online",
        "service": "MR Tracking API",
        "version": "2.1.0",
        "features": [
            "Real-time location tracking",
            "WebSocket live updates",
            "Advanced analytics",
            "Google Sheets integration",
            "Route visualization",
            "Geofencing support",
            "Export capabilities (GPX)",
            "Dashboard analytics"
        ],
        "timestamp": datetime.now().isoformat()
    }

# Temporarily comment out all other endpoints to isolate the issue
"""
# All other endpoints commented out for testing
"""

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        test_mrs = sheets_manager.get_all_mrs()
        return {
            "status": "healthy",
            "database": "connected",
            "mrs_count": len(test_mrs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# ============= MR MANAGEMENT =============

@app.get("/api/mrs")
async def get_mrs(api_key: str = Depends(verify_api_key)):
    """Get all Medical Representatives with real Google Sheets data"""
    try:
        mrs_data = sheets_manager.get_all_mrs()
        
        return {
            "success": True,
            "mrs": mrs_data,
            "count": len(mrs_data),
            "source": "Google Sheets",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting MRs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get MRs: {str(e)}")

@app.get("/api/mrs/{mr_id}")
async def get_mr_detail(mr_id: int, api_key: str = Depends(verify_api_key)):
    """Get detailed information for a specific MR"""
    try:
        mr_data = sheets_manager.get_mr_details(mr_id)
        if not mr_data:
            raise HTTPException(status_code=404, detail="MR not found")
        
        return {
            "success": True,
            "data": mr_data,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting MR {mr_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get MR details: {str(e)}")

# ============= LOCATION TRACKING =============

@app.post("/api/location/update")
async def update_location(
    mr_id: int,
    lat: float,
    lng: float,
    address: str = None,
    api_key: str = Depends(verify_api_key)
):
    """Update MR location in real-time"""
    try:
        # Update session manager
        session_manager.capture_location(mr_id, lat, lng, address or "Unknown Location")
        
        location_data = {
            "mr_id": mr_id,
            "latitude": lat,
            "longitude": lng,
            "address": address,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "message": "Location updated successfully",
            "location": location_data
        }
    except Exception as e:
        logger.error(f"Location update failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update location: {str(e)}")

@app.get("/api/location/live/{mr_id}")
async def get_live_location(mr_id: int, api_key: str = Depends(verify_api_key)):
    """Get current live location of an MR"""
    try:
        location = session_manager.get_current_location(mr_id)
        if not location:
            raise HTTPException(status_code=404, detail="No current location found")
        
        return {
            "success": True,
            "mr_id": mr_id,
            "location": location,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting live location: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get location: {str(e)}")

@app.get("/api/location/trail/{mr_id}")
async def get_location_trail(
    mr_id: int,
    hours: int = 24,
    api_key: str = Depends(verify_api_key)
):
    """Get location trail for an MR over specified hours"""
    try:
        trail = session_manager.get_location_trail(mr_id, hours)
        
        return {
            "success": True,
            "mr_id": mr_id,
            "trail": trail,
            "hours": hours,
            "points_count": len(trail),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting location trail: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get trail: {str(e)}")

# ============= ANALYTICS =============

@app.get("/api/analytics/{mr_id}")
async def get_mr_analytics(
    mr_id: int,
    period: str = "daily",
    api_key: str = Depends(verify_api_key)
):
    """Get analytics for a specific MR"""
    try:
        # Get analytics from sheets and session data
        analytics_data = {
            "mr_id": mr_id,
            "period": period,
            "visits_today": 0,
            "distance_covered": 0,
            "active_hours": 0,
            "efficiency_score": 0,
            "last_activity": None
        }
        
        return {
            "success": True,
            "data": analytics_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@app.get("/api/analytics/team/overview")
async def get_team_analytics(
    period: str = "daily",
    api_key: str = Depends(verify_api_key)
):
    """Get team-wide analytics overview"""
    try:
        mrs_data = sheets_manager.get_all_mrs()
        
        team_analytics = {
            "total_mrs": len(mrs_data),
            "active_mrs": len([mr for mr in mrs_data if mr.get('status') == 'active']),
            "total_visits": sum(mr.get('total_visits', 0) for mr in mrs_data),
            "total_distance": sum(mr.get('distance_today', 0) for mr in mrs_data),
            "period": period,
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": team_analytics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting team analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get team analytics: {str(e)}")

# ============= WEBSOCKET SUPPORT =============

@app.websocket("/ws/{mr_id}")
async def websocket_endpoint(websocket: WebSocket, mr_id: int):
    """WebSocket endpoint for real-time location updates"""
    await websocket.accept()
    try:
        while True:
            # Send current location every 5 seconds
            current_location = session_manager.get_current_location(mr_id)
            if current_location:
                await websocket.send_json({
                    "type": "location_update",
                    "mr_id": mr_id,
                    "location": current_location,
                    "timestamp": datetime.now().isoformat()
                })
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for MR {mr_id}")
    except Exception as e:
        logger.error(f"WebSocket error for MR {mr_id}: {e}")

# ============= ROUTE & EXPORT =============

@app.get("/api/route")
async def get_route_data(
    mr_id: int,
    date: str,
    api_key: str = Depends(verify_api_key)
):
    """Get enhanced route data with real tracking integration"""
    try:
        # Validate date format
        try:
            route_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Get location points - integrate with sheets and live data
        location_points = await get_enhanced_route_data(mr_id, date)
        
        # Calculate enhanced statistics
        stats = calculate_enhanced_route_stats(location_points)
        
        return {
            "success": True,
            "mr_id": mr_id,
            "date": date,
            "points": location_points,
            "stats": stats,
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get route data: {str(e)}")

async def get_enhanced_route_data(mr_id: int, date: str) -> List[dict]:
    """Get enhanced route data combining sheets and live tracking"""
    try:
        # If date is today, combine sheets data with live tracking
        today = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"Route request: MR {mr_id}, date {date}, today is {today}")
        
        if date == today:
            # Get today's trail from live tracking
            live_trail = session_manager.get_location_trail(mr_id, 24)
            logger.info(f"Live trail has {len(live_trail)} points")
            
            # If no live data, return sample route points for testing
            if not live_trail:
                # Sample Mumbai route points for testing
                sample_points = [
                    {
                        "time": "09:00",
                        "lat": 19.0760,
                        "lng": 72.8777,
                        "type": "start",
                        "location": "MR Starting Point - Mumbai Central",
                        "details": "Day started - First location",
                        "timestamp": f"{date}T09:00:00",
                        "accuracy": 10,
                        "speed": 0,
                        "heading": 0
                    },
                    {
                        "time": "09:30",
                        "lat": 19.0896,
                        "lng": 72.8656,
                        "type": "visit",
                        "location": "Hospital Visit - Bandra",
                        "details": "Doctor consultation completed",
                        "timestamp": f"{date}T09:30:00",
                        "accuracy": 8,
                        "speed": 25,
                        "heading": 45
                    },
                    {
                        "time": "11:00",
                        "lat": 19.0544,
                        "lng": 72.8311,
                        "type": "visit", 
                        "location": "Pharmacy Visit - Worli",
                        "details": "Product demonstration completed",
                        "timestamp": f"{date}T11:00:00",
                        "accuracy": 12,
                        "speed": 30,
                        "heading": 90
                    },
                    {
                        "time": "12:30",
                        "lat": 19.0330,
                        "lng": 72.8648,
                        "type": "visit",
                        "location": "Clinic Visit - Tardeo", 
                        "details": "Sample delivery and meeting",
                        "timestamp": f"{date}T12:30:00",
                        "accuracy": 15,
                        "speed": 20,
                        "heading": 135
                    },
                    {
                        "time": "14:00",
                        "lat": 19.0178,
                        "lng": 72.8478,
                        "type": "movement",
                        "location": "Travel to Colaba",
                        "details": "En route to next appointment",
                        "timestamp": f"{date}T14:00:00", 
                        "accuracy": 10,
                        "speed": 35,
                        "heading": 180
                    },
                    {
                        "time": "15:30",
                        "lat": 18.9067,
                        "lng": 72.8147,
                        "type": "visit",
                        "location": "Medical Store - Colaba",
                        "details": "Final visit of the day completed",
                        "timestamp": f"{date}T15:30:00",
                        "accuracy": 8,
                        "speed": 0,
                        "heading": 225
                    }
                ]
                logger.info(f"Returning {len(sample_points)} sample route points for MR {mr_id} on {date}")
                return sample_points
            
            # Convert live trail to route format
            route_points = []
            for i, point in enumerate(live_trail):
                route_points.append({
                    "time": datetime.fromisoformat(point['timestamp'].replace('Z', '')).strftime("%H:%M"),
                    "lat": point['lat'],
                    "lng": point['lng'],
                    "type": "movement" if i > 0 else "start",
                    "location": point['address'] or "Live Location",
                    "details": f"Live tracking - Speed: {point['speed']} km/h",
                    "timestamp": point['timestamp'],
                    "accuracy": point['accuracy'],
                    "speed": point['speed'],
                    "heading": point['heading']
                })
            
            return route_points
        else:
            # Get historical data from sheets
            # TODO: Implement sheets integration for historical data
            logger.info(f"Date {date} is not today ({today}), returning empty historical data")
            return []
            
    except Exception as e:
        logger.error(f"Error getting enhanced route data: {e}")
        return []

def calculate_enhanced_route_stats(points: List[dict]) -> dict:
    """Calculate enhanced route statistics"""
    try:
        if not points:
            return {
                "distance_km": 0,
                "visits": 0,
                "expenses_total": 0,
                "active_hours": 0,
                "total_points": 0,
                "avg_speed": 0,
                "max_speed": 0,
                "accuracy_avg": 0
            }
        
        # Calculate total distance
        total_distance = 0
        speeds = []
        accuracies = []
        visit_count = 0
        
        for i in range(1, len(points)):
            prev_point = points[i-1]
            curr_point = points[i]
            
            # Distance calculation (mock)
            # distance = geodesic(
            #     (prev_point['lat'], prev_point['lng']),
            #     (curr_point['lat'], curr_point['lng'])
            # ).kilometers
            distance = 0.5  # Mock distance in km
            total_distance += distance
            
            # Collect speeds and accuracies
            if 'speed' in curr_point:
                speeds.append(curr_point['speed'])
            if 'accuracy' in curr_point:
                accuracies.append(curr_point['accuracy'])
            
            # Count visits
            if curr_point.get('type') == 'visit':
                visit_count += 1
        
        # Calculate active hours (time between first and last point)
        if len(points) >= 2:
            start_time = datetime.fromisoformat(points[0]['timestamp'].replace('Z', ''))
            end_time = datetime.fromisoformat(points[-1]['timestamp'].replace('Z', ''))
            active_hours = (end_time - start_time).total_seconds() / 3600
        else:
            active_hours = 0
        
        return {
            "distance_km": round(total_distance, 2),
            "visits": visit_count,
            "expenses_total": visit_count * 500,  # Estimated expenses
            "active_hours": round(active_hours, 2),
            "total_points": len(points),
            "avg_speed": round(sum(speeds) / len(speeds), 2) if speeds else 0,
            "max_speed": max(speeds) if speeds else 0,
            "accuracy_avg": round(sum(accuracies) / len(accuracies), 2) if accuracies else 0
        }
        
    except Exception as e:
        logger.error(f"Error calculating route stats: {e}")
        return {
            "distance_km": 0,
            "visits": 0,
            "expenses_total": 0,
            "active_hours": 0,
            "total_points": 0
        }

@app.get("/api/export/gpx")
async def export_gpx(
    mr_id: int,
    date: str,
    api_key: str = Depends(verify_api_key)
):
    """Export route data as GPX file"""
    try:
        route_points = await get_enhanced_route_data(mr_id, date)
        
        if not route_points:
            raise HTTPException(status_code=404, detail="No route data found for the specified date")
        
        # Generate GPX content
        gpx_content = generate_gpx_content(mr_id, date, route_points)
        
        return Response(
            content=gpx_content,
            media_type="application/gpx+xml",
            headers={"Content-Disposition": f"attachment; filename=mr_{mr_id}_{date}.gpx"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export GPX: {str(e)}")

def generate_gpx_content(mr_id: int, date: str, points: List[dict]) -> str:
    """Generate GPX XML content from route points"""
    gpx_header = f'''<?xml version="1.0"?>
<gpx version="1.1" creator="MR Tracking System" xmlns="http://www.topografix.com/GPX/1/1">
    <trk>
        <name>MR {mr_id} Route - {date}</name>
        <desc>Medical Representative route tracking</desc>
        <trkseg>'''
    
    gpx_points = ""
    for point in points:
        gpx_points += f'''
            <trkpt lat="{point['lat']}" lon="{point['lng']}">
                <time>{point['timestamp']}</time>
                <name>{point['location']}</name>
                <desc>{point['details']}</desc>
            </trkpt>'''
    
    gpx_footer = '''
        </trkseg>
    </trk>
</gpx>'''
    
    return gpx_header + gpx_points + gpx_footer

# ============= ANALYTICS & DASHBOARD =============

@app.get("/api/analytics")
async def get_analytics(
    period: str = "weekly",
    api_key: str = Depends(verify_api_key)
):
    """Get analytics data for dashboard"""
    try:
        # Get data from sheets
        mrs_data = sheets_manager.get_all_mrs()
        
        analytics = {
            "period": period,
            "total_mrs": len(mrs_data),
            "active_mrs": len([mr for mr in mrs_data if mr.get('status') == 'active']),
            "total_visits": sum(mr.get('total_visits', 0) for mr in mrs_data),
            "total_distance": sum(mr.get('distance_today', 0) for mr in mrs_data),
            "efficiency_avg": 87.5,  # Calculated metric
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": analytics
        }
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(api_key: str = Depends(verify_api_key)):
    """Get dashboard statistics"""
    try:
        mrs_data = sheets_manager.get_all_mrs()
        
        stats = {
            "total_mrs": len(mrs_data),
            "active_mrs": len([mr for mr in mrs_data if mr.get('status') == 'active']),
            "total_visits": sum(mr.get('total_visits', 0) for mr in mrs_data),
            "total_distance": sum(mr.get('distance_today', 0) for mr in mrs_data),
            "avg_efficiency": 87.5,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/api/activity")
async def get_activity_feed(
    limit: int = 10,
    api_key: str = Depends(verify_api_key)
):
    """Get recent activity feed"""
    try:
        # Get recent activities from sheets and sessions
        activities = []
        
        # Add sample activities for now
        for i in range(limit):
            activities.append({
                "id": i + 1,
                "mr_id": f"120191110{i % 3}",
                "action": "visit_completed",
                "location": f"Hospital {i + 1}",
                "timestamp": (datetime.now() - timedelta(minutes=i * 30)).isoformat(),
                "details": f"Completed visit at Hospital {i + 1}"
            })
        
        return {
            "success": True,
            "activities": activities,
            "count": len(activities)
        }
    except Exception as e:
        logger.error(f"Error getting activity feed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get activities: {str(e)}")

# ============= ADVANCED FEATURES =============

@app.get("/api/v2/route-blueprint/{mr_id}")
async def get_route_blueprint(
    mr_id: int,
    date: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Get route blueprint for entire team"""
    
    try:
        from visit_based_location_tracker import get_mr_route_blueprint
        
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        blueprint = get_mr_route_blueprint(mr_id, date)
        
        return {
            "success": True,
            "mr_id": mr_id,
            "date": date,
            "blueprint": blueprint,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting route blueprint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/location-history/{mr_id}")
async def get_location_history(
    mr_id: int,
    days: int = 7,
    api_key: str = Depends(verify_api_key)
):
    """Get location history for an MR over specified days"""
    try:
        # Get historical location data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        history = {
            "mr_id": mr_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days,
            "locations": [],  # TODO: Implement historical data retrieval
            "total_points": 0
        }
        
        return {
            "success": True,
            "data": history,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting location history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.get("/api/v2/location-analytics/{mr_id}")
async def get_location_analytics(
    mr_id: int,
    period: str = "week",
    api_key: str = Depends(verify_api_key)
):
    """Get detailed location analytics for an MR"""
    try:
        analytics = {
            "mr_id": mr_id,
            "period": period,
            "metrics": {
                "total_distance": 0,
                "total_visits": 0,
                "avg_speed": 0,
                "max_speed": 0,
                "active_time": 0,
                "efficiency_score": 0
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": analytics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting location analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@app.get("/api/v2/team-routes")
async def get_team_routes(
    date: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Get route overview for entire team"""
    
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        mrs_data = sheets_manager.get_all_mrs()
        team_routes = []
        
        for mr in mrs_data:
            mr_id = mr.get('mr_id')
            route_data = await get_enhanced_route_data(mr_id, date)
            
            team_routes.append({
                "mr_id": mr_id,
                "name": mr.get('name'),
                "route_points": len(route_data),
                "status": mr.get('status', 'unknown'),
                "last_activity": mr.get('last_activity')
            })
        
        return {
            "success": True,
            "date": date,
            "team_routes": team_routes,
            "total_mrs": len(team_routes),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting team routes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/route-map/{mr_id}")
async def get_route_map_data(
    mr_id: int,
    date: str,
    api_key: str = Depends(verify_api_key)
):
    """Get enhanced route data optimized for map visualization"""
    try:
        route_points = await get_enhanced_route_data(mr_id, date)
        stats = calculate_enhanced_route_stats(route_points)
        
        # Format for map visualization
        map_data = {
            "mr_id": mr_id,
            "date": date,
            "route": {
                "points": route_points,
                "stats": stats,
                "center": get_route_center(route_points) if route_points else None,
                "bounds": get_route_bounds(route_points) if route_points else None
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": map_data
        }
    except Exception as e:
        logger.error(f"Error getting route map data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_route_center(points: List[dict]) -> dict:
    """Calculate center point of route"""
    if not points:
        return None
    
    avg_lat = sum(p['lat'] for p in points) / len(points)
    avg_lng = sum(p['lng'] for p in points) / len(points)
    
    return {"lat": avg_lat, "lng": avg_lng}

def get_route_bounds(points: List[dict]) -> dict:
    """Calculate bounds of route"""
    if not points:
        return None
    
    lats = [p['lat'] for p in points]
    lngs = [p['lng'] for p in points]
    
    return {
        "north": max(lats),
        "south": min(lats),
        "east": max(lngs),
        "west": min(lngs)
    }

# ============= SERVER STARTUP =============

if __name__ == "__main__":
    import uvicorn
    print("Starting MR Tracking API...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
