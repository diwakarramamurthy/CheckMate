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

const LandCostPage = () => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState("");
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(false);
  
  // Estimated land cost state
  const [estimated, setEstimated] = useState({
    land_cost: 0,
    premium_cost: 0,
    tdr_cost: 0,
    statutory_cost: 0,
    land_premium: 0,
    under_rehab_scheme: 0,
    estimated_rehab_cost: 0,
    actual_rehab_cost: 0,
    land_clearance_cost: 0,
    asr_linked_premium: 0
  });
  
  // Actual land cost state
  const [actual, setActual] = useState({
    land_cost: 0,
    premium_cost: 0,
    tdr_cost: 0,
    statutory_cost: 0,
    land_premium: 0,
    under_rehab_scheme: 0,
    estimated_rehab_cost: 0,
    actual_rehab_cost: 0,
    land_clearance_cost: 0,
    asr_linked_premium: 0
  });

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchLandCost();
    }
  }, [selectedProject]);

  const fetchProjects = async () => {
    try {
      const res = await axios.get(`${API}/projects`);
      setProjects(res.data);
      if (res.data.length > 0) setSelectedProject(res.data[0].project_id);
    } catch (err) {
      toast.error("Failed to fetch projects");
    }
  };

  const fetchLandCost = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/land-cost/${selectedProject}`);
      setEstimated(res.data.estimated || {
        land_cost: 0, premium_cost: 0, tdr_cost: 0, statutory_cost: 0,
        land_premium: 0, under_rehab_scheme: 0, estimated_rehab_cost: 0,
        actual_rehab_cost: 0, land_clearance_cost: 0, asr_linked_premium: 0
      });
      setActual(res.data.actual || {
        land_cost: 0, premium_cost: 0, tdr_cost: 0, statutory_cost: 0,
        land_premium: 0, under_rehab_scheme: 0, estimated_rehab_cost: 0,
        actual_rehab_cost: 0, land_clearance_cost: 0, asr_linked_premium: 0
      });
    } catch (err) {
      console.error("Failed to fetch land cost", err);
    } finally {
      setLoading(false);
    }
  };

  const handleEstimatedChange = (field, value) => {
    setEstimated(prev => ({ ...prev, [field]: parseFloat(value) || 0 }));
  };

  const handleActualChange = (field, value) => {
    setActual(prev => ({ ...prev, [field]: parseFloat(value) || 0 }));
  };

  const calculateTotal = (costs) => {
    // Only sum the actual cost fields, not the 'total' field itself
    const costFields = [
      'land_cost', 'premium_cost', 'tdr_cost', 'statutory_cost',
      'land_premium', 'under_rehab_scheme', 'estimated_rehab_cost',
      'actual_rehab_cost', 'land_clearance_cost', 'asr_linked_premium'
    ];
    return costFields.reduce((sum, field) => sum + (parseFloat(costs[field]) || 0), 0);
  };

  const saveLandCost = async () => {
    setSaving(true);
    try {
      await axios.post(`${API}/land-cost/${selectedProject}`, {
        estimated,
        actual
      });
      toast.success("Land cost saved successfully");
    } catch (err) {
      toast.error("Failed to save land cost");
    } finally {
      setSaving(false);
    }
  };

  const costFields = [
    { key: "land_cost", label: "a) Land Cost", description: "Amount paid for acquiring land or land rights" },
    { key: "premium_cost", label: "b) Premium Cost", description: "Amount of Premium payable for FSI, Fungible area to Statutory Authority" },
    { key: "tdr_cost", label: "c) TDR Cost", description: "Transfer of Development Rights cost" },
    { key: "statutory_cost", label: "d) Statutory Cost", description: "Amount paid - Stamp duty, transfer charges, registration fee etc." },
    { key: "land_premium", label: "e) Land Premium", description: "Amount payable as annual statement of rates (ASR) for redevelopment of Govt. land" },
    { key: "under_rehab_scheme", label: "f) Under Rehab Scheme", description: "Amount under rehabilitation scheme" },
    { key: "estimated_rehab_cost", label: "g) Estimated Cost for Rehab", description: "As certified by Engineer" },
    { key: "actual_rehab_cost", label: "h) Actual Cost of Rehab", description: "As certified by CA" },
    { key: "land_clearance_cost", label: "i) Cost towards Land Clearance", description: "For clearing encumbrances, legal/illegal occupants, Transit accommodation, Overhead cost etc." },
    { key: "asr_linked_premium", label: "j) Cost of ASR Linked Premium", description: "For ASR linked premium, fees, charges, security deposit for Rehabilitation projects" }
  ];

  const estimatedTotal = calculateTotal(estimated);
  const actualTotal = calculateTotal(actual);

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-800 font-heading">Land Cost</h1>
            <p className="text-slate-600 mt-1">Manage estimated and actual land costs for your project</p>
          </div>
        </div>

        {/* Project Selection */}
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-4">
              <Label className="form-label whitespace-nowrap">Select Project:</Label>
              <Select value={selectedProject} onValueChange={setSelectedProject}>
                <SelectTrigger className="w-80" data-testid="land-cost-project-select">
                  <SelectValue placeholder="Select a project" />
                </SelectTrigger>
                <SelectContent>
                  {projects.map((p) => (
                    <SelectItem key={p.project_id} value={p.project_id}>
                      {p.project_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {loading ? (
          <Card className="py-12 text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto text-blue-600" />
            <p className="text-slate-600 mt-2">Loading land cost data...</p>
          </Card>
        ) : selectedProject ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Estimated Land Cost */}
            <Card className="border-2 border-blue-200">
              <CardHeader className="bg-blue-50">
                <CardTitle className="text-lg text-blue-800">Estimated Land Cost</CardTitle>
                <CardDescription>Projected land acquisition costs</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 pt-4">
                {costFields.map((field) => (
                  <div key={`est-${field.key}`}>
                    <Label className="form-label text-sm">{field.label}</Label>
                    <p className="text-xs text-slate-500 mb-1">{field.description}</p>
                    <CurrencyInput
                      value={estimated[field.key]}
                      onChange={(val) => handleEstimatedChange(field.key, val)}
                      data-testid={`estimated-${field.key}`}
                    />
                  </div>
                ))}
                
                <Separator className="my-4" />
                
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-blue-700">Total Estimated Land Cost</span>
                    <span className="text-xl font-bold text-blue-800">{formatCurrency(estimatedTotal)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Actual Land Cost */}
            <Card className="border-2 border-emerald-200">
              <CardHeader className="bg-emerald-50">
                <CardTitle className="text-lg text-emerald-800">Actual Land Cost</CardTitle>
                <CardDescription>Actual costs incurred till date</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 pt-4">
                {costFields.map((field) => (
                  <div key={`act-${field.key}`}>
                    <Label className="form-label text-sm">{field.label}</Label>
                    <p className="text-xs text-slate-500 mb-1">{field.description}</p>
                    <CurrencyInput
                      value={actual[field.key]}
                      onChange={(val) => handleActualChange(field.key, val)}
                      data-testid={`actual-${field.key}`}
                    />
                  </div>
                ))}
                
                <Separator className="my-4" />
                
                <div className="bg-emerald-50 p-4 rounded-lg">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-emerald-700">Total Actual Land Cost</span>
                    <span className="text-xl font-bold text-emerald-800">{formatCurrency(actualTotal)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          <Card className="text-center py-12">
            <FolderKanban className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-600">Select a project to manage land costs</p>
          </Card>
        )}

        {/* Save Button */}
        {selectedProject && !loading && (
          <div className="flex justify-end">
            <Button 
              onClick={saveLandCost} 
              className="bg-blue-600 hover:bg-blue-700" 
              disabled={saving}
              data-testid="save-land-cost-btn"
            >
              {saving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Save Land Cost
            </Button>
          </div>
        )}
      </div>
    </Layout>
  );
};

// Buildings Page - Enhanced with building types, floor configurations, and bulk creation

export default LandCostPage;
