"""
MR Bot Utilities
Essential utilities for MR Bot operations
"""
import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

def ensure_dir_exists(directory: str):
    """Ensure directory exists, create if not"""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def save_json(data: Dict, filepath: str):
    """Save data to JSON file"""
    try:
        ensure_dir_exists(os.path.dirname(filepath))
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {filepath}: {e}")
        return False

def load_json(filepath: str) -> Optional[Dict]:
    """Load data from JSON file"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {e}")
        return {}

def format_timestamp(dt: Optional[datetime] = None, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Format datetime to string"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)

def parse_date(date_str: str, fmt: str = '%Y-%m-%d') -> Optional[datetime]:
    """Parse date string to datetime object"""
    try:
        return datetime.strptime(date_str, fmt)
    except Exception:
        return None

def validate_phone_number(phone: str) -> bool:
    """Basic phone number validation"""
    # Remove spaces, dashes, parentheses
    cleaned = ''.join(c for c in phone if c.isdigit())
    return len(cleaned) >= 10

def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()

def format_currency(amount: float, currency: str = '₹') -> str:
    """Format currency amount"""
    return f"{currency}{amount:.2f}"

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def get_mr_name(user_id: int, user_data: dict = None) -> str:
    """Get MR display name from user data or fallback to ID"""
    if user_data:
        # Try to get actual name from Telegram user data
        first_name = user_data.get('first_name', '')
        last_name = user_data.get('last_name', '')
        username = user_data.get('username', '')
        
        if first_name and last_name:
            return f"{first_name} {last_name}"
        elif first_name:
            return first_name
        elif username:
            return f"@{username}"
    
    # Fallback to MR_ID format
    return f"MR_{user_id}"

def validate_location_coords(lat: float, lon: float) -> bool:
    """Validate GPS coordinates are reasonable"""
    return -90 <= lat <= 90 and -180 <= lon <= 180

def calculate_session_remaining(start_time: float, duration: int) -> int:
    """Calculate remaining seconds in session"""
    import time
    elapsed = time.time() - start_time
    remaining = max(0, duration - elapsed)
    return int(remaining)

def format_duration(seconds: int) -> str:
    """Format seconds to readable duration"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s" if secs > 0 else f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
