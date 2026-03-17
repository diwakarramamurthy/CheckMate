"""Pydantic models for CheckMate API."""



from pydantic import BaseModel, Field, ConfigDict, EmailStr

from typing import List, Optional, Dict, Any



# =========================

# CONSTANTS

# =========================



APARTMENT_CLASSIFICATIONS = [

    "Studio", "1 BHK", "1.5 BHK", "2 BHK", "3 BHK", "4 BHK", "Pent-house", "NA"

]



# =========================

# USER MODELS

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



# =========================

# PROJECT MODELS

# =========================



class ProjectBase(BaseModel):

    project_name: str

    state: str = "GOA"

    rera_number: str

    promoter_name: str

    promoter_address: str

    project_address: str

    survey_number: Optional[str] = None

    plot_number: Optional[str] = None

    chalta_number: Optional[str] = None

    village: Optional[str] = None

    taluka: Optional[str] = None

    district: Optional[str] = None

    ward: Optional[str] = None

    municipality: Optional[str] = None

    pin_code: Optional[str] = None

    plot_area: Optional[float] = None

    total_built_up_area: Optional[float] = None

    boundary_north: Optional[str] = None

    boundary_south: Optional[str] = None

    boundary_east: Optional[str] = None

    boundary_west: Optional[str] = None

    rera_registration_date: Optional[str] = None

    rera_validity_date: Optional[str] = None

    project_phase: Optional[str] = None

    project_start_date: Optional[str] = None

    expected_completion_date: Optional[str] = None

    designated_bank_name: Optional[str] = None

    designated_account_number: Optional[str] = None

    designated_ifsc_code: Optional[str] = None

    architect_name: Optional[str] = None

    architect_license: Optional[str] = None

    architect_address: Optional[str] = None

    architect_contact: Optional[str] = None

    architect_email: Optional[str] = None

    engineer_name: Optional[str] = None

    engineer_license: Optional[str] = None

    engineer_address: Optional[str] = None

    engineer_contact: Optional[str] = None

    engineer_email: Optional[str] = None

    structural_consultant_name: Optional[str] = None

    structural_consultant_license: Optional[str] = None

    mep_consultant_name: Optional[str] = None

    mep_consultant_license: Optional[str] = None

    site_supervisor_name: Optional[str] = None

    quantity_surveyor_name: Optional[str] = None

    ca_name: Optional[str] = None

    ca_firm_name: Optional[str] = None

    ca_membership_number: Optional[str] = None

    ca_address: Optional[str] = None

    ca_contact: Optional[str] = None

    ca_email: Optional[str] = None

    auditor_name: Optional[str] = None

    auditor_firm_name: Optional[str] = None

    auditor_membership_number: Optional[str] = None

    auditor_address: Optional[str] = None

    auditor_contact: Optional[str] = None

    auditor_email: Optional[str] = None

    planning_authority_name: Optional[str] = None



class ProjectCreate(ProjectBase):

    pass



class ProjectResponse(ProjectBase):

    model_config = ConfigDict(extra="ignore")

    project_id: str

    created_by: str

    created_at: str

    updated_at: str



# =========================

# BUILDING MODELS

# =========================



class ParkingFloors(BaseModel):

    basement: int = 0

    stilt_ground: int = 0

    upper_level: int = 0



class BuildingBase(BaseModel):

    building_name: str

    building_type: str = "residential_tower"

    parking_basement: int = 0

    parking_stilt_ground: int = 0

    parking_upper_level: int = 0

    commercial_floors: int = 0

    residential_floors: int = 0

    apartments_per_floor: int = 0

    apartment_classification: Optional[str] = "NA"

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



class BuildingBulkCreate(BaseModel):

    project_id: str

    building_names: List[str]

    template: BuildingBase



class BuildingResponse(BuildingBase):

    model_config = ConfigDict(extra="ignore")

    building_id: str

    project_id: str

    created_at: str

    total_parking_floors: int = 0



# =========================

# CONSTRUCTION PROGRESS MODELS

# =========================



class ActivityItem(BaseModel):

    completion: float = 0

    is_applicable: bool = True

    base_weightage: float = 0



