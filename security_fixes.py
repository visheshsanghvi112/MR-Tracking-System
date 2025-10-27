"""
CRITICAL Security Fixes for MR Tracking System
Apply these fixes IMMEDIATELY for production deployment
"""
import os
import secrets
import hashlib
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import bcrypt

class SecurityManager:
    def __init__(self):
        self.security = HTTPBearer()
        self.jwt_secret = os.getenv('JWT_SECRET_KEY') or secrets.token_urlsafe(32)
        
    # FIX 1: Proper API Key Hashing
    def hash_api_key(self, api_key: str) -> str:
        """Hash API keys properly"""
        salt = os.getenv('API_SALT', secrets.token_urlsafe(16))
        return hashlib.pbkdf2_hmac('sha256', 
                                   api_key.encode('utf-8'), 
                                   salt.encode('utf-8'), 
                                   100000)
    
    # FIX 2: JWT Token Authentication 
    def create_jwt_token(self, mr_id: str, role: str = "mr") -> str:
        """Create JWT token for MR authentication"""
        payload = {
            "mr_id": mr_id,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
    
    def verify_jwt_token(self, token: str) -> dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    # FIX 3: Rate Limiting
    def check_rate_limit(self, client_ip: str, endpoint: str) -> bool:
        """Basic rate limiting - implement Redis for production"""
        # Store in Redis: key = f"rate_limit:{client_ip}:{endpoint}"
        # Allow 100 requests per hour per IP per endpoint
        pass
    
    # FIX 4: Input Sanitization
    def sanitize_input(self, user_input: str) -> str:
        """Sanitize user input to prevent injections"""
        import re
        import html
        
        # Remove dangerous characters
        sanitized = re.sub(r'[<>"\']', '', user_input)
        # HTML escape
        sanitized = html.escape(sanitized)
        # Limit length
        return sanitized[:500]
    
    # FIX 5: Secure Environment Variables
    def load_secure_config(self):
        """Load configuration securely"""
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'JWT_SECRET_KEY', 
            'DATABASE_ENCRYPTION_KEY',
            'API_RATE_LIMIT_REDIS_URL'
        ]
        
        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            raise RuntimeError(f"Missing critical environment variables: {missing}")

# Production Security Middleware
async def verify_secure_api_key(x_api_key: str = Header(None)):
    """PRODUCTION API Key verification"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    # Hash the provided key and compare with stored hash
    expected_hash = os.getenv('API_KEY_HASH')
    if not expected_hash:
        raise HTTPException(status_code=500, detail="Server configuration error")
    
    security_manager = SecurityManager()
    provided_hash = security_manager.hash_api_key(x_api_key)
    
    if not secrets.compare_digest(provided_hash, expected_hash.encode()):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return x_api_key

# CORS Security Fix
def get_secure_cors_origins():
    """Get secure CORS origins for production"""
    return [
        "https://yourdomain.com",
        "https://app.yourdomain.com", 
        "https://mr-tracking.yourdomain.com"
        # NO WILDCARDS IN PRODUCTION!
    ]

# Database Security
class SecureDatabase:
    def __init__(self):
        self.encryption_key = os.getenv('DATABASE_ENCRYPTION_KEY')
        if not self.encryption_key:
            raise ValueError("DATABASE_ENCRYPTION_KEY not set")
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data before storing"""
        from cryptography.fernet import Fernet
        f = Fernet(self.encryption_key.encode())
        return f.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data after retrieving"""
        from cryptography.fernet import Fernet
        f = Fernet(self.encryption_key.encode())
        return f.decrypt(encrypted_data.encode()).decode()

# Audit Logging
class AuditLogger:
    def log_api_access(self, mr_id: str, endpoint: str, ip: str, timestamp: datetime):
        """Log all API access for security audit"""
        audit_entry = {
            "mr_id": mr_id,
            "endpoint": endpoint,
            "ip_address": ip,
            "timestamp": timestamp.isoformat(),
            "action": "api_access"
        }
        # Store in secure audit log (separate from application logs)
        self._store_audit_log(audit_entry)
    
    def _store_audit_log(self, entry: dict):
        """Store audit log securely"""
        # Implement: Write to secure audit database or service
        pass

# HTTPS Enforcement
def enforce_https():
    """Middleware to enforce HTTPS in production"""
    def https_middleware(request):
        if not request.url.scheme == "https" and os.getenv('ENVIRONMENT') == 'production':
            raise HTTPException(status_code=403, detail="HTTPS required")
    return https_middleware
