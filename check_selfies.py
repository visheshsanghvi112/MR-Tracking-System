"""Quick script to check current selfie data in database"""
from selfie_db import get_selfie_db

db = get_selfie_db()
selfies = db.get_all_selfies()

print(f"\n{'='*80}")
print(f"SELFIE DATABASE - {len(selfies)} Total Records")
print(f"{'='*80}\n")

if selfies:
    for i, selfie in enumerate(selfies, 1):
        print(f"{i}. MR ID: {selfie['user_id']}")
        print(f"   Timestamp: {selfie['timestamp']}")
        print(f"   Status: {selfie['verification_status']}")
        print(f"   Media Type: {selfie['media_type']}")
        print(f"   File ID: {selfie['file_id'][:50]}...")
        print(f"   Geofence: {selfie['geofence_status']}")
        print(f"   Distance: {selfie['distance_m']}m")
        print(f"   Created: {selfie['created_at']}")
        print()
else:
    print("No selfies found in database.")

# Get stats
stats = db.get_stats()
print(f"\n{'='*80}")
print("STATISTICS")
print(f"{'='*80}")
print(f"Total Selfies: {stats['total_selfies']}")
print(f"Unique Users: {stats['unique_users']}")
print(f"{'='*80}\n")
