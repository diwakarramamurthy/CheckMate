"""Building management routes."""

from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timezone
from typing import Dict, Any
import uuid
from typing import List, Dict, Any

from database import db
from models import (
    BuildingBase, BuildingCreate, BuildingResponse, BuildingBulkCreate,
    APARTMENT_CLASSIFICATIONS
)
from auth import get_current_user

router = APIRouter()

def calculate_building_totals(building_data: dict) -> dict:
    """Calculate total floors and units based on building type and configuration."""
    building_type = building_data.get("building_type", "residential_tower")

    # Calculate total parking floors
    total_parking = (
        building_data.get("parking_basement", 0) +
        building_data.get("parking_stilt_ground", 0) +
        building_data.get("parking_upper_level", 0)
    )

    # Calculate total floors based on building type
    if building_type in ["residential_tower", "mixed_tower"]:
        commercial = building_data.get("commercial_floors", 0) if building_type == "mixed_tower" else 0
        residential = building_data.get("residential_floors", 0)
        apartments_per_floor = building_data.get("apartments_per_floor", 0)

        total_floors = total_parking + commercial + residential
        total_units = residential * apartments_per_floor
    else:  # row_house or bungalow
        residential = building_data.get("residential_floors", 0)
        total_floors = total_parking + residential
        total_units = 1  # Each row house/bungalow is 1 unit

    building_data["floors"] = total_floors
    building_data["units"] = total_units
    building_data["total_parking_floors"] = total_parking

    return building_data

@router.post("/buildings", response_model=BuildingResponse)
async def create_building(building: BuildingCreate, current_user: dict = Depends(get_current_user)):
    """Create a new building."""
    building_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    building_data = building.model_dump()
    building_data = calculate_building_totals(building_data)

    building_doc = {
        "building_id": building_id,
        **building_data,
        "created_at": now
    }
    await db.buildings.insert_one(building_doc)
    return BuildingResponse(**{k: v for k, v in building_doc.items() if k != "_id"})

@router.post("/buildings/bulk", response_model=Dict[str, Any])
async def create_buildings_bulk(bulk_data: BuildingBulkCreate, current_user: dict = Depends(get_current_user)):
    """Create multiple buildings with the same configuration but different names."""
    created = []
    errors = []
    now = datetime.now(timezone.utc).isoformat()

    # Get template data and calculate totals
    template_data = bulk_data.template.model_dump()
    template_data = calculate_building_totals(template_data)

    for idx, name in enumerate(bulk_data.building_names):
        try:
            building_id = str(uuid.uuid4())
            building_doc = {
                "building_id": building_id,
                "project_id": bulk_data.project_id,
                **template_data,
                "building_name": name.strip(),
                "created_at": now
            }
            await db.buildings.insert_one(building_doc)
            created.append({"building_id": building_id, "building_name": name})
        except Exception as e:
            errors.append({"name": name, "error": str(e)})

    return {
        "created": len(created),
        "buildings": created,
        "errors": errors
    }

@router.get("/buildings/types")
async def get_building_types():
    """Get available building types with their configurations."""
    return {
        "types": [
            {
                "value": "residential_tower",
                "label": "Multi-storey Residential Apartment Tower",
                "has_commercial": False,
                "has_apartments_per_floor": True,
                "is_single_unit": False
            },
            {
                "value": "mixed_tower",
                "label": "Multi-storey Mixed (Commercial & Residential) Tower",
                "has_commercial": True,
                "has_apartments_per_floor": True,
                "is_single_unit": False
            },
            {
                "value": "row_house",
                "label": "Row House",
                "has_commercial": False,
                "has_apartments_per_floor": False,
                "is_single_unit": True
            },
            {
                "value": "bungalow",
                "label": "Bungalow",
                "has_commercial": False,
                "has_apartments_per_floor": False,
                "is_single_unit": True
            }
        ],
        "parking_options": [
            {"field": "parking_basement", "label": "Basement Parking Floors"},
            {"field": "parking_stilt_ground", "label": "Stilt/Ground Parking Floors"},
            {"field": "parking_upper_level", "label": "Upper Level Parking Floors"}
        ],
        "apartment_classifications": APARTMENT_CLASSIFICATIONS
    }

@router.get("/buildings", response_model=List[BuildingResponse])
async def get_buildings(project_id: str = Query(...), current_user: dict = Depends(get_current_user)):
    """Get all buildings for a project."""
    buildings = await db.buildings.find({"project_id": project_id}, {"_id": 0}).to_list(1000)
    result = []
    for b in buildings:
        # Ensure backward compatibility - calculate totals if missing
        if "total_parking_floors" not in b:
            b = calculate_building_totals(b)
        result.append(BuildingResponse(**b))
    return result

@router.get("/buildings/{building_id}", response_model=BuildingResponse)
async def get_building(building_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific building."""
    building = await db.buildings.find_one({"building_id": building_id}, {"_id": 0})
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    if "total_parking_floors" not in building:
        building = calculate_building_totals(building)
    return BuildingResponse(**building)

@router.put("/buildings/{building_id}", response_model=BuildingResponse)
async def update_building(building_id: str, building: BuildingBase, current_user: dict = Depends(get_current_user)):
    """Update a building."""
    existing = await db.buildings.find_one({"building_id": building_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Building not found")

    building_data = building.model_dump()
    building_data = calculate_building_totals(building_data)

    await db.buildings.update_one({"building_id": building_id}, {"$set": building_data})
    updated = await db.buildings.find_one({"building_id": building_id}, {"_id": 0})
    return BuildingResponse(**updated)

@router.delete("/buildings/{building_id}")
async def delete_building(building_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a building."""
    result = await db.buildings.delete_one({"building_id": building_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Building not found")
    return {"message": "Building deleted"}


# =========================
# WEIGHTAGE PROFILE ROUTES
# =========================

@router.get("/buildings/{building_id}/weightages")
async def get_building_weightages(
    building_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get saved weightage overrides for a building.
    Returns custom profile if one has been saved, otherwise returns an empty object
    (the frontend falls back to template defaults when the profile is empty).
    """
    building = await db.buildings.find_one({"building_id": building_id})
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    profile = await db.building_weightages.find_one(
        {"building_id": building_id}, {"_id": 0}
    )
    if not profile:
        return {
            "building_id": building_id,
            "category_base_weightages": {},
            "activity_weightages": {},
            "updated_at": None
        }
    return profile


@router.put("/buildings/{building_id}/weightages")
async def save_building_weightages(
    building_id: str,
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Save custom weightage overrides for a building.

    Expected payload:
    {
        "category_base_weightages": { "<cat_id>": <float>, ... },
        "activity_weightages":      { "<cat_id>": { "<act_id>": <float>, ... }, ... }
    }

    These overrides are applied whenever the Construction Progress page loads
    for this building (across all quarters), so the user only needs to set them once.
    Per-quarter overrides saved inside tower_activities still take precedence.
    """
    building = await db.buildings.find_one({"building_id": building_id})
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "building_id": building_id,
        "project_id": building["project_id"],
        "category_base_weightages": payload.get("category_base_weightages", {}),
        "activity_weightages": payload.get("activity_weightages", {}),
        "updated_at": now,
        "updated_by": current_user.get("user_id", "unknown")
    }

    await db.building_weightages.update_one(
        {"building_id": building_id},
        {"$set": doc},
        upsert=True
    )
    return doc
