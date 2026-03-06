# RERA Compliance Manager - Report Template Architecture

## 1. Template System Overview

The report template architecture supports multi-state RERA compliance with flexible, version-controlled templates.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        REPORT TEMPLATE ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              TEMPLATE REGISTRY                                   │
│                                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐             │
│  │   GOA RERA       │  │  MAHARASHTRA     │  │  KARNATAKA       │             │
│  │   Templates      │  │  RERA Templates  │  │  RERA Templates  │             │
│  │                  │  │                  │  │                  │             │
│  │ • Form 1 v2024.1 │  │ • Form 1 v2024.1 │  │ • (Future)       │             │
│  │ • Form 2 v2024.1 │  │ • Form 2 v2024.1 │  │                  │             │
│  │ • Form 3 v2024.1 │  │ • Form 3 v2024.1 │  │                  │             │
│  │ • Form 4 v2024.1 │  │ • Form 4 v2024.1 │  │                  │             │
│  │ • Form 5 v2024.1 │  │ • Form 5 v2024.1 │  │                  │             │
│  │ • Form 6 v2024.1 │  │ • Form 6 v2024.1 │  │                  │             │
│  │ • Annexure-A     │  │ • Annexure-A     │  │                  │             │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘             │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                             TEMPLATE ENGINE                                      │
│                                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐             │
│  │  HTML/Jinja2     │  │  DOCX Template   │  │  XLSX Template   │             │
│  │  (PDF Render)    │  │  (Word Export)   │  │  (Excel Export)  │             │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘             │
│           │                     │                     │                         │
│           ▼                     ▼                     ▼                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐             │
│  │   WeasyPrint     │  │   python-docx    │  │    openpyxl      │             │
│  │   PDF Generator  │  │   Word Generator │  │  Excel Generator │             │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘             │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 2. Form Templates Specification

### 2.1 Form 1 - Architect Certificate

**Purpose:** Quarterly certification by project architect on construction progress

**Sections:**
```yaml
form_1:
  name: "Architect's Certificate"
  frequency: "Quarterly"
  responsible_role: "architect"
  
  sections:
    - section_id: "header"
      title: "Authority Header"
      fields:
        - field_id: "state_rera_name"
          type: "static"
          value: "GOA REAL ESTATE REGULATORY AUTHORITY"
        - field_id: "form_title"
          type: "static"
          value: "FORM 1 - ARCHITECT'S CERTIFICATE"
    
    - section_id: "project_info"
      title: "Project Information"
      fields:
        - field_id: "project_name"
          label: "Name of the Project"
          type: "text"
          mapping: "project.name"
          required: true
        - field_id: "rera_number"
          label: "RERA Registration Number"
          type: "text"
          mapping: "project.rera_number"
          required: true
        - field_id: "project_address"
          label: "Project Address"
          type: "textarea"
          mapping: "project.location.address"
          required: true
    
    - section_id: "reporting_period"
      title: "Reporting Period"
      fields:
        - field_id: "quarter"
          label: "Quarter"
          type: "select"
          options: ["Q1", "Q2", "Q3", "Q4"]
          required: true
        - field_id: "year"
          label: "Year"
          type: "number"
          required: true
        - field_id: "period_end_date"
          label: "Period Ending Date"
          type: "date"
          required: true
    
    - section_id: "construction_status"
      title: "Construction Progress"
      fields:
        - field_id: "construction_stage"
          label: "Current Stage of Construction"
          type: "textarea"
          required: true
          help_text: "Describe the current construction activities"
        - field_id: "percentage_completion"
          label: "Percentage of Work Completed"
          type: "number"
          validation:
            min: 0
            max: 100
          required: true
        - field_id: "progress_since_last"
          label: "Progress Since Last Report (%)"
          type: "number"
          validation:
            min: 0
            max: 100
    
    - section_id: "compliance"
      title: "Compliance Declaration"
      fields:
        - field_id: "sanction_compliance"
          label: "Compliance with Sanctioned Plan"
          type: "select"
          options: ["Yes", "No", "Partial"]
          required: true
        - field_id: "deviation_details"
          label: "Details of Deviations (if any)"
          type: "textarea"
          conditional:
            field: "sanction_compliance"
            values: ["No", "Partial"]
    
    - section_id: "architect_details"
      title: "Architect Information"
      fields:
        - field_id: "architect_name"
          label: "Name of Architect"
          type: "text"
          mapping: "user.profile.first_name + user.profile.last_name"
          required: true
        - field_id: "coa_registration"
          label: "Council of Architecture Registration No."
          type: "text"
          mapping: "user.profile.license_number"
          required: true
        - field_id: "architect_address"
          label: "Office Address"
          type: "textarea"
          mapping: "user.profile.address"
    
    - section_id: "signature"
      title: "Signature"
      fields:
        - field_id: "signature_image"
          label: "Signature"
          type: "signature"
        - field_id: "date_signed"
          label: "Date"
          type: "date"
          required: true
        - field_id: "place"
          label: "Place"
          type: "text"
```

