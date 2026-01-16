# FGN Savings Bond Application - Migration Plan: Streamlit to React + FastAPI

## Executive Summary

Migrate the FGN Savings Bond subscription application from Streamlit to a modern React frontend + FastAPI backend architecture. This addresses fundamental limitations of Streamlit for complex transactional forms while preserving ~70% of existing business logic.

**Estimated Timeline:** 3-4 weeks
**Risk Level:** Medium (well-structured codebase reduces risk)
**Strategy:** Parallel Operation - Keep Streamlit running while building React, cutover when verified

---

## Current State Analysis

### What Exists (9,000+ lines)
- **User Form**: 7-step wizard for bond subscription (Individual/Joint/Corporate)
- **Admin Dashboard**: Analytics, filtering, exports, reports
- **PDF Generation**: Professional DMO-styled forms (ReportLab)
- **Database**: MongoDB with comprehensive data model
- **70+ form fields** with validation

### Why Migration is Needed
1. **State Management Issues**: Text inputs don't persist between wizard steps
2. **CSS Hacks Required**: Fighting Streamlit for basic UI control
3. **Execution Model Mismatch**: Streamlit reruns entire script on every interaction
4. **Not Designed for Forms**: Streamlit is for data exploration, not transactional apps

---

## Architecture Overview

### New Stack
```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  React + TypeScript + React Hook Form + TailwindCSS         │
│  - Multi-step form wizard                                    │
│  - Admin dashboard with charts                               │
│  - Responsive design                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ REST API (JSON)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                               │
│  FastAPI + Pydantic + Motor (async MongoDB)                 │
│  - Form validation & submission                              │
│  - PDF generation (ReportLab - REUSED)                      │
│  - Admin authentication (JWT)                                │
│  - Analytics & exports                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        DATABASE                              │
│  MongoDB (unchanged schema)                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Code Reusability Analysis

### Fully Reusable (Move As-Is) - ~60%
| Component | Location | Lines | Notes |
|-----------|----------|-------|-------|
| PDF Generation | `src/pdf/` | ~600 | No Streamlit deps, pure ReportLab |
| Form Validation | `src/form_handler.py` | ~400 | Validation logic only |
| Utilities | `src/utils.py` | 50 | Number-to-words conversion |
| DB Operations | `src/form_handler.py` | ~200 | MongoDB queries |
| Design Tokens | `src/design_system/tokens.py` | 260 | Colors, spacing (→ CSS vars) |

### Partially Reusable (Adapt) - ~15%
| Component | Adaptation Needed |
|-----------|-------------------|
| `form_handler.py` | Convert to Pydantic models + FastAPI routes |
| Validation functions | Port to both backend (Pydantic) and frontend (Zod) |
| Export logic | Keep Python logic, expose via API |

### Complete Rewrite - ~25%
| Component | Replacement |
|-----------|-------------|
| `streamlit_app.py` | React form wizard |
| `admin_app.py` | React admin dashboard |
| `components/wizard.py` | React state management |
| All UI components | React components |

---

## Project Structure (New)

```
fgnbond_sub/
├── backend/                     # FastAPI Backend
│   ├── app/
│   │   ├── main.py             # FastAPI app entry
│   │   ├── config.py           # Settings & env vars
│   │   ├── models/
│   │   │   ├── application.py  # Pydantic models
│   │   │   └── user.py         # Admin user model
│   │   ├── routes/
│   │   │   ├── applications.py # Form submission API
│   │   │   ├── admin.py        # Admin dashboard API
│   │   │   └── auth.py         # Authentication API
│   │   ├── services/
│   │   │   ├── pdf.py          # PDF generation (reused)
│   │   │   ├── database.py     # MongoDB operations
│   │   │   └── analytics.py    # Dashboard analytics
│   │   └── utils/
│   │       └── validation.py   # Shared validators
│   ├── pdf/                    # COPIED FROM src/pdf/
│   │   ├── generator.py
│   │   ├── templates.py
│   │   ├── styles.py
│   │   └── elements.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                    # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── wizard/         # Form wizard components
│   │   │   ├── admin/          # Admin dashboard components
│   │   │   ├── ui/             # Shared UI components
│   │   │   └── charts/         # Chart components
│   │   ├── pages/
│   │   │   ├── SubscriptionForm.tsx
│   │   │   ├── AdminDashboard.tsx
│   │   │   └── AdminLogin.tsx
│   │   ├── hooks/
│   │   │   ├── useFormWizard.ts
│   │   │   └── useAuth.ts
│   │   ├── services/
│   │   │   └── api.ts          # API client
│   │   ├── types/
│   │   │   └── application.ts  # TypeScript types
│   │   └── utils/
│   │       ├── validation.ts   # Client-side validation
│   │       └── formatting.ts   # Currency, dates
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml           # Updated for new architecture
├── nginx/
│   └── nginx.conf              # Reverse proxy config
└── .env.example
```

---

## Phase 1: Backend Setup (Days 1-5)

### 1.1 Initialize FastAPI Project
**File:** `backend/app/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FGN Savings Bond API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 1.2 Create Pydantic Models
**File:** `backend/app/models/application.py`

Key models to create:
- `BondDetails` - tenor, month_of_offer, bond_value
- `IndividualApplicant` - personal details
- `JointApplicant` - joint applicant details
- `CorporateApplicant` - company details
- `BankDetails` - bank info, BVN, account
- `Classification` - residency, investor categories
- `ApplicationCreate` - full submission model
- `ApplicationResponse` - response with ID

### 1.3 Copy PDF Generation
```bash
cp -r src/pdf/ backend/pdf/
```
No modifications needed - works as-is.

### 1.4 Create API Endpoints

**Applications API (`backend/app/routes/applications.py`):**
```
POST   /api/applications              # Submit new application
GET    /api/applications/{id}         # Get application details
GET    /api/applications/{id}/pdf     # Generate/download PDF
GET    /api/constants                 # Get form constants (banks, categories)
```

**Admin API (`backend/app/routes/admin.py`):**
```
GET    /api/admin/applications        # List with filters & pagination
GET    /api/admin/summary             # Dashboard metrics
GET    /api/admin/analytics           # Charts data
GET    /api/admin/export/csv          # Export filtered data
GET    /api/admin/export/excel        # Export with summary sheet
POST   /api/admin/reports/monthly     # Generate monthly report
```

**Auth API (`backend/app/routes/auth.py`):**
```
POST   /api/auth/login               # Login, return JWT
POST   /api/auth/refresh             # Refresh token
GET    /api/auth/me                  # Get current user
```

### 1.5 Database Service
**File:** `backend/app/services/database.py`

Use Motor (async MongoDB driver):
```python
from motor.motor_asyncio import AsyncIOMotorClient

async def get_database():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    return client[settings.DB_NAME]
```

---

## Phase 2: React Frontend Setup (Days 6-10)

### 2.1 Initialize React Project
```bash
npx create-vite@latest frontend --template react-ts
cd frontend
npm install react-router-dom react-hook-form zod @hookform/resolvers axios
npm install @tanstack/react-query recharts date-fns
npm install tailwindcss postcss autoprefixer
```

### 2.2 Form Wizard Component Structure

```
src/components/wizard/
├── FormWizard.tsx           # Main wizard container
├── WizardProgress.tsx       # Step progress indicator
├── WizardNavigation.tsx     # Prev/Next buttons
├── steps/
│   ├── BondDetailsStep.tsx
│   ├── ApplicantTypeStep.tsx
│   ├── ApplicantInfoStep.tsx   # Conditional rendering
│   ├── BankDetailsStep.tsx
│   ├── ClassificationStep.tsx
│   ├── DistributionStep.tsx
│   └── ReviewStep.tsx
└── fields/
    ├── CurrencyInput.tsx
    ├── PhoneInput.tsx
    ├── BVNInput.tsx
    └── ValidatedInput.tsx
```

### 2.3 Form State Management
Use React Hook Form with Zod validation:
```typescript
const schema = z.object({
  tenor: z.enum(["2-Year", "3-Year"]),
  bondValue: z.number().min(5000).max(50000000),
  applicantType: z.enum(["Individual", "Joint", "Corporate"]),
  fullName: z.string().min(1, "Full name is required"),
  email: z.string().email().optional(),
  phone: z.string().regex(/^\+234\d{10}$/).optional(),
  bvn: z.string().length(11).optional(),
  accountNumber: z.string().length(10),
  // ... all 70+ fields
});
```

### 2.4 Wizard Hook
**File:** `src/hooks/useFormWizard.ts`
```typescript
export function useFormWizard() {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());

  const nextStep = async () => {
    const isValid = await validateCurrentStep();
    if (isValid) {
      setCompletedSteps(prev => new Set([...prev, currentStep]));
      setCurrentStep(prev => prev + 1);
    }
  };

  // ...
}
```

---

## Phase 3: Admin Dashboard (Days 11-15)

