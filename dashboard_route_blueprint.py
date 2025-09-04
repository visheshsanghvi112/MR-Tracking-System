"""
Dashboard Route Blueprint API
APIs for displaying visit-based location tracking and route blueprints
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from typing import Dict, List, Optional
import json
import logging
from datetime import datetime, timedelta
from visit_based_location_tracker import visit_tracker

logger = logging.getLogger(__name__)

# Dashboard Route Blueprint endpoints
async def get_mr_route_blueprint_api(mr_id: str, date: Optional[str] = None):
    """API endpoint to get MR route blueprint"""
    
    try:
        blueprint = await visit_tracker.get_route_blueprint(mr_id, date)
        
        if not blueprint:
            return {
                "success": False,
                "message": f"No route blueprint found for MR {mr_id} on {date or 'today'}",
                "data": None
            }
        
        return {
            "success": True,
            "message": "Route blueprint retrieved successfully",
            "data": blueprint
        }
        
    except Exception as e:
        logger.error(f"GET_ROUTE_BLUEPRINT_API: Error - {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_mr_location_history_api(mr_id: str, days: int = 7):
    """API endpoint to get MR location history"""
    
    try:
        history = await visit_tracker.get_location_history(mr_id, days)
        
        return {
            "success": True,
            "message": f"Location history retrieved for {days} days",
            "data": {
                "mr_id": mr_id,
                "days_requested": days,
                "history": history
            }
        }
        
    except Exception as e:
        logger.error(f"GET_LOCATION_HISTORY_API: Error - {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_mr_location_analytics_api(mr_id: str):
    """API endpoint to get MR location analytics"""
    
    try:
        analytics = await visit_tracker.get_location_analytics(mr_id)
        
        return {
            "success": True,
            "message": "Location analytics retrieved successfully",
            "data": {
                "mr_id": mr_id,
                "analytics": analytics
            }
        }
        
    except Exception as e:
        logger.error(f"GET_LOCATION_ANALYTICS_API: Error - {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_team_route_overview_api(team_ids: List[str], date: Optional[str] = None):
    """API endpoint to get team route overview"""
    
    try:
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        team_overview = []
        
        for mr_id in team_ids:
            blueprint = await visit_tracker.get_route_blueprint(mr_id, date)
            
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
            "message": f"Team overview retrieved for {len(team_ids)} MRs",
            "data": {
                "date": date,
                "team_performance": team_overview
            }
        }
        
    except Exception as e:
        logger.error(f"GET_TEAM_ROUTE_OVERVIEW_API: Error - {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Dashboard HTML templates
def generate_route_blueprint_html(blueprint: Dict) -> str:
    """Generate HTML for route blueprint visualization"""
    
    if not blueprint:
        return "<div class='alert alert-warning'>No route data available</div>"
    
    visits_html = ""
    for i, visit in enumerate(blueprint.get('visit_locations', [])):
        visits_html += f"""
        <div class="visit-card">
            <div class="visit-header">
                <span class="visit-number">{i+1}</span>
                <h4>{visit['location_name']}</h4>
                <span class="visit-type badge badge-{visit['location_type']}">{visit['location_type']}</span>
            </div>
            <div class="visit-details">
                <p><i class="fas fa-clock"></i> {datetime.fromisoformat(visit['visit_time']).strftime('%H:%M')}</p>
                <p><i class="fas fa-hourglass"></i> {visit['visit_duration']} minutes</p>
                <p><i class="fas fa-map-marker"></i> {visit['address']}</p>
                <p><i class="fas fa-check-circle"></i> {visit['visit_outcome'].title()}</p>
            </div>
        </div>
        """
    
    return f"""
    <div class="route-blueprint-dashboard">
        <div class="blueprint-header">
            <h2>Route Blueprint - {blueprint['mr_id']}</h2>
            <div class="blueprint-date">{blueprint['date']}</div>
        </div>
        
        <div class="blueprint-metrics">
            <div class="metric-card">
                <div class="metric-value">{blueprint['total_visits']}</div>
                <div class="metric-label">Total Visits</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{blueprint['total_distance']} km</div>
                <div class="metric-label">Distance Covered</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{blueprint['route_efficiency']:.1f}%</div>
                <div class="metric-label">Route Efficiency</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{blueprint['time_spent_visiting']} min</div>
                <div class="metric-label">Visit Time</div>
            </div>
        </div>
        
        <div class="blueprint-route">
            <div class="route-summary">
                <div class="route-start">
                    <h4>🏁 Started at</h4>
                    <p>{blueprint['start_location'].get('name', 'Unknown')}</p>
                    <small>{blueprint['start_location'].get('time', '')}</small>
                </div>
                <div class="route-path">
                    <div class="route-line"></div>
                    <div class="visit-count">{blueprint['total_visits']} visits</div>
                </div>
                <div class="route-end">
                    <h4>🏁 Ended at</h4>
                    <p>{blueprint['end_location'].get('name', 'Unknown')}</p>
                    <small>{blueprint['end_location'].get('time', '')}</small>
                </div>
            </div>
        </div>
        
        <div class="blueprint-visits">
            <h3>Visit Details</h3>
            <div class="visits-timeline">
                {visits_html}
            </div>
        </div>
        
        <div class="blueprint-coverage">
            <h3>Coverage Areas</h3>
            <div class="coverage-areas">
                {''.join([f'<span class="area-badge">{area}</span>' for area in blueprint['coverage_areas']])}
            </div>
        </div>
    </div>
    
    <style>
    .route-blueprint-dashboard {{
        background: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    
    .blueprint-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border-bottom: 2px solid #eee;
        padding-bottom: 10px;
    }}
    
    .blueprint-metrics {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 15px;
        margin-bottom: 25px;
    }}
    
    .metric-card {{
        text-align: center;
        padding: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
    }}
    
    .metric-value {{
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 5px;
    }}
    
    .metric-label {{
        font-size: 12px;
        opacity: 0.9;
    }}
    
    .route-summary {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 25px;
    }}
    
    .route-start, .route-end {{
        text-align: center;
        flex: 1;
    }}
    
    .route-path {{
        flex: 2;
        text-align: center;
        position: relative;
    }}
    
    .route-line {{
        height: 2px;
        background: linear-gradient(to right, #28a745, #17a2b8);
        margin: 10px 20px;
    }}
    
    .visits-timeline {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 15px;
    }}
    
    .visit-card {{
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        background: white;
    }}
    
    .visit-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }}
    
    .visit-number {{
        background: #007bff;
        color: white;
        width: 25px;
        height: 25px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
    }}
    
    .visit-details p {{
        margin: 5px 0;
        font-size: 14px;
    }}
    
    .coverage-areas {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }}
    
    .area-badge {{
        background: #e9ecef;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        border: 1px solid #dee2e6;
    }}
    
    .badge-hospital {{ background: #d4edda; }}
    .badge-pharmacy {{ background: #d1ecf1; }}
    .badge-clinic {{ background: #f8d7da; }}
    .badge-general {{ background: #e2e3e5; }}
    </style>
    """

def generate_location_history_html(history_data: Dict) -> str:
    """Generate HTML for location history visualization"""
    
    history = history_data.get('history', [])
    
    if not history:
        return "<div class='alert alert-warning'>No location history available</div>"
    
    history_rows = ""
    for day in history:
        history_rows += f"""
        <tr>
            <td>{day['date']}</td>
            <td><span class="badge badge-primary">{day['total_visits']}</span></td>
            <td>{day['avg_visit_duration']} min</td>
            <td>
                <div class="locations-list">
                    {'<br>'.join(day['locations_visited'][:3])}
                    {f'<small>+{len(day["locations_visited"])-3} more</small>' if len(day['locations_visited']) > 3 else ''}
                </div>
            </td>
        </tr>
        """
    
    return f"""
    <div class="location-history-dashboard">
        <div class="history-header">
            <h2>Location History - {history_data['mr_id']}</h2>
            <div class="history-period">Last {history_data['days_requested']} days</div>
        </div>
        
        <div class="history-table-container">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Total Visits</th>
                        <th>Avg Duration</th>
                        <th>Locations Visited</th>
                    </tr>
                </thead>
                <tbody>
                    {history_rows}
                </tbody>
            </table>
        </div>
    </div>
    
    <style>
    .location-history-dashboard {{
        background: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    
    .history-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border-bottom: 2px solid #eee;
        padding-bottom: 10px;
    }}
    
    .history-table-container {{
        overflow-x: auto;
    }}
    
    .table {{
        width: 100%;
        border-collapse: collapse;
    }}
    
    .table th, .table td {{
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }}
    
    .table th {{
        background: #f8f9fa;
        font-weight: 600;
    }}
    
    .locations-list {{
        max-width: 200px;
        font-size: 12px;
    }}
    
    .badge {{
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }}
    
    .badge-primary {{
        background: #007bff;
        color: white;
    }}
    </style>
    """

async def get_route_blueprint_html(mr_id: str, date: Optional[str] = None):
    """API endpoint to get route blueprint as HTML"""
    
    blueprint = await visit_tracker.get_route_blueprint(mr_id, date)
    html_content = generate_route_blueprint_html(blueprint)
    
    return HTMLResponse(content=html_content)

async def get_location_history_html(mr_id: str, days: int = 7):
    """API endpoint to get location history as HTML"""
    
    history = await visit_tracker.get_location_history(mr_id, days)
    history_data = {
        "mr_id": mr_id,
        "days_requested": days,
        "history": history
    }
    
    html_content = generate_location_history_html(history_data)
    
    return HTMLResponse(content=html_content)

# Map visualization functions
def generate_route_map_data(blueprint: Dict) -> Dict:
    """Generate map data for route visualization"""
    
    if not blueprint or not blueprint.get('visit_locations'):
        return {"markers": [], "routes": [], "center": {"lat": 19.0760, "lng": 72.8777}}
    
    markers = []
    route_points = []
    
    for i, visit in enumerate(blueprint['visit_locations']):
        markers.append({
            "id": i,
            "position": {"lat": visit['latitude'], "lng": visit['longitude']},
            "title": visit['location_name'],
            "info": {
                "type": visit['location_type'],
                "time": visit['visit_time'],
                "duration": f"{visit['visit_duration']} min",
                "outcome": visit['visit_outcome']
            },
            "icon": {
                "hospital": "🏥",
                "pharmacy": "💊", 
                "clinic": "🏪",
                "general": "📍"
            }.get(visit['location_type'], "📍")
        })
        
        route_points.append({
            "lat": visit['latitude'],
            "lng": visit['longitude']
        })
    
    # Calculate center point
    if route_points:
        center_lat = sum(p['lat'] for p in route_points) / len(route_points)
        center_lng = sum(p['lng'] for p in route_points) / len(route_points)
        center = {"lat": center_lat, "lng": center_lng}
    else:
        center = {"lat": 19.0760, "lng": 72.8777}  # Mumbai default
    
    return {
        "markers": markers,
        "route": route_points,
        "center": center,
        "stats": {
            "total_visits": blueprint['total_visits'],
            "total_distance": blueprint['total_distance'],
            "efficiency": blueprint['route_efficiency']
        }
    }

async def get_route_map_data_api(mr_id: str, date: Optional[str] = None):
    """API endpoint to get route map visualization data"""
    
    try:
        blueprint = await visit_tracker.get_route_blueprint(mr_id, date)
        map_data = generate_route_map_data(blueprint)
        
        return {
            "success": True,
            "message": "Route map data retrieved successfully",
            "data": map_data
        }
        
    except Exception as e:
        logger.error(f"GET_ROUTE_MAP_DATA_API: Error - {e}")
        raise HTTPException(status_code=500, detail=str(e))
