# RERA Compliance Manager - Report Generation Workflow

## 1. Report Generation Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         REPORT GENERATION WORKFLOW                               │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  TRIGGER                    PROCESS                       OUTPUT            │
│                                                                              │
│  ┌──────────┐             ┌──────────────────┐         ┌──────────────┐    │
│  │  User    │             │                  │         │              │    │
│  │ Request  │────────────▶│  Report Engine   │────────▶│  PDF File    │    │
│  │          │             │                  │         │              │    │
│  └──────────┘             └────────┬─────────┘         └──────────────┘    │
│                                    │                                        │
│  ┌──────────┐             ┌────────▼─────────┐         ┌──────────────┐    │
│  │Scheduled │             │                  │         │              │    │
│  │  Job     │────────────▶│  Template Engine │────────▶│  Word File   │    │
│  │          │             │                  │         │              │    │
│  └──────────┘             └────────┬─────────┘         └──────────────┘    │
│                                    │                                        │
│  ┌──────────┐             ┌────────▼─────────┐         ┌──────────────┐    │
│  │  Batch   │             │                  │         │              │    │
│  │ Export   │────────────▶│  Data Processor  │────────▶│  Excel File  │    │
│  │          │             │                  │         │              │    │
│  └──────────┘             └──────────────────┘         └──────────────┘    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 2. Report Generation Pipeline

### 2.1 Step-by-Step Process

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         GENERATION PIPELINE STEPS                                │
└─────────────────────────────────────────────────────────────────────────────────┘

STEP 1: INITIATE EXPORT REQUEST
───────────────────────────────────────────────────────────────────────────────────
User Action: Click "Export PDF" on Form Detail page
API Call: POST /api/v1/exports/forms/{form_id}/pdf
Request Body: {
  "include_signature_page": true,
  "include_annexures": true,
  "watermark": null  // "DRAFT" for draft forms
}
───────────────────────────────────────────────────────────────────────────────────

                                      │
                                      ▼

STEP 2: VALIDATE REQUEST
───────────────────────────────────────────────────────────────────────────────────
Checks:
  ✓ User has permission to export this form
  ✓ Form exists and belongs to user's organization
  ✓ Form status allows export (draft can export with watermark)
  ✓ Required data fields are populated
───────────────────────────────────────────────────────────────────────────────────

                                      │
                                      ▼

STEP 3: GATHER DATA
───────────────────────────────────────────────────────────────────────────────────
Data Sources:
  - Form document (primary data)
  - Project document (project details)
  - Organization document (company info)
  - User document (signatory details)
  - Template document (structure/config)
  - Form entries (for Annexure-A line items)
───────────────────────────────────────────────────────────────────────────────────

                                      │
                                      ▼

STEP 4: SELECT TEMPLATE
───────────────────────────────────────────────────────────────────────────────────
Template Selection Logic:
  1. Get state from project (e.g., "GOA")
  2. Get form_type from form (e.g., "form_1")
  3. Find latest active template for state + form_type
  4. Load template files (HTML, DOCX, or XLSX based on format)
───────────────────────────────────────────────────────────────────────────────────

                                      │
                                      ▼

STEP 5: PREPARE DATA CONTEXT
───────────────────────────────────────────────────────────────────────────────────
Context Object:
{
  "project": {...},
  "form": {...},
  "organization": {...},
  "signatory": {...},
  "report_date": "2024-12-31",
  "generated_at": "2024-01-15T10:30:00Z",
  "period": { "quarter": "Q4", "year": 2024 },
  "entries": [...],  // For Annexure-A
  "totals": {...},   // Calculated totals
  "config": {...}    // State-specific config
}
───────────────────────────────────────────────────────────────────────────────────

                                      │
                                      ▼

STEP 6: RENDER TEMPLATE
───────────────────────────────────────────────────────────────────────────────────
For PDF:
  1. Load Jinja2 HTML template
  2. Render with data context
  3. Apply CSS styling
  4. Convert HTML to PDF using WeasyPrint

For Word:
  1. Load DOCX template with placeholders
  2. Replace placeholders with data
  3. Handle tables and repeating sections
  4. Save as DOCX

For Excel:
  1. Load XLSX template
  2. Populate cells with data
  3. Apply formulas
  4. Format cells
───────────────────────────────────────────────────────────────────────────────────

                                      │
                                      ▼

