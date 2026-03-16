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

const DashboardPage = () => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchDashboard(selectedProject);
    }
  }, [selectedProject]);

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

  const fetchDashboard = async (projectId) => {
    try {
      const res = await axios.get(`${API}/dashboard/${projectId}`);
      setDashboard(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      </Layout>
    );
  }

  if (projects.length === 0) {
    return (
      <Layout>
        <div className="text-center py-12" data-testid="no-projects-message">
          <Building2 className="h-16 w-16 text-slate-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-900 mb-2">No Projects Yet</h2>
          <p className="text-slate-600 mb-6">Create your first project to get started</p>
          <Button asChild className="bg-blue-600 hover:bg-blue-700">
            <Link to="/projects/new" data-testid="create-first-project-btn">
              <Plus className="h-4 w-4 mr-2" />
              Create Project
            </Link>
          </Button>
        </div>
      </Layout>
    );
  }

  const stats = [
    { label: "Completion", value: `${formatNumber(dashboard?.project_completion_percentage || 0, 1)}%`, icon: TrendingUp, color: "blue" },
    { label: "Est. Cost", value: formatCurrency(dashboard?.total_estimated_cost), icon: IndianRupee, color: "slate" },
    { label: "Cost Incurred", value: formatCurrency(dashboard?.cost_incurred), icon: IndianRupee, color: "emerald" },
    { label: "Balance Cost", value: formatCurrency(dashboard?.balance_cost), icon: IndianRupee, color: "amber" },
    { label: "Sales Value", value: formatCurrency(dashboard?.total_sales_value), icon: Users, color: "purple" },
    { label: "Collected", value: formatCurrency(dashboard?.amount_collected), icon: CheckCircle2, color: "green" },
    { label: "Receivables", value: formatCurrency(dashboard?.receivables), icon: AlertCircle, color: "orange" },
    { label: "RERA Deposit", value: formatCurrency(dashboard?.rera_deposit_required), icon: Building, color: "red" },
  ];

  return (
    <Layout>
      <div className="space-y-6" data-testid="dashboard-page">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 font-heading">Dashboard</h1>
            <p className="text-slate-600">Project overview and compliance status</p>
          </div>
          <Select value={selectedProject} onValueChange={setSelectedProject}>
            <SelectTrigger className="w-full sm:w-64" data-testid="project-selector">
              <SelectValue placeholder="Select project" />
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

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((stat, idx) => (
            <Card key={idx} className="card-hover" data-testid={`stat-${stat.label.toLowerCase().replace(/\s+/g, '-')}`}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-slate-600 mb-1">{stat.label}</p>
                    <p className="text-xl font-bold text-slate-900 currency">{stat.value}</p>
                  </div>
                  <div className={({
                      blue: "bg-blue-50", slate: "bg-slate-50", emerald: "bg-emerald-50",
                      amber: "bg-amber-50", purple: "bg-purple-50", green: "bg-green-50",
                      orange: "bg-orange-50", red: "bg-red-50"
                    })[stat.color] + " p-2 rounded-lg"}>
                    <stat.icon className={({
                      blue: "text-blue-600", slate: "text-slate-600", emerald: "text-emerald-600",
                      amber: "text-amber-600", purple: "text-purple-600", green: "text-green-600",
                      orange: "text-orange-600", red: "text-red-600"
                    })[stat.color] + " h-5 w-5"} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Inventory Mismatch Alert */}
        {dashboard?.inventory_mismatch && (
          <div className="border border-amber-300 bg-amber-50 rounded-lg p-4 flex gap-3">
            <AlertCircle className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-amber-800">Inventory Count Mismatch Detected</p>
              <p className="text-sm text-amber-700 mt-1">
                The building configuration and sales data show different unit totals. Please reconcile before generating RERA reports.
              </p>
              <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
                <div className="bg-white border border-amber-200 rounded p-2">
                  <p className="text-amber-600 font-medium">Building Configuration</p>
                  <p className="text-xl font-bold text-slate-800">{dashboard.building_config_units}</p>
                  <p className="text-xs text-slate-500">units from floor × apt/floor</p>
                </div>
                <div className="bg-white border border-amber-200 rounded p-2">
                  <p className="text-amber-600 font-medium">Sales Data (Sold + Unsold)</p>
                  <p className="text-xl font-bold text-slate-800">{dashboard.sales_data_units}</p>
                  <p className="text-xs text-slate-500">
                    {dashboard.units_sold} sold + {dashboard.sales_data_units - dashboard.units_sold} unsold
                  </p>
                </div>
              </div>
              <p className="text-xs text-amber-700 mt-2 font-medium">
                Difference: {Math.abs(dashboard.inventory_mismatch_delta)} unit{Math.abs(dashboard.inventory_mismatch_delta) !== 1 ? "s" : ""}{" "}
                {dashboard.inventory_mismatch_delta > 0
                  ? "more in sales data than building config"
                  : "fewer in sales data than building config"}
              </p>
            </div>
          </div>
        )}

        {/* Progress Card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Project Completion Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-600">Overall Progress</span>
                <span className="font-semibold">{formatNumber(dashboard?.project_completion_percentage || 0, 1)}%</span>
              </div>
              <Progress value={dashboard?.project_completion_percentage || 0} className="h-3" />
            </div>
            <div className="grid grid-cols-2 gap-4 mt-6">
              <div className={`p-4 rounded-lg ${dashboard?.inventory_mismatch ? "bg-amber-50 border border-amber-200" : "bg-slate-50"}`}>
                <p className="text-sm text-slate-600">Total Units</p>
                <p className="text-2xl font-bold">{dashboard?.total_units || 0}</p>
                {dashboard?.inventory_mismatch && (
                  <p className="text-xs text-amber-600 mt-1">⚠ Mismatch: bldg {dashboard.building_config_units} vs sales {dashboard.sales_data_units}</p>
                )}
              </div>
              <div className="p-4 bg-emerald-50 rounded-lg">
                <p className="text-sm text-slate-600">Units Sold</p>
                <p className="text-2xl font-bold text-emerald-700">{dashboard?.units_sold || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              <Button asChild variant="outline" data-testid="quick-import-btn">
                <Link to="/import">
                  <Upload className="h-4 w-4 mr-2" />
                  Import Sales Excel
                </Link>
              </Button>
              <Button asChild variant="outline" data-testid="quick-reports-btn">
                <Link to="/reports">
                  <FileText className="h-4 w-4 mr-2" />
                  Generate Reports
                </Link>
              </Button>
              <Button asChild variant="outline" data-testid="quick-construction-btn">
                <Link to="/construction">
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Update Progress
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

// Projects List Page

export default DashboardPage;
