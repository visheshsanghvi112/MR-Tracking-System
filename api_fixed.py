#!/usr/bin/env python3
"""
Alternative API server with different configuration
"""
import os
import sys
from datetime import datetime

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_sheets import SmartMRSheetsManager
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MR Tracking API - Fixed",
    description="Real-time location tracking and route visualization API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:8081",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize sheets manager with error handling
try:
    logger.info("Initializing SmartMRSheetsManager...")
    sheets_manager = SmartMRSheetsManager()
    logger.info("SmartMRSheetsManager initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize SmartMRSheetsManager: {e}")
    sheets_manager = None

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
        "service": "MR Tracking API - Fixed",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "sheets_connected": sheets_manager is not None
    }

@app.get("/api/mrs")
async def get_mr_list(api_key: str = Depends(verify_api_key)):
    """Get list of MRs from Google Sheets"""
    try:
        logger.info("Processing /api/mrs request")
        
        if not sheets_manager:
            # Return fallback data if sheets not available
            mrs = [{
                "mr_id": "1201911108",
                "name": "Vishesh Sanghvi",
                "status": "active",
                "last_location": {"lat": 18.947962, "lng": 72.829974},
                "last_activity": "2025-09-03 14:37:15",
                "total_visits": 20
            }]
        else:
            # Get real data from sheets
            mrs = sheets_manager.get_all_mrs()
            logger.info(f"Retrieved {len(mrs)} MRs from sheets")
        
        return {
            "success": True,
            "mrs": mrs,
            "count": len(mrs)
        }
        
    except Exception as e:
        logger.error(f"Error in get_mr_list: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get MR list: {str(e)}")

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(api_key: str = Depends(verify_api_key)):
    """Get dashboard statistics from Google Sheets"""
    try:
        logger.info("Processing /api/dashboard/stats request")
        
        if not sheets_manager:
            stats = {
                'total_mrs': 1,
                'active_today': 1,
                'live_sessions': 1,
                'avg_distance': 25.5,
                'total_visits': 20,
                'total_distance': 25.5
            }
        else:
            stats = sheets_manager.get_dashboard_stats()
            if not stats:
                stats = {
                    'total_mrs': 0,
                    'active_today': 0,
                    'live_sessions': 0,
                    'avg_distance': 0,
                    'total_visits': 0,
                    'total_distance': 0
                }
        
        logger.info(f"Dashboard stats: {stats}")
        
        return {
            "success": True,
            "stats": stats,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in get_dashboard_stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")

@app.get("/api/activity")
async def get_activity_feed(api_key: str = Depends(verify_api_key)):
    """Get recent activity feed from Google Sheets"""
    try:
        logger.info("Processing /api/activity request")
        
        if not sheets_manager:
            activities = [
                {
                    'id': '1201911108_2025-09-03 14:37:15',
                    'mr_name': 'Vishesh Sanghvi',
                    'action': 'Field session started',
                    'timestamp': '2025-09-03 14:37:15',
                    'location': 'Lat: 18.947962, Lon: 72.829974'
                }
            ]
        else:
            activities = sheets_manager.get_activity_feed(limit=20)
        
        logger.info(f"Activity feed: {len(activities)} activities")
        
        return {
            "success": True,
            "activities": activities,
            "count": len(activities),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in get_activity_feed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get activity feed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    try:
        logger.info("Starting MR Tracking API server...")
        # Try different server configuration
        uvicorn.run(
            app, 
            host="127.0.0.1",  # Use localhost instead of 0.0.0.0
            port=8000, 
            log_level="info",
            access_log=True,
            loop="asyncio"  # Specify event loop
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        import traceback
        traceback.print_exc()
