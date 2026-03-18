"""Costs.Py routes."""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, status, Request
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid
import json
from io import BytesIO

from database import db
from models import (
    ProjectCostBase, ProjectCostCreate, ProjectCostResponse,
    BuildingCostBase, BuildingCostCreate, BuildingCostResponse,
    InfrastructureCostCreate, EstimatedDevelopmentCostCreate,
    UnitSaleCreate, UnitSaleResponse
)
from auth import get_current_user

router = APIRouter()

async def _compute_cost_summary(project_id: str):
    """
    Compute Estimated Cost, Cost Incurred, and Balance Cost using exactly
    the same logic as the Project Costs page frontend, for the latest
    available quarter.  This is the single source of truth used by both
    the dashboard and the /project-costs/live-summary endpoint.
    """
    # ── Determine latest quarter ────────────────────────────────────────
    latest_cost_rec = await db.project_costs.find_one(
        {"project_id": project_id}, {"_id": 0}, sort=[("year", -1), ("quarter", -1)]
    )
    latest_progress_rec = await db.construction_progress.find_one(
        {"project_id": project_id}, {"_id": 0}, sort=[("year", -1), ("quarter", -1)]
    )
    if latest_cost_rec:
        quarter = latest_cost_rec.get("quarter", "Q1")
        year    = latest_cost_rec.get("year", datetime.now().year)
    elif latest_progress_rec:
        quarter = latest_progress_rec.get("quarter", "Q1")
        year    = latest_progress_rec.get("year", datetime.now().year)
    else:
        quarter = "Q1"
        year    = datetime.now().year

    # ── 1. Land costs ────────────────────────────────────────────────────
    land_doc = await db.land_costs.find_one({"project_id": project_id}, {"_id": 0})
    estimated_land = land_doc.get("estimated", {}).get("total", 0) if land_doc else 0
    actual_land    = land_doc.get("actual",    {}).get("total", 0) if land_doc else 0

    # ── 2. Estimated development cost ────────────────────────────────────
    # Replicate GET /estimated-development-cost/{project_id} exactly:
    # the stored total_estimated_development_cost may be stale, so we
    # recompute it live from its component collections.
    buildings = await db.buildings.find({"project_id": project_id}, {"_id": 0}).to_list(1000)
    buildings_cost_est = sum(b.get("estimated_cost", 0) for b in buildings)

    infra_cost_doc = await db.infrastructure_costs.find_one(
        {"project_id": project_id}, {"_id": 0}
    )
    total_infra_cost     = infra_cost_doc.get("total_infrastructure_cost", 0) if infra_cost_doc else 0

    # Estimated site expenditure (db.site_expenditure, NOT actual_site_expenditure)
    est_site_exp_doc = await db.site_expenditure.find_one({"project_id": project_id}, {"_id": 0})
    est_site_exp_total = (
        (est_site_exp_doc.get("site_development_cost", 0) or 0) +
        (est_site_exp_doc.get("salaries",              0) or 0) +
        (est_site_exp_doc.get("consultants_fee",       0) or 0) +
        (est_site_exp_doc.get("site_overheads",        0) or 0) +
        (est_site_exp_doc.get("services_cost",         0) or 0) +
        (est_site_exp_doc.get("machinery_cost",        0) or 0)
    ) if est_site_exp_doc else 0

    # taxes_premiums_fees and finance_cost are user-entered on the estimate
    est_dev_doc = await db.estimated_development_costs.find_one(
        {"project_id": project_id}, {"_id": 0}
    )
    est_taxes_premiums = est_dev_doc.get("taxes_premiums_fees", 0) if est_dev_doc else 0
    est_finance_cost   = est_dev_doc.get("finance_cost",        0) if est_dev_doc else 0

    estimated_dev = (
        buildings_cost_est + total_infra_cost + est_site_exp_total +
        est_taxes_premiums + est_finance_cost
    )

    # ── 3. Actual construction cost = Σ(building estimated_cost × completion%) ──
    construction_progress = await db.construction_progress.find(
        {"project_id": project_id, "quarter": quarter, "year": year}, {"_id": 0}
    ).to_list(1000)
    progress_map = {p.get("building_id"): p.get("overall_completion", 0) for p in construction_progress}
    actual_construction = sum(
        b.get("estimated_cost", 0) * progress_map.get(b.get("building_id"), 0) / 100
        for b in buildings
    )

    # ── 4. Actual infrastructure cost = infra_total × infra_completion% ──
    # infra_cost_doc and total_infra_cost already fetched above
    infra_progress_doc = await db.infrastructure_progress.find_one(
        {"project_id": project_id, "quarter": quarter, "year": year}, {"_id": 0}
    )
    infra_completion    = infra_progress_doc.get("overall_completion", 0) if infra_progress_doc else 0
    actual_infrastructure = total_infra_cost * infra_completion / 100

    # ── 5. Actual site expenditure for the latest quarter ────────────────
    site_exp_doc = await db.actual_site_expenditure.find_one(
        {"project_id": project_id, "quarter": quarter, "year": year}, {"_id": 0}
    )
    actual_site_exp = site_exp_doc.get("total", 0) if site_exp_doc else 0

    # ── 6. Taxes & finance (user-entered on Project Costs page) ──────────
    taxes_finance = 0
    if latest_cost_rec:
        taxes_finance = (
            latest_cost_rec.get("taxes_statutory", 0) +
            latest_cost_rec.get("finance_cost", 0)
        )

    # ── Totals (mirrors frontend Project Costs page exactly) ─────────────
    total_estimated = estimated_land + estimated_dev
    total_dev_cost  = actual_construction + actual_infrastructure + actual_site_exp + taxes_finance
    total_incurred  = actual_land + total_dev_cost
    balance_cost    = total_estimated - total_incurred

    return {
        "total_estimated_cost": round(total_estimated, 2),
        "total_cost_incurred":  round(total_incurred,  2),
        "balance_cost":         round(balance_cost,    2),
        "latest_quarter": quarter,
        "latest_year":    year,
        # Breakdown for transparency
        "estimated_land":         round(estimated_land,         2),
        "estimated_dev":          round(estimated_dev,          2),
        "actual_land":            round(actual_land,            2),
        "actual_construction":    round(actual_construction,    2),
        "actual_infrastructure":  round(actual_infrastructure,  2),
        "actual_site_exp":        round(actual_site_exp,        2),
        "taxes_finance":          round(taxes_finance,          2),
    }


