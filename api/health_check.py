#!/usr/bin/env python3
"""
Fast API Health Check
Quick verification of API status and critical endpoints
"""
import requests
import sys
from datetime import datetime

API_BASE = "http://localhost:8000"
API_KEY = "mr-tracking-2025"

def check_health():
    """Quick health check"""
    results = []
    
    # 1. Root endpoint
    try:
        r = requests.get(f"{API_BASE}/", timeout=2)
        if r.status_code == 200:
            data = r.json()
            results.append(f"[OK] API Online: {data.get('service')} v{data.get('version')}")
        else:
            results.append(f"[FAIL] Root: {r.status_code}")
    except Exception as e:
        results.append(f"[FAIL] API Offline: {str(e)}")
        return results
    
    # 2. Authentication
    try:
        # Without key
        r = requests.get(f"{API_BASE}/api/mrs", timeout=2)
        if r.status_code == 401:
            results.append("[OK] Auth: Protected")
        else:
            results.append("[WARN] Auth: Not protected")
    except:
        pass
    
    # 3. With key
    try:
        r = requests.get(f"{API_BASE}/api/mrs", headers={"X-API-Key": API_KEY}, timeout=2)
        if r.status_code == 200:
            data = r.json()
            mr_count = data.get('count', 0)
            results.append(f"[OK] MRs Endpoint: {mr_count} active MRs")
        else:
            results.append(f"[FAIL] MRs: {r.status_code}")
    except Exception as e:
        results.append(f"[FAIL] MRs: {str(e)}")
    
    # 4. Route endpoint
    try:
        r = requests.get(
            f"{API_BASE}/api/route?mr_id=8393304686&date=2025-10-27",
            headers={"X-API-Key": API_KEY},
            timeout=2
        )
        if r.status_code == 200:
            data = r.json()
            points = len(data.get('points', []))
            results.append(f"[OK] Route Endpoint: {points} GPS points")
        else:
            results.append(f"[WARN] Route: {r.status_code}")
    except:
        pass
    
    return results

if __name__ == "__main__":
    print("Quick Health Check...")
    print("-" * 40)
    
    results = check_health()
    
    for result in results:
        print(result)
    
    print("-" * 40)
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Exit code based on results
    if any("[FAIL]" in r for r in results):
        sys.exit(1)
    sys.exit(0)

