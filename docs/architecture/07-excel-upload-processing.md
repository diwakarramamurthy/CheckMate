# RERA Compliance Manager - Excel Upload Processing Logic

## 1. Excel Processing Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        EXCEL PROCESSING PIPELINE                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Upload  │───▶│  Parse   │───▶│  Map     │───▶│ Validate │───▶│  Store   │
│  File    │    │  Sheets  │    │  Columns │    │  Data    │    │  Forms   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │               │
     ▼               ▼               ▼               ▼               ▼
 File saved      Sheet data     Data mapped    Errors/warnings  Forms created
 to storage      extracted      to form fields  reported        in database
```

## 2. Supported Excel Templates

### 2.1 Financial Data Template (For Form 4, 5)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         FINANCIAL DATA TEMPLATE                                  │
│                         (Sheet: "Financial Summary")                             │
└─────────────────────────────────────────────────────────────────────────────────┘

│ Row │    A         │      B           │      C         │      D           │
├─────┼──────────────┼──────────────────┼────────────────┼──────────────────┤
│  1  │ PROJECT FINANCIAL DATA - Q4 2024                                    │
│  2  │              │                  │                │                  │
│  3  │ Particulars  │ Amount (₹)       │ Remarks        │                  │
├─────┼──────────────┼──────────────────┼────────────────┼──────────────────┤
│  4  │ Total Project Cost         │ 50,00,00,000   │                  │
│  5  │ Land Cost                  │ 15,00,00,000   │                  │
│  6  │ Construction Cost          │ 30,00,00,000   │                  │
│  7  │ Other Costs               │  5,00,00,000   │                  │
│  8  │              │                  │                │                  │
│  9  │ COLLECTIONS                │                  │                │                  │
│ 10  │ Amount Received            │ 25,00,00,000   │                  │
│ 11  │ 70% of Received            │ 17,50,00,000   │ Auto-calculated  │
│ 12  │              │                  │                │                  │
│ 13  │ UTILIZATION               │                  │                │                  │
│ 14  │ Amount Utilized            │ 18,00,00,000   │                  │
│ 15  │ Balance in Account         │  7,00,00,000   │                  │
│ 16  │              │                  │                │                  │
│ 17  │ BANK DETAILS              │                  │                │                  │
│ 18  │ Bank Name                  │ State Bank of India │              │
│ 19  │ Account Number             │ 123456789012   │                  │
│ 20  │ IFSC Code                  │ SBIN0001234    │                  │
└─────┴──────────────┴──────────────────┴────────────────┴──────────────────┘
```

### 2.2 Receivables Template (For Annexure-A)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         RECEIVABLES TEMPLATE                                     │
│                         (Sheet: "Receivables")                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

│Row│   A    │   B    │   C      │     D      │     E        │     F       │
├───┼────────┼────────┼──────────┼────────────┼──────────────┼─────────────┤
│ 1 │ STATEMENT OF RECEIVABLES - ANNEXURE A                                │
│ 2 │ Project: Sunset Heights Phase 2    │ RERA No: PRGO12345            │
│ 3 │                                                                       │
│ 4 │ Unit   │ Type   │ Carpet   │ Buyer      │ Agreement    │ Agreement   │
│   │ No.    │        │ Area     │ Name       │ Date         │ Value (₹)   │
├───┼────────┼────────┼──────────┼────────────┼──────────────┼─────────────┤
│ 5 │ A-101  │ 2BHK   │ 65.50    │ Ramesh K.  │ 15-Mar-2023  │ 75,00,000   │
│ 6 │ A-102  │ 2BHK   │ 68.00    │ Suresh P.  │ 20-Apr-2023  │ 78,50,000   │
│ 7 │ A-103  │ 3BHK   │ 95.00    │ Meera S.   │ 01-May-2023  │ 1,10,00,000 │
│ 8 │ A-201  │ 2BHK   │ 65.50    │ John D.    │ 15-Jun-2023  │ 76,00,000   │
│ 9 │ ...    │ ...    │ ...      │ ...        │ ...          │ ...         │
│50 │        │        │          │            │              │             │
│51 │ TOTAL  │        │          │            │              │ 35,00,00,000│
└───┴────────┴────────┴──────────┴────────────┴──────────────┴─────────────┘

