# RERA Compliance Manager - Database Schema Design

## 1. Database Overview

MongoDB is used as the primary database with the following collections structure.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         DATABASE SCHEMA OVERVIEW                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                    │
│   │   users     │──────│organizations│──────│  projects   │                    │
│   └─────────────┘      └─────────────┘      └──────┬──────┘                    │
│         │                                          │                            │
│         │                                          │                            │
│         ▼                                          ▼                            │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                    │
│   │ audit_logs  │      │  templates  │──────│   forms     │                    │
│   └─────────────┘      └─────────────┘      └──────┬──────┘                    │
│                                                     │                            │
│                              ┌──────────────────────┼──────────────────────┐    │
│                              │                      │                      │    │
│                              ▼                      ▼                      ▼    │
│                        ┌─────────────┐      ┌─────────────┐      ┌────────────┐│
│                        │excel_uploads│      │form_entries │      │ exports    ││
│                        └─────────────┘      └─────────────┘      └────────────┘│
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 2. Collection Schemas

### 2.1 Users Collection

```javascript
{
  // Collection: users
  // Purpose: Store user accounts and authentication data
  
  "_id": ObjectId,                    // MongoDB auto-generated (excluded from API responses)
  "user_id": UUID,                    // Public identifier
  "email": String,                    // Unique, indexed
  "password_hash": String,            // bcrypt hashed
  "role": String,                     // Enum: "admin", "developer", "ca", "engineer", "architect"
  "profile": {
    "first_name": String,
    "last_name": String,
    "phone": String,
    "designation": String,
    "license_number": String,         // Professional license (CA/Engineer/Architect)
    "firm_name": String,
    "address": String
  },
  "organization_id": UUID,            // Reference to organization
  "permissions": [String],            // Array of permission codes
  "is_active": Boolean,
  "is_verified": Boolean,
  "last_login": ISODate,
  "created_at": ISODate,
  "updated_at": ISODate
}

// Indexes
// - { "email": 1 } - unique
// - { "user_id": 1 } - unique
// - { "organization_id": 1 }
// - { "role": 1 }
```

### 2.2 Organizations Collection

```javascript
{
  // Collection: organizations
  // Purpose: Multi-tenant organization data
  
  "_id": ObjectId,
  "organization_id": UUID,
  "name": String,
  "legal_name": String,
  "rera_registration_number": String,
  "gstin": String,
  "pan": String,
  "address": {
    "line1": String,
    "line2": String,
    "city": String,
    "state": String,                  // Important for state-specific templates
    "pincode": String
  },
  "contact": {
    "email": String,
    "phone": String,
    "website": String
  },
  "subscription": {
    "plan": String,                   // "basic", "professional", "enterprise"
    "valid_until": ISODate,
    "features": [String]
  },
  "settings": {
    "default_state": String,          // Default RERA state
    "logo_url": String,
    "primary_color": String
  },
  "is_active": Boolean,
  "created_at": ISODate,
  "updated_at": ISODate
}

// Indexes
// - { "organization_id": 1 } - unique
// - { "rera_registration_number": 1 }
```

### 2.3 Projects Collection

```javascript
{
  // Collection: projects
  // Purpose: Real estate project data
  
  "_id": ObjectId,
  "project_id": UUID,
  "organization_id": UUID,            // Reference to organization
  "rera_number": String,              // RERA registration number
  "name": String,
  "description": String,
  "type": String,                     // "residential", "commercial", "mixed"
  "state": String,                    // State for RERA compliance (e.g., "GOA")
  "location": {
    "address": String,
    "city": String,
    "district": String,
    "taluka": String,
    "survey_numbers": [String],
    "pincode": String,
    "coordinates": {
      "latitude": Number,
      "longitude": Number
    }
  },
  "details": {
    "total_area_sqm": Number,
    "fsi": Number,
    "total_units": Number,
    "total_floors": Number,
    "parking_slots": Number,
    "amenities": [String]
  },
  "timeline": {
    "commencement_date": ISODate,
    "completion_date": ISODate,
    "rera_validity_date": ISODate
  },
  "financials": {
    "total_project_cost": Number,
    "land_cost": Number,
    "construction_cost": Number,
    "amount_collected": Number,
    "amount_utilized": Number
  },
  "team": {
    "promoter_id": UUID,              // Reference to users
    "architect_id": UUID,
    "engineer_id": UUID,
    "ca_id": UUID
  },
  "compliance_status": {
    "overall_status": String,         // "compliant", "pending", "overdue"
    "last_submission_date": ISODate,
    "next_due_date": ISODate,
    "pending_forms": [String]
  },
  "is_active": Boolean,
  "created_by": UUID,
  "created_at": ISODate,
  "updated_at": ISODate
}

// Indexes
// - { "project_id": 1 } - unique
// - { "organization_id": 1 }
// - { "rera_number": 1 }
// - { "state": 1 }
// - { "compliance_status.overall_status": 1 }
```

