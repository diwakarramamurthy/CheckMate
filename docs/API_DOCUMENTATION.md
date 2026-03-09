# RERA Compliance Manager - Backend API Documentation

## Base URL
```
Production: https://your-domain.com/api
Development: http://localhost:8001/api
```

## Authentication
All endpoints (except `/auth/register` and `/auth/login`) require JWT authentication.

```
Authorization: Bearer <access_token>
```

---

## API Endpoints Overview

| Module | Endpoints | Description |
|--------|-----------|-------------|
| Auth | 3 | Registration, Login, Profile |
| Projects | 5 | CRUD operations |
| Buildings | 5 | CRUD operations |
| Construction Progress | 3 | Progress tracking |
| Project Costs | 3 | Cost management |
| Building Costs | 2 | Per-building costs |
| Unit Sales | 5 | Sales & receivables |
| Import | 2 | Excel import |
| Dashboard | 1 | Aggregated metrics |
| Reports | 4 | Report generation |
| Validation | 1 | Data validation |

---

## 1. Authentication Endpoints

### POST /api/auth/register
Create a new user account.

**Request:**
```json
{
  "email": "architect@example.com",
  "password": "SecureP@ss123",
  "name": "Ar. Rajesh Sharma",
  "role": "architect",
  "phone": "+91-9876543210",
  "license_number": "COA/2020/12345",
  "firm_name": "Sharma Associates"
}
```

**Response:** `201 Created`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "architect@example.com",
    "name": "Ar. Rajesh Sharma",
    "role": "architect",
    "phone": "+91-9876543210",
    "license_number": "COA/2020/12345",
    "firm_name": "Sharma Associates",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Roles:** `admin`, `developer`, `architect`, `engineer`, `ca`, `auditor`

---

### POST /api/auth/login
Authenticate and get access token.

**Request:**
```json
{
  "email": "architect@example.com",
  "password": "SecureP@ss123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "architect@example.com",
    "name": "Ar. Rajesh Sharma",
    "role": "architect",
    ...
  }
}
```

**Error Response:** `401 Unauthorized`
```json
{
  "detail": "Invalid credentials"
}
```

---

### GET /api/auth/me
Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "architect@example.com",
  "name": "Ar. Rajesh Sharma",
  "role": "architect",
  "phone": "+91-9876543210",
  "license_number": "COA/2020/12345",
  "firm_name": "Sharma Associates",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## 2. Projects Endpoints

### POST /api/projects
Create a new project.

**Request:**
```json
{
  "project_name": "Sunrise Heights Phase 1",
  "state": "GOA",
  "rera_number": "PRGO12345",
  "promoter_name": "ABC Developers Pvt Ltd",
  "promoter_address": "123 Main Street, Panaji",
  "project_address": "Plot 45, Porvorim, North Goa",
  "survey_number": "45/1/A",
  "plot_number": "45",
  "village": "Porvorim",
  "taluka": "Bardez",
  "district": "North Goa",
  "pin_code": "403521",
  "plot_area": 5000.00,
  "total_built_up_area": 12000.00,
  "project_start_date": "2023-01-15",
  "expected_completion_date": "2026-12-31",
  "architect_name": "Ar. Rajesh Sharma",
  "architect_license": "COA/2020/12345",
  "engineer_name": "Er. Suresh Kumar",
  "engineer_license": "IEI/2019/56789",
  "ca_name": "CA Priya Nair",
  "ca_firm_name": "Nair & Associates",
  "auditor_name": "CA Amit Verma",
  "auditor_firm_name": "Verma Audit Services"
}
```

**Response:** `201 Created`
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440001",
  "project_name": "Sunrise Heights Phase 1",
  "state": "GOA",
  "rera_number": "PRGO12345",
  ...
  "created_by": "user-uuid",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### GET /api/projects
List all projects.

**Response:** `200 OK`
```json
[
  {
    "project_id": "550e8400-e29b-41d4-a716-446655440001",
    "project_name": "Sunrise Heights Phase 1",
    "state": "GOA",
    "rera_number": "PRGO12345",
    ...
  },
  ...
]
```

---

### GET /api/projects/{project_id}
Get project by ID.

**Response:** `200 OK` - Returns single project object

---

### PUT /api/projects/{project_id}
Update project.

**Request:** Same as POST (all fields)

