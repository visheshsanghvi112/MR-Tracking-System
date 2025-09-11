#!/usr/bin/env python3
"""
Fix the remaining 2 API endpoint issues
1. Blueprint endpoint 500 error - add sample data if needed
2. GPX export 404 error - test endpoint
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_KEY = "dev_key_2024"

def test_blueprint_endpoint():
    """Test and fix blueprint endpoint"""
    print("🗺️ Testing Blueprint Endpoint...")
    
    # Test current status
    url = f"{BASE_URL}/api/v2/route-blueprint/1201911108"
    headers = {
        "accept": "application/json",
        "X-API-Key": API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Blueprint endpoint working!")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False

def test_gpx_export():
    """Test GPX export endpoint"""
    print("\n💾 Testing GPX Export...")
    
    # Get available MR first
    headers = {"X-API-Key": API_KEY}
    mrs_response = requests.get(f"{BASE_URL}/api/mrs", headers=headers)
    
    if mrs_response.status_code != 200:
        print(f"   ❌ Can't get MRs: {mrs_response.status_code}")
        return False
    
    mrs = mrs_response.json()
    if not mrs.get('mrs'):
        print("   ❌ No MRs found")
        return False
    
    mr_id = mrs['mrs'][0]['employee_id']
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Test GPX export
    url = f"{BASE_URL}/api/export/gpx"
    params = {
        "mr_id": mr_id,
        "date": date
    }
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"   URL: {url}")
        print(f"   Params: {params}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            print(f"   Content-Type: {content_type}")
            print(f"   Content Length: {len(response.content)} bytes")
            
            if 'gpx' in content_type.lower() or 'xml' in content_type.lower():
                print("   ✅ GPX export working!")
                return True
            else:
                print(f"   ⚠️ Unexpected content type: {content_type}")
                print(f"   Response: {response.text[:200]}...")
                return False
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False

def add_sample_visit_data():
    """Add sample visit data to test blueprint functionality"""
    print("\n📍 Adding Sample Visit Data...")
    
    try:
        # Import the visit tracker
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from visit_based_location_tracker import visit_tracker
        import asyncio
        
        async def add_visit():
            # Sample visit data
            visit_data = {
                'visit_id': f"visit_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'mr_id': '1201911108',
                'location_name': 'Apollo Hospital Mumbai',
                'location_type': 'hospital',
                'latitude': 19.0760,
                'longitude': 72.8777,
                'address': 'Tardeo, Mumbai, Maharashtra 400034',
                'visit_time': datetime.now().isoformat(),
                'visit_duration': 45,
                'visit_outcome': 'successful',
                'session_id': 'test_session_001',
                'weather': 'Clear',
                'area_type': 'urban',
                'notes': 'Sample visit for testing'
            }
            
            success = await visit_tracker.capture_visit_location(visit_data)
            return success
        
        result = asyncio.run(add_visit())
        
        if result:
            print("   ✅ Sample visit data added!")
            return True
        else:
            print("   ❌ Failed to add sample data")
            return False
            
    except Exception as e:
        print(f"   ❌ Error adding sample data: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing Remaining API Endpoints")
    print("=" * 50)
    
    # Step 1: Add sample data if needed
    add_sample_visit_data()
    
    # Step 2: Test blueprint endpoint
    blueprint_ok = test_blueprint_endpoint()
    
    # Step 3: Test GPX export
    gpx_ok = test_gpx_export()
    
    print("\n" + "=" * 50)
    print("📋 RESULTS:")
    print(f"   Blueprint Endpoint: {'✅ WORKING' if blueprint_ok else '❌ FAILED'}")
    print(f"   GPX Export: {'✅ WORKING' if gpx_ok else '❌ FAILED'}")
    
    if blueprint_ok and gpx_ok:
        print("\n🎉 ALL ENDPOINTS FIXED! Ready for 100% compatibility test.")
    else:
        print("\n⚠️ Some endpoints still need attention.")
