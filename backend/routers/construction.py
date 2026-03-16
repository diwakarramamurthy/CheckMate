"""Construction progress routes — tower and infrastructure tracking."""

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from datetime import datetime, timezone
from typing import List, Optional
import uuid

from database import db
from models import (
    ConstructionProgressCreate, ConstructionProgressResponse,
)
from auth import get_current_user

router = APIRouter()


# =========================
# SIMPLE CONSTRUCTION PROGRESS (legacy)
# =========================

@router.post("/construction-progress", response_model=ConstructionProgressResponse)
async def create_construction_progress(
    progress: ConstructionProgressCreate,
    current_user: dict = Depends(get_current_user)
):
    building = await db.buildings.find_one({"building_id": progress.building_id})
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    total_weighted = sum(a.weightage * a.completion_percentage / 100 for a in progress.activities)
    overall_completion = total_weighted

    progress_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    progress_doc = {
        "progress_id": progress_id,
        "project_id": building["project_id"],
        "building_id": progress.building_id,
        "quarter": progress.quarter,
        "year": progress.year,
        "activities": [a.model_dump() for a in progress.activities],
        "overall_completion": overall_completion,
        "created_at": now
    }

    await db.construction_progress.update_one(
        {"building_id": progress.building_id, "quarter": progress.quarter, "year": progress.year},
        {"$set": progress_doc},
        upsert=True
    )
    return ConstructionProgressResponse(**progress_doc)


