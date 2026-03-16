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

const SalesPage = () => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState("");
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingSale, setEditingSale] = useState(null);
  const [buildings, setBuildings] = useState([]);
  const [form, setForm] = useState({
    unit_number: "",
    building_id: "",
    building_name: "",
    carpet_area: 0,
    sale_value: 0,
    amount_received: 0,
    buyer_name: "",
    agreement_date: "",
    apartment_classification: "NA"
  });

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchSales();
      fetchBuildings();
    }
  }, [selectedProject]);

  const fetchProjects = async () => {
    const res = await axios.get(`${API}/projects`);
    setProjects(res.data);
    if (res.data.length > 0) setSelectedProject(res.data[0].project_id);
    setLoading(false);
  };

  const fetchBuildings = async () => {
    const res = await axios.get(`${API}/buildings?project_id=${selectedProject}`);
    setBuildings(res.data);
  };

  const fetchSales = async () => {
    const res = await axios.get(`${API}/unit-sales?project_id=${selectedProject}`);
    setSales(res.data);
  };

  const handleSubmit = async () => {
    try {
      const building = buildings.find(b => b.building_id === form.building_id);
      const data = { ...form, building_name: building?.building_name || form.building_name };
      
      if (editingSale) {
        await axios.put(`${API}/unit-sales/${editingSale.sale_id}`, data);
        toast.success("Sale updated");
      } else {
        await axios.post(`${API}/unit-sales`, { ...data, project_id: selectedProject });
        toast.success("Sale added");
      }
      setDialogOpen(false);
      setEditingSale(null);
      setForm({ unit_number: "", building_id: "", building_name: "", carpet_area: 0, sale_value: 0, amount_received: 0, buyer_name: "", agreement_date: "", apartment_classification: "NA" });
      fetchSales();
    } catch (err) {
      toast.error("Failed to save sale");
    }
  };

  const deleteSale = async (id) => {
    if (!window.confirm("Delete this sale record?")) return;
    try {
      await axios.delete(`${API}/unit-sales/${id}`);
      toast.success("Sale deleted");
      fetchSales();
    } catch (err) {
      toast.error("Failed to delete sale");
    }
  };

  const totalSales = sales.reduce((sum, s) => sum + s.sale_value, 0);
  const totalReceived = sales.reduce((sum, s) => sum + s.amount_received, 0);
  const totalReceivable = sales.reduce((sum, s) => sum + s.balance_receivable, 0);

  // Separate sold and unsold inventory
  const soldUnits = sales.filter(s => s.status === "sold" || s.buyer_name);
  const unsoldUnits = sales.filter(s => s.status === "unsold" || (!s.buyer_name && !s.status));
  
  const soldValue = soldUnits.reduce((sum, s) => sum + s.sale_value, 0);
  const unsoldValue = unsoldUnits.reduce((sum, s) => sum + s.sale_value, 0);

  const [activeTab, setActiveTab] = useState("all");

  const filteredSales = activeTab === "all" ? sales : 
                        activeTab === "sold" ? soldUnits : unsoldUnits;

  return (
    <Layout>
      <div className="space-y-6" data-testid="sales-page">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 font-heading">Sales & Receivables</h1>
            <p className="text-slate-600">Manage unit sales for Annexure-A</p>
          </div>
          <div className="flex gap-3">
            <Select value={selectedProject} onValueChange={setSelectedProject}>
              <SelectTrigger className="w-48"><SelectValue placeholder="Select project" /></SelectTrigger>
              <SelectContent>
                {projects.map(p => <SelectItem key={p.project_id} value={p.project_id}>{p.project_name}</SelectItem>)}
              </SelectContent>
            </Select>
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-blue-600 hover:bg-blue-700" onClick={() => { setEditingSale(null); setForm({ unit_number: "", building_id: "", building_name: "", carpet_area: 0, sale_value: 0, amount_received: 0, buyer_name: "", agreement_date: "", apartment_classification: "NA" }); }}>
                  <Plus className="h-4 w-4 mr-2" />Add Sale
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-lg">
                <DialogHeader><DialogTitle>{editingSale ? "Edit" : "Add"} Sale</DialogTitle></DialogHeader>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="form-label">Unit Number</Label>
                    <Input value={form.unit_number} onChange={(e) => setForm(f => ({ ...f, unit_number: e.target.value }))} />
                  </div>
                  <div>
                    <Label className="form-label">Building</Label>
                    <Select value={form.building_id} onValueChange={(v) => setForm(f => ({ ...f, building_id: v }))}>
                      <SelectTrigger><SelectValue placeholder="Select" /></SelectTrigger>
                      <SelectContent>
                        {buildings.map(b => <SelectItem key={b.building_id} value={b.building_id}>{b.building_name}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="form-label">Carpet Area (sq.ft)</Label>
                    <Input type="number" value={form.carpet_area} onChange={(e) => setForm(f => ({ ...f, carpet_area: parseFloat(e.target.value) || 0 }))} />
                  </div>
                  <div>
                    <Label className="form-label">Buyer Name <span className="text-slate-400 text-xs">(leave blank for unsold)</span></Label>
                    <Input value={form.buyer_name} onChange={(e) => setForm(f => ({ ...f, buyer_name: e.target.value }))} placeholder="Leave blank if unsold" />
                  </div>
                  <div>
                    <Label className="form-label">Sale Value (₹)</Label>
                    <Input type="number" value={form.sale_value} onChange={(e) => setForm(f => ({ ...f, sale_value: parseFloat(e.target.value) || 0 }))} />
                  </div>
                  <div>
                    <Label className="form-label">Amount Received (₹)</Label>
                    <Input type="number" value={form.amount_received} onChange={(e) => setForm(f => ({ ...f, amount_received: parseFloat(e.target.value) || 0 }))} />
                  </div>
                  <div>
                    <Label className="form-label">Agreement Date</Label>
                    <Input type="date" value={form.agreement_date} onChange={(e) => setForm(f => ({ ...f, agreement_date: e.target.value }))} />
                  </div>
                  <div>
                    <Label className="form-label">Apartment Classification</Label>
                    <Select value={form.apartment_classification || "NA"} onValueChange={(v) => setForm(f => ({ ...f, apartment_classification: v }))}>
                      <SelectTrigger><SelectValue placeholder="Select type" /></SelectTrigger>
                      <SelectContent>
                        {["Studio", "1 BHK", "1.5 BHK", "2 BHK", "3 BHK", "4 BHK", "Pent-house", "NA"].map(c => (
                          <SelectItem key={c} value={c}>{c === "NA" ? "NA (Not Specified)" : c}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
                  <Button onClick={handleSubmit} className="bg-blue-600 hover:bg-blue-700">Save</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Summary */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <Card className="bg-slate-50">
            <CardContent className="p-4">
              <p className="text-sm text-slate-600">Total Units</p>
              <p className="text-xl font-bold text-slate-900">{sales.length}</p>
            </CardContent>
          </Card>
          <Card className="bg-emerald-50">
            <CardContent className="p-4">
              <p className="text-sm text-emerald-600">Sold Units</p>
              <p className="text-xl font-bold text-emerald-900">{soldUnits.length}</p>
              <p className="text-xs text-emerald-600">{formatCurrency(soldValue)}</p>
            </CardContent>
          </Card>
          <Card className="bg-amber-50">
            <CardContent className="p-4">
              <p className="text-sm text-amber-600">Unsold Inventory</p>
              <p className="text-xl font-bold text-amber-900">{unsoldUnits.length}</p>
              <p className="text-xs text-amber-600">{formatCurrency(unsoldValue)}</p>
            </CardContent>
          </Card>
          <Card className="bg-blue-50">
            <CardContent className="p-4">
              <p className="text-sm text-blue-600">Amount Received</p>
              <p className="text-xl font-bold text-blue-900 currency">{formatCurrency(totalReceived)}</p>
            </CardContent>
          </Card>
          <Card className="bg-red-50">
            <CardContent className="p-4">
              <p className="text-sm text-red-600">Receivables</p>
              <p className="text-xl font-bold text-red-900 currency">{formatCurrency(totalReceivable)}</p>
            </CardContent>
          </Card>
        </div>

        {/* Sales Table with Tabs */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Unit Sales</CardTitle>
              <div className="flex gap-2">
                <Button 
                  variant={activeTab === "all" ? "default" : "outline"} 
                  size="sm"
                  onClick={() => setActiveTab("all")}
                >
                  All ({sales.length})
                </Button>
                <Button 
                  variant={activeTab === "sold" ? "default" : "outline"} 
                  size="sm"
                  onClick={() => setActiveTab("sold")}
                  className={activeTab === "sold" ? "bg-emerald-600" : ""}
                >
                  Sold ({soldUnits.length})
                </Button>
                <Button 
                  variant={activeTab === "unsold" ? "default" : "outline"} 
                  size="sm"
                  onClick={() => setActiveTab("unsold")}
                  className={activeTab === "unsold" ? "bg-amber-600" : ""}
                >
                  Unsold ({unsoldUnits.length})
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[400px]">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Unit</TableHead>
                    <TableHead>Building</TableHead>
                    <TableHead>Apt. Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Buyer</TableHead>
                    <TableHead className="text-right">Area</TableHead>
                    <TableHead className="text-right">Sale Value</TableHead>
                    <TableHead className="text-right">Received</TableHead>
                    <TableHead className="text-right">Receivable</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredSales.map((sale) => (
                    <TableRow key={sale.sale_id} className={!sale.buyer_name ? "bg-amber-50" : ""}>
                      <TableCell className="font-medium">{sale.unit_number}</TableCell>
                      <TableCell>{sale.building_name}</TableCell>
                      <TableCell>
                        {sale.apartment_classification && sale.apartment_classification !== "NA"
                          ? <Badge variant="outline" className="text-xs">{sale.apartment_classification}</Badge>
                          : <span className="text-slate-400 text-xs">NA</span>}
                      </TableCell>
                      <TableCell>
                        {sale.buyer_name ? (
                          <Badge className="bg-emerald-100 text-emerald-700">Sold</Badge>
                        ) : (
                          <Badge className="bg-amber-100 text-amber-700">Unsold</Badge>
                        )}
                      </TableCell>
                      <TableCell>{sale.buyer_name || <span className="text-slate-400 italic">Available</span>}</TableCell>
                      <TableCell className="text-right">{formatNumber(sale.carpet_area, 0)}</TableCell>
                      <TableCell className="text-right currency">{formatCurrency(sale.sale_value)}</TableCell>
                      <TableCell className="text-right currency text-emerald-600">{formatCurrency(sale.amount_received)}</TableCell>
                      <TableCell className="text-right currency text-amber-600">{formatCurrency(sale.balance_receivable)}</TableCell>
                      <TableCell>
                        <Button variant="ghost" size="icon" onClick={() => { setEditingSale(sale); setForm(sale); setDialogOpen(true); }}>
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => deleteSale(sale.sale_id)}>
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

// Reports Page

export default SalesPage;
