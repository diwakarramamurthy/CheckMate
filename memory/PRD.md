# RERA Compliance Manager - Product Requirements Document

## Project Overview
**Application Name:** RERA Compliance Manager  
**Purpose:** Automate RERA compliance reporting for real estate developers in India  
**Initial State:** Goa RERA  
**Created:** January 2026

## User Personas

### Primary Users
1. **Developers/Promoters** - Create projects, manage sales, generate reports
2. **Architects** - Sign Form-1 (Construction Progress) & Form-2 (Completion)
3. **Engineers** - Sign Form-3 (Cost Incurred Statement)
4. **Chartered Accountants** - Sign Form-4 (Project Cost), Form-5 (Compliance)
5. **Auditors** - Sign Form-6 (Statement of Accounts)
6. **Admins** - Manage templates, users, system settings

## Core Requirements

### Authentication & Authorization
- [x] JWT-based authentication
- [x] Multi-role support (admin, developer, architect, engineer, ca, auditor)
- [x] Protected routes
- [x] Token refresh mechanism

### Project Management
- [x] Create/Edit/Delete projects
- [x] Store project master data (name, RERA number, promoter details)
- [x] Store location details (address, survey number, taluka, district)
- [x] Store professional details (architect, engineer, CA, auditor)

### Buildings/Wings Management
- [x] Add buildings/towers per project
- [x] Track floors, units, estimated cost per building
- [x] Completion certificate tracking

### Construction Progress (Form-1)
- [x] 16 default construction activities with weightages
- [x] Per-building activity completion tracking
- [x] Quarterly progress entry
- [x] Overall weighted completion calculation

### Project Costs (Form-3 & Form-4)
- [x] Land costs (acquisition, TDR, stamp duty, etc.)
- [x] Development costs (construction, infrastructure, etc.)
- [x] Estimated vs actual cost tracking
- [x] Balance cost calculation

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

## What's Been Implemented (January 2026)

### Backend (FastAPI + MongoDB)
- ✅ Complete REST API for all modules
- ✅ JWT authentication with bcrypt password hashing
- ✅ Project CRUD endpoints
- ✅ Building CRUD endpoints
- ✅ Construction progress endpoints with weighted calculation
- ✅ Project cost endpoints with automatic totals
- ✅ Building cost endpoints
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
- ✅ Buildings management page
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
