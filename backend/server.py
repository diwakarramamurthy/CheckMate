"""CheckMate - RERA Manager API - Main entry point with router configuration."""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import logging
import uuid
from datetime import datetime, timezone

# Import database and models
from database import db, client
from models import APARTMENT_CLASSIFICATIONS

# Import routers
from routers.auth_router import router as auth_router
from routers.projects import router as projects_router
from routers.buildings import router as buildings_router
from routers.construction import router as construction_router
from routers.costs import router as costs_router
from routers.sales import router as sales_router
from routers.financial import router as financial_router
from routers.templates_router import router as templates_router
from routers.reports import router as reports_router
from routers.dashboard import router as dashboard_router

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the main app
app = FastAPI(title="CheckMate - RERA Manager API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
app.include_router(auth_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(buildings_router, prefix="/api")
app.include_router(construction_router, prefix="/api")
app.include_router(costs_router, prefix="/api")
app.include_router(sales_router, prefix="/api")
app.include_router(financial_router, prefix="/api")
app.include_router(templates_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")

# Root and health check endpoints
@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "service": "CheckMate - RERA Manager API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Startup and shutdown events
@app.on_event("startup")
async def startup():
    """Initialize database and templates on startup."""
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("user_id", unique=True)
    await db.projects.create_index("project_id", unique=True)
    await db.buildings.create_index("building_id", unique=True)
    await db.unit_sales.create_index("sale_id", unique=True)
    await db.report_templates.create_index([("state", 1), ("report_type", 1)])

    # Initialize default report templates for GOA
    existing = await db.report_templates.find_one({"state": "GOA"})
    if not existing:
        await initialize_goa_templates()

    logger.info("CheckMate - RERA Manager API started")

async def initialize_goa_templates():
    """Initialize default Goa RERA report templates."""
    templates = [
        {
            "template_id": str(uuid.uuid4()),
            "state": "GOA",
            "report_name": "Form-1: Architect Certificate",
            "report_type": "form-1",
            "template_html": GOA_FORM_1_TEMPLATE,
            "data_mapping": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "template_id": str(uuid.uuid4()),
            "state": "GOA",
            "report_name": "Form-2: Architect Completion Certificate",
            "report_type": "form-2",
            "template_html": GOA_FORM_2_TEMPLATE,
            "data_mapping": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "template_id": str(uuid.uuid4()),
            "state": "GOA",
            "report_name": "Form-3: Engineer Certificate",
            "report_type": "form-3",
            "template_html": GOA_FORM_3_TEMPLATE,
            "data_mapping": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "template_id": str(uuid.uuid4()),
            "state": "GOA",
            "report_name": "Form-4: CA Certificate",
            "report_type": "form-4",
            "template_html": GOA_FORM_4_TEMPLATE,
            "data_mapping": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "template_id": str(uuid.uuid4()),
            "state": "GOA",
            "report_name": "Form-5: CA Compliance Certificate",
            "report_type": "form-5",
            "template_html": GOA_FORM_5_TEMPLATE,
            "data_mapping": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "template_id": str(uuid.uuid4()),
            "state": "GOA",
            "report_name": "Form-6: Auditor Certificate",
            "report_type": "form-6",
            "template_html": GOA_FORM_6_TEMPLATE,
            "data_mapping": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "template_id": str(uuid.uuid4()),
            "state": "GOA",
            "report_name": "Annexure-A: Statement of Receivables",
            "report_type": "annexure-a",
            "template_html": GOA_ANNEXURE_A_TEMPLATE,
            "data_mapping": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]

    for template in templates:
        await db.report_templates.insert_one(template)

    logger.info("Initialized Goa RERA templates")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on shutdown."""
    client.close()

# =========================
# GOA RERA TEMPLATES
# =========================

GOA_FORM_1_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.6; padding: 40px; }
.header { text-align: center; margin-bottom: 30px; }
.title { font-size: 16pt; font-weight: bold; margin-bottom: 10px; }
.subtitle { font-size: 14pt; margin-bottom: 20px; }
table { width: 100%; border-collapse: collapse; margin: 20px 0; }
th, td { border: 1px solid #000; padding: 8px; text-align: left; }
th { background-color: #f0f0f0; }
.signature { margin-top: 50px; }
.form-section { margin: 20px 0; }
</style>
</head>
<body>
<div class="header">
<div class="title">GOA REAL ESTATE REGULATORY AUTHORITY</div>
<div class="subtitle">FORM - 1</div>
<div class="subtitle">ARCHITECT'S CERTIFICATE</div>
<div>(Percentage of Completion)</div>
</div>

<div class="form-section">
<p><strong>Project Name:</strong> {{project.project_name}}</p>
<p><strong>RERA Registration No:</strong> {{project.rera_number}}</p>
<p><strong>Quarter:</strong> {{quarter}} {{year}}</p>
<p><strong>Report Date:</strong> {{report_date}}</p>
</div>

<div class="form-section">
<p>I, {{project.architect_name}}, Architect, having License No. {{project.architect_license}},
hereby certify that the construction of the project mentioned above is progressing as per the sanctioned plans
and the percentage of completion is as follows:</p>
</div>

<table>
<tr>
<th>Sr. No.</th>
<th>Building/Wing</th>
<th>Activity</th>
<th>Weightage (%)</th>
<th>Completion (%)</th>
<th>Weighted Completion (%)</th>
</tr>
<!-- Building data will be populated here -->
</table>

<div class="signature">
<p>Date: {{report_date}}</p>
<p>Place: {{project.district}}, {{project.state}}</p>
<br><br>
<p>_____________________________</p>
<p>{{project.architect_name}}</p>
<p>Architect</p>
<p>License No: {{project.architect_license}}</p>
</div>
</body>
</html>
"""

GOA_FORM_2_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.6; padding: 40px; }
.header { text-align: center; margin-bottom: 30px; }
.title { font-size: 16pt; font-weight: bold; margin-bottom: 10px; }
.subtitle { font-size: 14pt; margin-bottom: 20px; }
table { width: 100%; border-collapse: collapse; margin: 20px 0; }
th, td { border: 1px solid #000; padding: 8px; text-align: left; }
th { background-color: #f0f0f0; }
.signature { margin-top: 50px; }
</style>
</head>
<body>
<div class="header">
<div class="title">GOA REAL ESTATE REGULATORY AUTHORITY</div>
<div class="subtitle">FORM - 2</div>
<div class="subtitle">ARCHITECT'S COMPLETION CERTIFICATE</div>
</div>

<div class="form-section">
<p><strong>Project Name:</strong> {{project.project_name}}</p>
<p><strong>RERA Registration No:</strong> {{project.rera_number}}</p>
</div>

<table>
<tr>
<th>Sr. No.</th>
<th>Building/Wing Name</th>
<th>Completion Cert. No.</th>
<th>Completion Cert. Date</th>
<th>Occupancy Cert. No.</th>
<th>Occupancy Cert. Date</th>
</tr>
<!-- Building completion data -->
</table>

<div class="signature">
<p>Date: {{report_date}}</p>
<p>Place: {{project.district}}, {{project.state}}</p>
<br><br>
<p>_____________________________</p>
<p>{{project.architect_name}}</p>
<p>Architect</p>
</div>
</body>
</html>
"""

GOA_FORM_3_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.6; padding: 40px; }
.header { text-align: center; margin-bottom: 30px; }
.title { font-size: 16pt; font-weight: bold; margin-bottom: 10px; }
table { width: 100%; border-collapse: collapse; margin: 20px 0; }
th, td { border: 1px solid #000; padding: 8px; text-align: left; }
th { background-color: #f0f0f0; }
.signature { margin-top: 50px; }
</style>
</head>
<body>
<div class="header">
<div class="title">GOA REAL ESTATE REGULATORY AUTHORITY</div>
<div class="title">FORM - 3</div>
<div class="title">ENGINEER'S CERTIFICATE</div>
</div>

<p><strong>Project:</strong> {{project.project_name}}</p>
<p><strong>RERA Registration No:</strong> {{project.rera_number}}</p>
<p><strong>Quarter:</strong> {{quarter}} {{year}}</p>

<table>
<tr>
<th>Building</th>
<th>Estimated Cost</th>
<th>Actual Cost (Incurred)</th>
<th>% Complete</th>
</tr>
<!-- Cost data -->
</table>

<div class="signature">
<p>Date: {{report_date}}</p>
<p>_____________________________</p>
<p>{{project.engineer_name}}</p>
<p>Engineer</p>
</div>
</body>
</html>
"""

GOA_FORM_4_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: 'Times New Roman', serif; font-size: 11pt; line-height: 1.4; padding: 30px; }
.header { text-align: center; margin-bottom: 20px; }
.title { font-size: 14pt; font-weight: bold; }
table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 10pt; }
th, td { border: 1px solid #000; padding: 4px; text-align: left; }
th { background-color: #e0e0e0; }
.section-title { font-weight: bold; margin-top: 15px; margin-bottom: 5px; }
.amount { text-align: right; }
</style>
</head>
<body>
<div class="header">
<div class="title">FORM-4: CA CERTIFICATE</div>
<p>Project: {{project.project_name}}</p>
<p>Quarter: {{quarter}} {{year}}</p>
</div>

<div class="section-title">LAND COSTS (Estimated vs Incurred)</div>
<table>
<tr><th>Item</th><th class="amount">Estimated</th><th class="amount">Incurred</th></tr>
<tr><td>Land Acquisition</td><td class="amount">{{lc_a_est}}</td><td class="amount">{{lc_a_inc}}</td></tr>
<tr><td>Total</td><td class="amount">{{land_sub_est}}</td><td class="amount">{{land_sub_inc}}</td></tr>
</table>

<div class="section-title">DEVELOPMENT COSTS</div>
<table>
<tr><th>Item</th><th class="amount">Estimated</th><th class="amount">Incurred</th></tr>
<tr><td>Construction Cost</td><td class="amount">{{dev_a1_est}}</td><td class="amount">{{dev_a2_inc}}</td></tr>
<tr><td>Taxes & Statutory</td><td class="amount">{{dev_b_est}}</td><td class="amount">{{dev_b_inc}}</td></tr>
<tr><td>Finance Cost</td><td class="amount">{{dev_c_est}}</td><td class="amount">{{dev_c_inc}}</td></tr>
<tr><td>Total</td><td class="amount">{{dev_sub_est}}</td><td class="amount">{{dev_sub_inc}}</td></tr>
</table>

<div class="signature" style="margin-top: 40px;">
<p>Date: {{report_date}}</p>
<p>_____________________________</p>
<p>{{project.ca_name}}</p>
<p>Chartered Accountant</p>
</div>
</body>
</html>
"""

GOA_FORM_5_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: 'Times New Roman', serif; font-size: 11pt; padding: 30px; }
table { width: 100%; border-collapse: collapse; margin: 15px 0; }
th, td { border: 1px solid #000; padding: 6px; text-align: left; }
th { background-color: #e0e0e0; }
.title { text-align: center; font-weight: bold; margin-bottom: 20px; }
.section { margin: 20px 0; }
</style>
</head>
<body>
<div class="title">FORM-5: FINANCIAL SUMMARY (ONGOING PROJECTS)</div>
<p><strong>Project:</strong> {{project.project_name}} | <strong>Quarter:</strong> {{quarter}} {{year}}</p>

<div class="section">
<h3>Designated Account Statement</h3>
<table>
<tr><td><strong>Opening Balance</strong></td><td>{{designated_account_opening_balance}}</td></tr>
<tr><td><strong>Amount Deposited This Quarter</strong></td><td>{{amount_deposited_this_quarter}}</td></tr>
<tr><td><strong>Amount Withdrawn This Quarter</strong></td><td>{{amount_withdrawn_this_quarter}}</td></tr>
<tr><td><strong>Closing Balance</strong></td><td>{{designated_account_closing_balance}}</td></tr>
</table>
</div>

<div class="signature" style="margin-top: 40px;">
<p>Date: {{report_date}}</p>
<p>_____________________________</p>
<p>{{project.ca_name}}</p>
<p>Chartered Accountant</p>
</div>
</body>
</html>
"""

GOA_FORM_6_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: 'Times New Roman', serif; font-size: 11pt; padding: 30px; }
table { width: 100%; border-collapse: collapse; margin: 15px 0; }
th, td { border: 1px solid #000; padding: 6px; }
th { background-color: #e0e0e0; }
.title { text-align: center; font-weight: bold; margin-bottom: 20px; font-size: 14pt; }
.amount { text-align: right; }
</style>
</head>
<body>
<div class="title">FORM-6: ANNUAL AUDITOR'S CERTIFICATE</div>
<p><strong>Project:</strong> {{project.project_name}} | <strong>Year:</strong> {{year}}</p>

<table>
<tr>
<th>Particulars</th>
<th class="amount">Amount</th>
</tr>
<tr>
<td>Amount Collected This Year</td>
<td class="amount">{{amount_collected_this_year}}</td>
</tr>
<tr>
<td>Amount Collected Till Date</td>
<td class="amount">{{amount_collected_till_date}}</td>
</tr>
<tr>
<td>Amount Withdrawn This Year</td>
<td class="amount">{{amount_withdrawn_this_year}}</td>
</tr>
</table>

<div class="signature" style="margin-top: 40px;">
<p>Date: {{report_date}}</p>
<p>_____________________________</p>
<p>{{project.auditor_name}}</p>
<p>Auditor</p>
</div>
</body>
</html>
"""

GOA_ANNEXURE_A_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: 'Times New Roman', serif; font-size: 11pt; padding: 30px; }
.title { text-align: center; font-weight: bold; margin-bottom: 20px; font-size: 14pt; }
table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 10pt; }
th, td { border: 1px solid #000; padding: 4px; text-align: left; }
th { background-color: #e0e0e0; }
.amount { text-align: right; }
</style>
</head>
<body>
<div class="title">ANNEXURE - A: STATEMENT OF RECEIVABLES</div>
<p><strong>Project:</strong> {{project.project_name}} | <strong>Date:</strong> {{report_date}}</p>

<table>
<tr>
<th>Unit No.</th>
<th>Building</th>
<th class="amount">Carpet Area</th>
<th class="amount">Sale Value</th>
<th class="amount">Amount Received</th>
<th class="amount">Balance Receivable</th>
</tr>
<tr>
<td colspan="5"><strong>Total Sold Units</strong></td>
<td class="amount">{{total_balance_receivable_sold}}</td>
</tr>
<tr>
<td colspan="5"><strong>Unsold Area (Sqm)</strong></td>
<td class="amount">{{unsold_area_sqm}}</td>
</tr>
<tr>
<td colspan="5"><strong>Unsold Estimated Value (@{{asr_rate_per_sqm}}/sqm)</strong></td>
<td class="amount">{{receivables}}</td>
</tr>
</table>

<div class="signature" style="margin-top: 40px;">
<p>Date: {{report_date}}</p>
<p>Place: {{project.district}}, {{project.state}}</p>
<br><br>
<p>_____________________________</p>
<p>{{project.promoter_name}}</p>
<p>Promoter/Developer</p>
</div>
</body>
</html>
"""
