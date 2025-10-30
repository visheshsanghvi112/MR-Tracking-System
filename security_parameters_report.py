#!/usr/bin/env python3
"""
Security Parameters Report
Comprehensive analysis of all security settings in the MR Bot system
"""
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

try:
    import config
except ImportError:
    print("[FAIL] Cannot import config module")
    sys.exit(1)

API_KEY_DEFAULT = "mr-tracking-2025"
API_BASE = "http://localhost:8000"

def check_api_security():
    """Check API security parameters"""
    results = {
        "title": "API SECURITY PARAMETERS",
        "items": []
    }
    
    # 1. API Key
    api_key = os.getenv("API_KEY", API_KEY_DEFAULT)
    if api_key == API_KEY_DEFAULT:
        results["items"].append({
            "status": "CRITICAL",
            "parameter": "API_KEY",
            "value": "Using default 'mr-tracking-2025' (INSECURE)",
            "recommendation": "Generate secure key: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        })
    else:
        results["items"].append({
            "status": "OK",
            "parameter": "API_KEY",
            "value": f"Configured ({api_key[:10]}...)",
            "recommendation": None
        })
    
    # 2. CORS Configuration (check main.py)
    cors_status = "Check main.py - Line 95: allow_origins includes '*' (INSECURE)"
    results["items"].append({
        "status": "WARNING",
        "parameter": "CORS Origins",
        "value": "Currently allows all origins (*)",
        "recommendation": "Remove '*' and specify exact domains"
    })
    
    # 3. Environment Variables
    env_file_exists = any(os.path.exists(p) for p in [
        os.path.join(os.path.dirname(__file__), '.env'),
        os.path.join(os.path.dirname(__file__), '..', '.env'),
        '.env'
    ])
    
    if env_file_exists:
        results["items"].append({
            "status": "OK",
            "parameter": ".env File",
            "value": "Found",
            "recommendation": None
        })
    else:
        results["items"].append({
            "status": "WARNING",
            "parameter": ".env File",
            "value": "Not found",
            "recommendation": "Create .env file for secure credential storage"
        })
    
    return results

def check_telegram_security():
    """Check Telegram bot security parameters"""
    results = {
        "title": "TELEGRAM BOT SECURITY PARAMETERS",
        "items": []
    }
    
    # 1. Bot Token
    if config.TELEGRAM_BOT_TOKEN:
        token_preview = config.TELEGRAM_BOT_TOKEN[:10] + "..."
        results["items"].append({
            "status": "OK",
            "parameter": "Bot Token",
            "value": f"Configured ({token_preview})",
            "recommendation": None
        })
    else:
        results["items"].append({
            "status": "FAIL",
            "parameter": "Bot Token",
            "value": "Not configured",
            "recommendation": "Set MR_BOT_TOKEN in environment variables"
        })
    
    # 2. Authorized MR IDs
    if hasattr(config, 'AUTHORIZED_MR_IDS') and config.AUTHORIZED_MR_IDS:
        ids_str = ', '.join(map(str, config.AUTHORIZED_MR_IDS[:5]))
        if len(config.AUTHORIZED_MR_IDS) > 5:
            ids_str += f" (+{len(config.AUTHORIZED_MR_IDS) - 5} more)"
        
        # Check if authorization is enforced
        results["items"].append({
            "status": "WARNING",
            "parameter": "Authorized MR IDs",
            "value": f"{len(config.AUTHORIZED_MR_IDS)} IDs configured: {ids_str}",
            "recommendation": "CRITICAL: Check main.py line 121 - authorization may be disabled!"
        })
    else:
        results["items"].append({
            "status": "CRITICAL",
            "parameter": "Authorized MR IDs",
            "value": "No authorized IDs (OPEN ACCESS)",
            "recommendation": "Set AUTHORIZED_MR_IDS in config.py or .env"
        })
    
    # 3. Admin ID
    if hasattr(config, 'ADMIN_ID'):
        results["items"].append({
            "status": "OK",
            "parameter": "Admin ID",
            "value": f"Set to {config.ADMIN_ID}",
            "recommendation": None
        })
    else:
        results["items"].append({
            "status": "WARNING",
            "parameter": "Admin ID",
            "value": "Not configured",
            "recommendation": "Set ADMIN_ID in config.py"
        })
    
    # 4. Session Duration
    if hasattr(config, 'LOCATION_SESSION_DURATION'):
        duration_mins = config.LOCATION_SESSION_DURATION // 60
        results["items"].append({
            "status": "OK",
            "parameter": "Session Duration",
            "value": f"{duration_mins} minutes",
            "recommendation": None
        })
    
    return results

def check_integration_security():
    """Check third-party integration security"""
    results = {
        "title": "INTEGRATION SECURITY PARAMETERS",
        "items": []
    }
    
    # 1. Google Sheets Credentials
    if hasattr(config, 'GOOGLE_SHEETS_CREDENTIALS'):
        creds_path = config.GOOGLE_SHEETS_CREDENTIALS
        if os.path.exists(creds_path):
            # Check if it's the default path (potential security risk)
            if 'pharmagiftapp' in creds_path:
                results["items"].append({
                    "status": "OK",
                    "parameter": "Google Sheets Credentials",
                    "value": f"Found at {creds_path}",
                    "recommendation": "Ensure file is not committed to git (.gitignore)"
                })
            else:
                results["items"].append({
                    "status": "OK",
                    "parameter": "Google Sheets Credentials",
                    "value": f"Found at {creds_path}",
                    "recommendation": None
                })
        else:
            results["items"].append({
                "status": "FAIL",
                "parameter": "Google Sheets Credentials",
                "value": f"Missing: {creds_path}",
                "recommendation": "Download credentials JSON from Google Cloud Console"
            })
    
    # 2. Spreadsheet ID
    if hasattr(config, 'MR_SPREADSHEET_ID') and config.MR_SPREADSHEET_ID:
        results["items"].append({
            "status": "OK",
            "parameter": "Spreadsheet ID",
            "value": "Configured",
            "recommendation": None
        })
    else:
        results["items"].append({
            "status": "WARNING",
            "parameter": "Spreadsheet ID",
            "value": "Not configured",
            "recommendation": "Set MR_SPREADSHEET_ID in environment variables"
        })
    
    # 3. Gemini API Keys (optional)
    if hasattr(config, 'GEMINI_API_KEYS'):
        keys_count = sum(1 for k in config.GEMINI_API_KEYS if k)
        if keys_count > 0:
            results["items"].append({
                "status": "OK",
                "parameter": "Gemini API Keys",
                "value": f"{keys_count} key(s) configured",
                "recommendation": None
            })
        else:
            results["items"].append({
                "status": "INFO",
                "parameter": "Gemini API Keys",
                "value": "Not configured (optional)",
                "recommendation": None
            })
    
    return results

def check_data_security():
    """Check data handling security"""
    results = {
        "title": "DATA SECURITY PARAMETERS",
        "items": []
    }
    
    # 1. GPS Requirements
    if hasattr(config, 'GPS_REQUIRED'):
        results["items"].append({
            "status": "OK" if config.GPS_REQUIRED else "WARNING",
            "parameter": "GPS Required",
            "value": "Yes" if config.GPS_REQUIRED else "No (allows manual entry)",
            "recommendation": "Keep GPS_REQUIRED=True for data integrity" if not config.GPS_REQUIRED else None
        })
    
    # 2. Location Accuracy
    if hasattr(config, 'MIN_LOCATION_ACCURACY'):
        results["items"].append({
            "status": "OK",
            "parameter": "Min Location Accuracy",
            "value": f"{config.MIN_LOCATION_ACCURACY} meters",
            "recommendation": None
        })
    
    # 3. Max Entries Per Session
    if hasattr(config, 'MAX_ENTRIES_PER_SESSION'):
        results["items"].append({
            "status": "OK",
            "parameter": "Max Entries/Session",
            "value": f"{config.MAX_ENTRIES_PER_SESSION}",
            "recommendation": None
        })
    
    return results

def print_report():
    """Generate and print security report"""
    print("=" * 70)
    print("SECURITY PARAMETERS REPORT")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Collect all checks
    checks = [
        check_api_security(),
        check_telegram_security(),
        check_integration_security(),
        check_data_security()
    ]
    
    # Print each section
    for check in checks:
        print(check["title"])
        print("-" * 70)
        
        for item in check["items"]:
            status_symbol = {
                "OK": "[OK]",
                "WARNING": "[!]",
                "CRITICAL": "[X]",
                "FAIL": "[X]",
                "INFO": "[i]"
            }.get(item["status"], "[?]")
            
            print(f"{status_symbol} {item['parameter']:.<30} {item['value']}")
            
            if item["recommendation"]:
                print(f"    -> {item['recommendation']}")
        
        print()
    
    # Summary
    print("=" * 70)
    print("SECURITY SUMMARY")
    print("=" * 70)
    
    all_items = [item for check in checks for item in check["items"]]
    critical = sum(1 for item in all_items if item["status"] == "CRITICAL")
    warnings = sum(1 for item in all_items if item["status"] == "WARNING")
    fails = sum(1 for item in all_items if item["status"] == "FAIL")
    ok = sum(1 for item in all_items if item["status"] == "OK")
    
    print(f"[X] Critical Issues:  {critical}")
    print(f"[!] Warnings:         {warnings}")
    print(f"[X] Failures:         {fails}")
    print(f"[OK] OK:              {ok}")
    print()
    
    # Security Score
    total = len(all_items)
    score = int((ok / total) * 10) if total > 0 else 0
    
    # Penalties for critical issues
    score -= critical * 2
    score -= fails
    score = max(0, min(10, score))
    
    print(f"Security Score: {score}/10")
    print()
    
    if critical > 0 or fails > 0:
        print("*** CRITICAL ACTIONS REQUIRED ***")
        print("Review critical issues and failures above immediately!")
        return 1
    elif warnings > 0:
        print("*** WARNINGS DETECTED ***")
        print("Review warnings for potential security improvements.")
        return 0
    else:
        print("All security parameters are properly configured!")
        return 0

if __name__ == "__main__":
    sys.exit(print_report())

