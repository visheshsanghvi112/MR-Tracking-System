"""
Enhanced Live MR Tracking API
Real-time location tracking with WebSocket support and advanced analytics
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
from geopy.distance import geodesic
import logging

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smart_sheets import SmartMRSheetsManager
from session_manager import mr_session_manager as session_manager
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Enhanced MR Live Tracking API",
    description="Real-time MR location tracking with advanced analytics and live updates",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app", 
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Initialize managers
sheets_manager = SmartMRSheetsManager()
# session_manager is imported as mr_session_manager

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, mr_id: int):
        await websocket.accept()
        self.active_connections[mr_id] = websocket
        logger.info(f"WebSocket connected for MR {mr_id}")

    def disconnect(self, mr_id: int):
        if mr_id in self.active_connections:
            del self.active_connections[mr_id]
            logger.info(f"WebSocket disconnected for MR {mr_id}")

    async def send_location_update(self, mr_id: int, data: dict):
        if mr_id in self.active_connections:
            try:
                await self.active_connections[mr_id].send_text(json.dumps(data))
            except:
                self.disconnect(mr_id)

    async def broadcast_to_all(self, message: dict):
        for mr_id, connection in self.active_connections.items():
            try:
                await connection.send_text(json.dumps(message))
            except:
                self.disconnect(mr_id)

manager = ConnectionManager()

# API key authentication
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Enhanced API key verification"""
    expected_key = os.getenv("API_KEY", "mr-tracking-2025")
    # Skip auth for development - enable in production
    return x_api_key

# ============= BASIC ENDPOINTS =============