async def _build_form4_data(
    project_id: str, quarter: str, year: int,
    buildings: list, construction_progress: list,
    project_cost: dict, sales: list
) -> dict:
    """
    Pre-compute every value needed by the Form-4 CA Certificate report.
    Fetches land_costs, site_expenditure, infrastructure collections in-place.
    Returns a flat dict consumed by all three report generators (Excel/PDF/DOCX).
    """
    pc = project_cost or {}

    # ── LAND COSTS (land_costs collection) ──────────────────────────────────
    land_doc    = await db.land_costs.find_one({"project_id": project_id}, {"_id": 0}) or {}
    land_est    = land_doc.get("estimated", {})
    land_inc    = land_doc.get("actual",    {})

    lc_a_est = land_est.get("land_cost", 0)
    lc_a_inc = land_inc.get("land_cost", 0)
    lc_b_est = land_est.get("premium_cost", 0)
    lc_b_inc = land_inc.get("premium_cost", 0)
    lc_c_est = land_est.get("tdr_cost", 0)
    lc_c_inc = land_inc.get("tdr_cost", 0)
    lc_d_est = land_est.get("statutory_cost", 0)
    lc_d_inc = land_inc.get("statutory_cost", 0)
    lc_e_est = land_est.get("land_premium", 0)
    lc_e_inc = land_inc.get("land_premium", 0)

    rehab_i_est   = land_est.get("estimated_rehab_cost", 0)
    rehab_i_inc   = land_inc.get("estimated_rehab_cost", 0)
    rehab_ii_inc  = land_inc.get("actual_rehab_cost", 0)
    rehab_iii_inc = land_inc.get("land_clearance_cost", 0)
    rehab_iv_inc  = land_inc.get("asr_linked_premium", 0)
    rehab_any     = any([rehab_i_inc, rehab_ii_inc, rehab_iii_inc, rehab_iv_inc])

    land_sub_est = lc_a_est + lc_b_est + lc_c_est + lc_d_est + lc_e_est + rehab_i_est
    land_sub_inc = lc_a_inc + lc_b_inc + lc_c_inc + lc_d_inc + lc_e_inc
    if rehab_any:
        land_sub_inc += min(rehab_i_inc, rehab_ii_inc) + rehab_iii_inc + rehab_iv_inc

    # ── DEVELOPMENT / CONSTRUCTION COSTS ────────────────────────────────────
    # a(i)  Estimated construction cost = sum of building estimated costs
    dev_a1_est = sum(b.get("estimated_cost", 0) for b in (buildings or []))

    # a(ii) Actual construction cost = Σ(building_est_cost × completion%)
    prog_map   = {p.get("building_id"): p.get("overall_completion", 0)
                  for p in (construction_progress or [])}
    dev_a2_inc = sum(
        b.get("estimated_cost", 0) * prog_map.get(b.get("building_id"), 0) / 100
        for b in (buildings or [])
    )

    # a(iii) On-site expenditure
    #   Estimated: infrastructure_costs + site_expenditure (salaries, consultants, etc.)
    infra_doc  = await db.infrastructure_costs.find_one({"project_id": project_id}, {"_id": 0}) or {}
    infra_est  = infra_doc.get("total_infrastructure_cost", 0)

    site_exp_doc = await db.site_expenditure.find_one({"project_id": project_id}, {"_id": 0}) or {}
    site_exp_est = (
        (site_exp_doc.get("site_development_cost", 0) or 0) +
        (site_exp_doc.get("salaries",              0) or 0) +
        (site_exp_doc.get("consultants_fee",       0) or 0) +
        (site_exp_doc.get("site_overheads",        0) or 0) +
        (site_exp_doc.get("services_cost",         0) or 0) +
        (site_exp_doc.get("machinery_cost",        0) or 0)
    )
    dev_a3_est = infra_est + site_exp_est

    #   Incurred: infrastructure (est × completion%) + actual_site_expenditure
    infra_prog_doc = await db.infrastructure_progress.find_one(
        {"project_id": project_id, "quarter": quarter, "year": year}, {"_id": 0}
    ) or {}
    infra_completion = infra_prog_doc.get("overall_completion", 0)
    infra_inc        = infra_est * infra_completion / 100

    act_site_doc = await db.actual_site_expenditure.find_one(
        {"project_id": project_id, "quarter": quarter, "year": year}, {"_id": 0}
    ) or {}
    dev_a3_inc = infra_inc + act_site_doc.get("total", 0)

    # b. Taxes, cess, fees to statutory authority
    est_dev_doc = await db.estimated_development_costs.find_one(
        {"project_id": project_id}, {"_id": 0}
    ) or {}
    dev_b_est = est_dev_doc.get("taxes_premiums_fees", 0)
    dev_b_inc = pc.get("taxes_statutory", 0)

    # c. Finance cost
    dev_c_est = est_dev_doc.get("finance_cost", 0)
    dev_c_inc = pc.get("finance_cost", 0)

    # Sub-totals
    dev_sub_est  = dev_a1_est + dev_a3_est + dev_b_est + dev_c_est
    dev_a_for_min = min(dev_a1_est, dev_a2_inc) if dev_a1_est and dev_a2_inc else (dev_a2_inc or 0)
    dev_sub_inc  = dev_a_for_min + dev_a3_inc + dev_b_inc + dev_c_inc

    # ── SUMMARY CALCULATIONS ─────────────────────────────────────────────────
    total_est      = land_sub_est + dev_sub_est
    total_inc      = land_sub_inc + dev_sub_inc

    # % Completion = Total Actual Dev Cost / Total Estimated Dev Cost
    arch_pct       = (dev_sub_inc / dev_sub_est) if dev_sub_est else 0

    proportion     = (total_inc / total_est) if total_est else 0
    withdraw_allow = total_inc   # same as total_est * proportion by definition

    # ── ADDITIONAL INFORMATION (ongoing projects) ────────────────────────────
    bal_cost      = total_est - total_inc

    # Compute receivables directly from sales data
    sold_sales_list   = [s for s in (sales or []) if s.get("buyer_name")]
    unsold_sales_list = [s for s in (sales or []) if not s.get("buyer_name")]

    # Sr 7: Total Sale Amount Received from Sold Units (sum of amount_received)
    total_amount_received_sold = sum(
        (s.get("amount_received", 0) or 0) for s in sold_sales_list
    )
    # Sr 8: Net Amount which can be Withdrawn = Sr 6 (withdraw_allow) - Sr 7
    net_withdraw = withdraw_allow - total_amount_received_sold

    # Balance receivable from sold units = sum of (sale_value - amount_received)
    bal_recv_sold = sum(
        (s.get("sale_value", 0) or 0) - (s.get("amount_received", 0) or 0)
        for s in sold_sales_list
    )

    # Total area of unsold units
    unsold_area = sum((s.get("carpet_area", 0) or 0) for s in unsold_sales_list)

    # Average sale price per sq.m. from sold units
    total_sale_val_sold   = sum((s.get("sale_value", 0) or 0)  for s in sold_sales_list)
    total_carpet_area_sold = sum((s.get("carpet_area", 0) or 0) for s in sold_sales_list)
    avg_sale_price = (total_sale_val_sold / total_carpet_area_sold) if total_carpet_area_sold else 0

    # Estimated value of unsold units = avg sale price × unsold area
    unsold_val = avg_sale_price * unsold_area

    # Total estimated receivables = total sale value of sold units + unsold estimated value
    total_recv = total_sale_val_sold + unsold_val

    # Also keep ASR rate from financial_summaries if available (for display reference)
    fs = await db.financial_summaries.find_one(
        {"project_id": project_id, "quarter": quarter, "year": year}, {"_id": 0}
    )
    if not fs:
        fs = await db.financial_summaries.find_one(
            {"project_id": project_id}, {"_id": 0},
            sort=[("year", -1), ("quarter", -1)]
        )
    fs = fs or {}
    asr_rate = fs.get("asr_rate_per_sqm", 0)

    deposit_pct   = 0.70 if total_recv > bal_cost else 1.00
    deposit_amt   = total_recv * deposit_pct

    building_map  = {b.get("building_id"): b.get("building_name", "") for b in (buildings or [])}

    return {
        # Land cost items
        "lc_a_est": lc_a_est, "lc_a_inc": lc_a_inc,
        "lc_b_est": lc_b_est, "lc_b_inc": lc_b_inc,
        "lc_c_est": lc_c_est, "lc_c_inc": lc_c_inc,
        "lc_d_est": lc_d_est, "lc_d_inc": lc_d_inc,
        "lc_e_est": lc_e_est, "lc_e_inc": lc_e_inc,
        "rehab_i_est": rehab_i_est, "rehab_i_inc": rehab_i_inc,
        "rehab_ii_inc": rehab_ii_inc,
        "rehab_iii_inc": rehab_iii_inc,
        "rehab_iv_inc": rehab_iv_inc,
        "rehab_any": rehab_any,
        "land_sub_est": land_sub_est, "land_sub_inc": land_sub_inc,
        # Development cost items
        "dev_a1_est": dev_a1_est,
        "dev_a2_inc": dev_a2_inc,
        "dev_a3_est": dev_a3_est,
        "dev_a3_inc": dev_a3_inc,
        "dev_b_est": dev_b_est, "dev_b_inc": dev_b_inc,
        "dev_c_est": dev_c_est, "dev_c_inc": dev_c_inc,
        "dev_sub_est": dev_sub_est, "dev_sub_inc": dev_sub_inc,
        # Summary
        "total_est": round(total_est, 2),
        "total_inc": round(total_inc, 2),
        "arch_pct": arch_pct,
        "proportion": proportion,
        "withdraw_allow": round(withdraw_allow, 2),
        "total_amount_received_sold": round(total_amount_received_sold, 2),
        "net_withdraw": round(net_withdraw, 2),
        # Additional info
        "bal_cost": round(bal_cost, 2),
        "bal_recv_sold": round(bal_recv_sold, 2),
        "unsold_area": unsold_area,
        "asr_rate": asr_rate,
        "avg_sale_price": round(avg_sale_price, 2),
        "total_sale_val_sold": round(total_sale_val_sold, 2),
        "unsold_val": round(unsold_val, 2),
        "total_recv": round(total_recv, 2),
        "deposit_pct": deposit_pct,
        "deposit_amt": round(deposit_amt, 2),
        # For Annexure A
        "sales": sales or [],
        "buildings": buildings or [],
        "building_map": building_map,
    }