class PlinthCompletion(BaseModel):

    excavation: ActivityItem = ActivityItem(base_weightage=0)

    pcc_below_footing: ActivityItem = ActivityItem(base_weightage=0)

    shuttering_for_footing: ActivityItem = ActivityItem(base_weightage=0)

    reinforcement_footing_column: ActivityItem = ActivityItem(base_weightage=0)

    concreting_for_footing: ActivityItem = ActivityItem(base_weightage=0)

    shuttering_column_to_plinth: ActivityItem = ActivityItem(base_weightage=0)

    concreting_for_column: ActivityItem = ActivityItem(base_weightage=0)

    shuttering_plinth_beam: ActivityItem = ActivityItem(base_weightage=0)

    reinforcement_plinth_beam: ActivityItem = ActivityItem(base_weightage=0)

    concreting_plinth_beam: ActivityItem = ActivityItem(base_weightage=0)

    filling_earth_plinth_pcc: ActivityItem = ActivityItem(base_weightage=0)



class BasementSlabCompletion(BaseModel):

    reinforcement_lintel_roof: ActivityItem = ActivityItem(base_weightage=0)

    shuttering_for_column: ActivityItem = ActivityItem(base_weightage=0)

    concreting_for_column: ActivityItem = ActivityItem(base_weightage=0)

    shuttering_beams_roof: ActivityItem = ActivityItem(base_weightage=0)

    reinforcement_beams_roof: ActivityItem = ActivityItem(base_weightage=0)

    concreting_beams_roof: ActivityItem = ActivityItem(base_weightage=0)

    dismantling_roof_shuttering: ActivityItem = ActivityItem(base_weightage=0)



class SlabCompletion(BaseModel):

    reinforcement_lintel_roof: ActivityItem = ActivityItem(base_weightage=0)

    shuttering_for_column: ActivityItem = ActivityItem(base_weightage=0)

    concreting_for_column: ActivityItem = ActivityItem(base_weightage=0)

    shuttering_beams_roof: ActivityItem = ActivityItem(base_weightage=0)

    reinforcement_beams_roof: ActivityItem = ActivityItem(base_weightage=0)

    concreting_beams_roof: ActivityItem = ActivityItem(base_weightage=0)

    dismantling_roof_shuttering: ActivityItem = ActivityItem(base_weightage=0)



class BrickworkPlastering(BaseModel):

    brickwork_external_walls: ActivityItem = ActivityItem(base_weightage=0)

    brickwork_internal_walls: ActivityItem = ActivityItem(base_weightage=0)

    fixing_door_window_frames: ActivityItem = ActivityItem(base_weightage=0)

    fixing_concealed_pipes: ActivityItem = ActivityItem(base_weightage=0)

    plastering_external_walls: ActivityItem = ActivityItem(base_weightage=0)

    plastering_internal_walls: ActivityItem = ActivityItem(base_weightage=0)

    waterproof_plastering_toilets: ActivityItem = ActivityItem(base_weightage=0)



class Plumbing(BaseModel):

    fixing_water_pipes: ActivityItem = ActivityItem(base_weightage=0)

    fixing_wc_pipes_traps: ActivityItem = ActivityItem(base_weightage=0)

    fixing_plumbing_fixtures: ActivityItem = ActivityItem(base_weightage=0)



class ElectricalWorks(BaseModel):

    laying_all_cables: ActivityItem = ActivityItem(base_weightage=0)

    fixing_electrical_fixtures: ActivityItem = ActivityItem(base_weightage=0)

    electrical_breaker_box: ActivityItem = ActivityItem(base_weightage=0)

    electric_meter_box: ActivityItem = ActivityItem(base_weightage=0)

    connecting_cable_electrical_box: ActivityItem = ActivityItem(base_weightage=0)



class WindowWorks(BaseModel):

    fixing_frames: ActivityItem = ActivityItem(base_weightage=0)

    fixing_glass: ActivityItem = ActivityItem(base_weightage=0)