│Row│    G          │     H       │     I       │     J       │
├───┼───────────────┼─────────────┼─────────────┼─────────────┤
│ 4 │ Amt Received  │ Amt Due     │ Due Date    │ Remarks     │
│   │ (₹)           │ (₹)         │             │             │
├───┼───────────────┼─────────────┼─────────────┼─────────────┤
│ 5 │ 60,00,000     │ 15,00,000   │ 15-Mar-2025 │             │
│ 6 │ 50,00,000     │ 28,50,000   │ 20-Apr-2025 │             │
│ 7 │ 88,00,000     │ 22,00,000   │ 01-May-2025 │ EMI         │
│ 8 │ 45,00,000     │ 31,00,000   │ 15-Jun-2025 │ Bank loan   │
│ 9 │ ...           │ ...         │ ...         │ ...         │
│51 │ 28,00,00,000  │ 7,00,00,000 │             │             │
└───┴───────────────┴─────────────┴─────────────┴─────────────┘
```

## 3. Excel Parser Module

### 3.1 Parser Architecture

```python
# /app/backend/services/excel_parser.py

class ExcelParser:
    """
    Main Excel parsing service
    """
    
    SUPPORTED_SHEETS = {
        "Financial Summary": {
            "target_form": "form_4",
            "parser": "parse_financial_summary",
            "required_columns": ["Particulars", "Amount"]
        },
        "Receivables": {
            "target_form": "annexure_a",
            "parser": "parse_receivables",
            "required_columns": ["Unit No.", "Buyer Name", "Agreement Value"]
        },
        "Construction Progress": {
            "target_form": "form_1",
            "parser": "parse_construction_progress",
            "required_columns": ["Stage", "Percentage"]
        }
    }
    
    def __init__(self, file_path: str, project_id: str):
        self.file_path = file_path
        self.project_id = project_id
        self.workbook = None
        self.results = ParseResults()
    
    async def parse(self) -> ParseResults:
        """
        Main parsing entry point
        """
        # 1. Load workbook
        self.workbook = openpyxl.load_workbook(self.file_path, data_only=True)
        
        # 2. Discover sheets
        self.results.sheets_found = self.workbook.sheetnames
        
        # 3. Process each recognized sheet
        for sheet_name in self.workbook.sheetnames:
            if sheet_name in self.SUPPORTED_SHEETS:
                await self._process_sheet(sheet_name)
        
        return self.results
    
    async def _process_sheet(self, sheet_name: str) -> None:
        """
        Process individual sheet
        """
        config = self.SUPPORTED_SHEETS[sheet_name]
        sheet = self.workbook[sheet_name]
        
        # Call appropriate parser
        parser_method = getattr(self, config["parser"])
        sheet_data = await parser_method(sheet, config)
        
        self.results.sheets_processed.append({
            "sheet_name": sheet_name,
            "rows_count": sheet_data.row_count,
            "mapped_to_form": config["target_form"],
            "data": sheet_data.data,
            "errors": sheet_data.errors,
            "warnings": sheet_data.warnings
        })
```

### 3.2 Column Mapping Logic

```python
# Column mapping configuration

RECEIVABLES_COLUMN_MAP = {
    # Excel Column Header -> Form Field ID
    "Unit No.": "unit_number",
    "Unit Number": "unit_number",
    "Flat No.": "unit_number",
    
    "Type": "flat_type",
    "Unit Type": "flat_type",
    "Flat Type": "flat_type",
    
    "Carpet Area": "carpet_area_sqm",
    "Carpet Area (sq.m)": "carpet_area_sqm",
    "Area (sqm)": "carpet_area_sqm",
    
    "Buyer Name": "buyer_name",
    "Allottee Name": "buyer_name",
    "Customer Name": "buyer_name",
    
    "Agreement Date": "agreement_date",
    "Date of Agreement": "agreement_date",
    "Booking Date": "agreement_date",
    
    "Agreement Value": "agreement_value",
    "Agreement Value (₹)": "agreement_value",
    "Total Value": "agreement_value",
    
    "Amount Received": "amount_received",
    "Amt Received": "amount_received",
    "Received (₹)": "amount_received",
    
    "Amount Due": "amount_due",
    "Amt Due": "amount_due",
    "Balance": "amount_due",
    "Outstanding": "amount_due"
}

def find_column_mapping(header_row: list) -> dict:
    """
    Find best column mapping based on header row
    """
    mapping = {}
    
    for col_idx, header in enumerate(header_row):
        if header is None:
            continue
            
        # Normalize header
        normalized = str(header).strip().title()
        
        # Find matching field
        for excel_header, field_id in RECEIVABLES_COLUMN_MAP.items():
            if normalized == excel_header or \
               normalized.lower() == excel_header.lower():
                mapping[col_idx] = field_id
                break
    
    return mapping
