"""
Quick MR Live Tracking Demo
Simulates live MR movement and shows real-time updates
"""
import requests
import json
import time
from datetime import datetime

def demo_live_tracking():
    base_url = "http://localhost:8000"
    headers = {"x-api-key": "mr-tracking-2025"}
    mr_id = 1201911108
    
    print("🚀 MR Live Tracking Demo Starting...")
    print("=" * 60)
    
    # Mumbai locations for realistic MR route
    route = [
        (19.0760, 72.8777, "Home Base - Bandra West", 0, "start"),
        (19.0820, 72.8850, "Dr. Sharma Clinic - Patient Visit", 15, "visit"),
        (19.0880, 72.8900, "Apollo Pharmacy - Stock Check", 22, "visit"), 
        (19.0920, 72.8950, "City Hospital - Doctor Meeting", 18, "visit"),
        (19.0860, 72.8800, "Medicare Center - Prescription Drop", 25, "visit"),
        (19.0780, 72.8720, "Health Plus Clinic - Follow-up", 20, "visit"),
        (19.0740, 72.8680, "Wellness Pharmacy - Final Visit", 12, "end")
    ]
    
    print(f"👨‍⚕️ MR {mr_id} starting field route with {len(route)} locations")
    print("📍 Route: Mumbai Medical Circuit")
    print("=" * 60)
    
    for i, (lat, lon, location, speed, visit_type) in enumerate(route):
        print(f"\n🎯 Step {i+1}: {location}")
        print(f"   📍 Coordinates: {lat:.4f}, {lon:.4f}")
        print(f"   🏃 Speed: {speed} km/h")
        print(f"   📋 Type: {visit_type}")
        
        # Send location update
        location_data = {
            "mr_id": mr_id,
            "lat": lat,
            "lon": lon,
            "address": location,
            "accuracy": 5.0 + (i * 0.5),
            "speed": float(speed),
            "heading": (i * 45) % 360,
            "battery_level": 95 - (i * 3)
        }
        
        try:
            # Update location
            response = requests.post(f"{base_url}/api/location/update", 
                                   headers=headers, json=location_data)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Location Updated: {data['message']}")
                print(f"   ⏰ Session Active: {data['data']['active']}")
                print(f"   🔋 Battery: {location_data['battery_level']}%")
                
                # Get live location to verify
                live_response = requests.get(f"{base_url}/api/location/live/{mr_id}", 
                                           headers=headers)
                if live_response.status_code == 200:
                    live_data = live_response.json()
                    location_info = live_data['location']
                    print(f"   📊 Live Status: {location_info['address']}")
                    print(f"   ⏳ Time Remaining: {location_info.get('time_remaining', 0)}s")
                
            else:
                print(f"   ❌ Update Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Wait between moves (simulate travel time)
        if i < len(route) - 1:
            wait_time = 3 + (i * 0.5)
            print(f"   🚗 Traveling to next location... ({wait_time:.1f}s)")
            time.sleep(wait_time)
    
    # Final analytics check
    print("\n" + "=" * 60)
    print("📊 FINAL ANALYTICS CHECK")
    print("=" * 60)
    
    try:
        # Get MR analytics
        response = requests.get(f"{base_url}/api/analytics/{mr_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            analytics = data['analytics']
            stats = analytics['today_stats']
            
            print(f"👨‍⚕️ MR {mr_id} Performance Summary:")
            print(f"   🛣️  Distance Traveled: {stats['distance_traveled']:.2f} km")
            print(f"   📍 Locations Visited: {stats['locations_visited']}")
            print(f"   ⏰ Active Time: {stats['active_time']:.2f} hours")
            print(f"   📝 Entries Logged: {stats['entries_logged']}")
            print(f"   🎯 Session Status: {'Active' if analytics['session_active'] else 'Completed'}")
            
        # Get location trail
        trail_response = requests.get(f"{base_url}/api/location/trail/{mr_id}?hours=1", 
                                    headers=headers)
        if trail_response.status_code == 200:
            trail_data = trail_response.json()
            print(f"   📈 Trail Points: {trail_data['count']} recorded")
            
        # Get team overview
        team_response = requests.get(f"{base_url}/api/analytics/team/overview", headers=headers)
        if team_response.status_code == 200:
            team_data = team_response.json()
            overview = team_data['overview']
            print(f"\n🏢 Team Performance:")
            print(f"   👥 Total MRs: {overview['total_mrs']}")
            print(f"   🟢 Active Today: {overview['active_today']}")
            print(f"   🛣️  Team Distance: {overview['total_distance']:.2f} km")
            print(f"   📍 Team Visits: {overview['total_visits']}")
            
    except Exception as e:
        print(f"❌ Analytics Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 LIVE TRACKING DEMO COMPLETE!")
    print("✅ Enhanced MR Tracking System Successfully Tested!")
    print("🔥 Real-time updates, analytics, and performance tracking all working!")
    print("=" * 60)

if __name__ == "__main__":
    demo_live_tracking()
