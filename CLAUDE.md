# CLAUDE.md - CheckMate (RERA Compliance Manager)

## Project Overview

CheckMate is a full-stack web application for managing RERA (Real Estate Regulatory Authority) compliance reporting for Indian real estate developers. It tracks construction progress, costs, sales, and generates statutory quarterly forms (Form 1-6, Annexure-A) in PDF, Word, and Excel formats.

**Repo:** https://github.com/diwakarramamurthy/CheckMate.git
**Branch:** main

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Tailwind CSS 3.4, Shadcn/UI (Radix primitives), React Router 7, Axios, React Hook Form + Zod, Recharts |
| Backend | Python FastAPI (async), Motor (async MongoDB), PyJWT, bcrypt |
| Database | MongoDB Atlas |
| Report Gen | ReportLab (PDF), python-docx (Word), openpyxl (Excel) |
| Package Mgr | Yarn (frontend), pip (backend) |
| Build | Craco (CRA wrapper), path alias `@/` → `src/` |
| Deployment | Render (render.yaml) |

---

## Project Structure

```
CheckMate/
├── backend/
│   ├── server.py              # Main FastAPI app (~3,500 lines, all routes + models)
│   ├── pdf_generator.py       # ReportLab PDF generation for all form types
│   ├── docx_generator.py      # python-docx Word generation
│   ├── excel_generator.py     # openpyxl Excel generation
│   ├── requirements.txt       # Python deps (unpinned, cross-platform)
│   ├── .env.example           # Required env vars template
│   └── .env                   # Local env (gitignored)
│
├── frontend/
│   ├── src/
│   │   ├── App.js             # Monolithic (~5,000 lines) - ALL pages, components, routing
│   │   ├── App.css            # CSS variable overrides, animations, report styles
│   │   ├── index.js           # React DOM entry point
│   │   ├── index.css          # Tailwind directives + custom utilities
│   │   ├── components/ui/     # 30+ Shadcn/UI components (button, card, dialog, table, etc.)
│   │   ├── hooks/use-toast.js # Custom toast notification hook
│   │   └── lib/utils.js       # cn() utility (clsx + tailwind-merge)
│   ├── tailwind.config.js     # Theme: colors, animations, dark mode
│   ├── craco.config.js        # Webpack config, path aliases, ESLint
│   ├── components.json        # Shadcn CLI config (new-york style)
│   └── package.json           # Yarn, React 19, all deps
│
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── DATABASE_SCHEMA.md
│   └── architecture/          # 10 detailed architecture docs (01-10)
│
├── tests/                     # Test suite directory
├── design_guidelines.json     # UI/UX spec (colors, typography, spacing)
├── render.yaml                # Render deployment config
├── start_all.bat              # Launches backend + frontend
├── start_backend.bat          # Backend only
├── start_frontend.bat         # Frontend only
└── backend_test.py            # API integration test suite
```

---

## Running the Project

