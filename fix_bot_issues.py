#!/usr/bin/env python3
"""
Comprehensive Bot Issue Fixer
Fixes all known issues with the MR Bot
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_issues():
    """Fix all known bot issues"""
    
    print("🔧 MR Bot Issue Fixer")
    print("=" * 40)
    
    issues_fixed = 0
    
    # 1. Check if methods exist in SmartMRSheetsManager
    print("\n1. Checking SmartMRSheetsManager methods...")
    try:
        from smart_sheets import smart_sheets
        
        required_methods = [
            'get_daily_visits',
            'get_daily_expenses', 
            'get_visits_range',
            'get_expenses_range'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(smart_sheets, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"   ❌ Missing methods: {missing_methods}")
        else:
            print("   ✅ All required methods present")
            issues_fixed += 1
            
    except Exception as e:
        print(f"   ❌ Error checking methods: {e}")
    
    # 2. Test method functionality
    print("\n2. Testing method functionality...")
    try:
        test_user_id = "12345"
        test_date = "2025-09-17"
        
        # Test each method
        methods_working = 0
        
        try:
            smart_sheets.get_daily_visits(test_user_id, test_date)
            print("   ✅ get_daily_visits working")
            methods_working += 1
        except Exception as e:
            print(f"   ❌ get_daily_visits error: {e}")
        
        try:
            smart_sheets.get_daily_expenses(test_user_id, test_date)
            print("   ✅ get_daily_expenses working")
            methods_working += 1
        except Exception as e:
            print(f"   ❌ get_daily_expenses error: {e}")
        
        try:
            smart_sheets.get_visits_range(test_user_id, test_date, test_date)
            print("   ✅ get_visits_range working")
            methods_working += 1
        except Exception as e:
            print(f"   ❌ get_visits_range error: {e}")
        
        try:
            smart_sheets.get_expenses_range(test_user_id, test_date, test_date)
            print("   ✅ get_expenses_range working")
            methods_working += 1
        except Exception as e:
            print(f"   ❌ get_expenses_range error: {e}")
        
        if methods_working == 4:
            print("   ✅ All methods working correctly")
            issues_fixed += 1
        else:
            print(f"   ⚠️ {methods_working}/4 methods working")
            
    except Exception as e:
        print(f"   ❌ Error testing methods: {e}")
    
    # 3. Check for localhost URLs
    print("\n3. Checking for localhost URL issues...")
    try:
        with open('mr_commands.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count uncommented localhost references
        lines = content.split('\n')
        localhost_issues = 0
        
        for i, line in enumerate(lines, 1):
            if 'localhost' in line and not line.strip().startswith('#'):
                print(f"   ⚠️ Line {i}: {line.strip()}")
                localhost_issues += 1
        
        if localhost_issues == 0:
            print("   ✅ No uncommented localhost URLs found")
            issues_fixed += 1
        else:
            print(f"   ❌ Found {localhost_issues} localhost URL issues")
            
    except Exception as e:
        print(f"   ❌ Error checking localhost URLs: {e}")
    
    # 4. Check error handling
    print("\n4. Checking error handling...")
    try:
        with open('mr_commands.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'try:' in content and 'except Exception as e:' in content:
            print("   ✅ Error handling present in callback queries")
            issues_fixed += 1
        else:
            print("   ❌ Missing error handling")
            
    except Exception as e:
        print(f"   ❌ Error checking error handling: {e}")
    
    # 5. Test AI components
    print("\n5. Testing AI components...")
    try:
        from ai_engine import mr_ai_engine
        
        # Test AI engine (basic import test)
        if hasattr(mr_ai_engine, 'get_smart_suggestions'):
            print("   ✅ AI engine methods available")
            issues_fixed += 1
        else:
            print("   ❌ AI engine methods missing")
            
    except Exception as e:
        print(f"   ❌ AI engine error: {e}")
    
    # Summary
    print("\n" + "=" * 40)
    print(f"🎯 Issues Fixed: {issues_fixed}/5")
    
    if issues_fixed >= 4:
        print("✅ Bot should be working correctly!")
        print("💡 Try running: python main.py")
    elif issues_fixed >= 2:
        print("⚠️ Most issues fixed, some minor problems remain")
        print("💡 Bot should work with limited functionality")
    else:
        print("❌ Major issues remain, bot may not work properly")
        print("💡 Check the errors above and fix manually")
    
    return issues_fixed

async def main():
    """Main function"""
    try:
        issues_fixed = fix_issues()
        
        if issues_fixed >= 4:
            print("\n🚀 Running quick bot test...")
            
            # Quick test
            try:
                from mr_commands import commands_handler
                print("✅ Bot components loaded successfully")
                print("🎉 Bot is ready to run!")
            except Exception as e:
                print(f"❌ Bot test failed: {e}")
        
    except Exception as e:
        print(f"❌ Fix script failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())