# CheckMate - RERA Manager - Product Requirements Document

## Project Overview
**Application Name:** CheckMate - RERA Manager  
**Purpose:** Automate RERA compliance reporting for real estate developers in India  
**Initial State:** Goa RERA  
**Created:** January 2026
**Last Updated:** March 2026

## User Personas

### Primary Users
1. **Developers/Promoters** - Create projects, manage sales, generate reports
2. **Architects** - Sign Form-1 (Construction Progress) & Form-2 (Completion)
3. **Engineers** - Sign Form-3 (Cost Incurred Statement)
4. **Chartered Accountants** - Sign Form-4 (Project Cost), Form-5 (Compliance)
5. **Auditors** - Sign Form-6 (Statement of Accounts)
6. **Admins** - Manage templates, users, system settings

## Goa RERA Report Formats (Official)

### FORM-1: Architect's Certificate (% Completion)
- **Table A**: Building-wise construction activities (Excavation, Basement/Plinth, Podiums, Stilt, Superstructure, Internal Works, Doors/Windows/Fittings, Staircases/Lifts, External Finishing, Final Installations)
- **Table B**: Common Development Works (Roads, Water Supply, Sewerage, Storm Drains, Landscaping, Fire Safety, Electrical Infrastructure, etc.)

### FORM-2: Architect's Certificate (Completion)
- Building completion certification for occupation certificate

### FORM-3: Engineer's Certificate (Cost Incurred)
- **Table A**: Building-wise estimated cost, cost incurred, balance
- **Table B**: Internal/External development works costs
- **Annexure A**: Extra/Additional items not in original estimate

### FORM-4: CA Certificate (Project Cost & Withdrawal)
- Land Cost breakdown (acquisition, development rights, TDR, stamp duty, rehabilitation costs)
- Development Cost (construction, on-site/off-site expenditure, taxes, finance cost)
- Withdrawal eligibility calculation

### FORM-5: CA Certificate (Ongoing Projects)
- Balance cost to complete
- Receivables from sold/unsold apartments
- Designated account deposit calculation (70% or 100%)

### FORM-6: CA Annual Report
- Statement of accounts on fund utilization
- Project-wise collection and withdrawal tracking

### Annexure-A: Statement of Receivables
- Sold inventory (unit, carpet area, agreement value, received, balance)
- Unsold inventory (unit, carpet area, ASR valuation)

## Core Requirements

### Authentication & Authorization
- [x] JWT-based authentication
- [x] Multi-role support (admin, developer, architect, engineer, ca, auditor)
- [x] Protected routes
- [x] Token refresh mechanism

### Project Management (Enhanced - March 2026)
- [x] Create/Edit/Delete projects
- [x] Store project master data (name, RERA number, promoter details)
- [x] Store location details (address, survey number, taluka, district)
- [x] **NEW**: PTS/Chalta Number, Ward, Municipality
- [x] **NEW**: Plot boundaries (North, South, East, West with lat/long)
- [x] **NEW**: RERA Registration & Validity dates
- [x] **NEW**: Project Phase tracking
- [x] **NEW**: Designated Bank Account (Bank Name, Account Number, IFSC)
- [x] Store professional details with full contact info:
  - Architect (Name, License, Address, Contact, Email)
  - Engineer (Name, License, Address, Contact, Email)
  - Structural Consultant, MEP Consultant, Site Supervisor, Quantity Surveyor
  - CA (Name, Firm, Membership No., Address, Contact, Email)
  - Auditor (Name, Firm, Membership No., Address, Contact, Email)
- [x] Planning Authority name

### Buildings/Wings Management (Enhanced - March 2026)
- [x] Add buildings/towers per project
- [x] Track floors, units, estimated cost per building
- [x] Completion certificate tracking
- [x] Building Type Selection (Residential Tower, Mixed Tower, Row House, Bungalow)
- [x] Parking Configuration (Basement, Stilt/Ground, Upper Level floors)
- [x] Floor Configuration (Commercial floors, Residential floors, Apartments per floor)
- [x] Auto-calculation of total floors and units based on building type
- [x] Bulk Add feature - create multiple buildings with same configuration
- [x] Enhanced table display with Type, Parking (B/S/U), Floors columns
- [x] **NEW**: On Site Expenditure tab for ESTIMATED costs (March 2026)

### Construction Progress (FORM-1 - Comprehensive Update March 2026)
- [x] 16 default construction activities with weightages (legacy)
- [x] Per-building activity completion tracking
- [x] Quarterly progress entry
- [x] Overall weighted completion calculation
- [x] **NEW**: Comprehensive 12-category, 48-activity tracking system
- [x] **NEW**: N/A (Not Applicable) checkbox for each activity
- [x] **NEW**: Automatic weightage recalibration when activities marked N/A
- [x] **NEW**: Category-wise completion percentage display
- [x] **NEW**: Expandable/collapsible category sections
- [x] **NEW**: Infrastructure Works tab (9 items, 100% total)
- [x] **NEW**: Actual Site Expenditure tab for quarterly ACTUAL costs (March 2026)

### Project Costs (FORM-3 & FORM-4 - Enhanced)
- [x] Land costs (acquisition, TDR, stamp duty, etc.)
- [x] Development costs (construction, infrastructure, etc.)
- [x] Estimated vs actual cost tracking
- [x] Balance cost calculation
- [x] **NEW**: Detailed land cost breakdown
- [x] **NEW**: Rehabilitation scheme costs
- [x] **NEW**: On-site expenditure - READ-ONLY display (March 2026)
  - Estimated costs pulled from Buildings & Infrastructure page
  - Actual costs pulled from Construction Progress page (auto-populated)
- [x] **NEW**: Off-site expenditure tracking
- [x] **NEW**: Extra/Additional items (Annexure A)
- [x] **NEW**: Cost completion percentage calculation