### Backend
```bash
cd backend
pip install -r requirements.txt
# Create .env with: MONGO_URL, DB_NAME, JWT_SECRET, CORS_ORIGINS
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend
```bash
cd frontend
yarn install
REACT_APP_BACKEND_URL=http://localhost:8001 yarn start
# Runs on http://localhost:3000
```

### Combined (Windows)
```bash
start_all.bat   # Opens both in separate terminals
```

### Environment Variables (backend/.env)
```
MONGO_URL=mongodb+srv://...          # MongoDB Atlas connection string
DB_NAME=checkmate_rera               # Database name
JWT_SECRET=<strong-secret>           # JWT signing key
CORS_ORIGINS=http://localhost:3000   # Comma-separated allowed origins
```

---

## Architecture Patterns

### Backend (server.py)

- **Single-file architecture**: All routes, models, and logic in `server.py`
- **Async everything**: All routes are async, using Motor for non-blocking MongoDB
- **Pydantic models**: Separate `*Base`, `*Create`, `*Response` classes per resource
- **JWT auth**: HS256, 24h expiry, `get_current_user()` dependency injection
- **UUID IDs**: `str(uuid.uuid4())` for all resource identifiers
- **Timestamps**: `datetime.now(timezone.utc).isoformat()` everywhere
- **Upsert pattern**: `update_one({query}, {"$set": data}, upsert=True)` for quarterly records
- **Cascading deletes**: Deleting a project removes buildings, construction_progress, project_costs, unit_sales (see Known Limitations for gaps)
- **API prefix**: All endpoints under `/api/`

### Frontend (App.js)

- **Monolithic file**: All pages, components, routing, and state in one file
- **React Context for auth**: `AuthProvider` + `useAuth()` hook
- **Token storage**: `localStorage` key `rera_token`, auto-set on Axios headers
- **State pattern**: Local `useState` per page, no global store (no Redux/Zustand)
- **Form pattern**: `form` object state + `handleChange(field, value)` handler
- **API pattern**: `try { axios.get/post } catch { toast.error(detail) } finally { setLoading(false) }`
- **Dialog pattern**: `dialogOpen` + `editingItem` state pair, reset on close
- **Currency**: `Intl.NumberFormat('en-IN')` for Indian number formatting (lakhs/crores)
- **Protected routes**: `<ProtectedRoute>` wrapper checks `useAuth().user`

---

## Frontend Routes & Pages

| Route | Page | Description |
|-------|------|-------------|
| `/login` | LoginPage | Email/password auth, register toggle |
| `/dashboard` | DashboardPage | KPI cards, project selector, progress bars |
| `/projects` | ProjectsPage | Project list with CRUD |
| `/projects/new` | ProjectFormPage | 6-tab form (70+ fields) |
| `/projects/:id/edit` | ProjectFormPage | Edit mode |
| `/land-cost` | LandCostPage | Estimated vs actual land costs |
| `/buildings` | BuildingsPage | Buildings + infrastructure costs (tabbed) |
| `/construction` | ConstructionProgressPage | Tower + infrastructure progress by quarter |
| `/costs` | ProjectCostsPage | Full cost tracking (land, dev, site expenditure) |
| `/sales` | SalesPage | Unit sales CRUD, sold/unsold tabs |
| `/reports` | ReportsPage | Generate Form 1-6 + Annexure-A (PDF/Excel/Word) |
| `/import` | ImportPage | Excel upload for bulk sales import |

---

## API Endpoints (50+)

### Auth
- `POST /api/auth/register` — Register user
- `POST /api/auth/login` — Login, returns JWT + user
- `GET /api/auth/me` — Current user profile

### Projects
- `POST /api/projects` | `GET /api/projects` | `GET /api/projects/{id}` | `PUT /api/projects/{id}` | `DELETE /api/projects/{id}`

### Buildings
- `POST /api/buildings` | `POST /api/buildings/bulk` | `GET /api/buildings?project_id=` | `GET /api/buildings/{id}` | `PUT /api/buildings/{id}` | `DELETE /api/buildings/{id}` | `GET /api/buildings/types`

### Construction Progress
- `POST /api/construction-progress` | `GET /api/construction-progress` | `GET /api/construction-progress/default-activities` | `GET /api/construction-progress/detailed-template` | `POST /api/construction-progress/detailed`

### Infrastructure Progress
- `POST /api/infrastructure-progress` | `GET /api/infrastructure-progress` | `GET /api/infrastructure-progress/latest/{project_id}`

### Costs
- `POST /api/project-costs` | `GET /api/project-costs` | `GET /api/project-costs/latest/{project_id}`
- `POST /api/building-costs` | `GET /api/building-costs`
- `POST /api/infrastructure-costs` | `GET /api/infrastructure-costs/{project_id}` | `GET /api/infrastructure-costs/template`
- `POST /api/estimated-development-cost` | `GET /api/estimated-development-cost/{project_id}`
- `GET /api/land-cost/{project_id}` | `POST /api/land-cost/{project_id}`
- `GET /api/site-expenditure/{project_id}` | `POST /api/site-expenditure`
- `GET /api/actual-site-expenditure/{project_id}` | `POST /api/actual-site-expenditure`

### Sales
- `POST /api/unit-sales` | `GET /api/unit-sales?project_id=` | `PUT /api/unit-sales/{id}` | `DELETE /api/unit-sales/{id}` | `POST /api/unit-sales/bulk`

### Financial Summary
- `POST /api/financial-summary` | `GET /api/financial-summary` | `GET /api/financial-summary/latest/{project_id}`

### Reports & Generation
- `GET /api/generate-report/{project_id}/{report_type}?quarter=&year=` — HTML preview
- `GET /api/generate-pdf/{project_id}/{report_type}?quarter=&year=` — PDF download
- `GET /api/generate-excel/{project_id}/{report_type}?quarter=&year=` — Excel download
- `GET /api/generate-docx/{project_id}/{report_type}?quarter=&year=` — Word download
- `POST /api/report-templates` | `GET /api/report-templates` | `PUT /api/report-templates/{id}`

### Dashboard & Validation
- `GET /api/dashboard/{project_id}` — Project summary stats
- `GET /api/validate/{project_id}` — Data completeness check

### Import
- `POST /api/import/sales-excel?project_id=` — Upload Excel sales data
- `GET /api/import/sales-template` — Download import template

---

## MongoDB Collections (17)

| Collection | Purpose | Key Indexes |
|-----------|---------|-------------|
| `users` | User accounts | email (unique), user_id (unique) |
| `projects` | RERA projects | project_id (unique) |
| `buildings` | Buildings/towers per project | building_id (unique) |
| `construction_progress` | Quarterly tower progress (12 activity categories) | progress_id (unique) |
| `infrastructure_progress` | Quarterly infra progress (13 work items) | — |
| `project_costs` | Form-4 CA certificate data | — |
| `building_costs` | Form-3 per-building costs | — |
| `unit_sales` | Individual unit sales (Annexure-A) | sale_id (unique) |
| `financial_summaries` | Form-5 financial data | — |
| `infrastructure_costs` | Estimated infra costs | — |
| `estimated_development_costs` | Total dev cost estimates | — |
| `land_costs` | Estimated vs actual land costs | — |
| `site_expenditure` | On-site expenditure tracking | — |
| `actual_site_expenditure` | Actual quarterly expenditure | — |
| `common_development_works` | Common area works progress | — |
| `quarterly_reports` | Report metadata (draft/submitted/approved) | — |
| `report_templates` | HTML templates with `{{placeholders}}` | (state, report_type) compound |

---

## Authentication & Roles

**JWT**: HS256, 24h expiry, payload: `{sub: user_id, email, role, exp}`
**Password**: bcrypt hashed
**Token**: Bearer token in `Authorization` header

| Role | Access |
|------|--------|
| `admin` | Full system access |
| `developer` | Project management, imports, reports |
| `architect` | Form 1 & 2 (completion certificates) |
| `engineer` | Form 3 (cost incurred) |
| `ca` | Forms 4, 5 & Annexure-A (financial) |
| `auditor` | Form 6 (audit certificate) |

---

## Report Types

| Report | Name | Generator Support |
|--------|------|-------------------|
| Form-1 | Architect Certificate (% Completion) | PDF, Excel, Word |
| Form-2 | Architect Completion Certificate | HTML only |
| Form-3 | Engineer Certificate (Cost Incurred) | PDF, Excel, Word |
| Form-4 | CA Certificate (Project Cost Statement) | PDF, Excel, Word |
| Form-5 | CA Compliance (Receivables) | HTML only |
| Form-6 | Auditor Certificate | HTML only |
| Annexure-A | Statement of Receivables | PDF, Excel, Word |

---

## Design System

- **Identity**: "The Digital Architect" — Swiss Bureaucracy 2.0
- **Primary**: Deep Royal Blue `#172554` (trust, authority)
- **Accent**: Blue 600 `#2563EB` (interactive elements)
- **Fonts**: Manrope (headings), Inter (body), JetBrains Mono (code)
- **Dark mode**: Tailwind configured (class-based) but not actively enabled in the UI
- **Components**: Shadcn/UI new-york style
- **Touch targets**: 44px minimum
- **Contrast**: 4.5:1 ratio
- **Spacing**: 6-12px padding/margin scale
- **Currency format**: Indian numbering (lakhs, crores) via `Intl.NumberFormat('en-IN')`

