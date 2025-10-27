#!/usr/bin/env python3
"""
Verify which backend code is running
"""
import requests
import json

API_URL = "http://localhost:8000"
API_KEY = "mr-tracking-2025"

print("=" * 70)
print("BACKEND VERIFICATION TEST")
print("=" * 70)

# Test with MR that should show different data now
mr_ids = [1201911108, 8393304686, 8254199110]
date = "2025-10-15"

headers = {"X-API-Key": API_KEY}

print(f"\nTesting {len(mr_ids)} different MRs to check if coordinates vary...\n")

coords_map = {}

for mr_id in mr_ids:
    print(f"Testing MR {mr_id}...")
    try:
        response = requests.get(
            f"{API_URL}/api/route?mr_id={mr_id}&date={date}",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('points'):
                point1 = data['points'][0]
                coords = (point1['lat'], point1['lng'])
                coords_map[mr_id] = coords
                print(f"  First point: {coords[0]}, {coords[1]}")
                print(f"  Location: {point1.get('location', 'N/A')}")
        else:
            print(f"  ERROR: Status {response.status_code}")
    except Exception as e:
        print(f"  ERROR: {e}")
    print()

print("=" * 70)
print("ANALYSIS")
print("=" * 70)

if len(coords_map) >= 2:
    unique_coords = len(set(coords_map.values()))
    
    print(f"\nTested {len(coords_map)} MRs")
    print(f"Unique coordinate sets: {unique_coords}")
    
    if unique_coords == 1:
        print("\n⚠️ ALL MRs HAVE SAME COORDINATES")
        print("   Backend is still using OLD code (not restarted)")
        print("\n   FIX:")
        print("   1. Stop backend (Ctrl+C in backend terminal)")
        print("   2. Run: cd api && python main.py")
        print("   3. Wait for 'Uvicorn running...'")
        print("   4. Run this test again")
    elif unique_coords == len(coords_map):
        print("\n✅ ALL MRs HAVE DIFFERENT COORDINATES")
        print("   Backend is using NEW code with sheets check!")
        if any('(MR' in str(v) for v in coords_map.values()):
            print("   Using sample data with MR-specific variation")
        else:
            print("   Using real data from Google Sheets")
    else:
        print(f"\n⚠️ MIXED: {unique_coords} unique out of {len(coords_map)}")
        print("   Some MRs have different data, some don't")
else:
    print("\n⚠️ Not enough data to analyze")

print("\n" + "=" * 70)

