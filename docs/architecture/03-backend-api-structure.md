# RERA Compliance Manager - Backend API Structure

## 1. API Overview

RESTful API built with FastAPI, following OpenAPI 3.0 specification.

**Base URL:** `/api`  
**Version:** `v1`  
**Full Prefix:** `/api/v1`

## 2. API Module Structure

```
/app/backend/
├── server.py                 # Main FastAPI application entry
├── config.py                 # Configuration management
├── database.py               # MongoDB connection & utilities
│
├── models/                   # Pydantic models
│   ├── __init__.py
│   ├── user.py
│   ├── organization.py
│   ├── project.py
│   ├── form.py
│   ├── template.py
│   ├── excel_upload.py
│   └── audit_log.py
│
├── routes/                   # API route handlers
│   ├── __init__.py
│   ├── auth.py               # Authentication endpoints
│   ├── users.py              # User management
│   ├── organizations.py      # Organization management
│   ├── projects.py           # Project CRUD
│   ├── forms.py              # Form operations
│   ├── templates.py          # Template management
│   ├── excel.py              # Excel upload/processing
│   ├── exports.py            # Report export endpoints
│   └── reports.py            # Report generation
│
├── services/                 # Business logic
│   ├── __init__.py
│   ├── auth_service.py
│   ├── project_service.py
│   ├── form_service.py
│   ├── excel_parser.py
│   ├── validation_engine.py
│   ├── report_generator.py
│   ├── pdf_generator.py
│   ├── word_generator.py
│   ├── excel_generator.py
│   └── audit_service.py
│
├── middleware/               # Custom middleware
│   ├── __init__.py
│   ├── auth_middleware.py
│   └── audit_middleware.py
│
├── utils/                    # Utility functions
│   ├── __init__.py
│   ├── validators.py
│   ├── helpers.py
│   └── constants.py
│
└── templates/                # Report templates
    ├── goa/
    │   ├── form_1.html
    │   ├── form_2.html
    │   └── ...
    └── maharashtra/
        └── ...
```

## 3. API Endpoints

### 3.1 Authentication Routes (`/api/v1/auth`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/register` | Register new user | No |
| POST | `/login` | User login, returns JWT | No |
| POST | `/logout` | Invalidate token | Yes |
| POST | `/refresh` | Refresh access token | Yes |
| POST | `/forgot-password` | Request password reset | No |
| POST | `/reset-password` | Reset password with token | No |
| GET | `/me` | Get current user profile | Yes |
| PUT | `/me` | Update current user profile | Yes |
| PUT | `/change-password` | Change password | Yes |

```python
# Request/Response Examples

# POST /api/v1/auth/register
Request:
{
  "email": "architect@example.com",
  "password": "SecureP@ss123",
  "first_name": "Rajesh",
  "last_name": "Sharma",
  "role": "architect",
  "license_number": "COA/2020/12345",
  "organization_id": "uuid-string"  # Optional, for joining existing org
}

Response: 201 Created
{
  "user_id": "uuid-string",
  "email": "architect@example.com",
  "role": "architect",
  "message": "Registration successful"
}

# POST /api/v1/auth/login
Request:
{
  "email": "architect@example.com",
  "password": "SecureP@ss123"
}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "user_id": "uuid-string",
    "email": "architect@example.com",
    "role": "architect",
    "profile": {...}
  }
}
```

### 3.2 User Management Routes (`/api/v1/users`)

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/` | List organization users | Yes | Admin |
| GET | `/{user_id}` | Get user details | Yes | Admin/Self |
| POST | `/` | Create user (invite) | Yes | Admin |
| PUT | `/{user_id}` | Update user | Yes | Admin |
| DELETE | `/{user_id}` | Deactivate user | Yes | Admin |
| GET | `/{user_id}/activity` | Get user activity log | Yes | Admin |

### 3.3 Organization Routes (`/api/v1/organizations`)

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/` | Get current organization | Yes | All |
| PUT | `/` | Update organization | Yes | Admin |
| GET | `/stats` | Organization statistics | Yes | Admin |
| PUT | `/settings` | Update org settings | Yes | Admin |
| GET | `/subscription` | Subscription details | Yes | Admin |

