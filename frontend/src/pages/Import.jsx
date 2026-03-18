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

const ImportPage = () => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState("");
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    const res = await axios.get(`${API}/projects`);
    setProjects(res.data);
    if (res.data.length > 0) setSelectedProject(res.data[0].project_id);
  };

  const handleUpload = async () => {
    if (!file || !selectedProject) {
      toast.error("Please select a project and file");
      return;
    }

    setUploading(true);
    setResult(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(`${API}/import/sales-excel?project_id=${selectedProject}`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setResult(res.data);
      if (res.data.created > 0) {
        toast.success(res.data.message || `Imported ${res.data.created} sales records`);
      }
      if (res.data.errors?.length > 0) {
        toast.warning(`${res.data.errors.length} errors occurred`);
      }
      setFile(null);
    } catch (err) {
      toast.error("Failed to import file");
    } finally {
      setUploading(false);
    }
  };

  const downloadTemplate = async () => {
    try {
      // Direct download using a hidden anchor tag with proper headers
      const response = await axios.get(`${API}/import/sales-template`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      
      // Create a temporary URL and trigger download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'CheckMate - Sales Data.xlsx';
      
      // Append to body, click, and remove
      document.body.appendChild(link);
      link.click();
      
      // Cleanup after a short delay
      setTimeout(() => {
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }, 100);
      
      toast.success("Template download started - check your Downloads folder");
    } catch (err) {
      toast.error("Failed to download template");
      console.error("Download error:", err);
    }
  };

  return (
    <Layout>
      <div className="space-y-6" data-testid="import-page">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 font-heading">Excel Import</h1>
          <p className="text-slate-600">Import sales data from Excel for Annexure-A</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Upload Sales Excel</CardTitle>
            <CardDescription>
              Import unit sales data. Download the template for the correct format.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label className="form-label">Project</Label>
                <Select value={selectedProject} onValueChange={setSelectedProject}>
                  <SelectTrigger><SelectValue placeholder="Select project" /></SelectTrigger>
                  <SelectContent>
                    {projects.map(p => <SelectItem key={p.project_id} value={p.project_id}>{p.project_name}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="form-label">Excel File</Label>
                <Input
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={(e) => setFile(e.target.files[0])}
                  data-testid="file-input"
                />
              </div>
            </div>

            <div className="flex gap-3 items-center">
                <Button variant="outline" onClick={downloadTemplate} data-testid="download-template-btn">
                  <Download className="h-4 w-4 mr-2" />
                  Download Template
                </Button>
                <Button onClick={handleUpload} disabled={uploading || !file} className="bg-blue-600 hover:bg-blue-700" data-testid="upload-btn">
                  {uploading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Upload className="h-4 w-4 mr-2" />}
                  Import Data
                </Button>
            </div>
          </CardContent>
        </Card>

        {/* Import Result */}
        {result && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                {result.errors?.length > 0 ? (
                  <AlertCircle className="h-5 w-5 text-amber-500" />
                ) : (
                  <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                )}
                Import Result
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
                <div className="p-4 bg-slate-50 rounded-lg">
                  <p className="text-sm text-slate-600">Previous Records</p>
                  <p className="text-2xl font-bold text-slate-700">{result.deleted || 0}</p>
                  <p className="text-xs text-slate-500">deleted</p>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-600">Total Rows</p>
                  <p className="text-2xl font-bold text-blue-700">{result.total_rows || 0}</p>
                  <p className="text-xs text-blue-500">in file</p>
                </div>
                <div className="p-4 bg-emerald-50 rounded-lg">
                  <p className="text-sm text-emerald-600">Sold Units</p>
                  <p className="text-2xl font-bold text-emerald-700">{result.sold_units || 0}</p>
                  <p className="text-xs text-emerald-500">with buyer name</p>
                </div>
                <div className="p-4 bg-amber-50 rounded-lg">
                  <p className="text-sm text-amber-600">Unsold Units</p>
                  <p className="text-2xl font-bold text-amber-700">{result.unsold_units || 0}</p>
                  <p className="text-xs text-amber-500">available inventory</p>
                </div>
                <div className="p-4 bg-rose-50 rounded-lg">
                  <p className="text-sm text-rose-600">Errors</p>
                  <p className="text-2xl font-bold text-rose-700">{result.errors?.length || 0}</p>
                  <p className="text-xs text-rose-500">skipped rows</p>
                </div>
              </div>
              
              {result.message && (
                <div className="p-3 bg-green-50 rounded-lg border border-green-200 mb-4">
                  <p className="text-sm text-green-700">{result.message}</p>
                </div>
              )}

              {result.errors?.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Errors:</h4>
                  <div className="bg-rose-50 rounded-lg p-4 max-h-40 overflow-auto">
                    {result.errors.map((err, idx) => (
                      <p key={idx} className="text-sm text-rose-700">
                        Row {err.row}: {err.error}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Instructions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Excel Format Requirements</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm text-slate-600">
              <p>The Excel file should have the following columns:</p>
              <ul className="list-disc list-inside space-y-1">
                <li><strong>Unit Number</strong> - Flat/Unit identifier (e.g., A-101)</li>
                <li><strong>Building Name</strong> - Tower/Wing name</li>
                <li><strong>Carpet Area</strong> - Area in sq.ft</li>
                <li><strong>Sale Value</strong> - Agreement value in ₹</li>
                <li><strong>Amount Received</strong> - Amount collected in ₹</li>
                <li><strong>Buyer Name</strong> - Customer name (optional, leave blank for unsold)</li>
                <li><strong>Agreement Date</strong> - Date of agreement (optional)</li>
                <li><strong>Apartment Classification</strong> - Unit type: Studio, 1 BHK, 1.5 BHK, 2 BHK, 3 BHK, 4 BHK, Pent-house, or NA (optional, defaults to NA)</li>
              </ul>
              <p className="text-slate-500 mt-4">
                Download the template for the exact format. The system auto-calculates Balance Receivable. Accepted column name aliases for Apartment Classification: "apartment type", "flat type", "bhk type", "unit type".
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default ImportPage;
