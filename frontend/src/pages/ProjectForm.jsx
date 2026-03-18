import { useState, useEffect } from "react";
import { useNavigate, Link, useLocation } from "react-router-dom";
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

const ProjectFormPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const pathname = location.pathname;
  const isEdit = pathname.includes("/edit");
  const projectId = isEdit ? pathname.split("/")[2] : null;
  
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState("basic");
  const [form, setForm] = useState({
    // Basic Info
    project_name: "",
    state: "GOA",
    rera_number: "",
    promoter_name: "",
    promoter_address: "",
    project_address: "",
    
    // Location & Land Details
    survey_number: "",
    plot_number: "",
    chalta_number: "",
    village: "",
    taluka: "",
    district: "",
    ward: "",
    municipality: "",
    pin_code: "",
    
    // Boundaries
    boundary_north: "",
    boundary_south: "",
    boundary_east: "",
    boundary_west: "",
    
    // Project Registration
    rera_registration_date: "",
    rera_validity_date: "",
    project_phase: "",
    
    // Project Details
    plot_area: "",
    total_built_up_area: "",
    project_start_date: "",
    expected_completion_date: "",
    
    // Designated Bank Account
    designated_bank_name: "",
    designated_account_number: "",
    designated_ifsc_code: "",
    
    // Professional - Architect
    architect_name: "",
    architect_license: "",
    architect_address: "",
    architect_contact: "",
    architect_email: "",
    
    // Professional - Engineer
    engineer_name: "",
    engineer_license: "",
    engineer_address: "",
    engineer_contact: "",
    engineer_email: "",
    
    // Professional - Consultants
    structural_consultant_name: "",
    structural_consultant_license: "",
    mep_consultant_name: "",
    mep_consultant_license: "",
    site_supervisor_name: "",
    quantity_surveyor_name: "",
    
    // Professional - CA
    ca_name: "",
    ca_firm_name: "",
    ca_membership_number: "",
    ca_address: "",
    ca_contact: "",
    ca_email: "",
    
    // Professional - Auditor
    auditor_name: "",
    auditor_firm_name: "",
    auditor_membership_number: "",
    auditor_address: "",
    auditor_contact: "",
    auditor_email: "",
    
    // Planning Authority
    planning_authority_name: ""
  });

  useEffect(() => {
    if (isEdit) {
      fetchProject();
    }
  }, [isEdit, projectId]);

  const fetchProject = async () => {
    try {
      const res = await axios.get(`${API}/projects/${projectId}`);
      setForm(res.data);
    } catch (err) {
      toast.error("Failed to load project");
      navigate("/projects");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (isEdit) {
        await axios.put(`${API}/projects/${projectId}`, form);
        toast.success("Project updated");
      } else {
        await axios.post(`${API}/projects`, form);
        toast.success("Project created");
      }
      navigate("/projects");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to save project");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-5xl mx-auto space-y-6" data-testid="project-form-page">
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <Link to="/projects" className="hover:text-blue-600">Projects</Link>
          <ChevronRight className="h-4 w-4" />
          <span>{isEdit ? "Edit" : "New"} Project</span>
        </div>

        <div>
          <h1 className="text-2xl font-bold text-slate-900 font-heading">
            {isEdit ? "Edit Project" : "Create New Project"}
          </h1>
          <p className="text-slate-600">Enter all project details for RERA compliance reporting</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Tab Navigation */}
          <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-2">
            {[
              { id: "basic", label: "Basic Info" },
              { id: "location", label: "Location & Boundaries" },
              { id: "registration", label: "RERA & Bank" },
              { id: "architect", label: "Architect & Engineer" },
              { id: "consultants", label: "Consultants" },
              { id: "ca", label: "CA & Auditor" },
            ].map(tab => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                  activeTab === tab.id 
                    ? "bg-blue-600 text-white" 
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Basic Info Tab */}
          {activeTab === "basic" && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <Label className="form-label">Project Name *</Label>
                  <Input value={form.project_name} onChange={(e) => handleChange("project_name", e.target.value)} required data-testid="project-name-input" />
                </div>
                <div>
                  <Label className="form-label">State *</Label>
                  <Select value={form.state} onValueChange={(v) => handleChange("state", v)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="GOA">Goa</SelectItem>
                      <SelectItem value="MAHARASHTRA">Maharashtra</SelectItem>
                      <SelectItem value="KARNATAKA">Karnataka</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label className="form-label">Project Phase</Label>
                  <Input value={form.project_phase} onChange={(e) => handleChange("project_phase", e.target.value)} placeholder="e.g., Phase 1, Phase 2" />
                </div>
                <div>
                  <Label className="form-label">Promoter Name *</Label>
                  <Input value={form.promoter_name} onChange={(e) => handleChange("promoter_name", e.target.value)} required />
                </div>
                <div className="md:col-span-2">
                  <Label className="form-label">Promoter Address</Label>
                  <Textarea value={form.promoter_address} onChange={(e) => handleChange("promoter_address", e.target.value)} rows={2} />
                </div>
                <div>
                  <Label className="form-label">Plot Area (sq.m)</Label>
                  <Input type="number" step="0.01" value={form.plot_area} onChange={(e) => handleChange("plot_area", e.target.value)} />
                </div>
                <div>
                  <Label className="form-label">Total Built-up Area (sq.m)</Label>
                  <Input type="number" step="0.01" value={form.total_built_up_area} onChange={(e) => handleChange("total_built_up_area", e.target.value)} />
                </div>
                <div>
                  <Label className="form-label">Project Start Date</Label>
                  <Input type="date" value={form.project_start_date} onChange={(e) => handleChange("project_start_date", e.target.value)} />
                </div>
                <div>
                  <Label className="form-label">Expected Completion Date</Label>
                  <Input type="date" value={form.expected_completion_date} onChange={(e) => handleChange("expected_completion_date", e.target.value)} />
                </div>
                <div>
                  <Label className="form-label">Planning Authority</Label>
                  <Input value={form.planning_authority_name} onChange={(e) => handleChange("planning_authority_name", e.target.value)} placeholder="e.g., TCP Goa" />
                </div>
              </CardContent>
            </Card>
          )}

          {/* Location & Boundaries Tab */}
          {activeTab === "location" && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Location & Boundaries (for RERA Forms)</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="md:col-span-2">
                    <Label className="form-label">Project Address</Label>
                    <Textarea value={form.project_address} onChange={(e) => handleChange("project_address", e.target.value)} rows={2} />
                  </div>
                  <div>
                    <Label className="form-label">PTS/Chalta Number</Label>
                    <Input value={form.chalta_number} onChange={(e) => handleChange("chalta_number", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Survey Number</Label>
                    <Input value={form.survey_number} onChange={(e) => handleChange("survey_number", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Plot Number</Label>
                    <Input value={form.plot_number} onChange={(e) => handleChange("plot_number", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Ward</Label>
                    <Input value={form.ward} onChange={(e) => handleChange("ward", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Village/Panchayat</Label>
                    <Input value={form.village} onChange={(e) => handleChange("village", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Municipality</Label>
                    <Input value={form.municipality} onChange={(e) => handleChange("municipality", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Taluka</Label>
                    <Input value={form.taluka} onChange={(e) => handleChange("taluka", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">District</Label>
                    <Input value={form.district} onChange={(e) => handleChange("district", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">PIN Code</Label>
                    <Input value={form.pin_code} onChange={(e) => handleChange("pin_code", e.target.value)} />
                  </div>
                </div>
                
                <Separator />
                <h4 className="font-semibold text-slate-700">Plot Boundaries (with lat/long coordinates)</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="form-label">Boundary - North</Label>
                    <Input value={form.boundary_north} onChange={(e) => handleChange("boundary_north", e.target.value)} placeholder="Description or coordinates" />
                  </div>
                  <div>
                    <Label className="form-label">Boundary - South</Label>
                    <Input value={form.boundary_south} onChange={(e) => handleChange("boundary_south", e.target.value)} placeholder="Description or coordinates" />
                  </div>
                  <div>
                    <Label className="form-label">Boundary - East</Label>
                    <Input value={form.boundary_east} onChange={(e) => handleChange("boundary_east", e.target.value)} placeholder="Description or coordinates" />
                  </div>
                  <div>
                    <Label className="form-label">Boundary - West</Label>
                    <Input value={form.boundary_west} onChange={(e) => handleChange("boundary_west", e.target.value)} placeholder="Description or coordinates" />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* RERA & Bank Tab */}
          {activeTab === "registration" && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">RERA Registration & Designated Bank Account</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="md:col-span-2">
                    <Label className="form-label">RERA Registration Number *</Label>
                    <Input value={form.rera_number} onChange={(e) => handleChange("rera_number", e.target.value)} required data-testid="rera-number-input" />
                  </div>
                  <div>
                    <Label className="form-label">Registration Date</Label>
                    <Input type="date" value={form.rera_registration_date} onChange={(e) => handleChange("rera_registration_date", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Validity Date</Label>
                    <Input type="date" value={form.rera_validity_date} onChange={(e) => handleChange("rera_validity_date", e.target.value)} />
                  </div>
                </div>
                
                <Separator />
                <h4 className="font-semibold text-slate-700">Designated Bank Account (Required for RERA Compliance)</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label className="form-label">Bank Name</Label>
                    <Input value={form.designated_bank_name} onChange={(e) => handleChange("designated_bank_name", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Account Number</Label>
                    <Input value={form.designated_account_number} onChange={(e) => handleChange("designated_account_number", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">IFSC Code</Label>
                    <Input value={form.designated_ifsc_code} onChange={(e) => handleChange("designated_ifsc_code", e.target.value)} />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Architect & Engineer Tab */}
          {activeTab === "architect" && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Architect & Engineer Details (for FORM-1, FORM-2, FORM-3)</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <h4 className="font-semibold text-slate-700">Architect / Licensed Surveyor</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="form-label">Name</Label>
                    <Input value={form.architect_name} onChange={(e) => handleChange("architect_name", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">License Number</Label>
                    <Input value={form.architect_license} onChange={(e) => handleChange("architect_license", e.target.value)} />
                  </div>
                  <div className="md:col-span-2">
                    <Label className="form-label">Address</Label>
                    <Input value={form.architect_address} onChange={(e) => handleChange("architect_address", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Contact Number</Label>
                    <Input value={form.architect_contact} onChange={(e) => handleChange("architect_contact", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Email</Label>
                    <Input type="email" value={form.architect_email} onChange={(e) => handleChange("architect_email", e.target.value)} />
                  </div>
                </div>
                
                <Separator />
                <h4 className="font-semibold text-slate-700">Project Engineer</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="form-label">Name</Label>
                    <Input value={form.engineer_name} onChange={(e) => handleChange("engineer_name", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">License Number</Label>
                    <Input value={form.engineer_license} onChange={(e) => handleChange("engineer_license", e.target.value)} />
                  </div>
                  <div className="md:col-span-2">
                    <Label className="form-label">Address</Label>
                    <Input value={form.engineer_address} onChange={(e) => handleChange("engineer_address", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Contact Number</Label>
                    <Input value={form.engineer_contact} onChange={(e) => handleChange("engineer_contact", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Email</Label>
                    <Input type="email" value={form.engineer_email} onChange={(e) => handleChange("engineer_email", e.target.value)} />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Consultants Tab */}
          {activeTab === "consultants" && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Technical Consultants (for RERA Forms)</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="form-label">Structural Consultant Name</Label>
                    <Input value={form.structural_consultant_name} onChange={(e) => handleChange("structural_consultant_name", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Structural Consultant License</Label>
                    <Input value={form.structural_consultant_license} onChange={(e) => handleChange("structural_consultant_license", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">MEP Consultant Name</Label>
                    <Input value={form.mep_consultant_name} onChange={(e) => handleChange("mep_consultant_name", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">MEP Consultant License</Label>
                    <Input value={form.mep_consultant_license} onChange={(e) => handleChange("mep_consultant_license", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Site Supervisor Name</Label>
                    <Input value={form.site_supervisor_name} onChange={(e) => handleChange("site_supervisor_name", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Quantity Surveyor Name</Label>
                    <Input value={form.quantity_surveyor_name} onChange={(e) => handleChange("quantity_surveyor_name", e.target.value)} />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* CA & Auditor Tab */}
          {activeTab === "ca" && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Chartered Accountant & Auditor (for FORM-4, FORM-5, FORM-6)</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <h4 className="font-semibold text-slate-700">Chartered Accountant</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="form-label">CA Name</Label>
                    <Input value={form.ca_name} onChange={(e) => handleChange("ca_name", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Firm Name</Label>
                    <Input value={form.ca_firm_name} onChange={(e) => handleChange("ca_firm_name", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Membership Number</Label>
                    <Input value={form.ca_membership_number} onChange={(e) => handleChange("ca_membership_number", e.target.value)} />
                  </div>
                  <div className="md:col-span-2">
                    <Label className="form-label">Address</Label>
                    <Input value={form.ca_address} onChange={(e) => handleChange("ca_address", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Contact Number</Label>
                    <Input value={form.ca_contact} onChange={(e) => handleChange("ca_contact", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Email</Label>
                    <Input type="email" value={form.ca_email} onChange={(e) => handleChange("ca_email", e.target.value)} />
                  </div>
                </div>
                
                <Separator />
                <h4 className="font-semibold text-slate-700">Statutory Auditor (for FORM-6 Annual Report)</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="form-label">Auditor Name</Label>
                    <Input value={form.auditor_name} onChange={(e) => handleChange("auditor_name", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Firm Name</Label>
                    <Input value={form.auditor_firm_name} onChange={(e) => handleChange("auditor_firm_name", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Membership Number</Label>
                    <Input value={form.auditor_membership_number} onChange={(e) => handleChange("auditor_membership_number", e.target.value)} />
                  </div>
                  <div className="md:col-span-2">
                    <Label className="form-label">Address</Label>
                    <Input value={form.auditor_address} onChange={(e) => handleChange("auditor_address", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Contact Number</Label>
                    <Input value={form.auditor_contact} onChange={(e) => handleChange("auditor_contact", e.target.value)} />
                  </div>
                  <div>
                    <Label className="form-label">Email</Label>
                    <Input type="email" value={form.auditor_email} onChange={(e) => handleChange("auditor_email", e.target.value)} />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Actions */}
          <div className="flex justify-between items-center">
            <div className="text-sm text-slate-500">
              Fields marked with * are required
            </div>
            <div className="flex gap-3">
              <Button type="button" variant="outline" onClick={() => navigate("/projects")}>
                Cancel
              </Button>
              <Button 
                type="submit" 
                className="bg-blue-600 hover:bg-blue-700"
                disabled={saving}
                data-testid="save-project-btn"
              >
                {saving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                {isEdit ? "Update Project" : "Create Project"}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </Layout>
  );
};

// Land Cost Page

export default ProjectFormPage;
