#!/usr/bin/env python3
"""
🔍 Session Loop Debugging - Step by Step Analysis
This script will help identify WHY the session loop is happening
"""

import time
from session_manager import MRSession, mr_session_manager
from config import LOCATION_SESSION_DURATION, MAX_ENTRIES_PER_SESSION

def test_session_loop():
    """Test the exact sequence that causes the loop"""
    print("🔍 **DEBUGGING SESSION LOOP**")
    print("=" * 50)
    
    # Use the actual user ID from logs
    user_id = 5901220876
    
    print(f"📋 **Config Values:**")
    print(f"   Session Duration: {LOCATION_SESSION_DURATION}s ({LOCATION_SESSION_DURATION//3600}h)")
    print(f"   Max Entries: {MAX_ENTRIES_PER_SESSION}")
    print()
    
    # Step 1: Capture location (like user did)
    print("📍 **STEP 1: Capture Location**")
    lat, lon = 18.949368, 72.828954
    address = "Test Location"
    
    status_before = mr_session_manager.get_location_status(user_id)
    print(f"   Before: Active={status_before['active']}, Entries={status_before.get('entries_count', 0)}")
    
    result = mr_session_manager.capture_location(user_id, lat, lon, address)
    
    status_after = mr_session_manager.get_location_status(user_id)
    print(f"   After:  Active={status_after['active']}, Entries={status_after.get('entries_count', 0)}")
    print(f"   Time Remaining: {status_after['time_remaining']}s")
    print()
    
    # Step 2: Try to log entry (what happens next)
    print("📝 **STEP 2: Log Entry (Simulate Visit)**")
    can_log_before = mr_session_manager.can_log_entry(user_id)
    print(f"   Can log entry: {can_log_before}")
    
    if can_log_before:
        mr_session_manager.log_entry(user_id)
        status_after_log = mr_session_manager.get_location_status(user_id)
        print(f"   After Log: Active={status_after_log['active']}, Entries={status_after_log.get('entries_count', 0)}")
    else:
        print(f"   ❌ Cannot log entry!")
        return
    print()
    
    # Step 3: Wait a moment and check again (simulate time passing)
    print("⏳ **STEP 3: Simulate Time Passing (10 seconds)**")
    time.sleep(1)  # Short wait for testing
    
    status_later = mr_session_manager.get_location_status(user_id)
    print(f"   Later: Active={status_later['active']}, Entries={status_later.get('entries_count', 0)}")
    print(f"   Time Remaining: {status_later['time_remaining']}s")
    print()
    
    # Step 4: Try to capture location again (this is where loop might happen)
    print("📍 **STEP 4: Capture Location Again (Loop Check)**")
    status_before_2nd = mr_session_manager.get_location_status(user_id)
    print(f"   Before 2nd: Active={status_before_2nd['active']}, Entries={status_before_2nd.get('entries_count', 0)}")
    
    result2 = mr_session_manager.capture_location(user_id, lat, lon, address + " Updated")
    
    status_after_2nd = mr_session_manager.get_location_status(user_id)
    print(f"   After 2nd:  Active={status_after_2nd['active']}, Entries={status_after_2nd.get('entries_count', 0)}")
    print()
    
    # Final check
    print("🎯 **FINAL STATUS**")
    if status_after_2nd.get('entries_count', 0) > 0:
        print("   ✅ SUCCESS: Entry count preserved!")
        print("   ✅ No session loop detected")
    else:
        print("   ❌ BUG: Entry count reset to 0!")
        print("   ❌ Session loop detected!")
    
    return status_after_2nd.get('entries_count', 0) > 0

if __name__ == "__main__":
    success = test_session_loop()
    if success:
        print("\n🎉 Session logic is working correctly!")
    else:
        print("\n🚨 Session loop bug still exists!")