# ─────────────────────────────────────────────────────────────────────────────
# INFRASTRUCTURE COSTS ROUTES
# ─────────────────────────────────────────────────────────────────────────────

# Canonical list of infrastructure items with their RERA-defined weightages
_INFRA_ITEMS = [
    {"id": "road_footpath_storm_drain",    "name": "Road, Foot-path and storm water drain",            "weightage": 21.5},
    {"id": "underground_sewage_network",   "name": "Underground sewage drainage network",               "weightage": 13.0},
    {"id": "sewage_treatment_plant",       "name": "Sewage Treatment Plant",                            "weightage": 8.5},
    {"id": "overhead_sump_reservoir",      "name": "Over-head and Sump water reservoir/Tank",           "weightage": 8.5},
    {"id": "underground_water_distribution","name": "Under ground water distribution network",          "weightage": 10.5},
    {"id": "electric_substation_cables",   "name": "Electric Substation & Under-ground electric cables","weightage": 10.5},
    {"id": "street_lights",                "name": "Street Lights",                                     "weightage": 4.0},
    {"id": "entry_gate",                   "name": "Entry Gate",                                        "weightage": 2.5},
    {"id": "boundary_wall",                "name": "Boundary wall",                                     "weightage": 6.0},
    {"id": "club_house",                   "name": "Club House",                                        "weightage": 7.0},
    {"id": "swimming_pool",                "name": "Swimming Pool",                                     "weightage": 3.5},
    {"id": "amphitheatre",                 "name": "Amphitheatre",                                      "weightage": 2.5},
    {"id": "gardens_playground",           "name": "Gardens / Play Ground",                             "weightage": 2.0},
]