---

## Key Development Conventions

### Code Style
- No TypeScript (plain JS frontend, Python backend)
- Shadcn/UI components imported from `@/components/ui/`
- `cn()` utility for conditional Tailwind classes
- Page components named `{Feature}Page`
- State variables: `selected{X}`, `{x}Loading`, `{x}Saving`, `editing{X}`, `{x}DialogOpen`
- Handlers: `handle{Action}`, `fetch{Data}`, `calculate{X}`, `format{X}`

### API Conventions
- All IDs are UUIDs (string)
- All timestamps are UTC ISO strings
- Error responses: `{ "detail": "message" }`
- File downloads return `StreamingResponse` with `Content-Disposition`
- Quarterly data keyed by `(project_id, quarter, year)` with upsert
- `_id` field excluded from all MongoDB responses

### Testing
- `backend_test.py` — Integration tests against live API
- `data-testid` attributes on frontend elements for test selectors
- Test pattern: create → read → update → verify → cleanup

---

## Deployment (Render)

Backend and frontend configured in `render.yaml`:
- **Backend**: Python runtime, port 8001
- **Frontend**: Static site build with `yarn build`
- **Database**: MongoDB Atlas (external, connection string in env)
- **CORS**: Must include frontend domain in `CORS_ORIGINS`

---

