"""Construction.Py routes."""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, status, Request
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid
import json
from io import BytesIO

from database import db
from models import (
    ConstructionProgressBase, ConstructionProgressCreate, ConstructionProgressResponse,
    ConstructionActivityBase, ActivityItem, TowerConstructionProgress
)
from auth import get_current_user

router = APIRouter()

@router.post("/construction-progress", response_model=ConstructionProgressResponse)
async def create_construction_progress(progress: ConstructionProgressCreate, current_user: dict = Depends(get_current_user)):
    # Get building to get project_id
    building = await db.buildings.find_one({"building_id": progress.building_id})
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
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
@router.get("/construction-progress/default-activities")
async def get_default_activities():
    return DEFAULT_ACTIVITIES
# Get comprehensive construction progress template with all activities
@router.get("/construction-progress/detailed-template")
async def get_detailed_construction_template():
    """Returns the comprehensive construction progress tracking template"""
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
# Calculate recalibrated weightage after N/A items
def calculate_recalibrated_completion(activities_data: dict, template_categories: list) -> tuple:
    """Calculate completion with recalibrated weightages for N/A items.
    Supports cost-based weightage mode per category (flag: _use_cost_weightage).
    When cost mode is ON, each sub-activity's effective weightage = (cost / total_cost) * cat_base_applicable_wt.
    """
    total_applicable_weightage = 0
    weighted_completion = 0
    category_completions = {}
# Save detailed construction progress with N/A support
@router.post("/construction-progress/detailed")
async def create_detailed_construction_progress(
    building_id: str = Query(...),
    quarter: str = Query(...),
    year: int = Query(...),
    number_of_floors: int = Query(1),
    current_user: dict = Depends(get_current_user),
    request: Request = None
):
    """Save detailed tower construction progress with N/A support and weightage recalibration"""
    # Get tower_activities from request body
    tower_activities = await request.json() if request else {}
# INFRASTRUCTURE PROGRESS ROUTES
@router.post("/infrastructure-progress")
async def create_infrastructure_progress(
    project_id: str = Query(...),
    quarter: str = Query(...),
    year: int = Query(...),
    current_user: dict = Depends(get_current_user),
    request: Request = None
):
    """Save infrastructure works progress with N/A support and recalibration"""
    # Get activities from request body
    activities = await request.json() if request else {}
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
