# RERA Compliance Manager - Validation Rules

## 1. Validation Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          VALIDATION ARCHITECTURE                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                           VALIDATION ENGINE                                   │
│                                                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │  Field-Level    │  │  Cross-Field    │  │  Business Rule  │              │
│  │  Validation     │  │  Validation     │  │  Validation     │              │
│  │                 │  │                 │  │                 │              │
│  │ • Type check    │  │ • Dependencies  │  │ • RERA rules    │              │
│  │ • Format check  │  │ • Comparisons   │  │ • State rules   │              │
│  │ • Range check   │  │ • Conditionals  │  │ • Financial rules│             │
│  │ • Required      │  │ • Calculations  │  │ • Date rules    │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│           │                    │                    │                        │
│           └────────────────────┴────────────────────┘                        │
│                                │                                              │
│                       ┌────────▼────────┐                                    │
│                       │ Validation      │                                    │
│                       │ Results         │                                    │
│                       │ Aggregator      │                                    │
│                       └─────────────────┘                                    │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

## 2. Field-Level Validation Rules

### 2.1 Common Field Types

```python
# /app/backend/services/validation_engine.py

FIELD_VALIDATORS = {
    "text": {
        "type": str,
        "validators": ["required", "min_length", "max_length", "pattern"]
    },
    "number": {
        "type": (int, float),
        "validators": ["required", "min", "max", "positive", "integer_only"]
    },
    "currency": {
        "type": (int, float),
        "validators": ["required", "positive", "max_decimals"]
    },
    "date": {
        "type": "date",
        "validators": ["required", "format", "min_date", "max_date", "not_future"]
    },
    "email": {
        "type": str,
        "validators": ["required", "email_format"]
    },
    "select": {
        "type": str,
        "validators": ["required", "in_options"]
    },
    "percentage": {
        "type": (int, float),
        "validators": ["required", "range_0_100"]
    }
}
```

### 2.2 Validation Rule Definitions

```python
# Field validation rules with error messages

VALIDATION_RULES = {
    # Text Validations
    "required": {
        "validator": lambda v: v is not None and str(v).strip() != "",
        "error": "This field is required"
    },
    
    "min_length": {
        "validator": lambda v, min_len: len(str(v)) >= min_len,
        "error": "Minimum {min_len} characters required"
    },
    
    "max_length": {
        "validator": lambda v, max_len: len(str(v)) <= max_len,
        "error": "Maximum {max_len} characters allowed"
    },
    
    "pattern": {
        "validator": lambda v, pattern: re.match(pattern, str(v)) is not None,
        "error": "Invalid format"
    },
    
    # Number Validations
    "min": {
        "validator": lambda v, min_val: float(v) >= min_val,
        "error": "Value must be at least {min_val}"
    },
    
    "max": {
        "validator": lambda v, max_val: float(v) <= max_val,
        "error": "Value must not exceed {max_val}"
    },
    
    "positive": {
        "validator": lambda v: float(v) >= 0,
        "error": "Value must be positive"
    },
    
    "range_0_100": {
        "validator": lambda v: 0 <= float(v) <= 100,
        "error": "Value must be between 0 and 100"
    },
    
    # Date Validations
    "not_future": {
        "validator": lambda v: parse_date(v) <= datetime.now(),
        "error": "Date cannot be in the future"
    },
    
    "min_date": {
        "validator": lambda v, min_d: parse_date(v) >= parse_date(min_d),
        "error": "Date must be on or after {min_d}"
    },
    
    # Format Validations
    "email_format": {
        "validator": lambda v: re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', v),
        "error": "Invalid email format"
    },
    
    "phone_format": {
        "validator": lambda v: re.match(r'^[6-9]\d{9}$', v),
        "error": "Invalid Indian phone number"
    },
    
    "pan_format": {
        "validator": lambda v: re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', v),
        "error": "Invalid PAN format"
    },
    
    "gstin_format": {
        "validator": lambda v: re.match(r'^\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d]$', v),
        "error": "Invalid GSTIN format"
    },
    
    "rera_number_format": {
        "validator": lambda v: re.match(r'^PR[A-Z]{2,3}\d+$', v),
        "error": "Invalid RERA registration number format"
    }
}
```

## 3. Form-Specific Validation Rules

### 3.1 Form 1 - Architect Certificate

