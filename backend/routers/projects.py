"""Project management routes."""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
import uuid
from typing import List

from database import db
from models import ProjectCreate, ProjectResponse
from auth import get_current_user

router = APIRouter()

@router.post("/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, current_user: dict = Depends(get_current_user)):
    """Create a new project."""
    project_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    project_doc = {
        "project_id": project_id,
        **project.model_dump(),
        "created_by": current_user["user_id"],
        "created_at": now,
        "updated_at": now
    }
    await db.projects.insert_one(project_doc)
    return ProjectResponse(**{k: v for k, v in project_doc.items() if k != "_id"})

@router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(current_user: dict = Depends(get_current_user)):
    """Get all projects."""
    projects = await db.projects.find({}, {"_id": 0}).to_list(1000)
    return [ProjectResponse(**p) for p in projects]

@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific project."""
    project = await db.projects.find_one({"project_id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(**project)

@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, project: ProjectCreate, current_user: dict = Depends(get_current_user)):
    """Update a project."""
    existing = await db.projects.find_one({"project_id": project_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project.model_dump()
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.projects.update_one({"project_id": project_id}, {"$set": update_data})

    updated = await db.projects.find_one({"project_id": project_id}, {"_id": 0})
    return ProjectResponse(**updated)

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a project and all related data."""
    result = await db.projects.delete_one({"project_id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    # Delete related data
    await db.buildings.delete_many({"project_id": project_id})
    await db.construction_progress.delete_many({"project_id": project_id})
    await db.project_costs.delete_many({"project_id": project_id})
    await db.unit_sales.delete_many({"project_id": project_id})
    return {"message": "Project deleted"}
