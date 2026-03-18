import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import {
  Building2, Plus, Pencil, Trash2, Download, ChevronRight, AlertCircle, CheckCircle2,
  Loader2, RefreshCw, Eye, ChevronDown, MapPin, TrendingUp, Users, IndianRupee, Building,
  FileSpreadsheet, ClipboardList, FileText, Upload, X, Menu, Settings
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

const ConstructionProgressPage = () => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState("");
  const [buildings, setBuildings] = useState([]);
  const [selectedBuilding, setSelectedBuilding] = useState("");
  const [quarter, setQuarter] = useState("Q1");
  const [year, setYear] = useState(new Date().getFullYear());
  const [template, setTemplate] = useState(null);
  const [towerActivities, setTowerActivities] = useState({});
  const [infraActivities, setInfraActivities] = useState({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState("tower");

  // Excel Import / Export state — single building
  const [importModalOpen, setImportModalOpen] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [downloadingTemplate, setDownloadingTemplate] = useState(false);

  // Excel Bulk Import / Export state — all buildings
  const [bulkImportModalOpen, setBulkImportModalOpen] = useState(false);
  const [bulkImportFile, setBulkImportFile] = useState(null);
  const [bulkImporting, setBulkImporting] = useState(false);
  const [bulkDownloading, setBulkDownloading] = useState(false);
  const [bulkImportResults, setBulkImportResults] = useState(null);
  const [expandedCategories, setExpandedCategories] = useState({});
  const [categoryCompletions, setCategoryCompletions] = useState({});
  const [overallCompletion, setOverallCompletion] = useState(0);
  const [infraOverallCompletion, setInfraOverallCompletion] = useState(0);
  const [weightageWarnings, setWeightageWarnings] = useState({ categories: {}, globalTotal: null });

  // Edit Weightages state
  const [weightageModalOpen, setWeightageModalOpen] = useState(false);
  const [draftWeightages, setDraftWeightages] = useState({ category_base_weightages: {}, activity_weightages: {} });
  const [savingWeightages, setSavingWeightages] = useState(false);
  const [buildingWeightageProfile, setBuildingWeightageProfile] = useState({ category_base_weightages: {}, activity_weightages: {} });

  // Actual Site Expenditure state
  const [actualSiteExpenditure, setActualSiteExpenditure] = useState({
    site_development_cost: 0,
    salaries: 0,
    consultants_fee: 0,
    site_overheads: 0,
    services_cost: 0,
    machinery_cost: 0
  });
  const [totalActualSiteExpenditure, setTotalActualSiteExpenditure] = useState(0);

  useEffect(() => {
    fetchProjects();
    fetchTemplate();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchBuildings();
      fetchActualSiteExpenditure();
    }
  }, [selectedProject]);

  useEffect(() => {
    if (selectedBuilding && template) {
      fetchProgress();
    }
  }, [selectedBuilding, quarter, year, template]);
  
  useEffect(() => {
    if (selectedProject && quarter && year) {
      fetchActualSiteExpenditure();
    }
  }, [selectedProject, quarter, year]);

  useEffect(() => {
    if (template) {
      calculateCompletions();
    }
  }, [towerActivities, infraActivities, template]);

  useEffect(() => {
    if (selectedBuilding && template) {
      fetchBuildingWeightages(selectedBuilding).then(profile => {
        applyWeightageProfile(profile);
      });
    }
  }, [selectedBuilding, template]);

  const fetchProjects = async () => {
    const res = await axios.get(`${API}/projects`);
    setProjects(res.data);
    if (res.data.length > 0) setSelectedProject(res.data[0].project_id);
  };

  const fetchBuildings = async () => {
    const res = await axios.get(`${API}/buildings?project_id=${selectedProject}`);
    setBuildings(res.data);
    if (res.data.length > 0) setSelectedBuilding(res.data[0].building_id);
  };

  const fetchBuildingWeightages = async (buildingId) => {
    try {
      const res = await axios.get(`${API}/buildings/${buildingId}/weightages`);
      const profile = res.data || { category_base_weightages: {}, activity_weightages: {} };
      setBuildingWeightageProfile(profile);
      return profile;
    } catch (err) {
      setBuildingWeightageProfile({ category_base_weightages: {}, activity_weightages: {} });
      return { category_base_weightages: {}, activity_weightages: {} };
    }
  };

  const fetchActualSiteExpenditure = async () => {
    if (!selectedProject) return;
    try {
      const res = await axios.get(`${API}/actual-site-expenditure/${selectedProject}?quarter=${quarter}&year=${year}`);
      setActualSiteExpenditure(res.data || {
        site_development_cost: 0,
        salaries: 0,
        consultants_fee: 0,
        site_overheads: 0,
        services_cost: 0,
        machinery_cost: 0
      });
      // Calculate total
      const total = (res.data?.site_development_cost || 0) +
                    (res.data?.salaries || 0) +
                    (res.data?.consultants_fee || 0) +
                    (res.data?.site_overheads || 0) +
                    (res.data?.services_cost || 0) +
                    (res.data?.machinery_cost || 0);
      setTotalActualSiteExpenditure(total);
    } catch (err) {
      console.error("Failed to fetch actual site expenditure", err);
    }
  };

  const handleActualSiteExpenditureChange = (field, value) => {
    const numValue = parseFloat(value) || 0;
    setActualSiteExpenditure(prev => {
      const updated = { ...prev, [field]: numValue };
      const total = (updated.site_development_cost || 0) +
                    (updated.salaries || 0) +
                    (updated.consultants_fee || 0) +
                    (updated.site_overheads || 0) +
                    (updated.services_cost || 0) +
                    (updated.machinery_cost || 0);
      setTotalActualSiteExpenditure(total);
      return updated;
    });
  };

  const saveActualSiteExpenditure = async () => {
    setSaving(true);
    try {
      await axios.post(
        `${API}/actual-site-expenditure?project_id=${selectedProject}&quarter=${quarter}&year=${year}`,
        actualSiteExpenditure
      );
      toast.success("Actual site expenditure saved");
    } catch (err) {
      toast.error("Failed to save actual site expenditure");
    } finally {
      setSaving(false);
    }
  };

  const fetchTemplate = async () => {
    try {
      const res = await axios.get(`${API}/construction-progress/detailed-template`);
      setTemplate(res.data);
      // Initialize activities with default values
      initializeActivities(res.data);
    } catch (err) {
      console.error("Failed to fetch template", err);
    }
  };

  const initializeActivities = (tmpl) => {
    const towerData = {};
    tmpl.tower_construction.categories.forEach(cat => {
      towerData[cat.id] = { _use_cost_weightage: false };
      cat.activities.forEach(act => {
        towerData[cat.id][act.id] = { completion: 0, is_applicable: true, cost: 0 };
      });
    });
    setTowerActivities(towerData);

    const infraData = {};
    tmpl.infrastructure_works.activities.forEach(act => {
      infraData[act.id] = { completion: 0, is_applicable: true };
    });
    setInfraActivities(infraData);
  };

  const fetchProgress = async () => {
    setLoading(true);
    try {
      // Fetch tower progress
      const res = await axios.get(
        `${API}/construction-progress?project_id=${selectedProject}&quarter=${quarter}&year=${year}`
      );
      const existing = res.data.find(p => p.building_id === selectedBuilding);
      if (existing?.tower_activities) {
        setTowerActivities(existing.tower_activities);
        setCategoryCompletions(existing.category_completions || {});
        setOverallCompletion(existing.overall_completion || 0);
      } else {
        initializeActivities(template);
      }

      // Fetch infrastructure progress
      const infraRes = await axios.get(
        `${API}/infrastructure-progress?project_id=${selectedProject}&quarter=${quarter}&year=${year}`
      );
      if (infraRes.data.length > 0) {
        setInfraActivities(infraRes.data[0].activities || {});
        setInfraOverallCompletion(infraRes.data[0].overall_completion || 0);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const calculateCompletions = () => {
    if (!template) return;

    // Calculate tower completion
    let totalApplicable = 0;
    let weightedCompletion = 0;
    const catComps = {};
    const newWarnings = { categories: {}, globalTotal: null };

    template.tower_construction.categories.forEach(cat => {
      const catData = towerActivities[cat.id] || {};
      const useCostWeightage = catData._use_cost_weightage || false;
      let catApplicable = 0;
      let catWeighted = 0;

      if (useCostWeightage) {
        // Cost-based mode: derive effective weightage from cost inputs
        const totalCost = cat.activities.reduce((sum, act) => {
          const actData = catData[act.id] || {};
          return actData.is_applicable !== false ? sum + (parseFloat(actData.cost) || 0) : sum;
        }, 0);
        const catBaseApplicable = cat.activities.reduce((sum, act) => {
          const actData = catData[act.id] || {};
          const actWt = (actData._custom_weightage != null && actData._custom_weightage !== "") ? parseFloat(actData._custom_weightage) || 0 : act.weightage;
          return actData.is_applicable !== false ? sum + actWt : sum;
        }, 0);

        cat.activities.forEach(act => {
          const actData = catData[act.id] || { completion: 0, is_applicable: true };
          if (actData.is_applicable !== false) {
            const cost = parseFloat(actData.cost) || 0;
            const actWt = (actData._custom_weightage != null && actData._custom_weightage !== "") ? parseFloat(actData._custom_weightage) || 0 : act.weightage;
            const effectiveWt = totalCost > 0
              ? (cost / totalCost) * catBaseApplicable
              : actWt;
            totalApplicable += effectiveWt;
            catApplicable += effectiveWt;
            weightedCompletion += effectiveWt * (actData.completion || 0) / 100;
            catWeighted += effectiveWt * (actData.completion || 0) / 100;
          }
        });
      } else {
        // Standard (custom or template) weightage mode
        cat.activities.forEach(act => {
          const actData = catData[act.id] || { completion: 0, is_applicable: true };
          if (actData.is_applicable !== false) {
            const effectiveWt = actData._custom_weightage !== undefined && actData._custom_weightage !== null && actData._custom_weightage !== ""
              ? parseFloat(actData._custom_weightage)
              : act.weightage;
            totalApplicable += effectiveWt;
            catApplicable += effectiveWt;
            weightedCompletion += effectiveWt * (actData.completion || 0) / 100;
            catWeighted += effectiveWt * (actData.completion || 0) / 100;
          }
        });
      }

      catComps[cat.id] = catApplicable > 0 ? (catWeighted / catApplicable * 100) : 0;

      // Validation: check if sub-activity weights sum to the category base weightage
      if (!useCostWeightage) {
        const subTotal = cat.activities.reduce((sum, act) => {
          const actData = catData[act.id] || {};
          const actWt = actData._custom_weightage !== undefined && actData._custom_weightage !== null && actData._custom_weightage !== ""
            ? parseFloat(actData._custom_weightage)
            : act.weightage;
          return sum + actWt;
        }, 0);
        const baseWt = catData._custom_base_weightage !== undefined && catData._custom_base_weightage !== null && catData._custom_base_weightage !== ""
          ? parseFloat(catData._custom_base_weightage)
          : cat.total_weightage;
        if (Math.abs(subTotal - baseWt) > 0.05) {
          newWarnings.categories[cat.id] = `Sub-activities sum to ${subTotal.toFixed(2)}% but Main Activity Base Weightage is ${baseWt.toFixed(2)}%`;
        }
      }
    });

    // Global validation: sum of all category base weightages should equal 100%
    const globalSum = template.tower_construction.categories.reduce((sum, cat) => {
      const catData = towerActivities[cat.id] || {};
      const baseWt = catData._custom_base_weightage !== undefined && catData._custom_base_weightage !== null && catData._custom_base_weightage !== ""
        ? parseFloat(catData._custom_base_weightage)
        : cat.total_weightage;
      return sum + baseWt;
    }, 0);
    if (Math.abs(globalSum - 100) > 0.05) {
      newWarnings.globalTotal = `Total of all Main Activity Base Weightages = ${globalSum.toFixed(2)}% (should equal 100%)`;
    }

    setWeightageWarnings(newWarnings);
    setCategoryCompletions(catComps);
    setOverallCompletion(totalApplicable > 0 ? (weightedCompletion / totalApplicable * 100) : 0);

    // Calculate infrastructure completion
    let infraTotal = 0;
    let infraWeighted = 0;
    template.infrastructure_works.activities.forEach(act => {
      const actData = infraActivities[act.id] || { completion: 0, is_applicable: true };
      if (actData.is_applicable) {
        infraTotal += act.weightage;
        infraWeighted += act.weightage * (actData.completion || 0) / 100;
      }
    });
    setInfraOverallCompletion(infraTotal > 0 ? (infraWeighted / infraTotal * 100) : 0);
  };

  const handleActivityChange = (categoryId, activityId, field, value) => {
    setTowerActivities(prev => ({
      ...prev,
      [categoryId]: {
        ...prev[categoryId],
        [activityId]: {
          ...prev[categoryId]?.[activityId],
          [field]: field === 'completion' ? Math.min(100, Math.max(0, parseFloat(value) || 0)) : value
        }
      }
    }));
  };

  const handleInfraChange = (activityId, field, value) => {
    setInfraActivities(prev => ({
      ...prev,
      [activityId]: {
        ...prev[activityId],
        [field]: field === 'completion' ? Math.min(100, Math.max(0, parseFloat(value) || 0)) : value
      }
    }));
  };

  const toggleCategory = (categoryId) => {
    setExpandedCategories(prev => ({ ...prev, [categoryId]: !prev[categoryId] }));
  };

  const handleCostModeToggle = (categoryId) => {
    setTowerActivities(prev => ({
      ...prev,
      [categoryId]: {
        ...prev[categoryId],
        _use_cost_weightage: !prev[categoryId]?._use_cost_weightage
      }
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Save tower progress
      const towerParams = new URLSearchParams({
        building_id: selectedBuilding,
        quarter,
        year: year.toString(),
        number_of_floors: (buildings.find(b => b.building_id === selectedBuilding)?.residential_floors || 1).toString()
      });
      
      await axios.post(`${API}/construction-progress/detailed?${towerParams.toString()}`, towerActivities);

      // Save infrastructure progress
      const infraParams = new URLSearchParams({
        project_id: selectedProject,
        quarter,
        year: year.toString()
      });
      
      await axios.post(`${API}/infrastructure-progress?${infraParams.toString()}`, infraActivities);

      toast.success("Progress saved successfully");
    } catch (err) {
      toast.error("Failed to save progress");
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  // ── Excel Template Download ──────────────────────────────────────────────
  const handleDownloadTemplate = async () => {
    if (!selectedBuilding || !selectedProject) {
      toast.error("Please select a project and building first");
      return;
    }
    setDownloadingTemplate(true);
    try {
      const params = new URLSearchParams({
        building_id: selectedBuilding,
        project_id: selectedProject,
        quarter,
        year: year.toString(),
      });
      const res = await axios.get(`${API}/construction-progress/excel-template?${params}`, {
        responseType: "blob",
      });
      const contentDisposition = res.headers["content-disposition"] || "";
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
      const filename = filenameMatch
        ? filenameMatch[1]
        : `construction_progress_${quarter}_${year}.xlsx`;
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success("Template downloaded successfully");
    } catch (err) {
      toast.error("Failed to download template");
      console.error(err);
    } finally {
      setDownloadingTemplate(false);
    }
  };

  // ── Excel Import ─────────────────────────────────────────────────────────
  const handleImportExcel = async () => {
    if (!importFile) {
      toast.error("Please select an Excel file first");
      return;
    }
    if (!selectedBuilding || !selectedProject) {
      toast.error("Please select a project and building first");
      return;
    }
    setImporting(true);
    try {
      const formData = new FormData();
      formData.append("file", importFile);
      const params = new URLSearchParams({
        building_id: selectedBuilding,
        project_id: selectedProject,
        quarter,
        year: year.toString(),
      });
      const res = await axios.post(
        `${API}/construction-progress/import-excel?${params}`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      const data = res.data;
      toast.success(
        `Imported successfully! Tower: ${data.tower_overall_completion?.toFixed(1)}% | Infrastructure: ${data.infra_overall_completion?.toFixed(1)}%`
      );
      setImportModalOpen(false);
      setImportFile(null);
      // Refresh progress data
      await fetchProgress();
    } catch (err) {
      const msg = err.response?.data?.detail || "Failed to import Excel file";
      toast.error(msg);
      console.error(err);
    } finally {
      setImporting(false);
    }
  };

  // ── Bulk Excel Template Download ────────────────────────────────────────
  const handleBulkDownloadTemplate = async () => {
    if (!selectedProject) {
      toast.error("Please select a project first");
      return;
    }
    setBulkDownloading(true);
    try {
      const params = new URLSearchParams({
        project_id: selectedProject,
        quarter,
        year: year.toString(),
      });
      const res = await axios.get(`${API}/construction-progress/bulk-excel-template?${params}`, {
        responseType: "blob",
      });
      const contentDisposition = res.headers["content-disposition"] || "";
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
      const filename = filenameMatch
        ? filenameMatch[1]
        : `bulk_construction_progress_${quarter}_${year}.xlsx`;
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success(`Bulk template downloaded — ${buildings.length} building(s) included`);
    } catch (err) {
      toast.error("Failed to download bulk template");
      console.error(err);
    } finally {
      setBulkDownloading(false);
    }
  };

  // ── Bulk Excel Import ────────────────────────────────────────────────────
  const handleBulkImportExcel = async () => {
    if (!bulkImportFile) {
      toast.error("Please select a bulk Excel file first");
      return;
    }
    if (!selectedProject) {
      toast.error("Please select a project first");
      return;
    }
    setBulkImporting(true);
    setBulkImportResults(null);
    try {
      const formData = new FormData();
      formData.append("file", bulkImportFile);
      const params = new URLSearchParams({
        project_id: selectedProject,
        quarter,
        year: year.toString(),
      });
      const res = await axios.post(
        `${API}/construction-progress/bulk-import-excel?${params}`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setBulkImportResults(res.data);
      toast.success(res.data.message);
      // Refresh progress for the currently selected building
      if (selectedBuilding) await fetchProgress();
    } catch (err) {
      const msg = err.response?.data?.detail || "Failed to bulk import Excel file";
      toast.error(msg);
      console.error(err);
    } finally {
      setBulkImporting(false);
    }
  };

  const saveBuildingWeightages = async () => {
    setSavingWeightages(true);
    try {
      // Validate: all category bases must sum to ~100
      const catSum = Object.values(draftWeightages.category_base_weightages)
        .reduce((s, v) => s + (parseFloat(v) || 0), 0);
      if (Math.abs(catSum - 100) > 0.1) {
        toast.error(`Category base weightages sum to ${catSum.toFixed(2)}% — must equal 100%`);
        setSavingWeightages(false);
        return;
      }
      await axios.put(`${API}/buildings/${selectedBuilding}/weightages`, draftWeightages);
      setBuildingWeightageProfile({ ...draftWeightages });
      // Apply the new profile to current towerActivities
      applyWeightageProfile({ ...draftWeightages });
      toast.success("Weightage profile saved for this building");
      setWeightageModalOpen(false);
    } catch (err) {
      toast.error("Failed to save weightage profile");
    } finally {
      setSavingWeightages(false);
    }
  };

  const applyWeightageProfile = (profile) => {
    if (!template) return;
    setTowerActivities(prev => {
      const next = { ...prev };
      template.tower_construction.categories.forEach(cat => {
        const catOverride = profile.category_base_weightages?.[cat.id];
        const actOverrides = profile.activity_weightages?.[cat.id] || {};
        next[cat.id] = { ...next[cat.id] };
        if (catOverride !== undefined && catOverride !== null && catOverride !== "") {
          next[cat.id]._custom_base_weightage = String(catOverride);
        }
        cat.activities.forEach(act => {
          const actOverride = actOverrides[act.id];
          next[cat.id][act.id] = { ...next[cat.id][act.id] };
          if (actOverride !== undefined && actOverride !== null && actOverride !== "") {
            next[cat.id][act.id]._custom_weightage = String(actOverride);
          }
        });
      });
      return next;
    });
  };

  const openWeightageModal = () => {
    if (!template) return;
    // Pre-populate draft with current effective values (custom overrides or template defaults)
    const catBases = {};
    const actWts = {};
    template.tower_construction.categories.forEach(cat => {
      const catData = towerActivities[cat.id] || {};
      catBases[cat.id] = catData._custom_base_weightage !== undefined && catData._custom_base_weightage !== null && catData._custom_base_weightage !== ""
        ? catData._custom_base_weightage
        : cat.total_weightage;
      actWts[cat.id] = {};
      cat.activities.forEach(act => {
        const actData = catData[act.id] || {};
        actWts[cat.id][act.id] = actData._custom_weightage !== undefined && actData._custom_weightage !== null && actData._custom_weightage !== ""
          ? actData._custom_weightage
          : act.weightage;
      });
    });
    setDraftWeightages({ category_base_weightages: catBases, activity_weightages: actWts });
    setWeightageModalOpen(true);
  };

  const getCompletionColor = (pct) => {
    if (pct >= 90) return "bg-green-500";
    if (pct >= 50) return "bg-blue-500";
    if (pct >= 25) return "bg-yellow-500";
    return "bg-slate-300";
  };

  return (
    <Layout>
      <div className="space-y-6" data-testid="construction-progress-page">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 font-heading">Construction Progress</h1>
          <p className="text-slate-600">Comprehensive tracking for Form-1 with N/A support</p>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
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
                <Label className="form-label">Building</Label>
                <Select value={selectedBuilding} onValueChange={setSelectedBuilding}>
                  <SelectTrigger><SelectValue placeholder="Select building" /></SelectTrigger>
                  <SelectContent>
                    {buildings.map(b => <SelectItem key={b.building_id} value={b.building_id}>{b.building_name}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="form-label">Quarter</Label>
                <Select value={quarter} onValueChange={setQuarter}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Q1">Q1 (Jan-Mar)</SelectItem>
                    <SelectItem value="Q2">Q2 (Apr-Jun)</SelectItem>
                    <SelectItem value="Q3">Q3 (Jul-Sep)</SelectItem>
                    <SelectItem value="Q4">Q4 (Oct-Dec)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="form-label">Year</Label>
                <Select value={year.toString()} onValueChange={(v) => setYear(parseInt(v))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {[2023, 2024, 2025, 2026, 2027].map(y => <SelectItem key={y} value={y.toString()}>{y}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2">
          <Button
            variant={activeTab === "tower" ? "default" : "outline"}
            onClick={() => setActiveTab("tower")}
            className={activeTab === "tower" ? "bg-blue-600" : ""}
          >
            Tower Construction ({formatNumber(overallCompletion, 1)}%)
          </Button>
          <Button
            variant={activeTab === "infrastructure" ? "default" : "outline"}
            onClick={() => setActiveTab("infrastructure")}
            className={activeTab === "infrastructure" ? "bg-blue-600" : ""}
          >
            Infrastructure Works ({formatNumber(infraOverallCompletion, 1)}%)
          </Button>
          <Button
            variant={activeTab === "site-expenditure" ? "default" : "outline"}
            onClick={() => setActiveTab("site-expenditure")}
            className={activeTab === "site-expenditure" ? "bg-emerald-600" : ""}
            data-testid="actual-site-expenditure-tab"
          >
            Actual Site Expenditure
          </Button>
        </div>

        {/* Overall Progress */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center justify-between">
              <span>Overall Completion</span>
              <span className="text-2xl text-blue-600">
                {formatNumber(activeTab === "tower" ? overallCompletion : infraOverallCompletion, 1)}%
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Progress 
              value={activeTab === "tower" ? overallCompletion : infraOverallCompletion} 
              className="h-4" 
            />
            <p className="text-xs text-slate-500 mt-2">
              * Weightages auto-recalibrate when activities are marked as N/A
            </p>
          </CardContent>
        </Card>

        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          </div>
        ) : template && activeTab === "tower" && selectedBuilding ? (
          /* Tower Construction Activities */
          <div className="space-y-4">
            {/* Global weightage warning */}
            {weightageWarnings.globalTotal && (
              <div className="flex items-start gap-2 bg-amber-50 border border-amber-300 rounded-lg px-4 py-3 text-sm text-amber-800">
                <span className="font-bold mt-0.5">⚠</span>
                <span>{weightageWarnings.globalTotal}</span>
              </div>
            )}
            {template.tower_construction.categories.map((category, catIdx) => {
              const catCompletion = categoryCompletions[category.id] || 0;
              const isExpanded = expandedCategories[category.id] !== false;
              const catData = towerActivities[category.id] || {};
              const useCostWeightage = catData._use_cost_weightage || false;
              const catWarning = weightageWarnings.categories[category.id];

              // Effective base weightage (custom or template)
              const effectiveCatBase = catData._custom_base_weightage !== undefined && catData._custom_base_weightage !== null && catData._custom_base_weightage !== ""
                ? parseFloat(catData._custom_base_weightage)
                : category.total_weightage;

              // Compute total cost for applicable activities in this category (for rollup display)
              const totalCategoryCost = category.activities.reduce((sum, act) => {
                const actData = catData[act.id] || {};
                return actData.is_applicable !== false ? sum + (parseFloat(actData.cost) || 0) : sum;
              }, 0);

              // Pre-compute effective weightages for cost-mode display
              const catBaseApplicable = category.activities.reduce((sum, act) => {
                const actData = catData[act.id] || {};
                const actWt = actData._custom_weightage !== undefined && actData._custom_weightage !== null && actData._custom_weightage !== ""
                  ? parseFloat(actData._custom_weightage) : act.weightage;
                return actData.is_applicable !== false ? sum + actWt : sum;
              }, 0);

              return (
                <Card key={category.id} className="overflow-hidden">
                  <div className="flex items-center justify-between p-4 hover:bg-slate-50 transition-colors">
                    <div
                      className="flex items-center gap-4 flex-1 cursor-pointer"
                      onClick={() => toggleCategory(category.id)}
                    >
                      <div className="flex items-center gap-2">
                        {isExpanded ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
                        <span className="text-sm font-medium text-slate-500">{String.fromCharCode(97 + catIdx)})</span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-slate-900">{category.name}</h3>
                        <div className="flex items-center gap-3 flex-wrap" onClick={(e) => e.stopPropagation()}>
                          <div className="flex items-center gap-1">
                            <span className="text-xs text-slate-500">Base Wt.%:</span>
                            <input
                              type="text"
                              inputMode="decimal"
                              value={catData._custom_base_weightage !== undefined && catData._custom_base_weightage !== null && catData._custom_base_weightage !== "" ? catData._custom_base_weightage : category.total_weightage}
                              onChange={(e) => setTowerActivities(prev => ({
                                ...prev,
                                [category.id]: { ...prev[category.id], _custom_base_weightage: e.target.value }
                              }))}
                              className={`w-20 h-7 text-xs text-center rounded-md border px-2 ${catWarning ? 'border-amber-400 bg-amber-50' : 'border-input bg-transparent'}`}
                              title="Edit Main Activity Base Weightage %"
                            />
                            <span className="text-xs text-slate-400">%</span>
                          </div>
                          {catWarning && (
                            <span className="text-xs text-amber-700 font-medium">⚠ {catWarning}</span>
                          )}
                          {useCostWeightage && totalCategoryCost > 0 && (
                            <p className="text-sm text-emerald-600 font-medium">
                              Total Cost: ₹{totalCategoryCost.toLocaleString('en-IN')}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      {/* Cost-Based Weightage Toggle */}
                      <div
                        className="flex items-center gap-2"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <label className="text-xs text-slate-500 whitespace-nowrap cursor-pointer select-none" htmlFor={`cost-toggle-${category.id}`}>
                          Cost Wt.
                        </label>
                        <button
                          id={`cost-toggle-${category.id}`}
                          role="switch"
                          aria-checked={useCostWeightage}
                          onClick={() => handleCostModeToggle(category.id)}
                          className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-1 ${
                            useCostWeightage ? 'bg-emerald-500' : 'bg-slate-300'
                          }`}
                          title={useCostWeightage ? 'Using cost-based weightage (click to switch to manual)' : 'Using manual weightage (click to switch to cost-based)'}
                        >
                          <span
                            className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform ${
                              useCostWeightage ? 'translate-x-4' : 'translate-x-0.5'
                            }`}
                          />
                        </button>
                      </div>
                      <div className="w-32">
                        <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${getCompletionColor(catCompletion)} transition-all`}
                            style={{ width: `${catCompletion}%` }}
                          />
                        </div>
                      </div>
                      <Badge variant={catCompletion >= 100 ? "success" : "secondary"} className="w-16 justify-center">
                        {formatNumber(catCompletion, 1)}%
                      </Badge>
                    </div>
                  </div>

                  {isExpanded && (
                    <CardContent className="pt-0 pb-4">
                      {useCostWeightage && (
                        <div className="mb-2 px-2 py-1.5 bg-emerald-50 border border-emerald-200 rounded text-xs text-emerald-700 flex items-center gap-1.5">
                          <span className="font-medium">Cost-Based Weightage ON</span>
                          <span className="text-emerald-600">— Wt.% is auto-calculated from cost. Enter costs below.</span>
                        </div>
                      )}
                      <Table>
                        <TableHeader>
                          <TableRow className="bg-slate-50">
                            <TableHead className="w-8">N/A</TableHead>
                            <TableHead>Activity</TableHead>
                            <TableHead className="text-right w-28">Cost (₹)</TableHead>
                            <TableHead className="text-center w-20">Wt. %</TableHead>
                            <TableHead className="text-center w-32">Completion %</TableHead>
                            <TableHead className="text-center w-24">Weighted</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {category.activities.map((activity, actIdx) => {
                            const actData = catData[activity.id] || { completion: 0, is_applicable: true, cost: 0 };
                            const isNA = actData.is_applicable === false;
                            const cost = parseFloat(actData.cost) || 0;
                            // Effective custom weightage for this activity
                            const customWt = actData._custom_weightage !== undefined && actData._custom_weightage !== null && actData._custom_weightage !== ""
                              ? parseFloat(actData._custom_weightage) : activity.weightage;

                            // Compute effective weightage for display
                            let displayWt = customWt;
                            if (useCostWeightage && !isNA) {
                              displayWt = totalCategoryCost > 0
                                ? (cost / totalCategoryCost) * catBaseApplicable
                                : customWt;
                            }

                            return (
                              <TableRow key={activity.id} className={isNA ? "bg-slate-100 opacity-60" : ""}>
                                <TableCell>
                                  <input
                                    type="checkbox"
                                    checked={isNA}
                                    onChange={(e) => handleActivityChange(category.id, activity.id, 'is_applicable', !e.target.checked)}
                                    className="h-4 w-4 rounded border-slate-300"
                                    title="Mark as Not Applicable"
                                  />
                                </TableCell>
                                <TableCell className={`text-sm ${isNA ? "line-through text-slate-400" : ""}`}>
                                  <span className="text-slate-500 mr-2">{actIdx + 1}.</span>
                                  {activity.name}
                                </TableCell>
                                <TableCell className="text-right">
                                  <div className="flex items-center justify-end gap-1">
                                    <span className="text-xs text-slate-400">₹</span>
                                    <Input
                                      type="number"
                                      min="0"
                                      step="1000"
                                      value={actData.cost || ""}
                                      placeholder="0"
                                      onChange={(e) => handleActivityChange(category.id, activity.id, 'cost', parseFloat(e.target.value) || 0)}
                                      disabled={isNA}
                                      className="w-24 text-right text-sm h-8"
                                    />
                                  </div>
                                </TableCell>
                                <TableCell className="text-center text-sm">
                                  {useCostWeightage && !isNA ? (
                                    <span className={`font-medium ${totalCategoryCost > 0 ? 'text-emerald-700' : 'text-slate-400'}`}>
                                      {formatNumber(displayWt, 2)}%
                                    </span>
                                  ) : !isNA ? (
                                    <input
                                      type="text"
                                      inputMode="decimal"
                                      value={actData._custom_weightage !== undefined && actData._custom_weightage !== null && actData._custom_weightage !== "" ? actData._custom_weightage : activity.weightage}
                                      onChange={(e) => handleActivityChange(category.id, activity.id, '_custom_weightage', e.target.value)}
                                      className="w-20 mx-auto block text-center text-sm rounded-md border border-input bg-transparent px-1 h-8"
                                      title="Edit sub-activity weightage %"
                                    />
                                  ) : (
                                    <span className="text-slate-400">—</span>
                                  )}
                                </TableCell>
                                <TableCell>
                                  <Input
                                    type="number"
                                    min="0"
                                    max="100"
                                    step="1"
                                    value={actData.completion || 0}
                                    onChange={(e) => handleActivityChange(category.id, activity.id, 'completion', e.target.value)}
                                    disabled={isNA}
                                    className="w-20 mx-auto text-center text-sm h-8"
                                  />
                                </TableCell>
                                <TableCell className="text-center font-medium text-sm">
                                  {isNA ? "-" : formatNumber(displayWt * (actData.completion || 0) / 100, 2) + "%"}
                                </TableCell>
                              </TableRow>
                            );
                          })}
                          {/* Category cost total row */}
                          {useCostWeightage && (
                            <TableRow className="bg-emerald-50 border-t-2 border-emerald-200">
                              <TableCell colSpan={2} className="text-sm font-semibold text-emerald-800">
                                Total (applicable activities)
                              </TableCell>
                              <TableCell className="text-right text-sm font-bold text-emerald-800">
                                ₹{totalCategoryCost.toLocaleString('en-IN')}
                              </TableCell>
                              <TableCell className="text-center text-sm font-semibold text-emerald-700">
                                {totalCategoryCost > 0 ? "100%" : "—"}
                              </TableCell>
                              <TableCell />
                              <TableCell />
                            </TableRow>
                          )}
                        </TableBody>
                      </Table>
                    </CardContent>
                  )}
                </Card>
              );
            })}
          </div>
        ) : template && activeTab === "infrastructure" ? (
          /* Infrastructure Works */
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Project Infrastructure Works</CardTitle>
              <p className="text-sm text-slate-500">Total weightage: 100% (recalibrates when items marked N/A)</p>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow className="bg-slate-50">
                    <TableHead className="w-8">N/A</TableHead>
                    <TableHead>Infrastructure Item</TableHead>
                    <TableHead className="text-center w-20">Wt. %</TableHead>
                    <TableHead className="text-center w-32">Completion %</TableHead>
                    <TableHead className="text-center w-24">Weighted</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {template.infrastructure_works.activities.map((activity, idx) => {
                    const actData = infraActivities[activity.id] || { completion: 0, is_applicable: true };
                    const isNA = !actData.is_applicable;
                    
                    return (
                      <TableRow key={activity.id} className={isNA ? "bg-slate-100 opacity-60" : ""}>
                        <TableCell>
                          <input
                            type="checkbox"
                            checked={isNA}
                            onChange={(e) => handleInfraChange(activity.id, 'is_applicable', !e.target.checked)}
                            className="h-4 w-4 rounded border-slate-300"
                            title="Mark as Not Applicable"
                          />
                        </TableCell>
                        <TableCell className={`font-medium ${isNA ? "line-through text-slate-400" : ""}`}>
                          <span className="text-slate-500 mr-2">{idx + 1}.</span>
                          {activity.name}
                        </TableCell>
                        <TableCell className="text-center">{activity.weightage}%</TableCell>
                        <TableCell>
                          <Input
                            type="number"
                            min="0"
                            max="100"
                            step="1"
                            value={actData.completion || 0}
                            onChange={(e) => handleInfraChange(activity.id, 'completion', e.target.value)}
                            disabled={isNA}
                            className="w-20 mx-auto text-center h-8"
                          />
                        </TableCell>
                        <TableCell className="text-center font-medium">
                          {isNA ? "-" : formatNumber(activity.weightage * (actData.completion || 0) / 100, 2) + "%"}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        ) : activeTab === "site-expenditure" && selectedProject ? (
          /* Actual Site Expenditure Tab */
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Actual On Site Expenditure for Development</CardTitle>
              <CardDescription>Enter actual costs incurred for {quarter} {year}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                <div>
                  <Label className="form-label">a. Development Cost (Site office, Toilets etc.)</Label>
                  <CurrencyInput
                    value={actualSiteExpenditure.site_development_cost}
                    onChange={(val) => handleActualSiteExpenditureChange("site_development_cost", val)}
                    data-testid="actual-site-development-cost"
                  />
                </div>
                <div>
                  <Label className="form-label">b. Salaries</Label>
                  <CurrencyInput
                    value={actualSiteExpenditure.salaries}
                    onChange={(val) => handleActualSiteExpenditureChange("salaries", val)}
                    data-testid="actual-salaries"
                  />
                </div>
                <div>
                  <Label className="form-label">c. Consultants Fee</Label>
                  <CurrencyInput
                    value={actualSiteExpenditure.consultants_fee}
                    onChange={(val) => handleActualSiteExpenditureChange("consultants_fee", val)}
                    data-testid="actual-consultants-fee"
                  />
                </div>
                <div>
                  <Label className="form-label">d. Site Over-heads</Label>
                  <CurrencyInput
                    value={actualSiteExpenditure.site_overheads}
                    onChange={(val) => handleActualSiteExpenditureChange("site_overheads", val)}
                    data-testid="actual-site-overheads"
                  />
                </div>
                <div>
                  <Label className="form-label">e. Cost of Services (Water, Electricity etc.)</Label>
                  <CurrencyInput
                    value={actualSiteExpenditure.services_cost}
                    onChange={(val) => handleActualSiteExpenditureChange("services_cost", val)}
                    data-testid="actual-services-cost"
                  />
                </div>
                <div>
                  <Label className="form-label">f. Cost of Machineries and Equipment</Label>
                  <CurrencyInput
                    value={actualSiteExpenditure.machinery_cost}
                    onChange={(val) => handleActualSiteExpenditureChange("machinery_cost", val)}
                    data-testid="actual-machinery-cost"
                  />
                </div>
              </div>
              
              <Separator />
              
              <div className="flex items-center justify-between bg-emerald-50 p-4 rounded-lg">
                <div>
                  <p className="text-sm text-emerald-600">Total On Site Expenditure (Actual) for {quarter} {year}</p>
                  <p className="text-2xl font-bold text-emerald-800">{formatCurrency(totalActualSiteExpenditure)}</p>
                </div>
                <Button 
                  onClick={saveActualSiteExpenditure} 
                  className="bg-emerald-600 hover:bg-emerald-700" 
                  disabled={saving}
                  data-testid="save-actual-site-expenditure-btn"
                >
                  {saving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                  Save Site Expenditure
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card className="text-center py-12">
            <Building className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-600">Select a project and building to track progress</p>
          </Card>
        )}

        {/* Save Button - Only for Tower and Infrastructure tabs */}
        {selectedBuilding && template && (activeTab === "tower" || activeTab === "infrastructure") && (
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => initializeActivities(template)}>
              Reset to Defaults
            </Button>
            <Button
              variant="outline"
              onClick={openWeightageModal}
              disabled={!selectedBuilding || !template}
              className="border-blue-300 text-blue-700 hover:bg-blue-50"
            >
              <Settings className="h-4 w-4 mr-2" />
              Edit Weightages
            </Button>
            <Button
              variant="outline"
              onClick={handleDownloadTemplate}
              disabled={!selectedBuilding || !selectedProject || downloadingTemplate}
              className="border-emerald-300 text-emerald-700 hover:bg-emerald-50"
              title="Download Excel template pre-filled with current progress data"
            >
              {downloadingTemplate
                ? <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                : <Download className="h-4 w-4 mr-2" />}
              Download Template
            </Button>
            <Button
              variant="outline"
              onClick={() => setImportModalOpen(true)}
              disabled={!selectedBuilding || !selectedProject}
              className="border-orange-300 text-orange-700 hover:bg-orange-50"
              title="Import progress data from an Excel file"
            >
              <Upload className="h-4 w-4 mr-2" />
              Import Excel
            </Button>

            {/* ── Bulk Dropdown ── */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="outline"
                  disabled={!selectedProject}
                  className="border-purple-300 text-purple-700 hover:bg-purple-50"
                  title="Bulk operations for all buildings"
                >
                  <FileSpreadsheet className="h-4 w-4 mr-2" />
                  Bulk Excel
                  <ChevronDown className="h-3 w-3 ml-1" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-64">
                <DropdownMenuItem
                  onClick={handleBulkDownloadTemplate}
                  disabled={bulkDownloading || !selectedProject}
                  className="cursor-pointer"
                >
                  {bulkDownloading
                    ? <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    : <Download className="h-4 w-4 mr-2 text-emerald-600" />}
                  <div>
                    <p className="font-medium">Download Bulk Template</p>
                    <p className="text-xs text-slate-500">All {buildings.length} building(s) in one file</p>
                  </div>
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => { setBulkImportResults(null); setBulkImportModalOpen(true); }}
                  disabled={!selectedProject}
                  className="cursor-pointer"
                >
                  <Upload className="h-4 w-4 mr-2 text-orange-600" />
                  <div>
                    <p className="font-medium">Bulk Import Excel</p>
                    <p className="text-xs text-slate-500">Update all buildings at once</p>
                  </div>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <Button onClick={handleSave} className="bg-blue-600 hover:bg-blue-700" disabled={saving}>
              {saving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Save Progress
            </Button>
          </div>
        )}

        {/* ── Bulk Import Excel Modal ──────────────────────────────────── */}
        <Dialog open={bulkImportModalOpen} onOpenChange={(open) => {
          setBulkImportModalOpen(open);
          if (!open) { setBulkImportFile(null); setBulkImportResults(null); }
        }}>
          <DialogContent className="max-w-xl">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <FileSpreadsheet className="h-5 w-5 text-purple-600" />
                Bulk Import Construction Progress
              </DialogTitle>
              <DialogDescription>
                Upload your bulk Excel template to update all buildings for{" "}
                <strong>{quarter} {year}</strong>.
                Data from identical buildings can be auto-copied using the
                <em> Copy From Building</em> column in the file.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-2">
              {/* Info guide */}
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 text-sm text-purple-800 space-y-1">
                <p className="font-semibold">How to use Bulk Import:</p>
                <p>1. Click <strong>Bulk Excel → Download Bulk Template</strong> to get the file.</p>
                <p>2. Each building has its own sheet. Fill <strong>Completion %</strong> and <strong>Applicable</strong>.</p>
                <p>3. For identical towers/villas, fill one sheet and write its name in the <em>Copy From Building</em> column in the <strong>Meta</strong> sheet for the others.</p>
                <p>4. Upload the file here.</p>
              </div>

              {/* File input */}
              <div className="space-y-2">
                <Label className="font-medium">Select Bulk Excel File (.xlsx)</Label>
                <div
                  className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center cursor-pointer hover:border-purple-400 hover:bg-purple-50 transition-colors"
                  onClick={() => document.getElementById("bulk-excel-import-input").click()}
                >
                  {bulkImportFile ? (
                    <div className="flex items-center justify-center gap-2 text-emerald-700">
                      <FileSpreadsheet className="h-6 w-6" />
                      <div>
                        <p className="font-semibold">{bulkImportFile.name}</p>
                        <p className="text-xs text-slate-500">{(bulkImportFile.size / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-slate-500">
                      <Upload className="h-8 w-8 mx-auto mb-2 text-slate-400" />
                      <p className="font-medium">Click to browse your bulk Excel file</p>
                      <p className="text-xs mt-1">Supports .xlsx files only</p>
                    </div>
                  )}
                </div>
                <input
                  id="bulk-excel-import-input"
                  type="file"
                  accept=".xlsx,.xlsm"
                  className="hidden"
                  onChange={(e) => { setBulkImportFile(e.target.files?.[0] || null); setBulkImportResults(null); }}
                />
                {bulkImportFile && !bulkImportResults && (
                  <Button variant="ghost" size="sm" className="text-slate-500 hover:text-red-600 w-full"
                    onClick={() => setBulkImportFile(null)}>
                    <X className="h-4 w-4 mr-1" /> Remove file
                  </Button>
                )}
              </div>

              {/* Warning */}
              {!bulkImportResults && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-800 flex gap-2">
                  <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                  <p>Importing will <strong>overwrite</strong> the current progress data for <strong>all buildings</strong> found in the file for {quarter} {year}.</p>
                </div>
              )}

              {/* Results after import */}
              {bulkImportResults && (
                <div className="space-y-2">
                  <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-sm text-emerald-800 font-semibold">
                    ✓ {bulkImportResults.message}
                    {bulkImportResults.infra_overall_completion > 0 && (
                      <span className="ml-2 text-xs font-normal">
                        · Infrastructure: {bulkImportResults.infra_overall_completion.toFixed(1)}%
                      </span>
                    )}
                  </div>
                  <div className="border rounded-lg overflow-hidden text-sm">
                    <div className="bg-slate-50 grid grid-cols-3 px-3 py-1.5 font-semibold text-slate-600 text-xs border-b">
                      <span>Building</span>
                      <span className="text-center">Status</span>
                      <span className="text-right">Completion</span>
                    </div>
                    {bulkImportResults.buildings?.map((b) => (
                      <div key={b.building_id} className="grid grid-cols-3 px-3 py-1.5 border-b last:border-0">
                        <span className="text-slate-800 truncate">{b.building_name}</span>
                        <span className={`text-center text-xs font-medium ${b.status === "imported" ? "text-emerald-600" : "text-slate-400"}`}>
                          {b.status === "imported" ? "✓ Imported" : "— Skipped"}
                        </span>
                        <span className="text-right font-medium text-blue-700">
                          {b.status === "imported" ? `${b.overall_completion}%` : "—"}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <DialogFooter className="gap-2">
              <Button variant="outline" onClick={() => {
                setBulkImportModalOpen(false); setBulkImportFile(null); setBulkImportResults(null);
              }}>
                {bulkImportResults ? "Close" : "Cancel"}
              </Button>
              {!bulkImportResults && (
                <Button
                  onClick={handleBulkImportExcel}
                  disabled={!bulkImportFile || bulkImporting}
                  className="bg-purple-600 hover:bg-purple-700 text-white"
                >
                  {bulkImporting ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Upload className="h-4 w-4 mr-2" />}
                  {bulkImporting ? "Importing…" : `Import All ${buildings.length} Building(s)`}
                </Button>
              )}
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* ── Import Excel Modal ─────────────────────────────────────── */}
        <Dialog open={importModalOpen} onOpenChange={(open) => { setImportModalOpen(open); if (!open) setImportFile(null); }}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <FileSpreadsheet className="h-5 w-5 text-orange-600" />
                Import Construction Progress from Excel
              </DialogTitle>
              <DialogDescription>
                Upload your filled-in Excel template to update the construction progress data for{" "}
                <strong>{buildings.find(b => b.building_id === selectedBuilding)?.building_name || "selected building"}</strong>{" — "}
                {quarter} {year}.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-2">
              {/* Step guide */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800 space-y-1">
                <p className="font-semibold">How to use:</p>
                <p>1. Click <strong>Download Template</strong> to get the pre-filled Excel file.</p>
                <p>2. Update the <strong>Completion %</strong> and <strong>Applicable</strong> columns.</p>
                <p>3. Save the file and upload it here.</p>
              </div>

              {/* File input */}
              <div className="space-y-2">
                <Label className="font-medium">Select Excel File (.xlsx)</Label>
                <div
                  className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center cursor-pointer hover:border-orange-400 hover:bg-orange-50 transition-colors"
                  onClick={() => document.getElementById("excel-import-input").click()}
                >
                  {importFile ? (
                    <div className="flex items-center justify-center gap-2 text-emerald-700">
                      <FileSpreadsheet className="h-6 w-6" />
                      <div>
                        <p className="font-semibold">{importFile.name}</p>
                        <p className="text-xs text-slate-500">{(importFile.size / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-slate-500">
                      <Upload className="h-8 w-8 mx-auto mb-2 text-slate-400" />
                      <p className="font-medium">Click to browse or drop your file here</p>
                      <p className="text-xs mt-1">Supports .xlsx files only</p>
                    </div>
                  )}
                </div>
                <input
                  id="excel-import-input"
                  type="file"
                  accept=".xlsx,.xlsm"
                  className="hidden"
                  onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                />
                {importFile && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-slate-500 hover:text-red-600 w-full"
                    onClick={() => setImportFile(null)}
                  >
                    <X className="h-4 w-4 mr-1" /> Remove file
                  </Button>
                )}
              </div>

              {/* Warning */}
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-800 flex gap-2">
                <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                <p>Importing will <strong>overwrite</strong> the current progress data for {quarter} {year}. This cannot be undone.</p>
              </div>
            </div>

            <DialogFooter className="gap-2">
              <Button variant="outline" onClick={() => { setImportModalOpen(false); setImportFile(null); }}>
                Cancel
              </Button>
              <Button
                onClick={handleImportExcel}
                disabled={!importFile || importing}
                className="bg-orange-600 hover:bg-orange-700 text-white"
              >
                {importing ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Upload className="h-4 w-4 mr-2" />}
                {importing ? "Importing…" : "Import & Update"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Edit Weightages Modal */}
        <Dialog open={weightageModalOpen} onOpenChange={setWeightageModalOpen}>
          <DialogContent className="max-w-3xl max-h-[85vh] flex flex-col">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5 text-blue-600" />
                Edit Weightages — {buildings.find(b => b.building_id === selectedBuilding)?.building_name || "Building"}
              </DialogTitle>
              <DialogDescription>
                Customise the Base Weightage % for each main activity and the Wt.% for each sub-activity.
                These values are saved at the building level and applied automatically every quarter.
                All category base weightages must sum to 100%.
              </DialogDescription>
            </DialogHeader>

            <ScrollArea className="flex-1 pr-4 overflow-y-auto">
              <div className="space-y-4 py-2">
                {/* Global sum indicator */}
                {(() => {
                  const total = template?.tower_construction?.categories?.reduce((sum, cat) => {
                    const val = parseFloat(draftWeightages.category_base_weightages?.[cat.id]) || 0;
                    return sum + val;
                  }, 0) || 0;
                  const isOk = Math.abs(total - 100) <= 0.1;
                  return (
                    <div className={`flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium ${isOk ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-amber-50 text-amber-700 border border-amber-200'}`}>
                      <span>Total of all Base Weightages</span>
                      <span>{total.toFixed(2)}% {isOk ? '✓' : `— must equal 100%`}</span>
                    </div>
                  );
                })()}

                {template?.tower_construction?.categories?.map((cat) => {
                  const catBase = parseFloat(draftWeightages.category_base_weightages?.[cat.id]) || 0;
                  const actSum = cat.activities.reduce((s, act) => {
                    return s + (parseFloat(draftWeightages.activity_weightages?.[cat.id]?.[act.id]) || 0);
                  }, 0);
                  const actSumOk = Math.abs(actSum - catBase) <= 0.05;

                  return (
                    <div key={cat.id} className="border rounded-lg overflow-hidden">
                      {/* Category header */}
                      <div className={`flex items-center justify-between px-4 py-2 ${actSumOk ? 'bg-slate-50' : 'bg-amber-50'}`}>
                        <span className="font-semibold text-slate-800 text-sm">{cat.name}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-slate-500">Base Weightage %:</span>
                          <input
                            type="number"
                            step="0.01"
                            min="0"
                            max="100"
                            value={draftWeightages.category_base_weightages?.[cat.id] ?? cat.total_weightage}
                            onChange={(e) => {
                              const val = e.target.value;
                              setDraftWeightages(prev => ({
                                ...prev,
                                category_base_weightages: { ...prev.category_base_weightages, [cat.id]: val }
                              }));
                            }}
                            className="w-20 h-7 text-center text-sm rounded border border-blue-300 bg-white px-1 font-semibold text-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-400"
                          />
                          <span className="text-xs text-slate-500">%</span>
                          {!actSumOk && (
                            <span className="text-xs text-amber-600 font-medium">
                              ⚠ sub-acts sum: {actSum.toFixed(2)}%
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Activity rows */}
                      <table className="w-full text-sm">
                        <thead className="bg-slate-100 text-xs text-slate-500">
                          <tr>
                            <th className="text-left px-4 py-1.5">Activity</th>
                            <th className="text-center px-4 py-1.5 w-32">Wt. %</th>
                          </tr>
                        </thead>
                        <tbody>
                          {cat.activities.map((act, idx) => (
                            <tr key={act.id} className={idx % 2 === 0 ? "bg-white" : "bg-slate-50/50"}>
                              <td className="px-4 py-1.5 text-slate-700">{idx + 1}. {act.name}</td>
                              <td className="px-4 py-1.5 text-center">
                                <input
                                  type="number"
                                  step="0.01"
                                  min="0"
                                  value={draftWeightages.activity_weightages?.[cat.id]?.[act.id] ?? act.weightage}
                                  onChange={(e) => {
                                    const val = e.target.value;
                                    setDraftWeightages(prev => ({
                                      ...prev,
                                      activity_weightages: {
                                        ...prev.activity_weightages,
                                        [cat.id]: {
                                          ...(prev.activity_weightages?.[cat.id] || {}),
                                          [act.id]: val
                                        }
                                      }
                                    }));
                                  }}
                                  className="w-20 text-center h-7 rounded border border-blue-300 bg-white px-1 text-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-400 mx-auto block"
                                />
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  );
                })}
              </div>
            </ScrollArea>

            <DialogFooter className="mt-4 gap-2">
              <Button variant="outline" onClick={() => setWeightageModalOpen(false)}>Cancel</Button>
              <Button
                onClick={saveBuildingWeightages}
                disabled={savingWeightages}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {savingWeightages ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Save Weightage Profile
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </Layout>
  );
};

// Project Costs Page

export default ConstructionProgressPage;