```

### 3.3 Data Extraction Process

```python
async def parse_receivables(self, sheet, config: dict) -> SheetData:
    """
    Parse receivables sheet for Annexure-A
    """
    result = SheetData()
    
    # 1. Find header row (usually row 4 or 5)
    header_row_idx = self._find_header_row(sheet, ["Unit No.", "Buyer Name"])
    if header_row_idx is None:
        result.errors.append({
            "row": 1,
            "column": "A",
            "message": "Could not find header row with expected columns"
        })
        return result
    
    # 2. Extract header and create column mapping
    header_row = [cell.value for cell in sheet[header_row_idx]]
    column_mapping = find_column_mapping(header_row)
    
    # 3. Validate required columns exist
    required_fields = ["unit_number", "buyer_name", "agreement_value"]
    missing = [f for f in required_fields if f not in column_mapping.values()]
    if missing:
        result.errors.append({
            "row": header_row_idx,
            "column": "A",
            "message": f"Missing required columns: {', '.join(missing)}"
        })
        return result
    
    # 4. Extract data rows
    data_rows = []
    for row_idx in range(header_row_idx + 1, sheet.max_row + 1):
        row_data = {}
        row = sheet[row_idx]
        
        # Skip empty rows
        if all(cell.value is None for cell in row):
            continue
        
        # Skip total/summary rows
        first_cell = str(row[0].value or "").upper()
        if first_cell in ["TOTAL", "SUBTOTAL", "SUM", ""]:
            continue
        
        # Extract cell values
        for col_idx, field_id in column_mapping.items():
            cell = row[col_idx]
            value = cell.value
            
            # Type conversion and validation
            converted_value, error = self._convert_value(
                value, field_id, row_idx, col_idx
            )
            
            if error:
                result.errors.append(error) if error["severity"] == "error" \
                    else result.warnings.append(error)
            
            row_data[field_id] = converted_value
        
        # Add row number
        row_data["row_number"] = len(data_rows) + 1
        row_data["source"] = "excel_import"
        
        data_rows.append(row_data)
    
    result.data = data_rows
    result.row_count = len(data_rows)
    
    return result

def _convert_value(self, value, field_id: str, row: int, col: int):
    """
    Convert cell value to appropriate type
    """
    error = None
    
    # Define field types
    NUMERIC_FIELDS = ["carpet_area_sqm", "agreement_value", "amount_received", "amount_due"]
    DATE_FIELDS = ["agreement_date", "due_date"]
    
    if value is None:
        return None, None
    
    if field_id in NUMERIC_FIELDS:
        try:
            # Handle currency formatted values
            if isinstance(value, str):
                # Remove currency symbols and commas
                value = value.replace("₹", "").replace(",", "").strip()
            return float(value), None
        except (ValueError, TypeError):
            return None, {
                "row": row,
                "column": self._col_letter(col),
                "message": f"Invalid numeric value: {value}",
                "severity": "error"
            }
    
    elif field_id in DATE_FIELDS:
        try:
            if isinstance(value, datetime):
                return value.isoformat(), None
            # Parse string dates
            return parse_date(str(value)).isoformat(), None
        except:
            return None, {
                "row": row,
                "column": self._col_letter(col),
                "message": f"Invalid date format: {value}",
                "severity": "warning"
            }
    
    else:
        return str(value).strip(), None