### Financial Summary (FORM-5 - NEW)
- [x] Designated account balance tracking
- [x] Amount deposited and withdrawn per quarter
- [x] Total withdrawals till date
- [x] Receivables from sold apartments
- [x] Unsold area and ASR rate
- [x] Unsold inventory value calculation
- [x] Deposit percentage logic
- [x] Amount to deposit calculation

### Sales & Receivables (Annexure-A)
- [x] Unit-wise sales entry
- [x] Buyer details, agreement date, carpet area
- [x] Sale value, amount received, balance receivable
- [x] Excel import functionality
- [x] **NEW**: Sales data replacement on import
- [x] **NEW**: Unsold inventory tracking

### Report Generation
- [x] Form-1: Architect Certificate (% Completion) - PDF Ready
- [x] Form-2: Architect Completion Certificate
- [x] Form-3: Engineer Certificate (Cost Incurred) - PDF Ready
- [x] Form-4: CA Certificate (Project Cost) - PDF Ready
- [x] Form-5: CA Compliance Certificate
- [x] Form-6: Auditor Certificate
- [x] Annexure-A: Statement of Receivables - PDF Ready

### Dashboard
- [x] Project completion percentage
- [x] Cost summary (estimated, incurred, balance)
- [x] Sales summary (value, collected, receivables)
- [x] RERA deposit calculation
- [x] Quick action buttons

## Completed This Session (March 2026)

### Land Cost Page Feature ✅ (Latest)
1. ✅ New "Land Cost" page created at /land-cost route
2. ✅ Navigation updated - Land Cost menu item between Projects and Buildings & Infra
3. ✅ Page has 10 cost fields (a-j) for both Estimated and Actual:
   - a) Land Cost (acquiring land or land rights)
   - b) Premium Cost (FSI, Fungible area to Statutory Authority)
   - c) TDR Cost
   - d) Statutory Cost (Stamp duty, registration fees, etc.)
   - e) Land Premium (ASR for redevelopment of Govt. land)
   - f) Under Rehab Scheme
   - g) Estimated Cost for Rehab (certified by Engineer)
   - h) Actual Cost of Rehab (certified by CA)
   - i) Cost towards Land Clearance
   - j) Cost of ASR Linked Premium
4. ✅ New backend endpoint: GET/POST /api/land-cost/{project_id}
5. ✅ Project Costs page updated - Land Cost sections now READ-ONLY
   - Shows "Auto-populated from Land Cost page" badge
   - Both Estimated and Actual sections pull from Land Cost page
6. ✅ All tests passed (Backend 100%, Frontend 100%)

### On Site Expenditure Relocation Feature ✅
1. ✅ Estimated costs entry moved to Buildings & Infrastructure page ("On Site Expenditure" tab)
2. ✅ Actual costs entry added to Construction Progress page ("Actual Site Expenditure" tab)
3. ✅ Project Costs page "On Site Expenditure" section now READ-ONLY
   - Displays "Auto-populated" badge
   - Shows "Data entered in Construction Progress page" message
   - Pulls estimated costs from Buildings page
   - Pulls actual costs from Construction Progress page
4. ✅ New backend endpoint: GET/POST /api/actual-site-expenditure (per quarter/year)
5. ✅ All tests passed (Backend 100%, Frontend 100%)

### Previous Completions
- ✅ PDF generation for Form-1, Form-3, Form-4, Annexure-A
- ✅ Sales data import with replacement logic
- ✅ Indian number formatting (lakhs/crores)
- ✅ App rebranding to "CheckMate - RERA Manager"

## Prioritized Backlog

### P1 - High Priority
- [ ] Implement PDF generation for Form-2, Form-5, Form-6
- [ ] Develop Quarterly Reporting feature
- [ ] Refactor `backend/server.py` into separate route files (>3400 lines)

### P2 - Medium Priority
- [ ] Build data validation module
- [ ] Create admin-only "Template Editor"
- [ ] Implement "Reports Archive"
- [ ] Multi-state support (Maharashtra, Karnataka)

### P3 - Nice to Have
- [ ] Charts on dashboard (completion trend, cost analysis)
- [ ] Digital signature fields
- [ ] Email notifications for report deadlines

## Technology Stack
- **Frontend:** React 18, TailwindCSS, Shadcn/UI
- **Backend:** FastAPI (Python 3.11+)
- **Database:** MongoDB
- **Auth:** JWT with bcrypt
- **Excel:** openpyxl
- **PDF:** reportlab
- **File Downloads:** file-saver

## Database Collections
- users
- projects
- buildings
- construction_progress
- infrastructure_progress
- project_costs
- building_costs
- unit_sales
- site_expenditure (estimated)
- actual_site_expenditure (per quarter)
- land_costs (estimated + actual)
- quarterly_reports
- report_templates

## Key API Endpoints
- **Auth:** /api/auth/login, /api/auth/register, /api/auth/me
- **Projects:** /api/projects (CRUD)
- **Land Cost:** /api/land-cost/{project_id}
- **Buildings:** /api/buildings, /api/buildings/bulk
- **Construction Progress:** /api/construction-progress, /api/construction-progress/detailed
- **Infrastructure:** /api/infrastructure-progress, /api/infrastructure-costs
- **Site Expenditure (Estimated):** /api/site-expenditure/{project_id}
- **Site Expenditure (Actual):** /api/actual-site-expenditure/{project_id}?quarter=Q1&year=2026
- **Project Costs:** /api/project-costs, /api/estimated-development-cost
- **Sales:** /api/unit-sales, /api/import/sales
- **Reports:** /api/projects/{project_id}/report/download/{form_name}
- **Dashboard:** /api/dashboard/{project_id}

