"""Reports.Py routes."""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, status, Request
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid
import json
from io import BytesIO

from database import db
from models import (
    QuarterlyReportBase, QuarterlyReportCreate, QuarterlyReportResponse
)
from auth import get_current_user

router = APIRouter()

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
