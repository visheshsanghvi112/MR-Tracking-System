#!/usr/bin/env python3
"""
Simple HTTP API server using built-in Python HTTP server
"""
import json
import os
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

# Add current directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from smart_sheets import SmartMRSheetsManager
    sheets_manager = SmartMRSheetsManager()
    print(f"✅ Google Sheets connection established")
except Exception as e:
    print(f"❌ Google Sheets connection failed: {e}")
    sheets_manager = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MRTrackingAPIHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        """Override to prevent default logging"""
        logger.info(f"{self.address_string()} - {format % args}")
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, x-api-key, X-API-Key')
        self.send_header('Content-Type', 'application/json')
    
    def verify_api_key(self):
        """Check API key"""
        api_key = self.headers.get('x-api-key') or self.headers.get('X-API-Key')
        return api_key == 'mr-tracking-2025'
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_cors_headers()
        self.end_headers()
        json_data = json.dumps(data, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def send_error_response(self, message, status_code=500):
        """Send error response"""
        self.send_json_response({
            "success": False,
            "error": message,
            "timestamp": datetime.now().isoformat()
        }, status_code)
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            logger.info(f"GET request: {path}")
            
            # Health check
            if path == '/':
                self.send_json_response({
                    "status": "ok",
                    "service": "MR Tracking API - Simple",
                    "version": "1.0.0",
                    "timestamp": datetime.now().isoformat(),
                    "sheets_connected": sheets_manager is not None
                })
                return
            
            # Verify API key for protected endpoints
            if not self.verify_api_key():
                self.send_error_response("Invalid API key", 401)
                return
            
            # MR list endpoint
            if path == '/api/mrs':
                try:
                    if sheets_manager:
                        mrs = sheets_manager.get_all_mrs()
                        logger.info(f"Retrieved {len(mrs)} MRs from sheets")
                    else:
                        # Fallback data
                        mrs = [{
                            "mr_id": "1201911108",
                            "name": "Vishesh Sanghvi",
                            "status": "active",
                            "last_location": {"lat": 18.947962, "lng": 72.829974},
                            "last_activity": "2025-09-03 14:37:15",
                            "total_visits": 20
                        }]
                    
                    self.send_json_response({
                        "success": True,
                        "mrs": mrs,
                        "count": len(mrs)
                    })
                    
                except Exception as e:
                    logger.error(f"Error getting MRs: {e}")
                    self.send_error_response(f"Failed to get MR list: {str(e)}")
                return
            
            # Dashboard stats endpoint
            if path == '/api/dashboard/stats':
                try:
                    if sheets_manager:
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
                    else:
                        stats = {
                            'total_mrs': 1,
                            'active_today': 1,
                            'live_sessions': 1,
                            'avg_distance': 25.5,
                            'total_visits': 20,
                            'total_distance': 25.5
                        }
                    
                    self.send_json_response({
                        "success": True,
                        "stats": stats,
                        "generated_at": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.error(f"Error getting stats: {e}")
                    self.send_error_response(f"Failed to get dashboard stats: {str(e)}")
                return
            
            # Activity feed endpoint
            if path == '/api/activity':
                try:
                    if sheets_manager:
                        activities = sheets_manager.get_activity_feed(limit=20)
                    else:
                        activities = [
                            {
                                'id': '1201911108_2025-09-03 14:37:15',
                                'mr_name': 'Vishesh Sanghvi',
                                'action': 'Field session started',
                                'timestamp': '2025-09-03 14:37:15',
                                'location': 'Lat: 18.947962, Lon: 72.829974'
                            }
                        ]
                    
                    self.send_json_response({
                        "success": True,
                        "activities": activities,
                        "count": len(activities),
                        "generated_at": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.error(f"Error getting activity: {e}")
                    self.send_error_response(f"Failed to get activity feed: {str(e)}")
                return
            
            # Unknown endpoint
            self.send_error_response(f"Endpoint not found: {path}", 404)
            
        except Exception as e:
            logger.error(f"Unexpected error in GET handler: {e}")
            self.send_error_response(f"Internal server error: {str(e)}")

def run_server(port=8000):
    """Run the HTTP server"""
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, MRTrackingAPIHandler)
    
    print(f"🚀 MR Tracking API server starting on http://127.0.0.1:{port}")
    print(f"📊 Google Sheets: {'✅ Connected' if sheets_manager else '❌ Not connected'}")
    print(f"🔑 API Key: mr-tracking-2025")
    print(f"🌐 Endpoints:")
    print(f"   GET  /                    - Health check")
    print(f"   GET  /api/mrs             - Get MR list")
    print(f"   GET  /api/dashboard/stats - Get dashboard stats") 
    print(f"   GET  /api/activity        - Get activity feed")
    print("\n🛑 Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