### 2.2 Form 2 - Architect Completion Certificate

**Purpose:** Certificate issued upon project completion

```yaml
form_2:
  name: "Architect's Completion Certificate"
  frequency: "Once (at completion)"
  responsible_role: "architect"
  
  sections:
    - section_id: "project_info"
      # Similar to Form 1
    
    - section_id: "completion_details"
      title: "Completion Details"
      fields:
        - field_id: "completion_date"
          label: "Date of Completion"
          type: "date"
          required: true
        - field_id: "occupancy_certificate_number"
          label: "Occupancy Certificate Number"
          type: "text"
        - field_id: "occupancy_certificate_date"
          label: "Date of Occupancy Certificate"
          type: "date"
    
    - section_id: "area_details"
      title: "Area Statement"
      fields:
        - field_id: "total_built_up_area"
          label: "Total Built-up Area (sq.m)"
          type: "number"
          required: true
        - field_id: "sanctioned_area"
          label: "Sanctioned Built-up Area (sq.m)"
          type: "number"
          required: true
        - field_id: "area_variance"
          label: "Variance (%)"
          type: "calculated"
          formula: "((total_built_up_area - sanctioned_area) / sanctioned_area) * 100"
    
    - section_id: "unit_details"
      title: "Unit Summary"
      type: "table"
      columns:
        - header: "Unit Type"
          field: "unit_type"
        - header: "Sanctioned"
          field: "sanctioned_count"
        - header: "Completed"
          field: "completed_count"
        - header: "Carpet Area (sq.m)"
          field: "carpet_area"
    
    - section_id: "declaration"
      title: "Declaration"
      fields:
        - field_id: "completion_declaration"
          label: "Declaration Text"
          type: "static"
          value: "I hereby certify that the construction of the above project has been completed as per the sanctioned plans and RERA regulations."
```

### 2.3 Form 3 - Engineer Certificate

**Purpose:** Structural engineer's certification

```yaml
form_3:
  name: "Engineer's Certificate"
  frequency: "Quarterly"
  responsible_role: "engineer"
  
  sections:
    - section_id: "project_info"
      # Standard project fields
    
    - section_id: "structural_certification"
      title: "Structural Certification"
      fields:
        - field_id: "structural_design_compliance"
          label: "Compliance with Structural Design"
          type: "select"
          options: ["Compliant", "Minor Deviations", "Major Deviations"]
          required: true
        - field_id: "structural_stability"
          label: "Structural Stability Status"
          type: "textarea"
          required: true
        - field_id: "material_quality"
          label: "Material Quality Certification"
          type: "select"
          options: ["Satisfactory", "Requires Attention", "Non-compliant"]
    
    - section_id: "test_results"
      title: "Test Results"
      type: "table"
      columns:
        - header: "Test Type"
          field: "test_type"
        - header: "Date"
          field: "test_date"
        - header: "Result"
          field: "result"
        - header: "Standard"
          field: "standard_met"
    
    - section_id: "engineer_details"
      title: "Engineer Details"
      fields:
        - field_id: "engineer_name"
          label: "Name of Structural Engineer"
          type: "text"
          required: true
        - field_id: "registration_number"
          label: "Registration Number"
          type: "text"
          required: true
```

### 2.4 Form 4 - Chartered Accountant Certificate

**Purpose:** Financial certification for project accounts