@app.get("/")
async def root():
    """Enhanced health check endpoint"""
    return {
        "status": "online",
        "service": "Enhanced MR Live Tracking API",
        "version": "2.0.0",
        "features": [
            "Real-time location tracking",
            "WebSocket live updates", 
            "Advanced analytics",
            "Geofencing support",
            "Route optimization"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    """Comprehensive health check"""
    try:
        sheets_connected = sheets_manager.client is not None
        active_sessions = len([s for s in session_manager.sessions.values() if s.is_location_active()])
        live_connections = len(manager.active_connections)
        
        return {
            "status": "healthy",
            "services": {
                "sheets_connected": sheets_connected,
                "session_manager": "active",
                "websocket_manager": "active"
            },
            "metrics": {
                "active_sessions": active_sessions,
                "live_connections": live_connections,
                "total_mrs_tracked": len(session_manager.sessions)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============= MR MANAGEMENT =============

@app.get("/api/mrs")
async def get_mr_list(api_key: str = Depends(verify_api_key)):
    """Get enhanced MR list with live status"""
    try:
        authorized_ids = getattr(config, 'AUTHORIZED_MR_IDS', [])
        
        mr_list = []
        for mr_id in authorized_ids:
            # Get live status
            analytics = session_manager.get_mr_analytics(mr_id)
            
            mr_info = {
                "id": mr_id,
                "name": f"MR {mr_id}",  # TODO: Get from sheets
                "status": "online" if analytics['session_active'] else "offline",
                "last_seen": analytics['current_location']['last_update'],
                "today_stats": analytics['today_stats'],
                "current_location": analytics['current_location']['address']
            }
            mr_list.append(mr_info)
        
        return {
            "success": True,
            "mrs": mr_list,
            "count": len(mr_list),
            "online_count": len([mr for mr in mr_list if mr['status'] == 'online'])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get MR list: {str(e)}")

# ============= LIVE LOCATION TRACKING =============

@app.post("/api/location/update")
async def update_location(
    mr_id: int,
    lat: float,
    lon: float,
    address: Optional[str] = "",
    accuracy: Optional[float] = 0,
    speed: Optional[float] = 0,
    heading: Optional[float] = 0,
    battery_level: Optional[int] = None,
    api_key: str = Depends(verify_api_key)
):
    """Update MR location with enhanced data"""
    try:
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise HTTPException(status_code=400, detail="Invalid coordinates")
        
        # Update location in session manager
        success = session_manager.update_live_location(
            mr_id, lat, lon, address, accuracy, speed, heading
        )
        
        if success:
            # Get updated location data
            location_data = session_manager.get_live_location(mr_id)
            
            # Broadcast to WebSocket connections
            await manager.send_location_update(mr_id, {
                "type": "location_update",
                "mr_id": mr_id,
                "data": location_data
            })
            
            # Log to sheets (async)
            try:
                # TODO: Implement async sheet logging
                pass
            except Exception as e:
                logger.error(f"Failed to log to sheets: {e}")
            
            return {
                "success": True,
                "message": "Location updated successfully",
                "data": location_data,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update location")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Location update failed: {str(e)}")

@app.get("/api/location/live/{mr_id}")
async def get_live_location(
    mr_id: int,
    api_key: str = Depends(verify_api_key)
):
    """Get current live location with enhanced data"""
    try:
        location_data = session_manager.get_live_location(mr_id)
        
        return {
            "success": True,
            "mr_id": mr_id,
            "location": location_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get live location: {str(e)}")

@app.get("/api/location/trail/{mr_id}")
async def get_location_trail(
    mr_id: int,
    hours: Optional[int] = 8,
    api_key: str = Depends(verify_api_key)
):
    """Get location trail for specific time period"""
    try:
        trail = session_manager.get_location_trail(mr_id, hours)
        
        return {
            "success": True,
            "mr_id": mr_id,
            "trail": trail,
            "count": len(trail),
            "hours": hours,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get location trail: {str(e)}")

# ============= ANALYTICS & INSIGHTS =============

@app.get("/api/analytics/{mr_id}")
async def get_mr_analytics(
    mr_id: int,
    api_key: str = Depends(verify_api_key)
):
    """Get comprehensive MR analytics"""
    try:
        analytics = session_manager.get_mr_analytics(mr_id)
        
        return {
            "success": True,
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@app.get("/api/analytics/team/overview")
async def get_team_overview(api_key: str = Depends(verify_api_key)):
    """Get team-wide analytics overview"""
    try:
        authorized_ids = getattr(config, 'AUTHORIZED_MR_IDS', [])
        
        team_stats = {
            "total_mrs": len(authorized_ids),
            "active_today": 0,
            "total_distance": 0,
            "total_visits": 0,
            "coverage_areas": []
        }
        
        mr_details = []
        
        for mr_id in authorized_ids:
            analytics = session_manager.get_mr_analytics(mr_id)
            
            if analytics['session_active']:
                team_stats["active_today"] += 1
                
            team_stats["total_distance"] += analytics['today_stats']['distance_traveled']
            team_stats["total_visits"] += analytics['today_stats']['locations_visited']
            
            mr_details.append({
                "mr_id": mr_id,
                "name": f"MR {mr_id}",
                "status": "active" if analytics['session_active'] else "inactive",
                "stats": analytics['today_stats']
            })
        
        return {
            "success": True,
            "overview": team_stats,
            "mr_details": mr_details,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get team overview: {str(e)}")

# ============= WEBSOCKET ENDPOINTS =============

@app.websocket("/ws/{mr_id}")
async def websocket_endpoint(websocket: WebSocket, mr_id: int):
    """WebSocket endpoint for real-time location updates"""
    await manager.connect(websocket, mr_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))
            elif message.get("type") == "location_update":
                # Handle location updates from client
                await update_location_websocket(mr_id, message.get("data", {}))
                
    except WebSocketDisconnect:
        manager.disconnect(mr_id)

async def update_location_websocket(mr_id: int, location_data: dict):
    """Handle location updates from WebSocket"""
    try:
        success = session_manager.update_live_location(
            mr_id,
            location_data.get('lat', 0),
            location_data.get('lon', 0),
            location_data.get('address', ''),
            location_data.get('accuracy', 0),
            location_data.get('speed', 0),
            location_data.get('heading', 0)
        )
        
        if success:
            updated_data = session_manager.get_live_location(mr_id)
            await manager.broadcast_to_all({
                "type": "location_broadcast",
                "mr_id": mr_id,
                "data": updated_data
            })
            
    except Exception as e:
        logger.error(f"WebSocket location update failed: {e}")

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
        
        if date == today:
            # Get today's trail from live tracking
            live_trail = session_manager.get_location_trail(mr_id, 24)
            
            # Convert to route format
            route_points = []
            for i, point in enumerate(live_trail):
                route_points.append({
                    "time": datetime.fromisoformat(point['timestamp'].replace('Z', '')).strftime("%H:%M"),
                    "lat": point['lat'],
                    "lng": point['lon'],
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
        
        for i in range(1, len(points)):
            prev_point = points[i-1]
            curr_point = points[i]
            
            # Distance calculation
            distance = geodesic(
                (prev_point['lat'], prev_point['lng']),
                (curr_point['lat'], curr_point['lng'])
            ).kilometers
            total_distance += distance
            
            # Speed and accuracy data
            if 'speed' in curr_point:
                speeds.append(curr_point['speed'])
            if 'accuracy' in curr_point:
                accuracies.append(curr_point['accuracy'])
        
        # Count visits
        visits = len([p for p in points if p['type'] == 'visit'])
        
        # Calculate active hours
        if len(points) >= 2:
            start_time = datetime.fromisoformat(points[0]['timestamp'].replace('Z', ''))
            end_time = datetime.fromisoformat(points[-1]['timestamp'].replace('Z', ''))
            active_hours = (end_time - start_time).total_seconds() / 3600
        else:
            active_hours = 0
        
        return {
            "distance_km": round(total_distance, 2),
            "visits": visits,
            "expenses_total": 0,  # TODO: Extract from expense details
            "active_hours": round(active_hours, 2),
            "total_points": len(points),
            "avg_speed": round(sum(speeds) / len(speeds), 2) if speeds else 0,
            "max_speed": max(speeds) if speeds else 0,
            "accuracy_avg": round(sum(accuracies) / len(accuracies), 2) if accuracies else 0,
            "first_location": points[0]['location'] if points else None,
            "last_location": points[-1]['location'] if points else None
        }
        
    except Exception as e:
        logger.error(f"Error calculating enhanced stats: {e}")
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

# ============= ROUTE BLUEPRINT ENDPOINTS =============

@app.get("/api/v2/route-blueprint/{mr_id}")
async def get_route_blueprint(
    mr_id: str, 
    date: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Get route blueprint for MR's daily visits"""
    
    try:
        # Import here to avoid circular imports
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from visit_based_location_tracker import get_mr_route_blueprint
        
        blueprint = await get_mr_route_blueprint(mr_id, date)
        
        if not blueprint:
            return {
                "success": False,
                "message": f"No route blueprint found for MR {mr_id}",
                "data": None
            }
        
        return {
            "success": True,
            "message": "Route blueprint retrieved successfully",
            "data": blueprint,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting route blueprint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/location-history/{mr_id}")
async def get_location_history(
    mr_id: str,
    days: int = 7,
    api_key: str = Depends(verify_api_key)
):
    """Get MR location history for specified days"""
    
    try:
        from visit_based_location_tracker import get_mr_location_history
        
        history = await get_mr_location_history(mr_id, days)
        
        return {
            "success": True,
            "message": f"Location history retrieved for {days} days",
            "data": {
                "mr_id": mr_id,
                "days_requested": days,
                "history": history,
                "total_days": len(history)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting location history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/location-analytics/{mr_id}")
async def get_location_analytics(
    mr_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get comprehensive location analytics for MR"""
    
    try:
        from visit_based_location_tracker import get_mr_location_analytics
        
        analytics = await get_mr_location_analytics(mr_id)
        
        return {
            "success": True,
            "message": "Location analytics retrieved successfully",
            "data": {
                "mr_id": mr_id,
                "analytics": analytics,
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting location analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/team-routes")
async def get_team_route_overview(
    team_ids: str,  # Comma-separated MR IDs
    date: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Get route overview for entire team"""
    
    try:
        from visit_based_location_tracker import get_mr_route_blueprint
        
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        mr_list = [mr_id.strip() for mr_id in team_ids.split(',')]
        team_overview = []
        
        for mr_id in mr_list:
            blueprint = await get_mr_route_blueprint(mr_id, date)
            
            if blueprint:
                team_overview.append({
                    "mr_id": mr_id,
                    "total_visits": blueprint["total_visits"],
                    "total_distance": blueprint["total_distance"],
                    "route_efficiency": blueprint["route_efficiency"],
                    "coverage_areas": blueprint["coverage_areas"],
                    "status": "active"
                })
            else:
                team_overview.append({
                    "mr_id": mr_id,
                    "total_visits": 0,
                    "total_distance": 0,
                    "route_efficiency": 0,
                    "coverage_areas": [],
                    "status": "no_data"
                })
        
        return {
            "success": True,
            "message": f"Team overview retrieved for {len(mr_list)} MRs",
            "data": {
                "date": date,
                "team_performance": team_overview,
                "summary": {
                    "total_mr_active": len([mr for mr in team_overview if mr["status"] == "active"]),
                    "total_visits": sum(mr["total_visits"] for mr in team_overview),
                    "total_distance": sum(mr["total_distance"] for mr in team_overview),
                    "avg_efficiency": sum(mr["route_efficiency"] for mr in team_overview) / len(team_overview)
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting team route overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/route-map/{mr_id}")
async def get_route_map_data(
    mr_id: str,
    date: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Get route map visualization data"""
    
    try:
        from dashboard_route_blueprint import generate_route_map_data
        from visit_based_location_tracker import get_mr_route_blueprint
        
        blueprint = await get_mr_route_blueprint(mr_id, date)
        map_data = generate_route_map_data(blueprint)
        
        return {
            "success": True,
            "message": "Route map data retrieved successfully",
            "data": map_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting route map data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        reload=True
    )