_INFRA_IDS = [item["id"] for item in _INFRA_ITEMS]


@router.get("/infrastructure-costs/template")
async def get_infrastructure_costs_template(current_user: dict = Depends(get_current_user)):
    """Return the canonical list of infrastructure items with names and weightages."""
    return {"items": _INFRA_ITEMS}


@router.get("/infrastructure-costs/{project_id}")
async def get_infrastructure_costs(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Fetch saved infrastructure cost entries for a project."""
    project = await db.projects.find_one({"project_id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    doc = await db.infrastructure_costs.find_one({"project_id": project_id}, {"_id": 0})
    if not doc:
        return {"project_id": project_id, "costs": {}, "total_infrastructure_cost": 0}

    # Build the costs dict from stored fields, supporting both old (named-field)
    # and new (nested costs dict) storage formats.
    stored_costs = doc.get("costs", None)
    if stored_costs is None:
        # Legacy format: each infra id is a top-level field in the document
        stored_costs = {
            item_id: doc.get(item_id, {"estimated_cost": 0, "is_applicable": True})
            for item_id in _INFRA_IDS
        }

    return {
        "project_id": project_id,
        "costs": stored_costs,
        "total_infrastructure_cost": doc.get("total_infrastructure_cost", 0),
    }


@router.post("/infrastructure-costs")
async def save_infrastructure_costs(
    project_id: str = Query(...),
    body: dict = None,
    request: Request = None,
    current_user: dict = Depends(get_current_user)
):
    """Create or update infrastructure cost data for a project.

    Body is a flat dict keyed by infrastructure item id:
      { "road_footpath_storm_drain": { "estimated_cost": 150000, "is_applicable": true }, ... }
    """
    project = await db.projects.find_one({"project_id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Accept body either as a passed dict or parsed from request JSON
    if body is None and request is not None:
        body = await request.json()
    if body is None:
        body = {}

    # Sanitise and compute total (only applicable items)
    costs: Dict[str, Any] = {}
    total = 0.0
    for item_id in _INFRA_IDS:
        raw = body.get(item_id, {})
        est_cost    = float(raw.get("estimated_cost", 0) or 0)
        is_applicable = raw.get("is_applicable", True)
        if is_applicable is None:
            is_applicable = True
        costs[item_id] = {"estimated_cost": est_cost, "is_applicable": bool(is_applicable)}
        if is_applicable:
            total += est_cost

    doc = {
        "project_id": project_id,
        "costs": costs,
        "total_infrastructure_cost": round(total, 2),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.infrastructure_costs.update_one(
        {"project_id": project_id},
        {"$set": doc},
        upsert=True
    )

    return doc


# ─────────────────────────────────────────────────────────────────────────────
# LAND COST ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/land-cost/{project_id}")
async def get_land_cost(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Fetch land cost data (estimated + actual) for a project."""
    project = await db.projects.find_one({"project_id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    doc = await db.land_costs.find_one({"project_id": project_id}, {"_id": 0})
    if not doc:
        # Return empty structure when no data exists yet
        empty = {
            "land_cost": 0, "premium_cost": 0, "tdr_cost": 0, "statutory_cost": 0,
            "land_premium": 0, "under_rehab_scheme": 0, "estimated_rehab_cost": 0,
            "actual_rehab_cost": 0, "land_clearance_cost": 0, "asr_linked_premium": 0,
            "total": 0
        }
        return {"project_id": project_id, "estimated": empty, "actual": empty}

    return doc


@router.post("/land-cost/{project_id}")
async def save_land_cost(
    project_id: str,
    body: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create or update land cost data for a project."""
    project = await db.projects.find_one({"project_id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    cost_fields = [
        "land_cost", "premium_cost", "tdr_cost", "statutory_cost",
        "land_premium", "under_rehab_scheme", "estimated_rehab_cost",
        "actual_rehab_cost", "land_clearance_cost", "asr_linked_premium"
    ]

    def _clean(section: dict) -> dict:
        cleaned = {f: float(section.get(f) or 0) for f in cost_fields}
        cleaned["total"] = sum(cleaned[f] for f in cost_fields)
        return cleaned

    estimated = _clean(body.get("estimated", {}))
    actual = _clean(body.get("actual", {}))

    doc = {
        "project_id": project_id,
        "estimated": estimated,
        "actual": actual,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.land_costs.update_one(
        {"project_id": project_id},
        {"$set": doc},
        upsert=True
    )

    return doc


@router.get("/project-costs/live-summary/{project_id}")
async def get_project_cost_live_summary(
    project_id: str, current_user: dict = Depends(get_current_user)
):
    """Return cost totals computed the same way as the Project Costs page."""
    return await _compute_cost_summary(project_id)


@router.post("/project-costs", response_model=ProjectCostResponse)
async def create_project_cost(cost: ProjectCostCreate, current_user: dict = Depends(get_current_user)):
    # Calculate Land Cost totals (Section 1.i in Form-4)
    total_land = (
        cost.land_acquisition_cost + cost.land_legal_cost + cost.land_interest_cost +
        cost.development_rights_premium + cost.tdr_cost + cost.stamp_duty + 
        cost.government_charges + cost.land_premium_redevelopment +
        cost.rehab_construction_cost + cost.rehab_transit_accommodation + 
        cost.rehab_clearance_cost + cost.rehab_asr_premium
    )
    
    total_land_estimated = (
        cost.land_acquisition_estimated + cost.development_rights_estimated +
        cost.tdr_estimated + cost.stamp_duty_estimated + cost.government_charges_estimated +
        cost.land_premium_estimated + cost.rehab_construction_estimated
    )
    
    # Calculate Development/Construction Cost totals (Section 1.ii in Form-4)
    total_dev = (
        cost.construction_cost_actual + cost.onsite_salaries + cost.onsite_consultants_fees +
        cost.onsite_site_overheads + cost.onsite_services_cost + cost.onsite_machinery_equipment +
        cost.onsite_consumables + cost.offsite_expenditure + cost.taxes_statutory + cost.finance_cost +
        cost.extra_items_cost
    )
    
    total_dev_estimated = cost.construction_cost_estimated + cost.taxes_statutory_estimated + cost.finance_cost_estimated
    
    # Legacy totals for backward compatibility
    total_estimated = total_land_estimated + total_dev_estimated
    if total_estimated == 0:
        total_estimated = cost.estimated_land_cost + cost.estimated_development_cost
    
    total_incurred = total_land + total_dev
    balance = total_estimated - total_incurred
    
    # Cost completion percentage
    cost_completion = (total_incurred / total_estimated * 100) if total_estimated > 0 else 0
    
    cost_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    cost_doc = {
        "cost_id": cost_id,
        **cost.model_dump(),
        "total_land_cost": total_land,
        "total_land_cost_estimated": total_land_estimated,
        "total_development_cost": total_dev,
        "total_development_cost_estimated": total_dev_estimated,
        "total_estimated_cost": total_estimated,
        "total_cost_incurred": total_incurred,
        "balance_cost": balance,
        "cost_completion_percentage": round(cost_completion, 2),
        "created_at": now
    }
    
    # Upsert
    await db.project_costs.update_one(
        {"project_id": cost.project_id, "quarter": cost.quarter, "year": cost.year},
        {"$set": cost_doc},
        upsert=True
    )
    return ProjectCostResponse(**cost_doc)

@router.get("/project-costs", response_model=List[ProjectCostResponse])
async def get_project_costs(
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
    
    costs = await db.project_costs.find(query, {"_id": 0}).to_list(1000)
    return [ProjectCostResponse(**c) for c in costs]

@router.get("/project-costs/latest/{project_id}", response_model=ProjectCostResponse)
async def get_latest_project_cost(project_id: str, current_user: dict = Depends(get_current_user)):
    cost = await db.project_costs.find_one(
        {"project_id": project_id},
        {"_id": 0},
        sort=[("year", -1), ("quarter", -1)]
    )
    if not cost:
        raise HTTPException(status_code=404, detail="No cost data found")
    return ProjectCostResponse(**cost)

# BUILDING COST ROUTES

@router.post("/building-costs", response_model=BuildingCostResponse)
async def create_building_cost(cost: BuildingCostCreate, current_user: dict = Depends(get_current_user)):
    building = await db.buildings.find_one({"building_id": cost.building_id})
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    
    completion = (cost.cost_incurred / cost.estimated_cost * 100) if cost.estimated_cost > 0 else 0
    balance = cost.estimated_cost - cost.cost_incurred
    
    cost_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    cost_doc = {
        "building_cost_id": cost_id,
        "project_id": building["project_id"],
        **cost.model_dump(),
        "completion_percentage": round(completion, 2),
        "balance_cost": balance,
        "created_at": now
    }
    
    await db.building_costs.update_one(
        {"building_id": cost.building_id, "quarter": cost.quarter, "year": cost.year},
        {"$set": cost_doc},
        upsert=True
    )
    return BuildingCostResponse(**cost_doc)

@router.get("/building-costs", response_model=List[BuildingCostResponse])
async def get_building_costs(
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
    
    costs = await db.building_costs.find(query, {"_id": 0}).to_list(1000)
    return [BuildingCostResponse(**c) for c in costs]

# UNIT SALES ROUTES (Annexure-A)

@router.post("/unit-sales", response_model=UnitSaleResponse)
async def create_unit_sale(sale: UnitSaleCreate, current_user: dict = Depends(get_current_user)):
    sale_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    balance = sale.sale_value - sale.amount_received