STEP 7: POST-PROCESSING
───────────────────────────────────────────────────────────────────────────────────
Actions:
  - Add watermark if draft
  - Add page numbers
  - Add header/footer
  - Compress file if needed
  - Generate file hash for integrity
───────────────────────────────────────────────────────────────────────────────────

                                      │
                                      ▼

STEP 8: STORE & RESPOND
───────────────────────────────────────────────────────────────────────────────────
Storage:
  - Save to: /exports/{org_id}/{project_id}/{form_type}_{date}.pdf
  - Create export record in database
  - Set expiration for download URL

Response:
{
  "export_id": "uuid",
  "format": "pdf",
  "filename": "Form1_Architect_Certificate_Q4_2024.pdf",
  "download_url": "/api/v1/exports/downloads/uuid",
  "expires_at": "2024-01-16T10:30:00Z",
  "file_size_bytes": 245678
}
───────────────────────────────────────────────────────────────────────────────────
```

## 3. PDF Generation Details

### 3.1 HTML Template Structure

```html
<!-- /app/backend/templates/goa/html/form_1.html -->

{% extends "base/base_template.html" %}

{% block title %}Form 1 - Architect's Certificate{% endblock %}

{% block content %}
<div class="form-container">
    <!-- Header Section -->
    <div class="header">
        <div class="authority-logo">
            <img src="{{ config.authority_logo }}" alt="RERA Logo">
        </div>
        <div class="authority-name">
            <h1>{{ config.authority_name }}</h1>
            <p>{{ config.authority_address }}</p>
        </div>
    </div>
    
    <!-- Form Title -->
    <div class="form-title">
        <h2>FORM 1</h2>
        <h3>ARCHITECT'S CERTIFICATE</h3>
        <p class="subtitle">
            (Under Section 11(4)(b) of the Real Estate (Regulation and Development) Act, 2016)
        </p>
    </div>
    
    <!-- Project Details Section -->
    <div class="section">
        <h4>1. PROJECT DETAILS</h4>
        <table class="details-table">
            <tr>
                <td class="label">Name of the Project:</td>
                <td class="value">{{ project.name }}</td>
            </tr>
            <tr>
                <td class="label">RERA Registration Number:</td>
                <td class="value">{{ project.rera_number }}</td>
            </tr>
            <tr>
                <td class="label">Project Address:</td>
                <td class="value">{{ project.location.address }}, {{ project.location.city }}</td>
            </tr>
        </table>
    </div>
    
    <!-- Reporting Period -->
    <div class="section">
        <h4>2. REPORTING PERIOD</h4>
        <table class="details-table">
            <tr>
                <td class="label">Quarter:</td>
                <td class="value">{{ period.quarter }} {{ period.year }}</td>
            </tr>
            <tr>
                <td class="label">Period Ending:</td>
                <td class="value">{{ form.data.period_end_date | format_date }}</td>
            </tr>
        </table>
    </div>
    
    <!-- Construction Status -->
    <div class="section">
        <h4>3. CONSTRUCTION PROGRESS</h4>
        <table class="details-table">
            <tr>
                <td class="label">Current Stage:</td>
                <td class="value">{{ form.data.construction_stage }}</td>
            </tr>
            <tr>
                <td class="label">Percentage Completed:</td>
                <td class="value">{{ form.data.percentage_completion }}%</td>
            </tr>
            {% if form.data.progress_since_last %}
            <tr>
                <td class="label">Progress Since Last Report:</td>
                <td class="value">{{ form.data.progress_since_last }}%</td>
            </tr>
            {% endif %}
        </table>
    </div>
    
    <!-- Compliance Declaration -->
    <div class="section">
        <h4>4. COMPLIANCE DECLARATION</h4>
        <p>
            I, {{ signatory.profile.first_name }} {{ signatory.profile.last_name }}, 
            registered Architect bearing Council of Architecture Registration Number 
            <strong>{{ signatory.profile.license_number }}</strong>, hereby certify that:
        </p>
        <ul>
            <li>The construction is progressing as per the sanctioned plans.</li>
            <li>Compliance with sanctioned plan: <strong>{{ form.data.sanction_compliance }}</strong></li>
            {% if form.data.deviation_details %}
            <li>Deviations noted: {{ form.data.deviation_details }}</li>
            {% endif %}
        </ul>
    </div>
    
    <!-- Signature Section -->
    <div class="signature-section">
        <div class="signature-block">
            <div class="signature-line">
                {% if form.signatures %}
                <img src="{{ form.signatures[0].signature_data }}" alt="Signature">
                {% else %}
                ____________________
                {% endif %}
            </div>
            <p class="signatory-name">{{ signatory.profile.first_name }} {{ signatory.profile.last_name }}</p>
            <p class="signatory-details">
                Architect<br>
                COA Reg. No.: {{ signatory.profile.license_number }}<br>
                {{ signatory.profile.firm_name }}
            </p>
        </div>
        
        <div class="date-place">
            <p>Date: {{ form.data.date_signed | format_date }}</p>
            <p>Place: {{ form.data.place }}</p>
        </div>
    </div>
