# 🔒 PRODUCTION SECURITY CHECKLIST

## ❌ CRITICAL VULNERABILITIES TO FIX

### 1. **API Authentication (CRITICAL)**
```python
# CURRENT: Authentication is DISABLED!
# if x_api_key != expected_key:
#     raise HTTPException(status_code=401, detail="Invalid API key")

# FIX: Enable authentication immediately
async def verify_api_key(x_api_key: str = Header(None)):
    expected_key = os.getenv("API_KEY", "mr-tracking-2025")
    if x_api_key != expected_key:  # UNCOMMENT THIS!
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
```

### 2. **CORS Configuration (CRITICAL)**
```python
# CURRENT: Accepts ALL domains
allow_origins=["*"]  

# FIX: Restrict to your domains only
allow_origins=[
    "https://yourdomain.com",
    "https://app.yourdomain.com"
]
```

### 3. **Environment Variables (HIGH)**
Create `.env` file with:
```bash
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=your-32-char-random-string
API_KEY=your-secure-api-key-here
MR_BOT_TOKEN=your-telegram-bot-token
DATABASE_ENCRYPTION_KEY=your-fernet-encryption-key
```

### 4. **HTTPS Enforcement (HIGH)**
```python
# Add to main.py
@app.middleware("http")
async def force_https(request, call_next):
    if not request.url.scheme == "https" and os.getenv('ENVIRONMENT') == 'production':
        raise HTTPException(403, "HTTPS required")
    return await call_next(request)
```

### 5. **Rate Limiting (HIGH)**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/route")
@limiter.limit("100/hour")  # 100 requests per hour
async def get_route(request: Request, ...):
    pass
```

## ✅ WHAT'S ALREADY SECURE

### 1. **Google Sheets Authentication**
```python
# ✅ GOOD: Uses service account OAuth
from google.oauth2.service_account import Credentials
```

### 2. **User Authorization**
```python
# ✅ GOOD: Whitelist approach
AUTHORIZED_MR_IDS = [1201911108, 8393304686, 5901220876]
```

### 3. **Telegram Bot Security**
- ✅ Bot token in environment variables
- ✅ User ID verification
- ✅ Location validation

## 🛠️ IMMEDIATE ACTIONS REQUIRED

### **Priority 1 (Do Today):**
1. **Enable API authentication** - Uncomment the auth check
2. **Fix CORS origins** - Remove "*", add your domain
3. **Create .env file** - Move secrets out of code
4. **Generate strong API keys** - Replace default "mr-tracking-2025"

### **Priority 2 (This Week):**
1. **Add rate limiting** - Prevent API abuse
2. **Input sanitization** - Prevent injection attacks  
3. **HTTPS enforcement** - Force secure connections
4. **Audit logging** - Track who accesses what

### **Priority 3 (This Month):**
1. **Database encryption** - Encrypt sensitive MR data
2. **Session management** - Proper user sessions
3. **Error monitoring** - Add Sentry for error tracking
4. **Security headers** - Add security middleware

## 📋 PRODUCTION DEPLOYMENT SECURITY

### **Infrastructure Security:**
```bash
# Firewall rules
ufw allow 443/tcp  # HTTPS only
ufw allow 80/tcp   # HTTP redirect to HTTPS
ufw deny 8000/tcp  # Block direct API access

# Process management
sudo systemctl enable mr-tracking
sudo systemctl start nginx
```

### **Nginx Security Configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

## 🚨 SECURITY SCORING

**Current State: 3/10**
- ❌ No API authentication
- ❌ Open CORS policy  
- ❌ Hardcoded secrets
- ❌ No rate limiting
- ✅ Basic user authorization
- ✅ Secure Google integration

**After Basic Fixes: 7/10**
- ✅ API authentication enabled
- ✅ Restricted CORS
- ✅ Environment variables
- ✅ Rate limiting
- ✅ User authorization  
- ✅ Secure integrations

**Production Ready: 9/10**
- ✅ All above +
- ✅ Database encryption
- ✅ Audit logging
- ✅ Error monitoring
- ✅ Security headers

## 💡 QUICK WIN COMMANDS

```bash
# 1. Install security dependencies
pip install -r requirements_security.txt

# 2. Generate secure keys
python -c "import secrets; print('API_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))"

# 3. Test security
curl -H "X-API-Key: wrong-key" http://localhost:8000/api/mrs
# Should return 401 Unauthorized

# 4. Enable production mode
export ENVIRONMENT=production
```

**BOTTOM LINE:** Fix Priority 1 items TODAY before any production use!
