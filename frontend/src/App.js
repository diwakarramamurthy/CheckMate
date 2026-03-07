import { useState, useEffect, createContext, useContext, useCallback } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation, Link } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { 
  Building2, LayoutDashboard, FolderKanban, FileText, Upload, Settings, 
  LogOut, Menu, X, ChevronRight, Plus, Pencil, Trash2, Download,
  AlertCircle, CheckCircle2, TrendingUp, Users, IndianRupee, Building,
  FileSpreadsheet, ClipboardList, ChevronDown, Eye, Loader2, RefreshCw
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

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("rera_token"));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const res = await axios.get(`${API}/auth/me`);
      setUser(res.data);
    } catch (e) {
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const res = await axios.post(`${API}/auth/login`, { email, password });
    const { access_token, user } = res.data;
    localStorage.setItem("rera_token", access_token);
    axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
    setToken(access_token);
    setUser(user);
    return user;
  };

  const register = async (data) => {
    const res = await axios.post(`${API}/auth/register`, data);
    const { access_token, user } = res.data;
    localStorage.setItem("rera_token", access_token);
    axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
    setToken(access_token);
    setUser(user);
    return user;
  };

  const logout = () => {
    localStorage.removeItem("rera_token");
    delete axios.defaults.headers.common["Authorization"];
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Format currency helper
const formatCurrency = (amount) => {
  if (!amount && amount !== 0) return "₹ 0";
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
};

// Format number helper
const formatNumber = (num, decimals = 2) => {
  if (!num && num !== 0) return "0";
  return new Intl.NumberFormat('en-IN', {
    maximumFractionDigits: decimals
  }).format(num);
};

// Protected Route
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// Sidebar Component
const Sidebar = ({ isOpen, setIsOpen }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems = [
    { icon: LayoutDashboard, label: "Dashboard", path: "/dashboard" },
    { icon: FolderKanban, label: "Projects", path: "/projects" },
    { icon: Building, label: "Buildings & Infra", path: "/buildings" },
    { icon: TrendingUp, label: "Construction Progress", path: "/construction" },
    { icon: IndianRupee, label: "Project Costs", path: "/costs" },
    { icon: Users, label: "Sales & Receivables", path: "/sales" },
    { icon: FileText, label: "Reports", path: "/reports" },
    { icon: Upload, label: "Excel Import", path: "/import" },
  ];

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
      
      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-50 h-full w-64 sidebar text-white
        transform transition-transform duration-200 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:z-auto
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center gap-3 p-5 border-b border-white/10">
            <div className="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center">
              <Building2 className="h-6 w-6" />
            </div>
            <div>
              <h1 className="font-bold text-lg font-heading">RERA Manager</h1>
              <p className="text-xs text-white/60">Compliance Suite</p>
            </div>
            <button 
              onClick={() => setIsOpen(false)}
              className="lg:hidden ml-auto p-1 hover:bg-white/10 rounded"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {menuItems.map((item) => {
              const isActive = location.pathname === item.path || 
                (item.path !== "/dashboard" && location.pathname.startsWith(item.path));
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsOpen(false)}
                  className={`
                    flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200
                    ${isActive 
                      ? 'bg-white/15 text-white' 
                      : 'text-white/70 hover:bg-white/10 hover:text-white'}
                  `}
                  data-testid={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                >
                  <item.icon className="h-5 w-5" />
                  <span className="font-medium text-sm">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* User section */}
          <div className="p-4 border-t border-white/10">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-9 h-9 rounded-full bg-white/10 flex items-center justify-center text-sm font-semibold">
                {user?.name?.charAt(0).toUpperCase() || "U"}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm truncate">{user?.name}</p>
                <p className="text-xs text-white/60 capitalize">{user?.role}</p>
              </div>
            </div>
            <Button 
              variant="ghost" 
              className="w-full justify-start text-white/70 hover:text-white hover:bg-white/10"
              onClick={handleLogout}
              data-testid="logout-btn"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </aside>
    </>
  );
};

// Layout Component
const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50 flex">
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile header */}
        <header className="lg:hidden sticky top-0 z-30 bg-white border-b px-4 py-3 flex items-center gap-3">
          <button 
            onClick={() => setSidebarOpen(true)}
            className="p-2 hover:bg-slate-100 rounded-lg"
            data-testid="mobile-menu-btn"
          >
            <Menu className="h-5 w-5" />
          </button>
          <h1 className="font-bold text-lg">RERA Manager</h1>
        </header>
        <main className="flex-1 p-4 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
};

