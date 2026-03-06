from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import json
from io import BytesIO

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Settings
JWT_SECRET = os.environ.get('JWT_SECRET', 'rera-compliance-secret-key-2024')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Create the main app
app = FastAPI(title="RERA Compliance Manager API")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =========================
# MODELS
# =========================

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str = Field(..., description="One of: admin, developer, architect, engineer, ca, auditor")
    phone: Optional[str] = None
    license_number: Optional[str] = None
    firm_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    created_at: str
    is_active: bool = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ProjectBase(BaseModel):
    project_name: str
    state: str = "GOA"
    rera_number: str
    promoter_name: str
    promoter_address: str
    project_address: str
    survey_number: Optional[str] = None
    plot_number: Optional[str] = None
    village: Optional[str] = None
    taluka: Optional[str] = None
    district: Optional[str] = None
    pin_code: Optional[str] = None
    plot_area: Optional[float] = None
    total_built_up_area: Optional[float] = None
    project_start_date: Optional[str] = None
    expected_completion_date: Optional[str] = None
    architect_name: Optional[str] = None
    architect_license: Optional[str] = None
    engineer_name: Optional[str] = None
    engineer_license: Optional[str] = None
    ca_name: Optional[str] = None
    ca_firm_name: Optional[str] = None
    auditor_name: Optional[str] = None
    auditor_firm_name: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    model_config = ConfigDict(extra="ignore")
    project_id: str
    created_by: str
    created_at: str
    updated_at: str

class BuildingBase(BaseModel):
    building_name: str
    floors: int = 0
    units: int = 0
    estimated_cost: float = 0
    completion_cert_number: Optional[str] = None
    completion_cert_date: Optional[str] = None
    occupancy_cert_number: Optional[str] = None
    occupancy_cert_date: Optional[str] = None
    planning_authority: Optional[str] = None
    structural_consultant: Optional[str] = None
    mep_consultant: Optional[str] = None
    site_supervisor: Optional[str] = None

class BuildingCreate(BuildingBase):
    project_id: str

class BuildingResponse(BuildingBase):
    model_config = ConfigDict(extra="ignore")
    building_id: str
    project_id: str
    created_at: str

class ConstructionActivityBase(BaseModel):
    activity_name: str
    weightage: float
    completion_percentage: float = 0

class ConstructionProgressBase(BaseModel):
    building_id: str
    quarter: str
    year: int
    activities: List[ConstructionActivityBase]
    overall_completion: float = 0

class ConstructionProgressCreate(ConstructionProgressBase):
    pass

class ConstructionProgressResponse(ConstructionProgressBase):
    model_config = ConfigDict(extra="ignore")
    progress_id: str
    project_id: str
    created_at: str

class ProjectCostBase(BaseModel):
    project_id: str
    quarter: str
    year: int
    land_acquisition_cost: float = 0
    development_rights_premium: float = 0
    tdr_cost: float = 0
    stamp_duty: float = 0
    government_charges: float = 0
    encumbrance_removal: float = 0
    construction_cost: float = 0
    infrastructure_cost: float = 0
    equipment_cost: float = 0
    taxes_statutory: float = 0
    finance_cost: float = 0
    estimated_land_cost: float = 0
    estimated_development_cost: float = 0

class ProjectCostCreate(ProjectCostBase):
    pass

class ProjectCostResponse(ProjectCostBase):
    model_config = ConfigDict(extra="ignore")
    cost_id: str
    total_land_cost: float = 0
    total_development_cost: float = 0
    total_estimated_cost: float = 0
    total_cost_incurred: float = 0
    balance_cost: float = 0
    created_at: str

class BuildingCostBase(BaseModel):
    building_id: str
    quarter: str
    year: int
    estimated_cost: float = 0
    cost_incurred: float = 0

class BuildingCostCreate(BuildingCostBase):
    pass

class BuildingCostResponse(BuildingCostBase):
    model_config = ConfigDict(extra="ignore")
    building_cost_id: str
    project_id: str
    completion_percentage: float = 0
    balance_cost: float = 0
    created_at: str

class UnitSaleBase(BaseModel):
    unit_number: str
    building_id: str
    building_name: str
    carpet_area: float
    sale_value: float
    amount_received: float = 0
    buyer_name: Optional[str] = None
    agreement_date: Optional[str] = None

class UnitSaleCreate(UnitSaleBase):
    project_id: str

class UnitSaleResponse(UnitSaleBase):
    model_config = ConfigDict(extra="ignore")
    sale_id: str
    project_id: str
    balance_receivable: float = 0
    created_at: str

class QuarterlyReportBase(BaseModel):
    project_id: str
    quarter: str
    year: int
    report_date: str
    status: str = "draft"

class QuarterlyReportCreate(QuarterlyReportBase):
    pass

class QuarterlyReportResponse(QuarterlyReportBase):
    model_config = ConfigDict(extra="ignore")
    report_id: str
    created_by: str
    created_at: str

class ReportTemplateBase(BaseModel):
    state: str
    report_name: str
    report_type: str
    template_html: str
    data_mapping: Dict[str, Any] = {}

class ReportTemplateCreate(ReportTemplateBase):
    pass

class ReportTemplateResponse(ReportTemplateBase):
    model_config = ConfigDict(extra="ignore")
    template_id: str
    created_at: str
    updated_at: str

class DashboardSummary(BaseModel):
    project_completion_percentage: float = 0
    total_estimated_cost: float = 0
    cost_incurred: float = 0
    balance_cost: float = 0
    total_sales_value: float = 0
    amount_collected: float = 0
    receivables: float = 0
    unsold_inventory_value: float = 0
    rera_deposit_required: float = 0
    total_units: int = 0
    units_sold: int = 0

