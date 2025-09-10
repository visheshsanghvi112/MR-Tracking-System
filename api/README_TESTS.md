# MR Tracking API Test Suite

This directory contains comprehensive tests for the MR Tracking API.

## Files

- `test_api.py` - Main test suite with all API endpoint tests
- `run_tests.py` - Simple test runner script

## Setup

1. Install test dependencies:
```bash
pip install -r requirements.txt
```

2. Start the API server:
```bash
python main.py
```

3. Run the tests:
```bash
python run_tests.py
```

Or run tests directly:
```bash
python api/test_api.py
```

## Test Coverage

The test suite covers:

- ✅ API Status and Health Checks
- ✅ MR Data Retrieval
- ✅ Route Data and Location Tracking
- ✅ Analytics and Dashboard Stats
- ✅ Activity Feed
- ✅ Location Updates
- ✅ GPX Export Functionality
- ✅ Team Analytics
- ✅ Authentication (API Key validation)
- ✅ Error Handling

## Test Results

After running tests, detailed results are saved to:
- `api_test_results.json` - Complete test results with timestamps

## Configuration

Tests use these default settings:
- Base URL: `http://localhost:8000`
- API Key: `mr-tracking-2025`
- Test MR ID: `1201911108`

Modify the `MRTrackingAPITester` class in `test_api.py` to change these settings.

## Sample Test Output

```
🚀 Starting MR Tracking API Test Suite
==================================================
🧪 Testing API Status...
✅ API Status: PASSED
🧪 Testing Health Check...
✅ Health Check: PASSED
...
==================================================
📊 TEST SUMMARY
==================================================
Total Tests: 11
Passed: 11
Failed: 0
Success Rate: 100.0%
🎉 ALL TESTS PASSED!
```