```yaml
form_4:
  name: "Chartered Accountant's Certificate"
  frequency: "Quarterly"
  responsible_role: "ca"
  
  sections:
    - section_id: "project_info"
      # Standard project fields
    
    - section_id: "financial_summary"
      title: "Financial Summary"
      fields:
        - field_id: "total_project_cost"
          label: "Total Estimated Project Cost"
          type: "currency"
          mapping: "project.financials.total_project_cost"
          required: true
        - field_id: "amount_received"
          label: "Amount Received from Allottees"
          type: "currency"
          required: true
        - field_id: "amount_utilized"
          label: "Amount Utilized for Project"
          type: "currency"
          required: true
        - field_id: "balance_amount"
          label: "Balance in Designated Account"
          type: "currency"
          required: true
    
    - section_id: "70_percent_rule"
      title: "70% Utilization Rule Compliance"
      fields:
        - field_id: "seventy_percent_amount"
          label: "70% of Amount Received"
          type: "calculated"
          formula: "amount_received * 0.70"
        - field_id: "utilization_compliance"
          label: "Utilization Compliance Status"
          type: "select"
          options: ["Compliant", "Non-compliant"]
          required: true
        - field_id: "non_compliance_reason"
          label: "Reason for Non-compliance (if any)"
          type: "textarea"
          conditional:
            field: "utilization_compliance"
            value: "Non-compliant"
    
    - section_id: "bank_details"
      title: "Designated Account Details"
      fields:
        - field_id: "bank_name"
          label: "Bank Name"
          type: "text"
          required: true
        - field_id: "account_number"
          label: "Account Number"
          type: "text"
          required: true
        - field_id: "ifsc_code"
          label: "IFSC Code"
          type: "text"
          required: true
    
    - section_id: "ca_details"
      title: "CA Details"
      fields:
        - field_id: "ca_name"
          label: "Name of Chartered Accountant"
          type: "text"
          required: true
        - field_id: "membership_number"
          label: "ICAI Membership Number"
          type: "text"
          required: true
        - field_id: "firm_registration"
          label: "Firm Registration Number"
          type: "text"
```

### 2.5 Form 5 - CA Compliance Certificate

**Purpose:** Compliance certificate for fund utilization

```yaml
form_5:
  name: "CA Compliance Certificate"
  frequency: "Quarterly"
  responsible_role: "ca"
  
  sections:
    - section_id: "compliance_checklist"
      title: "Compliance Checklist"
      type: "checklist"
      items:
        - item_id: "separate_account"
          text: "Separate designated account maintained"
        - item_id: "seventy_percent"
          text: "70% of amounts deposited in designated account"
        - item_id: "withdrawal_for_project"
          text: "Withdrawals used only for project purposes"
        - item_id: "gst_compliance"
          text: "GST compliance maintained"
        - item_id: "tds_compliance"
          text: "TDS compliance maintained"
    
    - section_id: "fund_flow"
      title: "Fund Flow Statement"
      type: "table"
      columns:
        - header: "Particulars"
          field: "particulars"
        - header: "Current Quarter"
          field: "current_quarter"
        - header: "Cumulative"
          field: "cumulative"
```

### 2.6 Form 6 - Auditor Certificate

**Purpose:** Annual audit certificate

```yaml
form_6:
  name: "Auditor's Certificate"
  frequency: "Annual"
  responsible_role: "ca"
  
  sections:
    - section_id: "audit_opinion"
      title: "Audit Opinion"
      fields:
        - field_id: "opinion_type"
          label: "Type of Opinion"
          type: "select"
          options: ["Unqualified", "Qualified", "Adverse", "Disclaimer"]
          required: true
        - field_id: "qualification_details"
          label: "Qualification/Modification Details"
          type: "textarea"
          conditional:
            field: "opinion_type"
            values: ["Qualified", "Adverse", "Disclaimer"]
    
    - section_id: "financial_statements"
      title: "Financial Statements Reviewed"
      type: "checklist"
      items:
        - "Balance Sheet"
        - "Income Statement"
        - "Cash Flow Statement"
        - "Designated Account Statement"
```

### 2.7 Annexure-A - Receivable Statement

**Purpose:** Detailed receivables from allottees

