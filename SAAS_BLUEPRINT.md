# 🚀 MR Tracking System → SaaS Product Blueprint

> **From Single-Org to Multi-Tenant SaaS in One Weekend**

---

## 📋 Table of Contents
1. [Current State Assessment](#current-state-assessment)
2. [SaaS Transformation Plan](#saas-transformation-plan)
3. [Technical Architecture](#technical-architecture)
4. [Weekend Implementation Guide](#weekend-implementation-guide)
5. [Pricing & Business Model](#pricing--business-model)
6. [Scaling Roadmap](#scaling-roadmap)
7. [Go-to-Market Strategy](#go-to-market-strategy)

---

## 🎯 Current State Assessment

### What We Have (Production-Ready):
✅ **Real-time GPS tracking** - 6 active MRs, 132+ daily visits  
✅ **Telegram bot integration** - Field agents can log visits via chat  
✅ **Google Sheets backend** - Zero database setup, auto-sync  
✅ **React dashboard** - Beautiful UI with maps, analytics  
✅ **FastAPI backend** - Deployed on Vercel, auto-scaling  
✅ **Selfie verification** - Photo proof of visits  
✅ **Route analytics** - Daily blueprints, visit patterns  

### What's Missing for SaaS:
❌ User authentication & registration  
❌ Multi-organization support  
❌ Subscription/billing system  
❌ Usage limits & quotas  
❌ Onboarding flow  

---

## 🏗️ SaaS Transformation Plan

### Phase 1: MVP Multi-Tenancy (1 Weekend)
**Goal:** Allow multiple companies to use the same system with isolated data

**Core Changes:**
1. Add Firebase Authentication
2. Create organization concept (org_id)
3. Isolate data per organization
4. Add basic usage limits
5. Manual billing workflow

**Timeline:** Saturday + Sunday (12-16 hours total)

### Phase 2: Self-Service Onboarding (Week 2)
**Goal:** Users can sign up and start using without manual intervention

**Core Changes:**
1. Signup wizard with company info
2. Auto-create Google Sheet for new org
3. Email verification & welcome emails
4. Interactive tutorial/demo data
5. Invite team members flow

**Timeline:** 1 week (20-25 hours)

### Phase 3: Automated Billing (Week 3-4)
**Goal:** Subscription management with auto-renewal

**Core Changes:**
1. Razorpay/Stripe integration
2. Plan selection during signup
3. Usage monitoring & alerts
4. Automatic account suspension for non-payment
5. Invoicing & receipt generation

**Timeline:** 1-2 weeks (30-40 hours)

### Phase 4: Scale & Optimize (Ongoing)
**Goal:** Handle 100+ organizations, 1000+ MRs

**Core Changes:**
1. Database migration (optional - if Sheets hits limits)
2. Caching layer (Redis)
3. Mobile apps (React Native)
4. Advanced features (AI insights, integrations)
5. White-label options for enterprise

**Timeline:** Continuous improvement

---

## 🛠️ Technical Architecture

### Current Architecture:
```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Telegram Bot   │ ───> │  FastAPI Backend │ ───> │ Google Sheets   │
│  (Field MRs)    │      │  (Python)        │      │  (Single Sheet) │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  React Frontend  │
                         │  (Public Access) │
                         └──────────────────┘
```

### SaaS Architecture (Target):
```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────────┐
│  Telegram Bot   │ ───> │  FastAPI Backend │ ───> │ Google Sheets Pool  │
│  (Field MRs)    │      │  + Firebase SDK  │      │ (1 sheet per org)   │
│                 │      │                  │      │ - org_123_sheet     │
└─────────────────┘      └──────────────────┘      │ - org_456_sheet     │
                                  │                 │ - org_789_sheet     │
                                  │                 └─────────────────────┘
                                  ▼
                         ┌──────────────────┐
                         │  React Frontend  │
                         │  + Firebase Auth │
                         └──────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    Firestore     │
                         │  (User/Org Data) │
                         │  - Users         │
                         │  - Organizations │
                         │  - Subscriptions │
                         │  - Usage Metrics │
                         └──────────────────┘
```

### Data Model:

**Firestore Collections:**

```javascript
// /users/{userId}
{
  uid: "firebase_user_123",
  email: "vishesh@pharma.com",
  name: "Vishesh Sanghvi",
  role: "admin",
  orgId: "org_abc123",
  createdAt: "2025-11-06",
  lastLogin: "2025-11-06T10:30:00Z"
}

// /organizations/{orgId}
{
  orgId: "org_abc123",
  companyName: "ABC Pharmaceuticals",
  plan: "professional",  // free_trial, starter, professional, enterprise
  mrLimit: 50,
  sheetsId: "1R-HToQJsMOygvBulPoWS4ihwFHhDXynv4cgq85TuTHg",
  telegramBotToken: "8269645225:AAFx...",  // Each org can have own bot
  subscriptionStatus: "active",  // active, trial, suspended, cancelled
  subscriptionEndsAt: "2025-12-06",
  usageStats: {
    activeMRs: 25,
    monthlyVisits: 3200,
    apiCallsThisMonth: 45000
  },
  billingInfo: {
    razorpayCustomerId: "cust_xyz",
    lastPayment: "2025-11-01",
    nextBillingDate: "2025-12-01"
  },
  createdAt: "2025-10-01",
  createdBy: "firebase_user_123"
}

// /organizations/{orgId}/members/{userId}
{
  userId: "firebase_user_456",
  role: "manager",  // admin, manager, viewer
  permissions: ["view_all_mrs", "edit_routes", "approve_expenses"],
  addedAt: "2025-10-15",
  addedBy: "firebase_user_123"
}

// /organizations/{orgId}/mrs/{mrId}
{
  mrId: "1201911108",
  name: "Rahul Sharma",
  phone: "+919876543210",
  telegramId: "telegram_user_789",
  email: "rahul@pharma.com",
  territory: "Mumbai Central",
  status: "active",  // active, inactive, on_leave
  addedAt: "2025-10-05"
}
```

**Google Sheets Structure (Per Org):**
```
Sheet Name: MR_Daily_Log_org_abc123

Columns:
org_id | Date | Time | MR_ID | MR_Name | Action_Type | Visit_Type | 
Contact_Name | Orders | Remarks | Location | GPS_Lat | GPS_Lon | Session_ID
```

---

## 🗓️ Weekend Implementation Guide

### Saturday Morning (4 hours) - Firebase Setup

**Step 1: Create Firebase Project**
```bash
1. Go to console.firebase.google.com
2. Create new project: "MR-Tracking-SaaS"
3. Enable Authentication (Email/Password + Google OAuth)
4. Enable Firestore Database
5. Get config credentials
```

**Step 2: Install Firebase in Frontend**
```bash
cd frontend
npm install firebase
```

**Step 3: Create Firebase Config**
```javascript
// frontend/src/lib/firebase.ts
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
```

**Step 4: Create Auth Pages**
```bash
# Create these components:
frontend/src/pages/Signup.tsx
frontend/src/pages/Login.tsx
frontend/src/contexts/AuthContext.tsx
frontend/src/components/ProtectedRoute.tsx
```

### Saturday Afternoon (4 hours) - Backend Integration

**Step 1: Install Firebase Admin in Backend**
```bash
cd api
pip install firebase-admin
```

**Step 2: Add Firebase Verification Middleware**
```python
# api/firebase_auth.py
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, Header
import os

# Initialize Firebase Admin
cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_JSON'))
firebase_admin.initialize_app(cred)

async def verify_firebase_token(authorization: str = Header(None)):
    """Verify Firebase ID token from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No token provided")
    
    try:
        # Extract Bearer token
        token = authorization.replace("Bearer ", "")
        decoded = auth.verify_id_token(token)
        return decoded  # Contains uid, org_id, email, etc.
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
```

**Step 3: Update API Endpoints**
```python
# api/main.py
from firebase_auth import verify_firebase_token

@app.get("/api/mrs")
async def get_mrs(user=Depends(verify_firebase_token)):
    org_id = user.get('org_id')
    # Fetch only this org's MRs
    return sheets_manager.get_all_mrs(org_id=org_id)

@app.get("/api/route")
async def get_route(
    mr_id: str,
    date: str,
    user=Depends(verify_firebase_token)
):
    org_id = user.get('org_id')
    # Verify this MR belongs to this org
    return sheets_manager.get_route(org_id=org_id, mr_id=mr_id, date=date)
```

### Saturday Evening (4 hours) - Multi-Tenancy Logic

**Step 1: Update SmartSheetsManager**
```python
# smart_sheets.py
class SmartMRSheetsManager:
    def __init__(self):
        self.sheets_cache = {}  # Cache sheets by org_id
    
    def get_sheet_for_org(self, org_id: str):
        """Get or create Google Sheet for organization"""
        if org_id in self.sheets_cache:
            return self.sheets_cache[org_id]
        
        # Fetch sheet_id from Firestore
        from firebase_admin import firestore
        db = firestore.client()
        org_doc = db.collection('organizations').document(org_id).get()
        
        if not org_doc.exists:
            raise ValueError(f"Organization {org_id} not found")
        
        sheet_id = org_doc.to_dict().get('sheetsId')
        sheet = self.gc.open_by_key(sheet_id)
        self.sheets_cache[org_id] = sheet
        return sheet
    
    def get_all_mrs(self, org_id: str):
        """Get all MRs for specific organization"""
        sheet = self.get_sheet_for_org(org_id)
        # ... existing logic, but scoped to this org's sheet
```

**Step 2: Create Sheet Template Function**
```python
# api/sheet_creator.py
def create_sheet_for_new_org(org_id: str, company_name: str):
    """Create a new Google Sheet for organization"""
    # Copy template sheet
    template_sheet_id = "YOUR_TEMPLATE_SHEET_ID"
    template = gc.open_by_key(template_sheet_id)
    
    # Create copy
    new_sheet = gc.copy(
        template.id,
        title=f"MR_Tracking_{company_name}_{org_id}",
        copy_permissions=False
    )
    
    # Share with service account
    new_sheet.share('mr-bot-service@pharmagiftapp.iam.gserviceaccount.com', 
                     perm_type='user', 
                     role='writer')
    
    return new_sheet.id
```

### Sunday Morning (4 hours) - Signup Flow

**Step 1: Create Signup Component**
```javascript
// frontend/src/pages/Signup.tsx
const handleSignup = async (email, password, companyName) => {
  // 1. Create Firebase user
  const userCredential = await createUserWithEmailAndPassword(auth, email, password);
  const user = userCredential.user;
  
  // 2. Create organization in Firestore
  const orgId = `org_${Date.now()}`;
  await setDoc(doc(db, 'organizations', orgId), {
    orgId,
    companyName,
    plan: 'free_trial',
    mrLimit: 5,
    subscriptionStatus: 'trial',
    subscriptionEndsAt: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000), // 14 days
    createdAt: new Date(),
    createdBy: user.uid
  });
  
  // 3. Create user document with org reference
  await setDoc(doc(db, 'users', user.uid), {
    uid: user.uid,
    email: user.email,
    name: email.split('@')[0],
    role: 'admin',
    orgId,
    createdAt: new Date()
  });
  
  // 4. Call backend to create Google Sheet
  await fetch('/api/setup-organization', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${await user.getIdToken()}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ orgId, companyName })
  });
  
  // 5. Redirect to dashboard
  navigate('/dashboard');
};
```

**Step 2: Backend Setup Endpoint**
```python
# api/main.py
@app.post("/api/setup-organization")
async def setup_organization(
    data: dict,
    user=Depends(verify_firebase_token)
):
    org_id = data['orgId']
    company_name = data['companyName']
    
    # Create Google Sheet for org
    sheet_id = create_sheet_for_new_org(org_id, company_name)
    
    # Update Firestore with sheet_id
    from firebase_admin import firestore
    db = firestore.client()
    db.collection('organizations').document(org_id).update({
        'sheetsId': sheet_id
    })
    
    return {"success": True, "sheetId": sheet_id}
```

### Sunday Afternoon (4 hours) - Usage Limits & Polish

**Step 1: Add Limit Checks**
```python
# api/middleware.py
async def check_usage_limits(user=Depends(verify_firebase_token)):
    """Check if organization has exceeded limits"""
    from firebase_admin import firestore
    db = firestore.client()
    
    org_id = user.get('org_id')
    org = db.collection('organizations').document(org_id).get().to_dict()
    
    # Check subscription status
    if org['subscriptionStatus'] == 'suspended':
        raise HTTPException(status_code=403, detail="Subscription suspended. Please renew.")
    
    # Check MR limit
    if org['usageStats']['activeMRs'] >= org['mrLimit']:
        raise HTTPException(status_code=403, detail="MR limit reached. Upgrade plan.")
    
    return org

@app.post("/api/add-mr")
async def add_mr(
    mr_data: dict,
    org=Depends(check_usage_limits),
    user=Depends(verify_firebase_token)
):
    # Add MR logic
    pass
```

**Step 2: Update Frontend with Auth**
```javascript
// frontend/src/App.tsx
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        
        {/* Protected Routes */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
        {/* ... other protected routes */}
      </Routes>
    </AuthProvider>
  );
}
```

---

## 💰 Pricing & Business Model

### Pricing Tiers:

| Plan | MRs | Monthly Price | Annual Price | Features |
|------|-----|---------------|--------------|----------|
| **Free Trial** | 5 | ₹0 (14 days) | - | Basic tracking, 1 admin |
| **Starter** | 10-25 | ₹299/MR | ₹2,999/MR/year (17% off) | All features, Email support |
| **Professional** | 26-100 | ₹199/MR | ₹1,999/MR/year | + API access, Priority support |
| **Enterprise** | 100+ | Custom | Custom | + White-label, Dedicated support, SLA |

### Revenue Projections:

**Conservative (Year 1):**
- 20 companies × 30 MRs avg × ₹250/MR = **₹1,50,000/month**
- Annual Run Rate: **₹18 lakhs** (~$21.6K USD)

**Moderate (Year 2):**
- 50 companies × 40 MRs avg × ₹220/MR = **₹4,40,000/month**
- Annual Run Rate: **₹52.8 lakhs** (~$63.4K USD)

**Aggressive (Year 3):**
- 200 companies × 50 MRs avg × ₹200/MR = **₹20,00,000/month**
- Annual Run Rate: **₹2.4 crores** (~$288K USD)

### Unit Economics:

**Cost per Customer (Monthly):**
- Vercel hosting: ₹500 / 50 customers = ₹10
- Firebase: ₹200 / 50 customers = ₹4
- Google Sheets API: Free (within limits)
- Support (10% of time): ₹2,000 / 50 = ₹40
- **Total Cost per Customer: ~₹54/month**

**Gross Margin:**
- Average customer: 30 MRs × ₹250 = ₹7,500/month
- Cost: ₹54/month
- **Margin: 99.3%** (SaaS dream!)

---

## 🚀 Scaling Roadmap

### Month 1-3: Foundation
- ✅ Multi-tenancy working
- ✅ 5-10 beta customers
- ✅ Manual billing
- ✅ Basic support process
- **Target: ₹50K MRR**

### Month 4-6: Automation
- 🔄 Razorpay integration
- 🔄 Automated onboarding
- 🔄 Email marketing setup
- 🔄 Knowledge base / FAQ
- **Target: ₹2L MRR**

### Month 7-12: Growth
- 📱 Android mobile app
- 🤖 WhatsApp Business API
- 🧠 AI route optimization
- 🌐 English + Hindi interface
- **Target: ₹5L MRR**

### Year 2: Scale
- 🏢 Sales team (2-3 people)
- 🎨 White-label option
- 🔌 CRM integrations (Salesforce, Zoho)
- 🌍 International expansion (Bangladesh, Sri Lanka)
- **Target: ₹20L MRR**

### Technical Scaling Thresholds:

**When to migrate from Google Sheets:**
- 100+ organizations OR
- 10M+ rows of data OR
- API rate limits hit consistently

**Migration path:** 
- Google Sheets → PostgreSQL (Supabase or Railway)
- Keep Sheets as backup/export option
- Gradual migration, not big-bang

**When to add Redis caching:**
- API response times > 500ms
- 1000+ concurrent users
- Database load > 80%

**When to consider microservices:**
- Team size > 5 developers
- Monolith becomes hard to deploy
- Different components need different scaling

---

## 📈 Go-to-Market Strategy

### Phase 1: Beta Launch (Month 1-2)

**Target:** 10 paying customers

**Channels:**
1. **Direct Outreach**
   - LinkedIn: Message pharma sales managers
   - Cold email: 100 targeted companies
   - Warm intros: Ask friends in pharma

2. **Offer:** 
   - ₹999/month flat (50% off) for first 50 MRs
   - Lifetime discount if they sign before [date]
   - Free setup assistance

3. **Success Criteria:**
   - 50 MRs actively using system
   - 2-3 video testimonials
   - Case study: "How XYZ increased productivity by 30%"

### Phase 2: Product Hunt Launch (Month 3)

**Goal:** Generate buzz, get early adopters

**Preparation:**
1. Polish landing page (mr-tracking.com)
2. Create demo video (2-3 mins)
3. Prepare launch assets (screenshots, GIFs)
4. Line up 20 supporters for upvotes

**Expected Results:**
- 500-1000 website visits
- 50-100 signups
- 5-10 paying customers

### Phase 3: Content Marketing (Month 4-6)

**SEO Blog Posts:**
- "Top 5 Field Force Management Tools in India 2025"
- "How to Track Medical Representatives: Complete Guide"
- "Pharma Field Force Productivity: 10 Data-Driven Tips"
- "Google Sheets vs CRM: Which is Better for Small Pharma?"

**Target Keywords:**
- "pharma field force management software"
- "MR tracking system"
- "medical representative tracking app"
- "field sales tracking India"

### Phase 4: Paid Acquisition (Month 6+)

**Channels:**
1. **LinkedIn Ads**
   - Target: Sales Managers, Pharma Companies in India
   - Budget: ₹20K/month
   - Expected CAC: ₹5K
   - Expected LTV: ₹90K (12 months retention)
   - LTV/CAC ratio: 18x ✅

2. **Google Ads**
   - Target: "field force management", "MR tracking"
   - Budget: ₹15K/month
   - Focus on comparison keywords

3. **Partnerships**
   - Pharma ERP vendors (cross-sell)
   - HR/Payroll software for pharma
   - Medical software distributors

---

## 🎯 Success Metrics (KPIs)

### Product Metrics:
- **MAU (Monthly Active Users):** Target 100 users by Month 3
- **DAU/MAU Ratio:** Target > 0.6 (users log in 18+ days/month)
- **Session Duration:** Target > 10 minutes
- **Feature Adoption:** 80% use map view, 60% use analytics

### Business Metrics:
- **MRR (Monthly Recurring Revenue):** Track weekly
- **Churn Rate:** Target < 5% monthly
- **CAC (Customer Acquisition Cost):** Target < ₹5K
- **LTV (Lifetime Value):** Target > ₹90K (18 months avg)
- **NPS (Net Promoter Score):** Target > 50

### Technical Metrics:
- **API Uptime:** Target > 99.5%
- **Page Load Time:** Target < 2 seconds
- **Error Rate:** Target < 0.1%
- **Support Tickets:** Track and aim to reduce

---

## 🛡️ Risk Mitigation

### Technical Risks:

**Risk 1: Google Sheets API Rate Limits**
- **Mitigation:** Cache aggressively, batch requests, move to DB if needed
- **Threshold:** Monitor API usage, alert at 80% of limits

**Risk 2: Data Security Breach**
- **Mitigation:** Firebase security rules, audit logs, encryption at rest
- **Insurance:** Get cyber insurance once revenue > ₹10L/month

**Risk 3: Service Account Access Revoked**
- **Mitigation:** Backup service accounts, alert on access failures
- **Recovery:** Auto-switch to backup credentials

### Business Risks:

**Risk 1: No Customer Acquisition**
- **Mitigation:** Pivot channels, improve product-market fit
- **Threshold:** If < 5 customers after 3 months, reassess

**Risk 2: High Churn Rate**
- **Mitigation:** Customer success calls, feature requests, refund if unhappy
- **Threshold:** If > 10% monthly churn, deep-dive on reasons

**Risk 3: Competitor Undercuts Pricing**
- **Mitigation:** Focus on superior UX, faster support, unique features
- **Moat:** Telegram integration, Google Sheets simplicity (no DB setup)

---

## 📞 Support Infrastructure

### Tier 1: Self-Service
- Knowledge base / FAQ
- Video tutorials (YouTube)
- In-app tooltips
- Email templates for common questions

### Tier 2: Assisted Support
- WhatsApp support (10 AM - 6 PM IST)
- Email support (response < 24 hours)
- Zoom screen-share for setup help

### Tier 3: Premium Support (Enterprise)
- Dedicated account manager
- Phone support
- Custom feature development
- On-site training

---

## 🎓 Learning Resources

### For Firebase Auth:
- [Firebase Auth Docs](https://firebase.google.com/docs/auth)
- [Firebase + React Tutorial](https://www.youtube.com/watch?v=PKwu15ldZ7k)

### For Multi-Tenancy:
- [SaaS Multi-Tenancy Patterns](https://aws.amazon.com/blogs/apn/saas-architecture-fundamentals/)
- [Firestore Data Modeling](https://firebase.google.com/docs/firestore/manage-data/structure-data)

### For Billing:
- [Razorpay Subscriptions](https://razorpay.com/docs/payments/subscriptions/)
- [Stripe Billing](https://stripe.com/docs/billing)

---

## ✅ Launch Checklist

### Pre-Launch (Weekend Sprint):
- [ ] Firebase project created
- [ ] Authentication pages built (Login/Signup)
- [ ] Firestore data model implemented
- [ ] Backend middleware for token verification
- [ ] Multi-org sheet isolation working
- [ ] Usage limits enforced
- [ ] Local testing complete

### Week 1 (Polish):
- [ ] Landing page updated
- [ ] Pricing page created
- [ ] Terms of Service / Privacy Policy
- [ ] Email templates (welcome, trial ending, invoice)
- [ ] Beta customer outreach list prepared
- [ ] Payment link workflow tested

### Week 2 (Beta Launch):
- [ ] Invite 10 beta customers
- [ ] Onboard each personally (Zoom call)
- [ ] Collect feedback in Notion/Airtable
- [ ] Fix critical bugs
- [ ] Get 2-3 testimonials

### Week 3-4 (Optimize):
- [ ] Analytics dashboard (Mixpanel/PostHog)
- [ ] Error tracking (Sentry)
- [ ] Customer success process documented
- [ ] Knowledge base articles (10+)
- [ ] Referral program design

### Month 2 (Scale):
- [ ] Razorpay integration complete
- [ ] Self-service signup working end-to-end
- [ ] Mobile app (Android) in beta
- [ ] Content marketing started
- [ ] 20+ paying customers

---

## 🎉 Conclusion

**Bottom Line:** You're closer than you think. The core product is 90% done. You just need:

1. **Firebase for auth** (4 hours)
2. **Org isolation logic** (4 hours)
3. **Firestore for org data** (4 hours)
4. **Signup flow** (4 hours)

**Total: 16 hours = 1 weekend.**

Then launch, get 10 beta customers, iterate based on feedback, and scale from there.

**The hardest part (building the product) is DONE.** Now it's just packaging it for multiple customers. 

**You got this! 🚀**

---

**Created:** November 6, 2025  
**Last Updated:** November 6, 2025  
**Version:** 1.0  
**Author:** Vishesh Sanghvi