```

## 4. Upload Processing Workflow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         UPLOAD PROCESSING WORKFLOW                               │
└─────────────────────────────────────────────────────────────────────────────────┘

STEP 1: FILE UPLOAD
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  POST /api/v1/excel/upload                                                  │
│  Content-Type: multipart/form-data                                          │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. Validate file extension (.xlsx, .xls)                            │   │
│  │ 2. Validate file size (< 10MB)                                      │   │
│  │ 3. Scan for malware (optional)                                      │   │
│  │ 4. Generate unique filename                                         │   │
│  │ 5. Save to /uploads/{org_id}/{project_id}/{filename}               │   │
│  │ 6. Create upload record in database                                 │   │
│  │ 7. Return upload_id                                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  Response: { upload_id: "uuid", status: "uploaded" }                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
STEP 2: PARSE FILE
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  POST /api/v1/excel/uploads/{upload_id}/parse                              │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. Load file from storage                                           │   │
│  │ 2. Identify sheets and their purposes                               │   │
│  │ 3. Map columns to form fields                                       │   │
│  │ 4. Extract and convert data                                         │   │
│  │ 5. Validate each row                                                │   │
│  │ 6. Generate error/warning report                                    │   │
│  │ 7. Store parsed data temporarily                                    │   │
│  │ 8. Update upload status                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  Response: { status: "parsed", parse_results: {...} }                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
STEP 3: PREVIEW DATA
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  GET /api/v1/excel/uploads/{upload_id}/preview                             │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Returns:                                                            │   │
│  │ - Parsed data organized by target form                              │   │
│  │ - Error list with cell references                                   │   │
│  │ - Warning list with suggestions                                     │   │
│  │ - Summary statistics                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
STEP 4: USER REVIEW & FIX
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  Frontend displays:                                                          │
│  - Data preview table                                                        │
│  - Errors highlighted in red                                                 │
│  - Warnings highlighted in yellow                                            │
│  - Option to edit values inline                                              │
│  - Option to ignore warnings                                                 │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
STEP 5: CONFIRM & CREATE FORMS
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  POST /api/v1/excel/uploads/{upload_id}/confirm                            │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. Verify no blocking errors remain                                 │   │
│  │ 2. Create form documents for each target form                       │   │
│  │ 3. Create form_entries for line items (Annexure-A)                  │   │
│  │ 4. Link forms to upload record                                      │   │
│  │ 5. Update project compliance status                                 │   │
│  │ 6. Log action in audit trail                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  Response: { forms_created: ["uuid1", "uuid2"], status: "completed" }       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 5. Error Handling

### 5.1 Error Categories

```python
ERROR_CATEGORIES = {
    "FILE_ERROR": {
        "UNSUPPORTED_FORMAT": "File format not supported. Use .xlsx or .xls",
        "FILE_TOO_LARGE": "File exceeds 10MB limit",
        "CORRUPTED_FILE": "File appears to be corrupted",
        "PASSWORD_PROTECTED": "Password-protected files not supported"
    },
    
    "STRUCTURE_ERROR": {
        "NO_RECOGNIZED_SHEETS": "No recognized sheet names found",
        "MISSING_HEADER": "Could not identify header row",
        "MISSING_COLUMNS": "Required columns not found: {columns}"
    },
    
    "DATA_ERROR": {
        "INVALID_NUMBER": "Cell {cell} contains invalid number: {value}",
        "INVALID_DATE": "Cell {cell} contains invalid date: {value}",
        "REQUIRED_EMPTY": "Required field {field} is empty at row {row}",
        "DUPLICATE_UNIT": "Duplicate unit number {unit} at row {row}",
        "NEGATIVE_VALUE": "Negative value not allowed in {field} at row {row}"
    },
    
    "BUSINESS_ERROR": {
        "AMOUNT_MISMATCH": "Amount received ({received}) exceeds agreement value ({total})",
        "DATE_FUTURE": "Agreement date cannot be in the future",
        "AREA_INVALID": "Carpet area must be positive number"
    }
}
```

### 5.2 Error Response Format

```python
{
    "upload_id": "uuid",
    "status": "parsed_with_errors",
    "parse_results": {
        "sheets_found": ["Receivables", "Financial Summary", "Notes"],
        "sheets_processed": [
            {
                "sheet_name": "Receivables",
                "rows_count": 48,
                "valid_rows": 45,
                "error_rows": 3,
                "mapped_to_form": "annexure_a"
            }
        ],
        "errors": [
            {
                "sheet": "Receivables",
                "row": 15,
                "column": "F",
                "cell_reference": "F15",
                "field": "agreement_value",
                "message": "Invalid numeric value: '75lakhs'",
                "severity": "error",
                "suggestion": "Enter numeric value like 7500000"
            },
            {
                "sheet": "Receivables",
                "row": 23,
                "column": "E",
                "cell_reference": "E23",
                "field": "agreement_date",
                "message": "Invalid date format: '15/13/2024'",
                "severity": "error",
                "suggestion": "Use DD/MM/YYYY or YYYY-MM-DD format"
            }
        ],
        "warnings": [
            {
                "sheet": "Receivables",
                "row": 8,
                "column": "G",
                "message": "Amount received equals agreement value - verify if complete payment",
                "severity": "warning"
            }
        ],
        "summary": {
            "total_rows": 48,
            "valid_rows": 45,
            "error_count": 3,
            "warning_count": 1,
            "can_proceed": false
        }
    }
}
```

## 6. Template Download

Users can download blank templates with proper formatting:

```python
GET /api/v1/excel/template/{form_type}

# Returns pre-formatted Excel template with:
# - Proper column headers
# - Data validation dropdowns
# - Sample data (optional)
# - Instructions sheet
# - Formatting and formulas
```
