import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import {
  Building2, Plus, Pencil, Trash2, Download, ChevronRight, AlertCircle, CheckCircle2,
  Loader2, RefreshCw, Eye, ChevronDown, MapPin, TrendingUp, Users, IndianRupee, Building,
  FileSpreadsheet, ClipboardList, FileText, Upload, X, Menu
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "../context/AuthContext";
import Layout from "../components/layout/Layout";
import { formatCurrency, formatIndianNumber, formatNumber, CurrencyInput } from "../utils/formatting";
import { API } from "../config";

const ProjectCostsPage = () => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState("");
  const [quarter, setQuarter] = useState("Q1");
  const [year, setYear] = useState(new Date().getFullYear());
  const [cost, setCost] = useState({
    land_acquisition_cost: 0,
    development_rights_premium: 0,
    tdr_cost: 0,
    stamp_duty: 0,
    government_charges: 0,
    encumbrance_removal: 0,
    construction_cost: 0,
    infrastructure_cost: 0,
    equipment_cost: 0,
    taxes_statutory: 0,
    finance_cost: 0,
    estimated_land_cost: 0,
    estimated_development_cost: 0,
    // New fields for matching structure
    site_development_cost: 0,
    salaries: 0,
    consultants_fee: 0,
    site_overheads: 0,
    services_cost: 0
  });
  const [saving, setSaving] = useState(false);
  
  // Estimated Development Cost breakdown (fixed values)
  const [estimatedDevCost, setEstimatedDevCost] = useState({
    buildings_cost: 0,
    infrastructure_cost: 0,
    // On Site Expenditure
    site_development_cost: 0,
    salaries: 0,
    consultants_fee: 0,
    site_overheads: 0,
    services_cost: 0,
    machinery_cost: 0,
    // Taxes & Finance
    taxes_premiums_fees: 0,
    finance_cost: 0,
    total: 0,
    is_locked: false
  });

  // Actual costs calculated from progress
  const [actualCosts, setActualCosts] = useState({
    construction_cost: 0,
    infrastructure_cost: 0,
    construction_completion: 0,
    infrastructure_completion: 0
  });
  
  // Actual Site Expenditure (from Construction Progress page)
  const [actualSiteExpenditure, setActualSiteExpenditure] = useState({
    site_development_cost: 0,
    salaries: 0,
    consultants_fee: 0,
    site_overheads: 0,
    services_cost: 0,
    machinery_cost: 0,
    total: 0
  });
  
  // Land Cost (from Land Cost page)
  const [landCost, setLandCost] = useState({
    estimated: { total: 0 },
    actual: { total: 0 }
  });

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchCost();
      fetchEstimatedDevCost();
      fetchActualCostsFromProgress();
      fetchActualSiteExpenditure();
      fetchLandCost();
    }
  }, [selectedProject, quarter, year]);

  const fetchProjects = async () => {
    const res = await axios.get(`${API}/projects`);
    setProjects(res.data);
    if (res.data.length > 0) setSelectedProject(res.data[0].project_id);
  };
  
  const fetchLandCost = async () => {
    try {
      const res = await axios.get(`${API}/land-cost/${selectedProject}`);
      setLandCost(res.data);
    } catch (err) {
      console.error("Failed to fetch land cost", err);
    }
  };
  
  const fetchActualSiteExpenditure = async () => {
    try {
      const res = await axios.get(`${API}/actual-site-expenditure/${selectedProject}?quarter=${quarter}&year=${year}`);
      setActualSiteExpenditure({
        site_development_cost: res.data.site_development_cost || 0,
        salaries: res.data.salaries || 0,
        consultants_fee: res.data.consultants_fee || 0,
        site_overheads: res.data.site_overheads || 0,
        services_cost: res.data.services_cost || 0,
        machinery_cost: res.data.machinery_cost || 0,
        total: res.data.total || 0
      });
    } catch (err) {
      console.error("Failed to fetch actual site expenditure", err);
    }
  };

  const fetchCost = async () => {
    try {
      const res = await axios.get(`${API}/project-costs?project_id=${selectedProject}&quarter=${quarter}&year=${year}`);
      if (res.data.length > 0) {
        setCost(res.data[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchEstimatedDevCost = async () => {
    try {
      const res = await axios.get(`${API}/estimated-development-cost/${selectedProject}`);
      const data = res.data;
      const total = (data.buildings_cost || 0) + 
                    (data.infrastructure_cost || 0) + 
                    (data.site_development_cost || 0) +
                    (data.salaries || 0) +
                    (data.consultants_fee || 0) + 
                    (data.site_overheads || 0) +
                    (data.services_cost || 0) +
                    (data.machinery_cost || 0) +
                    (data.taxes_premiums_fees || 0) +
                    (data.finance_cost || 0);
      
      setEstimatedDevCost({
        buildings_cost: data.buildings_cost || 0,
        infrastructure_cost: data.infrastructure_cost || 0,
        site_development_cost: data.site_development_cost || 0,
        salaries: data.salaries || 0,
        consultants_fee: data.consultants_fee || 0,
        site_overheads: data.site_overheads || 0,
        services_cost: data.services_cost || 0,
        machinery_cost: data.machinery_cost || 0,
        taxes_premiums_fees: data.taxes_premiums_fees || 0,
        finance_cost: data.finance_cost || 0,
        total: data.total_estimated_development_cost || total,
        is_locked: !data.is_draft
      });
    } catch (err) {
      console.error(err);
    }
  };

  // Fetch actual costs from construction progress
  const fetchActualCostsFromProgress = async () => {
    try {
      // Get all buildings with their costs
      const buildingsRes = await axios.get(`${API}/buildings?project_id=${selectedProject}`);
      const buildings = buildingsRes.data || [];
      
      // Get construction progress for each building
      const progressRes = await axios.get(`${API}/construction-progress?project_id=${selectedProject}&quarter=${quarter}&year=${year}`);
      const progressData = progressRes.data || [];
      
      // Calculate actual construction cost: Sum of (building cost × completion %)
      let totalConstructionActual = 0;
      let totalBuildingsCost = 0;
      
      buildings.forEach(building => {
        const buildingCost = building.estimated_cost || 0;
        totalBuildingsCost += buildingCost;
        
        const progress = progressData.find(p => p.building_id === building.building_id);
        const completion = progress?.overall_completion || 0;
        totalConstructionActual += buildingCost * completion / 100;
      });
      
      const avgConstructionCompletion = totalBuildingsCost > 0 
        ? (totalConstructionActual / totalBuildingsCost * 100) 
        : 0;
      
      // Get infrastructure progress
      const infraProgressRes = await axios.get(`${API}/infrastructure-progress?project_id=${selectedProject}&quarter=${quarter}&year=${year}`);
      const infraProgress = infraProgressRes.data?.[0];
      const infraCompletion = infraProgress?.overall_completion || 0;
      
      // Get infrastructure cost
      const infraCostRes = await axios.get(`${API}/infrastructure-costs/${selectedProject}`);
      const totalInfraCost = infraCostRes.data?.total_infrastructure_cost || 0;
      
      // Calculate actual infrastructure cost
      const infraActual = totalInfraCost * infraCompletion / 100;
      
      setActualCosts({
        construction_cost: totalConstructionActual,
        infrastructure_cost: infraActual,
        construction_completion: avgConstructionCompletion,
        infrastructure_completion: infraCompletion
      });
      
      // Update cost state with calculated values
      setCost(prev => ({
        ...prev,
        construction_cost: totalConstructionActual,
        infrastructure_cost: infraActual
      }));
      
    } catch (err) {
      console.error("Failed to fetch actual costs from progress", err);
    }
  };

  const refreshBuildingsInfraCost = async () => {
    try {
      const res = await axios.get(`${API}/estimated-development-cost/${selectedProject}/refresh-buildings`);
      setEstimatedDevCost(prev => {
        const updated = {
          ...prev,
          buildings_cost: res.data.buildings_cost,
          infrastructure_cost: res.data.infrastructure_cost
        };
        updated.total = updated.buildings_cost + updated.infrastructure_cost + 
                        updated.site_development_cost + updated.salaries +
                        updated.consultants_fee + updated.site_overheads +
                        updated.services_cost + updated.machinery_cost +
                        updated.taxes_premiums_fees + updated.finance_cost;
        return updated;
      });
      toast.success("Buildings & Infrastructure costs refreshed");
    } catch (err) {
      toast.error("Failed to refresh costs");
    }
  };

  const saveEstimatedDevCost = async () => {
    setSaving(true);
    try {
      await axios.post(`${API}/estimated-development-cost?project_id=${selectedProject}`, {
        site_development_cost: estimatedDevCost.site_development_cost,
        salaries: estimatedDevCost.salaries,
        consultants_fee: estimatedDevCost.consultants_fee,
        site_overheads: estimatedDevCost.site_overheads,
        services_cost: estimatedDevCost.services_cost,
        machinery_cost: estimatedDevCost.machinery_cost,
        taxes_premiums_fees: estimatedDevCost.taxes_premiums_fees,
        finance_cost: estimatedDevCost.finance_cost
      });
      toast.success("Estimated Development Cost saved and locked");
      fetchEstimatedDevCost();
    } catch (err) {
      toast.error("Failed to save estimated cost");
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field, value) => {
    setCost(prev => ({ ...prev, [field]: parseFloat(value) || 0 }));
  };

  const handleEstimatedChange = (field, value) => {
    const newValue = parseFloat(value) || 0;
    setEstimatedDevCost(prev => {
      const updated = { ...prev, [field]: newValue };
      updated.total = updated.buildings_cost + updated.infrastructure_cost + 
                      updated.site_development_cost + updated.salaries +
                      updated.consultants_fee + updated.site_overheads +
                      updated.services_cost + updated.machinery_cost +
                      updated.taxes_premiums_fees + updated.finance_cost;
      return updated;
    });
  };

  // Land cost totals from Land Cost page
  const estimatedLandTotal = landCost.estimated?.total || 0;
  const actualLandTotal = landCost.actual?.total || 0;
  
  // Use actual costs from progress for construction and infrastructure, and actual site expenditure
  const totalDevCost = actualCosts.construction_cost + actualCosts.infrastructure_cost + 
    (actualSiteExpenditure.total || 0) + 
    cost.taxes_statutory + cost.finance_cost;
  
  const totalEstimated = estimatedLandTotal + estimatedDevCost.total;
  const totalIncurred = actualLandTotal + totalDevCost;
  const balanceCost = totalEstimated - totalIncurred;

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.post(`${API}/project-costs`, {
        project_id: selectedProject,
        quarter,
        year,
        ...cost,
        // Map frontend field names to the backend model field names so that
        // total_cost_incurred and total_estimated_cost are stored correctly.
        construction_cost_actual: actualCosts.construction_cost,
        onsite_salaries: actualSiteExpenditure.salaries,
        onsite_consultants_fees: actualSiteExpenditure.consultants_fee,
        onsite_site_overheads: actualSiteExpenditure.site_overheads,
        onsite_services_cost: actualSiteExpenditure.services_cost,
        onsite_machinery_equipment: actualSiteExpenditure.machinery_cost,
        // Estimated totals from their authoritative sources
        estimated_land_cost: estimatedLandTotal,
        estimated_development_cost: estimatedDevCost.total,
        construction_cost_estimated: estimatedDevCost.buildings_cost + estimatedDevCost.infrastructure_cost,
      });
      toast.success("Cost data saved");
    } catch (err) {
      toast.error("Failed to save cost data");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-6" data-testid="project-costs-page">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 font-heading">Project Costs</h1>
          <p className="text-slate-600">Manage project cost data for Form-3 and Form-4</p>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label className="form-label">Project</Label>
                <Select value={selectedProject} onValueChange={setSelectedProject}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {projects.map(p => <SelectItem key={p.project_id} value={p.project_id}>{p.project_name}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="form-label">Quarter</Label>
                <Select value={quarter} onValueChange={setQuarter}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Q1">Q1</SelectItem>
                    <SelectItem value="Q2">Q2</SelectItem>
                    <SelectItem value="Q3">Q3</SelectItem>
                    <SelectItem value="Q4">Q4</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="form-label">Year</Label>
                <Select value={year.toString()} onValueChange={(v) => setYear(parseInt(v))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {[2023, 2024, 2025, 2026].map(y => <SelectItem key={y} value={y.toString()}>{y}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="bg-blue-50">
            <CardContent className="p-4">
              <p className="text-sm text-blue-600">Estimated Cost</p>
              <p className="text-xl font-bold text-blue-900 currency">{formatCurrency(totalEstimated)}</p>
            </CardContent>
          </Card>
          <Card className="bg-emerald-50">
            <CardContent className="p-4">
              <p className="text-sm text-emerald-600">Cost Incurred</p>
              <p className="text-xl font-bold text-emerald-900 currency">{formatCurrency(totalIncurred)}</p>
            </CardContent>
          </Card>
          <Card className="bg-amber-50">
            <CardContent className="p-4">
              <p className="text-sm text-amber-600">Balance Cost</p>
              <p className="text-xl font-bold text-amber-900 currency">{formatCurrency(balanceCost)}</p>
            </CardContent>
          </Card>
          <Card className="bg-purple-50">
            <CardContent className="p-4">
              <p className="text-sm text-purple-600">Completion</p>
              <p className="text-xl font-bold text-purple-900">{totalEstimated > 0 ? formatNumber(totalIncurred / totalEstimated * 100, 1) : 0}%</p>
            </CardContent>
          </Card>
        </div>

        {/* Cost Forms - Two Column Layout: Estimated vs Actual */}
        <div className="grid lg:grid-cols-2 gap-6">
          
          {/* LEFT COLUMN: ESTIMATED COSTS */}
          <div className="space-y-6">
            {/* ESTIMATED LAND COST - Read Only */}
            <Card className="border-2 border-amber-200">
              <CardHeader className="bg-amber-50">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-lg text-amber-800">Estimated Land Cost</CardTitle>
                    <CardDescription>
                      <Badge variant="secondary" className="text-xs">Auto-populated from Land Cost page</Badge>
                    </CardDescription>
                  </div>
                  <Button variant="outline" size="sm" onClick={fetchLandCost}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="p-6 space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label className="form-label text-xs">a) Land Cost</Label>
                    <CurrencyInput value={landCost.estimated?.land_cost || 0} onChange={() => {}} disabled className="bg-amber-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">b) Premium Cost (FSI)</Label>
                    <CurrencyInput value={landCost.estimated?.premium_cost || 0} onChange={() => {}} disabled className="bg-amber-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">c) TDR Cost</Label>
                    <CurrencyInput value={landCost.estimated?.tdr_cost || 0} onChange={() => {}} disabled className="bg-amber-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">d) Statutory Cost</Label>
                    <CurrencyInput value={landCost.estimated?.statutory_cost || 0} onChange={() => {}} disabled className="bg-amber-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">e) Land Premium (ASR)</Label>
                    <CurrencyInput value={landCost.estimated?.land_premium || 0} onChange={() => {}} disabled className="bg-amber-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">f) Under Rehab Scheme</Label>
                    <CurrencyInput value={landCost.estimated?.under_rehab_scheme || 0} onChange={() => {}} disabled className="bg-amber-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">g) Est. Rehab Cost (Engineer)</Label>
                    <CurrencyInput value={landCost.estimated?.estimated_rehab_cost || 0} onChange={() => {}} disabled className="bg-amber-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">h) Actual Rehab Cost (CA)</Label>
                    <CurrencyInput value={landCost.estimated?.actual_rehab_cost || 0} onChange={() => {}} disabled className="bg-amber-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">i) Land Clearance Cost</Label>
                    <CurrencyInput value={landCost.estimated?.land_clearance_cost || 0} onChange={() => {}} disabled className="bg-amber-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">j) ASR Linked Premium</Label>
                    <CurrencyInput value={landCost.estimated?.asr_linked_premium || 0} onChange={() => {}} disabled className="bg-amber-50/50" />
                  </div>
                </div>
                <div className="bg-amber-100 p-3 rounded-lg mt-4">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-amber-700">Total Estimated Land Cost</span>
                    <span className="text-xl font-bold text-amber-800">{formatCurrency(estimatedLandTotal)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* ESTIMATED DEVELOPMENT COST */}
            <Card className="border-2 border-blue-200">
              <CardHeader className="bg-blue-50">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg text-blue-800">Estimated Development Cost</CardTitle>
                  <CardDescription>Fixed once saved - used in all quarterly reports</CardDescription>
                </div>
                {!estimatedDevCost.is_locked && (
                  <Button variant="outline" size="sm" onClick={refreshBuildingsInfraCost}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              {/* 1. Construction Cost */}
              <div className="space-y-3">
                <h4 className="font-semibold text-slate-700 border-b pb-1">1. Construction Cost</h4>
                <div className="grid grid-cols-2 gap-4 pl-4">
                  <div>
                    <Label className="form-label text-xs">a. Buildings</Label>
                    <CurrencyInput
                      value={estimatedDevCost.buildings_cost}
                      onChange={() => {}}
                      disabled
                      className="bg-slate-100"
                    />
                  </div>
                  <div>
                    <Label className="form-label text-xs">b. Infrastructure</Label>
                    <CurrencyInput
                      value={estimatedDevCost.infrastructure_cost}
                      onChange={() => {}}
                      disabled
                      className="bg-slate-100"
                    />
                  </div>
                </div>
              </div>

              {/* 2. On Site Expenditure */}
              <div className="space-y-3">
                <h4 className="font-semibold text-slate-700 border-b pb-1">2. On Site Expenditure for Development</h4>
                <div className="grid grid-cols-2 gap-4 pl-4">
                  <div>
                    <Label className="form-label text-xs">a. Development Cost (Site office, etc.)</Label>
                    <CurrencyInput
                      value={estimatedDevCost.site_development_cost || 0}
                      onChange={(val) => handleEstimatedChange("site_development_cost", val)}
                      disabled={estimatedDevCost.is_locked}
                    />
                  </div>
                  <div>
                    <Label className="form-label text-xs">b. Salaries</Label>
                    <CurrencyInput
                      value={estimatedDevCost.salaries || 0}
                      onChange={(val) => handleEstimatedChange("salaries", val)}
                      disabled={estimatedDevCost.is_locked}
                    />
                  </div>
                  <div>
                    <Label className="form-label text-xs">c. Consultants Fee</Label>
                    <CurrencyInput
                      value={estimatedDevCost.consultants_fee || 0}
                      onChange={(val) => handleEstimatedChange("consultants_fee", val)}
                      disabled={estimatedDevCost.is_locked}
                    />
                  </div>
                  <div>
                    <Label className="form-label text-xs">d. Site Over-heads</Label>
                    <CurrencyInput
                      value={estimatedDevCost.site_overheads || 0}
                      onChange={(val) => handleEstimatedChange("site_overheads", val)}
                      disabled={estimatedDevCost.is_locked}
                    />
                  </div>
                  <div>
                    <Label className="form-label text-xs">e. Cost of Services (Water, Elec.)</Label>
                    <CurrencyInput
                      value={estimatedDevCost.services_cost || 0}
                      onChange={(val) => handleEstimatedChange("services_cost", val)}
                      disabled={estimatedDevCost.is_locked}
                    />
                  </div>
                  <div>
                    <Label className="form-label text-xs">f. Machineries & Equipment</Label>
                    <CurrencyInput
                      value={estimatedDevCost.machinery_cost || 0}
                      onChange={(val) => handleEstimatedChange("machinery_cost", val)}
                      disabled={estimatedDevCost.is_locked}
                    />
                  </div>
                </div>
                <div className="pl-4 mt-3 pt-2 border-t border-dashed">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-slate-600">Sub-total (On Site Expenditure)</span>
                    <span className="font-semibold text-slate-700">{formatCurrency(
                      (estimatedDevCost.site_development_cost || 0) + 
                      (estimatedDevCost.salaries || 0) + 
                      (estimatedDevCost.consultants_fee || 0) + 
                      (estimatedDevCost.site_overheads || 0) + 
                      (estimatedDevCost.services_cost || 0) + 
                      (estimatedDevCost.machinery_cost || 0)
                    )}</span>
                  </div>
                </div>
              </div>

              {/* 3. Taxes, Premiums, Fees */}
              <div className="space-y-3">
                <h4 className="font-semibold text-slate-700 border-b pb-1">3. Payment of Taxes, Premiums, Fees Etc.</h4>
                <div className="pl-4">
                  <CurrencyInput
                    value={estimatedDevCost.taxes_premiums_fees || 0}
                    onChange={(val) => handleEstimatedChange("taxes_premiums_fees", val)}
                    disabled={estimatedDevCost.is_locked}
                  />
                </div>
              </div>

              {/* 4. Finance Cost */}
              <div className="space-y-3">
                <h4 className="font-semibold text-slate-700 border-b pb-1">4. Finance Cost</h4>
                <div className="pl-4">
                  <CurrencyInput
                    value={estimatedDevCost.finance_cost || 0}
                    onChange={(val) => handleEstimatedChange("finance_cost", val)}
                    disabled={estimatedDevCost.is_locked}
                  />
                </div>
              </div>

              <Separator className="my-4" />
              <div className="flex items-center justify-between bg-blue-50 p-4 rounded-lg">
                <div>
                  <p className="text-sm text-blue-600">Total Estimated Development Cost</p>
                  <p className="text-2xl font-bold text-blue-800 currency">{formatCurrency(estimatedDevCost.total)}</p>
                  {estimatedDevCost.is_locked && (
                    <Badge variant="secondary" className="mt-1">Locked</Badge>
                  )}
                </div>
                {!estimatedDevCost.is_locked && (
                  <Button onClick={saveEstimatedDevCost} className="bg-blue-600 hover:bg-blue-700">
                    Save & Lock
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
          </div>

          {/* RIGHT COLUMN: ACTUAL COSTS */}
          <div className="space-y-6">
            {/* ACTUAL LAND COST - Read Only */}
            <Card className="border-2 border-orange-200">
              <CardHeader className="bg-orange-50">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-lg text-orange-800">Actual Land Cost</CardTitle>
                    <CardDescription>
                      <Badge variant="secondary" className="text-xs">Auto-populated from Land Cost page</Badge>
                    </CardDescription>
                  </div>
                  <Button variant="outline" size="sm" onClick={fetchLandCost}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="p-6 space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label className="form-label text-xs">a) Land Cost</Label>
                    <CurrencyInput value={landCost.actual?.land_cost || 0} onChange={() => {}} disabled className="bg-orange-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">b) Premium Cost (FSI)</Label>
                    <CurrencyInput value={landCost.actual?.premium_cost || 0} onChange={() => {}} disabled className="bg-orange-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">c) TDR Cost</Label>
                    <CurrencyInput value={landCost.actual?.tdr_cost || 0} onChange={() => {}} disabled className="bg-orange-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">d) Statutory Cost</Label>
                    <CurrencyInput value={landCost.actual?.statutory_cost || 0} onChange={() => {}} disabled className="bg-orange-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">e) Land Premium (ASR)</Label>
                    <CurrencyInput value={landCost.actual?.land_premium || 0} onChange={() => {}} disabled className="bg-orange-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">f) Under Rehab Scheme</Label>
                    <CurrencyInput value={landCost.actual?.under_rehab_scheme || 0} onChange={() => {}} disabled className="bg-orange-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">g) Est. Rehab Cost (Engineer)</Label>
                    <CurrencyInput value={landCost.actual?.estimated_rehab_cost || 0} onChange={() => {}} disabled className="bg-orange-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">h) Actual Rehab Cost (CA)</Label>
                    <CurrencyInput value={landCost.actual?.actual_rehab_cost || 0} onChange={() => {}} disabled className="bg-orange-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">i) Land Clearance Cost</Label>
                    <CurrencyInput value={landCost.actual?.land_clearance_cost || 0} onChange={() => {}} disabled className="bg-orange-50/50" />
                  </div>
                  <div>
                    <Label className="form-label text-xs">j) ASR Linked Premium</Label>
                    <CurrencyInput value={landCost.actual?.asr_linked_premium || 0} onChange={() => {}} disabled className="bg-orange-50/50" />
                  </div>
                </div>
                <div className="bg-orange-100 p-3 rounded-lg mt-4">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-orange-700">Total Actual Land Cost</span>
                    <span className="text-xl font-bold text-orange-800">{formatCurrency(actualLandTotal)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* ACTUAL DEVELOPMENT COST */}
            <Card className="border-2 border-emerald-200">
              <CardHeader className="bg-emerald-50">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-lg text-emerald-800">Actual Development Cost</CardTitle>
                    <CardDescription>Cost incurred till date</CardDescription>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => { fetchActualCostsFromProgress(); fetchActualSiteExpenditure(); }}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                  </Button>
                </div>
              </CardHeader>
            <CardContent className="p-6 space-y-6">
              {/* 1. Construction Cost */}
              <div className="space-y-3">
                <h4 className="font-semibold text-slate-700 border-b pb-1">1. Construction Cost</h4>
                <div className="grid grid-cols-2 gap-4 pl-4">
                  <div>
                    <Label className="form-label text-xs">a. Buildings</Label>
                    <CurrencyInput
                      value={actualCosts.construction_cost}
                      onChange={() => {}}
                      disabled
                      className="bg-emerald-50 border-emerald-200"
                    />
                    <p className="text-xs text-emerald-600 mt-1">{formatNumber(actualCosts.construction_completion, 1)}% done</p>
                  </div>
                  <div>
                    <Label className="form-label text-xs">b. Infrastructure</Label>
                    <CurrencyInput
                      value={actualCosts.infrastructure_cost}
                      onChange={() => {}}
                      disabled
                      className="bg-emerald-50 border-emerald-200"
                    />
                    <p className="text-xs text-emerald-600 mt-1">{formatNumber(actualCosts.infrastructure_completion, 1)}% done</p>
                  </div>
                </div>
              </div>

              {/* 2. On Site Expenditure */}
              <div className="space-y-3">
                <h4 className="font-semibold text-slate-700 border-b pb-1">
                  2. On Site Expenditure for Development
                  <Badge variant="secondary" className="ml-2 text-xs">Auto-populated</Badge>
                </h4>
                <p className="text-xs text-slate-500 pl-4">Data entered in Construction Progress page</p>
                <div className="grid grid-cols-2 gap-4 pl-4">
                  <div>
                    <Label className="form-label text-xs">a. Development Cost (Site office, etc.)</Label>
                    <CurrencyInput
                      value={actualSiteExpenditure.site_development_cost || 0}
                      onChange={() => {}}
                      disabled
                      className="bg-emerald-50 border-emerald-200"
                    />
                  </div>
                  <div>
                    <Label className="form-label text-xs">b. Salaries</Label>
                    <CurrencyInput
                      value={actualSiteExpenditure.salaries || 0}
                      onChange={() => {}}
                      disabled
                      className="bg-emerald-50 border-emerald-200"
                    />
                  </div>
                  <div>
                    <Label className="form-label text-xs">c. Consultants Fee</Label>
                    <CurrencyInput
                      value={actualSiteExpenditure.consultants_fee || 0}
                      onChange={() => {}}
                      disabled
                      className="bg-emerald-50 border-emerald-200"
                    />
                  </div>
                  <div>
                    <Label className="form-label text-xs">d. Site Over-heads</Label>
                    <CurrencyInput
                      value={actualSiteExpenditure.site_overheads || 0}
                      onChange={() => {}}
                      disabled
                      className="bg-emerald-50 border-emerald-200"
                    />
                  </div>
                  <div>
                    <Label className="form-label text-xs">e. Cost of Services (Water, Elec.)</Label>
                    <CurrencyInput
                      value={actualSiteExpenditure.services_cost || 0}
                      onChange={() => {}}
                      disabled
                      className="bg-emerald-50 border-emerald-200"
                    />
                  </div>
                  <div>
                    <Label className="form-label text-xs">f. Machineries & Equipment</Label>
                    <CurrencyInput
                      value={actualSiteExpenditure.machinery_cost || 0}
                      onChange={() => {}}
                      disabled
                      className="bg-emerald-50 border-emerald-200"
                    />
                  </div>
                </div>
                <div className="pl-4 mt-3 pt-2 border-t border-dashed">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-slate-600">Sub-total (On Site Expenditure)</span>
                    <span className="font-semibold text-emerald-700">{formatCurrency(actualSiteExpenditure.total || 0)}</span>
                  </div>
                </div>
              </div>

              {/* 3. Taxes, Premiums, Fees */}
              <div className="space-y-3">
                <h4 className="font-semibold text-slate-700 border-b pb-1">3. Payment of Taxes, Premiums, Fees Etc.</h4>
                <div className="pl-4">
                  <CurrencyInput
                    value={cost.taxes_statutory || 0}
                    onChange={(val) => handleChange("taxes_statutory", val)}
                  />
                </div>
              </div>

              {/* 4. Finance Cost */}
              <div className="space-y-3">
                <h4 className="font-semibold text-slate-700 border-b pb-1">4. Finance Cost</h4>
                <div className="pl-4">
                  <CurrencyInput
                    value={cost.finance_cost || 0}
                    onChange={(val) => handleChange("finance_cost", val)}
                  />
                </div>
              </div>

              <Separator className="my-4" />
              <div className="flex items-center justify-between bg-emerald-50 p-4 rounded-lg">
                <div>
                  <p className="text-sm text-emerald-600">Total Actual Development Cost</p>
                  <p className="text-2xl font-bold text-emerald-800 currency">{formatCurrency(totalDevCost)}</p>
                </div>
                <Button onClick={handleSave} className="bg-emerald-600 hover:bg-emerald-700">
                  Save Costs
                </Button>
              </div>
            </CardContent>
          </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
};

// Sales & Receivables Page

export default ProjectCostsPage;