# =========================
# AUTHENTICATION HELPERS
# =========================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# =========================
# AUTH ROUTES
# =========================

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user: UserCreate):
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user_doc = {
        "user_id": user_id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "phone": user.phone,
        "license_number": user.license_number,
        "firm_name": user.firm_name,
        "password_hash": hash_password(user.password),
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user_doc)
    
    token = create_token(user_id, user.email, user.role)
    user_response = UserResponse(
        user_id=user_id,
        email=user.email,
        name=user.name,
        role=user.role,
        phone=user.phone,
        license_number=user.license_number,
        firm_name=user.firm_name,
        created_at=user_doc["created_at"],
        is_active=True
    )
    return TokenResponse(access_token=token, user=user_response)

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user["user_id"], user["email"], user["role"])
    user_response = UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        name=user["name"],
        role=user["role"],
        phone=user.get("phone"),
        license_number=user.get("license_number"),
        firm_name=user.get("firm_name"),
        created_at=user["created_at"],
        is_active=user.get("is_active", True)
    )
    return TokenResponse(access_token=token, user=user_response)

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        user_id=current_user["user_id"],
        email=current_user["email"],
        name=current_user["name"],
        role=current_user["role"],
        phone=current_user.get("phone"),
        license_number=current_user.get("license_number"),
        firm_name=current_user.get("firm_name"),
        created_at=current_user["created_at"],
        is_active=current_user.get("is_active", True)
    )

# =========================
# PROJECT ROUTES
# =========================

