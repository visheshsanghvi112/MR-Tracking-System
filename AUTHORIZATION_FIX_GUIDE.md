# 🔐 MR Bot Authorization Guide

## 🚫 **Problem**: "Access Denied" for New Users

When you try to use the bot from a different mobile account, you get:
```
❌ Access denied. You are not authorized to use this MR Bot.
```

## 🔍 **Why This Happens**

Each Telegram account has a unique **User ID** (like `1201911108`). The bot only allows users whose IDs are in the `AUTHORIZED_MR_IDS` list.

**Current authorized users**: Only `1201911108`

## 🛠️ **How to Fix - Method 1: Get User ID First**

### Step 1: Run the User ID Checker
```bash
cd "d:\mr_bot"
python get_user_ids.py
```

### Step 2: Send Message from New Account
- Open Telegram on the new mobile account
- Send any message to your MR Bot
- The bot will reply with the User ID

### Step 3: Add User ID to .env
Edit `d:\mr_bot\.env` file:
```bash
# OLD (only one user):
AUTHORIZED_MR_IDS=1201911108

# NEW (multiple users):
AUTHORIZED_MR_IDS=1201911108,NEW_USER_ID_HERE
```

### Step 4: Restart Bot
```bash
# Kill existing bot
taskkill /f /im python.exe

# Start fresh
python main.py
```

## 🛠️ **How to Fix - Method 2: Add Common IDs**

If you know the User IDs already, directly update `.env`:

```bash
# Multiple MR users
AUTHORIZED_MR_IDS=1201911108,123456789,987654321

# Format: comma-separated, no spaces
```

## 🎯 **Quick Commands**

### Get current authorized IDs:
```bash
python -c "from config import AUTHORIZED_MR_IDS; print('Authorized Users:', AUTHORIZED_MR_IDS)"
```

### Test authorization:
```bash
python -c "
import config
test_id = 123456789  # Replace with actual ID
if test_id in config.AUTHORIZED_MR_IDS:
    print('✅ User authorized')
else:
    print('❌ User NOT authorized')
    print('Current authorized:', config.AUTHORIZED_MR_IDS)
"
```

## 📋 **Example .env Configuration**

```bash
# MR Bot Environment Configuration
MR_BOT_TOKEN=8269645225:AAFx7qqNSMhMMSA8ZhaqnOBslbBREhJY7Wg
ADMIN_ID=1201911108

# Authorized MR User IDs (comma-separated)
AUTHORIZED_MR_IDS=1201911108,123456789,987654321,555444333

# Rest of config...
LOCATION_SESSION_DURATION=7200
MAX_ENTRIES_PER_SESSION=20
```

## 🔄 **After Making Changes**

1. **Save .env file**
2. **Restart the bot**:
   ```bash
   taskkill /f /im python.exe
   python main.py
   ```
3. **Test from new account** - should work now! ✅

## 🎉 **What Changes**

**Before**: Only `1201911108` can use bot
**After**: All users in `AUTHORIZED_MR_IDS` can use bot

Each authorized user gets:
- ✅ Location capture
- ✅ Visit logging  
- ✅ Expense tracking
- ✅ Full MR functionality