**Response:** `200 OK` - Returns updated project

---

### DELETE /api/projects/{project_id}
Delete project and all related data.

**Response:** `200 OK`
```json
{
  "message": "Project deleted"
}
```

---

## 3. Buildings Endpoints

### POST /api/buildings
Create a new building/wing.

**Request:**
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440001",
  "building_name": "Tower A",
  "floors": 12,
  "units": 48,
  "estimated_cost": 50000000
}
```

**Response:** `201 Created`
```json
{
  "building_id": "550e8400-e29b-41d4-a716-446655440002",
  "project_id": "550e8400-e29b-41d4-a716-446655440001",
  "building_name": "Tower A",
  "floors": 12,
  "units": 48,
  "estimated_cost": 50000000,
  "completion_cert_number": null,
  "completion_cert_date": null,
  "occupancy_cert_number": null,
  "occupancy_cert_date": null,
  ...
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### GET /api/buildings?project_id={project_id}
List buildings for a project.

**Query Parameters:**
- `project_id` (required): Project UUID

**Response:** `200 OK` - Array of building objects

---

### GET /api/buildings/{building_id}
Get building by ID.

---

### PUT /api/buildings/{building_id}
Update building.

---

### DELETE /api/buildings/{building_id}
Delete building.

---

## 4. Construction Progress Endpoints

### POST /api/construction-progress
Create/update construction progress for a building.

**Request:**
```json
{
  "building_id": "550e8400-e29b-41d4-a716-446655440002",
  "quarter": "Q4",
  "year": 2024,
  "activities": [
    {
      "activity_name": "Excavation",
      "weightage": 5.0,
      "completion_percentage": 100.0
    },
    {
      "activity_name": "Basement / Plinth",
      "weightage": 8.0,
      "completion_percentage": 100.0
    },
    {
      "activity_name": "Podium",
      "weightage": 5.0,
      "completion_percentage": 80.0
    },
    ...
  ],
  "overall_completion": 45.65
}
```

**Response:** `200 OK`
```json
{
  "progress_id": "550e8400-e29b-41d4-a716-446655440003",
  "project_id": "550e8400-e29b-41d4-a716-446655440001",
  "building_id": "550e8400-e29b-41d4-a716-446655440002",
  "quarter": "Q4",
  "year": 2024,
  "activities": [...],
  "overall_completion": 45.65,
  "created_at": "2024-12-31T10:30:00Z"
}
```

**Note:** Uses upsert - updates if record exists for same building/quarter/year.

---

### GET /api/construction-progress
Get construction progress records.

**Query Parameters:**
- `project_id` (required): Project UUID
- `quarter` (optional): Q1, Q2, Q3, Q4
- `year` (optional): Year number

**Response:** `200 OK` - Array of progress records

---

### GET /api/construction-progress/default-activities
Get default activity list with weightages.

**Response:** `200 OK`
```json
[
  {"activity_name": "Excavation", "weightage": 5, "completion_percentage": 0},
  {"activity_name": "Basement / Plinth", "weightage": 8, "completion_percentage": 0},
  {"activity_name": "Podium", "weightage": 5, "completion_percentage": 0},
  {"activity_name": "Stilt Floor", "weightage": 5, "completion_percentage": 0},
  {"activity_name": "Superstructure Slabs", "weightage": 20, "completion_percentage": 0},
  {"activity_name": "Internal Walls & Plaster", "weightage": 10, "completion_percentage": 0},
  {"activity_name": "Doors & Windows", "weightage": 7, "completion_percentage": 0},
  {"activity_name": "Sanitary Fittings", "weightage": 5, "completion_percentage": 0},
  {"activity_name": "Electrical Fittings", "weightage": 5, "completion_percentage": 0},
  {"activity_name": "Staircases and Lift Wells", "weightage": 5, "completion_percentage": 0},
  {"activity_name": "Water Tanks", "weightage": 3, "completion_percentage": 0},
  {"activity_name": "External Plumbing and Plaster", "weightage": 7, "completion_percentage": 0},
  {"activity_name": "Terrace Waterproofing", "weightage": 3, "completion_percentage": 0},
  {"activity_name": "Fire Fighting Systems", "weightage": 5, "completion_percentage": 0},
  {"activity_name": "Common Area Finishing", "weightage": 4, "completion_percentage": 0},
  {"activity_name": "Compound Wall and Final Works", "weightage": 3, "completion_percentage": 0}
]
```

---

## 5. Project Costs Endpoints

### POST /api/project-costs
Create/update project costs.

**Request:**
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440001",
  "quarter": "Q4",
  "year": 2024,
  "estimated_land_cost": 100000000,
  "estimated_development_cost": 150000000,
  "land_acquisition_cost": 80000000,
  "development_rights_premium": 5000000,
  "tdr_cost": 0,
  "stamp_duty": 4800000,
  "government_charges": 2000000,
  "encumbrance_removal": 500000,
  "construction_cost": 75000000,
  "infrastructure_cost": 10000000,
  "equipment_cost": 5000000,
  "taxes_statutory": 8000000,
  "finance_cost": 12000000
}
```

**Response:** `200 OK`
```json
{
  "cost_id": "550e8400-e29b-41d4-a716-446655440004",
  "project_id": "550e8400-e29b-41d4-a716-446655440001",
  "quarter": "Q4",
  "year": 2024,
  ...
  "total_land_cost": 92300000,
  "total_development_cost": 110000000,
  "total_estimated_cost": 250000000,
  "total_cost_incurred": 202300000,
  "balance_cost": 47700000,
  "created_at": "2024-12-31T10:30:00Z"
}
```

---

### GET /api/project-costs
Get project costs.

**Query Parameters:**
- `project_id` (required)
- `quarter` (optional)
- `year` (optional)

---

### GET /api/project-costs/latest/{project_id}
Get latest cost record for project.

---

## 6. Building Costs Endpoints

### POST /api/building-costs
Create/update building costs.

**Request:**
```json
{
  "building_id": "550e8400-e29b-41d4-a716-446655440002",
  "quarter": "Q4",
  "year": 2024,
  "estimated_cost": 50000000,
  "cost_incurred": 30000000
}
```

**Response:** `200 OK`
```json
{
  "building_cost_id": "...",
  "project_id": "...",
  "building_id": "...",
  "quarter": "Q4",
  "year": 2024,
  "estimated_cost": 50000000,
  "cost_incurred": 30000000,
  "completion_percentage": 60.0,
  "balance_cost": 20000000,
  "created_at": "..."
}
```

---

### GET /api/building-costs
Get building costs.

**Query Parameters:**
- `project_id` (required)
- `quarter` (optional)
- `year` (optional)

---

## 7. Unit Sales Endpoints

### POST /api/unit-sales
Create a unit sale record.

**Request:**
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440001",
  "unit_number": "A-101",
  "building_id": "550e8400-e29b-41d4-a716-446655440002",
  "building_name": "Tower A",
  "carpet_area": 850.0,
  "sale_value": 7500000,
  "amount_received": 5000000,
  "buyer_name": "John Doe",
  "agreement_date": "2024-03-15"
}
```

