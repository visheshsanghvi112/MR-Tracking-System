#!/usr/bin/env python3
"""
Combined Health Check
Quick check of both API and Telegram bot status
"""
import subprocess
import sys
import os
from datetime import datetime

def run_check(name, script_path):
    """Run a health check script and return results"""
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.path.dirname(script_path)
        )
        return result.stdout, result.returncode == 0
    except Exception as e:
        return f"Error running {name}: {str(e)}", False

def main():
    """Run combined health checks"""
    print("=" * 60)
    print("COMBINED HEALTH CHECK")
    print("=" * 60)
    print()
    
    # Get script paths
    api_path = os.path.join(os.path.dirname(__file__), "api", "health_check.py")
    telegram_path = os.path.join(os.path.dirname(__file__), "telegram_health_check.py")
    
    all_healthy = True
    
    # Check API
    print("1. API HEALTH CHECK")
    print("-" * 60)
    api_output, api_ok = run_check("API", api_path)
    print(api_output)
    if not api_ok:
        all_healthy = False
    print()
    
    # Check Telegram Bot
    print("2. TELEGRAM BOT HEALTH CHECK")
    print("-" * 60)
    telegram_output, telegram_ok = run_check("Telegram Bot", telegram_path)
    print(telegram_output)
    if not telegram_ok:
        all_healthy = False
    print()
    
    # Summary
    print("=" * 60)
    if all_healthy:
        print("[SUCCESS] All systems healthy!")
    else:
        print("[WARNING] Some checks failed - review output above")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sys.exit(0 if all_healthy else 1)

if __name__ == "__main__":
    main()