// Login Page
const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState("");
  const [role, setRole] = useState("developer");
  const { login, register, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) navigate("/dashboard");
  }, [user, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    // Small delay to ensure state updates properly
    await new Promise(resolve => setTimeout(resolve, 100));
    try {
      if (isRegister) {
        await register({ email, password, name, role });
        toast.success("Account created successfully!");
      } else {
        await login(email, password);
        toast.success("Welcome back!");
      }
      navigate("/dashboard");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Authentication failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left side - Image */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: "url('https://images.unsplash.com/photo-1725656796236-9ae43c627429?w=1200')" }}
        />
        <div className="absolute inset-0 bg-gradient-to-br from-blue-950/90 to-slate-900/90" />
        <div className="relative z-10 flex flex-col justify-center p-12 text-white">
          <Building2 className="h-12 w-12 mb-6" />
          <h1 className="text-4xl font-bold mb-4 font-heading">RERA Compliance Manager</h1>
          <p className="text-lg text-white/80 max-w-md">
            Automate your RERA compliance reporting. Generate all statutory certificates in minutes.
          </p>
          <div className="mt-8 space-y-3">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="h-5 w-5 text-emerald-400" />
              <span>Form 1-6 Report Generation</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle2 className="h-5 w-5 text-emerald-400" />
              <span>Excel Import for Sales Data</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle2 className="h-5 w-5 text-emerald-400" />
              <span>Multi-State Template Support</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-lg bg-blue-950 flex items-center justify-center">
              <Building2 className="h-6 w-6 text-white" />
            </div>
            <h1 className="font-bold text-xl">RERA Manager</h1>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 font-heading">
              {isRegister ? "Create Account" : "Welcome back"}
            </h2>
            <p className="text-slate-600 mt-1">
              {isRegister ? "Sign up to get started" : "Sign in to your account"}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegister && (
              <>
                <div>
                  <Label htmlFor="name" className="form-label">Full Name</Label>
                  <Input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter your name"
                    required
                    data-testid="register-name-input"
                  />
                </div>
                <div>
                  <Label htmlFor="role" className="form-label">Role</Label>
                  <Select value={role} onValueChange={setRole}>
                    <SelectTrigger data-testid="register-role-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="developer">Developer</SelectItem>
                      <SelectItem value="architect">Architect</SelectItem>
                      <SelectItem value="engineer">Engineer</SelectItem>
                      <SelectItem value="ca">Chartered Accountant</SelectItem>
                      <SelectItem value="auditor">Auditor</SelectItem>
                      <SelectItem value="admin">Admin</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </>
            )}
            <div>
              <Label htmlFor="email" className="form-label">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                required
                data-testid="login-email-input"
              />
            </div>
            <div>
              <Label htmlFor="password" className="form-label">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                data-testid="login-password-input"
              />
            </div>
            <Button 
              type="submit" 
              className="w-full bg-blue-600 hover:bg-blue-700"
              disabled={isLoading}
              data-testid="login-submit-btn"
            >
              {isLoading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              {isRegister ? "Create Account" : "Sign In"}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => setIsRegister(!isRegister)}
              className="text-sm text-blue-600 hover:text-blue-700"
              data-testid="toggle-auth-mode"
            >
              {isRegister ? "Already have an account? Sign in" : "Don't have an account? Sign up"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Dashboard Page
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
                  <div className={`p-2 rounded-lg bg-${stat.color}-50`}>
                    <stat.icon className={`h-5 w-5 text-${stat.color}-600`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

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
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-sm text-slate-600">Total Units</p>
                <p className="text-2xl font-bold">{dashboard?.total_units || 0}</p>
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
const ProjectsPage = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [projectToDelete, setProjectToDelete] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await axios.get(`${API}/projects`);
      setProjects(res.data);
    } catch (err) {
      toast.error("Failed to load projects");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (project) => {
    setProjectToDelete(project);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!projectToDelete) return;
    try {
      await axios.delete(`${API}/projects/${projectToDelete.project_id}`);
      toast.success("Project deleted");
      fetchProjects();
    } catch (err) {
      toast.error("Failed to delete project");
    } finally {
      setDeleteDialogOpen(false);
      setProjectToDelete(null);
    }
  };

  return (
    <Layout>
      <div className="space-y-6" data-testid="projects-page">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 font-heading">Projects</h1>
            <p className="text-slate-600">Manage your RERA registered projects</p>
          </div>
          <Button asChild className="bg-blue-600 hover:bg-blue-700" data-testid="new-project-btn">
            <Link to="/projects/new">
              <Plus className="h-4 w-4 mr-2" />
              New Project
            </Link>
          </Button>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          </div>
        ) : projects.length === 0 ? (
          <Card className="text-center py-12">
            <FolderKanban className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-600">No projects found. Create your first project.</p>
          </Card>
        ) : (
          <div className="grid gap-4">
            {projects.map((project) => (
              <Card key={project.project_id} className="card-hover" data-testid={`project-card-${project.project_id}`}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-slate-900">{project.project_name}</h3>
                        <Badge variant="secondary">{project.state}</Badge>
                      </div>
                      <p className="text-sm text-slate-600 mb-3">RERA: {project.rera_number}</p>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-slate-500">Promoter:</span>
                          <p className="font-medium">{project.promoter_name || "-"}</p>
                        </div>
                        <div>
                          <span className="text-slate-500">Location:</span>
                          <p className="font-medium">{project.district || "-"}, {project.state}</p>
                        </div>
                        <div>
                          <span className="text-slate-500">Architect:</span>
                          <p className="font-medium">{project.architect_name || "-"}</p>
                        </div>
                        <div>
                          <span className="text-slate-500">Engineer:</span>
                          <p className="font-medium">{project.engineer_name || "-"}</p>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <Button 
                        variant="ghost" 
                        size="icon"
                        onClick={() => navigate(`/projects/${project.project_id}/edit`)}
                        data-testid={`edit-project-${project.project_id}`}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="icon"
                        onClick={() => handleDeleteClick(project)}
                        data-testid={`delete-project-${project.project_id}`}
                      >
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Project</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{projectToDelete?.project_name}"? This will also delete all buildings, costs, and sales data associated with this project. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete} className="bg-red-600 hover:bg-red-700">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Layout>
  );
};

// Project Form Page (Create/Edit)
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

// Buildings Page - Enhanced with building types, floor configurations, and bulk creation
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
  
  const defaultForm = {
    building_name: "",
    building_type: "residential_tower",
    parking_basement: 0,
    parking_stilt_ground: 0,
    parking_upper_level: 0,
    commercial_floors: 0,
    residential_floors: 0,
    apartments_per_floor: 0,
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
  }, [buildings, infraCosts, infraTemplate]);

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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
            <Card className="bg-blue-50">
              <CardContent className="p-4">
                <div className="text-sm text-blue-600 font-medium">Combined Total</div>
                <div className="text-2xl font-bold text-blue-700">{formatCurrency(totalBuildingsCost + totalInfraCost)}</div>
                <div className="text-xs text-blue-500">Buildings + Infrastructure</div>
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
        ) : (
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
        )}
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

