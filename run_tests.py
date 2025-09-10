#!/usr/bin/env python3
"""
Simple test runner for MR Tracking API
Usage: python run_tests.py
"""
import subprocess
import sys
import os

def run_tests():
    """Run the API test suite"""
    print("🚀 Running MR Tracking API Tests")
    print("=" * 50)

    # Check if API server is running
    try:
        import requests
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code != 200:
            print("⚠️  Warning: API server may not be running on port 8000")
    except:
        print("⚠️  Warning: Could not connect to API server on port 8000")
        print("   Make sure to start the server first: python main.py")

    # Run the test suite
    try:
        result = subprocess.run([
            sys.executable,
            "api/test_api.py"
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))

        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