```python
FORM_1_VALIDATIONS = {
    "field_rules": {
        "project_name": {
            "type": "text",
            "required": True,
            "max_length": 200
        },
        "rera_number": {
            "type": "text",
            "required": True,
            "pattern": r'^PR[A-Z]{2,3}\d+$'
        },
        "percentage_completion": {
            "type": "percentage",
            "required": True
        },
        "construction_stage": {
            "type": "text",
            "required": True,
            "min_length": 10,
            "max_length": 500
        },
        "sanction_compliance": {
            "type": "select",
            "required": True,
            "options": ["Yes", "No", "Partial"]
        },
        "deviation_details": {
            "type": "text",
            "required_if": {
                "field": "sanction_compliance",
                "values": ["No", "Partial"]
            }
        },
        "architect_name": {
            "type": "text",
            "required": True
        },
        "coa_registration": {
            "type": "text",
            "required": True,
            "pattern": r'^COA/\d{4}/\d+$'
        },
        "date_signed": {
            "type": "date",
            "required": True,
            "not_future": True
        }
    },
    
    "cross_field_rules": [
        {
            "rule_id": "progress_consistency",
            "description": "Progress since last report should be less than or equal to current completion minus previous",
            "fields": ["percentage_completion", "progress_since_last"],
            "validator": "progress_since_last <= percentage_completion",
            "error": "Progress since last report cannot exceed total completion percentage"
        },
        {
            "rule_id": "completion_progression",
            "description": "Completion percentage should not decrease from previous report",
            "async_validator": "validate_completion_progression",
            "error": "Completion percentage cannot be less than previous quarter"
        }
    ],
    
    "business_rules": [
        {
            "rule_id": "quarterly_submission",
            "description": "Form must be submitted within 7 days of quarter end",
            "validator": "validate_submission_deadline",
            "severity": "warning"
        }
    ]
}
```

### 3.2 Form 4 - CA Certificate (Financial)

```python
FORM_4_VALIDATIONS = {
    "field_rules": {
        "total_project_cost": {
            "type": "currency",
            "required": True,
            "positive": True
        },
        "amount_received": {
            "type": "currency",
            "required": True,
            "positive": True
        },
        "amount_utilized": {
            "type": "currency",
            "required": True,
            "positive": True
        },
        "balance_amount": {
            "type": "currency",
            "required": True,
            "positive": True
        },
        "bank_name": {
            "type": "text",
            "required": True
        },
        "account_number": {
            "type": "text",
            "required": True,
            "pattern": r'^\d{9,18}$'
        },
        "ifsc_code": {
            "type": "text",
            "required": True,
            "pattern": r'^[A-Z]{4}0[A-Z0-9]{6}$'
        },
        "ca_membership_number": {
            "type": "text",
            "required": True,
            "pattern": r'^\d{6}$'
        }
    },
    
    "cross_field_rules": [
        {
            "rule_id": "balance_calculation",
            "description": "Balance = Received - Utilized",
            "fields": ["amount_received", "amount_utilized", "balance_amount"],
            "validator": "abs(balance_amount - (amount_received - amount_utilized)) < 0.01",
            "error": "Balance amount does not match (Received - Utilized)"
        },
        {
            "rule_id": "utilization_limit",
            "description": "Utilized amount cannot exceed received amount",
            "fields": ["amount_received", "amount_utilized"],
            "validator": "amount_utilized <= amount_received",
            "error": "Utilized amount cannot exceed amount received"
        }
    ],
    
    "business_rules": [
        {
            "rule_id": "seventy_percent_rule",
            "description": "70% of amount received must be deposited in designated account",
            "validator": "validate_70_percent_rule",
            "severity": "error",
            "error": "70% utilization rule violation detected"
        },
        {
            "rule_id": "designated_account",
            "description": "Must use designated RERA escrow account",
            "async_validator": "validate_designated_account",
            "severity": "warning"
        }
    ]
}
```

### 3.3 Annexure-A - Receivables

