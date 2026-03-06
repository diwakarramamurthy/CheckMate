# RERA Compliance Manager - Multi-State Template System Design

## 1. Multi-State Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      MULTI-STATE TEMPLATE SYSTEM                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                           TEMPLATE REGISTRY                                      │
│                                                                                  │
│   ┌───────────────────────────────────────────────────────────────────────┐    │
│   │                        State Configuration                             │    │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │    │
│   │  │   GOA   │  │MAHARASH │  │KARNATAKA│  │ KERALA  │  │ GUJARAT │   │    │
│   │  │         │  │  TRA    │  │         │  │         │  │         │   │    │
│   │  │ ✓ Active│  │ ○ Ready │  │ ○ Plan  │  │ ○ Plan  │  │ ○ Plan  │   │    │
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │    │
│   └───────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
│   ┌───────────────────────────────────────────────────────────────────────┐    │
│   │                        Template Inheritance                            │    │
│   │                                                                        │    │
│   │            ┌─────────────────────────────┐                            │    │
│   │            │     BASE TEMPLATE           │                            │    │
│   │            │   (Common structure)        │                            │    │
│   │            └──────────────┬──────────────┘                            │    │
│   │                           │                                            │    │
│   │         ┌─────────────────┼─────────────────┐                         │    │
│   │         ▼                 ▼                 ▼                         │    │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                   │    │
│   │  │ GOA Template│  │MAHA Template│  │ KA Template │                   │    │
│   │  │  (Override) │  │  (Override) │  │  (Override) │                   │    │
│   │  └─────────────┘  └─────────────┘  └─────────────┘                   │    │
│   │                                                                        │    │
│   └───────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 2. State Configuration Schema

### 2.1 Master State Configuration

```python
# /app/backend/config/states.py

SUPPORTED_STATES = {
    "GOA": {
        "code": "GOA",
        "name": "Goa",
        "is_active": True,
        "authority": {
            "name": "Goa Real Estate Regulatory Authority",
            "short_name": "GOARERA",
            "website": "https://rera.goa.gov.in",
            "address": "Porvorim, Goa - 403521",
            "email": "grievance.rera@goa.gov.in"
        },
        "rera_number_format": {
            "pattern": r"^PRGO\d{5}$",
            "example": "PRGO12345",
            "prefix": "PRGO"
        },
        "forms_config": {
            "forms_required": ["form_1", "form_2", "form_3", "form_4", "form_5", "form_6", "annexure_a"],
            "quarterly_forms": ["form_1", "form_3", "form_4", "form_5", "annexure_a"],
            "annual_forms": ["form_6"],
            "completion_forms": ["form_2"]
        },
        "locale": {
            "date_format": "DD/MM/YYYY",
            "currency": "INR",
            "number_locale": "en-IN",
            "timezone": "Asia/Kolkata"
        },
        "geographic": {
            "districts": ["North Goa", "South Goa"],
            "talukas": ["Tiswadi", "Bardez", "Pernem", "Bicholim", "Sattari",
                       "Ponda", "Mormugao", "Salcete", "Quepem", "Canacona", "Sanguem"]
        },
        "compliance": {
            "submission_deadline_days": 7,  # Days after quarter end
            "reminder_days_before": [14, 7, 3, 1]
        }
    },
    
    "MAHARASHTRA": {
        "code": "MAHARASHTRA",
        "name": "Maharashtra",
        "is_active": False,  # Ready but not activated
        "authority": {
            "name": "Maharashtra Real Estate Regulatory Authority",
            "short_name": "MahaRERA",
            "website": "https://maharera.mahaonline.gov.in",
            "address": "Mumbai, Maharashtra",
            "email": "support@maharera.gov.in"
        },
        "rera_number_format": {
            "pattern": r"^P\d{11}$",
            "example": "P51200012345",
            "prefix": "P"
        },
        "forms_config": {
            "forms_required": ["form_1", "form_2", "form_3", "form_4", "form_5", "form_6", "annexure_a"],
            "quarterly_forms": ["form_1", "form_3", "form_4", "form_5", "annexure_a"],
            "annual_forms": ["form_6"],
            "completion_forms": ["form_2"]
        },
        "locale": {
            "date_format": "DD/MM/YYYY",
            "currency": "INR",
            "number_locale": "en-IN",
            "timezone": "Asia/Kolkata"
        },
        "geographic": {
            "districts": ["Mumbai City", "Mumbai Suburban", "Thane", "Pune", "Nagpur", ...],
            "zones": ["Mumbai Metropolitan Region", "Pune Metropolitan Region", ...]
        }
    },
    
    # Template for adding new states
    "_TEMPLATE": {
        "code": "STATE_CODE",
        "name": "State Name",
        "is_active": False,
        "authority": {
            "name": "State RERA Authority Name",
            "short_name": "RERA",
            "website": "",
            "address": "",
            "email": ""
        },
        "rera_number_format": {
            "pattern": r"",
            "example": "",
            "prefix": ""
        }
    }
}
```

