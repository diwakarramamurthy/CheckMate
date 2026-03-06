# RERA Compliance Manager - Database Schema

## MongoDB Collections Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DATABASE: rera_compliance                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────────┐                  │
│   │   users     │     │  projects   │────▶│    buildings    │                  │
│   └─────────────┘     └──────┬──────┘     └────────┬────────┘                  │
│                              │                     │                            │
│         ┌────────────────────┼─────────────────────┤                            │
│         │                    │                     │                            │
│         ▼                    ▼                     ▼                            │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────────┐                  │
│   │project_costs│     │ unit_sales  │     │construction_prog│                  │
│   └─────────────┘     └─────────────┘     └─────────────────┘                  │
│                                                                                  │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────────┐                  │
│   │building_cost│     │quarterly_rep│     │report_templates │                  │
│   └─────────────┘     └─────────────┘     └─────────────────┘                  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Users Collection

**Purpose:** Store user accounts with role-based access control

```javascript
{
  "_id": ObjectId,                    // MongoDB internal (excluded from API)
  "user_id": "uuid-string",           // Public identifier (indexed, unique)
  "email": "user@example.com",        // Unique, indexed
  "password_hash": "bcrypt-hash",     // bcrypt hashed password
  "name": "John Doe",                 // Full name
  "role": "developer",                // Enum: admin, developer, architect, 
                                      //       engineer, ca, auditor
  "phone": "+91-9876543210",          // Optional
  "license_number": "COA/2020/12345", // Professional license (optional)
  "firm_name": "ABC & Associates",    // Firm name (optional)
  "is_active": true,                  // Account status
  "created_at": "2024-01-15T10:30:00Z"
}

// Indexes
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "user_id": 1 }, { unique: true })
```

---

## 2. Projects Collection

**Purpose:** Store RERA registered project master data

```javascript
{
  "_id": ObjectId,
  "project_id": "uuid-string",        // Public identifier (indexed, unique)
  "project_name": "Sunrise Heights Phase 1",
  "state": "GOA",                     // State code for templates
  "rera_number": "PRGO12345",         // RERA registration number
  
  // Promoter Details
  "promoter_name": "ABC Developers Pvt Ltd",
  "promoter_address": "123 Main Street, Panaji, Goa",
  
  // Project Location
  "project_address": "Plot 45, Sector 12, Porvorim",
  "survey_number": "45/1/A",
  "plot_number": "45",
  "village": "Porvorim",
  "taluka": "Bardez",
  "district": "North Goa",
  "pin_code": "403521",
  
  // Project Details
  "plot_area": 5000.00,               // In sq.m
  "total_built_up_area": 12000.00,    // In sq.m
  "project_start_date": "2023-01-15",
  "expected_completion_date": "2026-12-31",
  
  // Professional Details
  "architect_name": "Ar. Rajesh Sharma",
  "architect_license": "COA/2020/12345",
  "engineer_name": "Er. Suresh Kumar",
  "engineer_license": "IEI/2019/56789",
  "ca_name": "CA Priya Nair",
  "ca_firm_name": "Nair & Associates",
  "auditor_name": "CA Amit Verma",
  "auditor_firm_name": "Verma Audit Services",
  
  // Metadata
  "created_by": "user-uuid",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:45:00Z"
}

// Indexes
db.projects.createIndex({ "project_id": 1 }, { unique: true })
db.projects.createIndex({ "rera_number": 1 })
db.projects.createIndex({ "state": 1 })
```

---

## 3. Buildings Collection

**Purpose:** Store building/wing/tower data for each project

```javascript
{
  "_id": ObjectId,
  "building_id": "uuid-string",       // Public identifier (indexed, unique)
  "project_id": "uuid-string",        // Foreign key to projects
  "building_name": "Tower A",         // e.g., Tower A, Wing E-01
  "floors": 12,                       // Number of floors
  "units": 48,                        // Total units in building
  "estimated_cost": 50000000.00,      // Estimated construction cost
  
  // Completion Details (for Form-2)
  "completion_cert_number": "CC/2025/123",
  "completion_cert_date": "2025-06-30",
  "occupancy_cert_number": "OC/2025/456",
  "occupancy_cert_date": "2025-07-15",
  "planning_authority": "TCP Goa",
  "structural_consultant": "Er. Structural Eng",
  "mep_consultant": "MEP Consultants Pvt Ltd",
  "site_supervisor": "Mr. Site Manager",
  
  "created_at": "2024-01-15T10:30:00Z"
}

// Indexes
db.buildings.createIndex({ "building_id": 1 }, { unique: true })
db.buildings.createIndex({ "project_id": 1 })
```

---

## 4. Construction Progress Collection

**Purpose:** Store quarterly construction progress for Form-1