class TilingFlooring(BaseModel):

    laying_floor_tiles: ActivityItem = ActivityItem(base_weightage=0)

    laying_wall_tiles_kitchen_bathroom: ActivityItem = ActivityItem(base_weightage=0)

    laying_granite_kitchen_counter: ActivityItem = ActivityItem(base_weightage=0)



class DoorShutterFixing(BaseModel):

    fixing_door_shutters: ActivityItem = ActivityItem(base_weightage=0)

    fixing_locks_handles: ActivityItem = ActivityItem(base_weightage=0)



class WaterProofing(BaseModel):

    terrace_roof_waterproofing: ActivityItem = ActivityItem(base_weightage=0)



class Painting(BaseModel):

    painting_ceiling: ActivityItem = ActivityItem(base_weightage=0)

    painting_walls: ActivityItem = ActivityItem(base_weightage=0)

    painting_grills: ActivityItem = ActivityItem(base_weightage=0)

    painting_doors_windows: ActivityItem = ActivityItem(base_weightage=0)



class Carpark(BaseModel):

    levelling: ActivityItem = ActivityItem(base_weightage=0)

    paving: ActivityItem = ActivityItem(base_weightage=0)



class HandoverIntimation(BaseModel):

    intimation_of_handover: ActivityItem = ActivityItem(base_weightage=0)



class TowerConstructionProgress(BaseModel):

    basement_slab_completion: BasementSlabCompletion = BasementSlabCompletion()

    plinth_completion: PlinthCompletion = PlinthCompletion()

    slab_completion: SlabCompletion = SlabCompletion()

    brickwork_plastering: BrickworkPlastering = BrickworkPlastering()

    plumbing: Plumbing = Plumbing()

    electrical_works: ElectricalWorks = ElectricalWorks()

    window_works: WindowWorks = WindowWorks()

    tiling_flooring: TilingFlooring = TilingFlooring()

    door_shutter_fixing: DoorShutterFixing = DoorShutterFixing()

    water_proofing: WaterProofing = WaterProofing()

    painting: Painting = Painting()

    carpark: Carpark = Carpark()

    handover_intimation: HandoverIntimation = HandoverIntimation()



class InfrastructureActivityItem(BaseModel):

    completion: float = 0

    is_applicable: bool = True

    base_weightage: float = 0



class ProjectInfrastructureWorks(BaseModel):

    road_footpath_storm_drain: InfrastructureActivityItem = InfrastructureActivityItem(base_weightage=0)

    underground_sewage_network: InfrastructureActivityItem = InfrastructureActivityItem(base_weightage=0)

    sewage_treatment_plant: InfrastructureActivityItem = InfrastructureActivityItem(base_weightage=0)

    overhead_sump_reservoir: InfrastructureActivityItem = InfrastructureActivityItem(base_weightage=0)

    underground_water_distribution: InfrastructureActivityItem = InfrastructureActivityItem(base_weightage=0)

    electric_substation_cables: InfrastructureActivityItem = InfrastructureActivityItem(base_weightage=0)

    street_lights: InfrastructureActivityItem = InfrastructureActivityItem(base_weightage=0)

    entry_gate: InfrastructureActivityItem = InfrastructureActivityItem(base_weightage=0)

    boundary_wall: InfrastructureActivityItem = InfrastructureActivityItem(base_weightage=0)

    club_house: InfrastructureActivityItem = InfrastructureActivityItem(base_weightage=0)

    swimming_pool: InfrastructureActivityItem = InfrastructureActivityItem(base_weightage=0)

    amphitheatre: InfrastructureActivityItem = InfrastructureActivityItem(base_weightage=0)

    gardens_playground: InfrastructureActivityItem = InfrastructureActivityItem(base_weightage=0)



class ConstructionActivityBase(BaseModel):

    activity_name: str

    weightage: float

    completion_percentage: float = 0

    is_applicable: bool = True



class ConstructionProgressBase(BaseModel):

    building_id: str

    quarter: str

    year: int

    activities: List[ConstructionActivityBase] = []

    overall_completion: float = 0

    tower_progress: Optional[TowerConstructionProgress] = None

    number_of_floors: int = 1

    recalibrated_total_weightage: float = 100.0



