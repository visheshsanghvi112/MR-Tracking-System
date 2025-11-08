"""Check if today's 8:02 AM selfie is in the database"""
from selfie_db import get_selfie_db

db = get_selfie_db()
selfies = db.get_all_selfies()

# The selfie you just shared
target_file_id = "AgACAgUAAxkBAAIO9GkO-RBq04Ae78xH14RZZeM6A3EtAAIlDGsbh0h5VCkAAdDZpugBuAEAAwIAA3kAAzYE"
target_time = "2025-11-08 08:02:31"
target_mr = "1201911108"

print(f"\n{'='*80}")
print("CHECKING FOR TODAY'S 8:02 AM SELFIE")
print(f"{'='*80}\n")
print(f"Target MR ID: {target_mr}")
print(f"Target Time: {target_time}")
print(f"Target File ID: {target_file_id[:60]}...")
print()

# Search for exact match
exact_match = [s for s in selfies if s['file_id'] == target_file_id]

if exact_match:
    print("✅ FOUND IN DATABASE!\n")
    selfie = exact_match[0]
    print(f"   MR ID: {selfie['user_id']}")
    print(f"   Timestamp: {selfie['timestamp']}")
    print(f"   Status: {selfie['verification_status']}")
    print(f"   Geofence: {selfie['geofence_status']}")
    print(f"   Distance: {selfie['distance_m']}m")
else:
    print("❌ NOT FOUND IN DATABASE\n")
    print("This selfie needs to be added to the database.")
    print("\nChecking for any selfies from your MR today...")
    
    your_selfies_today = [s for s in selfies 
                          if str(s['user_id']) == target_mr 
                          and s['timestamp'].startswith('2025-11-08')]
    
    print(f"   Your MR (1201911108) selfies today: {len(your_selfies_today)}")
    if your_selfies_today:
        for s in your_selfies_today:
            print(f"   - {s['timestamp']}: {s['file_id'][:50]}...")

print(f"\n{'='*80}")
print(f"Total selfies in database: {len(selfies)}")
print(f"{'='*80}\n")