```javascript
{
  "_id": ObjectId,
  "progress_id": "uuid-string",       // Public identifier
  "project_id": "uuid-string",        // Foreign key to projects
  "building_id": "uuid-string",       // Foreign key to buildings
  "quarter": "Q4",                    // Q1, Q2, Q3, Q4
  "year": 2024,
  
  // Activity-wise progress (16 default activities)
  "activities": [
    {
      "activity_name": "Excavation",
      "weightage": 5.0,               // Percentage weight
      "completion_percentage": 100.0  // 0-100%
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
    {
      "activity_name": "Stilt Floor",
      "weightage": 5.0,
      "completion_percentage": 75.0
    },
    {
      "activity_name": "Superstructure Slabs",
      "weightage": 20.0,
      "completion_percentage": 60.0
    },
    {
      "activity_name": "Internal Walls & Plaster",
      "weightage": 10.0,
      "completion_percentage": 40.0
    },
    {
      "activity_name": "Doors & Windows",
      "weightage": 7.0,
      "completion_percentage": 30.0
    },
    {
      "activity_name": "Sanitary Fittings",
      "weightage": 5.0,
      "completion_percentage": 20.0
    },
    {
      "activity_name": "Electrical Fittings",
      "weightage": 5.0,
      "completion_percentage": 15.0
    },
    {
      "activity_name": "Staircases and Lift Wells",
      "weightage": 5.0,
      "completion_percentage": 50.0
    },
    {
      "activity_name": "Water Tanks",
      "weightage": 3.0,
      "completion_percentage": 0.0
    },
    {
      "activity_name": "External Plumbing and Plaster",
      "weightage": 7.0,
      "completion_percentage": 10.0
    },
    {
      "activity_name": "Terrace Waterproofing",
      "weightage": 3.0,
      "completion_percentage": 0.0
    },
    {
      "activity_name": "Fire Fighting Systems",
      "weightage": 5.0,
      "completion_percentage": 5.0
    },
    {
      "activity_name": "Common Area Finishing",
      "weightage": 4.0,
      "completion_percentage": 0.0
    },
    {
      "activity_name": "Compound Wall and Final Works",
      "weightage": 3.0,
      "completion_percentage": 0.0
    }
  ],
  
  // Calculated overall completion (weighted average)
  "overall_completion": 45.65,        // Sum of (weightage × completion / 100)
  
  "created_at": "2024-12-31T10:30:00Z"
}

// Indexes
db.construction_progress.createIndex({ "progress_id": 1 }, { unique: true })
db.construction_progress.createIndex({ "project_id": 1, "quarter": 1, "year": 1 })
db.construction_progress.createIndex({ "building_id": 1, "quarter": 1, "year": 1 })
```

---

## 5. Project Costs Collection

**Purpose:** Store quarterly project cost data for Form-3 and Form-4

```javascript
{
  "_id": ObjectId,
  "cost_id": "uuid-string",           // Public identifier
  "project_id": "uuid-string",        // Foreign key to projects
  "quarter": "Q4",
  "year": 2024,
  
  // Estimated Costs
  "estimated_land_cost": 100000000.00,
  "estimated_development_cost": 150000000.00,
  
  // Actual Land Costs
  "land_acquisition_cost": 80000000.00,
  "development_rights_premium": 5000000.00,
  "tdr_cost": 0.00,
  "stamp_duty": 4800000.00,
  "government_charges": 2000000.00,
  "encumbrance_removal": 500000.00,
  
  // Actual Development Costs
  "construction_cost": 75000000.00,
  "infrastructure_cost": 10000000.00,
  "equipment_cost": 5000000.00,
  "taxes_statutory": 8000000.00,
  "finance_cost": 12000000.00,
  
  // Calculated Totals (computed on save)
  "total_land_cost": 92300000.00,     // Sum of land costs
  "total_development_cost": 110000000.00, // Sum of dev costs
  "total_estimated_cost": 250000000.00,   // est_land + est_dev
  "total_cost_incurred": 202300000.00,    // total_land + total_dev
  "balance_cost": 47700000.00,            // estimated - incurred
  
  "created_at": "2024-12-31T10:30:00Z"
}

// Indexes
db.project_costs.createIndex({ "cost_id": 1 }, { unique: true })
db.project_costs.createIndex({ "project_id": 1, "quarter": 1, "year": 1 })
```

---

## 6. Building Costs Collection

**Purpose:** Store per-building cost data for Form-3

