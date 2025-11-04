## MR Tracking System — Interview Brief

### What I built
- Real-time field tracking platform for Medical Representatives (MRs)
- Live GPS route visualization, visit logging, analytics, and dashboards
- Clean separation of concerns: data ingestion, processing, APIs, and UI

### Architecture (high level)
- Backend: FastAPI service (`mr_bot/api/main.py`) exposing REST + WebSocket
- Data: Google Sheets as source of truth (via `SmartMRSheetsManager`), plus in-memory/live session manager
- Frontend: React + Vite (TypeScript), modern UI with Tailwind/shadcn
- Real-time: WebSocket (`/ws/{mr_id}`) for live location updates

### Key backend APIs (real, no mocks)
- GET `/api/mrs` — list MRs with status, last activity, last location
- GET `/api/route?mr_id&date` — enhanced route: visits/live trail + stats
- GET `/api/analytics` — team analytics (counts, distance, averages)
- GET `/api/activity` — recent activity feed (from Sheets records)
- GET `/api/v2/route-blueprint/{mr_id}` — visit blueprint built from real data

### Security
- API key required on protected routes via `X-API-Key` header (config/env)
- CORS hardened for known origins in production
- Input validation and safe fallbacks when Sheets is unavailable

### Data integration
- Google Sheets used as the operational datastore (daily MR logs, visits, GPS)
- Robust parsing and transformation: converts Sheets rows → typed route points and analytics
- Live data fusion: when date == today, merges session live trail with Sheets

### Frontend (what matters)
- Real-only UI: removed fake counters/testimonials; stats come from APIs
- Dashboard: MR list + map route, filters (date, MR), activity feed, KPIs
- Map: shows route points (visits/movement), start/end, and fit-to-bounds

### Reliability and health
- Health scripts: `api/health_check.py`, `combined_health_check.py`
- One-liners to start/stop services and free ports (Windows-friendly)

### How to run (local)
- Backend: `cd mr_bot/api && python main.py` → http://localhost:8000
- Frontend: `cd mr_bot/frontend && npm run dev -- --host --port 8080` → http://localhost:8080

### Impact (what I’d highlight)
- Turned messy, inconsistent data into reliable APIs and a clean UI
- Real-time route insights and historical analytics without a heavy DB
- Practical security and ops: API keys, CORS, health checks, fast local dev

### Talking points (quick bullets)
- Why Sheets? Rapid delivery with existing ops; strict transforms to keep integrity
- API design: predictable shapes, defensive error handling, empty arrays over fake data
- Frontend choices: only real data on landing/Dashboard; loading and empty states
- Extensibility: geofencing, heatmaps, clustering, and mobile capture can drop in