@router.get("/construction-progress", response_model=List[ConstructionProgressResponse])
async def get_construction_progress(
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

    progress_list = await db.construction_progress.find(query, {"_id": 0}).to_list(1000)
    return [ConstructionProgressResponse(**p) for p in progress_list]


@router.get("/construction-progress/default-activities")
async def get_default_activities():
    return []


# =========================
# DETAILED TEMPLATE
# =========================

@router.get("/construction-progress/detailed-template")
async def get_detailed_construction_template():
    """Returns the comprehensive construction progress tracking template."""
    return {
        "tower_construction": {
            "total_weightage": 100,
            "categories": [
                {
                    "id": "basement_slab_completion",
                    "name": "Completion of Basement Slabs (Below Plinth)",
                    "total_weightage": 0,
                    "note": "Default 0% weightage — adjust using editable weightage inputs",
                    "activities": [
                        {"id": "reinforcement_lintel_roof", "name": "Reinforcement up to Lintel/Roof bottom", "weightage": 0},
                        {"id": "shuttering_for_column", "name": "Shuttering for Column", "weightage": 0},
                        {"id": "concreting_for_column", "name": "Concreting for Column", "weightage": 0},
                        {"id": "shuttering_beams_roof", "name": "Shuttering for Beams and Roof", "weightage": 0},
                        {"id": "reinforcement_beams_roof", "name": "Reinforcement for Beams and Roof", "weightage": 0},
                        {"id": "concreting_beams_roof", "name": "Concreting for Beams and Roof", "weightage": 0},
                        {"id": "dismantling_roof_shuttering", "name": "Dismantling of Roof Shuttering", "weightage": 0}
                    ]
                },
                {
                    "id": "plinth_completion",
                    "name": "Completion of Plinth",
                    "total_weightage": 10.89,
                    "activities": [
                        {"id": "excavation", "name": "Excavation", "weightage": 0.90},
                        {"id": "pcc_below_footing", "name": "PCC below footing", "weightage": 0.80},
                        {"id": "shuttering_for_footing", "name": "Shuttering for Footing", "weightage": 0.90},
                        {"id": "reinforcement_footing_column", "name": "Reinforcement for Footing and Column", "weightage": 1.70},
                        {"id": "concreting_for_footing", "name": "Concreting for Footing", "weightage": 1.50},
                        {"id": "shuttering_column_to_plinth", "name": "Shuttering for Column up to Plinth", "weightage": 0.50},
                        {"id": "concreting_for_column", "name": "Concreting for Column", "weightage": 1.79},
                        {"id": "shuttering_plinth_beam", "name": "Shuttering for Plinth Beam", "weightage": 0.70},
                        {"id": "reinforcement_plinth_beam", "name": "Reinforcement for Plinth Beam", "weightage": 1.00},
                        {"id": "concreting_plinth_beam", "name": "Concreting for Plinth Beam", "weightage": 0.80},
                        {"id": "filling_earth_plinth_pcc", "name": "Filling earth within Plinth and PCC", "weightage": 0.30}
                    ]
                },
                {
                    "id": "slab_completion",
                    "name": "Completion of Slabs at all levels",
                    "total_weightage": 31.78,
                    "note": "Divide by number of floors from Buildings section",
                    "activities": [
                        {"id": "reinforcement_lintel_roof", "name": "Reinforcement up to Lintel/Roof bottom", "weightage": 6.00},
                        {"id": "shuttering_for_column", "name": "Shuttering for Column", "weightage": 4.40},
                        {"id": "concreting_for_column", "name": "Concreting for Column", "weightage": 5.00},
                        {"id": "shuttering_beams_roof", "name": "Shuttering for Beams and Roof", "weightage": 4.80},
                        {"id": "reinforcement_beams_roof", "name": "Reinforcement for Beams and Roof", "weightage": 6.00},
                        {"id": "concreting_beams_roof", "name": "Concreting for Beams and Roof", "weightage": 4.00},
                        {"id": "dismantling_roof_shuttering", "name": "Dismantling of Roof Shuttering", "weightage": 1.58}
                    ]
                },
                {
                    "id": "brickwork_plastering",
                    "name": "Completion of Brickwork and Plastering",
                    "total_weightage": 12.71,
                    "activities": [
                        {"id": "brickwork_external_walls", "name": "Brickwork External walls", "weightage": 2.50},
                        {"id": "brickwork_internal_walls", "name": "Brickwork Internal walls", "weightage": 2.80},
                        {"id": "fixing_door_window_frames", "name": "Fixing of Door/Window frames", "weightage": 1.50},
                        {"id": "fixing_concealed_pipes", "name": "Fixing concealed Water & Electric pipes", "weightage": 1.40},
                        {"id": "plastering_external_walls", "name": "Plastering External walls", "weightage": 1.30},
                        {"id": "plastering_internal_walls", "name": "Plastering Internal walls", "weightage": 1.80},
                        {"id": "waterproof_plastering_toilets", "name": "Water-proof Plastering of Toilets", "weightage": 1.41}
                    ]
                },
                {
                    "id": "plumbing",
                    "name": "Plumbing",
                    "total_weightage": 3.93,
                    "activities": [
                        {"id": "fixing_water_pipes", "name": "Fixing External & Internal Water Pipes", "weightage": 1.40},
                        {"id": "fixing_wc_pipes_traps", "name": "Fixing External & Internal WC Pipes & Traps", "weightage": 1.30},
                        {"id": "fixing_plumbing_fixtures", "name": "Fixing of all Plumbing fixtures", "weightage": 1.23}
                    ]
                },
                {
                    "id": "electrical_works",
                    "name": "Electrical Works",
                    "total_weightage": 9.08,
                    "activities": [
                        {"id": "laying_all_cables", "name": "Laying all Cables (Internal)", "weightage": 3.00},
                        {"id": "fixing_electrical_fixtures", "name": "Fixing all Electrical fixtures (Internal)", "weightage": 2.00},
                        {"id": "electrical_breaker_box", "name": "Electrical/Breaker Box (External)", "weightage": 2.00},
                        {"id": "electric_meter_box", "name": "Electric meter box (External)", "weightage": 1.00},
                        {"id": "connecting_cable_electrical_box", "name": "Connecting cable to the Electrical box", "weightage": 1.08}
                    ]
                },
                {
                    "id": "window_works",
                    "name": "Aluminium/UPVC Window",
                    "total_weightage": 8.02,
                    "activities": [
                        {"id": "fixing_frames", "name": "Fixing of frames", "weightage": 4.40},
                        {"id": "fixing_glass", "name": "Fixing of Glass", "weightage": 3.62}
                    ]
                },
                {
                    "id": "tiling_flooring",
                    "name": "Tiling/Flooring",
                    "total_weightage": 8.02,
                    "activities": [
                        {"id": "laying_floor_tiles", "name": "Laying of Floor tiles", "weightage": 3.00},
                        {"id": "laying_wall_tiles_kitchen_bathroom", "name": "Laying of Wall tiles Kitchen & Bathroom", "weightage": 2.80},
                        {"id": "laying_granite_kitchen_counter", "name": "Laying of Granite/Kadapa slab for Kitchen Counter", "weightage": 2.22}
                    ]
                },
                {
                    "id": "door_shutter_fixing",
                    "name": "Door Shutter Fixing",
                    "total_weightage": 2.42,
                    "activities": [
                        {"id": "fixing_door_shutters", "name": "Fixing of Door shutters", "weightage": 1.30},
                        {"id": "fixing_locks_handles", "name": "Fixing of locks, handles & accessories", "weightage": 1.12}
                    ]
                },
                {
                    "id": "water_proofing",
                    "name": "Water Proofing",
                    "total_weightage": 2.42,
                    "activities": [
                        {"id": "terrace_roof_waterproofing", "name": "Terrace roof water proofing", "weightage": 2.42}
                    ]
                },
                {
                    "id": "painting",
                    "name": "Painting",
                    "total_weightage": 8.32,
                    "activities": [
                        {"id": "painting_ceiling", "name": "Ceiling", "weightage": 2.30},
                        {"id": "painting_walls", "name": "Walls", "weightage": 2.80},
                        {"id": "painting_grills", "name": "Grills", "weightage": 1.80},
                        {"id": "painting_doors_windows", "name": "Doors/Windows", "weightage": 1.42}
                    ]
                },
                {
                    "id": "carpark",
                    "name": "Carpark",
                    "total_weightage": 0.76,
                    "activities": [
                        {"id": "levelling", "name": "Levelling", "weightage": 0.20},
                        {"id": "paving", "name": "Paving", "weightage": 0.56}
                    ]
                },
                {
                    "id": "handover_intimation",
                    "name": "Intimation of Handover",
                    "total_weightage": 1.66,
                    "activities": [
                        {"id": "intimation_of_handover", "name": "Intimation of Handover", "weightage": 1.66}
                    ]
                }
            ]
        },
        "infrastructure_works": {
            "total_weightage": 100,
            "activities": [
                {"id": "road_footpath_storm_drain", "name": "Road, Foot-path and storm water drain", "weightage": 21.5},
                {"id": "underground_sewage_network", "name": "Underground sewage drainage network", "weightage": 13.0},
                {"id": "sewage_treatment_plant", "name": "Sewage Treatment Plant", "weightage": 8.5},
                {"id": "overhead_sump_reservoir", "name": "Over-head and Sump water reservoir/Tank", "weightage": 8.5},
                {"id": "underground_water_distribution", "name": "Under ground water distribution network", "weightage": 10.5},
                {"id": "electric_substation_cables", "name": "Electric Substation & Under-ground electric cables", "weightage": 10.5},
                {"id": "street_lights", "name": "Street Lights", "weightage": 4.0},
                {"id": "entry_gate", "name": "Entry Gate", "weightage": 2.5},
                {"id": "boundary_wall", "name": "Boundary wall", "weightage": 6.0},
                {"id": "club_house", "name": "Club House", "weightage": 7.0},
                {"id": "swimming_pool", "name": "Swimming Pool", "weightage": 3.5},
                {"id": "amphitheatre", "name": "Amphitheatre", "weightage": 2.5},
                {"id": "gardens_playground", "name": "Gardens / Play Ground", "weightage": 2.0}
            ]
        }
    }


# =========================
# WEIGHTAGE CALCULATION HELPER
# =========================

def calculate_recalibrated_completion(activities_data: dict, template_categories: list) -> tuple:
    """Calculate completion with recalibrated weightages for N/A items.
    Supports cost-based weightage mode per category (flag: _use_cost_weightage).
    When cost mode is ON, each sub-activity's effective weightage = (cost / total_cost) * cat_base_applicable_wt.
    """
    total_applicable_weightage = 0
    weighted_completion = 0
    category_completions = {}

    for category in template_categories:
        cat_id = category["id"]
        cat_data = activities_data.get(cat_id, {})
        cat_applicable_weightage = 0
        cat_weighted_completion = 0

        use_cost_weightage = cat_data.get("_use_cost_weightage", False)

        def _get_act_weightage(act_data: dict, template_weightage: float) -> float:
            """Return custom weightage if explicitly set (even if 0), else template default."""
            cw = act_data.get("_custom_weightage")
            if cw is not None and cw != "":
                try:
                    return float(cw)
                except (TypeError, ValueError):
                    pass
            return template_weightage

        if use_cost_weightage:
            total_cost = 0
            cat_base_applicable = 0
            for activity in category["activities"]:
                act_id = activity["id"]
                act_data = cat_data.get(act_id, {})
                if act_data.get("is_applicable", True):
                    total_cost += float(act_data.get("cost", 0) or 0)
                    act_base_wt = _get_act_weightage(act_data, activity["weightage"])
                    cat_base_applicable += act_base_wt

            for activity in category["activities"]:
                act_id = activity["id"]
                act_data = cat_data.get(act_id, {})
                is_applicable = act_data.get("is_applicable", True)
                if is_applicable:
                    completion = act_data.get("completion", 0)
                    cost = float(act_data.get("cost", 0) or 0)
                    act_base_wt = _get_act_weightage(act_data, activity["weightage"])
                    if total_cost > 0:
                        effective_wt = (cost / total_cost) * cat_base_applicable
                    else:
                        effective_wt = act_base_wt

                    total_applicable_weightage += effective_wt
                    cat_applicable_weightage += effective_wt
                    weighted_completion += effective_wt * completion / 100
                    cat_weighted_completion += effective_wt * completion / 100
        else:
            for activity in category["activities"]:
                act_id = activity["id"]
                act_data = cat_data.get(act_id, {})
                is_applicable = act_data.get("is_applicable", True)
                if is_applicable:
                    base_weightage = _get_act_weightage(act_data, activity["weightage"])
                    completion = act_data.get("completion", 0)

                    total_applicable_weightage += base_weightage
                    cat_applicable_weightage += base_weightage
                    weighted_completion += base_weightage * completion / 100
                    cat_weighted_completion += base_weightage * completion / 100

        if cat_applicable_weightage > 0:
            category_completions[cat_id] = round(cat_weighted_completion / cat_applicable_weightage * 100, 2)
        else:
            category_completions[cat_id] = 0

    overall_completion = 0
    if total_applicable_weightage > 0:
        overall_completion = weighted_completion / total_applicable_weightage * 100

    return round(overall_completion, 2), total_applicable_weightage, category_completions


# =========================
# DETAILED PROGRESS SAVE (with weightage recalibration)
# =========================

@router.post("/construction-progress/detailed")
async def create_detailed_construction_progress(
    building_id: str = Query(...),
    quarter: str = Query(...),
    year: int = Query(...),
    number_of_floors: int = Query(1),
    current_user: dict = Depends(get_current_user),
    request: Request = None
):
    """Save detailed tower construction progress with N/A support and weightage recalibration."""
    tower_activities = await request.json() if request else {}

    building = await db.buildings.find_one({"building_id": building_id})
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    template = await get_detailed_construction_template()
    categories = template["tower_construction"]["categories"]

    overall_completion, total_applicable_weightage, category_completions = calculate_recalibrated_completion(
        tower_activities, categories
    )

    progress_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    progress_doc = {
        "progress_id": progress_id,
        "project_id": building["project_id"],
        "building_id": building_id,
        "quarter": quarter,
        "year": year,
        "tower_activities": tower_activities,
        "number_of_floors": number_of_floors,
        "overall_completion": overall_completion,
        "recalibrated_total_weightage": total_applicable_weightage,
        "category_completions": category_completions,
        "created_at": now
    }

    await db.construction_progress.update_one(
        {"building_id": building_id, "quarter": quarter, "year": year},
        {"$set": progress_doc},
        upsert=True
    )

    return progress_doc


# =========================
# INFRASTRUCTURE PROGRESS ROUTES
# =========================

INFRASTRUCTURE_TEMPLATE = [
    {"id": "road_footpath_storm_drain", "name": "Road, Foot-path and storm water drain", "weightage": 21.5},
    {"id": "underground_sewage_network", "name": "Underground sewage drainage network", "weightage": 13.0},
    {"id": "sewage_treatment_plant", "name": "Sewage Treatment Plant", "weightage": 8.5},
    {"id": "overhead_sump_reservoir", "name": "Over-head and Sump water reservoir/Tank", "weightage": 8.5},
    {"id": "underground_water_distribution", "name": "Under ground water distribution network", "weightage": 10.5},
    {"id": "electric_substation_cables", "name": "Electric Substation & Under-ground electric cables", "weightage": 10.5},
    {"id": "street_lights", "name": "Street Lights", "weightage": 4.0},
    {"id": "entry_gate", "name": "Entry Gate", "weightage": 2.5},
    {"id": "boundary_wall", "name": "Boundary wall", "weightage": 6.0},
    {"id": "club_house", "name": "Club House", "weightage": 7.0},
    {"id": "swimming_pool", "name": "Swimming Pool", "weightage": 3.5},
    {"id": "amphitheatre", "name": "Amphitheatre", "weightage": 2.5},
    {"id": "gardens_playground", "name": "Gardens / Play Ground", "weightage": 2.0},
]


@router.post("/infrastructure-progress")
async def create_infrastructure_progress(
    project_id: str = Query(...),
    quarter: str = Query(...),
    year: int = Query(...),
    current_user: dict = Depends(get_current_user),
    request: Request = None
):
    """Save infrastructure works progress with N/A support and recalibration."""
    activities = await request.json() if request else {}

    total_applicable_weightage = 0
    weighted_completion = 0

    for item in INFRASTRUCTURE_TEMPLATE:
        item_id = item["id"]
        item_data = activities.get(item_id, {})
        is_applicable = item_data.get("is_applicable", True)

        if is_applicable:
            completion = item_data.get("completion", 0)
            weightage = item["weightage"]
            total_applicable_weightage += weightage
            weighted_completion += weightage * completion / 100

    overall_completion = 0
    if total_applicable_weightage > 0:
        overall_completion = weighted_completion / total_applicable_weightage * 100

    progress_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    progress_doc = {
        "progress_id": progress_id,
        "project_id": project_id,
        "quarter": quarter,
        "year": year,
        "activities": activities,
        "overall_completion": round(overall_completion, 2),
        "recalibrated_total_weightage": total_applicable_weightage,
        "created_at": now
    }

    await db.infrastructure_progress.update_one(
        {"project_id": project_id, "quarter": quarter, "year": year},
        {"$set": progress_doc},
        upsert=True
    )

    return progress_doc


@router.get("/infrastructure-progress")
async def get_infrastructure_progress(
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

    progress_list = await db.infrastructure_progress.find(query, {"_id": 0}).to_list(100)
    return progress_list


@router.get("/infrastructure-progress/latest/{project_id}")
async def get_latest_infrastructure_progress(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    progress = await db.infrastructure_progress.find_one(
        {"project_id": project_id},
        {"_id": 0},
        sort=[("year", -1), ("quarter", -1)]
    )
    if not progress:
        raise HTTPException(status_code=404, detail="No infrastructure progress data found")
    return progress
