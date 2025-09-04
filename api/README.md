# MR Tracking API

FastAPI backend for MR field tracking system.

## Setup

```bash
cd api
pip install -r requirements.txt
```

## Environment Variables

Create `.env` file:
```
API_KEY=your-secure-api-key
MR_SPREADSHEET_ID=your-google-sheet-id
GOOGLE_SHEETS_CREDENTIALS=../pharmagiftapp-60fb5a6a3ca9.json
```

## Run Locally

```bash
python main.py
```

API will be available at: http://localhost:8000

## Endpoints

- `GET /` - Health check
- `GET /api/mrs` - List all MRs
- `GET /api/route?mr_id=123&date=2025-01-01` - Get route data
- `GET /api/live?mr_id=123` - Get live location
- `GET /api/export/gpx?mr_id=123&date=2025-01-01` - Export GPX

## Authentication

Add header: `X-API-Key: your-secure-api-key`

## Deploy to DigitalOcean

```bash
# On your droplet
git clone your-repo
cd mr_bot/api
pip install -r requirements.txt
python main.py
```

Use nginx/supervisor for production setup.