### 2.2 State-Specific Template Variations

```python
# /app/backend/config/template_variations.py

TEMPLATE_VARIATIONS = {
    "GOA": {
        "form_1": {
            "version": "2024.1",
            "effective_from": "2024-01-01",
            
            # Goa-specific field additions
            "additional_fields": [
                {
                    "field_id": "panchayat_noc",
                    "label": "Panchayat NOC Number",
                    "type": "text",
                    "section": "compliance",
                    "required": False
                }
            ],
            
            # Fields to remove from base template
            "removed_fields": [],
            
            # Field modifications
            "field_overrides": {
                "construction_stage": {
                    "options": [
                        "Land leveling and compound wall",
                        "Foundation work",
                        "Plinth level",
                        "RCC columns up to slab level",
                        "First floor slab",
                        "Brickwork",
                        "Internal plastering",
                        "External plastering",
                        "Flooring and tiling",
                        "Electrical and plumbing",
                        "Painting and finishing",
                        "Completion"
                    ]
                }
            },
            
            # Goa-specific validation rules
            "validation_overrides": {
                "percentage_completion": {
                    "milestones": {
                        "Foundation": {"min": 0, "max": 15},
                        "Plinth": {"min": 10, "max": 25},
                        "Structural": {"min": 20, "max": 60},
                        "Finishing": {"min": 50, "max": 90},
                        "Completion": {"min": 85, "max": 100}
                    }
                }
            },
            
            # Export template customization
            "export_config": {
                "header_logo": "goa_rera_logo.png",
                "header_text": "GOA REAL ESTATE REGULATORY AUTHORITY",
                "footer_text": "This is a computer generated certificate",
                "watermark_draft": "DRAFT - NOT FOR SUBMISSION"
            }
        },
        
        "annexure_a": {
            "version": "2024.1",
            
            # Goa-specific columns
            "additional_columns": [
                {
                    "column_id": "communidade_land",
                    "header": "Communidade Land",
                    "type": "boolean",
                    "default": False
                }
            ],
            
            # Rate validation for Goa market
            "validation_overrides": {
                "rate_per_sqm": {
                    "min": 50000,
                    "max": 500000,
                    "warning_threshold": {
                        "low": 75000,
                        "high": 350000
                    }
                }
            }
        }
    },
    
    "MAHARASHTRA": {
        "form_1": {
            "version": "2024.1",
            "effective_from": "2024-01-01",
            
            "field_overrides": {
                "construction_stage": {
                    "options": [
                        "Below plinth",
                        "Plinth",
                        "Podium",
                        "Ground floor",
                        "Stilt",
                        "Typical floor",
                        "Terrace",
                        "Internal finishing",
                        "External finishing",
                        "Services",
                        "Amenities",
                        "Occupation certificate applied",
                        "Occupation certificate received"
                    ]
                }
            },
            
            "additional_fields": [
                {
                    "field_id": "bmc_approval_number",
                    "label": "BMC/Local Authority Approval Number",
                    "type": "text",
                    "required": False
                }
            ],
            
            "export_config": {
                "header_logo": "maharera_logo.png",
                "header_text": "MAHARASHTRA REAL ESTATE REGULATORY AUTHORITY"
            }
        }
    }
}
```

## 3. Template Engine Architecture

### 3.1 Template Resolver

```python
# /app/backend/services/template_resolver.py

class TemplateResolver:
    """
    Resolves the correct template for a given state and form type
    """
    
    def __init__(self):
        self.base_templates_path = "/app/backend/templates/base"
        self.state_templates_path = "/app/backend/templates"
    
    def get_template_config(self, state: str, form_type: str) -> dict:
        """
        Get merged template configuration for state + form
        """
        # 1. Load base template config
        base_config = self._load_base_template(form_type)
        
        # 2. Load state variations
        state_variations = TEMPLATE_VARIATIONS.get(state, {}).get(form_type, {})
        
        # 3. Merge configurations
        merged_config = self._merge_configs(base_config, state_variations)
        
        return merged_config
    
    def _merge_configs(self, base: dict, override: dict) -> dict:
        """
        Deep merge base config with state-specific overrides
        """
        result = copy.deepcopy(base)
        
        # Add additional fields
        if "additional_fields" in override:
            result["structure"]["sections"][-1]["fields"].extend(
                override["additional_fields"]
            )
        
        # Remove fields
        if "removed_fields" in override:
            for section in result["structure"]["sections"]:
                section["fields"] = [
                    f for f in section["fields"] 
                    if f["field_id"] not in override["removed_fields"]
                ]
        
        # Override field properties
        if "field_overrides" in override:
            for field_id, overrides in override["field_overrides"].items():
                self._apply_field_override(result, field_id, overrides)
        
        # Merge export config
        if "export_config" in override:
            result["export_config"] = {
                **result.get("export_config", {}),
                **override["export_config"]
            }
        
        # Merge validation overrides
        if "validation_overrides" in override:
            result["validation_rules"] = {
                **result.get("validation_rules", {}),
                **override["validation_overrides"]
            }
        
        return result
    
    def get_html_template_path(self, state: str, form_type: str) -> str:
        """
        Get path to HTML template file
        """
        # First try state-specific template
        state_path = f"{self.state_templates_path}/{state.lower()}/html/{form_type}.html"
        if os.path.exists(state_path):
            return state_path
        
        # Fall back to base template
        base_path = f"{self.base_templates_path}/html/{form_type}.html"
        return base_path
```

### 3.2 Dynamic Field Renderer

```python
# /app/backend/services/field_renderer.py

class FieldRenderer:
    """
    Renders form fields based on template configuration
    """
    
    def render_field(self, field_config: dict, value: Any = None) -> dict:
        """
        Render a field with its current value
        """
        field_type = field_config.get("type")
        
        rendered = {
            "field_id": field_config["field_id"],
            "label": field_config["label"],
            "type": field_type,
            "value": value,
            "required": field_config.get("required", False),
            "help_text": field_config.get("help_text"),
            "placeholder": field_config.get("placeholder"),
            "disabled": field_config.get("disabled", False),
            "validation": field_config.get("validation_rules", {})
        }
        
        # Add type-specific properties
        if field_type == "select":
            rendered["options"] = field_config.get("options", [])
        
        elif field_type == "number":
            rendered["min"] = field_config.get("validation_rules", {}).get("min")
            rendered["max"] = field_config.get("validation_rules", {}).get("max")
            rendered["step"] = field_config.get("step", 1)
        
        elif field_type == "date":
            rendered["min_date"] = field_config.get("min_date")
            rendered["max_date"] = field_config.get("max_date")
        
        return rendered
    
    def render_table(self, table_config: dict, entries: list) -> dict:
        """
        Render a data table (e.g., for Annexure-A)
        """
        return {
            "table_id": table_config["table_id"],
            "title": table_config["title"],
            "columns": table_config["columns"],
            "rows": entries,
            "footer": self._calculate_footer(table_config, entries)
        }
    
    def _calculate_footer(self, table_config: dict, entries: list) -> dict:
        """
        Calculate footer totals for table
        """
        footer = {}
        for footer_def in table_config.get("footer", []):
            column = footer_def["column"]
            if footer_def["type"] == "sum":
                footer[column] = sum(
                    entry.get(column, 0) or 0 
                    for entry in entries
                )
        return footer
```

## 4. Adding a New State - Step by Step

### 4.1 State Addition Workflow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      ADDING A NEW STATE WORKFLOW                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

STEP 1: RESEARCH & DOCUMENTATION
────────────────────────────────────────────────────────────────────────────────────
□ Study state RERA website and regulations
□ Download official form templates
□ Document field differences from base templates
□ Note state-specific validation requirements
□ Identify any unique compliance rules
────────────────────────────────────────────────────────────────────────────────────

                                      │
                                      ▼

STEP 2: CONFIGURATION SETUP
────────────────────────────────────────────────────────────────────────────────────
□ Add state to SUPPORTED_STATES config
□ Add RERA number format pattern
□ Configure authority details
□ Set up geographic data (districts, cities)
────────────────────────────────────────────────────────────────────────────────────

                                      │
                                      ▼

STEP 3: TEMPLATE VARIATIONS
────────────────────────────────────────────────────────────────────────────────────
□ Define field additions for each form type
□ Define field removals/modifications
□ Configure validation rule overrides
□ Set up export configuration (logos, headers)
────────────────────────────────────────────────────────────────────────────────────

                                      │
                                      ▼

STEP 4: CREATE EXPORT TEMPLATES
────────────────────────────────────────────────────────────────────────────────────
□ Create HTML templates for PDF export
□ Create DOCX templates for Word export
□ Create XLSX templates for Excel export
□ Add state logo and branding assets
────────────────────────────────────────────────────────────────────────────────────

                                      │
                                      ▼

STEP 5: VALIDATION RULES
────────────────────────────────────────────────────────────────────────────────────
□ Create state-specific validation file
□ Implement custom validators if needed
□ Test validation with sample data
────────────────────────────────────────────────────────────────────────────────────

                                      │
                                      ▼

STEP 6: DATABASE SETUP
────────────────────────────────────────────────────────────────────────────────────
□ Add template records to templates collection
□ Set version and effective dates
□ Mark as active/inactive
────────────────────────────────────────────────────────────────────────────────────

                                      │
                                      ▼