```yaml
annexure_a:
  name: "Statement of Receivables"
  frequency: "Quarterly"
  responsible_role: ["developer", "ca"]
  
  sections:
    - section_id: "summary"
      title: "Summary"
      fields:
        - field_id: "total_units"
          label: "Total Units"
          type: "number"
        - field_id: "units_sold"
          label: "Units Sold"
          type: "number"
        - field_id: "total_receivable"
          label: "Total Amount Receivable"
          type: "currency"
        - field_id: "total_received"
          label: "Total Amount Received"
          type: "currency"
        - field_id: "balance_receivable"
          label: "Balance Receivable"
          type: "calculated"
          formula: "total_receivable - total_received"
    
    - section_id: "unit_wise_details"
      title: "Unit-wise Receivables"
      type: "table"
      source: "form_entries"
      columns:
        - header: "Sr. No."
          field: "row_number"
          width: "5%"
        - header: "Unit No."
          field: "unit_number"
          width: "8%"
        - header: "Type"
          field: "flat_type"
          width: "8%"
        - header: "Carpet Area (sq.m)"
          field: "carpet_area_sqm"
          width: "10%"
        - header: "Buyer Name"
          field: "buyer_name"
          width: "15%"
        - header: "Agreement Date"
          field: "agreement_date"
          width: "10%"
        - header: "Agreement Value (₹)"
          field: "agreement_value"
          width: "12%"
        - header: "Amount Received (₹)"
          field: "amount_received"
          width: "12%"
        - header: "Amount Due (₹)"
          field: "amount_due"
          width: "12%"
        - header: "Remarks"
          field: "remarks"
          width: "8%"
      
      footer:
        - column: "agreement_value"
          type: "sum"
        - column: "amount_received"
          type: "sum"
        - column: "amount_due"
          type: "sum"
```

## 3. Template File Structure

```
/app/backend/templates/
├── base/
│   ├── base_template.html        # Common HTML structure
│   ├── base_styles.css           # Common CSS
│   └── header_footer.html        # Header/footer partial
│
├── goa/
│   ├── config.json               # Goa-specific configuration
│   │
│   ├── html/                     # PDF templates (Jinja2)
│   │   ├── form_1.html
│   │   ├── form_2.html
│   │   ├── form_3.html
│   │   ├── form_4.html
│   │   ├── form_5.html
│   │   ├── form_6.html
│   │   └── annexure_a.html
│   │
│   ├── docx/                     # Word templates
│   │   ├── form_1.docx
│   │   ├── form_2.docx
│   │   └── ...
│   │
│   └── xlsx/                     # Excel templates
│       ├── form_4.xlsx
│       ├── form_5.xlsx
│       └── annexure_a.xlsx
│
├── maharashtra/
│   └── ... (similar structure)
│
└── common/
    ├── styles.css                # Shared styles
    ├── fonts/                    # Embedded fonts
    └── images/                   # Logos, watermarks
```

## 4. Template Rendering Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          TEMPLATE RENDERING PIPELINE                             │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Form    │───▶│   Template   │───▶│   Data       │───▶│  Rendered    │
│  Data    │    │   Selector   │    │  Injector    │    │  Template    │
└──────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                      │                    │                    │
                      ▼                    ▼                    ▼
               ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
               │ Load template│    │ Merge data   │    │ Apply format │
               │ by state +   │    │ with template│    │ specific     │
               │ form_type    │    │ placeholders │    │ processing   │
               └──────────────┘    └──────────────┘    └──────────────┘
                                                              │
                                                              ▼
                                          ┌─────────────────────────────────┐
                                          │     OUTPUT GENERATORS           │
                                          │                                 │
                                          │  ┌─────┐  ┌─────┐  ┌─────┐     │
                                          │  │ PDF │  │Word │  │Excel│     │
                                          │  └─────┘  └─────┘  └─────┘     │
                                          └─────────────────────────────────┘
```

## 5. Multi-State Support Design

### State Configuration Schema

```python
# /app/backend/templates/goa/config.json
{
  "state_code": "GOA",
  "state_name": "Goa",
  "authority_name": "Goa Real Estate Regulatory Authority",
  "authority_short": "GOARERA",
  "authority_logo": "goa_rera_logo.png",
  "authority_address": "...",
  "contact_email": "...",
  
  "form_variations": {
    "form_1": {
      "version": "2024.1",
      "effective_from": "2024-01-01",
      "specific_fields": [
        // Goa-specific field overrides
      ],
      "removed_fields": [],
      "additional_sections": []
    }
  },
  
  "validation_rules": {
    // State-specific validation rules
  },
  
  "date_format": "DD/MM/YYYY",
  "currency_format": "INR",
  "number_locale": "en-IN"
}
```

### Adding a New State

1. Create state directory: `/app/backend/templates/{state_code}/`
2. Add `config.json` with state-specific configuration
3. Copy and modify HTML/DOCX/XLSX templates
4. Add state to database templates collection
5. Update frontend state selector
