"""
Simple HTTP Tests for Enhanced MR Tracking API
Direct HTTP requests to test all functionality
"""

def test_with_curl():
    """Test using curl commands"""
    print("🚀 Testing Enhanced MR Tracking API with HTTP Requests")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    headers = '-H "x-api-key: mr-tracking-2025" -H "Content-Type: application/json"'
    
    print("1. Testing API Status:")
    print(f'curl -X GET "{base_url}/"')
    print()
    
    print("2. Testing Health Check:")
    print(f'curl -X GET "{base_url}/api/health" {headers}')
    print()
    
    print("3. Testing MR List:")
    print(f'curl -X GET "{base_url}/api/mrs" {headers}')
    print()
    
    print("4. Testing Location Update:")
    location_data = '''{
    "mr_id": 1201911108,
    "lat": 19.0760,
    "lon": 72.8777,
    "address": "Bandra West, Mumbai - Test Location",
    "accuracy": 10.5,
    "speed": 25.0,
    "heading": 45.0,
    "battery_level": 85
}'''
    print(f'curl -X POST "{base_url}/api/location/update" {headers} -d \'{location_data}\'')
    print()
    
    print("5. Testing Live Location:")
    print(f'curl -X GET "{base_url}/api/location/live/1201911108" {headers}')
    print()
    
    print("6. Testing Analytics:")
    print(f'curl -X GET "{base_url}/api/analytics/1201911108" {headers}')
    print()
    
    print("7. Testing Team Overview:")
    print(f'curl -X GET "{base_url}/api/analytics/team/overview" {headers}')
    print()
    
    print("8. Testing Dashboard:")
    print(f'curl -X GET "{base_url}/api/dashboard/overview" {headers}')
    print()

if __name__ == "__main__":
    test_with_curl()
