# 🚀 Deployment Guide

This guide covers deploying the MR Bot system to production environments.

## 📋 Pre-Deployment Checklist

### Security
- [ ] All API keys moved to environment variables
- [ ] Service account credentials secured
- [ ] `.gitignore` properly configured
- [ ] No sensitive data in repository
- [ ] HTTPS certificates ready

### Configuration
- [ ] Production environment variables set
- [ ] Database configuration verified
- [ ] Google Sheets permissions configured
- [ ] API rate limits checked
- [ ] Monitoring setup planned

## 🖥️ Backend Deployment

### Option 1: Traditional Server (Ubuntu/CentOS)

#### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12+
sudo apt install python3.12 python3.12-venv python3-pip -y

# Install nginx (optional for reverse proxy)
sudo apt install nginx -y
```

#### 2. Application Setup
```bash
# Clone repository
git clone https://github.com/yourusername/mr_bot.git
cd mr_bot

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install production WSGI server
pip install gunicorn uvicorn[standard]
```

#### 3. Environment Configuration
```bash
# Create production environment file
cp .env.example .env
nano .env  # Edit with production values
```

#### 4. Run with Gunicorn
```bash
# Test run
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

# Production run with systemd (recommended)
```

#### 5. Systemd Service (Optional)
Create `/etc/systemd/system/mr-bot.service`:
```ini
[Unit]
Description=MR Bot FastAPI Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/mr_bot
Environment=PATH=/path/to/mr_bot/venv/bin
ExecStart=/path/to/mr_bot/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable mr-bot
sudo systemctl start mr-bot
sudo systemctl status mr-bot
```

### Option 2: Docker Deployment

#### 1. Create Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
```

#### 2. Create docker-compose.yml
```yaml
version: '3.8'

services:
  mr-bot-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MR_BOT_TOKEN=${MR_BOT_TOKEN}
      - MR_SPREADSHEET_ID=${MR_SPREADSHEET_ID}
      - GOOGLE_SHEETS_CREDENTIALS=${GOOGLE_SHEETS_CREDENTIALS}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - mr-bot-api
    restart: unless-stopped
```

#### 3. Deploy with Docker
```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Scale if needed
docker-compose up -d --scale mr-bot-api=3
```

### Option 3: Cloud Platforms

#### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### Heroku
```bash
# Install Heroku CLI
# Create Procfile
echo "web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:\$PORT" > Procfile

# Deploy
heroku create your-mr-bot-app
heroku config:set MR_BOT_TOKEN=your_token
heroku config:set MR_SPREADSHEET_ID=your_sheet_id
git push heroku main
```

#### DigitalOcean App Platform
Create `app.yaml`:
```yaml
name: mr-bot
services:
- name: api
  source_dir: /
  github:
    repo: yourusername/mr_bot
    branch: main
  run_command: gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: MR_BOT_TOKEN
    value: ${MR_BOT_TOKEN}
  - key: MR_SPREADSHEET_ID
    value: ${MR_SPREADSHEET_ID}
```

## 🌐 Frontend Deployment

### Option 1: Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from frontend directory
cd frontend
vercel

# Configure environment variables in Vercel dashboard
# - NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
# - NEXT_PUBLIC_API_URL
```

### Option 2: Netlify
```bash
# Build the project
cd frontend
npm run build

# Deploy to Netlify
# Upload the 'out' or '.next' folder
# Configure environment variables in Netlify dashboard
```

### Option 3: Traditional Server
```bash
# Build the project
cd frontend
npm run build

# Serve with nginx
sudo cp -r .next/* /var/www/html/
sudo systemctl restart nginx
```

## 🔧 Production Configuration

### Environment Variables

#### Backend (.env)
```env
# Production values
MR_BOT_TOKEN=prod_bot_token
MR_SPREADSHEET_ID=prod_spreadsheet_id
GOOGLE_SHEETS_CREDENTIALS=prod_service_account.json
GEMINI_API_KEY=prod_gemini_key

# Database
DATABASE_URL=postgresql://user:pass@host:5432/mrbot_prod

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/mr-bot/app.log

# Security
SECRET_KEY=your_super_secret_key_here
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=prod_maps_key
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NODE_ENV=production
```

### Database Migration (if using PostgreSQL)
```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# Update database configuration
# Run migrations if needed
```

## 🔍 Monitoring & Logging

### Application Monitoring
```bash
# Install monitoring tools
pip install prometheus-client

# Add health check endpoint
# Monitor with Prometheus + Grafana
```

### Log Management
```bash
# Configure log rotation
sudo nano /etc/logrotate.d/mr-bot

# Content:
/var/log/mr-bot/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    copytruncate
}
```

### Nginx Configuration (if using reverse proxy)
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Performance Optimization

### Backend Optimization
- Use connection pooling for database
- Implement caching (Redis)
- Enable gzip compression
- Set up CDN for static assets

### Frontend Optimization
- Enable Next.js optimization features
- Use image optimization
- Implement code splitting
- Set up CDN for assets

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Binding Error
```bash
# Check what's using the port
sudo lsof -i :8000

# Kill process if needed
sudo kill -9 PID
```

#### 2. Permission Errors
```bash
# Fix file permissions
sudo chown -R www-data:www-data /path/to/mr_bot
sudo chmod -R 755 /path/to/mr_bot
```

#### 3. Service Account Issues
```bash
# Verify service account file
python -c "import json; print(json.load(open('service_account.json'))['client_email'])"

# Check Google Sheets permissions
```

#### 4. Memory Issues
```bash
# Monitor memory usage
htop

# Adjust worker count
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app
```

## 🔄 Maintenance

### Regular Tasks
- Monitor application logs
- Update dependencies monthly
- Rotate API keys quarterly
- Backup database weekly
- Review performance metrics

### Updates
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Restart services
sudo systemctl restart mr-bot
```

---

For specific deployment questions, check the [documentation](README.md) or create an issue on GitHub.
