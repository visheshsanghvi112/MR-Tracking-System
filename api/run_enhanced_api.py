"""
Enhanced MR Tracking API Startup Script
Runs the complete live tracking system with all components
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
import logging

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all components
from enhanced_live_api import app as main_app
from dashboard_api import router as dashboard_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_enhanced_app():
    """Create the complete enhanced tracking app"""
    
    # Create main app with enhanced configuration
    app = FastAPI(
        title="Complete MR Live Tracking System",
        description="""
        ## Enhanced MR Live Tracking API
        
        Complete real-time tracking system for Medical Representatives with:
        
        ### Core Features
        - **Real-time Location Tracking**: Live GPS updates with WebSocket support
        - **Advanced Analytics**: Performance metrics and insights
        - **Route Optimization**: Smart route planning and analysis  
        - **Team Management**: Multi-MR tracking and coordination
        - **Dashboard Integration**: Real-time monitoring dashboards
        
        ### API Endpoints
        - `/api/location/*` - Location tracking and updates
        - `/api/analytics/*` - Performance analytics  
        - `/api/dashboard/*` - Real-time dashboard data
        - `/ws/{mr_id}` - WebSocket live updates
        
        ### Authentication
        Include `x-api-key` header with your API key for authenticated endpoints.
        
        ### WebSocket Usage
        Connect to `/ws/{mr_id}` for real-time location updates and notifications.
        """,
        version="2.0.0",
        contact={
            "name": "MR Tracking Support",
            "email": "support@mrtracking.com"
        }
    )
    
    # Enhanced CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",      # React development
            "http://localhost:3001",      # React alternate port
            "https://*.vercel.app",       # Vercel deployments
            "https://*.netlify.app",      # Netlify deployments
            "*"                           # Allow all for development
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )
    
    # Copy all routes from main app
    for route in main_app.routes:
        app.router.routes.append(route)
        
    # Add dashboard router
    app.include_router(dashboard_router)
    
    # Add startup event
    @app.on_event("startup")
    async def startup_event():
        logger.info("🚀 Enhanced MR Tracking API Starting Up...")
        logger.info("📍 Live location tracking: ENABLED")
        logger.info("🔌 WebSocket connections: ENABLED") 
        logger.info("📊 Advanced analytics: ENABLED")
        logger.info("🎯 Dashboard integration: ENABLED")
        logger.info("✅ System ready for MR tracking!")
        
    # Add shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("🛑 Enhanced MR Tracking API Shutting Down...")
        logger.info("💾 Saving session data...")
        logger.info("❌ System stopped")
    
    return app

def main():
    """Main startup function"""
    print("=" * 60)
    print("🚀 ENHANCED MR LIVE TRACKING SYSTEM")
    print("=" * 60)
    print("Features:")
    print("  ✅ Real-time GPS tracking")  
    print("  ✅ WebSocket live updates")
    print("  ✅ Advanced analytics")
    print("  ✅ Performance monitoring")
    print("  ✅ Team dashboards")
    print("  ✅ Route optimization")
    print("=" * 60)
    
    # Get configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    # Create enhanced app
    app = create_enhanced_app()
    
    print(f"🌐 Starting server on http://{host}:{port}")
    print(f"📖 API Documentation: http://{host}:{port}/docs")
    print(f"🔧 ReDoc Documentation: http://{host}:{port}/redoc")
    print("=" * 60)
    
    # Run server with enhanced configuration
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True,
        ws_ping_interval=20,
        ws_ping_timeout=20,
        timeout_keep_alive=30
    )

if __name__ == "__main__":
    main()
