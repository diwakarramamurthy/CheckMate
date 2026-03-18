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

const ReportsPage = () => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState("");
  const [quarter, setQuarter] = useState("Q1");
  const [year, setYear] = useState(new Date().getFullYear());
  const [templates, setTemplates] = useState([]);
  const [generating, setGenerating] = useState("");
  const [downloading, setDownloading] = useState("");
  const [downloadingExcel, setDownloadingExcel] = useState("");
  const [downloadingDocx, setDownloadingDocx] = useState("");
  const [previewHtml, setPreviewHtml] = useState("");
  const [previewPdfUrl, setPreviewPdfUrl] = useState("");

  // Cleanup blob URL on unmount or when it changes (prevents memory leaks)
  useEffect(() => {
    return () => {
      if (previewPdfUrl) URL.revokeObjectURL(previewPdfUrl);
    };
  }, [previewPdfUrl]);
  const [previewType, setPreviewType] = useState("html"); // "html" | "pdf"
  const [previewTitle, setPreviewTitle] = useState("Report Preview");
  const [previewReportType, setPreviewReportType] = useState("");
  const [previewOpen, setPreviewOpen] = useState(false);

  // Reports with PDF support marked
  const reportTypes = [
    { type: "form-1", name: "Form-1: Architect Certificate", description: "Percentage of Completion", role: "architect", hasPdf: true },
    { type: "form-2", name: "Form-2: Architect Completion", description: "Building Completion Certificate", role: "architect", hasPdf: false },
    { type: "form-3", name: "Form-3: Engineer Certificate", description: "Cost Incurred Statement", role: "engineer", hasPdf: true },
    { type: "form-4", name: "Form-4: CA Certificate", description: "Project Cost Statement", role: "ca", hasPdf: true },
    { type: "form-5", name: "Form-5: CA Compliance", description: "Receivable Compliance", role: "ca", hasPdf: false },
    { type: "form-6", name: "Form-6: Auditor Certificate", description: "Statement of Accounts", role: "auditor", hasPdf: false },
    { type: "annexure-a", name: "Annexure-A", description: "Statement of Receivables", role: "developer", hasPdf: true },
  ];

  useEffect(() => {
    fetchProjects();
    fetchTemplates();
  }, []);

  const fetchProjects = async () => {
    const res = await axios.get(`${API}/projects`);
    setProjects(res.data);
    if (res.data.length > 0) setSelectedProject(res.data[0].project_id);
  };

  const fetchTemplates = async () => {
    const res = await axios.get(`${API}/report-templates?state=GOA`);
    setTemplates(res.data);
  };

  const generateReport = async (reportType) => {
    if (!selectedProject) {
      toast.error("Please select a project");
      return;
    }
    setGenerating(reportType);
    const report = reportTypes.find(r => r.type === reportType);
    const title = report?.name || "Report Preview";

    try {
      if (report?.hasPdf) {
        // For PDF-supported reports: fetch the actual PDF and show it in an iframe
        // so the preview is an exact match to what downloads
        toast.info("Loading preview…");
        const response = await axios.get(
          `${API}/generate-pdf/${selectedProject}/${reportType}?quarter=${quarter}&year=${year}`,
          { responseType: "blob" }
        );
        const blobUrl = URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }));
        setPreviewPdfUrl(blobUrl);
        setPreviewType("pdf");
      } else {
        // For non-PDF reports: use the HTML data endpoint
        const res = await axios.get(
          `${API}/generate-report/${selectedProject}/${reportType}?quarter=${quarter}&year=${year}`
        );
        const html = res.data.html || generateHtmlFromData(reportType, res.data.data);
        setPreviewHtml(html);
        setPreviewType("html");
      }
      setPreviewTitle(title);
      setPreviewReportType(reportType);
      setPreviewOpen(true);
    } catch (err) {
      toast.error("Failed to generate report preview");
    } finally {
      setGenerating("");
    }
  };

  const generateHtmlFromData = (reportType, data) => {
    const project = data.project || {};
    const sales = data.sales || [];
    const cost = data.project_cost || {};
    
    // Simple HTML generation for preview
    let html = `
      <div style="font-family: 'Times New Roman', serif; padding: 40px; max-width: 800px; margin: 0 auto;">
        <div style="text-align: center; margin-bottom: 30px;">
          <h1 style="font-size: 18px; margin-bottom: 10px;">GOA REAL ESTATE REGULATORY AUTHORITY</h1>
          <h2 style="font-size: 16px;">${reportTypes.find(r => r.type === reportType)?.name || reportType}</h2>
        </div>
        <div style="margin-bottom: 20px;">
          <p><strong>Project:</strong> ${project.project_name || '-'}</p>
          <p><strong>RERA No:</strong> ${project.rera_number || '-'}</p>
          <p><strong>Quarter:</strong> ${data.quarter} ${data.year}</p>
          <p><strong>Report Date:</strong> ${data.report_date}</p>
        </div>
    `;

    if (reportType === "annexure-a") {
      html += `
        <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
          <thead>
            <tr style="background: #f0f0f0;">
              <th style="border: 1px solid #000; padding: 8px;">Sr.</th>
              <th style="border: 1px solid #000; padding: 8px;">Unit</th>
              <th style="border: 1px solid #000; padding: 8px;">Building</th>
              <th style="border: 1px solid #000; padding: 8px;">Buyer</th>
              <th style="border: 1px solid #000; padding: 8px; text-align: right;">Sale Value</th>
              <th style="border: 1px solid #000; padding: 8px; text-align: right;">Received</th>
              <th style="border: 1px solid #000; padding: 8px; text-align: right;">Receivable</th>
            </tr>
          </thead>
          <tbody>
      `;
      sales.forEach((sale, idx) => {
        html += `
          <tr>
            <td style="border: 1px solid #000; padding: 6px; text-align: center;">${idx + 1}</td>
            <td style="border: 1px solid #000; padding: 6px;">${sale.unit_number}</td>
            <td style="border: 1px solid #000; padding: 6px;">${sale.building_name}</td>
            <td style="border: 1px solid #000; padding: 6px;">${sale.buyer_name || '-'}</td>
            <td style="border: 1px solid #000; padding: 6px; text-align: right;">${formatCurrency(sale.sale_value)}</td>
            <td style="border: 1px solid #000; padding: 6px; text-align: right;">${formatCurrency(sale.amount_received)}</td>
            <td style="border: 1px solid #000; padding: 6px; text-align: right;">${formatCurrency(sale.balance_receivable)}</td>
          </tr>
        `;
      });
      html += `
          <tr style="font-weight: bold; background: #f5f5f5;">
            <td colspan="4" style="border: 1px solid #000; padding: 8px; text-align: center;">TOTAL</td>
            <td style="border: 1px solid #000; padding: 8px; text-align: right;">${formatCurrency(data.total_sales_value)}</td>
            <td style="border: 1px solid #000; padding: 8px; text-align: right;">${formatCurrency(data.amount_collected)}</td>
            <td style="border: 1px solid #000; padding: 8px; text-align: right;">${formatCurrency(data.receivables)}</td>
          </tr>
          </tbody>
        </table>
      `;
    } else if (reportType === "form-4" || reportType === "form-5") {
      html += `
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
          <tr><td style="border: 1px solid #000; padding: 8px;">Total Estimated Cost</td><td style="border: 1px solid #000; padding: 8px; text-align: right;">${formatCurrency(cost.total_estimated_cost)}</td></tr>
          <tr><td style="border: 1px solid #000; padding: 8px;">Cost Incurred</td><td style="border: 1px solid #000; padding: 8px; text-align: right;">${formatCurrency(cost.total_cost_incurred)}</td></tr>
          <tr><td style="border: 1px solid #000; padding: 8px;">Balance Cost</td><td style="border: 1px solid #000; padding: 8px; text-align: right;">${formatCurrency(cost.balance_cost)}</td></tr>
        </table>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
          <tr><td style="border: 1px solid #000; padding: 8px;">Total Receivables</td><td style="border: 1px solid #000; padding: 8px; text-align: right;">${formatCurrency(data.receivables)}</td></tr>
          <tr><td style="border: 1px solid #000; padding: 8px;">Amount Collected</td><td style="border: 1px solid #000; padding: 8px; text-align: right;">${formatCurrency(data.amount_collected)}</td></tr>
        </table>
      `;
    }

    html += `
        <div style="margin-top: 50px;">
          <p>Date: ${data.report_date}</p>
          <p>Place: ${project.district || '-'}, ${project.state || 'GOA'}</p>
          <br/><br/>
          <p>_________________________</p>
          <p>${project.promoter_name || 'Authorized Signatory'}</p>
        </div>
      </div>
    `;

    return html;
  };

  const printReport = () => {
    const printWindow = window.open('', '_blank');
    printWindow.document.write(previewHtml);
    printWindow.document.close();
    printWindow.print();
  };

  const downloadPdf = async (reportType) => {
    if (!selectedProject) {
      toast.error("Please select a project");
      return;
    }
    setDownloading(reportType);
    try {
      toast.info("Generating PDF...");
      const response = await axios.get(
        `${API}/generate-pdf/${selectedProject}/${reportType}?quarter=${quarter}&year=${year}`,
        { responseType: 'blob' }
      );
      const contentDisposition = response.headers['content-disposition'];
      let filename = `${reportType}_report.pdf`;
      if (contentDisposition) {
        const m = contentDisposition.match(/filename=(.+)/);
        if (m) filename = m[1].replace(/"/g, '');
      }
      saveAs(response.data, filename);
      toast.success("PDF downloaded successfully!");
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Failed to generate PDF";
      toast.error(errorMsg);
    } finally {
      setDownloading("");
    }
  };

  const downloadExcel = async (reportType) => {
    if (!selectedProject) {
      toast.error("Please select a project");
      return;
    }
    setDownloadingExcel(reportType);
    try {
      toast.info("Generating Excel...");
      const response = await axios.get(
        `${API}/generate-excel/${selectedProject}/${reportType}?quarter=${quarter}&year=${year}`,
        { responseType: 'blob' }
      );
      const contentDisposition = response.headers['content-disposition'];
      let filename = `${reportType}_report.xlsx`;
      if (contentDisposition) {
        const m = contentDisposition.match(/filename=(.+)/);
        if (m) filename = m[1].replace(/"/g, '');
      }
      saveAs(response.data, filename);
      toast.success("Excel downloaded successfully!");
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Failed to generate Excel";
      toast.error(errorMsg);
    } finally {
      setDownloadingExcel("");
    }
  };

  const downloadDocx = async (reportType) => {
    if (!selectedProject) {
      toast.error("Please select a project");
      return;
    }
    setDownloadingDocx(reportType);
    try {
      toast.info("Generating Word document...");
      const response = await axios.get(
        `${API}/generate-docx/${selectedProject}/${reportType}?quarter=${quarter}&year=${year}`,
        { responseType: 'blob' }
      );
      const contentDisposition = response.headers['content-disposition'];
      let filename = `${reportType}_report.docx`;
      if (contentDisposition) {
        const m = contentDisposition.match(/filename=(.+)/);
        if (m) filename = m[1].replace(/"/g, '');
      }
      saveAs(response.data, filename);
      toast.success("Word document downloaded successfully!");
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Failed to generate Word document";
      toast.error(errorMsg);
    } finally {
      setDownloadingDocx("");
    }
  };

  return (
    <Layout>
      <div className="space-y-6" data-testid="reports-page">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 font-heading">RERA Reports</h1>
          <p className="text-slate-600">Generate statutory compliance reports</p>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="grid grid-cols-3 gap-4">
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
                    {[2023, 2024, 2025, 2026].map(y => <SelectItem key={y} value={y.toString()}>{y}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Reports Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reportTypes.map((report) => (
            <Card key={report.type} className="card-hover">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-base">{report.name}</CardTitle>
                    <CardDescription>{report.description}</CardDescription>
                  </div>
                  <Badge variant="secondary" className="capitalize shrink-0 ml-2">{report.role}</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-2">
                {/* Row 1: Preview + Download PDF */}
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => generateReport(report.type)}
                    disabled={generating === report.type}
                    className="flex-1"
                    data-testid={`preview-${report.type}`}
                  >
                    {generating === report.type ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <><Eye className="h-4 w-4 mr-1" />Preview</>
                    )}
                  </Button>
                  {report.hasPdf ? (
                    <Button
                      size="sm"
                      onClick={() => downloadPdf(report.type)}
                      disabled={downloading === report.type}
                      className="flex-1 bg-blue-600 hover:bg-blue-700"
                      data-testid={`download-${report.type}`}
                    >
                      {downloading === report.type ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <><Download className="h-4 w-4 mr-1" />PDF</>
                      )}
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      onClick={() => generateReport(report.type)}
                      disabled={generating === report.type}
                      className="flex-1 bg-blue-600 hover:bg-blue-700"
                      data-testid={`generate-${report.type}`}
                    >
                      {generating === report.type ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <><FileText className="h-4 w-4 mr-1" />Generate</>
                      )}
                    </Button>
                  )}
                </div>
                {/* Row 2: Excel + Word (only for PDF-ready reports) */}
                {report.hasPdf && (
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => downloadExcel(report.type)}
                      disabled={downloadingExcel === report.type}
                      className="flex-1 text-emerald-700 border-emerald-300 hover:bg-emerald-50"
                      data-testid={`download-excel-${report.type}`}
                    >
                      {downloadingExcel === report.type ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <><Download className="h-4 w-4 mr-1" />Excel</>
                      )}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => downloadDocx(report.type)}
                      disabled={downloadingDocx === report.type}
                      className="flex-1 text-violet-700 border-violet-300 hover:bg-violet-50"
                      data-testid={`download-docx-${report.type}`}
                    >
                      {downloadingDocx === report.type ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <><Download className="h-4 w-4 mr-1" />Word</>
                      )}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Preview Dialog */}
        <Dialog open={previewOpen} onOpenChange={(open) => { if (!open && previewPdfUrl) { URL.revokeObjectURL(previewPdfUrl); setPreviewPdfUrl(""); } setPreviewOpen(open); }}>
          <DialogContent className="max-w-5xl max-h-[95vh]">
            <DialogHeader>
              <DialogTitle>{previewTitle || 'Report Preview'}</DialogTitle>
            </DialogHeader>
            {previewType === 'pdf' ? (
              <iframe
                src={previewPdfUrl}
                className="w-full border rounded-lg"
                style={{ height: '70vh' }}
                title="PDF Preview"
              />
            ) : (
              <ScrollArea className="h-[65vh] border rounded-lg">
                <div dangerouslySetInnerHTML={{ __html: previewHtml }} />
              </ScrollArea>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={() => setPreviewOpen(false)}>Close</Button>
              {previewType === 'html' && (
                <Button onClick={printReport} className="bg-blue-600 hover:bg-blue-700">
                  <Download className="h-4 w-4 mr-2" />
                  Print / Download PDF
                </Button>
              )}
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </Layout>
  );
};

// Import Page

export default ReportsPage;