### 3.1 Admin Components
```
src/components/admin/
├── Dashboard.tsx            # Main dashboard with metrics
├── ApplicationsTable.tsx    # Paginated data table
├── FilterPanel.tsx          # Advanced filters
├── ExportButtons.tsx        # CSV/Excel/PDF export
├── charts/
│   ├── ApplicantTypeChart.tsx
│   ├── ValueDistributionChart.tsx
│   ├── TrendChart.tsx
│   └── TopApplicantsChart.tsx
└── ApplicationDetail.tsx    # Single app view + PDF
```

### 3.2 Authentication
**File:** `src/hooks/useAuth.ts`
```typescript
export function useAuth() {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('token')
  );

  const login = async (username: string, password: string) => {
    const response = await api.post('/auth/login', { username, password });
    setToken(response.data.access_token);
    localStorage.setItem('token', response.data.access_token);
  };

  // ...
}
```

### 3.3 Charts with Recharts
Replace Streamlit/Plotly charts with Recharts:
- Bar charts for applicant types, monthly breakdown
- Pie chart for value distribution
- Line chart for daily trends

---

## Phase 4: Integration & Testing (Days 16-20)

### 4.1 Docker Setup
**File:** `docker-compose.yml`
```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - mongodb

  mongodb:
    image: mongo:7.0
    volumes:
      - mongodb_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=${MONGO_USER}
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASS}

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - frontend
      - backend
```

### 4.2 Testing Checklist
- [ ] Form submission flow (all 7 steps)
- [ ] All 3 applicant types (Individual, Joint, Corporate)
- [ ] Validation errors display correctly
- [ ] PDF generation and download
- [ ] Admin login/logout
- [ ] Dashboard metrics accuracy
- [ ] Filter and search functionality
- [ ] Export (CSV, Excel, PDF)
- [ ] Mobile responsiveness

---

## Phase 5: Deployment & Cutover (Days 21-25)

### 5.1 Data Migration
MongoDB schema remains unchanged - no data migration needed.

### 5.2 Deployment Steps
1. Deploy backend to production server
2. Build and deploy frontend
3. Update nginx configuration
4. Test all functionality
5. Switch DNS/load balancer
6. Deprecate Streamlit containers

---

## API Endpoints Summary

### Public Endpoints (User Form)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/constants` | Banks, categories, tenors |
| POST | `/api/applications` | Submit application |
| GET | `/api/applications/{id}/pdf` | Download PDF |

### Protected Endpoints (Admin)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Admin login |
| GET | `/api/admin/applications` | List with filters |
| GET | `/api/admin/summary` | Dashboard metrics |
| GET | `/api/admin/analytics` | Chart data |
| GET | `/api/admin/export/csv` | Export CSV |
| GET | `/api/admin/export/excel` | Export Excel |

---

## Dependencies

### Backend (Python)
```
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.0
motor==3.3.0
python-jose[cryptography]==3.3.0  # JWT
passlib[bcrypt]==1.7.4            # Password hashing
python-multipart==0.0.6
aiofiles==23.2.1
# Existing (keep)
reportlab==4.3.1
pillow==11.1.0
pandas==2.2.3
openpyxl==3.1.5
xlsxwriter==3.1.2
num2words==0.5.14
pytz==2025.1
```

### Frontend (Node.js)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "react-hook-form": "^7.49.0",
    "@hookform/resolvers": "^3.3.0",
    "zod": "^3.22.0",
    "axios": "^1.6.0",
    "@tanstack/react-query": "^5.17.0",
    "recharts": "^2.10.0",
    "date-fns": "^3.2.0",
    "tailwindcss": "^3.4.0"
  }
}
```

---

## Verification Plan

### Manual Testing
1. **Form Submission Flow**
   - Complete all 7 steps as Individual
   - Complete all 7 steps as Joint
   - Complete all 7 steps as Corporate
   - Verify PDF downloads correctly
   - Verify data appears in admin

2. **Admin Dashboard**
   - Login with credentials
   - Verify metrics are accurate
   - Test all filters
   - Export CSV/Excel/PDF
   - View individual application

3. **Edge Cases**
   - Validation errors show correctly
   - Required fields enforced
   - Currency formatting correct
   - Mobile responsive layout

### Automated Testing
- Backend: pytest with FastAPI TestClient
- Frontend: React Testing Library + Vitest

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Data loss during transition | Keep Streamlit running until React verified |
| PDF generation breaks | Copy pdf/ folder unchanged, test early |
| Validation mismatch | Port validation rules to both Pydantic and Zod |
| Performance regression | Load test before cutover |

---

## Success Criteria

1. All 70+ form fields work correctly
2. All 3 applicant types supported
3. PDF generation matches current output
4. Admin dashboard feature parity
5. No data loss
6. Mobile responsive
7. Performance equal or better than Streamlit
