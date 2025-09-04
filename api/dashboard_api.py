"""
Real-time Dashboard API
Provides endpoints for live monitoring dashboard
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any
from datetime import datetime, timedelta
import asyncio

from enhanced_live_api import verify_api_key
from session_manager import mr_session_manager as session_manager

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/overview")
async def get_dashboard_overview(api_key: str = Depends(verify_api_key)):
    """Get real-time dashboard overview"""
    try:
        # Get all MR analytics
        all_analytics = []
        total_distance = 0
        total_visits = 0
        active_count = 0
        
        for mr_id in session_manager.sessions.keys():
            analytics = session_manager.get_mr_analytics(mr_id)
            all_analytics.append(analytics)
            
            total_distance += analytics['today_stats']['distance_traveled']
            total_visits += analytics['today_stats']['locations_visited']
            
            if analytics['session_active']:
                active_count += 1
        
        # Calculate team performance metrics
        team_performance = {
            "efficiency_score": calculate_team_efficiency(all_analytics),
            "coverage_score": calculate_coverage_score(all_analytics),
            "activity_score": calculate_activity_score(all_analytics)
        }
        
        return {
            "success": True,
            "overview": {
                "total_mrs": len(all_analytics),
                "active_now": active_count,
                "total_distance_today": round(total_distance, 2),
                "total_visits_today": total_visits,
                "team_performance": team_performance
            },
            "mr_analytics": all_analytics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard overview: {str(e)}")

@router.get("/live-map")
async def get_live_map_data(api_key: str = Depends(verify_api_key)):
    """Get live map data for all MRs"""
    try:
        map_data = {
            "mrs": [],
            "heat_zones": [],
            "activity_areas": []
        }
        
        for mr_id in session_manager.sessions.keys():
            location_data = session_manager.get_live_location(mr_id)
            trail = session_manager.get_location_trail(mr_id, 2)  # Last 2 hours
            
            mr_map_data = {
                "mr_id": mr_id,
                "current_location": {
                    "lat": location_data['lat'],
                    "lon": location_data['lon'],
                    "address": location_data['address'],
                    "status": "active" if location_data['active'] else "inactive",
                    "last_update": location_data['last_update']
                },
                "trail": trail[-20:],  # Last 20 points for trail
                "stats": {
                    "distance_today": session_manager.calculate_distance_traveled(mr_id, 12),
                    "locations_visited": len(trail),
                    "active_time": session_manager._calculate_active_time(mr_id)
                }
            }
            
            map_data["mrs"].append(mr_map_data)
        
        return {
            "success": True,
            "map_data": map_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get live map data: {str(e)}")

@router.get("/alerts")
async def get_system_alerts(api_key: str = Depends(verify_api_key)):
    """Get system alerts and notifications"""
    try:
        alerts = []
        
        for mr_id in session_manager.sessions.keys():
            analytics = session_manager.get_mr_analytics(mr_id)
            location_data = session_manager.get_live_location(mr_id)
            
            # Check for various alert conditions
            
            # Inactive MR alert
            if not analytics['session_active']:
                last_seen = location_data.get('last_update')
                if last_seen:
                    last_seen_time = datetime.fromisoformat(last_seen.replace('Z', ''))
                    hours_inactive = (datetime.now() - last_seen_time).total_seconds() / 3600
                    
                    if hours_inactive > 2:
                        alerts.append({
                            "type": "warning",
                            "mr_id": mr_id,
                            "title": f"MR {mr_id} Inactive",
                            "message": f"No activity for {hours_inactive:.1f} hours",
                            "timestamp": datetime.now().isoformat()
                        })
            
            # Low activity alert
            if analytics['today_stats']['locations_visited'] < 2:
                alerts.append({
                    "type": "info",
                    "mr_id": mr_id,
                    "title": f"Low Activity - MR {mr_id}",
                    "message": f"Only {analytics['today_stats']['locations_visited']} locations visited today",
                    "timestamp": datetime.now().isoformat()
                })
            
            # High performance alert
            if analytics['today_stats']['distance_traveled'] > 50:
                alerts.append({
                    "type": "success",
                    "mr_id": mr_id,
                    "title": f"High Performance - MR {mr_id}",
                    "message": f"Covered {analytics['today_stats']['distance_traveled']} km today",
                    "timestamp": datetime.now().isoformat()
                })
        
        return {
            "success": True,
            "alerts": alerts,
            "count": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")

@router.get("/performance-metrics")
async def get_performance_metrics(
    timeframe: str = "today",
    api_key: str = Depends(verify_api_key)
):
    """Get performance metrics for specified timeframe"""
    try:
        hours = get_hours_for_timeframe(timeframe)
        
        metrics = {
            "team_metrics": {
                "total_distance": 0,
                "total_visits": 0,
                "active_hours": 0,
                "efficiency_score": 0
            },
            "individual_metrics": [],
            "comparisons": {
                "top_performer": None,
                "most_distance": None,
                "most_visits": None
            }
        }
        
        all_mr_metrics = []
        
        for mr_id in session_manager.sessions.keys():
            distance = session_manager.calculate_distance_traveled(mr_id, hours)
            trail = session_manager.get_location_trail(mr_id, hours)
            
            mr_metrics = {
                "mr_id": mr_id,
                "distance_traveled": distance,
                "locations_visited": len(trail),
                "active_time": session_manager._calculate_active_time(mr_id),
                "avg_speed": session_manager._calculate_avg_speed(mr_id),
                "efficiency_score": calculate_efficiency_score(distance, len(trail), hours)
            }
            
            all_mr_metrics.append(mr_metrics)
            
            # Add to team totals
            metrics["team_metrics"]["total_distance"] += distance
            metrics["team_metrics"]["total_visits"] += len(trail)
            metrics["team_metrics"]["active_hours"] += mr_metrics["active_time"]
        
        # Calculate team efficiency
        if all_mr_metrics:
            metrics["team_metrics"]["efficiency_score"] = sum(m["efficiency_score"] for m in all_mr_metrics) / len(all_mr_metrics)
            
            # Find top performers
            metrics["comparisons"]["most_distance"] = max(all_mr_metrics, key=lambda x: x["distance_traveled"])
            metrics["comparisons"]["most_visits"] = max(all_mr_metrics, key=lambda x: x["locations_visited"])
            metrics["comparisons"]["top_performer"] = max(all_mr_metrics, key=lambda x: x["efficiency_score"])
        
        metrics["individual_metrics"] = all_mr_metrics
        
        return {
            "success": True,
            "timeframe": timeframe,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

# Helper functions

def get_hours_for_timeframe(timeframe: str) -> int:
    """Convert timeframe to hours"""
    timeframes = {
        "today": 24,
        "week": 24 * 7,
        "month": 24 * 30,
        "current_session": 8
    }
    return timeframes.get(timeframe, 24)

def calculate_efficiency_score(distance: float, visits: int, hours: int) -> float:
    """Calculate efficiency score based on distance, visits, and time"""
    if hours == 0:
        return 0
    
    # Score factors
    distance_score = min(distance * 2, 100)  # Max 100 for 50km+
    visit_score = min(visits * 10, 100)      # Max 100 for 10+ visits
    time_efficiency = min((distance + visits) / hours * 10, 100)
    
    return round((distance_score + visit_score + time_efficiency) / 3, 2)

def calculate_team_efficiency(analytics_list: List[Dict]) -> float:
    """Calculate overall team efficiency score"""
    if not analytics_list:
        return 0
    
    scores = []
    for analytics in analytics_list:
        stats = analytics['today_stats']
        score = calculate_efficiency_score(
            stats['distance_traveled'],
            stats['locations_visited'],
            stats['active_time'] or 1
        )
        scores.append(score)
    
    return round(sum(scores) / len(scores), 2)

def calculate_coverage_score(analytics_list: List[Dict]) -> float:
    """Calculate geographical coverage score"""
    if not analytics_list:
        return 0
    
    # Simple coverage score based on total area covered
    total_coverage = sum(a['today_stats']['locations_visited'] for a in analytics_list)
    return min(total_coverage * 5, 100)  # Max 100 for 20+ total locations

def calculate_activity_score(analytics_list: List[Dict]) -> float:
    """Calculate team activity score"""
    if not analytics_list:
        return 0
    
    active_count = sum(1 for a in analytics_list if a['session_active'])
    activity_percentage = (active_count / len(analytics_list)) * 100
    
    return round(activity_percentage, 2)
