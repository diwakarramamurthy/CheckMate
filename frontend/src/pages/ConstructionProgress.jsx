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
  const [expandedCategories, setExpandedCategories] = useState({});
  const [categoryCompletions, setCategoryCompletions] = useState({});
  const [overallCompletion, setOverallCompletion] = useState(0);
  const [infraOverallCompletion, setInfraOverallCompletion] = useState(0);
  const [weightageWarnings, setWeightageWarnings] = useState({ categories: {}, globalTotal: null });

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
            const effectiveWt = parseFloat(actData._custom_weightage) !== undefined && actData._custom_weightage !== null && actData._custom_weightage !== ""
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
          const actWt = parseFloat(actData._custom_weightage) !== undefined && actData._custom_weightage !== null && actData._custom_weightage !== ""
            ? parseFloat(actData._custom_weightage)
            : act.weightage;
          return sum + actWt;
        }, 0);
        const baseWt = parseFloat(catData._custom_base_weightage) !== undefined && catData._custom_base_weightage !== null && catData._custom_base_weightage !== ""
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
      const baseWt = parseFloat(catData._custom_base_weightage) !== undefined && catData._custom_base_weightage !== null && catData._custom_base_weightage !== ""
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
            <Button onClick={handleSave} className="bg-blue-600 hover:bg-blue-700" disabled={saving}>
              {saving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Save Progress
            </Button>
          </div>
        )}
      </div>
    </Layout>
  );
};

// Project Costs Page

export default ConstructionProgressPage;