class ConstructionProgressCreate(ConstructionProgressBase):

    pass



class ConstructionProgressResponse(ConstructionProgressBase):

    model_config = ConfigDict(extra="ignore")

    progress_id: str

    project_id: str

    created_at: str

    tower_completion_percentage: float = 0

    category_completions: Dict[str, float] = {}

    tower_activities: Optional[Dict] = None



class InfrastructureProgressBase(BaseModel):

    project_id: str

    quarter: str

    year: int

    infrastructure_works: ProjectInfrastructureWorks = ProjectInfrastructureWorks()

    overall_completion: float = 0

    recalibrated_total_weightage: float = 100.0



class InfrastructureProgressCreate(InfrastructureProgressBase):

    pass



class InfrastructureProgressResponse(InfrastructureProgressBase):

    model_config = ConfigDict(extra="ignore")

    progress_id: str

    created_at: str



class CommonDevelopmentWorksBase(BaseModel):

    project_id: str

    quarter: str

    year: int

    works: Dict[str, Any] = {}

    overall_completion: float = 0



class CommonDevelopmentWorksCreate(CommonDevelopmentWorksBase):

    pass



class CommonDevelopmentWorksResponse(CommonDevelopmentWorksBase):

    model_config = ConfigDict(extra="ignore")

    works_id: str

    created_at: str



# =========================

# COST MODELS

# =========================



class InfrastructureCostItem(BaseModel):

    estimated_cost: float = 0

    is_applicable: bool = True



class InfrastructureCostBase(BaseModel):

    project_id: str

    road_footpath_storm_drain: InfrastructureCostItem = InfrastructureCostItem()

    underground_sewage_network: InfrastructureCostItem = InfrastructureCostItem()

    sewage_treatment_plant: InfrastructureCostItem = InfrastructureCostItem()

    overhead_sump_reservoir: InfrastructureCostItem = InfrastructureCostItem()

    underground_water_distribution: InfrastructureCostItem = InfrastructureCostItem()

    electric_substation_cables: InfrastructureCostItem = InfrastructureCostItem()

    street_lights: InfrastructureCostItem = InfrastructureCostItem()

    entry_gate: InfrastructureCostItem = InfrastructureCostItem()

    boundary_wall: InfrastructureCostItem = InfrastructureCostItem()

    club_house: InfrastructureCostItem = InfrastructureCostItem()

    swimming_pool: InfrastructureCostItem = InfrastructureCostItem()

    amphitheatre: InfrastructureCostItem = InfrastructureCostItem()

    gardens_playground: InfrastructureCostItem = InfrastructureCostItem()



class InfrastructureCostCreate(InfrastructureCostBase):

    pass



class InfrastructureCostResponse(InfrastructureCostBase):

    model_config = ConfigDict(extra="ignore")

    cost_id: str

    total_infrastructure_cost: float = 0

    created_at: str



class EstimatedDevelopmentCostBase(BaseModel):

    project_id: str

    buildings_cost: float = 0

    infrastructure_cost: float = 0

    consultants_fee: float = 0

    machinery_cost: float = 0



class EstimatedDevelopmentCostCreate(EstimatedDevelopmentCostBase):

    pass



class EstimatedDevelopmentCostResponse(EstimatedDevelopmentCostBase):

    model_config = ConfigDict(extra="ignore")

    estimate_id: str

    total_estimated_development_cost: float = 0

    created_at: str

    updated_at: Optional[str] = None