### 3.4 Project Routes (`/api/v1/projects`)

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/` | List projects | Yes | All |
| GET | `/{project_id}` | Get project details | Yes | Assigned |
| POST | `/` | Create project | Yes | Admin/Developer |
| PUT | `/{project_id}` | Update project | Yes | Admin/Developer |
| DELETE | `/{project_id}` | Delete project | Yes | Admin |
| GET | `/{project_id}/compliance` | Compliance status | Yes | Assigned |
| GET | `/{project_id}/team` | Project team | Yes | Assigned |
| PUT | `/{project_id}/team` | Update team assignment | Yes | Admin |
| GET | `/{project_id}/forms` | List project forms | Yes | Assigned |
| GET | `/{project_id}/timeline` | Project timeline | Yes | Assigned |

```python
# POST /api/v1/projects
Request:
{
  "name": "Sunset Heights Phase 2",
  "rera_number": "PRGO12345",
  "type": "residential",
  "state": "GOA",
  "location": {
    "address": "Plot 45, Sector 12",
    "city": "Panaji",
    "district": "North Goa",
    "taluka": "Tiswadi",
    "pincode": "403001"
  },
  "details": {
    "total_area_sqm": 5000,
    "total_units": 48,
    "total_floors": 12
  },
  "timeline": {
    "commencement_date": "2023-01-15",
    "completion_date": "2026-12-31"
  }
}