### 2.4 Templates Collection

```javascript
{
  // Collection: templates
  // Purpose: Store state-wise RERA form templates
  
  "_id": ObjectId,
  "template_id": UUID,
  "state": String,                    // "GOA", "MAHARASHTRA", "KARNATAKA", etc.
  "form_type": String,                // "form_1", "form_2", ..., "form_6", "annexure_a"
  "form_name": String,                // "Architect Certificate"
  "version": String,                  // "2024.1"
  "is_active": Boolean,
  "is_latest": Boolean,
  "structure": {
    "sections": [
      {
        "section_id": String,
        "title": String,
        "order": Number,
        "fields": [
          {
            "field_id": String,
            "label": String,
            "type": String,           // "text", "number", "date", "select", "textarea", "table"
            "required": Boolean,
            "validation_rules": {
              "min": Number,
              "max": Number,
              "pattern": String,
              "custom_validator": String
            },
            "options": [String],      // For select type
            "default_value": Any,
            "placeholder": String,
            "help_text": String,
            "mapping": {
              "excel_column": String, // Maps to Excel column
              "db_path": String       // Maps to project/form data path
            }
          }
        ]
      }
    ],
    "tables": [
      {
        "table_id": String,
        "title": String,
        "columns": [
          {
            "column_id": String,
            "header": String,
            "type": String,
            "width": String,
            "formula": String         // For calculated columns
          }
        ],
        "row_source": String          // Data source for rows
      }
    ]
  },
  "export_config": {
    "pdf_template": String,           // HTML template name
    "word_template": String,          // DOCX template path
    "excel_template": String,         // XLSX template path
    "page_size": String,              // "A4", "Legal"
    "orientation": String,            // "portrait", "landscape"
    "margins": {
      "top": Number,
      "bottom": Number,
      "left": Number,
      "right": Number
    }
  },
  "validation_rules": {
    "cross_field_rules": [
      {
        "rule_id": String,
        "description": String,
        "expression": String,         // JavaScript-like expression
        "error_message": String
      }
    ]
  },
  "created_by": UUID,
  "created_at": ISODate,
  "updated_at": ISODate
}

// Indexes
// - { "template_id": 1 } - unique
// - { "state": 1, "form_type": 1, "is_latest": 1 }
```

### 2.5 Forms Collection

```javascript
{
  // Collection: forms
  // Purpose: Store submitted/draft forms for projects
  
  "_id": ObjectId,
  "form_id": UUID,
  "project_id": UUID,                 // Reference to project
  "organization_id": UUID,
  "template_id": UUID,                // Reference to template used
  "form_type": String,                // "form_1", "form_2", etc.
  "form_name": String,
  "state": String,
  "status": String,                   // "draft", "pending_review", "approved", "submitted", "rejected"
  "period": {
    "quarter": Number,                // 1-4
    "year": Number,                   // 2024
    "start_date": ISODate,
    "end_date": ISODate
  },
  "data": {
    // Dynamic structure based on template
    // Contains all form field values
  },
  "validation_results": {
    "is_valid": Boolean,
    "errors": [
      {
        "field_id": String,
        "message": String,
        "severity": String            // "error", "warning"
      }
    ],
    "validated_at": ISODate
  },
  "signatures": [
    {
      "role": String,                 // "architect", "engineer", "ca"
      "user_id": UUID,
      "name": String,
      "license_number": String,
      "signed_at": ISODate,
      "signature_data": String        // Base64 or reference
    }
  ],
  "exports": [
    {
      "export_id": UUID,
      "format": String,               // "pdf", "excel", "word"
      "file_url": String,
      "generated_at": ISODate,
      "generated_by": UUID
    }
  ],
  "workflow": {
    "current_step": String,
    "history": [
      {
        "step": String,
        "action": String,
        "user_id": UUID,
        "timestamp": ISODate,
        "comments": String
      }
    ]
  },
  "source_excel_id": UUID,            // Reference to uploaded Excel
  "created_by": UUID,
  "updated_by": UUID,
  "created_at": ISODate,
  "updated_at": ISODate,
  "submitted_at": ISODate
}

// Indexes
// - { "form_id": 1 } - unique
// - { "project_id": 1, "form_type": 1 }
// - { "organization_id": 1 }
// - { "status": 1 }
// - { "period.year": 1, "period.quarter": 1 }
```

### 2.6 Excel Uploads Collection