**Response:** `201 Created`
```json
{
  "sale_id": "550e8400-e29b-41d4-a716-446655440005",
  "project_id": "...",
  "unit_number": "A-101",
  "building_id": "...",
  "building_name": "Tower A",
  "carpet_area": 850.0,
  "sale_value": 7500000,
  "amount_received": 5000000,
  "balance_receivable": 2500000,
  "buyer_name": "John Doe",
  "agreement_date": "2024-03-15",
  "created_at": "..."
}
```

---

### GET /api/unit-sales?project_id={project_id}
List all unit sales for a project.

---

### PUT /api/unit-sales/{sale_id}
Update a unit sale.

---

### DELETE /api/unit-sales/{sale_id}
Delete a unit sale.

---

### POST /api/unit-sales/bulk?project_id={project_id}
Bulk create unit sales.

**Request:**
```json
[
  {
    "unit_number": "A-101",
    "building_id": "...",
    "building_name": "Tower A",
    "carpet_area": 850,
    "sale_value": 7500000,
    "amount_received": 5000000
  },
  {
    "unit_number": "A-102",
    ...
  }
]
```

**Response:** `200 OK`
```json
{
  "created": 2,
  "errors": []
}
```

---

## 8. Excel Import Endpoints

### POST /api/import/sales-excel?project_id={project_id}
Import unit sales from Excel file.

**Content-Type:** `multipart/form-data`

