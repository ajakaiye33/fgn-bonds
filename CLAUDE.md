# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FGN Savings Bond Subscription Application - A modern React + FastAPI web application for submitting Federal Government of Nigeria Savings Bond applications. Digitizes the official DMO FGNSB subscription form process.

**Author:** Hedgar Ajakaiye
**License:** MIT

## Tech Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, React Hook Form, Zod, Recharts
- **Backend**: FastAPI, Pydantic, SQLAlchemy, SQLite
- **PDF Generation**: ReportLab
- **Authentication**: JWT with bcrypt
- **Deployment**: Docker, Nginx

## Build & Run Commands

### Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Local Development

```bash
# Backend (terminal 1)
cd backend
source venv/bin/activate  # or: python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (terminal 2)
cd frontend
npm install
npm run dev
```

### Using Makefile

```bash
make help          # Show all commands
make setup         # First-time setup
make up            # Start Docker services
make dev           # Start local development
make down          # Stop services
make logs          # View logs
make test          # Run tests
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         NGINX (:80)                         │
│         /api/* → Backend    /* → Frontend                   │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   │
┌─────────────────┐  ┌─────────────────┐         │
│    Frontend     │  │     Backend     │         │
│  React + Vite   │  │    FastAPI      │         │
│    (:3000)      │  │    (:8000)      │         │
└─────────────────┘  └────────┬────────┘         │
                              │                   │
                              ▼                   │
                    ┌─────────────────┐          │
                    │  SQLite + PDF   │◄─────────┘
                    └─────────────────┘
```

## Project Structure

```
fgnbond_sub/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models/              # SQLAlchemy models
│   │   │   └── application.py   # Application model
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── application.py   # Application request/response
│   │   │   ├── auth.py          # Auth schemas
│   │   │   └── admin.py         # Admin schemas
│   │   ├── routers/             # API endpoints
│   │   │   ├── applications.py  # /api/applications
│   │   │   ├── auth.py          # /api/auth
│   │   │   └── admin.py         # /api/admin
│   │   ├── services/            # Business logic
│   │   │   └── pdf.py           # PDF generation service
│   │   └── utils/               # Utilities
│   │       ├── constants.py     # Banks, categories, etc.
│   │       └── money.py         # Number-to-words
│   ├── pdf/                     # PDF generation (ReportLab)
│   │   ├── generator.py         # PDFGenerator class
│   │   ├── templates.py         # FGNSBTemplate
│   │   ├── styles.py            # Colors and table styles
│   │   └── elements.py          # Custom PDF elements
│   ├── data/                    # SQLite database
│   ├── requirements.txt
│   ├── .env                     # Environment config
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── wizard/          # Form wizard steps
│   │   │   │   ├── Step1BondDetails.tsx
│   │   │   │   ├── Step2ApplicantType.tsx
│   │   │   │   ├── Step3ApplicantInfo.tsx
│   │   │   │   ├── Step4BankDetails.tsx
│   │   │   │   ├── Step5Classification.tsx
│   │   │   │   ├── Step6Distribution.tsx
│   │   │   │   └── Step7Review.tsx
│   │   │   ├── ui/              # Reusable components
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Select.tsx
│   │   │   │   └── ...
│   │   │   └── FormWizard.tsx   # Main wizard component
│   │   ├── pages/
│   │   │   ├── SubscriptionForm.tsx
│   │   │   ├── AdminLogin.tsx
│   │   │   └── AdminDashboard.tsx
│   │   ├── hooks/
│   │   │   ├── useFormWizard.ts
│   │   │   └── useAuth.ts
│   │   ├── services/
│   │   │   └── api.ts           # Axios API client
│   │   ├── lib/
│   │   │   ├── validation.ts    # Zod schemas
│   │   │   ├── constants.ts     # Banks, categories
│   │   │   └── utils.ts         # Helpers
│   │   └── types/
│   │       └── application.ts   # TypeScript types
│   ├── package.json
│   ├── vite.config.ts           # Vite config with API proxy
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── nginx/
│   └── nginx.conf               # Reverse proxy config
│
├── docker-compose.yml
├── Makefile
├── README.md
└── CLAUDE.md
```

