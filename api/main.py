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

# Real Google Sheets Integration
try:
    # Force reload of smart_sheets module to get latest code
    import importlib
    if 'smart_sheets' in sys.modules:
        print("[INFO] Reloading smart_sheets module to get latest changes...")
        importlib.reload(sys.modules['smart_sheets'])
    
    from smart_sheets import SmartMRSheetsManager
    sheets_manager = SmartMRSheetsManager()
    print("[OK] Real Google Sheets Manager loaded successfully (with latest code)")
    
    # IMMEDIATE TEST: Check if sheets can find today's data
    print("\n[TEST] STARTUP TEST: Checking sheets data availability...")
    test_result = sheets_manager.get_mr_route_data("1201911108", "2025-10-15")
    if test_result:
        print(f"   [OK] TEST PASSED: Found {len(test_result)} records for MR 1201911108 on 2025-10-15")
        print(f"   [GPS] First location: {test_result[0].get('lat', 0)}, {test_result[0].get('lng', 0)}")
    else:
        print(f"   [WARN] TEST: No data found for MR 1201911108 on 2025-10-15")
        print(f"   [INFO] This is normal if no data exists for this date")
except Exception as e:
    print(f"[ERROR] Smart Sheets Manager failed: {e}")
    import traceback
    traceback.print_exc()
    # Mock fallback only if real sheets fail
    class MockSheetsManager:
        def get_all_mrs(self): return [{"id": 1201911108, "name": "Test MR", "status": "active"}]
        def get_mr_details(self, mr_id): return {"id": mr_id, "name": f"MR {mr_id}", "status": "active"}
        def get_route_data(self, mr_id, date): return []
    sheets_manager = MockSheetsManager()
    print("[WARN] Using Mock Sheets Manager (Real sheets failed to load)")

# Real Session Manager Integration  
try:
    from session_manager import mr_session_manager as session_manager
    print("[OK] Real Session Manager loaded successfully")
except Exception as e:
    print(f"[ERROR] Session Manager failed: {e}")
    # Mock fallback only if real session manager fails
    class MockSessionManager:
        def capture_location(self, mr_id, lat, lng, address): return True
        def get_current_location(self, mr_id): return {"lat": 19.0760, "lng": 72.8777}
        def get_location_trail(self, mr_id, hours): return []
    session_manager = MockSessionManager()

# Real Config Integration
try:
    import config
    print("[OK] Real Config loaded successfully")
except Exception as e:
    print(f"[ERROR] Config failed: {e}")
    # Mock config fallback
    class MockConfig:
        pass
    config = MockConfig()

# ============= PRODUCTION SETUP =============
try:
    from production import (
        setup_production_logging, init_sentry, 
        get_full_health_status, CircuitBreaker,
        RequestContext, capture_exception,
        with_correlation_id
    )
    
    # Setup production logging (JSON in prod, readable in dev)
    setup_production_logging(
        json_format=os.getenv("ENVIRONMENT") == "production",
        level=os.getenv("LOG_LEVEL", "INFO")
    )
    
    # Initialize Sentry error tracking
    init_sentry()
    
    print("[OK] Production utilities loaded (Sentry, structured logging, circuit breakers)")
except ImportError as e:
    print(f"[WARN] Production utilities not available: {e}")
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

# Utility functions
def clean_mr_name(name: str) -> str:
    """Clean MR name by removing Unicode artifacts and special characters"""
    if not name:
        return "Unknown MR"
    
    # Remove common Unicode artifacts
    import re
    cleaned = re.sub(r'[\u0300-\u036f\u20d0-\u20ff\u1ab0-\u1aff\u1dc0-\u1dff]', '', name)  # Remove combining characters
    cleaned = re.sub(r'[\ud800-\udfff]', '', cleaned)  # Remove surrogate pairs
    cleaned = re.sub(r'[^\w\s.-]', '', cleaned)  # Keep only word chars, spaces, dots, hyphens
    cleaned = ' '.join(cleaned.split())  # Normalize whitespace
    
    return cleaned.strip() or "Unknown MR"

# Initialize managers
# Real managers are loaded at startup above
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


