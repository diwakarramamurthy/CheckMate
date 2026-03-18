"""Financial summary router — quarterly RERA financial tracking."""

from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timezone
from typing import List, Optional
import uuid

from database import db
from models import (
    FinancialSummaryCreate, FinancialSummaryResponse
)
from auth import get_current_user

router = APIRouter()


@router.post("/financial-summary", response_model=FinancialSummaryResponse)
async def create_financial_summary(
    summary: FinancialSummaryCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create or update a quarterly financial summary (upsert by project+quarter+year)."""
    summary_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    # Compute derived fields
    unsold_inventory_value = summary.unsold_area_sqm * summary.asr_rate_per_sqm
    amount_to_deposit = (
        summary.total_estimated_receivables * summary.deposit_percentage / 100
    )

    summary_doc = {
        "summary_id": summary_id,
        **summary.model_dump(),
        "unsold_inventory_value": unsold_inventory_value,
        "amount_to_deposit": amount_to_deposit,
        "created_at": now,
    }

    await db.financial_summaries.update_one(
        {
            "project_id": summary.project_id,
            "quarter": summary.quarter,
            "year": summary.year,
        },
        {"$set": summary_doc},
        upsert=True,
    )

    # Return the actual saved doc so summary_id is consistent on updates
    saved = await db.financial_summaries.find_one(
        {
            "project_id": summary.project_id,
            "quarter": summary.quarter,
            "year": summary.year,
        },
        {"_id": 0},
    )
    return FinancialSummaryResponse(**saved)


@router.get("/financial-summary", response_model=List[FinancialSummaryResponse])
async def get_financial_summaries(
    project_id: str = Query(...),
    quarter: Optional[str] = None,
    year: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all financial summaries for a project, optionally filtered by quarter/year."""
    query: dict = {"project_id": project_id}
    if quarter:
        query["quarter"] = quarter
    if year:
        query["year"] = year

    summaries = await db.financial_summaries.find(query, {"_id": 0}).to_list(1000)
    return [FinancialSummaryResponse(**s) for s in summaries]


@router.get("/financial-summary/latest/{project_id}", response_model=FinancialSummaryResponse)
async def get_latest_financial_summary(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the most-recent financial summary for a project."""
    summary = await db.financial_summaries.find_one(
        {"project_id": project_id},
        {"_id": 0},
        sort=[("year", -1), ("quarter", -1)],
    )
    if not summary:
        raise HTTPException(status_code=404, detail="No financial summary data found")
    return FinancialSummaryResponse(**summary)
