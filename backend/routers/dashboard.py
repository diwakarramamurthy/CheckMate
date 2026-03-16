"""Dashboard.Py routes."""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, status, Request
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid
import json
from io import BytesIO

from database import db
from models import (
    DashboardSummary, CommonDevelopmentWorksBase, CommonDevelopmentWorksCreate
)
from auth import get_current_user

router = APIRouter()

@router.get("/dashboard/{project_id}", response_model=DashboardSummary)
async def get_dashboard(project_id: str, current_user: dict = Depends(get_current_user)):
    # Cost summary – computed via shared helper (same logic as Project Costs page)
    cost_summary = await _compute_cost_summary(project_id)
# QUARTERLY REPORTS
@router.post("/quarterly-reports", response_model=QuarterlyReportResponse)
async def create_quarterly_report(report: QuarterlyReportCreate, current_user: dict = Depends(get_current_user)):
    report_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    report_doc = {
        "report_id": report_id,
        **report.model_dump(),
        "created_by": current_user["user_id"],
        "created_at": now
    }
    await db.quarterly_reports.insert_one(report_doc)
    return QuarterlyReportResponse(**{k: v for k, v in report_doc.items() if k != "_id"})
@router.get("/quarterly-reports", response_model=List[QuarterlyReportResponse])
async def get_quarterly_reports(project_id: str = Query(...), current_user: dict = Depends(get_current_user)):
    reports = await db.quarterly_reports.find({"project_id": project_id}, {"_id": 0}).to_list(1000)
    return [QuarterlyReportResponse(**r) for r in reports]
# REPORT TEMPLATES
@router.post("/report-templates", response_model=ReportTemplateResponse)
async def create_report_template(template: ReportTemplateCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
@router.get("/report-templates", response_model=List[ReportTemplateResponse])
async def get_report_templates(state: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    query = {}
    if state:
        query["state"] = state
    templates = await db.report_templates.find(query, {"_id": 0}).to_list(1000)
    return [ReportTemplateResponse(**t) for t in templates]
@router.get("/report-templates/{template_id}", response_model=ReportTemplateResponse)
async def get_report_template(template_id: str, current_user: dict = Depends(get_current_user)):
    template = await db.report_templates.find_one({"template_id": template_id}, {"_id": 0})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return ReportTemplateResponse(**template)
@router.put("/report-templates/{template_id}", response_model=ReportTemplateResponse)
async def update_report_template(template_id: str, template: ReportTemplateCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
# REPORT GENERATION
@router.get("/generate-report/{project_id}/{report_type}")
async def generate_report(
    project_id: str,
    report_type: str,
    quarter: str = Query(...),
    year: int = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """Generate RERA report as HTML (for PDF conversion on frontend)"""
# PDF GENERATION ENDPOINT
@router.get("/generate-pdf/{project_id}/{report_type}")
async def generate_pdf_report(
    project_id: str,
    report_type: str,
    quarter: str = Query(...),
    year: int = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """Generate RERA report as downloadable PDF"""
    from pdf_generator import (
        generate_form1_pdf, 
        generate_form3_pdf, 
        generate_form4_pdf, 
        generate_annexure_a_pdf
    )
# EXCEL GENERATION ENDPOINT
@router.get("/generate-excel/{project_id}/{report_type}")
async def generate_excel_report(
    project_id: str,
    report_type: str,
    quarter: str = Query(...),
    year: int = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """Generate RERA report as downloadable Excel (.xlsx)"""
    from excel_generator import (
        generate_form1_excel,
        generate_form3_excel,
        generate_form4_excel,
        generate_annexure_a_excel,
    )
# WORD GENERATION ENDPOINT
@router.get("/generate-docx/{project_id}/{report_type}")
async def generate_docx_report(
    project_id: str,
    report_type: str,
    quarter: str = Query(...),
    year: int = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """Generate RERA report as downloadable Word document (.docx)"""
    from docx_generator import (
        generate_form1_docx,
        generate_form3_docx,
        generate_form4_docx,
        generate_annexure_a_docx,
    )
def flatten_dict(d, parent_key='', sep='.'):
    """Flatten nested dict"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
# DATA VALIDATION
@router.get("/validate/{project_id}")
async def validate_project_data(project_id: str, current_user: dict = Depends(get_current_user)):
    """Validate project data for RERA compliance"""
    warnings = []
    errors = []
# HEALTH CHECK