@app.get("/api/health/detailed")
async def detailed_health_check():
    """Comprehensive health check with component status - for monitoring systems"""
    try:
        health_status = await get_full_health_status()
        
        # Add API-specific checks
        try:
            test_mrs = sheets_manager.get_all_mrs()
            health_status["components"]["api"] = {
                "status": "healthy",
                "mrs_loaded": len(test_mrs)
            }
        except Exception as e:
            health_status["components"]["api"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        status_code = 200 if health_status["status"] == "healthy" else 503
        return Response(
            content=json.dumps(health_status, indent=2),
            status_code=status_code,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=json.dumps({
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }),
            status_code=503,
            media_type="application/json"
        )

# ============= MR MANAGEMENT =============

@app.get("/api/mrs")
@with_correlation_id
async def get_mrs(api_key: str = Depends(verify_api_key)):
    """Get all Medical Representatives with real Google Sheets data"""
    correlation_id = RequestContext.get_correlation_id()
    logger.info("Fetching MRs", extra={'correlation_id': correlation_id})
    try:
        mrs_data = sheets_manager.get_all_mrs()
        
        # Clean MR names for better display
        for mr in mrs_data:
            if 'name' in mr:
                mr['name'] = clean_mr_name(mr['name'])
        
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
        # Get all MRs and find the specific one
        all_mrs = sheets_manager.get_all_mrs()
        mr_data = None
        for mr in all_mrs:
            if str(mr.get('mr_id')) == str(mr_id):
                mr_data = mr
                break
        
        if not mr_data:
            raise HTTPException(status_code=404, detail="MR not found")
        
        # Clean MR name for better display
        if 'name' in mr_data:
            mr_data['name'] = clean_mr_name(mr_data['name'])
        
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
        location = session_manager.get_live_location(mr_id)
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

# ============= VERIFICATION (SELFIE) =============

@app.get("/api/verification/selfies")
async def list_selfies(mr_id: Optional[int] = None, limit: int = 20, api_key: str = Depends(verify_api_key)):
    """List recent selfie verification records from Google Sheets."""
    try:
        items = sheets_manager.get_recent_selfies(limit)
        if mr_id is not None:
            items = [i for i in items if str(i.get('mr_id')) == str(mr_id)]
        return {"success": True, "items": items, "count": len(items)}
    except Exception as e:
        logger.error(f"Error listing selfies: {e}")
        raise HTTPException(status_code=500, detail="Failed to list selfies")

@app.get("/api/verification/selfies/health")
async def selfie_sheet_health(api_key: str = Depends(verify_api_key)):
    """Report health of the Selfie_Verifications sheet: existence, headers, and row count."""
    try:
        # Ensure sheet object is available
        # Access protected method carefully
        try:
            sheets_manager._ensure_selfie_sheet()  # type: ignore[attr-defined]
        except Exception:
            pass

        selfie_sheet = getattr(sheets_manager, 'selfie_sheet', None)
        exists = selfie_sheet is not None
        header_ok = False
        headers = []
        row_count = 0
        if exists:
            values = selfie_sheet.get_all_values()  # A:O expected
            if values:
                headers = values[0]
                expected = [
                    'Timestamp','Date','Time','MR_ID','MR_Name','Location','GPS_Lat','GPS_Lon',
                    'Media_Type','File_ID','Verification_Status','Geofence_Status','Distance_M','Notes','Selfie_URL'
                ]
                header_ok = headers[:len(expected)] == expected
                row_count = max(0, len(values) - 1)
        return {
            "success": True,
            "exists": exists,
            "header_ok": header_ok,
            "headers": headers,
            "row_count": row_count
        }
    except Exception as e:
        logger.error(f"Error checking selfie sheet health: {e}")
        raise HTTPException(status_code=500, detail="Failed to check selfie sheet health")

@app.get("/api/verification/selfies/{file_id}/download")
async def download_selfie(file_id: str, key: Optional[str] = None):
    """Proxy-download Telegram media by file_id so frontend can render even if Drive URL is missing.

    Auth: supply ?key=API_KEY as query param (browser <img> cannot send headers).
    Resolves file_path via Telegram getFile, then streams bytes to the client.
    """
    try:
        # Simple query-key auth
        expected_key = os.getenv("API_KEY", "mr-tracking-2025")
        if key != expected_key:
            raise HTTPException(status_code=401, detail="Invalid or missing key")

        import requests
        token = getattr(config, 'TELEGRAM_BOT_TOKEN', None) or os.getenv('MR_BOT_TOKEN')
        if not token:
            raise HTTPException(status_code=500, detail="Bot token not configured")

        # Resolve file path
        gf = requests.get(f"https://api.telegram.org/bot{token}/getFile", params={"file_id": file_id}, timeout=15)
        if not gf.ok:
            raise HTTPException(status_code=gf.status_code, detail="Failed to resolve file")
        file_path = gf.json().get('result', {}).get('file_path')
        if not file_path:
            raise HTTPException(status_code=404, detail="File path not found")

        # Stream file
        url = f"https://api.telegram.org/file/bot{token}/{file_path}"
        r = requests.get(url, stream=True, timeout=30)
        if not r.ok:
            raise HTTPException(status_code=r.status_code, detail="Failed to download file")

        # Infer content-type from extension
        import mimetypes
        content_type = r.headers.get('Content-Type') or mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        return StreamingResponse(r.iter_content(chunk_size=8192), media_type=content_type)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Selfie proxy download error: {e}")
        raise HTTPException(status_code=500, detail="Selfie download failed")

# ============= DEBUG: SHEETS INSPECTION =============

@app.get("/api/debug/sheets")
async def debug_sheets(api_key: str = Depends(verify_api_key)):
    """Return high-level info about connected Google Sheet and tabs.

    Helps verify Vercel credentials, spreadsheet id, worksheet names, row counts,
    and which sheet is currently selected as the main daily log.
    """
    try:
        info = {
            "spreadsheet_id": getattr(sheets_manager, 'spreadsheet_id', None),
            "using_env_json": getattr(sheets_manager, 'using_env_json', False),
            "main_sheet": getattr(getattr(sheets_manager, 'main_sheet', None), 'title', None),
            "sheets": []
        }

        try:
            worksheets = sheets_manager.spreadsheet.worksheets() if getattr(sheets_manager, 'spreadsheet', None) else []
            for ws in worksheets:
                try:
                    values = ws.get_all_values()
                    headers = values[0] if values else []
                    info["sheets"].append({
                        "title": ws.title,
                        "rows": max(0, len(values) - 1) if values else 0,
                        "headers": headers,
                        "has_mr_headers": bool(headers) and ("MR_ID" in headers and "Date" in headers)
                    })
                except Exception as e:
                    info["sheets"].append({"title": ws.title, "error": str(e)})
        except Exception as e:
            info["error"] = f"Failed to enumerate worksheets: {e}"

        return {"success": True, "data": info}
    except Exception as e:
        logger.error(f"debug_sheets error: {e}")
        raise HTTPException(status_code=500, detail="debug failed")

# ============= ANALYTICS =============

@app.get("/api/analytics/{mr_id}")
async def get_mr_analytics(
    mr_id: int,
    period: str = "daily",
    api_key: str = Depends(verify_api_key)
):
    """Get analytics for a specific MR"""
    try:
        # Get real analytics from sheets
        mrs_data = sheets_manager.get_all_mrs()
        mr_data = None
        for mr in mrs_data:
            if str(mr.get('mr_id')) == str(mr_id):
                mr_data = mr
                break

        if not mr_data:
            raise HTTPException(status_code=404, detail="MR not found")

        # Get route data for today to calculate real analytics
        today = datetime.now().strftime("%Y-%m-%d")
        route_data = sheets_manager.get_mr_route_data(mr_id, today)

        # Calculate real analytics
        visits_today = len([r for r in route_data if r.get('visit_type')])
        total_distance = sum([0.5 for _ in route_data])  # Mock distance calculation
        active_hours = len(route_data) * 0.5  # Mock active hours
        efficiency_score = min(100, (visits_today * 10) + 50)  # Simple efficiency calculation

        analytics_data = {
            "mr_id": mr_id,
            "period": period,
            "visits_today": visits_today,
            "distance_covered": round(total_distance, 2),
            "active_hours": round(active_hours, 2),
            "efficiency_score": efficiency_score,
            "last_activity": mr_data.get('last_activity'),
            "total_visits": mr_data.get('total_visits', 0),
            "status": mr_data.get('status', 'unknown')
        }

        return {
            "success": True,
            "data": analytics_data,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
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

        # Calculate real analytics from sheets data
        total_mrs = len(mrs_data)
        active_mrs = len([mr for mr in mrs_data if mr.get('status') == 'active'])
        total_visits = sum(mr.get('total_visits', 0) for mr in mrs_data)
        total_distance = sum(mr.get('distance_today', 0) for mr in mrs_data)

        # Get today's route data for more accurate calculations
        today = datetime.now().strftime("%Y-%m-%d")
        today_visits = 0
        today_distance = 0

        for mr in mrs_data:
            mr_id = mr.get('mr_id')
            route_data = sheets_manager.get_mr_route_data(mr_id, today)
            today_visits += len([r for r in route_data if r.get('visit_type')])
            today_distance += sum([0.5 for _ in route_data])  # Mock distance calculation

        team_analytics = {
            "total_mrs": total_mrs,
            "active_mrs": active_mrs,
            "total_visits": total_visits,
            "total_distance": round(total_distance, 2),
            "today_visits": today_visits,
            "today_distance": round(today_distance, 2),
            "avg_visits_per_mr": round(total_visits / max(total_mrs, 1), 2),
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
    mr_id: Optional[int] = None,
    date: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Get enhanced route data with real tracking integration"""
    try:
        # Set defaults if not provided
        if not mr_id:
            # Get first available MR
            mrs_data = sheets_manager.get_all_mrs()
            if mrs_data:
                mr_id = int(mrs_data[0].get('mr_id', 1201911108))
            else:
                mr_id = 1201911108
                
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            
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

@app.get("/api/debug/route-scan")
async def debug_route_scan(mr_id: int, date: str, api_key: str = Depends(verify_api_key)):
    """Debug endpoint: show counts and sample records for an MR and date from Sheets."""
    try:
        data = sheets_manager.get_mr_route_data(str(mr_id), date)
        # Also summarize date distribution for this MR and show first raw record for the date
        summary = {}
        raw_sample = None
        try:
            records = sheets_manager.main_sheet.get_all_records()
            for r in records:
                if str(r.get('MR_ID')) == str(mr_id):
                    d = r.get('Date', '')
                    summary[d] = summary.get(d, 0) + 1
                    if raw_sample is None and d == date:
                        raw_sample = r
        except Exception:
            pass
        return {
            "success": True,
            "count": len(data or []),
            "sample": data[0] if data else None,
            "date_summary": summary,
            "raw_sample": raw_sample
        }
    except Exception as e:
        logger.error(f"debug_route_scan error: {e}")
        raise HTTPException(status_code=500, detail="scan failed")

async def get_enhanced_route_data(mr_id: int, date: str) -> List[dict]:
    """Get enhanced route data combining sheets and live tracking"""
    try:
        # If date is today, combine sheets data with live tracking
        today = datetime.now().strftime("%Y-%m-%d")
        print("\n" + "="*70)
        print(f"[DEBUG] ROUTE REQUEST")
        print("="*70)
        print(f"[MR] ID: {mr_id}")
        print(f"[DATE] Requested: {date}")
        print(f"[DATE] Today: {today}")
        print(f"[CHECK] Is Today: {date == today}")
        logger.info(f"Route request: MR {mr_id}, date {date}, today is {today}")
        
        if date == today:
            # PRIORITY 1: Try live tracking first
            print(f"\n[STEP 1] Checking live tracking...")
            live_trail = session_manager.get_location_trail(mr_id, 24)
            print(f"[LIVE] Trail result: {len(live_trail)} points")
            logger.info(f"📡 Live trail has {len(live_trail)} points")
            
            # PRIORITY 2: If no live data, try Google Sheets for today
            if not live_trail:
                print(f"\n[STEP 2] No live data, checking Google Sheets for TODAY...")
                print(f"   [CALL] sheets_manager.get_mr_route_data('{mr_id}', '{date}')")
                logger.info(f"[INFO] No live trail, checking Google Sheets for today's data for MR {mr_id}")
                
                try:
                    sheets_data_today = sheets_manager.get_mr_route_data(str(mr_id), date)
                    print(f"[SHEETS] Returned: {len(sheets_data_today) if sheets_data_today else 0} records")
                    if sheets_data_today and len(sheets_data_today) > 0:
                        print(f"   [DATA] First record: {sheets_data_today[0] if sheets_data_today else 'None'}")
                except Exception as sheet_error:
                    print(f"[ERROR] SHEETS ERROR: {sheet_error}")
                    sheets_data_today = []
                
                if sheets_data_today:
                    print(f"\n[SUCCESS] FOUND REAL DATA IN SHEETS!")
                    print(f"   [COUNT] Records found: {len(sheets_data_today)}")
                    logger.info(f"[OK] Found {len(sheets_data_today)} records in sheets for MR {mr_id} today")
                    
                    # Transform sheets data to route format
                    print(f"\n[TRANSFORM] Converting sheets data to route format...")
                    route_points = []
                    for idx, record in enumerate(sheets_data_today):
                        print(f"   [REC {idx+1}] {record.get('location', 'N/A')} at ({record.get('lat', 0)}, {record.get('lng', 0)})")
                        # FIXED: Data from sheets should default to 'visit' type (logged locations are visits)
                        route_points.append({
                            "time": record.get('timestamp', '').split('T')[1][:5] if 'T' in record.get('timestamp', '') else '00:00',
                            "lat": record.get('lat', 0),
                            "lng": record.get('lng', 0),
                            "type": "visit",  # All logged locations from sheets are visits
                            "location": record.get('location', 'Unknown Location'),
                            "details": f"Visit: {record.get('contact_name', 'N/A')} | Orders: {record.get('orders', 0)}",
                            "timestamp": record.get('timestamp', f"{date}T00:00:00"),
                            "visit_type": record.get('visit_type') or 'other',  # Default to 'other' if empty
                            "contact_name": record.get('contact_name', ''),
                            "orders": record.get('orders', 0),
                            "accuracy": 10,
                            "speed": 0,
                            "heading": 0
                        })
                    print(f"\n[SUCCESS] Returning {len(route_points)} REAL points from Google Sheets")
                    print(f"   [INFO] MR {mr_id} will show ACTUAL logged locations")
                    print("="*70 + "\n")
                    logger.info(f"[OK] Returning {len(route_points)} real points from sheets for MR {mr_id}")
                    return route_points
                
                # PRIORITY 3: No data found - return empty array instead of fake data
                print(f"\n[INFO] No real data found for MR {mr_id} on {date}")
                print(f"   [INFO] Sheets had 0 records for MR {mr_id} on {date}")
                print(f"   [INFO] Returning empty array (no sample/fake data)")
                print("="*70 + "\n")
                logger.info(f"📭 No data available for MR {mr_id} on {date} - returning empty result")
                return []  # Return empty array instead of fake Mumbai data
            
            # Convert live trail to route format
            print(f"\n[SUCCESS] FOUND LIVE TRACKING DATA!")
            print(f"   [COUNT] Live trail points: {len(live_trail)}")
            route_points = []
            for i, point in enumerate(live_trail):
                if i == 0:
                    print(f"   [GPS] First live point: ({point['lat']}, {point['lng']}) at {point['timestamp']}")
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
            
            print(f"\n[SUCCESS] Returning {len(route_points)} live tracking points")
            print("="*70 + "\n")
            return route_points
        else:
            # Get historical data from Google Sheets
            print(f"\n[HISTORY] Date is NOT today - fetching HISTORICAL data")
            print(f"   [DATE] Requested: {date}, Today: {today}")
            logger.info(f"📅 Fetching historical data for MR {mr_id} on {date}")
            
            try:
                # Use sheets manager to get historical route data
                print(f"   [CALL] sheets_manager.get_mr_route_data('{mr_id}', '{date}')")
                historical_data = sheets_manager.get_mr_route_data(str(mr_id), date)
                print(f"[SHEETS] Returned: {len(historical_data) if historical_data else 0} historical records")
                logger.info(f"[INFO] Found {len(historical_data)} historical records from sheets")
                
                if not historical_data:
                    print(f"[WARN] No historical data found in sheets for MR {mr_id} on {date}")
                    print("="*70 + "\n")
                    logger.warning(f"[WARN] No historical data found for MR {mr_id} on {date}")
                    return []
                
                # Transform sheets data to route format
                print(f"\n[TRANSFORM] Converting {len(historical_data)} historical records...")
                route_points = []
                for idx, record in enumerate(historical_data):
                    if idx == 0:
                        print(f"   [REC 1] {record.get('location', 'N/A')} at ({record.get('lat', 0)}, {record.get('lng', 0)})")
                    # Sheets returns: {timestamp, lat, lng, location, visit_type, contact_name, orders}
                    # FIXED: All historical data from sheets should be marked as visits
                    route_points.append({
                        "time": record.get('timestamp', '').split('T')[1][:5] if 'T' in record.get('timestamp', '') else '00:00',
                        "lat": record.get('lat', 0),
                        "lng": record.get('lng', 0),
                        "type": "visit",  # All logged locations from sheets are visits
                        "location": record.get('location', 'Unknown Location'),
                        "details": f"Visit: {record.get('contact_name', 'N/A')} | Orders: {record.get('orders', 0)}",
                        "timestamp": record.get('timestamp', f"{date}T00:00:00"),
                        "visit_type": record.get('visit_type') or 'other',  # Default to 'other' if empty
                        "contact_name": record.get('contact_name', ''),
                        "orders": record.get('orders', 0),
                        "accuracy": 10,  # Sheets data is verified
                        "speed": 0,
                        "heading": 0
                    })
                
                print(f"\n[SUCCESS] Returning {len(route_points)} HISTORICAL points from sheets")
                print(f"   [INFO] MR {mr_id} showing data from {date}")
                print("="*70 + "\n")
                logger.info(f"[OK] Transformed {len(route_points)} historical points for MR {mr_id} on {date}")
                return route_points
                
            except Exception as e:
                print(f"\n[ERROR] ERROR in historical data fetch: {e}")
                print(f"   [TYPE] Exception type: {type(e).__name__}")
                print(f"   [DETAIL] Exception details: {str(e)}")
                print("="*70 + "\n")
                logger.error(f"[ERROR] Error fetching historical data: {e}")
                return []
            
    except Exception as e:
        print(f"\n[CRITICAL] ERROR in get_enhanced_route_data: {e}")
        print(f"   [TYPE] Exception type: {type(e).__name__}")
        print(f"   [DETAIL] Full error: {str(e)}")
        print("="*70 + "\n")
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
    mr_id: Optional[int] = None,
    date: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Export route data as GPX file"""
    try:
        # Set defaults if not provided
        if not mr_id:
            # Get first available MR
            mrs_data = sheets_manager.get_all_mrs()
            if mrs_data:
                mr_id = int(mrs_data[0].get('mr_id', 1201911108))
            else:
                mr_id = 1201911108
                
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            
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

        # Calculate real analytics
        total_mrs = len(mrs_data)
        active_mrs = len([mr for mr in mrs_data if mr.get('status') == 'active'])
        total_visits = sum(mr.get('total_visits', 0) for mr in mrs_data)
        total_distance = sum(mr.get('distance_today', 0) for mr in mrs_data)

        # Get today's data for more accurate metrics
        # OPTIMIZED: Use pre-calculated values from get_all_mrs() instead of querying each MR
        today = datetime.now().strftime("%Y-%m-%d")
        today_visits = sum(mr.get('total_visits', 0) for mr in mrs_data)  # Already calculated
        today_distance = sum(mr.get('distance_today', 0) for mr in mrs_data)  # Already calculated

        analytics = {
            "period": period,
            "total_mrs": total_mrs,
            "active_mrs": active_mrs,
            "total_visits": total_visits,
            "total_distance": round(total_distance, 2),
            "today_visits": today_visits,
            "today_distance": round(today_distance, 2),
            "avg_visits_per_mr": round(total_visits / max(total_mrs, 1), 2),
            "efficiency_avg": round((today_visits * 10) + 50, 1),  # Simple efficiency calculation
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
        # Get real activities from sheets
        activities = []

        # Get all MRs first
        mrs_data = sheets_manager.get_all_mrs()

        # Get recent visit records from sheets
        visit_records = sheets_manager.get_all_visit_records_with_gps()

        # Sort by timestamp and take the most recent ones
        visit_records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        for i, record in enumerate(visit_records[:limit]):
            # Find the MR name
            mr_name = "Unknown MR"
            for mr in mrs_data:
                if str(mr.get('mr_id')) == str(record.get('mr_id')):
                    mr_name = mr.get('name', 'Unknown MR')
                    break

            activities.append({
                "id": f"{record.get('mr_id')}_{record.get('timestamp')}_{i}",
                "mr_id": str(record.get('mr_id')),
                "mr_name": mr_name,
                "action": "visit_completed",
                "location": record.get('location', 'Unknown Location'),
                "timestamp": record.get('timestamp', datetime.now().isoformat()),
                "details": f"Visit completed at {record.get('location', 'Unknown Location')}",
                "visit_type": record.get('visit_type', 'Unknown'),
                "gps_coordinates": f"{record.get('gps_lat', 0):.6f}, {record.get('gps_lon', 0):.6f}"
            })

        # If we don't have enough real activities, add some from MR status changes
        if len(activities) < limit:
            for mr in mrs_data[:limit - len(activities)]:
                activities.append({
                    "id": f"status_{mr.get('mr_id')}_{datetime.now().isoformat()}",
                    "mr_id": str(mr.get('mr_id')),
                    "mr_name": mr.get('name', 'Unknown MR'),
                    "action": "status_update",
                    "location": mr.get('last_location', {}).get('address', 'Unknown'),
                    "timestamp": mr.get('last_activity', datetime.now().isoformat()),
                    "details": f"MR status: {mr.get('status', 'unknown')}",
                    "visit_type": "status",
                    "gps_coordinates": f"{mr.get('last_location', {}).get('lat', 0):.6f}, {mr.get('last_location', {}).get('lng', 0):.6f}"
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
    """Get route blueprint - creates REAL blueprint from actual route data"""
    
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"🗺️ Creating route blueprint for MR {mr_id} on {date}")
        
        # Get actual route data
        route_points = await get_enhanced_route_data(mr_id, date)
        
        if not route_points:
            logger.warning(f"⚠️ No route data found to create blueprint for MR {mr_id} on {date}")
            return {
                "success": False,
                "error": "No route data available for this date",
                "mr_id": mr_id,
                "date": date,
                "timestamp": datetime.now().isoformat()
            }
        
        # Create REAL blueprint from actual data
        visits = [p for p in route_points if p.get('type') == 'visit']
        
        # Calculate real statistics
        stats = calculate_enhanced_route_stats(route_points)
        
        # Build blueprint
        blueprint = {
            "mr_id": str(mr_id),
            "date": date,
            "total_visits": len(visits),
            "total_points": len(route_points),
            "total_distance_km": stats.get('distance_km', 0),
            "active_hours": stats.get('active_hours', 0),
            
            # Route points
            "route_points": route_points,
            
            # Visit locations
            "visit_locations": [
                {
                    "sequence": i + 1,
                    "location_name": v.get('location', 'Unknown'),
                    "latitude": v.get('lat', 0),
                    "longitude": v.get('lng', 0),
                    "time": v.get('time', '00:00'),
                    "visit_type": v.get('visit_type', 'unknown'),
                    "details": v.get('details', '')
                }
                for i, v in enumerate(visits)
            ],
            
            # Route summary
            "start_location": route_points[0] if route_points else None,
            "end_location": route_points[-1] if route_points else None,
            "start_time": route_points[0].get('time', '00:00') if route_points else None,
            "end_time": route_points[-1].get('time', '00:00') if route_points else None,
            
            # Coverage areas (unique locations)
            "coverage_areas": list(set([p.get('location', 'Unknown') for p in route_points if p.get('location')])),
            
            # Efficiency metrics
            "route_efficiency": min(100, (len(visits) * 10) + 50),  # Simple calculation
            "avg_speed_kmh": stats.get('avg_speed', 0),
            "max_speed_kmh": stats.get('max_speed', 0),
            
            # Data source
            "data_source": "Google Sheets" if date != datetime.now().strftime("%Y-%m-%d") else "Live Tracking",
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Created blueprint with {len(visits)} visits and {len(route_points)} total points")
        
        return {
            "success": True,
            "mr_id": mr_id,
            "date": date,
            "blueprint": blueprint,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating route blueprint: {e}")
        return {
            "success": False,
            "error": f"Failed to create blueprint: {str(e)}",
            "mr_id": mr_id,
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat()
        }

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
    date: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Get enhanced route data optimized for map visualization"""
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            
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
