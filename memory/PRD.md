# RERA Compliance Manager - Product Requirements Document

## Project Overview
**Application Name:** RERA Compliance Manager  
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

### Construction Progress (FORM-1 Table A)
- [x] 16 default construction activities with weightages
- [x] Per-building activity completion tracking
- [x] Quarterly progress entry
- [x] Overall weighted completion calculation
- [x] **NEW**: FORM-1 Table A structured activities (10 categories matching RERA format)
- [x] **NEW**: API endpoint for FORM-1 Table A template

### Common Development Works (FORM-1 Table B)
- [x] **NEW**: Internal Roads & Footpaths
- [x] **NEW**: Water Supply, Sewerage, Storm Drains
- [x] **NEW**: Landscaping, Street Lighting
- [x] **NEW**: Community Buildings, Sewage Treatment
- [x] **NEW**: Rainwater Harvesting, Energy Management
- [x] **NEW**: Fire Safety, Electrical Infrastructure
- [x] **NEW**: Proposed/Not Proposed flags for each item
- [x] **NEW**: Overall completion calculation

### Project Costs (FORM-3 & FORM-4 - Enhanced)
- [x] Land costs (acquisition, TDR, stamp duty, etc.)
- [x] Development costs (construction, infrastructure, etc.)
- [x] Estimated vs actual cost tracking
- [x] Balance cost calculation
- [x] **NEW**: Detailed land cost breakdown (legal cost, interest, development rights, government charges)
- [x] **NEW**: Rehabilitation scheme costs (transit accommodation, clearance, ASR premium)
- [x] **NEW**: On-site expenditure breakdown (salaries, consultants, site overheads, services, machinery)
- [x] **NEW**: Off-site expenditure tracking
- [x] **NEW**: Extra/Additional items (Annexure A) with details
- [x] **NEW**: Cost completion percentage calculation

### Financial Summary (FORM-5 - NEW)
- [x] **NEW**: Designated account balance tracking
- [x] **NEW**: Amount deposited and withdrawn per quarter
- [x] **NEW**: Total withdrawals till date
- [x] **NEW**: Receivables from sold apartments
- [x] **NEW**: Unsold area (sq.m) and ASR rate
- [x] **NEW**: Unsold inventory value calculation
- [x] **NEW**: Deposit percentage (70% or 100%) logic
- [x] **NEW**: Amount to deposit calculation

### Sales & Receivables (Annexure-A)
- [x] Unit-wise sales entry
- [x] Buyer details, agreement date, carpet area
- [x] Sale value, amount received, balance receivable
- [x] Excel import functionality

### Report Generation
- [x] Form-1: Architect Certificate (% Completion)
- [x] Form-2: Architect Completion Certificate
- [x] Form-3: Engineer Certificate (Cost Incurred)
- [x] Form-4: CA Certificate (Project Cost)
- [x] Form-5: CA Compliance Certificate
- [x] Form-6: Auditor Certificate
- [x] Annexure-A: Statement of Receivables

### Dashboard
- [x] Project completion percentage
- [x] Cost summary (estimated, incurred, balance)
- [x] Sales summary (value, collected, receivables)
- [x] RERA deposit calculation
- [x] Quick action buttons

## What's Been Implemented (January 2026 - March 2026)

### Backend (FastAPI + MongoDB)
- ✅ Complete REST API for all modules
- ✅ JWT authentication with bcrypt password hashing
- ✅ Project CRUD endpoints with 40+ fields for RERA compliance
- ✅ Building CRUD endpoints with enhanced fields (building type, parking config, floor config)
- ✅ Bulk building creation endpoint (POST /api/buildings/bulk)
- ✅ Building types configuration endpoint (GET /api/buildings/types)
- ✅ Construction progress endpoints with weighted calculation
- ✅ **NEW**: FORM-1 Table A template endpoint (/api/construction-progress/form1-table-a-template)
- ✅ **NEW**: Common Development Works CRUD (/api/common-development-works)
- ✅ Project cost endpoints with detailed Form-4 structure
- ✅ Building cost endpoints with Form-3 structure
- ✅ **NEW**: Financial Summary CRUD (/api/financial-summary) for Form-5
- ✅ Unit sales CRUD and bulk import
- ✅ Excel import endpoint with column mapping
- ✅ Excel template download
- ✅ Dashboard aggregation endpoint
- ✅ Report generation endpoint
- ✅ Data validation endpoint
- ✅ Report template storage (7 Goa RERA templates)

### Frontend (React)
- ✅ Login/Register with role selection
- ✅ Responsive sidebar navigation
- ✅ Dashboard with metrics cards
- ✅ Projects list and form pages
- ✅ **Enhanced Project Form** (March 2026) with 6 tabbed sections:
  - Basic Info (Name, State, Phase, Promoter, Plot Area, Dates, Planning Authority)
  - Location & Boundaries (Address, PTS/Chalta, Survey, Ward, Village, Boundaries)
  - RERA & Bank (Registration Number, Dates, Designated Account)
  - Architect & Engineer (Full contact details)
  - Consultants (Structural, MEP, Site Supervisor, Quantity Surveyor)
  - CA & Auditor (Full contact and membership details)
- ✅ **Enhanced Buildings management page** (March 2026)
  - Building type selector (Residential Tower, Mixed Tower, Row House, Bungalow)
  - Parking configuration (Basement, Stilt/Ground, Upper Level)
  - Floor configuration (Commercial, Residential, Apartments per floor)
  - Bulk Add dialog for multiple buildings
  - Enhanced table with Type, Parking, Floors columns
- ✅ Construction progress tracking page
- ✅ Project costs management page
- ✅ Sales & receivables page with table
- ✅ Reports generation page with preview
- ✅ Excel import page
- ✅ Blue theme with Manrope/Inter fonts

### Database Collections
- users
- projects
- buildings
- construction_progress
- project_costs
- building_costs
- unit_sales
- quarterly_reports
- report_templates

## Prioritized Backlog

### P0 - Critical (Next Sprint)
- [ ] PDF export using browser print/save
- [ ] Form signature fields for digital signatures
- [ ] Quarterly data copy from previous quarter

### P1 - High Priority
- [ ] Admin template editor with HTML preview
- [ ] Email notifications for report deadlines
- [ ] Bulk building import from Excel
- [ ] Data export to Excel

### P2 - Medium Priority
- [ ] Multi-state support (Maharashtra, Karnataka)
- [ ] Report archive with history
- [ ] Audit trail for all changes
- [ ] User management admin page

### P3 - Nice to Have
- [ ] Charts on dashboard (completion trend, cost analysis)
- [ ] Mobile app (React Native)
- [ ] WhatsApp/SMS notifications
- [ ] Integration with RERA portal APIs

## Technology Stack
- **Frontend:** React 18, TailwindCSS, Shadcn/UI
- **Backend:** FastAPI (Python 3.11+)
- **Database:** MongoDB
- **Auth:** JWT with bcrypt
- **Excel:** openpyxl

## Next Tasks
1. Implement PDF download using html2canvas/jsPDF
2. Add form signature capture component
3. Build quarterly data copy feature
4. Create admin template editor
