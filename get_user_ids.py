#!/usr/bin/env python3
"""
🔧 MR Bot User Authorization Helper
Simple way to check current authorized users and add new ones
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

def show_current_users():
    """Show currently authorized users"""
    authorized_ids = os.getenv('AUTHORIZED_MR_IDS', '1201911108')
    user_list = [id.strip() for id in authorized_ids.split(',') if id.strip()]
    
    print("� **Current Authorized Users:**")
    print("━" * 40)
    for i, user_id in enumerate(user_list, 1):
        print(f"  {i}. User ID: {user_id}")
    print("━" * 40)
    return user_list

def add_user(new_user_id):
    """Add a new user to authorized list"""
    try:
        # Read current .env
        env_path = '.env'
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Find and update AUTHORIZED_MR_IDS line
        updated_lines = []
        found = False
        
        for line in lines:
            if line.startswith('AUTHORIZED_MR_IDS='):
                current_ids = line.split('=')[1].strip()
                if new_user_id not in current_ids:
                    new_line = f"AUTHORIZED_MR_IDS={current_ids},{new_user_id}\n"
                    updated_lines.append(new_line)
                    print(f"✅ Added user {new_user_id} to authorized list")
                    found = True
                else:
                    updated_lines.append(line)
                    print(f"ℹ️ User {new_user_id} already authorized")
                    found = True
            else:
                updated_lines.append(line)
        
        if not found:
            updated_lines.append(f"AUTHORIZED_MR_IDS=1201911108,{new_user_id}\n")
            print(f"✅ Created new AUTHORIZED_MR_IDS with user {new_user_id}")
        
        # Write back to .env
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)
            
        print("💾 Updated .env file successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env: {e}")
        return False

def main():
    """Main interactive menu"""
    print("🤖 **MR Bot User Authorization Helper**")
    print("=" * 50)
    
    while True:
        print("\n📋 **Options:**")
        print("1. Show current authorized users")
        print("2. Add new user ID")
        print("3. Manual instructions")
        print("4. Exit")
        
        choice = input("\n👉 Enter choice (1-4): ").strip()
        
        if choice == '1':
            show_current_users()
            
        elif choice == '2':
            user_id = input("📱 Enter Telegram User ID to add: ").strip()
            if user_id and user_id.isdigit():
                add_user(user_id)
                print("\n🔄 **Next step:** Restart the bot with: python main.py")
            else:
                print("❌ Invalid User ID. Must be numbers only.")
                
        elif choice == '3':
            print("\n📖 **Manual Instructions:**")
            print("1. Get User ID from other mobile:")
            print("   - Send /start to your bot from that account")
            print("   - Check bot logs for 'User ID: XXXXXX'")
            print("   - Or ask user to forward any message to @userinfobot")
            print("\n2. Add to .env file:")
            print("   AUTHORIZED_MR_IDS=1201911108,NEW_USER_ID")
            print("\n3. Restart bot: python main.py")
            
        elif choice == '4':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()
