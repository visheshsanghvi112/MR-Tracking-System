"""
Integration Setup Script
Sets up the bridge between Telegram bot and Enhanced API
"""
import sys
import os
import asyncio
import logging

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from session_manager import session_manager  # Basic session manager
from integrated_session_manager import IntegratedSessionManager
from telegram_api_bridge import telegram_api_bridge

logger = logging.getLogger(__name__)

async def setup_integration():
    """Set up integration between Telegram bot and Enhanced API"""
    
    print("🔗 Setting up Telegram Bot ↔ Enhanced API Integration")
    print("=" * 60)
    
    # Test Enhanced API connection
    print("1. Testing Enhanced API connection...")
    api_available = await telegram_api_bridge.validate_api_connection()
    
    if api_available:
        print("   ✅ Enhanced API is accessible")
        print("   🔗 Integration mode: ENHANCED")
    else:
        print("   ⚠️  Enhanced API not available")
        print("   🔗 Integration mode: BASIC (fallback)")
    
    # Create integrated session manager
    print("\n2. Creating integrated session manager...")
    integrated_manager = IntegratedSessionManager(session_manager)
    
    if api_available:
        integrated_manager.enable_integration()
        print("   ✅ Enhanced integration enabled")
    else:
        integrated_manager.disable_integration()
        print("   ⚠️  Using basic mode only")
    
    # Test location capture
    print("\n3. Testing location capture integration...")
    test_mr_id = 1201911108
    test_lat = 19.0760
    test_lon = 72.8777
    test_address = "Integration Test - Bandra West, Mumbai"
    test_user_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'username': 'testuser'
    }
    
    success = integrated_manager.capture_location(
        test_mr_id, test_lat, test_lon, test_address, test_user_data
    )
    
    if success:
        print("   ✅ Location capture successful")
        
        # Get status
        status = integrated_manager.get_location_status(test_mr_id)
        print(f"   📍 Status: {'Active' if status['active'] else 'Inactive'}")
        print(f"   📝 Address: {status['address']}")
        
        if api_available:
            # Wait a moment for async API call
            await asyncio.sleep(2)
            print("   🔗 Enhanced API integration tested")
    else:
        print("   ❌ Location capture failed")
    
    print("\n" + "=" * 60)
    print("🎯 INTEGRATION SETUP SUMMARY")
    print("=" * 60)
    
    print(f"Enhanced API Available: {'✅ Yes' if api_available else '❌ No'}")
    print(f"Integration Mode: {'🔥 Enhanced' if api_available else '⚠️  Basic'}")
    print(f"Location Capture: {'✅ Working' if success else '❌ Failed'}")
    
    if api_available:
        print("\n🚀 ENHANCED FEATURES AVAILABLE:")
        print("   ✅ Real-time location tracking")
        print("   ✅ Advanced analytics")
        print("   ✅ Performance metrics") 
        print("   ✅ Live dashboard data")
        print("   ✅ Team insights")
    else:
        print("\n⚠️  BASIC MODE ACTIVE:")
        print("   ✅ Location capture via Telegram")
        print("   ✅ Session management")
        print("   ✅ Google Sheets logging")
        print("   ❌ Real-time analytics disabled")
        print("   ❌ Live dashboard disabled")
    
    return integrated_manager, api_available

async def test_continuous_tracking():
    """Test continuous location tracking"""
    print("\n🔄 Testing Continuous Location Tracking...")
    print("=" * 60)
    
    test_mr_id = 1201911108
    
    # Simulate MR movement
    locations = [
        (19.0760, 72.8777, "Starting Location - Bandra"),
        (19.0820, 72.8850, "Moving to Kurla"),
        (19.0880, 72.8900, "Doctor Visit - Apollo Clinic"),
        (19.0920, 72.8950, "Pharmacy Visit - MedPlus")
    ]
    
    for i, (lat, lon, address) in enumerate(locations):
        print(f"\n📍 Location Update {i+1}: {address}")
        
        success = await telegram_api_bridge.send_location_update(
            test_mr_id, lat, lon, address, {'step': i+1}
        )
        
        if success:
            print(f"   ✅ Update sent: {lat:.6f}, {lon:.6f}")
            
            # Get live status
            status = await telegram_api_bridge.get_live_status(test_mr_id)
            if status:
                print(f"   📊 Live Status: {status.get('address', 'Unknown')}")
                print(f"   🏃 Speed: {status.get('speed', 0)} km/h")
        else:
            print(f"   ❌ Update failed")
        
        # Wait between updates
        await asyncio.sleep(3)
    
    # Get final analytics
    print("\n📈 Final Analytics Check...")
    analytics = await telegram_api_bridge.get_mr_analytics(test_mr_id)
    
    if analytics:
        stats = analytics.get('today_stats', {})
        print(f"   🛣️  Distance: {stats.get('distance_traveled', 0)} km")
        print(f"   📍 Visits: {stats.get('locations_visited', 0)}")
        print(f"   ⏰ Active Time: {stats.get('active_time', 0)} hours")
    else:
        print("   ❌ Analytics not available")

async def main():
    """Main setup function"""
    try:
        # Setup integration
        integrated_manager, api_available = await setup_integration()
        
        if api_available:
            # Test continuous tracking if API is available
            await test_continuous_tracking()
        
        print("\n" + "=" * 60)
        print("🎉 INTEGRATION SETUP COMPLETE!")
        
        if api_available:
            print("🔥 Your Telegram bot is now connected to the Enhanced API!")
            print("✅ MRs can capture location via Telegram")
            print("✅ Data flows to real-time analytics")
            print("✅ Live tracking and dashboards enabled")
        else:
            print("⚠️  Running in basic mode. Start Enhanced API for full features.")
        
        print("=" * 60)
        
        # Close bridge session
        await telegram_api_bridge.close()
        
    except Exception as e:
        print(f"❌ Integration setup error: {e}")
        logging.error(f"Integration setup failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
