#!/usr/bin/env python3
"""
Check if backend is using new or old smart_sheets code
"""
import requests

API_URL = "http://localhost:8000"
API_KEY = "mr-tracking-2025"
headers = {"X-API-Key": API_KEY}

print("="*70)
print("CHECKING BACKEND VERSION")
print("="*70)

# Test route endpoint
print("\nTesting: /api/route?mr_id=1201911108&date=2025-10-15")
try:
    response = requests.get(
        f"{API_URL}/api/route?mr_id=1201911108&date=2025-10-15",
        headers=headers,
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        points = data.get('points', [])
        
        print(f"Response: {response.status_code} OK")
        print(f"Points returned: {len(points)}")
        
        if len(points) > 0:
            first = points[0]
            lat = first.get('lat', 0)
            lng = first.get('lng', 0)
            location = first.get('location', 'N/A')
            
            print(f"\nFirst point:")
            print(f"  Lat: {lat}")
            print(f"  Lng: {lng}")
            print(f"  Location: {location}")
            
            # Check if it's real data or sample
            if lat == 18.947934 and lng == 72.829943:
                print("\n[OK] USING NEW CODE - REAL DATA FROM SHEETS!")
                print("  This is the actual coordinate from your sheets!")
            elif 19.0 < lat < 19.1 and 72.8 < lng < 72.9:
                if "(MR" in location:
                    print("\n[PARTIAL] Using new code but no sheets data")
                    print("  Sample data with MR-specific variation")
                else:
                    print("\n[FAIL] USING OLD CODE - HARDCODED SAMPLE DATA")
                    print("  Backend hasn't been restarted!")
            else:
                print(f"\n[UNKNOWN] Unexpected coordinates")
        else:
            print("\n[FAIL] NO POINTS RETURNED!")
            print("Backend returned empty array")
            print("\nThis could mean:")
            print("  1. Date format mismatch in sheets")
            print("  2. Exception being caught silently")
            print("  3. Backend using Mock manager (sheets failed to load)")
    else:
        print(f"[FAIL] HTTP {response.status_code}: {response.text}")
except Exception as e:
    print(f"\n[FAIL] Connection error: {e}")
    print("Backend is not running or not accessible")

print("\n" + "="*70)
print("DIAGNOSIS")
print("="*70)

print("""
If you see:
- [OK] REAL DATA -> Backend restarted correctly, using real coords!
- [PARTIAL] -> Backend restarted but sheets have no data for this MR/date
- [FAIL] OLD CODE -> Backend NOT restarted, still using old code
- [FAIL] NO POINTS -> Backend running but returning empty (check backend console)
- [FAIL] Connection -> Backend not running at all

ACTION:
- Find the terminal window running: python api/main.py
- Press Ctrl+C to stop it
- Run: python api/main.py again
- Wait for "Uvicorn running..."
- Run this script again
""")