## Weighted Completion Calculations

### Tower Construction (12 categories)
Plinth, Slab, Brickwork/Plastering, Plumbing, Electrical, Windows, Tiling/Flooring, Doors, Waterproofing, Painting, Carpark, Handover — each with sub-activities and individual weightages. Recalibrated when items marked N/A.

### Infrastructure (13 items)
Road/Footpath (21.5%), Sewage Network (13%), STP (8.5%), Water Tank (8.5%), Water Distribution (10.5%), Electrical (10.5%), Street Lights (4%), Entry Gate (2.5%), Boundary Wall (6%), Club House (7%), Swimming Pool (3.5%), Amphitheatre (2.5%), Gardens (2%). Recalibrated when items marked N/A.

---

## Common Tasks

**Adding a new API endpoint**: Add route + Pydantic models in `backend/server.py`
**Adding a new page**: Add component + route in `frontend/src/App.js`
**Adding a new report type**: Update `pdf_generator.py`, `excel_generator.py`, `docx_generator.py` + add frontend button in ReportsPage
**Supporting a new state**: Add template config, validation rules, update frontend state selector
**Modifying Excel import**: Update column mapping in import endpoint in `server.py`

---

## Business Rules (Hardcoded in server.py)

### RERA 70% Deposit Rule (Form-5 / Dashboard)
The most critical compliance calculation. Determines how much a developer must deposit in their designated RERA account:

```
IF total_receivables > balance_cost:
    deposit = total_receivables × 70%     (ratio > 1)
ELSE:
    deposit = total_receivables × 100%    (ratio ≤ 1)
```

- **Where applied**: `create_financial_summary()` (line ~2195) and `get_dashboard()` (line ~2502)
- **total_receivables** = sold unit balance receivables + unsold inventory value
- **balance_cost** = estimated cost − cost incurred to date
- **Impact**: Directly determines the RERA deposit amount shown on dashboard and in Form-5

### Building Unit Calculation
Runs on every building create/update/read via `calculate_building_totals()`:

| Building Type | Total Floors | Total Units |
|--------------|-------------|-------------|
| `residential_tower` | parking + residential | residential_floors × apartments_per_floor |
| `mixed_tower` | parking + commercial + residential | residential_floors × apartments_per_floor |
| `row_house` | parking + residential | **Always 1** |
| `bungalow` | parking + residential | **Always 1** |

- Commercial floors exist only in `mixed_tower`
- Total parking = basement + stilt + upper_level parking floors
- Backward compatibility: recalculates totals on read if fields are missing

### Construction Progress Recalibration Algorithm
Complex weighted completion calculation in `calculate_recalibrated_completion()` (line ~1676):

**Two modes per category:**

1. **Template-based (default)**: Each sub-activity has a fixed `base_weightage` from the template
2. **Cost-based** (flag: `_use_cost_weightage`): `effective_weight = (activity_cost / total_category_cost) × category_base_applicable_weight`

**N/A handling**: When a sub-activity is marked `is_applicable: False`, its weightage is excluded and the remaining weights are recalibrated proportionally.

**Formula**:
```
category_completion = Σ(effective_weight × completion%) / Σ(applicable_weights) × 100
overall_completion  = Σ(all_weighted_completion) / Σ(all_applicable_weights) × 100
```

### Sales Status Assignment
During Excel import (`import_sales_excel`, line ~2366):
- **buyer_name is filled** → status = `"sold"`
- **buyer_name is empty** → status = `"unsold"`
- **balance_receivable** = `sale_value - amount_received` (negative = over-collection)

