"""
Mobile App Simulator for MR Live Tracking
Simulates MR field representatives sending live location updates
"""
import asyncio
import aiohttp
import json
import random
import time
from datetime import datetime
from typing import List, Tuple

class MRSimulator:
    """Simulates an MR moving in the field"""
    
    def __init__(self, mr_id: int, api_base_url: str = "http://localhost:8000"):
        self.mr_id = mr_id
        self.api_base_url = api_base_url
        self.current_lat = 19.0760  # Mumbai starting point
        self.current_lon = 72.8777
        self.speed = 0.0  # km/h
        self.heading = 0.0  # degrees
        self.battery_level = 100
        self.is_moving = True
        
        # Predefined route points (Mumbai area)
        self.route_points = [
            (19.0760, 72.8777, "Home - Bandra West"),
            (19.0820, 72.8850, "Dr. Sharma Clinic"),
            (19.0880, 72.8900, "Apollo Pharmacy"),
            (19.0920, 72.8950, "City Hospital"),
            (19.0860, 72.8800, "Medicare Center"),
            (19.0780, 72.8720, "Health Plus Clinic"),
            (19.0740, 72.8680, "Wellness Pharmacy")
        ]
        self.route_index = 0
        
    async def start_simulation(self, duration_minutes: int = 60):
        """Start location simulation for specified duration"""
        print(f"Starting MR {self.mr_id} simulation for {duration_minutes} minutes")
        
        end_time = time.time() + (duration_minutes * 60)
        
        while time.time() < end_time:
            try:
                # Simulate movement
                await self.simulate_movement()
                
                # Send location update
                await self.send_location_update()
                
                # Wait 10-30 seconds between updates
                await asyncio.sleep(random.uniform(10, 30))
                
            except Exception as e:
                print(f"Simulation error: {e}")
                await asyncio.sleep(5)
                
        print(f"MR {self.mr_id} simulation completed")
        
    async def simulate_movement(self):
        """Simulate realistic movement between locations"""
        if not self.is_moving:
            return
            
        # Get next destination
        target_lat, target_lon, location_name = self.route_points[self.route_index]
        
        # Calculate distance to target
        from geopy.distance import geodesic
        current_pos = (self.current_lat, self.current_lon)
        target_pos = (target_lat, target_lon)
        distance_to_target = geodesic(current_pos, target_pos).kilometers
        
        # If close to target, move to next point
        if distance_to_target < 0.05:  # 50 meters
            self.route_index = (self.route_index + 1) % len(self.route_points)
            self.is_moving = random.choice([True, True, False])  # 66% chance to keep moving
            
            if not self.is_moving:
                print(f"MR {self.mr_id} stopped at {location_name}")
                # Stop for 2-5 minutes
                await asyncio.sleep(random.uniform(120, 300))
                self.is_moving = True
            
            return
            
        # Move toward target
        movement_speed = random.uniform(0.001, 0.003)  # Realistic walking/driving speed
        
        # Calculate direction
        lat_diff = target_lat - self.current_lat
        lon_diff = target_lon - self.current_lon
        
        # Move a fraction of the way
        self.current_lat += lat_diff * movement_speed
        self.current_lon += lon_diff * movement_speed
        
        # Update speed and heading
        self.speed = random.uniform(3, 25)  # 3-25 km/h
        self.heading = random.uniform(0, 360)
        
        # Battery drain simulation
        self.battery_level = max(10, self.battery_level - random.uniform(0.1, 0.3))
        
    async def send_location_update(self):
        """Send location update to API"""
        try:
            # Get current location name
            current_location = self.get_current_location_name()
            
            location_data = {
                "mr_id": self.mr_id,
                "lat": round(self.current_lat, 6),
                "lon": round(self.current_lon, 6),
                "address": current_location,
                "accuracy": random.uniform(5, 20),  # GPS accuracy in meters
                "speed": self.speed,
                "heading": self.heading,
                "battery_level": int(self.battery_level)
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base_url}/api/location/update"
                
                async with session.post(url, json=location_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"MR {self.mr_id}: Location update sent - {current_location} (Speed: {self.speed:.1f} km/h)")
                    else:
                        print(f"MR {self.mr_id}: Failed to send location update - Status: {response.status}")
                        
        except Exception as e:
            print(f"MR {self.mr_id}: Error sending location: {e}")
            
    def get_current_location_name(self) -> str:
        """Get descriptive name for current location"""
        # Find closest route point
        min_distance = float('inf')
        closest_location = "Field Location"
        
        from geopy.distance import geodesic
        current_pos = (self.current_lat, self.current_lon)
        
        for lat, lon, name in self.route_points:
            distance = geodesic(current_pos, (lat, lon)).kilometers
            if distance < min_distance:
                min_distance = distance
                closest_location = name
                
        # Add movement status
        if min_distance < 0.1:  # Within 100m
            return closest_location
        else:
            return f"En Route to {closest_location}"

class MultiMRSimulator:
    """Manages multiple MR simulations"""
    
    def __init__(self, mr_ids: List[int], api_base_url: str = "http://localhost:8000"):
        self.simulators = [MRSimulator(mr_id, api_base_url) for mr_id in mr_ids]
        self.api_base_url = api_base_url
        
    async def start_team_simulation(self, duration_minutes: int = 60):
        """Start simulation for all MRs"""
        print(f"Starting team simulation with {len(self.simulators)} MRs")
        
        # Start all simulations concurrently
        tasks = []
        for simulator in self.simulators:
            task = asyncio.create_task(simulator.start_simulation(duration_minutes))
            tasks.append(task)
            
        # Wait for all simulations to complete
        await asyncio.gather(*tasks)
        
        print("Team simulation completed")
        
    async def test_api_connection(self):
        """Test API connection"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/api/health") as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"API Connection: OK - {result['status']}")
                        return True
                    else:
                        print(f"API Connection: Failed - Status {response.status}")
                        return False
        except Exception as e:
            print(f"API Connection Error: {e}")
            return False

async def main():
    """Main simulation function"""
    print("=== MR Live Tracking Simulation ===")
    
    # Configure MR IDs to simulate
    mr_ids = [1201911108, 987654321, 123456789]
    
    # Create multi-MR simulator
    simulator = MultiMRSimulator(mr_ids)
    
    # Test API connection first
    if not await simulator.test_api_connection():
        print("Cannot connect to API. Make sure the server is running on http://localhost:8000")
        return
        
    print("API connection successful. Starting simulation...")
    
    # Start simulation (30 minutes for demo)
    await simulator.start_team_simulation(duration_minutes=30)

if __name__ == "__main__":
    asyncio.run(main())
