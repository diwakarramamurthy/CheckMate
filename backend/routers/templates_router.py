"""Templates Router.Py routes."""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, status, Request
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid
import json
from io import BytesIO

from database import db
from models import (
    ReportTemplateBase, ReportTemplateCreate, ReportTemplateResponse
)
from auth import get_current_user

router = APIRouter()

@router.post("/financial-summary", response_model=FinancialSummaryResponse)
async def create_financial_summary(summary: FinancialSummaryCreate, current_user: dict = Depends(get_current_user)):
    # Calculate unsold inventory value
    unsold_value = summary.unsold_area_sqm * summary.asr_rate_per_sqm
@router.get("/financial-summary", response_model=List[FinancialSummaryResponse])
async def get_financial_summaries(
    project_id: str = Query(...),
    quarter: Optional[str] = None,
    year: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    query = {"project_id": project_id}
    if quarter:
        query["quarter"] = quarter
    if year:
        query["year"] = year
@router.get("/financial-summary/latest/{project_id}", response_model=FinancialSummaryResponse)
async def get_latest_financial_summary(project_id: str, current_user: dict = Depends(get_current_user)):
    summary = await db.financial_summaries.find_one(
        {"project_id": project_id},
        {"_id": 0},
        sort=[("year", -1), ("quarter", -1)]
    )
    if not summary:
        raise HTTPException(status_code=404, detail="No financial summary data found")
    return FinancialSummaryResponse(**summary)
@router.post("/unit-sales/bulk", response_model=Dict[str, Any])
async def bulk_create_unit_sales(
    project_id: str = Query(...),
    sales: List[UnitSaleBase] = None,
    current_user: dict = Depends(get_current_user)
):
    if not sales:
        raise HTTPException(status_code=400, detail="No sales data provided")
# EXCEL IMPORT