STEP 7: TESTING
────────────────────────────────────────────────────────────────────────────────────
□ Test form creation for new state
□ Test Excel upload with state format
□ Test report generation
□ Test validation rules
□ Test export in all formats
────────────────────────────────────────────────────────────────────────────────────

                                      │
                                      ▼

STEP 8: ACTIVATION
────────────────────────────────────────────────────────────────────────────────────
□ Set is_active = True in config
□ Update frontend state selector
□ Announce new state support
────────────────────────────────────────────────────────────────────────────────────
```

### 4.2 New State File Structure

```
/app/backend/templates/
├── base/                          # Base templates (shared)
│   ├── html/
│   │   ├── form_1.html
│   │   ├── form_2.html
│   │   └── ...
│   ├── docx/
│   │   └── ...
│   └── xlsx/
│       └── ...
│
├── goa/                           # Goa state (reference)
│   ├── config.json
│   ├── styles.css
│   ├── html/
│   │   ├── form_1.html           # Goa-specific modifications
│   │   └── ...
│   ├── docx/
│   ├── xlsx/
│   └── assets/
│       └── goa_rera_logo.png
│
├── maharashtra/                   # New state example
│   ├── config.json               # State config
│   ├── styles.css                # State-specific styles
│   ├── html/
│   │   ├── form_1.html          # Can override or use base
│   │   └── ...
│   ├── docx/
│   ├── xlsx/
│   └── assets/
│       └── maharera_logo.png
│
└── karnataka/                     # Future state (placeholder)
    └── ...
```

## 5. State-Specific API Responses

```python
# API endpoints return state-aware data

# GET /api/v1/templates/states
{
    "states": [
        {
            "code": "GOA",
            "name": "Goa",
            "authority_name": "Goa Real Estate Regulatory Authority",
            "is_active": true,
            "forms_available": ["form_1", "form_2", "form_3", "form_4", "form_5", "form_6", "annexure_a"]
        },
        {
            "code": "MAHARASHTRA",
            "name": "Maharashtra",
            "authority_name": "Maharashtra Real Estate Regulatory Authority",
            "is_active": false,
            "forms_available": ["form_1", "form_2", "form_3", "form_4", "form_5", "form_6", "annexure_a"],
            "coming_soon": true
        }
    ]
}

# GET /api/v1/templates/states/GOA/form_1
{
    "template_id": "uuid",
    "state": "GOA",
    "form_type": "form_1",
    "form_name": "Architect's Certificate",
    "version": "2024.1",
    "structure": {
        "sections": [
            {
                "section_id": "project_info",
                "title": "Project Information",
                "fields": [
                    {
                        "field_id": "project_name",
                        "label": "Name of the Project",
                        "type": "text",
                        "required": true
                    },
                    // ... more fields
                ]
            },
            // ... more sections with Goa-specific fields
        ]
    },
    "validation_rules": {
        // Goa-specific validation rules
    }
}
```

## 6. Frontend State Selection

```jsx
// StateSelector.jsx

const StateSelector = ({ value, onChange }) => {
    const [states, setStates] = useState([]);
    
    useEffect(() => {
        // Fetch available states
        api.get('/api/v1/templates/states').then(res => {
            setStates(res.data.states);
        });
    }, []);
    
    return (
        <Select value={value} onValueChange={onChange}>
            <SelectTrigger>
                <SelectValue placeholder="Select State" />
            </SelectTrigger>
            <SelectContent>
                {states.map(state => (
                    <SelectItem 
                        key={state.code} 
                        value={state.code}
                        disabled={!state.is_active}
                    >
                        {state.name}
                        {state.coming_soon && (
                            <Badge variant="secondary" className="ml-2">
                                Coming Soon
                            </Badge>
                        )}
                    </SelectItem>
                ))}
            </SelectContent>
        </Select>
    );
};
```

## 7. State Migration Support

When a state template is updated:

```python
# Template versioning and migration

class TemplateMigration:
    """
    Handle template version migrations
    """
    
    async def migrate_forms_to_new_template(
        self, 
        state: str, 
        form_type: str, 
        from_version: str, 
        to_version: str
    ):
        """
        Migrate existing forms to new template version
        """
        # 1. Get all draft forms using old version
        forms = await db.forms.find({
            "state": state,
            "form_type": form_type,
            "template_version": from_version,
            "status": "draft"
        }).to_list()
        
        # 2. For each form, migrate data
        for form in forms:
            migrated_data = await self._migrate_form_data(
                form["data"],
                from_version,
                to_version
            )
            
            # 3. Update form with new version
            await db.forms.update_one(
                {"form_id": form["form_id"]},
                {
                    "$set": {
                        "data": migrated_data,
                        "template_version": to_version,
                        "migrated_at": datetime.now(timezone.utc)
                    }
                }
            )
```