@api_router.post("/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, current_user: dict = Depends(get_current_user)):
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

@api_router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(current_user: dict = Depends(get_current_user)):
    projects = await db.projects.find({}, {"_id": 0}).to_list(1000)
    return [ProjectResponse(**p) for p in projects]

@api_router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, current_user: dict = Depends(get_current_user)):
    project = await db.projects.find_one({"project_id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(**project)

@api_router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, project: ProjectCreate, current_user: dict = Depends(get_current_user)):
    existing = await db.projects.find_one({"project_id": project_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project.model_dump()
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.projects.update_one({"project_id": project_id}, {"$set": update_data})
    
    updated = await db.projects.find_one({"project_id": project_id}, {"_id": 0})
    return ProjectResponse(**updated)

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.projects.delete_one({"project_id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    # Delete related data
    await db.buildings.delete_many({"project_id": project_id})
    await db.construction_progress.delete_many({"project_id": project_id})
    await db.project_costs.delete_many({"project_id": project_id})
    await db.unit_sales.delete_many({"project_id": project_id})
    return {"message": "Project deleted"}

# =========================
# BUILDING ROUTES
# =========================

@api_router.post("/buildings", response_model=BuildingResponse)
async def create_building(building: BuildingCreate, current_user: dict = Depends(get_current_user)):
    building_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    building_doc = {
        "building_id": building_id,
        **building.model_dump(),
        "created_at": now
    }
    await db.buildings.insert_one(building_doc)
    return BuildingResponse(**{k: v for k, v in building_doc.items() if k != "_id"})

@api_router.get("/buildings", response_model=List[BuildingResponse])
async def get_buildings(project_id: str = Query(...), current_user: dict = Depends(get_current_user)):
    buildings = await db.buildings.find({"project_id": project_id}, {"_id": 0}).to_list(1000)
    return [BuildingResponse(**b) for b in buildings]

@api_router.get("/buildings/{building_id}", response_model=BuildingResponse)
async def get_building(building_id: str, current_user: dict = Depends(get_current_user)):
    building = await db.buildings.find_one({"building_id": building_id}, {"_id": 0})
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return BuildingResponse(**building)

@api_router.put("/buildings/{building_id}", response_model=BuildingResponse)
async def update_building(building_id: str, building: BuildingBase, current_user: dict = Depends(get_current_user)):
    existing = await db.buildings.find_one({"building_id": building_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Building not found")
    
    await db.buildings.update_one({"building_id": building_id}, {"$set": building.model_dump()})
    updated = await db.buildings.find_one({"building_id": building_id}, {"_id": 0})
    return BuildingResponse(**updated)

@api_router.delete("/buildings/{building_id}")
async def delete_building(building_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.buildings.delete_one({"building_id": building_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Building not found")
    return {"message": "Building deleted"}

# =========================
# CONSTRUCTION PROGRESS ROUTES
# =========================

DEFAULT_ACTIVITIES = [
    {"activity_name": "Excavation", "weightage": 5, "completion_percentage": 0},
    {"activity_name": "Basement / Plinth", "weightage": 8, "completion_percentage": 0},
    {"activity_name": "Podium", "weightage": 5, "completion_percentage": 0},
    {"activity_name": "Stilt Floor", "weightage": 5, "completion_percentage": 0},
    {"activity_name": "Superstructure Slabs", "weightage": 20, "completion_percentage": 0},
    {"activity_name": "Internal Walls & Plaster", "weightage": 10, "completion_percentage": 0},
    {"activity_name": "Doors & Windows", "weightage": 7, "completion_percentage": 0},
    {"activity_name": "Sanitary Fittings", "weightage": 5, "completion_percentage": 0},
    {"activity_name": "Electrical Fittings", "weightage": 5, "completion_percentage": 0},
    {"activity_name": "Staircases and Lift Wells", "weightage": 5, "completion_percentage": 0},
    {"activity_name": "Water Tanks", "weightage": 3, "completion_percentage": 0},
    {"activity_name": "External Plumbing and Plaster", "weightage": 7, "completion_percentage": 0},
    {"activity_name": "Terrace Waterproofing", "weightage": 3, "completion_percentage": 0},
    {"activity_name": "Fire Fighting Systems", "weightage": 5, "completion_percentage": 0},
    {"activity_name": "Common Area Finishing", "weightage": 4, "completion_percentage": 0},
    {"activity_name": "Compound Wall and Final Works", "weightage": 3, "completion_percentage": 0},
]

@api_router.post("/construction-progress", response_model=ConstructionProgressResponse)
async def create_construction_progress(progress: ConstructionProgressCreate, current_user: dict = Depends(get_current_user)):
    # Get building to get project_id
    building = await db.buildings.find_one({"building_id": progress.building_id})
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    
    # Calculate overall completion
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
    
    # Upsert - update if exists for same building/quarter/year
    await db.construction_progress.update_one(
        {"building_id": progress.building_id, "quarter": progress.quarter, "year": progress.year},
        {"$set": progress_doc},
        upsert=True
    )
    return ConstructionProgressResponse(**progress_doc)

@api_router.get("/construction-progress", response_model=List[ConstructionProgressResponse])
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

@api_router.get("/construction-progress/default-activities")
async def get_default_activities():
    return DEFAULT_ACTIVITIES

# =========================
# PROJECT COST ROUTES
# =========================

@api_router.post("/project-costs", response_model=ProjectCostResponse)
async def create_project_cost(cost: ProjectCostCreate, current_user: dict = Depends(get_current_user)):
    # Calculate totals
    total_land = (cost.land_acquisition_cost + cost.development_rights_premium + 
                  cost.tdr_cost + cost.stamp_duty + cost.government_charges + cost.encumbrance_removal)
    total_dev = (cost.construction_cost + cost.infrastructure_cost + cost.equipment_cost + 
                 cost.taxes_statutory + cost.finance_cost)
    total_estimated = cost.estimated_land_cost + cost.estimated_development_cost
    total_incurred = total_land + total_dev
    balance = total_estimated - total_incurred
    
    cost_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    cost_doc = {
        "cost_id": cost_id,
        **cost.model_dump(),
        "total_land_cost": total_land,
        "total_development_cost": total_dev,
        "total_estimated_cost": total_estimated,
        "total_cost_incurred": total_incurred,
        "balance_cost": balance,
        "created_at": now
    }
    
    # Upsert
    await db.project_costs.update_one(
        {"project_id": cost.project_id, "quarter": cost.quarter, "year": cost.year},
        {"$set": cost_doc},
        upsert=True
    )
    return ProjectCostResponse(**cost_doc)

@api_router.get("/project-costs", response_model=List[ProjectCostResponse])
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

@api_router.get("/project-costs/latest/{project_id}", response_model=ProjectCostResponse)
async def get_latest_project_cost(project_id: str, current_user: dict = Depends(get_current_user)):
    cost = await db.project_costs.find_one(
        {"project_id": project_id},
        {"_id": 0},
        sort=[("year", -1), ("quarter", -1)]
    )
    if not cost:
        raise HTTPException(status_code=404, detail="No cost data found")
    return ProjectCostResponse(**cost)

# =========================
# BUILDING COST ROUTES
# =========================

@api_router.post("/building-costs", response_model=BuildingCostResponse)
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

@api_router.get("/building-costs", response_model=List[BuildingCostResponse])
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

# =========================
# UNIT SALES ROUTES (Annexure-A)
# =========================

@api_router.post("/unit-sales", response_model=UnitSaleResponse)
async def create_unit_sale(sale: UnitSaleCreate, current_user: dict = Depends(get_current_user)):
    sale_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    balance = sale.sale_value - sale.amount_received
    
    sale_doc = {
        "sale_id": sale_id,
        **sale.model_dump(),
        "balance_receivable": balance,
        "created_at": now
    }
    await db.unit_sales.insert_one(sale_doc)
    return UnitSaleResponse(**{k: v for k, v in sale_doc.items() if k != "_id"})

@api_router.get("/unit-sales", response_model=List[UnitSaleResponse])
async def get_unit_sales(project_id: str = Query(...), current_user: dict = Depends(get_current_user)):
    sales = await db.unit_sales.find({"project_id": project_id}, {"_id": 0}).to_list(10000)
    return [UnitSaleResponse(**s) for s in sales]

@api_router.put("/unit-sales/{sale_id}", response_model=UnitSaleResponse)
async def update_unit_sale(sale_id: str, sale: UnitSaleBase, current_user: dict = Depends(get_current_user)):
    existing = await db.unit_sales.find_one({"sale_id": sale_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Unit sale not found")
    
    balance = sale.sale_value - sale.amount_received
    update_data = sale.model_dump()
    update_data["balance_receivable"] = balance
    
    await db.unit_sales.update_one({"sale_id": sale_id}, {"$set": update_data})
    updated = await db.unit_sales.find_one({"sale_id": sale_id}, {"_id": 0})
    return UnitSaleResponse(**updated)

@api_router.delete("/unit-sales/{sale_id}")
async def delete_unit_sale(sale_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.unit_sales.delete_one({"sale_id": sale_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Unit sale not found")
    return {"message": "Unit sale deleted"}

@api_router.post("/unit-sales/bulk", response_model=Dict[str, Any])
async def bulk_create_unit_sales(
    project_id: str = Query(...),
    sales: List[UnitSaleBase] = None,
    current_user: dict = Depends(get_current_user)
):
    if not sales:
        raise HTTPException(status_code=400, detail="No sales data provided")
    
    created = 0
    errors = []
    for idx, sale in enumerate(sales):
        try:
            sale_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc).isoformat()
            balance = sale.sale_value - sale.amount_received
            
            sale_doc = {
                "sale_id": sale_id,
                "project_id": project_id,
                **sale.model_dump(),
                "balance_receivable": balance,
                "created_at": now
            }
            await db.unit_sales.insert_one(sale_doc)
            created += 1
        except Exception as e:
            errors.append({"row": idx + 1, "error": str(e)})
    
    return {"created": created, "errors": errors}

# =========================
# EXCEL IMPORT
# =========================

@api_router.post("/import/sales-excel")
async def import_sales_excel(
    project_id: str = Query(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Import unit sales from Excel file"""
    import openpyxl
    from io import BytesIO
    
    contents = await file.read()
    wb = openpyxl.load_workbook(BytesIO(contents))
    ws = wb.active
    
    # Find header row
    headers = {}
    header_row = 1
    for col in range(1, ws.max_column + 1):
        cell_value = ws.cell(row=1, column=col).value
        if cell_value:
            headers[str(cell_value).lower().strip()] = col
    
    # Map columns
    column_map = {
        "unit_number": ["unit number", "unit no", "unit no.", "flat no", "flat number"],
        "building_name": ["building name", "building", "wing", "tower"],
        "carpet_area": ["carpet area", "area", "carpet area (sq ft)", "carpet area (sqm)"],
        "sale_value": ["sale value", "agreement value", "total value", "price"],
        "amount_received": ["amount received", "received", "collection", "amount collected"],
        "buyer_name": ["buyer name", "buyer", "customer name", "allottee"],
        "agreement_date": ["agreement date", "date", "booking date"]
    }
    
    def find_column(field):
        for alias in column_map.get(field, []):
            if alias in headers:
                return headers[alias]
        return None
    
    created = 0
    errors = []
    
    # Get buildings for this project to map building names to IDs
    buildings = await db.buildings.find({"project_id": project_id}, {"_id": 0}).to_list(1000)
    building_map = {b["building_name"].lower(): b["building_id"] for b in buildings}
    
    for row in range(2, ws.max_row + 1):
        try:
            unit_col = find_column("unit_number")
            building_col = find_column("building_name")
            area_col = find_column("carpet_area")
            value_col = find_column("sale_value")
            received_col = find_column("amount_received")
            buyer_col = find_column("buyer_name")
            date_col = find_column("agreement_date")
            
            unit_number = ws.cell(row=row, column=unit_col).value if unit_col else None
            building_name = ws.cell(row=row, column=building_col).value if building_col else None
            
            if not unit_number:
                continue
            
            carpet_area = float(ws.cell(row=row, column=area_col).value or 0) if area_col else 0
            sale_value = float(ws.cell(row=row, column=value_col).value or 0) if value_col else 0
            amount_received = float(ws.cell(row=row, column=received_col).value or 0) if received_col else 0
            buyer_name = str(ws.cell(row=row, column=buyer_col).value or "") if buyer_col else ""
            agreement_date = ws.cell(row=row, column=date_col).value if date_col else None
            
            if agreement_date and hasattr(agreement_date, 'isoformat'):
                agreement_date = agreement_date.isoformat()
            elif agreement_date:
                agreement_date = str(agreement_date)
            
            # Find building_id
            building_id = building_map.get(str(building_name).lower(), "") if building_name else ""
            
            sale_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc).isoformat()
            balance = sale_value - amount_received
            
            sale_doc = {
                "sale_id": sale_id,
                "project_id": project_id,
                "unit_number": str(unit_number),
                "building_id": building_id,
                "building_name": str(building_name or ""),
                "carpet_area": carpet_area,
                "sale_value": sale_value,
                "amount_received": amount_received,
                "buyer_name": buyer_name,
                "agreement_date": agreement_date,
                "balance_receivable": balance,
                "created_at": now
            }
            await db.unit_sales.insert_one(sale_doc)
            created += 1
        except Exception as e:
            errors.append({"row": row, "error": str(e)})
    
    return {"created": created, "errors": errors, "total_rows": ws.max_row - 1}

@api_router.get("/import/sales-template")
async def get_sales_template():
    """Download Excel template for sales import"""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sales Data"
    
    headers = ["Unit Number", "Building Name", "Carpet Area", "Sale Value", "Amount Received", "Buyer Name", "Agreement Date"]
    header_fill = PatternFill(start_color="172554", end_color="172554", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
        ws.column_dimensions[cell.column_letter].width = 18
    
    # Add sample data
    sample_data = [
        ["A-101", "Tower A", 850, 7500000, 5000000, "John Doe", "2024-01-15"],
        ["A-102", "Tower A", 920, 8200000, 4100000, "Jane Smith", "2024-02-20"],
    ]
    for row_idx, row_data in enumerate(sample_data, 2):
        for col_idx, value in enumerate(row_data, 1):
            ws.cell(row=row_idx, column=col_idx, value=value)
    
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=sales_template.xlsx"}
    )

# =========================
# DASHBOARD & SUMMARY
# =========================

@api_router.get("/dashboard/{project_id}", response_model=DashboardSummary)
async def get_dashboard(project_id: str, current_user: dict = Depends(get_current_user)):
    # Get latest project cost
    cost = await db.project_costs.find_one(
        {"project_id": project_id},
        {"_id": 0},
        sort=[("year", -1), ("quarter", -1)]
    )
    
    # Get all unit sales
    sales = await db.unit_sales.find({"project_id": project_id}, {"_id": 0}).to_list(10000)
    
    # Get buildings
    buildings = await db.buildings.find({"project_id": project_id}, {"_id": 0}).to_list(1000)
    
    # Get construction progress
    progress_list = await db.construction_progress.find(
        {"project_id": project_id},
        {"_id": 0},
        sort=[("year", -1), ("quarter", -1)]
    ).to_list(1000)
    
    # Calculate totals
    total_sales_value = sum(s.get("sale_value", 0) for s in sales)
    amount_collected = sum(s.get("amount_received", 0) for s in sales)
    receivables = sum(s.get("balance_receivable", 0) for s in sales)
    units_sold = len(sales)
    total_units = sum(b.get("units", 0) for b in buildings)
    
    # Calculate unsold inventory
    total_building_value = sum(b.get("estimated_cost", 0) for b in buildings)
    unsold_units = total_units - units_sold
    avg_unit_value = total_sales_value / units_sold if units_sold > 0 else 0
    unsold_inventory_value = unsold_units * avg_unit_value
    
    # Calculate overall completion
    if progress_list:
        # Get latest progress for each building
        building_progress = {}
        for p in progress_list:
            bid = p.get("building_id")
            if bid not in building_progress:
                building_progress[bid] = p.get("overall_completion", 0)
        overall_completion = sum(building_progress.values()) / len(building_progress) if building_progress else 0
    else:
        overall_completion = 0
    
    # Cost data
    total_estimated = cost.get("total_estimated_cost", 0) if cost else 0
    cost_incurred = cost.get("total_cost_incurred", 0) if cost else 0
    balance_cost = cost.get("balance_cost", 0) if cost else 0
    
    # RERA deposit calculation (Form-5 logic)
    if balance_cost > 0 and receivables > 0:
        ratio = receivables / balance_cost
        if ratio > 1:
            rera_deposit = receivables * 0.7
        else:
            rera_deposit = receivables
    else:
        rera_deposit = 0
    
    return DashboardSummary(
        project_completion_percentage=round(overall_completion, 2),
        total_estimated_cost=total_estimated,
        cost_incurred=cost_incurred,
        balance_cost=balance_cost,
        total_sales_value=total_sales_value,
        amount_collected=amount_collected,
        receivables=receivables,
        unsold_inventory_value=unsold_inventory_value,
        rera_deposit_required=rera_deposit,
        total_units=total_units,
        units_sold=units_sold
    )

# =========================
# QUARTERLY REPORTS
# =========================

@api_router.post("/quarterly-reports", response_model=QuarterlyReportResponse)
async def create_quarterly_report(report: QuarterlyReportCreate, current_user: dict = Depends(get_current_user)):
    report_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    report_doc = {
        "report_id": report_id,
        **report.model_dump(),
        "created_by": current_user["user_id"],
        "created_at": now
    }
    await db.quarterly_reports.insert_one(report_doc)
    return QuarterlyReportResponse(**{k: v for k, v in report_doc.items() if k != "_id"})

@api_router.get("/quarterly-reports", response_model=List[QuarterlyReportResponse])
async def get_quarterly_reports(project_id: str = Query(...), current_user: dict = Depends(get_current_user)):
    reports = await db.quarterly_reports.find({"project_id": project_id}, {"_id": 0}).to_list(1000)
    return [QuarterlyReportResponse(**r) for r in reports]

# =========================
# REPORT TEMPLATES
# =========================

@api_router.post("/report-templates", response_model=ReportTemplateResponse)
async def create_report_template(template: ReportTemplateCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    template_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    template_doc = {
        "template_id": template_id,
        **template.model_dump(),
        "created_at": now,
        "updated_at": now
    }
    await db.report_templates.insert_one(template_doc)
    return ReportTemplateResponse(**{k: v for k, v in template_doc.items() if k != "_id"})

@api_router.get("/report-templates", response_model=List[ReportTemplateResponse])
async def get_report_templates(state: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    query = {}
    if state:
        query["state"] = state
    templates = await db.report_templates.find(query, {"_id": 0}).to_list(1000)
    return [ReportTemplateResponse(**t) for t in templates]

@api_router.get("/report-templates/{template_id}", response_model=ReportTemplateResponse)
async def get_report_template(template_id: str, current_user: dict = Depends(get_current_user)):
    template = await db.report_templates.find_one({"template_id": template_id}, {"_id": 0})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return ReportTemplateResponse(**template)

@api_router.put("/report-templates/{template_id}", response_model=ReportTemplateResponse)
async def update_report_template(template_id: str, template: ReportTemplateCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    existing = await db.report_templates.find_one({"template_id": template_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Template not found")
    
    update_data = template.model_dump()
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.report_templates.update_one({"template_id": template_id}, {"$set": update_data})
    
    updated = await db.report_templates.find_one({"template_id": template_id}, {"_id": 0})
    return ReportTemplateResponse(**updated)

# =========================
# REPORT GENERATION
# =========================

@api_router.get("/generate-report/{project_id}/{report_type}")
async def generate_report(
    project_id: str,
    report_type: str,
    quarter: str = Query(...),
    year: int = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """Generate RERA report as HTML (for PDF conversion on frontend)"""
    
    # Get project
    project = await db.projects.find_one({"project_id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get template
    template = await db.report_templates.find_one(
        {"state": project["state"], "report_type": report_type},
        {"_id": 0}
    )
    
    # Get related data
    buildings = await db.buildings.find({"project_id": project_id}, {"_id": 0}).to_list(1000)
    
    progress_list = await db.construction_progress.find(
        {"project_id": project_id, "quarter": quarter, "year": year},
        {"_id": 0}
    ).to_list(1000)
    
    cost = await db.project_costs.find_one(
        {"project_id": project_id, "quarter": quarter, "year": year},
        {"_id": 0}
    )
    
    building_costs = await db.building_costs.find(
        {"project_id": project_id, "quarter": quarter, "year": year},
        {"_id": 0}
    ).to_list(1000)
    
    sales = await db.unit_sales.find({"project_id": project_id}, {"_id": 0}).to_list(10000)
    
    # Calculate summary
    total_sales_value = sum(s.get("sale_value", 0) for s in sales)
    amount_collected = sum(s.get("amount_received", 0) for s in sales)
    receivables = sum(s.get("balance_receivable", 0) for s in sales)
    
    # Build data context
    data = {
        "project": project,
        "buildings": buildings,
        "construction_progress": progress_list,
        "project_cost": cost or {},
        "building_costs": building_costs,
        "sales": sales,
        "quarter": quarter,
        "year": year,
        "report_date": datetime.now().strftime("%d/%m/%Y"),
        "total_sales_value": total_sales_value,
        "amount_collected": amount_collected,
        "receivables": receivables,
        "balance_cost": cost.get("balance_cost", 0) if cost else 0
    }
    
    # If template exists, use it
    if template:
        html = template["template_html"]
        # Replace placeholders
        for key, value in flatten_dict(data).items():
            placeholder = "{{" + key + "}}"
            html = html.replace(placeholder, str(value) if value else "")
        return {"html": html, "data": data}
    
    # Return raw data for frontend rendering
    return {"html": None, "data": data}

def flatten_dict(d, parent_key='', sep='.'):
    """Flatten nested dict"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

# =========================
# DATA VALIDATION
# =========================

@api_router.get("/validate/{project_id}")
async def validate_project_data(project_id: str, current_user: dict = Depends(get_current_user)):
    """Validate project data for RERA compliance"""
    warnings = []
    errors = []
    
    # Get all data
    project = await db.projects.find_one({"project_id": project_id}, {"_id": 0})
    if not project:
        return {"errors": [{"type": "critical", "message": "Project not found"}], "warnings": []}
    
    buildings = await db.buildings.find({"project_id": project_id}, {"_id": 0}).to_list(1000)
    sales = await db.unit_sales.find({"project_id": project_id}, {"_id": 0}).to_list(10000)
    cost = await db.project_costs.find_one({"project_id": project_id}, {"_id": 0}, sort=[("year", -1), ("quarter", -1)])
    
    # Check for missing required fields
    required_fields = ["project_name", "rera_number", "promoter_name", "architect_name", "engineer_name", "ca_name"]
    for field in required_fields:
        if not project.get(field):
            warnings.append({"type": "missing_field", "message": f"Missing required field: {field}"})
    
    # Check for duplicate units
    unit_numbers = [s["unit_number"] for s in sales]
    duplicates = [u for u in set(unit_numbers) if unit_numbers.count(u) > 1]
    if duplicates:
        errors.append({"type": "duplicate", "message": f"Duplicate unit numbers found: {', '.join(duplicates)}"})
    
    # Check for negative receivables
    negative_receivables = [s for s in sales if s.get("balance_receivable", 0) < 0]
    if negative_receivables:
        warnings.append({
            "type": "negative_receivable",
            "message": f"{len(negative_receivables)} units have negative receivables (over-collection)"
        })
    
    # Check completion vs cost mismatch
    if cost:
        total_estimated = cost.get("total_estimated_cost", 0)
        cost_incurred = cost.get("total_cost_incurred", 0)
        
        if cost_incurred > total_estimated:
            warnings.append({
                "type": "cost_overrun",
                "message": f"Cost incurred ({cost_incurred:,.0f}) exceeds estimated cost ({total_estimated:,.0f})"
            })
    
    # Check receivables vs balance cost
    total_receivables = sum(s.get("balance_receivable", 0) for s in sales)
    balance_cost = cost.get("balance_cost", 0) if cost else 0
    
    if total_receivables > 0 and balance_cost > 0:
        ratio = total_receivables / balance_cost
        if ratio > 1.5:
            warnings.append({
                "type": "receivable_mismatch",
                "message": f"Receivables ({total_receivables:,.0f}) significantly exceed balance cost ({balance_cost:,.0f})"
            })
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "buildings": len(buildings),
            "units_sold": len(sales),
            "total_receivables": total_receivables,
            "balance_cost": balance_cost
        }
    }

# =========================
# HEALTH CHECK
# =========================

@api_router.get("/")
async def root():
    return {"message": "RERA Compliance Manager API", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("user_id", unique=True)
    await db.projects.create_index("project_id", unique=True)
    await db.buildings.create_index("building_id", unique=True)
    await db.unit_sales.create_index("sale_id", unique=True)
    await db.report_templates.create_index([("state", 1), ("report_type", 1)])
    
    # Initialize default report templates for GOA
    existing = await db.report_templates.find_one({"state": "GOA"})
    if not existing:
        await initialize_goa_templates()
    
    logger.info("RERA Compliance Manager API started")

async def initialize_goa_templates():
    """Initialize default Goa RERA report templates"""
    templates = [
        {
            "template_id": str(uuid.uuid4()),
            "state": "GOA",
            "report_name": "Form-1: Architect Certificate",
            "report_type": "form-1",
            "template_html": GOA_FORM_1_TEMPLATE,
            "data_mapping": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "template_id": str(uuid.uuid4()),
            "state": "GOA",
            "report_name": "Form-2: Architect Completion Certificate",
            "report_type": "form-2",
            "template_html": GOA_FORM_2_TEMPLATE,
            "data_mapping": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "template_id": str(uuid.uuid4()),
            "state": "GOA",
            "report_name": "Form-3: Engineer Certificate",
            "report_type": "form-3",
            "template_html": GOA_FORM_3_TEMPLATE,
            "data_mapping": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "template_id": str(uuid.uuid4()),
            "state": "GOA",
            "report_name": "Form-4: CA Certificate",
            "report_type": "form-4",
            "template_html": GOA_FORM_4_TEMPLATE,
            "data_mapping": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "template_id": str(uuid.uuid4()),
            "state": "GOA",
            "report_name": "Form-5: CA Compliance Certificate",
            "report_type": "form-5",
            "template_html": GOA_FORM_5_TEMPLATE,
            "data_mapping": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "template_id": str(uuid.uuid4()),
            "state": "GOA",
            "report_name": "Form-6: Auditor Certificate",
            "report_type": "form-6",
            "template_html": GOA_FORM_6_TEMPLATE,
            "data_mapping": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "template_id": str(uuid.uuid4()),
            "state": "GOA",
            "report_name": "Annexure-A: Statement of Receivables",
            "report_type": "annexure-a",
            "template_html": GOA_ANNEXURE_A_TEMPLATE,
            "data_mapping": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    for template in templates:
        await db.report_templates.insert_one(template)
    
    logger.info("Initialized Goa RERA templates")

# =========================
# GOA RERA TEMPLATES
# =========================

GOA_FORM_1_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.6; padding: 40px; }
.header { text-align: center; margin-bottom: 30px; }
.title { font-size: 16pt; font-weight: bold; margin-bottom: 10px; }
.subtitle { font-size: 14pt; margin-bottom: 20px; }
table { width: 100%; border-collapse: collapse; margin: 20px 0; }
th, td { border: 1px solid #000; padding: 8px; text-align: left; }
th { background-color: #f0f0f0; }
.signature { margin-top: 50px; }
.form-section { margin: 20px 0; }
</style>
</head>
<body>
<div class="header">
<div class="title">GOA REAL ESTATE REGULATORY AUTHORITY</div>
<div class="subtitle">FORM - 1</div>
<div class="subtitle">ARCHITECT'S CERTIFICATE</div>
<div>(Percentage of Completion)</div>
</div>

<div class="form-section">
<p><strong>Project Name:</strong> {{project.project_name}}</p>
<p><strong>RERA Registration No:</strong> {{project.rera_number}}</p>
<p><strong>Quarter:</strong> {{quarter}} {{year}}</p>
<p><strong>Report Date:</strong> {{report_date}}</p>
</div>

<div class="form-section">
<p>I, {{project.architect_name}}, Architect, having License No. {{project.architect_license}}, 
hereby certify that the construction of the project mentioned above is progressing as per the sanctioned plans 
and the percentage of completion is as follows:</p>
</div>

<table>
<tr>
<th>Sr. No.</th>
<th>Building/Wing</th>
<th>Activity</th>
<th>Weightage (%)</th>
<th>Completion (%)</th>
<th>Weighted Completion (%)</th>
</tr>
<!-- Building data will be populated here -->
</table>

<div class="signature">
<p>Date: {{report_date}}</p>
<p>Place: {{project.district}}, {{project.state}}</p>
<br><br>
<p>_____________________________</p>
<p>{{project.architect_name}}</p>
<p>Architect</p>
<p>License No: {{project.architect_license}}</p>
</div>
</body>
</html>
"""

GOA_FORM_2_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.6; padding: 40px; }
.header { text-align: center; margin-bottom: 30px; }
.title { font-size: 16pt; font-weight: bold; margin-bottom: 10px; }
.subtitle { font-size: 14pt; margin-bottom: 20px; }
table { width: 100%; border-collapse: collapse; margin: 20px 0; }
th, td { border: 1px solid #000; padding: 8px; text-align: left; }
th { background-color: #f0f0f0; }
.signature { margin-top: 50px; }
</style>
</head>
<body>
<div class="header">
<div class="title">GOA REAL ESTATE REGULATORY AUTHORITY</div>
<div class="subtitle">FORM - 2</div>
<div class="subtitle">ARCHITECT'S COMPLETION CERTIFICATE</div>
</div>

<div class="form-section">
<p><strong>Project Name:</strong> {{project.project_name}}</p>
<p><strong>RERA Registration No:</strong> {{project.rera_number}}</p>
</div>

<table>
<tr>
<th>Sr. No.</th>
<th>Building/Wing Name</th>
<th>Completion Cert. No.</th>
<th>Completion Cert. Date</th>
<th>Occupancy Cert. No.</th>
<th>Occupancy Cert. Date</th>
</tr>
<!-- Building completion data -->
</table>

<div class="signature">
<p>Date: {{report_date}}</p>
<p>Place: {{project.district}}, {{project.state}}</p>
<br><br>
<p>_____________________________</p>
<p>{{project.architect_name}}</p>
<p>Architect</p>
</div>
</body>
</html>
"""

GOA_FORM_3_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.6; padding: 40px; }
.header { text-align: center; margin-bottom: 30px; }
.title { font-size: 16pt; font-weight: bold; margin-bottom: 10px; }
.subtitle { font-size: 14pt; margin-bottom: 20px; }
table { width: 100%; border-collapse: collapse; margin: 20px 0; }
th, td { border: 1px solid #000; padding: 8px; text-align: left; }
th { background-color: #f0f0f0; }
.amount { text-align: right; }
.signature { margin-top: 50px; }
</style>
</head>
<body>
<div class="header">
<div class="title">GOA REAL ESTATE REGULATORY AUTHORITY</div>
<div class="subtitle">FORM - 3</div>
<div class="subtitle">ENGINEER'S CERTIFICATE</div>
<div>(Cost Incurred)</div>
</div>

<div class="form-section">
<p><strong>Project Name:</strong> {{project.project_name}}</p>
<p><strong>RERA Registration No:</strong> {{project.rera_number}}</p>
<p><strong>Quarter:</strong> {{quarter}} {{year}}</p>
</div>

<table>
<tr>
<th>Sr. No.</th>
<th>Building/Wing Name</th>
<th>Estimated Cost (Rs.)</th>
<th>Cost Incurred (Rs.)</th>
<th>Completion %</th>
<th>Balance Cost (Rs.)</th>
</tr>
<!-- Building cost data -->
</table>

<div class="signature">
<p>Date: {{report_date}}</p>
<p>Place: {{project.district}}, {{project.state}}</p>
<br><br>
<p>_____________________________</p>
<p>{{project.engineer_name}}</p>
<p>Engineer</p>
<p>License No: {{project.engineer_license}}</p>
</div>
</body>
</html>
"""

GOA_FORM_4_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.6; padding: 40px; }
.header { text-align: center; margin-bottom: 30px; }
.title { font-size: 16pt; font-weight: bold; margin-bottom: 10px; }
.subtitle { font-size: 14pt; margin-bottom: 20px; }
table { width: 100%; border-collapse: collapse; margin: 20px 0; }
th, td { border: 1px solid #000; padding: 8px; text-align: left; }
th { background-color: #f0f0f0; }
.amount { text-align: right; }
.signature { margin-top: 50px; }
</style>
</head>
<body>
<div class="header">
<div class="title">GOA REAL ESTATE REGULATORY AUTHORITY</div>
<div class="subtitle">FORM - 4</div>
<div class="subtitle">CHARTERED ACCOUNTANT'S CERTIFICATE</div>
<div>(Project Cost)</div>
</div>

<div class="form-section">
<p><strong>Project Name:</strong> {{project.project_name}}</p>
<p><strong>RERA Registration No:</strong> {{project.rera_number}}</p>
<p><strong>Quarter:</strong> {{quarter}} {{year}}</p>
</div>

<h4>A. Land Cost</h4>
<table>
<tr><th>Particulars</th><th>Estimated Amount (Rs.)</th><th>Actual Amount (Rs.)</th></tr>
<tr><td>Land Acquisition Cost</td><td class="amount">{{project_cost.estimated_land_cost}}</td><td class="amount">{{project_cost.land_acquisition_cost}}</td></tr>
<tr><td>Development Rights Premium</td><td class="amount">-</td><td class="amount">{{project_cost.development_rights_premium}}</td></tr>
<tr><td>TDR Cost</td><td class="amount">-</td><td class="amount">{{project_cost.tdr_cost}}</td></tr>
<tr><td>Stamp Duty</td><td class="amount">-</td><td class="amount">{{project_cost.stamp_duty}}</td></tr>
<tr><td>Government Charges</td><td class="amount">-</td><td class="amount">{{project_cost.government_charges}}</td></tr>
<tr><td><strong>Total Land Cost</strong></td><td class="amount"><strong>{{project_cost.estimated_land_cost}}</strong></td><td class="amount"><strong>{{project_cost.total_land_cost}}</strong></td></tr>
</table>

<h4>B. Development Cost</h4>
<table>
<tr><th>Particulars</th><th>Estimated Amount (Rs.)</th><th>Actual Amount (Rs.)</th></tr>
<tr><td>Construction Cost</td><td class="amount">{{project_cost.estimated_development_cost}}</td><td class="amount">{{project_cost.construction_cost}}</td></tr>
<tr><td>Infrastructure Cost</td><td class="amount">-</td><td class="amount">{{project_cost.infrastructure_cost}}</td></tr>
<tr><td>Equipment Cost</td><td class="amount">-</td><td class="amount">{{project_cost.equipment_cost}}</td></tr>
<tr><td>Taxes & Statutory Charges</td><td class="amount">-</td><td class="amount">{{project_cost.taxes_statutory}}</td></tr>
<tr><td>Finance Cost</td><td class="amount">-</td><td class="amount">{{project_cost.finance_cost}}</td></tr>
<tr><td><strong>Total Development Cost</strong></td><td class="amount"><strong>{{project_cost.estimated_development_cost}}</strong></td><td class="amount"><strong>{{project_cost.total_development_cost}}</strong></td></tr>
</table>

<table>
<tr><td><strong>Total Estimated Cost</strong></td><td class="amount"><strong>{{project_cost.total_estimated_cost}}</strong></td></tr>
<tr><td><strong>Total Cost Incurred</strong></td><td class="amount"><strong>{{project_cost.total_cost_incurred}}</strong></td></tr>
<tr><td><strong>Balance Cost</strong></td><td class="amount"><strong>{{project_cost.balance_cost}}</strong></td></tr>
</table>

<div class="signature">
<p>Date: {{report_date}}</p>
<p>Place: {{project.district}}, {{project.state}}</p>
<br><br>
<p>_____________________________</p>
<p>{{project.ca_name}}</p>
<p>Chartered Accountant</p>
<p>Firm: {{project.ca_firm_name}}</p>
</div>
</body>
</html>
"""

GOA_FORM_5_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.6; padding: 40px; }
.header { text-align: center; margin-bottom: 30px; }
.title { font-size: 16pt; font-weight: bold; margin-bottom: 10px; }
.subtitle { font-size: 14pt; margin-bottom: 20px; }
table { width: 100%; border-collapse: collapse; margin: 20px 0; }
th, td { border: 1px solid #000; padding: 8px; text-align: left; }
th { background-color: #f0f0f0; }
.amount { text-align: right; }
.highlight { background-color: #ffffcc; }
.signature { margin-top: 50px; }
</style>
</head>
<body>
<div class="header">
<div class="title">GOA REAL ESTATE REGULATORY AUTHORITY</div>
<div class="subtitle">FORM - 5</div>
<div class="subtitle">CA CERTIFICATE - RECEIVABLE COMPLIANCE</div>
</div>

<div class="form-section">
<p><strong>Project Name:</strong> {{project.project_name}}</p>
<p><strong>RERA Registration No:</strong> {{project.rera_number}}</p>
<p><strong>Quarter:</strong> {{quarter}} {{year}}</p>
</div>

<h4>Receivable Compliance Calculation</h4>
<table>
<tr><td>Total Receivables (A)</td><td class="amount">Rs. {{receivables}}</td></tr>
<tr><td>Balance Cost (B)</td><td class="amount">Rs. {{balance_cost}}</td></tr>
<tr><td>Ratio (A/B)</td><td class="amount">{{ratio}}</td></tr>
</table>

<h4>RERA Deposit Requirement</h4>
<table>
<tr class="highlight">
<td><strong>If Ratio > 1:</strong> Deposit 70% of Receivables</td>
<td class="amount">Rs. {{deposit_70}}</td>
</tr>
<tr class="highlight">
<td><strong>If Ratio ≤ 1:</strong> Deposit 100% of Receivables</td>
<td class="amount">Rs. {{deposit_100}}</td>
</tr>
<tr>
<td><strong>Required RERA Deposit</strong></td>
<td class="amount"><strong>Rs. {{rera_deposit}}</strong></td>
</tr>
</table>

<div class="signature">
<p>Date: {{report_date}}</p>
<p>Place: {{project.district}}, {{project.state}}</p>
<br><br>
<p>_____________________________</p>
<p>{{project.ca_name}}</p>
<p>Chartered Accountant</p>
<p>Firm: {{project.ca_firm_name}}</p>
</div>
</body>
</html>
"""

GOA_FORM_6_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.6; padding: 40px; }
.header { text-align: center; margin-bottom: 30px; }
.title { font-size: 16pt; font-weight: bold; margin-bottom: 10px; }
.subtitle { font-size: 14pt; margin-bottom: 20px; }
table { width: 100%; border-collapse: collapse; margin: 20px 0; }
th, td { border: 1px solid #000; padding: 8px; text-align: left; }
th { background-color: #f0f0f0; }
.amount { text-align: right; }
.signature { margin-top: 50px; }
</style>
</head>
<body>
<div class="header">
<div class="title">GOA REAL ESTATE REGULATORY AUTHORITY</div>
<div class="subtitle">FORM - 6</div>
<div class="subtitle">AUDITOR'S CERTIFICATE</div>
<div>(Statement of Accounts)</div>
</div>

<div class="form-section">
<p><strong>Project Name:</strong> {{project.project_name}}</p>
<p><strong>RERA Registration No:</strong> {{project.rera_number}}</p>
<p><strong>Financial Year:</strong> {{year}}</p>
</div>

<h4>Statement of Accounts</h4>
<table>
<tr><td>Project Completion Percentage</td><td class="amount">{{completion_percentage}}%</td></tr>
<tr><td>Total Collections</td><td class="amount">Rs. {{amount_collected}}</td></tr>
<tr><td>Total Withdrawals/Utilization</td><td class="amount">Rs. {{cost_incurred}}</td></tr>
<tr><td>Balance in RERA Account</td><td class="amount">Rs. {{balance}}</td></tr>
</table>

<p>I hereby certify that I have audited the accounts of the above project and confirm that 
the funds collected from allottees have been utilized for the purposes of the project 
in accordance with the Real Estate (Regulation and Development) Act, 2016.</p>

<div class="signature">
<p>Date: {{report_date}}</p>
<p>Place: {{project.district}}, {{project.state}}</p>
<br><br>
<p>_____________________________</p>
<p>{{project.auditor_name}}</p>
<p>Auditor</p>
<p>Firm: {{project.auditor_firm_name}}</p>
</div>
</body>
</html>
"""

GOA_ANNEXURE_A_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: 'Times New Roman', serif; font-size: 10pt; line-height: 1.4; padding: 20px; }
.header { text-align: center; margin-bottom: 20px; }
.title { font-size: 14pt; font-weight: bold; margin-bottom: 10px; }
.subtitle { font-size: 12pt; margin-bottom: 15px; }
table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 9pt; }
th, td { border: 1px solid #000; padding: 5px; text-align: left; }
th { background-color: #f0f0f0; text-align: center; }
.amount { text-align: right; }
.center { text-align: center; }
.total-row { font-weight: bold; background-color: #f5f5f5; }
</style>
</head>
<body>
<div class="header">
<div class="title">GOA REAL ESTATE REGULATORY AUTHORITY</div>
<div class="subtitle">ANNEXURE - A</div>
<div class="subtitle">STATEMENT OF RECEIVABLES</div>
</div>

<div class="form-section">
<p><strong>Project Name:</strong> {{project.project_name}}</p>
<p><strong>RERA Registration No:</strong> {{project.rera_number}}</p>
<p><strong>Quarter:</strong> {{quarter}} {{year}}</p>
</div>

<table>
<tr>
<th>Sr. No.</th>
<th>Unit No.</th>
<th>Building</th>
<th>Carpet Area (sq.ft.)</th>
<th>Buyer Name</th>
<th>Agreement Date</th>
<th>Sale Value (Rs.)</th>
<th>Amount Received (Rs.)</th>
<th>Balance Receivable (Rs.)</th>
</tr>
<!-- Sales data rows will be populated here -->
<tr class="total-row">
<td colspan="6" class="center">TOTAL</td>
<td class="amount">{{total_sales_value}}</td>
<td class="amount">{{amount_collected}}</td>
<td class="amount">{{receivables}}</td>
</tr>
</table>

<div class="signature">
<p>Date: {{report_date}}</p>
<p>Place: {{project.district}}, {{project.state}}</p>
<br><br>
<p>_____________________________</p>
<p>{{project.promoter_name}}</p>
<p>Promoter/Developer</p>
</div>
</body>
</html>
"""

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