### Validation Rules (validate_project_data endpoint)
- Required fields: `project_name`, `rera_number`, `promoter_name`, `architect_name`, `engineer_name`, `ca_name`
- Duplicate unit number detection
- Negative receivable warnings (buyer over-paid)
- Cost overrun warnings (actual > estimated)
- Receivable-to-cost ratio > 1.5 flagged as warning

---

## Multi-State Template System

Report templates are stored per-state in MongoDB (`report_templates` collection) with `{{placeholder}}` syntax for dynamic data injection.

| State | Status | Templates |
|-------|--------|-----------|
| **Goa** | Active (auto-initialized on first run) | Form 1-6, Annexure-A |
| Maharashtra | Planned (schema ready) | Not yet created |
| Other states | Planned | Not yet created |

**How templates work:**
1. Templates are HTML with `{{placeholder}}` markers (e.g., `{{project_name}}`, `{{deposit_70}}`)
2. On report generation, backend fetches the template by `(state, report_type)`
3. Placeholders are replaced with computed project data
4. Result is rendered as HTML preview, or passed to PDF/Excel/Word generators

**Adding a new state**: Insert templates via `POST /api/report-templates` (admin-only), then the state appears automatically in the frontend state selector.

---

## Missing API Endpoints in Previous Section

### Common Development Works
- `POST /api/common-development-works` — Save common area works progress (upsert by project/quarter/year)
- `GET /api/common-development-works?project_id=&quarter=&year=` — List works
- `GET /api/common-development-works/latest/{project_id}` — Latest entry

### Quarterly Reports (Metadata)
- `POST /api/quarterly-reports` — Create report metadata (tracks draft/submitted/approved status)
- `GET /api/quarterly-reports?project_id=` — List report metadata

### Health & Root
- `GET /api/` — API info (`{"message": "CheckMate - RERA Manager API", "version": "1.0.0"}`)
- `GET /api/health` — Health check (`{"status": "healthy", "timestamp": "..."}`)

---

## Operational Details

### First-Run Behavior
On startup (`@app.on_event("startup")`), the backend automatically:
1. Creates 6 MongoDB indexes:
   - `users.email` (unique)
   - `users.user_id` (unique)
   - `projects.project_id` (unique)
   - `buildings.building_id` (unique)
   - `unit_sales.sale_id` (unique)
   - `report_templates.(state, report_type)` (compound)
2. Checks if Goa templates exist — if not, initializes all 7 Goa RERA templates
3. Logs "CheckMate - RERA Manager API started"

### Shutdown
`@app.on_event("shutdown")` closes the MongoDB client connection.

### CORS Configuration
Backend resolves CORS origins in this order:
1. `CORS_ORIGINS` env var (comma-separated)
2. **Fallback** (if env var empty): `https://checkmate-frontend-ei62.onrender.com`, `http://localhost:3000`

All methods and headers are allowed (`allow_methods=["*"]`, `allow_headers=["*"]`).

### Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| CORS errors in browser | `CORS_ORIGINS` env var missing or wrong | Add frontend URL to `CORS_ORIGINS` in `.env` |
| MongoDB connection timeout | Atlas IP whitelist | Add server IP to Atlas Network Access |
| JWT decode errors | Secret mismatch between instances | Ensure same `JWT_SECRET` across all instances |
| "No report template found" | State templates not initialized | POST templates via admin endpoint or restart for Goa auto-init |
| Blank PDF/Excel downloads | Generator import error | Check server logs for import errors in `pdf_generator.py` etc. |
| Login returns 401 after restart | JWT_SECRET changed | Users must re-login; old tokens are invalid |
| Import shows 0 created | Column headers don't match aliases | Check column mapping in `import_sales_excel` (~line 2330) |

---

## Third-Party Integrations

### PostHog Analytics (Frontend)
- **Embedded in**: `frontend/public/index.html`
- **API key**: Hardcoded in HTML (not env-driven)
- **Host**: `https://us.i.posthog.com`
- **Config**: `person_profiles: "identified_only"` — only creates profiles for logged-in users
- **Tracks**: Page views, session recordings, user interactions

### Emergent.sh (Frontend Dev Tool)
- **Embedded in**: `frontend/public/index.html` (badge script)
- **Config**: `craco.config.js` has optional visual editing overlay
- **Purpose**: Visual editing and debugging in development
- **Note**: Badge visible in production — may want to conditionally load

### Google Fonts (Frontend)
- **Loaded in**: `frontend/public/index.html` via `<link>` tags
- **Fonts**: Inter (body), Manrope (headings), JetBrains Mono (code/data)
- **Preconnect**: `fonts.googleapis.com`, `fonts.gstatic.com`

