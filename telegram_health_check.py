#!/usr/bin/env python3
"""
Telegram Bot Health Check
Fast verification of Telegram bot configuration and API connectivity
"""
import sys
import os
import requests
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

try:
    import config
except ImportError as e:
    print(f"[FAIL] Config import failed: {e}")
    sys.exit(1)

API_BASE = "http://localhost:8000"
API_KEY = "mr-tracking-2025"

def check_telegram_config():
    """Check Telegram bot configuration"""
    results = []
    
    # 1. Check bot token
    if not config.TELEGRAM_BOT_TOKEN:
        results.append("[FAIL] Bot Token: Not configured")
    else:
        token_preview = config.TELEGRAM_BOT_TOKEN[:10] + "..." if len(config.TELEGRAM_BOT_TOKEN) > 10 else "***"
        results.append(f"[OK] Bot Token: Configured ({token_preview})")
    
    # 2. Check authorized MR IDs
    if hasattr(config, 'AUTHORIZED_MR_IDS') and config.AUTHORIZED_MR_IDS:
        results.append(f"[OK] Authorized MRs: {len(config.AUTHORIZED_MR_IDS)} IDs")
        results.append(f"     IDs: {', '.join(map(str, config.AUTHORIZED_MR_IDS[:3]))}")
    else:
        results.append("[WARN] Authorized MRs: None (OPEN ACCESS - SECURITY RISK!)")
    
    # 3. Check Google Sheets config
    if hasattr(config, 'MR_SPREADSHEET_ID') and config.MR_SPREADSHEET_ID:
        results.append("[OK] Google Sheets: Spreadsheet ID configured")
    else:
        results.append("[WARN] Google Sheets: Spreadsheet ID missing")
    
    if hasattr(config, 'GOOGLE_SHEETS_CREDENTIALS'):
        creds_path = config.GOOGLE_SHEETS_CREDENTIALS
        if os.path.exists(creds_path):
            results.append(f"[OK] Google Sheets: Credentials found ({creds_path})")
        else:
            results.append(f"[FAIL] Google Sheets: Credentials missing ({creds_path})")
    
    # 4. Check session settings
    if hasattr(config, 'LOCATION_SESSION_DURATION'):
        duration_mins = config.LOCATION_SESSION_DURATION // 60
        results.append(f"[OK] Session Duration: {duration_mins} minutes")
    
    return results

def check_api_connection():
    """Check API backend connection"""
    results = []
    
    # 1. Check if API is running
    try:
        r = requests.get(f"{API_BASE}/", timeout=2)
        if r.status_code == 200:
            data = r.json()
            results.append(f"[OK] API Online: {data.get('service')} v{data.get('version')}")
        else:
            results.append(f"[FAIL] API Status: {r.status_code}")
            return results
    except Exception as e:
        results.append(f"[FAIL] API Connection: {str(e)[:50]}")
        return results
    
    # 2. Test API authentication
    try:
        r = requests.get(f"{API_BASE}/api/mrs", timeout=2)
        if r.status_code == 401:
            results.append("[OK] API Auth: Protected (requires API key)")
        else:
            results.append("[WARN] API Auth: Not properly protected")
    except:
        pass
    
    # 3. Test API with key
    try:
        r = requests.get(
            f"{API_BASE}/api/mrs",
            headers={"X-API-Key": API_KEY},
            timeout=2
        )
        if r.status_code == 200:
            data = r.json()
            results.append(f"[OK] API Bridge: {data.get('count', 0)} MRs accessible")
        else:
            results.append(f"[WARN] API Bridge: Status {r.status_code}")
    except Exception as e:
        results.append(f"[WARN] API Bridge: {str(e)[:50]}")
    
    # 4. Test location endpoint (used by Telegram bridge)
    try:
        r = requests.get(
            f"{API_BASE}/api/route?mr_id=8393304686&date=2025-10-27",
            headers={"X-API-Key": API_KEY},
            timeout=2
        )
        if r.status_code == 200:
            data = r.json()
            points = len(data.get('points', []))
            results.append(f"[OK] API Location: {points} GPS points available")
        else:
            results.append(f"[WARN] API Location: Status {r.status_code}")
    except Exception as e:
        results.append(f"[WARN] API Location: {str(e)[:50]}")
    
    return results

def check_bot_process():
    """Check if bot process might be running"""
    results = []
    
    try:
        import psutil
        bot_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'main.py' in cmdline and 'telegram' in cmdline.lower():
                    bot_processes.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if bot_processes:
            results.append(f"[OK] Bot Process: Running (PID: {', '.join(map(str, bot_processes))})")
        else:
            results.append("[WARN] Bot Process: Not detected (might not be running)")
    except ImportError:
        results.append("[INFO] Bot Process: Cannot check (psutil not installed)")
    except Exception as e:
        results.append(f"[INFO] Bot Process: Check failed - {str(e)[:30]}")
    
    return results

def main():
    """Run all health checks"""
    print("Telegram Bot Health Check...")
    print("-" * 50)
    
    all_results = []
    
    # Check Telegram config
    config_results = check_telegram_config()
    all_results.extend(config_results)
    
    # Check API connection
    api_results = check_api_connection()
    all_results.extend(api_results)
    
    # Check bot process
    process_results = check_bot_process()
    all_results.extend(process_results)
    
    # Print results
    for result in all_results:
        print(result)
    
    print("-" * 50)
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Summary
    fails = sum(1 for r in all_results if "[FAIL]" in r)
    warns = sum(1 for r in all_results if "[WARN]" in r)
    ok = sum(1 for r in all_results if "[OK]" in r)
    
    print(f"\nSummary: {ok} OK, {warns} Warnings, {fails} Failures")
    
    # Security warning
    if any("OPEN ACCESS" in r for r in all_results):
        print("\n*** SECURITY WARNING: Bot is open to everyone! ***")
    
    # Exit code
    if any("[FAIL]" in r for r in all_results):
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
