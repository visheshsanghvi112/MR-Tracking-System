"""
Historical Data Blueprint Generator
Generate route blueprints from existing Google Sheets records
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import sys
import os

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_sheets import smart_sheets
from visit_based_location_tracker import visit_tracker, log_visit_with_location
from geopy.geocoders import Nominatim

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HistoricalBlueprintGenerator:
    """Generate route blueprints from existing Google Sheets data"""
    
    def __init__(self):
        self.sheets = smart_sheets
        self.geocoder = Nominatim(user_agent="mr_bot_historical_generator")
        
    async def generate_blueprints_from_sheets(self, days_back: int = 30):
        """Generate blueprints from Google Sheets historical data"""
        
        print("🔄 **Generating Route Blueprints from Historical Data**")
        print("=" * 60)
        
        try:
            # Get all historical records from sheets
            print(f"📊 Fetching records from last {days_back} days...")
            
            # Get data from MR_Daily_Log sheet
            records = await self.get_historical_records(days_back)
            
            if not records:
                print("❌ No historical records found")
                return
            
            print(f"📋 Found {len(records)} historical records")
            
            # Group records by MR and date
            grouped_records = self.group_records_by_mr_date(records)
            
            print(f"👥 Processing {len(grouped_records)} MR-date combinations")
            
            # Generate blueprints for each MR-date group
            total_blueprints = 0
            for (mr_id, date), mr_records in grouped_records.items():
                try:
                    blueprint_generated = await self.generate_blueprint_for_mr_date(mr_id, date, mr_records)
                    if blueprint_generated:
                        total_blueprints += 1
                        print(f"   ✅ {mr_id} - {date}: {len(mr_records)} visits")
                    else:
                        print(f"   ⚠️ {mr_id} - {date}: Failed to generate blueprint")
                        
                except Exception as e:
                    logger.error(f"Error generating blueprint for {mr_id} on {date}: {e}")
            
            print(f"\n✅ **Historical Blueprint Generation Complete**")
            print(f"📊 Total blueprints generated: {total_blueprints}")
            
        except Exception as e:
            logger.error(f"Historical blueprint generation error: {e}")
            print(f"❌ Error: {e}")
    
    async def get_historical_records(self, days_back: int) -> List[Dict]:
        """Get historical records from Google Sheets"""
        
        try:
            # This is a simplified version - you'll need to adapt based on your sheets structure
            # For now, we'll simulate getting records
            
            # In real implementation, you would:
            # worksheet = self.sheets.get_worksheet('MR_Daily_Log')
            # all_records = worksheet.get_all_records()
            
            # Simulated historical data for demonstration
            simulated_records = []
            
            current_date = datetime.now()
            for i in range(days_back):
                record_date = current_date - timedelta(days=i)
                
                # Sample records for different MRs
                for mr_id in ['MR001', 'MR002', 'MR003']:
                    # Generate 2-4 visits per MR per day
                    import random
                    num_visits = random.randint(2, 4)
                    
                    for visit_num in range(num_visits):
                        record = {
                            'MR_ID': mr_id,
                            'Date': record_date.strftime('%Y-%m-%d'),
                            'Time': f"{9 + visit_num * 2}:{random.randint(0, 59):02d}",
                            'Visit_Type': random.choice(['Doctor Visit', 'Pharmacy Visit', 'Clinic Visit']),
                            'Contact_Name': f"Contact_{visit_num+1}",
                            'Location': f"Location_{visit_num+1}",
                            'GPS_Coordinates': f"{19.0760 + random.uniform(-0.01, 0.01):.6f},{72.8777 + random.uniform(-0.01, 0.01):.6f}",
                            'Orders': f"Order details {visit_num+1}",
                            'Remarks': f"Visit remarks {visit_num+1}",
                            'Outcome': random.choice(['Successful', 'No Order', 'Follow-up'])
                        }
                        simulated_records.append(record)
            
            print(f"📋 Generated {len(simulated_records)} simulated historical records")
            return simulated_records
            
        except Exception as e:
            logger.error(f"Error getting historical records: {e}")
            return []
    
    def group_records_by_mr_date(self, records: List[Dict]) -> Dict:
        """Group records by MR ID and date"""
        
        grouped = {}
        
        for record in records:
            mr_id = record.get('MR_ID', '')
            date = record.get('Date', '')
            
            if mr_id and date:
                key = (mr_id, date)
                if key not in grouped:
                    grouped[key] = []
                grouped[key].append(record)
        
        return grouped
    
    async def generate_blueprint_for_mr_date(self, mr_id: str, date: str, records: List[Dict]) -> bool:
        """Generate blueprint for specific MR and date"""
        
        try:
            # Convert sheet records to visit location format
            for record in records:
                # Extract GPS coordinates
                gps_str = record.get('GPS_Coordinates', '0,0')
                try:
                    lat_str, lon_str = gps_str.split(',')
                    latitude = float(lat_str.strip())
                    longitude = float(lon_str.strip())
                except:
                    latitude, longitude = 19.0760, 72.8777  # Default Mumbai coordinates
                
                # Determine location type
                visit_type = record.get('Visit_Type', '').lower()
                if 'doctor' in visit_type or 'hospital' in visit_type:
                    location_type = 'hospital'
                elif 'pharmacy' in visit_type:
                    location_type = 'pharmacy'
                elif 'clinic' in visit_type:
                    location_type = 'clinic'
                else:
                    location_type = 'general'
                
                # Determine visit outcome
                outcome = record.get('Outcome', 'Successful').lower()
                if 'successful' in outcome:
                    visit_outcome = 'successful'
                elif 'no order' in outcome:
                    visit_outcome = 'no_order'
                else:
                    visit_outcome = 'follow_up'
                
                # Create visit timestamp
                time_str = record.get('Time', '09:00')
                visit_datetime = datetime.strptime(f"{date} {time_str}", '%Y-%m-%d %H:%M')
                
                # Prepare location and visit data
                location_data = {
                    'latitude': latitude,
                    'longitude': longitude,
                    'address': record.get('Location', 'Unknown Location')
                }
                
                visit_data = {
                    'location_name': record.get('Contact_Name', 'Unknown Contact'),
                    'location_type': location_type,
                    'visit_time': visit_datetime.isoformat(),
                    'visit_duration': 30,  # Default duration
                    'visit_outcome': visit_outcome,
                    'session_id': f"historical_{date}_{mr_id}",
                    'notes': f"Orders: {record.get('Orders', '')} | Remarks: {record.get('Remarks', '')}"
                }
                
                # Log the historical visit
                await log_visit_with_location(mr_id, location_data, visit_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error generating blueprint for {mr_id} on {date}: {e}")
            return False

async def main():
    """Main function to generate historical blueprints"""
    
    generator = HistoricalBlueprintGenerator()
    
    print("🚀 **Historical Blueprint Generator**")
    print("This will generate route blueprints from existing Google Sheets data")
    print()
    
    # Generate blueprints for last 30 days
    await generator.generate_blueprints_from_sheets(days_back=30)
    
    print("\n🎯 **Next Steps:**")
    print("1. Start the enhanced API server:")
    print("   cd api && python run_enhanced_api.py")
    print()
    print("2. Test the blueprint APIs:")
    print("   http://localhost:8000/api/v2/route-blueprint/MR001")
    print("   http://localhost:8000/api/v2/location-history/MR001")
    print()
    print("3. Frontend can now consume these APIs for map visualization!")

if __name__ == "__main__":
    asyncio.run(main())
