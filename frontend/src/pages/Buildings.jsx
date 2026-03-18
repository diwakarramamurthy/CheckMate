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

const BuildingsPage = () => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState("");
  const [buildings, setBuildings] = useState([]);
  const [buildingTypes, setBuildingTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [bulkDialogOpen, setBulkDialogOpen] = useState(false);
  const [editingBuilding, setEditingBuilding] = useState(null);
  const [saving, setSaving] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [buildingToDelete, setBuildingToDelete] = useState(null);
  const [activeTab, setActiveTab] = useState("buildings");
  
  // Infrastructure costs state
  const [infraTemplate, setInfraTemplate] = useState([]);
  const [infraCosts, setInfraCosts] = useState({});
  const [totalInfraCost, setTotalInfraCost] = useState(0);
  const [totalBuildingsCost, setTotalBuildingsCost] = useState(0);
  
  // On Site Expenditure state (Estimated)
  const [siteExpenditure, setSiteExpenditure] = useState({
    site_development_cost: 0,
    salaries: 0,
    consultants_fee: 0,
    site_overheads: 0,
    services_cost: 0,
    machinery_cost: 0
  });
  const [totalSiteExpenditure, setTotalSiteExpenditure] = useState(0);
  
  const defaultForm = {
    building_name: "",
    building_type: "residential_tower",
    parking_basement: 0,
    parking_stilt_ground: 0,
    parking_upper_level: 0,
    commercial_floors: 0,
    residential_floors: 0,
    apartments_per_floor: 0,
    apartment_classification: "NA",
    estimated_cost: 0
  };
  
  const [form, setForm] = useState(defaultForm);
  const [bulkForm, setBulkForm] = useState({
    building_names: "",
    ...defaultForm
  });

  useEffect(() => {
    fetchProjects();
    fetchBuildingTypes();
    fetchInfraTemplate();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchBuildings();
      fetchInfraCosts();
      fetchSiteExpenditure();
    }
  }, [selectedProject]);

  useEffect(() => {
    // Calculate totals
    const bldgTotal = buildings.reduce((sum, b) => sum + (b.estimated_cost || 0), 0);
    setTotalBuildingsCost(bldgTotal);
    
    let infraTotal = 0;
    infraTemplate.forEach(item => {
      const cost = infraCosts[item.id]?.estimated_cost || 0;
      const isApplicable = infraCosts[item.id]?.is_applicable !== false;
      if (isApplicable) infraTotal += cost;
    });
    setTotalInfraCost(infraTotal);
    
    // Calculate site expenditure total
    const siteTotal = (siteExpenditure.site_development_cost || 0) +
                      (siteExpenditure.salaries || 0) +
                      (siteExpenditure.consultants_fee || 0) +
                      (siteExpenditure.site_overheads || 0) +
                      (siteExpenditure.services_cost || 0) +
                      (siteExpenditure.machinery_cost || 0);
    setTotalSiteExpenditure(siteTotal);
  }, [buildings, infraCosts, infraTemplate, siteExpenditure]);

  const fetchProjects = async () => {
    try {
      const res = await axios.get(`${API}/projects`);
      setProjects(res.data);
      if (res.data.length > 0) {
        setSelectedProject(res.data[0].project_id);
      }
    } catch (err) {
      toast.error("Failed to load projects");
    } finally {
      setLoading(false);
    }
  };

  const fetchBuildingTypes = async () => {
    try {
      const res = await axios.get(`${API}/buildings/types`);
      setBuildingTypes(res.data.types || []);
    } catch (err) {
      console.error("Failed to load building types");
    }
  };

  const fetchInfraTemplate = async () => {
    try {
      const res = await axios.get(`${API}/infrastructure-costs/template`);
      setInfraTemplate(res.data.items || []);
    } catch (err) {
      console.error("Failed to load infrastructure template");
    }
  };

  const fetchInfraCosts = async () => {
    try {
      const res = await axios.get(`${API}/infrastructure-costs/${selectedProject}`);
      setInfraCosts(res.data.costs || {});
    } catch (err) {
      console.error("Failed to load infrastructure costs");
    }
  };

  const fetchSiteExpenditure = async () => {
    try {
      const res = await axios.get(`${API}/site-expenditure/${selectedProject}`);
      setSiteExpenditure(res.data || {
        site_development_cost: 0,
        salaries: 0,
        consultants_fee: 0,
        site_overheads: 0,
        services_cost: 0,
        machinery_cost: 0
      });
    } catch (err) {
      console.error("Failed to load site expenditure");
    }
  };

  const saveSiteExpenditure = async () => {
    setSaving(true);
    try {
      await axios.post(`${API}/site-expenditure?project_id=${selectedProject}`, siteExpenditure);
      toast.success("Site expenditure saved");
    } catch (err) {
      toast.error("Failed to save site expenditure");
    } finally {
      setSaving(false);
    }
  };

  const handleSiteExpenditureChange = (field, value) => {
    setSiteExpenditure(prev => ({ ...prev, [field]: parseFloat(value) || 0 }));
  };

  const fetchBuildings = async () => {
    try {
      const res = await axios.get(`${API}/buildings?project_id=${selectedProject}`);
      setBuildings(res.data);
    } catch (err) {
      toast.error("Failed to load buildings");
    }
  };

  const getTypeConfig = (typeValue) => {
    return buildingTypes.find(t => t.value === typeValue) || {};
  };

  const handleSubmit = async () => {
    if (!form.building_name.trim()) {
      toast.error("Building name is required");
      return;
    }
    setSaving(true);
    try {
      if (editingBuilding) {
        await axios.put(`${API}/buildings/${editingBuilding.building_id}`, form);
        toast.success("Building updated");
      } else {
        await axios.post(`${API}/buildings`, { ...form, project_id: selectedProject });
        toast.success("Building created");
      }
      setDialogOpen(false);
      setEditingBuilding(null);
      setForm(defaultForm);
      fetchBuildings();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to save building");
    } finally {
      setSaving(false);
    }
  };

  const handleBulkSubmit = async () => {
    const names = bulkForm.building_names.split('\n').map(n => n.trim()).filter(n => n);
    if (names.length === 0) {
      toast.error("Enter at least one building name");
      return;
    }
    setSaving(true);
    try {
      const template = { ...bulkForm };
      delete template.building_names;
      
      const res = await axios.post(`${API}/buildings/bulk`, {
        project_id: selectedProject,
        building_names: names,
        template
      });
      toast.success(`Created ${res.data.created} buildings`);
      setBulkDialogOpen(false);
      setBulkForm({ building_names: "", ...defaultForm });
      fetchBuildings();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to create buildings");
    } finally {
      setSaving(false);
    }
  };

  const openEdit = (building) => {
    setEditingBuilding(building);
    setForm({
      building_name: building.building_name,
      building_type: building.building_type || "residential_tower",
      parking_basement: building.parking_basement || 0,
      parking_stilt_ground: building.parking_stilt_ground || 0,
      parking_upper_level: building.parking_upper_level || 0,
      commercial_floors: building.commercial_floors || 0,
      residential_floors: building.residential_floors || 0,
      apartments_per_floor: building.apartments_per_floor || 0,
      apartment_classification: building.apartment_classification || "NA",
      estimated_cost: building.estimated_cost || 0
    });
    setDialogOpen(true);
  };

  const deleteBuilding = async (building) => {
    setBuildingToDelete(building);
    setDeleteDialogOpen(true);
  };

  const confirmDeleteBuilding = async () => {
    if (!buildingToDelete) return;
    try {
      await axios.delete(`${API}/buildings/${buildingToDelete.building_id}`);
      toast.success("Building deleted");
      fetchBuildings();
    } catch (err) {
      toast.error("Failed to delete building");
    } finally {
      setDeleteDialogOpen(false);
      setBuildingToDelete(null);
    }
  };

  // Infrastructure cost handlers
  const handleInfraCostChange = (itemId, value) => {
    setInfraCosts(prev => ({
      ...prev,
      [itemId]: {
        ...prev[itemId],
        estimated_cost: parseFloat(value) || 0,
        is_applicable: prev[itemId]?.is_applicable !== false
      }
    }));
  };

  const handleInfraApplicableChange = (itemId, isApplicable) => {
    setInfraCosts(prev => ({
      ...prev,
      [itemId]: {
        ...prev[itemId],
        is_applicable: isApplicable
      }
    }));
  };

  const saveInfraCosts = async () => {
    setSaving(true);
    try {
      await axios.post(`${API}/infrastructure-costs?project_id=${selectedProject}`, infraCosts);
      toast.success("Infrastructure costs saved");
    } catch (err) {
      toast.error("Failed to save infrastructure costs");
    } finally {
      setSaving(false);
    }
  };

  const getBuildingTypeLabel = (typeValue) => {
    const type = buildingTypes.find(t => t.value === typeValue);
    return type?.label || typeValue;
  };

  // Render form fields based on building type
  const renderFormFields = (formData, setFormData, isBulk = false) => {
    const typeConfig = getTypeConfig(formData.building_type);
    
    return (
      <div className="space-y-4">
        {!isBulk && (
          <div>
            <Label className="form-label">Building Name *</Label>
            <Input
              value={formData.building_name}
              onChange={(e) => setFormData(f => ({ ...f, building_name: e.target.value }))}
              placeholder="e.g., Tower A, Wing E-01"
              data-testid="building-name-input"
            />
          </div>
        )}
        
        {isBulk && (
          <div>
            <Label className="form-label">Building Names (one per line) *</Label>
            <Textarea
              value={formData.building_names}
              onChange={(e) => setFormData(f => ({ ...f, building_names: e.target.value }))}
              placeholder="Tower A&#10;Tower B&#10;Tower C"
              rows={4}
              data-testid="bulk-building-names-input"
            />
            <p className="text-xs text-slate-500 mt-1">Enter each building name on a new line</p>
          </div>
        )}

        <div>
          <Label className="form-label">Building Type *</Label>
          <Select 
            value={formData.building_type} 
            onValueChange={(v) => setFormData(f => ({ ...f, building_type: v, commercial_floors: 0 }))}
          >
            <SelectTrigger data-testid="building-type-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {buildingTypes.map(type => (
                <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Separator />
        
        <div>
          <Label className="form-label text-slate-700 font-semibold">Parking Configuration</Label>
          <div className="grid grid-cols-3 gap-3 mt-2">
            <div>
              <Label className="text-xs text-slate-500">Basement</Label>
              <Input
                type="number"
                min="0"
                value={formData.parking_basement}
                onChange={(e) => setFormData(f => ({ ...f, parking_basement: parseInt(e.target.value) || 0 }))}
                data-testid="parking-basement-input"
              />
            </div>
            <div>
              <Label className="text-xs text-slate-500">Stilt/Ground</Label>
              <Input
                type="number"
                min="0"
                value={formData.parking_stilt_ground}
                onChange={(e) => setFormData(f => ({ ...f, parking_stilt_ground: parseInt(e.target.value) || 0 }))}
              />
            </div>
            <div>
              <Label className="text-xs text-slate-500">Upper Level</Label>
              <Input
                type="number"
                min="0"
                value={formData.parking_upper_level}
                onChange={(e) => setFormData(f => ({ ...f, parking_upper_level: parseInt(e.target.value) || 0 }))}
              />
            </div>
          </div>
        </div>

        <Separator />

        <div>
          <Label className="form-label text-slate-700 font-semibold">Floor Configuration</Label>
          <div className="grid grid-cols-2 gap-4 mt-2">
            {typeConfig.has_commercial && (
              <div>
                <Label className="text-xs text-slate-500">Commercial Floors</Label>
                <Input
                  type="number"
                  min="0"
                  value={formData.commercial_floors}
                  onChange={(e) => setFormData(f => ({ ...f, commercial_floors: parseInt(e.target.value) || 0 }))}
                  data-testid="commercial-floors-input"
                />
              </div>
            )}
            <div className={typeConfig.has_commercial ? "" : "col-span-2"}>
              <Label className="text-xs text-slate-500">Residential Floors</Label>
              <Input
                type="number"
                min="0"
                value={formData.residential_floors}
                onChange={(e) => setFormData(f => ({ ...f, residential_floors: parseInt(e.target.value) || 0 }))}
                data-testid="residential-floors-input"
              />
            </div>
          </div>
        </div>

        {typeConfig.has_apartments_per_floor && (
          <div>
            <Label className="form-label">Apartments per Floor</Label>
            <Input
              type="number"
              min="0"
              value={formData.apartments_per_floor}
              onChange={(e) => setFormData(f => ({ ...f, apartments_per_floor: parseInt(e.target.value) || 0 }))}
              data-testid="apartments-per-floor-input"
            />
          </div>
        )}

        {typeConfig.has_apartments_per_floor && (
          <div>
            <Label className="form-label">Apartment Classification</Label>
            <Select
              value={formData.apartment_classification || "NA"}
              onValueChange={(v) => setFormData(f => ({ ...f, apartment_classification: v }))}
            >
              <SelectTrigger data-testid="apartment-classification-select">
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                {["Studio", "1 BHK", "1.5 BHK", "2 BHK", "3 BHK", "4 BHK", "Pent-house", "NA"].map(c => (
                  <SelectItem key={c} value={c}>{c === "NA" ? "NA (Not Applicable / Mixed)" : c}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        <Separator />

        <div>
          <Label className="form-label">Estimated Cost (₹)</Label>
          <Input
            type="number"
            min="0"
            value={formData.estimated_cost}
            onChange={(e) => setFormData(f => ({ ...f, estimated_cost: parseFloat(e.target.value) || 0 }))}
            data-testid="estimated-cost-input"
          />
        </div>
      </div>
    );
  };

  return (
    <Layout>
      <div className="space-y-6" data-testid="buildings-page">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 font-heading">Buildings & Infrastructure</h1>
            <p className="text-slate-600">Manage buildings and infrastructure development costs</p>
          </div>
          <Select value={selectedProject} onValueChange={setSelectedProject}>
            <SelectTrigger className="w-48" data-testid="project-select">
              <SelectValue placeholder="Select project" />
            </SelectTrigger>
            <SelectContent>
              {projects.map((p) => (
                <SelectItem key={p.project_id} value={p.project_id}>{p.project_name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Summary Cards */}
        {selectedProject && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="text-sm text-slate-500">Total Buildings Cost</div>
                <div className="text-2xl font-bold text-slate-900">{formatCurrency(totalBuildingsCost)}</div>
                <div className="text-xs text-slate-400">{buildings.length} buildings</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-sm text-slate-500">Total Infrastructure Cost</div>
                <div className="text-2xl font-bold text-slate-900">{formatCurrency(totalInfraCost)}</div>
                <div className="text-xs text-slate-400">{infraTemplate.length} items</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-sm text-slate-500">On Site Expenditure</div>
                <div className="text-2xl font-bold text-slate-900">{formatCurrency(totalSiteExpenditure)}</div>
                <div className="text-xs text-slate-400">Estimated costs</div>
              </CardContent>
            </Card>
            <Card className="bg-blue-50">
              <CardContent className="p-4">
                <div className="text-sm text-blue-600 font-medium">Total Estimated</div>
                <div className="text-2xl font-bold text-blue-700">{formatCurrency(totalBuildingsCost + totalInfraCost + totalSiteExpenditure)}</div>
                <div className="text-xs text-blue-500">Construction + Site Exp.</div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex gap-2 border-b border-slate-200 pb-2">
          <Button
            variant={activeTab === "buildings" ? "default" : "outline"}
            onClick={() => setActiveTab("buildings")}
            className={activeTab === "buildings" ? "bg-blue-600" : ""}
          >
            <Building className="h-4 w-4 mr-2" />
            Buildings ({buildings.length})
          </Button>
          <Button
            variant={activeTab === "infrastructure" ? "default" : "outline"}
            onClick={() => setActiveTab("infrastructure")}
            className={activeTab === "infrastructure" ? "bg-blue-600" : ""}
          >
            <FileSpreadsheet className="h-4 w-4 mr-2" />
            Infrastructure Works
          </Button>
          <Button
            variant={activeTab === "site-expenditure" ? "default" : "outline"}
            onClick={() => setActiveTab("site-expenditure")}
            className={activeTab === "site-expenditure" ? "bg-blue-600" : ""}
          >
            <IndianRupee className="h-4 w-4 mr-2" />
            On Site Expenditure
          </Button>
        </div>

        {!selectedProject ? (
          <Card className="text-center py-12">
            <p className="text-slate-600">Please select a project first</p>
          </Card>
        ) : activeTab === "buildings" ? (
          /* Buildings Tab */
          <>
            <div className="flex justify-end gap-3">
              {/* Bulk Add Dialog */}
              <Dialog open={bulkDialogOpen} onOpenChange={setBulkDialogOpen}>
                <DialogTrigger asChild>
                  <Button 
                    variant="outline"
                    onClick={() => setBulkForm({ building_names: "", ...defaultForm })}
                    data-testid="bulk-add-btn"
                  >
                    <FileSpreadsheet className="h-4 w-4 mr-2" />
                    Bulk Add
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>Bulk Add Buildings</DialogTitle>
                    <DialogDescription>Create multiple buildings with the same configuration</DialogDescription>
                  </DialogHeader>
                  <ScrollArea className="max-h-[60vh] pr-4">
                    {renderFormFields(bulkForm, setBulkForm, true)}
                  </ScrollArea>
                  <DialogFooter className="mt-4">
                    <Button variant="outline" onClick={() => setBulkDialogOpen(false)}>Cancel</Button>
                    <Button onClick={handleBulkSubmit} className="bg-blue-600 hover:bg-blue-700" disabled={saving} data-testid="bulk-save-btn">
                      {saving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                      Create Buildings
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
              
              {/* Single Add Dialog */}
              <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogTrigger asChild>
                  <Button 
                    className="bg-blue-600 hover:bg-blue-700"
                    onClick={() => {
                      setEditingBuilding(null);
                      setForm(defaultForm);
                    }}
                    data-testid="add-building-btn"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Building
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>{editingBuilding ? "Edit" : "Add"} Building</DialogTitle>
                    <DialogDescription>Configure building type and floor details</DialogDescription>
                  </DialogHeader>
                  <ScrollArea className="max-h-[60vh] pr-4">
                    {renderFormFields(form, setForm, false)}
                  </ScrollArea>
                  <DialogFooter className="mt-4">
                    <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
                    <Button onClick={handleSubmit} className="bg-blue-600 hover:bg-blue-700" disabled={saving} data-testid="save-building-btn">
                      {saving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                      {editingBuilding ? "Update" : "Create"} Building
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>

            {buildings.length === 0 ? (
              <Card className="text-center py-12">
                <Building className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600 mb-2">No buildings added yet.</p>
                <p className="text-sm text-slate-500">Click "Add Building" or "Bulk Add" to create buildings.</p>
              </Card>
            ) : (
              <Card>
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Building Name</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead className="text-center">Parking</TableHead>
                        <TableHead className="text-center">Floors</TableHead>
                        <TableHead className="text-center">Units</TableHead>
                        <TableHead className="text-right">Est. Cost</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {buildings.map((b) => (
                        <TableRow key={b.building_id} data-testid={`building-row-${b.building_id}`}>
                          <TableCell className="font-medium">{b.building_name}</TableCell>
                          <TableCell>
                            <Badge variant="secondary" className="text-xs">
                              {getBuildingTypeLabel(b.building_type).split(' ').slice(0, 2).join(' ')}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-center">
                            <span className="text-sm" title="Basement / Stilt / Upper">
                              {b.parking_basement || 0}/{b.parking_stilt_ground || 0}/{b.parking_upper_level || 0}
                            </span>
                          </TableCell>
                          <TableCell className="text-center">
                            <span className="text-sm">
                              {b.building_type === "mixed_tower" 
                                ? `${b.commercial_floors || 0}C + ${b.residential_floors || 0}R`
                                : b.residential_floors || b.floors || 0
                              }
                            </span>
                          </TableCell>
                          <TableCell className="text-center">{b.units || 0}</TableCell>
                          <TableCell className="text-right currency">{formatCurrency(b.estimated_cost)}</TableCell>
                          <TableCell className="text-right">
                            <Button variant="ghost" size="icon" onClick={() => openEdit(b)} data-testid={`edit-building-${b.building_id}`}>
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="icon" onClick={() => deleteBuilding(b)} data-testid={`delete-building-${b.building_id}`}>
                              <Trash2 className="h-4 w-4 text-red-500" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                      {/* Total Row */}
                      <TableRow className="bg-slate-50 font-semibold">
                        <TableCell colSpan={5} className="text-right">Total Buildings Cost:</TableCell>
                        <TableCell className="text-right currency">{formatCurrency(totalBuildingsCost)}</TableCell>
                        <TableCell></TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </div>
              </Card>
            )}
          </>
        ) : activeTab === "infrastructure" ? (
          /* Infrastructure Tab */
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Project Infrastructure Works</CardTitle>
              <p className="text-sm text-slate-500">Enter estimated cost for each infrastructure item. Mark N/A for items not applicable to your project.</p>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow className="bg-slate-50">
                    <TableHead className="w-8">N/A</TableHead>
                    <TableHead>Infrastructure Item</TableHead>
                    <TableHead className="text-center w-20">Wt. %</TableHead>
                    <TableHead className="text-right w-48">Estimated Cost (₹)</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {infraTemplate.map((item, idx) => {
                    const itemData = infraCosts[item.id] || { estimated_cost: 0, is_applicable: true };
                    const isNA = itemData.is_applicable === false;
                    
                    return (
                      <TableRow key={item.id} className={isNA ? "bg-slate-100 opacity-60" : ""}>
                        <TableCell>
                          <input
                            type="checkbox"
                            checked={isNA}
                            onChange={(e) => handleInfraApplicableChange(item.id, !e.target.checked)}
                            className="h-4 w-4 rounded border-slate-300"
                            title="Mark as Not Applicable"
                          />
                        </TableCell>
                        <TableCell className={`font-medium ${isNA ? "line-through text-slate-400" : ""}`}>
                          <span className="text-slate-500 mr-2">{idx + 1}.</span>
                          {item.name}
                        </TableCell>
                        <TableCell className="text-center">{item.weightage}%</TableCell>
                        <TableCell>
                          <Input
                            type="number"
                            min="0"
                            step="1000"
                            value={itemData.estimated_cost || ""}
                            onChange={(e) => handleInfraCostChange(item.id, e.target.value)}
                            disabled={isNA}
                            className="w-40 ml-auto text-right"
                            placeholder="0"
                          />
                        </TableCell>
                      </TableRow>
                    );
                  })}
                  {/* Total Row */}
                  <TableRow className="bg-blue-50 font-semibold">
                    <TableCell colSpan={3} className="text-right">Total Infrastructure Cost:</TableCell>
                    <TableCell className="text-right currency text-blue-700">{formatCurrency(totalInfraCost)}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
              
              <div className="flex justify-end mt-4">
                <Button onClick={saveInfraCosts} className="bg-blue-600 hover:bg-blue-700" disabled={saving}>
                  {saving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                  Save Infrastructure Costs
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : activeTab === "site-expenditure" ? (
          /* On Site Expenditure Tab */
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">On Site Expenditure for Development (Estimated)</CardTitle>
              <CardDescription>Enter estimated costs for site operations and development</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                <div>
                  <Label className="form-label">a. Development Cost (Site office, Toilets etc.)</Label>
                  <CurrencyInput
                    value={siteExpenditure.site_development_cost}
                    onChange={(val) => handleSiteExpenditureChange("site_development_cost", val)}
                  />
                </div>
                <div>
                  <Label className="form-label">b. Salaries</Label>
                  <CurrencyInput
                    value={siteExpenditure.salaries}
                    onChange={(val) => handleSiteExpenditureChange("salaries", val)}
                  />
                </div>
                <div>
                  <Label className="form-label">c. Consultants Fee</Label>
                  <CurrencyInput
                    value={siteExpenditure.consultants_fee}
                    onChange={(val) => handleSiteExpenditureChange("consultants_fee", val)}
                  />
                </div>
                <div>
                  <Label className="form-label">d. Site Over-heads</Label>
                  <CurrencyInput
                    value={siteExpenditure.site_overheads}
                    onChange={(val) => handleSiteExpenditureChange("site_overheads", val)}
                  />
                </div>
                <div>
                  <Label className="form-label">e. Cost of Services (Water, Electricity etc.)</Label>
                  <CurrencyInput
                    value={siteExpenditure.services_cost}
                    onChange={(val) => handleSiteExpenditureChange("services_cost", val)}
                  />
                </div>
                <div>
                  <Label className="form-label">f. Cost of Machineries and Equipment</Label>
                  <CurrencyInput
                    value={siteExpenditure.machinery_cost}
                    onChange={(val) => handleSiteExpenditureChange("machinery_cost", val)}
                  />
                </div>
              </div>
              
              <Separator />
              
              <div className="flex items-center justify-between bg-blue-50 p-4 rounded-lg">
                <div>
                  <p className="text-sm text-blue-600">Total On Site Expenditure (Estimated)</p>
                  <p className="text-2xl font-bold text-blue-800">{formatCurrency(totalSiteExpenditure)}</p>
                </div>
                <Button onClick={saveSiteExpenditure} className="bg-blue-600 hover:bg-blue-700" disabled={saving}>
                  {saving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                  Save Site Expenditure
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : null}
      </div>

      {/* Delete Building Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Building</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{buildingToDelete?.building_name}"? This will also delete all construction progress and cost data associated with this building. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDeleteBuilding} className="bg-red-600 hover:bg-red-700">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Layout>
  );
};

// Continue in next part due to length...
// Construction Progress Page, Costs Page, Sales Page, Reports Page, Import Page

// I'll create these as separate components to keep the code organized


export default BuildingsPage;