```javascript
{
  "_id": ObjectId,
  "building_cost_id": "uuid-string",
  "project_id": "uuid-string",
  "building_id": "uuid-string",
  "quarter": "Q4",
  "year": 2024,
  
  "estimated_cost": 50000000.00,
  "cost_incurred": 30000000.00,
  
  // Calculated fields
  "completion_percentage": 60.00,     // (incurred / estimated) × 100
  "balance_cost": 20000000.00,        // estimated - incurred
  
  "created_at": "2024-12-31T10:30:00Z"
}

// Indexes
db.building_costs.createIndex({ "building_cost_id": 1 }, { unique: true })
db.building_costs.createIndex({ "project_id": 1, "quarter": 1, "year": 1 })
```

---

## 7. Unit Sales Collection

**Purpose:** Store unit-wise sales data for Annexure-A

```javascript
{
  "_id": ObjectId,
  "sale_id": "uuid-string",           // Public identifier (indexed, unique)
  "project_id": "uuid-string",        // Foreign key to projects
  "building_id": "uuid-string",       // Foreign key to buildings
  "building_name": "Tower A",         // Denormalized for reports
  
  "unit_number": "A-101",             // Flat/Unit number
  "carpet_area": 850.00,              // In sq.ft
  "buyer_name": "John Doe",           // Customer name
  "agreement_date": "2024-03-15",     // Date of agreement
  
  "sale_value": 7500000.00,           // Total agreement value
  "amount_received": 5000000.00,      // Amount collected
  "balance_receivable": 2500000.00,   // Calculated: sale - received
  
  "created_at": "2024-03-15T10:30:00Z"
}

// Indexes
db.unit_sales.createIndex({ "sale_id": 1 }, { unique: true })
db.unit_sales.createIndex({ "project_id": 1 })
db.unit_sales.createIndex({ "building_id": 1 })
db.unit_sales.createIndex({ "unit_number": 1, "project_id": 1 })
```

---

## 8. Quarterly Reports Collection

**Purpose:** Track quarterly report submissions

```javascript
{
  "_id": ObjectId,
  "report_id": "uuid-string",
  "project_id": "uuid-string",
  "quarter": "Q4",
  "year": 2024,
  "report_date": "2024-12-31",
  "status": "draft",                  // draft, submitted, approved
  "created_by": "user-uuid",
  "created_at": "2024-12-31T10:30:00Z"
}

// Indexes
db.quarterly_reports.createIndex({ "report_id": 1 }, { unique: true })
db.quarterly_reports.createIndex({ "project_id": 1, "quarter": 1, "year": 1 })
```

---

## 9. Report Templates Collection

**Purpose:** Store state-wise HTML templates for report generation

```javascript
{
  "_id": ObjectId,
  "template_id": "uuid-string",       // Public identifier
  "state": "GOA",                     // State code
  "report_name": "Form-1: Architect Certificate",
  "report_type": "form-1",            // form-1 to form-6, annexure-a
  "template_html": "<!DOCTYPE html>...", // Full HTML template with placeholders
  "data_mapping": {                   // Field mappings for placeholders
    "project_name": "project.project_name",
    "rera_number": "project.rera_number"
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}

// Indexes
db.report_templates.createIndex({ "template_id": 1 }, { unique: true })
db.report_templates.createIndex({ "state": 1, "report_type": 1 })
```

---

## Data Relationships Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           ENTITY RELATIONSHIPS                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

users ─────────────────────┐
  │                        │ created_by
  │                        ▼
  │                   ┌─────────────┐
  │                   │  projects   │
  │                   └──────┬──────┘
  │                          │
  │         ┌────────────────┼────────────────┬──────────────────┐
  │         │                │                │                  │
  │         ▼                ▼                ▼                  ▼
  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
  │   │  buildings  │  │project_costs│  │ unit_sales  │  │quarterly_rep│
  │   └──────┬──────┘  └─────────────┘  └─────────────┘  └─────────────┘
  │          │
  │          ├─────────────────────┐
  │          ▼                     ▼
  │   ┌─────────────────┐  ┌─────────────────┐
  │   │construction_prog│  │ building_costs  │
  │   └─────────────────┘  └─────────────────┘
  │
  └───────────────────────────────────────────────────────────────────────────────

LEGEND:
───────▶  One-to-Many relationship
- - - -▶  Many-to-Many relationship (if any)
```

---

## Summary Statistics

| Collection | Est. Documents | Key Indexes |
|------------|----------------|-------------|
| users | 10-100 | email, user_id |
| projects | 10-500 | project_id, rera_number |
| buildings | 50-2000 | building_id, project_id |
| construction_progress | 200-8000 | project_id+quarter+year |
| project_costs | 40-2000 | project_id+quarter+year |
| building_costs | 200-8000 | project_id+quarter+year |
| unit_sales | 1000-50000 | sale_id, project_id |
| quarterly_reports | 40-2000 | project_id+quarter+year |
| report_templates | 50-100 | state+report_type |