```python
ANNEXURE_A_VALIDATIONS = {
    "entry_rules": {
        "unit_number": {
            "type": "text",
            "required": True,
            "unique_in_form": True
        },
        "buyer_name": {
            "type": "text",
            "required": True
        },
        "carpet_area_sqm": {
            "type": "number",
            "required": True,
            "positive": True,
            "max": 1000  # Reasonable max for single unit
        },
        "agreement_date": {
            "type": "date",
            "required": True,
            "not_future": True
        },
        "agreement_value": {
            "type": "currency",
            "required": True,
            "positive": True
        },
        "amount_received": {
            "type": "currency",
            "required": True,
            "min": 0
        },
        "amount_due": {
            "type": "currency",
            "required": True,
            "min": 0
        }
    },
    
    "entry_cross_rules": [
        {
            "rule_id": "amount_consistency",
            "description": "Received + Due = Agreement Value",
            "validator": "abs((amount_received + amount_due) - agreement_value) < 1",
            "error": "Amount received + Amount due must equal Agreement value"
        },
        {
            "rule_id": "received_limit",
            "description": "Received cannot exceed agreement value",
            "validator": "amount_received <= agreement_value",
            "error": "Amount received cannot exceed agreement value"
        }
    ],
    
    "summary_rules": [
        {
            "rule_id": "total_units_match",
            "description": "Entry count should match total units sold",
            "validator": "len(entries) == summary.units_sold",
            "severity": "warning"
        },
        {
            "rule_id": "totals_match",
            "description": "Sum of individual amounts should match summary totals",
            "validator": "validate_summary_totals",
            "error": "Summary totals do not match individual entry sums"
        }
    ]
}
```

## 4. Cross-Form Validation

```python
# Validation across multiple forms for same project/period

CROSS_FORM_VALIDATIONS = [
    {
        "rule_id": "financial_consistency",
        "description": "Form 4 totals should match Annexure-A summary",
        "forms": ["form_4", "annexure_a"],
        "validator": "form_4.amount_received == annexure_a.total_received",
        "severity": "error",
        "error": "Financial data inconsistency between Form 4 and Annexure-A"
    },
    {
        "rule_id": "completion_vs_financial",
        "description": "Financial progress should align with construction progress",
        "forms": ["form_1", "form_4"],
        "validator": "validate_progress_vs_collection",
        "severity": "warning",
        "error": "Collection significantly ahead of construction progress"
    },
    {
        "rule_id": "all_forms_submitted",
        "description": "All required forms should be submitted for the period",
        "forms": ["form_1", "form_2", "form_3", "form_4", "form_5", "form_6", "annexure_a"],
        "validator": "validate_complete_submission",
        "severity": "warning"
    }
]
```

## 5. State-Specific Validation Rules

```python
# /app/backend/services/state_validators/goa.py

GOA_SPECIFIC_RULES = {
    "form_1": [
        {
            "rule_id": "goa_construction_stages",
            "description": "Goa RERA specific construction milestone definitions",
            "validator": "validate_goa_construction_stage",
            "severity": "warning"
        }
    ],
    
    "annexure_a": [
        {
            "rule_id": "goa_rate_per_sqm",
            "description": "Validate rate per sqm is within Goa market range",
            "validator": lambda entry: 50000 <= (entry['agreement_value'] / entry['carpet_area_sqm']) <= 500000,
            "severity": "warning",
            "error": "Rate per sq.m seems outside typical Goa range"
        }
    ],
    
    "general": [
        {
            "rule_id": "goa_taluka_valid",
            "description": "Validate taluka is valid Goa taluka",
            "field": "project.location.taluka",
            "options": [
                "Tiswadi", "Bardez", "Pernem", "Bicholim", "Sattari",
                "Ponda", "Mormugao", "Salcete", "Quepem", "Canacona", "Sanguem"
            ]
        }
    ]
}

# /app/backend/services/state_validators/maharashtra.py

MAHARASHTRA_SPECIFIC_RULES = {
    "form_1": [
        {
            "rule_id": "maha_rera_format",
            "description": "Maharashtra RERA number format",
            "field": "rera_number",
            "pattern": r'^P\d{11}$',
            "error": "Invalid MahaRERA registration number format"
        }
    ],
    
    "general": [
        {
            "rule_id": "maha_district_valid",
            "description": "Validate district is valid Maharashtra district",
            "field": "project.location.district",
            "validator": "validate_maharashtra_district"
        }
    ]
}
```

## 6. Validation Engine Implementation