Response: 201 Created
{
  "project_id": "uuid-string",
  "name": "Sunset Heights Phase 2",
  "rera_number": "PRGO12345",
  "state": "GOA",
  "compliance_status": {
    "overall_status": "pending",
    "pending_forms": ["form_1", "form_2", "form_3", "form_4", "form_5", "form_6", "annexure_a"]
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 3.5 Form Routes (`/api/v1/forms`)

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/` | List forms (filtered) | Yes | All |
| GET | `/{form_id}` | Get form details | Yes | Assigned |
| POST | `/` | Create new form | Yes | Role-specific |
| PUT | `/{form_id}` | Update form data | Yes | Role-specific |
| DELETE | `/{form_id}` | Delete draft form | Yes | Role-specific |
| POST | `/{form_id}/validate` | Validate form | Yes | All |
| POST | `/{form_id}/submit` | Submit form | Yes | Role-specific |
| POST | `/{form_id}/approve` | Approve form | Yes | Admin |
| POST | `/{form_id}/reject` | Reject form | Yes | Admin |
| GET | `/{form_id}/history` | Form change history | Yes | Assigned |
| POST | `/{form_id}/sign` | Add signature | Yes | Role-specific |

```python
# Form Type to Role Mapping
FORM_ROLE_PERMISSIONS = {
    "form_1": ["architect"],           # Architect Certificate
    "form_2": ["architect"],           # Architect Completion Certificate
    "form_3": ["engineer"],            # Engineer Certificate
    "form_4": ["ca"],                  # CA Certificate
    "form_5": ["ca"],                  # CA Compliance Certificate
    "form_6": ["ca"],                  # Auditor Certificate
    "annexure_a": ["developer", "ca"]  # Receivable Statement
}

# POST /api/v1/forms
Request:
{
  "project_id": "uuid-string",
  "form_type": "form_1",
  "period": {
    "quarter": 4,
    "year": 2024
  },
  "data": {
    "certificate_number": "ARCH/2024/001",
    "project_name": "Sunset Heights Phase 2",
    "rera_number": "PRGO12345",
    "construction_stage": "Structural work - 7th floor",
    "percentage_completion": 58.5,
    "deviation_remarks": "None",
    ...
  }
}
```

### 3.6 Template Routes (`/api/v1/templates`)

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/` | List templates | Yes | All |
| GET | `/{template_id}` | Get template structure | Yes | All |
| GET | `/states` | List supported states | Yes | All |
| GET | `/states/{state}` | Get state templates | Yes | All |
| POST | `/` | Create template | Yes | Admin |
| PUT | `/{template_id}` | Update template | Yes | Admin |
| POST | `/{template_id}/version` | Create new version | Yes | Admin |
| GET | `/{template_id}/preview` | Preview template | Yes | All |

### 3.7 Excel Upload Routes (`/api/v1/excel`)

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/upload` | Upload Excel file | Yes | Developer/CA |
| GET | `/uploads` | List uploads | Yes | All |
| GET | `/uploads/{upload_id}` | Get upload status | Yes | All |
| POST | `/uploads/{upload_id}/parse` | Parse Excel file | Yes | All |
| GET | `/uploads/{upload_id}/preview` | Preview parsed data | Yes | All |
| POST | `/uploads/{upload_id}/confirm` | Confirm & create forms | Yes | All |
| DELETE | `/uploads/{upload_id}` | Delete upload | Yes | All |
| GET | `/template/{form_type}` | Download Excel template | Yes | All |

```python
# POST /api/v1/excel/upload
# Content-Type: multipart/form-data

Request:
{
  "file": <binary>,
  "project_id": "uuid-string",
  "target_forms": ["form_4", "form_5", "annexure_a"]  # Optional
}

Response: 202 Accepted
{
  "upload_id": "uuid-string",
  "filename": "Q4_2024_Financial_Data.xlsx",
  "status": "uploaded",
  "message": "File uploaded successfully. Call /parse to process."
}

# GET /api/v1/excel/uploads/{upload_id}
Response: 200 OK
{
  "upload_id": "uuid-string",
  "status": "parsed",
  "parse_results": {
    "sheets_found": ["Sales Register", "Collection Report", "Receivables"],
    "sheets_processed": [
      {
        "sheet_name": "Receivables",
        "rows_count": 48,
        "mapped_to_form": "annexure_a",
        "validation_status": "valid"
      }
    ],
    "errors": [],
    "warnings": [
      {
        "sheet": "Sales Register",
        "row": 15,
        "column": "E",
        "message": "Date format non-standard, auto-corrected"
      }
    ]
  }
}
```

### 3.8 Export Routes (`/api/v1/exports`)

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/forms/{form_id}/pdf` | Export form as PDF | Yes | Assigned |
| POST | `/forms/{form_id}/word` | Export form as Word | Yes | Assigned |
| POST | `/forms/{form_id}/excel` | Export form as Excel | Yes | Assigned |
| POST | `/projects/{project_id}/bundle` | Export all forms | Yes | Admin/Developer |
| GET | `/downloads/{export_id}` | Download exported file | Yes | All |
| GET | `/history` | Export history | Yes | All |

```python
# POST /api/v1/exports/forms/{form_id}/pdf
Request:
{
  "include_signature_page": true,
  "include_annexures": true,
  "watermark": "DRAFT"  # Optional
}

Response: 200 OK
{
  "export_id": "uuid-string",
  "format": "pdf",
  "filename": "Form1_Architect_Certificate_Q4_2024.pdf",
  "download_url": "/api/v1/exports/downloads/uuid-string",
  "expires_at": "2024-01-16T10:30:00Z",
  "file_size_bytes": 245678
}
```

### 3.9 Reports Routes (`/api/v1/reports`)

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/dashboard` | Dashboard summary | Yes | All |
| GET | `/compliance-status` | Compliance overview | Yes | All |
| GET | `/projects/{project_id}/summary` | Project summary | Yes | Assigned |
| GET | `/due-dates` | Upcoming due dates | Yes | All |
| GET | `/audit-trail` | Audit trail report | Yes | Admin |

## 4. Authentication & Authorization

### JWT Token Structure

```python
# Access Token Payload
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "architect",
  "org_id": "organization_id",
  "permissions": ["form_1:read", "form_1:write", "form_2:read", "form_2:write"],
  "iat": 1704067200,
  "exp": 1704069000  # 30 minutes
}
```

### Role-Based Access Control (RBAC)

```python
ROLES = {
    "admin": {
        "description": "Organization Administrator",
        "permissions": ["*"]  # All permissions
    },
    "developer": {
        "description": "Real Estate Developer",
        "permissions": [
            "project:*",
            "form:read", "form:create",
            "annexure_a:*",
            "excel:*",
            "export:*"
        ]
    },
    "architect": {
        "description": "Licensed Architect",
        "permissions": [
            "project:read",
            "form_1:*", "form_2:*",
            "export:read"
        ]
    },
    "engineer": {
        "description": "Licensed Engineer",
        "permissions": [
            "project:read",
            "form_3:*",
            "export:read"
        ]
    },
    "ca": {
        "description": "Chartered Accountant",
        "permissions": [
            "project:read",
            "form_4:*", "form_5:*", "form_6:*",
            "annexure_a:*",
            "excel:*",
            "export:read"
        ]
    }
}
```

## 5. Error Handling

### Standard Error Response

```python
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Form validation failed",
    "details": [
      {
        "field": "construction_stage",
        "message": "This field is required"
      },
      {
        "field": "percentage_completion",
        "message": "Value must be between 0 and 100"
      }
    ]
  },
  "request_id": "uuid-string",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted (async processing) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 409 | Conflict (duplicate) |
| 422 | Unprocessable Entity |
| 429 | Rate Limited |
| 500 | Internal Server Error |

## 6. Pagination & Filtering

### Standard Query Parameters

```
GET /api/v1/projects?
  page=1&
  limit=20&
  sort=-created_at&
  status=active&
  state=GOA&
  search=sunset
```

### Response Format

```python
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_items": 156,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```