```javascript
{
  // Collection: excel_uploads
  // Purpose: Track uploaded Excel files and parsing results
  
  "_id": ObjectId,
  "upload_id": UUID,
  "project_id": UUID,
  "organization_id": UUID,
  "original_filename": String,
  "stored_filename": String,
  "file_path": String,
  "file_size": Number,
  "mime_type": String,
  "upload_status": String,            // "uploaded", "parsing", "parsed", "error"
  "parse_results": {
    "sheets_found": [String],
    "sheets_processed": [
      {
        "sheet_name": String,
        "rows_count": Number,
        "columns_count": Number,
        "mapped_to_form": String,
        "validation_status": String
      }
    ],
    "errors": [
      {
        "sheet": String,
        "row": Number,
        "column": String,
        "message": String,
        "severity": String
      }
    ],
    "warnings": [
      {
        "sheet": String,
        "row": Number,
        "column": String,
        "message": String
      }
    ]
  },
  "extracted_data": {
    // Structured data extracted from Excel
    // Organized by form type
  },
  "forms_generated": [UUID],          // References to forms created from this upload
  "uploaded_by": UUID,
  "parsed_at": ISODate,
  "created_at": ISODate
}

// Indexes
// - { "upload_id": 1 } - unique
// - { "project_id": 1 }
// - { "upload_status": 1 }
```

### 2.7 Audit Logs Collection

```javascript
{
  // Collection: audit_logs
  // Purpose: Complete audit trail for compliance
  
  "_id": ObjectId,
  "log_id": UUID,
  "organization_id": UUID,
  "user_id": UUID,
  "action": String,                   // "create", "update", "delete", "export", "submit", "login"
  "resource_type": String,            // "project", "form", "user", "template"
  "resource_id": UUID,
  "resource_name": String,
  "details": {
    "changes": {
      "before": Object,
      "after": Object
    },
    "metadata": Object
  },
  "ip_address": String,
  "user_agent": String,
  "session_id": String,
  "timestamp": ISODate
}

// Indexes
// - { "log_id": 1 } - unique
// - { "organization_id": 1, "timestamp": -1 }
// - { "user_id": 1, "timestamp": -1 }
// - { "resource_type": 1, "resource_id": 1 }
// - { "action": 1 }
// TTL index for log retention: { "timestamp": 1 }, expireAfterSeconds: 31536000 (1 year)
```

### 2.8 Form Entries Collection (Detailed Data)

```javascript
{
  // Collection: form_entries
  // Purpose: Store detailed line-item data for forms (especially Annexure-A)
  
  "_id": ObjectId,
  "entry_id": UUID,
  "form_id": UUID,                    // Reference to parent form
  "project_id": UUID,
  "entry_type": String,               // "unit_sale", "payment", "receivable", "expense"
  "data": {
    // For Annexure-A Receivable entries
    "unit_number": String,
    "flat_type": String,
    "carpet_area_sqm": Number,
    "buyer_name": String,
    "agreement_date": ISODate,
    "agreement_value": Number,
    "amount_received": Number,
    "amount_due": Number,
    "payment_schedule": [
      {
        "milestone": String,
        "due_date": ISODate,
        "amount": Number,
        "received": Number,
        "status": String
      }
    ]
  },
  "row_number": Number,               // For ordering
  "source": String,                   // "excel_import", "manual_entry"
  "created_at": ISODate,
  "updated_at": ISODate
}

// Indexes
// - { "entry_id": 1 } - unique
// - { "form_id": 1, "row_number": 1 }
// - { "project_id": 1, "entry_type": 1 }
```

## 3. Data Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ENTITY RELATIONSHIP DIAGRAM                          │
└─────────────────────────────────────────────────────────────────────────────┘

organizations ─────────────────┬─────────────────────────────────┐
      │                        │                                 │
      │ 1:N                    │ 1:N                             │ 1:N
      ▼                        ▼                                 ▼
   users                   projects                          templates
      │                        │                                 │
      │                        │ 1:N                             │
      │                        ▼                                 │
      │                     forms ◄──────────────────────────────┘
      │                        │                              N:1
      │                        │ 1:N
      │                        ├─────────────┬───────────────┐
      │                        ▼             ▼               ▼
      │                 form_entries   excel_uploads    exports
      │
      │ 1:N
      ▼
  audit_logs
```

## 4. Index Strategy

### Primary Indexes
- All `*_id` fields (UUID) - unique indexes
- `email` in users - unique index

### Query Optimization Indexes
- Compound indexes for common queries
- Partial indexes for status-based queries
- Text indexes for search functionality

### Performance Considerations
- Avoid querying by `_id` in API responses
- Use projection to exclude `_id` from results
- Index fields used in sorting and filtering