---

## Security Notes

### JWT Default Secret
`server.py` line 28 falls back to `'rera-compliance-secret-key-2024'` if `JWT_SECRET` env var is not set. **Always set JWT_SECRET in production.**

### Role-Based Access Control (Incomplete)
Only 2 endpoints enforce role checks:
- `POST /api/report-templates` — admin only
- `PUT /api/report-templates/{id}` — admin only

**All other endpoints** only check for a valid JWT (any authenticated user can access any data). The role field exists in the user model and JWT payload but is not enforced on most routes.

### No Rate Limiting
No rate limiting or request throttling is implemented. All endpoints are open to unlimited requests from authenticated users.

### No Token Refresh
JWT tokens expire after 24 hours with no refresh mechanism. Users must re-login after expiry.

### Password Requirements
No password strength validation — any non-empty string is accepted.

### Sensitive Data in Code
- JWT default secret in `server.py`
- PostHog API key in `index.html`
- Render production URL in CORS fallback
- No secrets scanning or pre-commit hooks configured

---

## Testing

### What Exists
- `backend_test.py` — Integration tests running against a live API instance
- Tests cover: building CRUD, land cost API, PDF generation, site expenditure
- Frontend has `data-testid` attributes for selector-based testing

### What's Missing
- **No frontend tests** — no Jest, React Testing Library, or Cypress
- **No unit tests** for backend business logic (recalibration algorithm, 70% rule, building calculations)
- **No test for Excel import** (critical data-replacement operation)
- **No test for cascading deletes**
- **No test for auth flow** (registration, login, token expiry)
- **No test for financial summary calculations**
- **No CI/CD pipeline** — no GitHub Actions, no automated test runs
- **No test database** — tests run against the same database as development

---

## Known Limitations & Technical Debt

### Architecture
- **Monolithic frontend**: All ~5,000 lines in a single `App.js` — no component splitting, code splitting, or lazy loading
- **Monolithic backend**: All ~3,500 lines in a single `server.py` — no route separation or service layer
- **No TypeScript**: Frontend has no type safety
- **No error boundary**: A React render crash takes down the entire app
- **No i18n**: All text is hardcoded in English
- **No Docker**: Deployed as raw services on Render; no containerization

### Data Integrity
- **Incomplete cascading deletes**: Deleting a project removes `buildings`, `construction_progress`, `project_costs`, `unit_sales` but **orphans** these 9 collections:
  - `infrastructure_progress`
  - `building_costs`
  - `infrastructure_costs`
  - `estimated_development_costs`
  - `land_costs`
  - `site_expenditure`
  - `actual_site_expenditure`
  - `common_development_works`
  - `financial_summaries`
- **Missing MongoDB indexes**: No compound index on `(project_id, quarter, year)` despite heavy query usage — will degrade at scale
- **No pagination**: Many queries use `.to_list(10000)` — will OOM on large datasets

### File Management
- **Temp files not cleaned**: Sales template download uses `tempfile.NamedTemporaryFile(delete=False)` — files accumulate on disk indefinitely
- **No file size limits**: Excel upload has no max file size enforcement

### Operational
- **Minimal logging**: Only PDF/Excel/Word generation errors are logged; no audit trail for user actions, data changes, or imports
- **Basic health check**: Returns `{"status": "healthy"}` without checking MongoDB connectivity or template availability
- **No database backup strategy**: MongoDB Atlas has built-in backups but no documented restore procedure
- **No git branching strategy**: All development happens on `main`

### Frontend
- **Dark mode configured but not enabled**: Tailwind dark mode is set up (class-based) but no toggle exists in the UI
- **44 Shadcn/UI components installed, ~15 used**: Unused components add to bundle size
- **Print stylesheets exist** (`@media print` rules in App.css and index.css) but are not well-tested
- **Custom CurrencyInput component**: Inline in App.js, formats Indian numbers on blur, selects-all on focus — not extracted as reusable

### Report Generation
- **Forms 2, 5, 6 only support HTML preview** — no PDF/Excel/Word export
- **Generator modules imported at runtime** (not at top of server.py) — import errors only surface when generating a report
- **Some endpoints use raw `await request.json()`** instead of Pydantic models — no schema validation for detailed progress saves
