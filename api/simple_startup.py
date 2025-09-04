"""
Simple Enhanced API Startup
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_live_api import app
from dashboard_api import router as dashboard_router

# Add dashboard routes
app.include_router(dashboard_router)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Enhanced MR Live Tracking API...")
    print("📍 Real-time location tracking enabled")
    print("🔌 WebSocket support enabled")
    print("📊 Advanced analytics enabled")
    print("🎯 Dashboard integration enabled")
    print("🌐 Server starting on http://0.0.0.0:8000")
    print("📖 Documentation: http://0.0.0.0:8000/docs")
    
    uvicorn.run(
        "simple_startup:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
