# Professional MR Tracking Frontend Development Plan

## 🎯 **Project Overview**

**Goal**: Create a professional, map-focused frontend for MR tracking with route blueprints visualization

**Tech Stack**: 
- Next.js (React)
- TypeScript
- Tailwind CSS (Professional theme)
- Leaflet/MapboxGL for maps
- Chart.js for analytics
- API integration with FastAPI backend

## 📋 **Site Structure**

### 1. **Header & Navigation**
```
┌─────────────────────────────────────────────────────────┐
│ [LOGO] MR Tracking Pro    [Dashboard] [About] [Contact] │
└─────────────────────────────────────────────────────────┘
```

### 2. **Pages Structure**
```
├── / (Index/Dashboard)
│   ├── Hero Section
│   ├── Live Map with Route Blueprints
│   ├── MR Selection Panel
│   ├── Analytics Overview
│   └── Recent Activity
├── /about
│   ├── Platform Overview
│   ├── Features
│   └── How It Works
├── /contact
│   ├── Contact Information
│   └── Support
└── /mr/[id] (Individual MR Dashboard)
    ├── MR Details
    ├── Route Blueprint Map
    ├── Location History
    └── Performance Analytics
```

## 🎨 **Professional Theme**

### **Color Palette:**
```css
Primary: #1e40af (Professional Blue)
Secondary: #059669 (Success Green) 
Accent: #dc2626 (Alert Red)
Background: #f8fafc (Light Gray)
Text: #1f2937 (Dark Gray)
Surface: #ffffff (White)
```

### **Typography:**
- Headers: Inter (Bold, Professional)
- Body: Inter (Regular, Clean)
- Code/Data: JetBrains Mono

### **Components:**
- Clean, minimal design
- Card-based layouts
- Subtle shadows and rounded corners
- Professional color scheme
- Responsive design

## 🗺️ **Map Implementation Focus**

### **Core Map Features:**
1. **Route Blueprint Visualization**
   - Daily route paths with visit markers
   - Color-coded visit types (Hospital=Red, Pharmacy=Blue, Clinic=Green)
   - Interactive popups with visit details
   - Route efficiency indicators

2. **Real-time Updates**
   - WebSocket integration for live updates
   - Auto-refresh route data
   - Real-time MR position (if available)

3. **Interactive Controls**
   - MR selector dropdown
   - Date picker for historical routes
   - Route optimization toggle
   - Layer controls (visits, routes, areas)

### **Map Data Structure:**
```typescript
interface VisitMarker {
  id: string;
  position: [number, number]; // [lat, lng]
  type: 'hospital' | 'pharmacy' | 'clinic' | 'general';
  title: string;
  time: string;
  duration: number;
  outcome: 'successful' | 'no_order' | 'follow_up';
  details: string;
}

interface RouteBlueprint {
  mr_id: string;
  date: string;
  visits: VisitMarker[];
  route_path: [number, number][];
  total_distance: number;
  efficiency: number;
  coverage_areas: string[];
}
```

## 🚀 **Implementation Plan**

### **Phase 1: Foundation (Day 1)**
1. Set up professional theme
2. Create header/footer components
3. Build page structure
4. Implement basic routing

### **Phase 2: Map Integration (Day 2)**
1. Integrate Leaflet map
2. Connect to blueprint APIs
3. Implement visit markers
4. Add route path visualization

### **Phase 3: Dashboard Features (Day 3)**
1. MR selection panel
2. Analytics cards
3. Recent activity feed
4. Performance metrics

### **Phase 4: Polish & Enhancement (Day 4)**
1. Responsive design optimization
2. Loading states and animations
3. Error handling
4. Performance optimization

## 📁 **File Structure**
```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx (Dashboard)
│   │   ├── about/page.tsx
│   │   ├── contact/page.tsx
│   │   ├── mr/[id]/page.tsx
│   │   └── layout.tsx (Root layout)
│   ├── components/
│   │   ├── ui/ (Reusable UI components)
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Card.tsx
│   │   │   └── Button.tsx
│   │   ├── map/
│   │   │   ├── MapContainer.tsx
│   │   │   ├── RouteBlueprint.tsx
│   │   │   ├── VisitMarker.tsx
│   │   │   └── MapControls.tsx
│   │   ├── dashboard/
│   │   │   ├── MRSelector.tsx
│   │   │   ├── AnalyticsCards.tsx
│   │   │   ├── ActivityFeed.tsx
│   │   │   └── PerformanceChart.tsx
│   ├── lib/
│   │   ├── api.ts (API integration)
│   │   ├── types.ts (TypeScript types)
│   │   └── utils.ts (Helper functions)
│   └── styles/
│       └── globals.css (Tailwind + custom styles)
```

## 🔌 **API Integration**

### **API Endpoints to Use:**
```typescript
// Route blueprint data
GET /api/v2/route-blueprint/{mr_id}?date=2025-09-04

// Location history
GET /api/v2/location-history/{mr_id}?days=7

// Location analytics
GET /api/v2/location-analytics/{mr_id}

// Team overview
GET /api/v2/team-routes?team_ids=MR001,MR002,MR003

// Map visualization data
GET /api/v2/route-map/{mr_id}?date=2025-09-04
```

### **WebSocket Integration:**
```typescript
// Real-time updates
ws://localhost:8000/ws/{mr_id}
```

## 📱 **Responsive Design**

### **Breakpoints:**
- Mobile: 320px - 768px (Stack layout)
- Tablet: 768px - 1024px (Mixed layout)
- Desktop: 1024px+ (Full layout)

### **Map Responsiveness:**
- Mobile: Full-screen map with overlay controls
- Tablet: Split view (map + sidebar)
- Desktop: Full dashboard with integrated map

## 🎯 **Success Metrics**

### **User Experience:**
- Load time < 2 seconds
- Smooth map interactions
- Intuitive navigation
- Professional appearance

### **Technical:**
- TypeScript strict mode
- 100% responsive design
- Accessible components
- SEO optimized

## 🚀 **Let's Start Building!**

Ready to implement this professional frontend with beautiful map-based route blueprint visualization!