</div>
{% endblock %}
```

### 3.2 PDF Generator Service

```python
# /app/backend/services/pdf_generator.py

from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
import os

class PDFGenerator:
    """
    Generate PDF reports using WeasyPrint
    """
    
    def __init__(self):
        self.template_dir = "/app/backend/templates"
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir)
        )
        # Register custom filters
        self.env.filters['format_date'] = self.format_date
        self.env.filters['format_currency'] = self.format_currency
        self.env.filters['format_number'] = self.format_number
    
    async def generate(
        self, 
        form_type: str, 
        state: str, 
        data_context: dict,
        options: dict
    ) -> bytes:
        """
        Generate PDF from template and data
        """
        # 1. Load template
        template_path = f"{state.lower()}/html/{form_type}.html"
        template = self.env.get_template(template_path)
        
        # 2. Load CSS
        css_path = os.path.join(self.template_dir, "common", "styles.css")
        state_css_path = os.path.join(self.template_dir, state.lower(), "styles.css")
        
        stylesheets = [CSS(filename=css_path)]
        if os.path.exists(state_css_path):
            stylesheets.append(CSS(filename=state_css_path))
        
        # 3. Render HTML
        html_content = template.render(**data_context)
        
        # 4. Add watermark if draft
        if options.get('watermark'):
            html_content = self._add_watermark(html_content, options['watermark'])
        
        # 5. Convert to PDF
        html = HTML(string=html_content, base_url=self.template_dir)
        pdf_bytes = html.write_pdf(stylesheets=stylesheets)
        
        return pdf_bytes
    
    def _add_watermark(self, html: str, watermark_text: str) -> str:
        """
        Add watermark to HTML
        """
        watermark_css = f"""
        <style>
        .watermark {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 120px;
            color: rgba(200, 200, 200, 0.3);
            z-index: -1;
            pointer-events: none;
        }}
        </style>
        <div class="watermark">{watermark_text}</div>
        """
        return html.replace('</body>', f'{watermark_css}</body>')
    
    @staticmethod
    def format_date(value, format_str="%d %B %Y"):
        """Format date for display"""
        if isinstance(value, str):
            from dateutil.parser import parse
            value = parse(value)
        return value.strftime(format_str)
    
    @staticmethod
    def format_currency(value, symbol="₹"):
        """Format currency with Indian numbering"""
        if value is None:
            return f"{symbol} 0"
        # Indian number formatting
        s = f"{value:,.2f}"
        return f"{symbol} {s}"
    
    @staticmethod
    def format_number(value, decimals=2):
        """Format number with commas"""
        if value is None:
            return "0"
        return f"{value:,.{decimals}f}"
```

## 4. Word Document Generation

```python
# /app/backend/services/word_generator.py

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

