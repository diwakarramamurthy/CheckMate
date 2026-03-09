# RERA Compliance Manager - Architecture Index

## Document Overview

This directory contains the complete system architecture specification for the RERA Compliance Manager application.

## Documents

| # | Document | Description |
|---|----------|-------------|
| 01 | [System Architecture](./01-system-architecture.md) | High-level system overview, technology stack, core modules, security layers |
| 02 | [Database Schema](./02-database-schema.md) | MongoDB collections, document schemas, indexes, relationships |
| 03 | [Backend API Structure](./03-backend-api-structure.md) | FastAPI routes, endpoints, request/response formats, RBAC |
| 04 | [Frontend Page Structure](./04-frontend-page-structure.md) | React components, pages, routing, wireframes |
| 05 | [Report Template Architecture](./05-report-template-architecture.md) | Form templates (Form 1-6, Annexure-A), field specifications |
| 06 | [Data Flow Diagram](./06-data-flow-diagram.md) | Authentication, project creation, form submission, export flows |
| 07 | [Excel Upload Processing](./07-excel-upload-processing.md) | Excel parsing, column mapping, validation, workflow |
| 08 | [Report Generation Workflow](./08-report-generation-workflow.md) | PDF/Word/Excel generation pipeline, templates |
| 09 | [Validation Rules](./09-validation-rules.md) | Field validation, cross-field rules, business rules, state-specific |
| 10 | [Multi-State Template System](./10-multi-state-template-system.md) | State configuration, template variations, adding new states |

## Quick Reference

### Technology Stack
- **Frontend:** React 18+, TailwindCSS, Shadcn/UI
- **Backend:** FastAPI (Python 3.11+)
- **Database:** MongoDB
- **Authentication:** JWT
- **Report Generation:** WeasyPrint (PDF), python-docx (Word), openpyxl (Excel)

### User Roles
| Role | Access |
|------|--------|
| Admin | Full access to all features |
| Developer | Projects, Annexure-A, Excel upload |
| Architect | Form 1, Form 2 |
| Engineer | Form 3 |
| CA | Form 4, Form 5, Form 6, Annexure-A |

### Form Types
| Form | Name | Frequency | Responsible |
|------|------|-----------|-------------|
| Form 1 | Architect Certificate | Quarterly | Architect |
| Form 2 | Architect Completion Certificate | Once | Architect |
| Form 3 | Engineer Certificate | Quarterly | Engineer |
| Form 4 | CA Certificate | Quarterly | CA |
| Form 5 | CA Compliance Certificate | Quarterly | CA |
| Form 6 | Auditor Certificate | Annual | CA |
| Annexure-A | Receivable Statement | Quarterly | Developer/CA |

### Supported States
| State | Status | RERA Format |
|-------|--------|-------------|
| Goa | Active | PRGO##### |
| Maharashtra | Ready | P########### |
| Karnataka | Planned | - |
| Kerala | Planned | - |

## Design Guidelines

Design specifications are available in `/app/design_guidelines.json`:
- **Primary Color:** #172554 (Deep Royal Blue)
- **Typography:** Manrope (headings), Inter (body)
- **Theme:** Professional Light

## Next Steps

After reviewing this architecture specification:
1. Proceed with implementation approval
2. Set up development environment
3. Begin Phase 1 development (Core Infrastructure)

---
*Architecture version: 1.0.0*  
*Last updated: January 2024*
