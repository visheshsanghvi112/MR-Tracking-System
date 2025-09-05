from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional
import json
from geopy.distance import geodesic

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smart_sheets import SmartMRSheetsManager
from session_manager import MRSessionManager
import config

app = FastAPI(
    title="MR Tracking API",
    description="Real-time location tracking and route visualization API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default
        "http://localhost:8080",  # Vite frontend
        "http://localhost:5173",  # Vite alternative
        "https://*.vercel.app",   # Vercel deployments
        # Add your custom domain when ready
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize managers
sheets_manager = SmartMRSheetsManager()
session_manager = MRSessionManager()

# Simple API key authentication
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Simple API key verification"""
    expected_key = os.getenv("API_KEY", "mr-tracking-2025")
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "MR Tracking API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test sheets connection
        sheets_connected = sheets_manager.client is not None
        
        return {
            "status": "healthy",
            "sheets_connected": sheets_connected,
            "session_manager": "active",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/mrs")
async def get_mr_list(api_key: str = Depends(verify_api_key)):
    """Get list of MRs from Google Sheets"""
    try:
        # Get real MR data from Google Sheets
        mrs = sheets_manager.get_all_mrs()
        
        return {
            "success": True,
            "mrs": mrs,
            "count": len(mrs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get MR list: {str(e)}")

@app.get("/api/route")
async def get_route_data(
    mr_id: int,
    date: str,
    api_key: str = Depends(verify_api_key)
):
    """Get route data for specific MR and date"""
    try:
        # Validate date format
        try:
            route_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Get location data from sheets
        location_points = get_location_points_from_sheets(mr_id, date)
        
        # Calculate route statistics
        stats = calculate_route_stats(location_points)
        
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

@app.get("/api/live")
async def get_live_location(
    mr_id: int,
    api_key: str = Depends(verify_api_key)
):
    """Get current live location status for MR"""
    try:
        status = session_manager.get_location_status(mr_id)
        
        if status['active']:
            return {
                "success": True,
                "live": True,
                "mr_id": mr_id,
                "location": {
                    "lat": status.get('lat', 0),
                    "lng": status.get('lon', 0),
                    "address": status.get('address', ''),
                    "time_remaining": status.get('time_remaining', 0),
                    "entries_count": status.get('entries_count', 0),
                    "session_started": status.get('session_start', ''),
                    "last_activity": status.get('last_activity', '')
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": True,
                "live": False,
                "mr_id": mr_id,
                "message": "No active session",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get live location: {str(e)}")

@app.get("/api/export/gpx")
async def export_route_gpx(
    mr_id: int,
    date: str,
    api_key: str = Depends(verify_api_key)
):
    """Export route as GPX file"""
    try:
        # Get route data
        location_points = get_location_points_from_sheets(mr_id, date)
        
        # Generate GPX content
        gpx_content = generate_gpx_file(location_points, mr_id, date)
        
        return Response(
            content=gpx_content,
            media_type="application/gpx+xml",
            headers={"Content-Disposition": f"attachment; filename=mr_{mr_id}_{date}.gpx"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export GPX: {str(e)}")

def get_location_points_from_sheets(mr_id: int, date: str) -> List[dict]:
    """Extract location points from Google Sheets for specific MR and date"""
    try:
        # Get real route data from Google Sheets
        route_data = sheets_manager.get_mr_route_data(str(mr_id), date)
        
        # Convert to expected format
        location_points = []
        for point in route_data:
            location_points.append({
                "time": point['timestamp'].split(' ')[1] if ' ' in point['timestamp'] else point['timestamp'],
                "lat": point['lat'],
                "lng": point['lng'],
                "type": "visit" if point['visit_type'] else "movement",
                "location": point['contact_name'] if point['contact_name'] else "Location",
                "details": point['remarks'],
                "timestamp": point['timestamp'],
                "action": point['action'],
                "visit_type": point['visit_type']
            })
        
        return location_points
        
    except Exception as e:
        print(f"Error getting location points: {e}")
        return []

def calculate_route_stats(points: List[dict]) -> dict:
    """Calculate route statistics from location points"""
    try:
        if not points:
            return {
                "distance_km": 0,
                "visits": 0,
                "expenses_total": 0,
                "active_hours": 0,
                "total_points": 0
            }
        
        # Calculate total distance
        total_distance = 0
        for i in range(1, len(points)):
            prev_point = points[i-1]
            curr_point = points[i]
            
            distance = geodesic(
                (prev_point['lat'], prev_point['lng']),
                (curr_point['lat'], curr_point['lng'])
            ).kilometers
            
            total_distance += distance
        
        # Count visits and expenses
        visits = len([p for p in points if p['type'] == 'visit'])
        expenses = len([p for p in points if p['type'] == 'expense'])
        
        # Calculate active hours
        if len(points) >= 2:
            start_time = datetime.fromisoformat(points[0]['timestamp'])
            end_time = datetime.fromisoformat(points[-1]['timestamp'])
            active_hours = (end_time - start_time).total_seconds() / 3600
        else:
            active_hours = 0
        
        return {
            "distance_km": round(total_distance, 2),
            "visits": visits,
            "expenses_total": 0,  # TODO: Extract from expense details
            "active_hours": round(active_hours, 2),
            "total_points": len(points),
            "first_location": points[0]['location'] if points else None,
            "last_location": points[-1]['location'] if points else None
        }
        
    except Exception as e:
        print(f"Error calculating stats: {e}")
        return {
            "distance_km": 0,
            "visits": 0,
            "expenses_total": 0,
            "active_hours": 0,
            "total_points": 0
        }

def generate_gpx_file(points: List[dict], mr_id: int, date: str) -> str:
    """Generate GPX file content from location points"""
    gpx_header = f'''<?xml version="1.0"?>
<gpx version="1.1" creator="MR Tracking System" xmlns="http://www.topografix.com/GPX/1/1">
  <metadata>
    <name>MR {mr_id} Route - {date}</name>
    <desc>Medical Representative field tracking route</desc>
    <time>{date}T00:00:00Z</time>
  </metadata>
  <trk>
    <name>MR Route {date}</name>
    <trkseg>'''
    
    gpx_points = ""
    for point in points:
        gpx_points += f'''
      <trkpt lat="{point['lat']}" lon="{point['lng']}">
        <time>{point['timestamp']}:00Z</time>
        <name>{point['location']}</name>
        <desc>{point['details']}</desc>
        <type>{point['type']}</type>
      </trkpt>'''
    
    gpx_footer = '''
    </trkseg>
  </trk>
</gpx>'''
    
    return gpx_header + gpx_points + gpx_footer

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(api_key: str = Depends(verify_api_key)):
    """Get dashboard statistics from Google Sheets"""
    try:
        # Get real dashboard stats from Google Sheets
        stats = sheets_manager.get_dashboard_stats()
        
        if not stats:
            # Fallback if sheets are not available
            stats = {
                'total_mrs': 0,
                'active_today': 0,
                'live_sessions': 0,
                'avg_distance': 0,
                'total_visits': 0,
                'total_distance': 0
            }
        
        return {
            "success": True,
            "stats": stats,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")

@app.get("/api/activity")
async def get_activity_feed(api_key: str = Depends(verify_api_key)):
    """Get recent activity feed from Google Sheets"""
    try:
        # Get real activity feed from Google Sheets
        activities = sheets_manager.get_activity_feed(limit=20)
        
        return {
            "success": True,
            "activities": activities,
            "count": len(activities),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get activity feed: {str(e)}")
        
        return {
            "success": True,
            "activities": activities[:20],  # Return last 20 activities
            "count": len(activities[:20])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get activity feed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