class WordGenerator:
    """
    Generate Word documents using python-docx
    """
    
    async def generate(
        self, 
        form_type: str, 
        state: str, 
        data_context: dict
    ) -> bytes:
        """
        Generate Word document from template
        """
        # Load template
        template_path = f"/app/backend/templates/{state.lower()}/docx/{form_type}.docx"
        doc = Document(template_path)
        
        # Replace placeholders
        self._replace_placeholders(doc, data_context)
        
        # Handle tables
        if 'entries' in data_context:
            self._populate_tables(doc, data_context['entries'])
        
        # Save to bytes
        from io import BytesIO
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return buffer.getvalue()
    
    def _replace_placeholders(self, doc: Document, context: dict):
        """
        Replace {{placeholder}} with actual values
        """
        for paragraph in doc.paragraphs:
            for key, value in self._flatten_dict(context).items():
                placeholder = f"{{{{{key}}}}}"
                if placeholder in paragraph.text:
                    paragraph.text = paragraph.text.replace(
                        placeholder, 
                        str(value) if value else ""
                    )
        
        # Also check tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for key, value in self._flatten_dict(context).items():
                        placeholder = f"{{{{{key}}}}}"
                        if placeholder in cell.text:
                            cell.text = cell.text.replace(
                                placeholder,
                                str(value) if value else ""
                            )
    
    def _flatten_dict(self, d: dict, parent_key: str = '', sep: str = '.') -> dict:
        """
        Flatten nested dict: {'a': {'b': 1}} -> {'a.b': 1}
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
```

## 5. Excel Export Generation

```python
# /app/backend/services/excel_generator.py

from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, Border, PatternFill

class ExcelGenerator:
    """
    Generate Excel reports using openpyxl
    """
    
    async def generate(
        self, 
        form_type: str, 
        state: str, 
        data_context: dict
    ) -> bytes:
        """
        Generate Excel file from template
        """
        # Load template
        template_path = f"/app/backend/templates/{state.lower()}/xlsx/{form_type}.xlsx"
        wb = load_workbook(template_path)
        ws = wb.active
        
        # Populate header data
        self._populate_header(ws, data_context)
        
        # Populate data rows (for Annexure-A)
        if 'entries' in data_context:
            self._populate_data_rows(ws, data_context['entries'])
        
        # Update formulas
        self._update_formulas(ws)
        
        # Save to bytes
        from io import BytesIO
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        return buffer.getvalue()
    
    def _populate_data_rows(self, ws, entries: list):
        """
        Populate data rows for Annexure-A
        """
        start_row = 5  # Data starts from row 5
        
        for idx, entry in enumerate(entries):
            row = start_row + idx
            ws.cell(row=row, column=1, value=idx + 1)  # Sr. No.
            ws.cell(row=row, column=2, value=entry.get('unit_number'))
            ws.cell(row=row, column=3, value=entry.get('flat_type'))
            ws.cell(row=row, column=4, value=entry.get('carpet_area_sqm'))
            ws.cell(row=row, column=5, value=entry.get('buyer_name'))
            ws.cell(row=row, column=6, value=entry.get('agreement_date'))
            ws.cell(row=row, column=7, value=entry.get('agreement_value'))
            ws.cell(row=row, column=8, value=entry.get('amount_received'))
            ws.cell(row=row, column=9, value=entry.get('amount_due'))
            
            # Apply formatting
            for col in range(1, 10):
                cell = ws.cell(row=row, column=col)
                cell.alignment = Alignment(horizontal='center')
                if col in [7, 8, 9]:  # Currency columns
                    cell.number_format = '₹ #,##0.00'
```

## 6. Batch Export Workflow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         BATCH EXPORT WORKFLOW                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

POST /api/v1/exports/projects/{project_id}/bundle
Request: {
  "forms": ["form_1", "form_2", "form_3", "form_4", "form_5", "form_6", "annexure_a"],
  "format": "pdf",
  "period": { "quarter": 4, "year": 2024 },
  "package_type": "zip"  // or "merged_pdf"
}

┌──────────────────────────────────────────────────────────────────────────────────┐
│                                                                                  │
│   1. Validate all requested forms exist                                         │
│   2. Queue batch job                                                            │
│   3. Generate each form sequentially                                            │
│   4. Package outputs:                                                           │
│      - ZIP: Create archive with individual files                                │
│      - Merged PDF: Combine all PDFs into single document                        │
│   5. Store and return download link                                             │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘

Response: {
  "export_id": "uuid",
  "status": "processing",
  "estimated_time_seconds": 30,
  "progress_url": "/api/v1/exports/{export_id}/status"
}
```

## 7. Export History & Audit

```python
# Export record structure
{
    "export_id": UUID,
    "form_id": UUID,
    "project_id": UUID,
    "organization_id": UUID,
    "format": "pdf",
    "filename": "Form1_Architect_Certificate_Q4_2024.pdf",
    "file_path": "/exports/org_id/proj_id/form1_20240115.pdf",
    "file_size_bytes": 245678,
    "file_hash": "sha256:...",
    "options": {
        "watermark": None,
        "include_signatures": True
    },
    "generated_by": UUID,
    "generated_at": ISODate,
    "download_count": 0,
    "last_downloaded_at": ISODate,
    "expires_at": ISODate
}
```
