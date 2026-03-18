"""Report templates router — CRUD for multi-state RERA report templates."""

from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timezone
from typing import List, Optional
import uuid

from database import db
from models import (
    ReportTemplateBase, ReportTemplateCreate, ReportTemplateResponse
)
from auth import get_current_user

router = APIRouter()


@router.post("/report-templates", response_model=ReportTemplateResponse)
async def create_report_template(
    template: ReportTemplateCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new report template. Admin-only."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    template_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    template_doc = {
        "template_id": template_id,
        **template.model_dump(),
        "created_at": now,
        "updated_at": now,
    }
    await db.report_templates.insert_one(template_doc)
    return ReportTemplateResponse(**{k: v for k, v in template_doc.items() if k != "_id"})


@router.get("/report-templates", response_model=List[ReportTemplateResponse])
async def get_report_templates(
    state: Optional[str] = None,
    report_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all report templates, optionally filtered by state or report_type."""
    query = {}
    if state:
        query["state"] = state
    if report_type:
        query["report_type"] = report_type

    templates = await db.report_templates.find(query, {"_id": 0}).to_list(1000)
    return [ReportTemplateResponse(**t) for t in templates]


@router.get("/report-templates/{template_id}", response_model=ReportTemplateResponse)
async def get_report_template(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific report template by ID."""
    template = await db.report_templates.find_one(
        {"template_id": template_id}, {"_id": 0}
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return ReportTemplateResponse(**template)


@router.put("/report-templates/{template_id}", response_model=ReportTemplateResponse)
async def update_report_template(
    template_id: str,
    template: ReportTemplateCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing report template. Admin-only."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    existing = await db.report_templates.find_one({"template_id": template_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Template not found")

    now = datetime.now(timezone.utc).isoformat()
    update_data = template.model_dump()
    update_data["updated_at"] = now

    await db.report_templates.update_one(
        {"template_id": template_id}, {"$set": update_data}
    )
    updated = await db.report_templates.find_one(
        {"template_id": template_id}, {"_id": 0}
    )
    return ReportTemplateResponse(**updated)


@router.delete("/report-templates/{template_id}")
async def delete_report_template(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a report template. Admin-only."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    result = await db.report_templates.delete_one({"template_id": template_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted"}