export { AuthProvider, Layout, LoginPage, DashboardPage, ProjectsPage, ProjectFormPage, BuildingsPage };

// Main App
function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/projects" element={<ProtectedRoute><ProjectsPage /></ProtectedRoute>} />
          <Route path="/projects/new" element={<ProtectedRoute><ProjectFormPage /></ProtectedRoute>} />
          <Route path="/projects/:id/edit" element={<ProtectedRoute><ProjectFormPage /></ProtectedRoute>} />
          <Route path="/buildings" element={<ProtectedRoute><BuildingsPage /></ProtectedRoute>} />
          <Route path="/construction" element={<ProtectedRoute><ConstructionProgressPage /></ProtectedRoute>} />
          <Route path="/costs" element={<ProtectedRoute><ProjectCostsPage /></ProtectedRoute>} />
          <Route path="/sales" element={<ProtectedRoute><SalesPage /></ProtectedRoute>} />
          <Route path="/reports" element={<ProtectedRoute><ReportsPage /></ProtectedRoute>} />
          <Route path="/import" element={<ProtectedRoute><ImportPage /></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
    </AuthProvider>
  );
}

// Construction Progress Page
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

  useEffect(() => {
    fetchProjects();
    fetchTemplate();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchBuildings();
    }
  }, [selectedProject]);

  useEffect(() => {
    if (selectedBuilding && template) {
      fetchProgress();
    }
  }, [selectedBuilding, quarter, year, template]);

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
      towerData[cat.id] = {};
      cat.activities.forEach(act => {
        towerData[cat.id][act.id] = { completion: 0, is_applicable: true };
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

    template.tower_construction.categories.forEach(cat => {
      let catApplicable = 0;
      let catWeighted = 0;
      
      cat.activities.forEach(act => {
        const actData = towerActivities[cat.id]?.[act.id] || { completion: 0, is_applicable: true };
        if (actData.is_applicable) {
          totalApplicable += act.weightage;
          catApplicable += act.weightage;
          weightedCompletion += act.weightage * (actData.completion || 0) / 100;
          catWeighted += act.weightage * (actData.completion || 0) / 100;
        }
      });
      
      catComps[cat.id] = catApplicable > 0 ? (catWeighted / catApplicable * 100) : 0;
    });

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
        <div className="flex gap-2">
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
            {template.tower_construction.categories.map((category, catIdx) => {
              const catCompletion = categoryCompletions[category.id] || 0;
              const isExpanded = expandedCategories[category.id] !== false;
              
              return (
                <Card key={category.id} className="overflow-hidden">
                  <div 
                    className="flex items-center justify-between p-4 cursor-pointer hover:bg-slate-50 transition-colors"
                    onClick={() => toggleCategory(category.id)}
                  >
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        {isExpanded ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
                        <span className="text-sm font-medium text-slate-500">{String.fromCharCode(97 + catIdx)})</span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-slate-900">{category.name}</h3>
                        <p className="text-sm text-slate-500">Base Weightage: {category.total_weightage}%</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
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
                      <Table>
                        <TableHeader>
                          <TableRow className="bg-slate-50">
                            <TableHead className="w-8">N/A</TableHead>
                            <TableHead>Activity</TableHead>
                            <TableHead className="text-center w-20">Wt. %</TableHead>
                            <TableHead className="text-center w-32">Completion %</TableHead>
                            <TableHead className="text-center w-24">Weighted</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {category.activities.map((activity, actIdx) => {
                            const actData = towerActivities[category.id]?.[activity.id] || { completion: 0, is_applicable: true };
                            const isNA = !actData.is_applicable;
                            
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
                                <TableCell className="text-center text-sm">{activity.weightage}%</TableCell>
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
                                  {isNA ? "-" : formatNumber(activity.weightage * (actData.completion || 0) / 100, 2) + "%"}
                                </TableCell>
                              </TableRow>
                            );
                          })}
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
        ) : (
          <Card className="text-center py-12">
            <Building className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-600">Select a project and building to track progress</p>
          </Card>
        )}

        {/* Save Button */}
        {selectedBuilding && template && (
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
    estimated_development_cost: 0
  });
  const [saving, setSaving] = useState(false);
  
  // Estimated Development Cost breakdown (fixed values)
  const [estimatedDevCost, setEstimatedDevCost] = useState({
    buildings_cost: 0,
    infrastructure_cost: 0,
    consultants_fee: 0,
    machinery_cost: 0,
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

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchCost();
      fetchEstimatedDevCost();
      fetchActualCostsFromProgress();
    }
  }, [selectedProject, quarter, year]);

  const fetchProjects = async () => {
    const res = await axios.get(`${API}/projects`);
    setProjects(res.data);
    if (res.data.length > 0) setSelectedProject(res.data[0].project_id);
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
      setEstimatedDevCost({
        buildings_cost: res.data.buildings_cost || 0,
        infrastructure_cost: res.data.infrastructure_cost || 0,
        consultants_fee: res.data.consultants_fee || 0,
        machinery_cost: res.data.machinery_cost || 0,
        total: res.data.total_estimated_development_cost || 0,
        is_locked: !res.data.is_draft
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
      setEstimatedDevCost(prev => ({
        ...prev,
        buildings_cost: res.data.buildings_cost,
        infrastructure_cost: res.data.infrastructure_cost,
        total: res.data.buildings_cost + res.data.infrastructure_cost + prev.consultants_fee + prev.machinery_cost
      }));
      toast.success("Buildings & Infrastructure costs refreshed");
    } catch (err) {
      toast.error("Failed to refresh costs");
    }
  };

  const saveEstimatedDevCost = async () => {
    setSaving(true);
    try {
      await axios.post(`${API}/estimated-development-cost?project_id=${selectedProject}`, {
        consultants_fee: estimatedDevCost.consultants_fee,
        machinery_cost: estimatedDevCost.machinery_cost
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
      updated.total = updated.buildings_cost + updated.infrastructure_cost + updated.consultants_fee + updated.machinery_cost;
      return updated;
    });
  };

  const totalLandCost = cost.land_acquisition_cost + cost.development_rights_premium + 
    cost.tdr_cost + cost.stamp_duty + cost.government_charges + cost.encumbrance_removal;
  
  // Use actual costs from progress for construction and infrastructure
  const totalDevCost = actualCosts.construction_cost + actualCosts.infrastructure_cost + 
    cost.equipment_cost + cost.taxes_statutory + cost.finance_cost;
  
  const totalEstimated = cost.estimated_land_cost + estimatedDevCost.total;
  const totalIncurred = totalLandCost + totalDevCost;
  const balanceCost = totalEstimated - totalIncurred;

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.post(`${API}/project-costs`, {
        project_id: selectedProject,
        quarter,
        year,
        ...cost,
        estimated_development_cost: estimatedDevCost.total
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

        {/* Cost Forms */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Estimated Development Cost Breakdown - NEW */}
          <Card className="md:col-span-2 border-2 border-blue-200">
            <CardHeader className="bg-blue-50">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg text-blue-800">Estimated Development Cost Breakdown</CardTitle>
                  <CardDescription>This total is fixed once saved and used in all quarterly reports</CardDescription>
                </div>
                {!estimatedDevCost.is_locked && (
                  <Button variant="outline" size="sm" onClick={refreshBuildingsInfraCost}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh from Buildings
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent className="p-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div>
                  <Label className="form-label">1. Buildings Cost</Label>
                  <Input
                    type="number"
                    value={estimatedDevCost.buildings_cost}
                    disabled
                    className="bg-slate-100 font-medium"
                  />
                  <p className="text-xs text-slate-500 mt-1">Auto-calculated from Buildings section</p>
                </div>
                <div>
                  <Label className="form-label">2. Infrastructure Cost</Label>
                  <Input
                    type="number"
                    value={estimatedDevCost.infrastructure_cost}
                    disabled
                    className="bg-slate-100 font-medium"
                  />
                  <p className="text-xs text-slate-500 mt-1">From Infrastructure Works section</p>
                </div>
                <div>
                  <Label className="form-label">3. Consultants Fee</Label>
                  <Input
                    type="number"
                    value={estimatedDevCost.consultants_fee}
                    onChange={(e) => handleEstimatedChange("consultants_fee", e.target.value)}
                    disabled={estimatedDevCost.is_locked}
                  />
                  <p className="text-xs text-slate-500 mt-1">Manual input</p>
                </div>
                <div>
                  <Label className="form-label">4. Cost of Machineries</Label>
                  <Input
                    type="number"
                    value={estimatedDevCost.machinery_cost}
                    onChange={(e) => handleEstimatedChange("machinery_cost", e.target.value)}
                    disabled={estimatedDevCost.is_locked}
                  />
                  <p className="text-xs text-slate-500 mt-1">Manual input</p>
                </div>
              </div>
              <Separator className="my-6" />
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500">Total Estimated Development Cost</p>
                  <p className="text-3xl font-bold text-blue-700 currency">{formatCurrency(estimatedDevCost.total)}</p>
                  {estimatedDevCost.is_locked && (
                    <Badge variant="secondary" className="mt-2">Locked - Used in all reports</Badge>
                  )}
                </div>
                {!estimatedDevCost.is_locked && (
                  <Button onClick={saveEstimatedDevCost} className="bg-blue-600 hover:bg-blue-700">
                    Save & Lock Estimate
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Estimated Land Cost */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Estimated Land Cost</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="form-label">Estimated Land Cost (₹)</Label>
                <Input
                  type="number"
                  value={cost.estimated_land_cost}
                  onChange={(e) => handleChange("estimated_land_cost", e.target.value)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Land Costs */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Land Costs (Actual)</CardTitle>
              <CardDescription>Total: {formatCurrency(totalLandCost)}</CardDescription>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-4">
              <div>
                <Label className="form-label text-xs">Land Acquisition</Label>
                <Input type="number" value={cost.land_acquisition_cost} onChange={(e) => handleChange("land_acquisition_cost", e.target.value)} />
              </div>
              <div>
                <Label className="form-label text-xs">Dev. Rights Premium</Label>
                <Input type="number" value={cost.development_rights_premium} onChange={(e) => handleChange("development_rights_premium", e.target.value)} />
              </div>
              <div>
                <Label className="form-label text-xs">TDR Cost</Label>
                <Input type="number" value={cost.tdr_cost} onChange={(e) => handleChange("tdr_cost", e.target.value)} />
              </div>
              <div>
                <Label className="form-label text-xs">Stamp Duty</Label>
                <Input type="number" value={cost.stamp_duty} onChange={(e) => handleChange("stamp_duty", e.target.value)} />
              </div>
              <div>
                <Label className="form-label text-xs">Govt. Charges</Label>
                <Input type="number" value={cost.government_charges} onChange={(e) => handleChange("government_charges", e.target.value)} />
              </div>
              <div>
                <Label className="form-label text-xs">Encumbrance Removal</Label>
                <Input type="number" value={cost.encumbrance_removal} onChange={(e) => handleChange("encumbrance_removal", e.target.value)} />
              </div>
            </CardContent>
          </Card>

          {/* Development Costs */}
          <Card className="md:col-span-2">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">Development Costs (Actual)</CardTitle>
                  <CardDescription>Total: {formatCurrency(totalDevCost)}</CardDescription>
                </div>
                <Button variant="outline" size="sm" onClick={fetchActualCostsFromProgress}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh from Progress
                </Button>
              </div>
            </CardHeader>
            <CardContent className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div>
                <Label className="form-label text-xs">Construction</Label>
                <Input 
                  type="number" 
                  value={actualCosts.construction_cost} 
                  disabled 
                  className="bg-green-50 border-green-200 font-medium"
                />
                <p className="text-xs text-green-600 mt-1">
                  {formatNumber(actualCosts.construction_completion, 1)}% complete
                </p>
              </div>
              <div>
                <Label className="form-label text-xs">Infrastructure</Label>
                <Input 
                  type="number" 
                  value={actualCosts.infrastructure_cost} 
                  disabled 
                  className="bg-green-50 border-green-200 font-medium"
                />
                <p className="text-xs text-green-600 mt-1">
                  {formatNumber(actualCosts.infrastructure_completion, 1)}% complete
                </p>
              </div>
              <div>
                <Label className="form-label text-xs">Equipment</Label>
                <Input type="number" value={cost.equipment_cost} onChange={(e) => handleChange("equipment_cost", e.target.value)} />
              </div>
              <div>
                <Label className="form-label text-xs">Taxes & Statutory</Label>
                <Input type="number" value={cost.taxes_statutory} onChange={(e) => handleChange("taxes_statutory", e.target.value)} />
              </div>
              <div>
                <Label className="form-label text-xs">Finance Cost</Label>
                <Input type="number" value={cost.finance_cost} onChange={(e) => handleChange("finance_cost", e.target.value)} />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="flex justify-end">
          <Button onClick={handleSave} className="bg-blue-600 hover:bg-blue-700" disabled={saving}>
            {saving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
            Save Cost Data
          </Button>
        </div>
      </div>
    </Layout>
  );
};

// Sales & Receivables Page
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
    agreement_date: ""
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
      setForm({ unit_number: "", building_id: "", building_name: "", carpet_area: 0, sale_value: 0, amount_received: 0, buyer_name: "", agreement_date: "" });
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
                <Button className="bg-blue-600 hover:bg-blue-700" onClick={() => { setEditingSale(null); setForm({ unit_number: "", building_id: "", building_name: "", carpet_area: 0, sale_value: 0, amount_received: 0, buyer_name: "", agreement_date: "" }); }}>
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
                    <Label className="form-label">Buyer Name</Label>
                    <Input value={form.buyer_name} onChange={(e) => setForm(f => ({ ...f, buyer_name: e.target.value }))} />
                  </div>
                  <div>
                    <Label className="form-label">Sale Value (₹)</Label>
                    <Input type="number" value={form.sale_value} onChange={(e) => setForm(f => ({ ...f, sale_value: parseFloat(e.target.value) || 0 }))} />
                  </div>
                  <div>
                    <Label className="form-label">Amount Received (₹)</Label>
                    <Input type="number" value={form.amount_received} onChange={(e) => setForm(f => ({ ...f, amount_received: parseFloat(e.target.value) || 0 }))} />
                  </div>
                  <div className="col-span-2">
                    <Label className="form-label">Agreement Date</Label>
                    <Input type="date" value={form.agreement_date} onChange={(e) => setForm(f => ({ ...f, agreement_date: e.target.value }))} />
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
        <div className="grid grid-cols-3 gap-4">
          <Card className="bg-blue-50">
            <CardContent className="p-4">
              <p className="text-sm text-blue-600">Total Sales Value</p>
              <p className="text-xl font-bold text-blue-900 currency">{formatCurrency(totalSales)}</p>
            </CardContent>
          </Card>
          <Card className="bg-emerald-50">
            <CardContent className="p-4">
              <p className="text-sm text-emerald-600">Amount Received</p>
              <p className="text-xl font-bold text-emerald-900 currency">{formatCurrency(totalReceived)}</p>
            </CardContent>
          </Card>
          <Card className="bg-amber-50">
            <CardContent className="p-4">
              <p className="text-sm text-amber-600">Receivables</p>
              <p className="text-xl font-bold text-amber-900 currency">{formatCurrency(totalReceivable)}</p>
            </CardContent>
          </Card>
        </div>

        {/* Sales Table */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Unit Sales ({sales.length} records)</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[400px]">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Unit</TableHead>
                    <TableHead>Building</TableHead>
                    <TableHead>Buyer</TableHead>
                    <TableHead className="text-right">Area</TableHead>
                    <TableHead className="text-right">Sale Value</TableHead>
                    <TableHead className="text-right">Received</TableHead>
                    <TableHead className="text-right">Receivable</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sales.map((sale) => (
                    <TableRow key={sale.sale_id}>
                      <TableCell className="font-medium">{sale.unit_number}</TableCell>
                      <TableCell>{sale.building_name}</TableCell>
                      <TableCell>{sale.buyer_name || "-"}</TableCell>
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
const ReportsPage = () => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState("");
  const [quarter, setQuarter] = useState("Q1");
  const [year, setYear] = useState(new Date().getFullYear());
  const [templates, setTemplates] = useState([]);
  const [generating, setGenerating] = useState("");
  const [downloading, setDownloading] = useState("");
  const [previewHtml, setPreviewHtml] = useState("");
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
    try {
      const res = await axios.get(`${API}/generate-report/${selectedProject}/${reportType}?quarter=${quarter}&year=${year}`);
      if (res.data.html) {
        setPreviewHtml(res.data.html);
      } else {
        // Generate HTML from data
        const html = generateHtmlFromData(reportType, res.data.data);
        setPreviewHtml(html);
      }
      setPreviewOpen(true);
    } catch (err) {
      toast.error("Failed to generate report");
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
      const response = await axios.get(
        `${API}/generate-pdf/${selectedProject}/${reportType}?quarter=${quarter}&year=${year}`,
        { responseType: 'blob' }
      );
      
      // Get filename from header or generate one
      const contentDisposition = response.headers['content-disposition'];
      let filename = `${reportType}_report.pdf`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=(.+)/);
        if (filenameMatch) filename = filenameMatch[1];
      }
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      
      // Create a temporary URL and trigger download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      
      // Append to body, click, and remove
      document.body.appendChild(link);
      link.click();
      
      // Cleanup after a short delay
      setTimeout(() => {
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }, 100);
      
      toast.success("PDF download started - check your Downloads folder");
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Failed to generate PDF";
      toast.error(errorMsg);
    } finally {
      setDownloading("");
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
                  {report.hasPdf && (
                    <Badge variant="outline" className="text-green-600 border-green-300 bg-green-50">
                      PDF Ready
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col gap-3">
                  <div className="flex items-center justify-between">
                    <Badge variant="secondary" className="capitalize">{report.role}</Badge>
                  </div>
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
                        <>
                          <Eye className="h-4 w-4 mr-1" />
                          Preview
                        </>
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
                          <>
                            <Download className="h-4 w-4 mr-1" />
                            Download PDF
                          </>
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
                          <>
                            <FileText className="h-4 w-4 mr-1" />
                            Generate
                          </>
                        )}
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Preview Dialog */}
        <Dialog open={previewOpen} onOpenChange={setPreviewOpen}>
          <DialogContent className="max-w-4xl max-h-[90vh]">
            <DialogHeader>
              <DialogTitle>Report Preview</DialogTitle>
            </DialogHeader>
            <ScrollArea className="h-[60vh] border rounded-lg">
              <div dangerouslySetInnerHTML={{ __html: previewHtml }} />
            </ScrollArea>
            <DialogFooter>
              <Button variant="outline" onClick={() => setPreviewOpen(false)}>Close</Button>
              <Button onClick={printReport} className="bg-blue-600 hover:bg-blue-700">
                <Download className="h-4 w-4 mr-2" />
                Print / Download PDF
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </Layout>
  );
};

// Import Page
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
        toast.success(`Imported ${res.data.created} sales records`);
      }
      if (res.data.errors?.length > 0) {
        toast.warning(`${res.data.errors.length} errors occurred`);
      }
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
      link.download = 'sales_template.xlsx';
      
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

            <div className="flex gap-3">
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
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="p-4 bg-slate-50 rounded-lg">
                  <p className="text-sm text-slate-600">Total Rows</p>
                  <p className="text-2xl font-bold">{result.total_rows || 0}</p>
                </div>
                <div className="p-4 bg-emerald-50 rounded-lg">
                  <p className="text-sm text-emerald-600">Imported</p>
                  <p className="text-2xl font-bold text-emerald-700">{result.created || 0}</p>
                </div>
                <div className="p-4 bg-rose-50 rounded-lg">
                  <p className="text-sm text-rose-600">Errors</p>
                  <p className="text-2xl font-bold text-rose-700">{result.errors?.length || 0}</p>
                </div>
              </div>

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
                <li><strong>Buyer Name</strong> - Customer name (optional)</li>
                <li><strong>Agreement Date</strong> - Date of agreement (optional)</li>
              </ul>
              <p className="text-slate-500 mt-4">
                Download the template for the exact format. The system auto-calculates Balance Receivable.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default App;