## Key Files to Know

### Backend

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app, CORS, routers |
| `backend/app/config.py` | Environment settings |
| `backend/app/routers/applications.py` | Form submission, PDF download |
| `backend/app/routers/admin.py` | Dashboard, filters, exports |
| `backend/app/routers/auth.py` | JWT login, password verification |
| `backend/app/schemas/application.py` | Pydantic validation |
| `backend/pdf/generator.py` | PDF generation logic |

### Frontend

| File | Purpose |
|------|---------|
| `frontend/src/App.tsx` | Routes configuration |
| `frontend/src/components/FormWizard.tsx` | 7-step form wizard |
| `frontend/src/pages/AdminDashboard.tsx` | Admin with charts |
| `frontend/src/services/api.ts` | API client (axios) |
| `frontend/src/lib/validation.ts` | Zod schemas |
| `frontend/src/lib/constants.ts` | Banks, categories |

## API Endpoints

### Public
- `GET /api/health` - Health check
- `GET /api/constants` - Form constants (banks, categories)
- `POST /api/applications` - Submit application
- `GET /api/applications/{id}/pdf` - Download PDF

### Admin (JWT Protected)
- `POST /api/auth/login` - Admin login
- `GET /api/auth/me` - Current user
- `GET /api/admin/applications` - List with filters
- `GET /api/admin/summary` - Dashboard metrics
- `GET /api/admin/analytics` - Chart data
- `GET /api/admin/export/csv` - Export CSV
- `GET /api/admin/export/excel` - Export Excel

## Applicant Types

Three applicant types with different form structures:
- **Individual** - Personal details, CSCS/CHN numbers
- **Joint** - Primary + secondary applicant
- **Corporate** - Company details, RC number

## Key Constants

### Banks (22 Nigerian banks)
Located in `backend/app/utils/constants.py` and `frontend/src/lib/constants.ts`

### Investor Categories (10 types)
Individual, Insurance, Corporate, Others, Foreign Investor, Non-Bank Financial Institution, Co-operative Society, Government Agencies, Staff Scheme, Micro Finance Bank

### Bond Values
- Minimum: ₦5,000
- Maximum: ₦50,000,000
- Step: ₦1,000

### Design Tokens
- Primary: DMO Green `#006400`
- Accent: `#4CAF50`
- Dark theme for form, light charts

## Configuration

### Backend (.env)
```bash
ENVIRONMENT=development
DATABASE_URL=sqlite:///./data/fgn_bonds.db
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=<bcrypt-hash>
JWT_SECRET_KEY=<secret>
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### Frontend (vite.config.ts)
API proxy configured to forward `/api` to backend:8000

## Testing

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

## Common Tasks

### Add new form field
1. Add to `backend/app/models/application.py` (SQLAlchemy)
2. Add to `backend/app/schemas/application.py` (Pydantic)
3. Add to `frontend/src/types/application.ts` (TypeScript)
4. Add to `frontend/src/lib/validation.ts` (Zod)
5. Add to appropriate step component

### Update PDF layout
Edit `backend/pdf/templates.py` (FGNSBTemplate class)

### Add admin filter
1. Add to `backend/app/schemas/admin.py` (AdminFilters)
2. Update `backend/app/routers/admin.py` (apply_filters)
3. Add UI in `frontend/src/pages/AdminDashboard.tsx`

## Troubleshooting

### CORS errors
Check `CORS_ORIGINS` in `backend/.env` includes frontend URL

### PDF not generating
Check ReportLab and Pillow are installed

### Auth failing
Verify `ADMIN_PASSWORD_HASH` is valid bcrypt hash
