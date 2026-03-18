"""Report generation router — RERA quarterly reports (HTML / PDF / Excel / Word)."""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse, JSONResponse
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import uuid
from io import BytesIO

from database import db
from models import (
    QuarterlyReportCreate, QuarterlyReportResponse
)
from auth import get_current_user

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# QUARTERLY REPORT TRACKING
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/quarterly-reports", response_model=QuarterlyReportResponse)
async def create_quarterly_report(
    report: QuarterlyReportCreate,
    current_user: dict = Depends(get_current_user)
):
    """Record a new quarterly report entry."""
    report_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    report_doc = {
        "report_id": report_id,
        **report.model_dump(),
        "created_by": current_user["user_id"],
        "created_at": now,
    }
    await db.quarterly_reports.insert_one(report_doc)
    return QuarterlyReportResponse(**{k: v for k, v in report_doc.items() if k != "_id"})


@router.get("/quarterly-reports", response_model=List[QuarterlyReportResponse])
async def get_quarterly_reports(
    project_id: str = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """List all quarterly reports for a project."""
    reports = await db.quarterly_reports.find(
        {"project_id": project_id}, {"_id": 0}
    ).to_list(1000)
    return [QuarterlyReportResponse(**r) for r in reports]


# ─────────────────────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────────────────────

def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """Recursively flatten a nested dictionary."""
    items: list = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


VALID_REPORT_TYPES = {"form1", "form3", "form4", "annexure_a"}


async def _gather_report_data(project_id: str, quarter: str, year: int) -> dict:
    """Collect all data needed to render any RERA report."""
    project = await db.projects.find_one({"project_id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    buildings = await db.buildings.find({"project_id": project_id}, {"_id": 0}).to_list(100)
    unit_sales = await db.unit_sales.find({"project_id": project_id}, {"_id": 0}).to_list(10000)

    construction_progress = await db.construction_progress.find(
        {"project_id": project_id, "quarter": quarter, "year": year}, {"_id": 0}
    ).to_list(100)

    infra_progress = await db.infrastructure_progress.find_one(
        {"project_id": project_id, "quarter": quarter, "year": year}, {"_id": 0}
    )

    project_costs = await db.project_costs.find_one(
        {"project_id": project_id, "quarter": quarter, "year": year}, {"_id": 0}
    )

    financial_summary = await db.financial_summaries.find_one(
        {"project_id": project_id, "quarter": quarter, "year": year}, {"_id": 0}
    )

    land_cost = await db.land_costs.find_one({"project_id": project_id}, {"_id": 0})

    return {
        "project": project,
        "buildings": buildings,
        "unit_sales": unit_sales,
        "construction_progress": construction_progress,
        "infrastructure_progress": infra_progress or {},
        "project_costs": project_costs or {},
        "financial_summary": financial_summary or {},
        "land_cost": land_cost or {},
        "quarter": quarter,
        "year": year,
        "report_date": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# HTML REPORT (for frontend PDF conversion)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/generate-report/{project_id}/{report_type}")
async def generate_report(
    project_id: str,
    report_type: str,
    quarter: str = Query(...),
    year: int = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """Generate RERA report as JSON data (for frontend PDF/HTML rendering)."""
    if report_type not in VALID_REPORT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid report_type. Valid types: {sorted(VALID_REPORT_TYPES)}"
        )
    data = await _gather_report_data(project_id, quarter, year)
    return JSONResponse(content={"report_type": report_type, "data": data})


# ─────────────────────────────────────────────────────────────────────────────
# PDF REPORT
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/generate-pdf/{project_id}/{report_type}")
async def generate_pdf_report(
    project_id: str,
    report_type: str,
    quarter: str = Query(...),
    year: int = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """Generate RERA report as a downloadable PDF."""
    if report_type not in VALID_REPORT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid report_type. Valid types: {sorted(VALID_REPORT_TYPES)}"
        )

    from pdf_generator import (
        generate_form1_pdf,
        generate_form3_pdf,
        generate_form4_pdf,
        generate_annexure_a_pdf,
    )

    data = await _gather_report_data(project_id, quarter, year)
    generators = {
        "form1": generate_form1_pdf,
        "form3": generate_form3_pdf,
        "form4": generate_form4_pdf,
        "annexure_a": generate_annexure_a_pdf,
    }

    pdf_bytes: BytesIO = generators[report_type](data)
    filename = f"RERA_{report_type.upper()}_{data['project']['rera_number']}_{quarter}_{year}.pdf"

    return StreamingResponse(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ─────────────────────────────────────────────────────────────────────────────
# EXCEL REPORT
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/generate-excel/{project_id}/{report_type}")
async def generate_excel_report(
    project_id: str,
    report_type: str,
    quarter: str = Query(...),
    year: int = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """Generate RERA report as a downloadable Excel (.xlsx)."""
    if report_type not in VALID_REPORT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid report_type. Valid types: {sorted(VALID_REPORT_TYPES)}"
        )

    from excel_generator import (
        generate_form1_excel,
        generate_form3_excel,
        generate_form4_excel,
        generate_annexure_a_excel,
    )

    data = await _gather_report_data(project_id, quarter, year)
    generators = {
        "form1": generate_form1_excel,
        "form3": generate_form3_excel,
        "form4": generate_form4_excel,
        "annexure_a": generate_annexure_a_excel,
    }

    xlsx_bytes: BytesIO = generators[report_type](data)
    filename = f"RERA_{report_type.upper()}_{data['project']['rera_number']}_{quarter}_{year}.xlsx"

    return StreamingResponse(
        xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ─────────────────────────────────────────────────────────────────────────────
# WORD REPORT
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/generate-docx/{project_id}/{report_type}")
async def generate_docx_report(
    project_id: str,
    report_type: str,
    quarter: str = Query(...),
    year: int = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """Generate RERA report as a downloadable Word document (.docx)."""
    if report_type not in VALID_REPORT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid report_type. Valid types: {sorted(VALID_REPORT_TYPES)}"
        )

    from docx_generator import (
        generate_form1_docx,
        generate_form3_docx,
        generate_form4_docx,
        generate_annexure_a_docx,
    )

    data = await _gather_report_data(project_id, quarter, year)
    generators = {
        "form1": generate_form1_docx,
        "form3": generate_form3_docx,
        "form4": generate_form4_docx,
        "annexure_a": generate_annexure_a_docx,
    }

    docx_bytes: BytesIO = generators[report_type](data)
    filename = f"RERA_{report_type.upper()}_{data['project']['rera_number']}_{quarter}_{year}.docx"

    return StreamingResponse(
        docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
