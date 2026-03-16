import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/common/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import Dashboard from "./pages/Dashboard";
import Projects from "./pages/Projects";
import ProjectForm from "./pages/ProjectForm";
import LandCost from "./pages/LandCost";
import Buildings from "./pages/Buildings";
import ConstructionProgress from "./pages/ConstructionProgress";
import ProjectCosts from "./pages/ProjectCosts";
import Sales from "./pages/Sales";
import Reports from "./pages/Reports";
import Import from "./pages/Import";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects"
            element={
              <ProtectedRoute>
                <Projects />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/new"
            element={
              <ProtectedRoute>
                <ProjectForm />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:id/edit"
            element={
              <ProtectedRoute>
                <ProjectForm />
              </ProtectedRoute>
            }
          />
          <Route
            path="/land-cost"
            element={
              <ProtectedRoute>
                <LandCost />
              </ProtectedRoute>
            }
          />
          <Route
            path="/buildings"
            element={
              <ProtectedRoute>
                <Buildings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/construction"
            element={
              <ProtectedRoute>
                <ConstructionProgress />
              </ProtectedRoute>
            }
          />
          <Route
            path="/costs"
            element={
              <ProtectedRoute>
                <ProjectCosts />
              </ProtectedRoute>
            }
          />
          <Route
            path="/sales"
            element={
              <ProtectedRoute>
                <Sales />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports"
            element={
              <ProtectedRoute>
                <Reports />
              </ProtectedRoute>
            }
          />
          <Route
            path="/import"
            element={
              <ProtectedRoute>
                <Import />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
    </AuthProvider>
  );
}

export default App;
