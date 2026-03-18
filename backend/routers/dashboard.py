"""Dashboard router — project overview & RERA compliance validation."""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from typing import List, Dict, Any

from database import db
from models import DashboardSummary
from auth import get_current_user

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/dashboard/{project_id}", response_model=DashboardSummary)
async def get_dashboard(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Return a consolidated project dashboard summary for the latest available quarter."""
    project = await db.projects.find_one({"project_id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # ── Determine latest quarter ─────────────────────────────────────────
    latest_cost = await db.project_costs.find_one(
        {"project_id": project_id}, {"_id": 0}, sort=[("year", -1), ("quarter", -1)]
    )
    latest_progress = await db.construction_progress.find_one(
        {"project_id": project_id}, {"_id": 0}, sort=[("year", -1), ("quarter", -1)]
    )
    if latest_cost:
        quarter = latest_cost.get("quarter", "Q1")
        year = latest_cost.get("year", datetime.now().year)
    elif latest_progress:
        quarter = latest_progress.get("quarter", "Q1")
        year = latest_progress.get("year", datetime.now().year)
    else:
        quarter = "Q1"
        year = datetime.now().year

    # ── Buildings & units ───────────────────────────────────────────────
    buildings = await db.buildings.find({"project_id": project_id}, {"_id": 0}).to_list(100)
    building_config_units = sum(b.get("units", 0) for b in buildings)

    # ── Sales data ──────────────────────────────────────────────────────
    unit_sales = await db.unit_sales.find({"project_id": project_id}, {"_id": 0}).to_list(10000)
    total_units = building_config_units
    sales_data_units = len(unit_sales)
    units_sold = sum(1 for s in unit_sales if s.get("is_sold", True))
    total_sales_value = sum(s.get("sale_value", 0) for s in unit_sales if s.get("is_sold", True))
    amount_collected = sum(s.get("amount_received", 0) for s in unit_sales if s.get("is_sold", True))
    receivables = total_sales_value - amount_collected

    # ── Land cost ───────────────────────────────────────────────────────
    land_doc = await db.land_costs.find_one({"project_id": project_id}, {"_id": 0})
    estimated_land = land_doc.get("estimated", {}).get("total", 0) if land_doc else 0
    actual_land = land_doc.get("actual", {}).get("total", 0) if land_doc else 0

    # ── Estimated development cost ──────────────────────────────────────
    edc_doc = await db.estimated_development_costs.find_one(
        {"project_id": project_id}, {"_id": 0}
    )
    if edc_doc:
        estimated_dev = edc_doc.get("total_estimated_development_cost", 0)
    else:
        estimated_dev = sum(b.get("estimated_cost", 0) for b in buildings)

    total_estimated_cost = estimated_land + estimated_dev

    # ── Actual costs incurred ───────────────────────────────────────────
    building_cost_total = 0
    for b in buildings:
        bc = await db.building_costs.find_one(
            {"building_id": b["building_id"], "quarter": quarter, "year": year},
            {"_id": 0},
        )
        if bc:
            building_cost_total += bc.get("cost_incurred", 0) + bc.get("extra_items_cost", 0)

    project_cost_doc = await db.project_costs.find_one(
        {"project_id": project_id, "quarter": quarter, "year": year}, {"_id": 0}
    )
    onsite_costs = 0
    if project_cost_doc:
        onsite_fields = [
            "onsite_salaries", "onsite_consultants_fees", "onsite_site_overheads",
            "onsite_services_cost", "onsite_machinery_equipment", "onsite_consumables",
            "offsite_expenditure", "taxes_statutory", "finance_cost", "extra_items_cost",
        ]
        onsite_costs = sum(project_cost_doc.get(f, 0) for f in onsite_fields)

    cost_incurred = actual_land + building_cost_total + onsite_costs
    balance_cost = max(0, total_estimated_cost - cost_incurred)
    cost_completion_pct = (cost_incurred / total_estimated_cost * 100) if total_estimated_cost > 0 else 0

    # ── Construction completion ─────────────────────────────────────────
    infra_doc = await db.infrastructure_progress.find_one(
        {"project_id": project_id, "quarter": quarter, "year": year}, {"_id": 0}
    )
    infra_completion = infra_doc.get("overall_completion", 0) if infra_doc else 0

    tower_completions = []
    for b in buildings:
        cp = await db.construction_progress.find_one(
            {"building_id": b["building_id"], "quarter": quarter, "year": year},
            {"_id": 0},
        )
        if cp:
            tower_completions.append(cp.get("overall_completion", 0))

    avg_tower = sum(tower_completions) / len(tower_completions) if tower_completions else 0
    project_completion = (avg_tower * 0.7 + infra_completion * 0.3) if tower_completions else infra_completion

    # ── RERA deposit (70 % rule) ────────────────────────────────────────
    financial_summary = await db.financial_summaries.find_one(
        {"project_id": project_id, "quarter": quarter, "year": year}, {"_id": 0}
    )
    rera_deposit_required = 0
    unsold_inventory_value = 0
    if financial_summary:
        rera_deposit_required = financial_summary.get("amount_to_deposit", 0)
        unsold_inventory_value = financial_summary.get("unsold_inventory_value", 0)

    # ── Inventory mismatch check ────────────────────────────────────────
    inventory_mismatch = building_config_units != sales_data_units
    inventory_mismatch_delta = abs(building_config_units - sales_data_units)

    return DashboardSummary(
        project_completion_percentage=round(project_completion, 2),
        total_estimated_cost=total_estimated_cost,
        cost_incurred=cost_incurred,
        balance_cost=balance_cost,
        total_sales_value=total_sales_value,
        amount_collected=amount_collected,
        receivables=receivables,
        unsold_inventory_value=unsold_inventory_value,
        rera_deposit_required=rera_deposit_required,
        total_units=total_units,
        units_sold=units_sold,
        building_config_units=building_config_units,
        sales_data_units=sales_data_units,
        inventory_mismatch=inventory_mismatch,
        inventory_mismatch_delta=inventory_mismatch_delta,
    )


# ─────────────────────────────────────────────────────────────────────────────
# RERA COMPLIANCE VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/validate/{project_id}")
async def validate_project_data(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Validate project data for RERA compliance and return warnings/errors."""
    project = await db.projects.find_one({"project_id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    warnings: List[str] = []
    errors: List[str] = []

    # Required project fields
    required_fields = [
        ("rera_number", "RERA Number"),
        ("promoter_name", "Promoter Name"),
        ("promoter_address", "Promoter Address"),
        ("project_address", "Project Address"),
        ("rera_registration_date", "RERA Registration Date"),
        ("rera_validity_date", "RERA Validity Date"),
    ]
    for field, label in required_fields:
        if not project.get(field):
            errors.append(f"Missing required field: {label}")

    # Buildings check
    buildings = await db.buildings.find({"project_id": project_id}, {"_id": 0}).to_list(100)
    if not buildings:
        errors.append("No buildings configured for this project")
    else:
        for b in buildings:
            if b.get("units", 0) == 0:
                warnings.append(f"Building '{b.get('building_name')}' has 0 units configured")

    # Sales vs building units mismatch
    unit_sales = await db.unit_sales.find({"project_id": project_id}, {"_id": 0}).to_list(10000)
    building_units = sum(b.get("units", 0) for b in buildings)
    if unit_sales and len(unit_sales) > building_units:
        warnings.append(
            f"Sales records ({len(unit_sales)}) exceed total building units ({building_units})"
        )

    # Financial summary check
    financial_summary = await db.financial_summaries.find_one(
        {"project_id": project_id}, {"_id": 0}
    )
    if not financial_summary:
        warnings.append("No financial summary data found — RERA deposit tracking incomplete")

    # Designated bank account
    if not project.get("designated_bank_name") or not project.get("designated_account_number"):
        warnings.append("Designated bank account details incomplete")

    return {
        "project_id": project_id,
        "project_name": project.get("project_name"),
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }
