"""Check selfies from today"""
from selfie_db import get_selfie_db
from datetime import datetime

db = get_selfie_db()
selfies = db.get_all_selfies()

# Filter for today
today = '2025-11-08'
today_selfies = [s for s in selfies if s['timestamp'].startswith(today)]

print(f"\n{'='*80}")
print(f"SELFIES FROM TODAY ({today})")
print(f"{'='*80}\n")
print(f"Total: {len(today_selfies)} selfies\n")

if today_selfies:
    for i, selfie in enumerate(today_selfies, 1):
        print(f"{i}. MR ID: {selfie['user_id']}")
        print(f"   Time: {selfie['timestamp']}")
        print(f"   Status: {selfie['verification_status']}")
        print(f"   Geofence: {selfie['geofence_status']}")
        print(f"   Distance: {selfie['distance_m']}m")
        print(f"   File ID: {selfie['file_id'][:60]}...")
        print()
else:
    print("❌ No selfies recorded today yet.")
    print("\nNote: The bot needs to be running to capture new selfies.")
    print("All existing selfies are from November 4, 2025.")

print(f"{'='*80}\n")