```python
# /app/backend/services/validation_engine.py

from typing import Dict, List, Any
from pydantic import BaseModel

class ValidationError(BaseModel):
    field_id: str
    message: str
    severity: str  # "error" or "warning"
    value: Any = None
    rule_id: str = None

class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    validated_at: str

class ValidationEngine:
    """
    Main validation engine for RERA forms
    """
    
    def __init__(self, state: str):
        self.state = state
        self.state_rules = self._load_state_rules(state)
    
    async def validate_form(
        self, 
        form_type: str, 
        form_data: dict,
        project_data: dict = None
    ) -> ValidationResult:
        """
        Validate a complete form
        """
        errors = []
        warnings = []
        
        # Get form-specific rules
        form_rules = self._get_form_rules(form_type)
        
        # 1. Field-level validation
        field_results = await self._validate_fields(
            form_data, 
            form_rules.get('field_rules', {})
        )
        errors.extend(field_results['errors'])
        warnings.extend(field_results['warnings'])
        
        # 2. Cross-field validation
        cross_results = await self._validate_cross_fields(
            form_data,
            form_rules.get('cross_field_rules', [])
        )
        errors.extend(cross_results['errors'])
        warnings.extend(cross_results['warnings'])
        
        # 3. Business rule validation
        business_results = await self._validate_business_rules(
            form_data,
            project_data,
            form_rules.get('business_rules', [])
        )
        errors.extend(business_results['errors'])
        warnings.extend(business_results['warnings'])
        
        # 4. State-specific validation
        state_results = await self._validate_state_rules(
            form_type,
            form_data,
            project_data
        )
        errors.extend(state_results['errors'])
        warnings.extend(state_results['warnings'])
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validated_at=datetime.now(timezone.utc).isoformat()
        )
    
    async def _validate_fields(
        self, 
        data: dict, 
        rules: dict
    ) -> dict:
        """
        Validate individual fields
        """
        errors = []
        warnings = []
        
        for field_id, field_rules in rules.items():
            value = data.get(field_id)
            
            # Check required
            if field_rules.get('required') and not value:
                errors.append(ValidationError(
                    field_id=field_id,
                    message="This field is required",
                    severity="error",
                    rule_id="required"
                ))
                continue
            
            # Skip further validation if empty and not required
            if not value:
                continue
            
            # Type validation
            field_type = field_rules.get('type')
            if not self._validate_type(value, field_type):
                errors.append(ValidationError(
                    field_id=field_id,
                    message=f"Invalid {field_type} value",
                    severity="error",
                    value=value,
                    rule_id="type"
                ))
                continue
            
            # Pattern validation
            pattern = field_rules.get('pattern')
            if pattern and not re.match(pattern, str(value)):
                errors.append(ValidationError(
                    field_id=field_id,
                    message="Invalid format",
                    severity="error",
                    value=value,
                    rule_id="pattern"
                ))
            
            # Range validation
            if field_rules.get('min') is not None:
                if float(value) < field_rules['min']:
                    errors.append(ValidationError(
                        field_id=field_id,
                        message=f"Value must be at least {field_rules['min']}",
                        severity="error",
                        value=value,
                        rule_id="min"
                    ))
            
            # ... additional validations
        
        return {"errors": errors, "warnings": warnings}
    
    async def _validate_cross_fields(
        self, 
        data: dict, 
        rules: list
    ) -> dict:
        """
        Validate relationships between fields
        """
        errors = []
        warnings = []
        
        for rule in rules:
            try:
                # Build expression context
                context = {field: data.get(field) for field in rule.get('fields', [])}
                
                # Evaluate expression
                result = eval(rule['validator'], {"__builtins__": {}}, context)
                
                if not result:
                    severity = rule.get('severity', 'error')
                    error = ValidationError(
                        field_id=rule['fields'][0],
                        message=rule['error'],
                        severity=severity,
                        rule_id=rule['rule_id']
                    )
                    if severity == 'error':
                        errors.append(error)
                    else:
                        warnings.append(error)
            
            except Exception as e:
                # Log validation error but don't fail
                pass
        
        return {"errors": errors, "warnings": warnings}
```

## 7. Validation Response Format

```python
# API Response for POST /api/v1/forms/{form_id}/validate

{
    "is_valid": false,
    "errors": [
        {
            "field_id": "percentage_completion",
            "message": "Value must be between 0 and 100",
            "severity": "error",
            "value": 105,
            "rule_id": "range_0_100"
        },
        {
            "field_id": "deviation_details",
            "message": "This field is required when compliance is 'Partial'",
            "severity": "error",
            "value": null,
            "rule_id": "required_if"
        }
    ],
    "warnings": [
        {
            "field_id": "progress_since_last",
            "message": "Progress seems unusually high for one quarter",
            "severity": "warning",
            "value": 35,
            "rule_id": "progress_warning"
        }
    ],
    "validated_at": "2024-01-15T10:30:00Z",
    "can_submit": false
}
```