**Request:**
- `file`: Excel file (.xlsx, .xls)
- Query param: `project_id`

**Response:** `200 OK`
```json
{
  "created": 45,
  "errors": [
    {"row": 15, "error": "Invalid sale value"},
    {"row": 23, "error": "Missing unit number"}
  ],
  "total_rows": 47
}
```

**Expected Excel Columns:**
- Unit Number / Unit No / Flat No
- Building Name / Building / Wing / Tower
- Carpet Area / Area
- Sale Value / Agreement Value / Total Value
- Amount Received / Received / Collection
- Buyer Name (optional)
- Agreement Date (optional)

---

### GET /api/import/sales-template
Download Excel template for sales import.

**Response:** Excel file download (.xlsx)

---

## 9. Dashboard Endpoint

### GET /api/dashboard/{project_id}
Get aggregated dashboard metrics for a project.

**Response:** `200 OK`
```json
{
  "project_completion_percentage": 45.65,
  "total_estimated_cost": 250000000,
  "cost_incurred": 202300000,
  "balance_cost": 47700000,
  "total_sales_value": 150000000,
  "amount_collected": 95000000,
  "receivables": 55000000,
  "unsold_inventory_value": 75000000,
  "rera_deposit_required": 38500000,
  "total_units": 48,
  "units_sold": 30
}
```

**RERA Deposit Calculation:**
- If `receivables / balance_cost > 1`: Deposit = 70% of receivables
- If `receivables / balance_cost <= 1`: Deposit = 100% of receivables

---

## 10. Report Endpoints

### GET /api/generate-report/{project_id}/{report_type}
Generate a RERA report.

**Path Parameters:**
- `project_id`: Project UUID
- `report_type`: `form-1`, `form-2`, `form-3`, `form-4`, `form-5`, `form-6`, `annexure-a`

**Query Parameters:**
- `quarter` (required): Q1, Q2, Q3, Q4
- `year` (required): Year number

**Response:** `200 OK`
```json
{
  "html": "<!DOCTYPE html>...",  // Rendered HTML template
  "data": {
    "project": {...},
    "buildings": [...],
    "construction_progress": [...],
    "project_cost": {...},
    "building_costs": [...],
    "sales": [...],
    "quarter": "Q4",
    "year": 2024,
    "report_date": "31/12/2024",
    "total_sales_value": 150000000,
    "amount_collected": 95000000,
    "receivables": 55000000,
    "balance_cost": 47700000
  }
}
```

---

### POST /api/report-templates
Create a report template (Admin only).

**Request:**
```json
{
  "state": "GOA",
  "report_name": "Form-1: Architect Certificate",
  "report_type": "form-1",
  "template_html": "<!DOCTYPE html>...",
  "data_mapping": {}
}
```

---

### GET /api/report-templates
List report templates.

**Query Parameters:**
- `state` (optional): Filter by state

---

### GET /api/report-templates/{template_id}
Get a specific template.

---

### PUT /api/report-templates/{template_id}
Update a template (Admin only).

---

## 11. Validation Endpoint

### GET /api/validate/{project_id}
Validate project data for RERA compliance.

**Response:** `200 OK`
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": [
    {
      "type": "missing_field",
      "message": "Missing required field: auditor_name"
    },
    {
      "type": "negative_receivable",
      "message": "2 units have negative receivables (over-collection)"
    }
  ],
  "summary": {
    "buildings": 3,
    "units_sold": 45,
    "total_receivables": 55000000,
    "balance_cost": 47700000
  }
}
```

**Validation Checks:**
- Missing required fields (project_name, rera_number, etc.)
- Duplicate unit numbers
- Negative receivables (over-collection)
- Cost overrun (incurred > estimated)
- Receivable/cost mismatch

---

## 12. Health Check Endpoints

### GET /api/
API info.

**Response:** `200 OK`
```json
{
  "message": "RERA Compliance Manager API",
  "version": "1.0.0"
}
```

---

### GET /api/health
Health check.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid token"
}
```

### 403 Forbidden
```json
{
  "detail": "Admin access required"
}
```

### 404 Not Found
```json
{
  "detail": "Project not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limits
- No rate limiting currently implemented
- Recommended: 100 requests/minute per user

## Pagination
- Currently returns all records
- Recommended: Add `page` and `limit` query parameters for list endpoints