class ProjectCostBase(BaseModel):

    project_id: str

    quarter: str

    year: int

    land_acquisition_cost: float = 0

    land_acquisition_estimated: float = 0

    land_legal_cost: float = 0

    land_interest_cost: float = 0

    development_rights_premium: float = 0

    development_rights_estimated: float = 0

    tdr_cost: float = 0

    tdr_estimated: float = 0

    stamp_duty: float = 0

    stamp_duty_estimated: float = 0

    government_charges: float = 0

    government_charges_estimated: float = 0

    land_premium_redevelopment: float = 0

    land_premium_estimated: float = 0

    rehab_construction_cost: float = 0

    rehab_construction_estimated: float = 0

    rehab_transit_accommodation: float = 0

    rehab_clearance_cost: float = 0

    rehab_asr_premium: float = 0

    construction_cost_estimated: float = 0

    construction_cost_actual: float = 0

    onsite_salaries: float = 0

    onsite_consultants_fees: float = 0

    onsite_site_overheads: float = 0

    onsite_services_cost: float = 0

    onsite_machinery_equipment: float = 0

    onsite_consumables: float = 0

    offsite_expenditure: float = 0

    taxes_statutory: float = 0

    taxes_statutory_estimated: float = 0

    finance_cost: float = 0

    finance_cost_estimated: float = 0

    extra_items_cost: float = 0

    extra_items_details: Optional[str] = None

    infrastructure_cost: float = 0

    equipment_cost: float = 0

    encumbrance_removal: float = 0

    estimated_land_cost: float = 0

    estimated_development_cost: float = 0



class ProjectCostCreate(ProjectCostBase):

    pass



class ProjectCostResponse(ProjectCostBase):

    model_config = ConfigDict(extra="ignore")

    cost_id: str

    total_land_cost: float = 0

    total_land_cost_estimated: float = 0

    total_development_cost: float = 0

    total_development_cost_estimated: float = 0

    total_estimated_cost: float = 0

    total_cost_incurred: float = 0

    balance_cost: float = 0

    cost_completion_percentage: float = 0

    created_at: str



class BuildingCostBase(BaseModel):

    building_id: str

    quarter: str

    year: int

    estimated_cost: float = 0

    cost_incurred: float = 0

    extra_items_cost: float = 0

    extra_items_details: Optional[str] = None



class BuildingCostCreate(BuildingCostBase):

    pass



class BuildingCostResponse(BuildingCostBase):

    model_config = ConfigDict(extra="ignore")

    building_cost_id: str

    project_id: str

    completion_percentage: float = 0

    balance_cost: float = 0

    created_at: str



# =========================

# SALES & FINANCIAL MODELS

# =========================



class UnitSaleBase(BaseModel):

    unit_number: str

    building_id: str

    building_name: str

    carpet_area: float

    sale_value: float

    amount_received: float = 0

    buyer_name: Optional[str] = None

    agreement_date: Optional[str] = None

    allotment_letter_date: Optional[str] = None

    is_sold: bool = True

    apartment_classification: Optional[str] = "NA"



class UnitSaleCreate(UnitSaleBase):

    project_id: str



class UnitSaleResponse(UnitSaleBase):

    model_config = ConfigDict(extra="ignore")

    sale_id: str

    project_id: str

    balance_receivable: float = 0

    created_at: str



class FinancialSummaryBase(BaseModel):

    project_id: str

    quarter: str

    year: int

    designated_account_opening_balance: float = 0

    amount_deposited_this_quarter: float = 0

    amount_withdrawn_this_quarter: float = 0

    designated_account_closing_balance: float = 0

    total_amount_withdrawn_till_date: float = 0

    total_balance_receivable_sold: float = 0

    unsold_area_sqm: float = 0

    asr_rate_per_sqm: float = 0

    unsold_inventory_value: float = 0

    total_estimated_receivables: float = 0

    deposit_percentage: int = 70

    amount_to_deposit: float = 0

    amount_collected_this_year: float = 0

    amount_collected_till_date: float = 0

    amount_withdrawn_this_year: float = 0



class FinancialSummaryCreate(FinancialSummaryBase):

    pass



class FinancialSummaryResponse(FinancialSummaryBase):

    model_config = ConfigDict(extra="ignore")

    summary_id: str

    created_at: str



# =========================

# REPORT MODELS

# =========================



class QuarterlyReportBase(BaseModel):

    project_id: str

    quarter: str

    year: int

    report_date: str

    report_status: str = "draft"



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



# =========================

# DASHBOARD MODELS

# =========================



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

    building_config_units: int = 0

    sales_data_units: int = 0

    inventory_mismatch: bool = False

    inventory_mismatch_delta: int = 0

