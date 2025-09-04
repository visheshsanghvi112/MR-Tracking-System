from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import os
from datetime import datetime, timedelta
from typing import List, Optional
import json

app = FastAPI(
    title="MR Tracking API",
    description="Real-time location tracking and route visualization API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://*.vercel.app",   # Vercel deployments
        "*"  # Allow all for now
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Simple API key authentication
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Simple API key verification"""
    expected_key = os.getenv("API_KEY", "mr-tracking-2025")
    # Skip auth for development
    # if x_api_key != expected_key:
    #     raise HTTPException(status_code=401, detail="Invalid API key")
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
    return {
        "status": "healthy",
        "sheets_connected": True,
        "session_manager": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/mrs")
async def get_mr_list(api_key: str = Depends(verify_api_key)):
    """Get list of authorized MRs"""
    try:
        # Sample MR data
        mr_list = [
            {"id": 1201911108, "name": "Vishesh Sanghvi", "status": "active"},
            {"id": 987654321, "name": "John Doe", "status": "active"},
            {"id": 123456789, "name": "Jane Smith", "status": "active"}
        ]
        
        return {
            "success": True,
            "mrs": mr_list,
            "count": len(mr_list)
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
        
        # Sample route data - you'll replace this with actual Sheets integration
        sample_points = [
            {
                "time": "09:00",
                "lat": 19.0760,
                "lng": 72.8777,
                "type": "start",
                "location": "Home - Bandra West",
                "details": "Field session started - Ready for doctor visits",
                "timestamp": f"{date}T09:00:00"
            },
            {
                "time": "09:15",
                "lat": 19.0785,
                "lng": 72.8795,
                "type": "movement",
                "location": "En Route",
                "details": "Moving towards first appointment",
                "timestamp": f"{date}T09:15:00"
            },
            {
                "time": "09:30",
                "lat": 19.0820,
                "lng": 72.8850,
                "type": "visit",
                "location": "Dr. Sharma Clinic - Khar",
                "details": "Doctor visit completed - Discussed new cardiac medications",
                "timestamp": f"{date}T09:30:00"
            },
            {
                "time": "09:45",
                "lat": 19.0825,
                "lng": 72.8855,
                "type": "movement",
                "location": "Leaving Clinic",
                "details": "Heading to next appointment",
                "timestamp": f"{date}T09:45:00"
            },
            {
                "time": "10:00",
                "lat": 19.0880,
                "lng": 72.8900,
                "type": "visit",
                "location": "Apollo Pharmacy - Santacruz",
                "details": "Pharmacy visit - Stock check and order placement",
                "timestamp": f"{date}T10:00:00"
            },
            {
                "time": "10:30",
                "lat": 19.0885,
                "lng": 72.8905,
                "type": "expense",
                "location": "Near Apollo Pharmacy",
                "details": "Travel expense logged - ₹120 for auto fare",
                "timestamp": f"{date}T10:30:00"
            },
            {
                "time": "11:00",
                "lat": 19.0920,
                "lng": 72.8950,
                "type": "visit",
                "location": "Lilavati Hospital - Bandra",
                "details": "Hospital visit - Meeting with procurement team",
                "timestamp": f"{date}T11:00:00"
            },
            {
                "time": "11:45",
                "lat": 19.0925,
                "lng": 72.8955,
                "type": "movement",
                "location": "Hospital Exit",
                "details": "Completed hospital visit, moving to next location",
                "timestamp": f"{date}T11:45:00"
            },
            {
                "time": "12:15",
                "lat": 19.0960,
                "lng": 72.9000,
                "type": "current",
                "location": "Dr. Patel Clinic - Kurla",
                "details": "Currently at location - In progress visit",
                "timestamp": f"{date}T12:15:00"
            }
        ]
        
        # Calculate route statistics
        stats = {
            "distance_km": 8.5,
            "visits": len([p for p in sample_points if p['type'] == 'visit']),
            "expenses_total": 120,
            "active_hours": 3.25,
            "total_points": len(sample_points),
            "first_location": sample_points[0]['location'] if sample_points else None,
            "last_location": sample_points[-1]['location'] if sample_points else None
        }
        
        return {
            "success": True,
            "mr_id": mr_id,
            "date": date,
            "points": sample_points,
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
        # Sample live data
        if mr_id == 1201911108:
            return {
                "success": True,
                "live": True,
                "mr_id": mr_id,
                "location": {
                    "lat": 19.0960,
                    "lng": 72.9000,
                    "address": "Dr. Patel Clinic - Kurla",
                    "time_remaining": 1800,  # 30 minutes
                    "entries_count": 6,
                    "session_started": "2025-09-04T09:00:00",
                    "last_activity": "2025-09-04T12:15:00"
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
        # Get route data (reuse the sample data)
        route_response = await get_route_data(mr_id, date, api_key)
        location_points = route_response["points"]
        
        # Generate GPX content
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
        for point in location_points:
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
        
        gpx_content = gpx_header + gpx_points + gpx_footer
        
        return Response(
            content=gpx_content,
            media_type="application/gpx+xml",
            headers={"Content-Disposition": f"attachment; filename=mr_{mr_id}_{date}.gpx"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export GPX: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting MR Tracking API Server...")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("🗺️ Frontend: http://localhost:3000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
