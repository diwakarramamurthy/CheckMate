# RERA Compliance Manager - Frontend Page Structure

## 1. Application Structure

```
/app/frontend/src/
├── index.js                    # Entry point
├── App.js                      # Main app with routing
├── App.css                     # Global styles
├── index.css                   # Tailwind imports
│
├── config/
│   └── constants.js            # App constants
│
├── context/
│   ├── AuthContext.js          # Authentication state
│   └── AppContext.js           # Global app state
│
├── hooks/
│   ├── useAuth.js              # Auth hook
│   ├── useProjects.js          # Projects data hook
│   ├── useForms.js             # Forms data hook
│   └── useToast.js             # Toast notifications
│
├── services/
│   ├── api.js                  # Axios instance
│   ├── authService.js          # Auth API calls
│   ├── projectService.js       # Project API calls
│   ├── formService.js          # Form API calls
│   ├── excelService.js         # Excel API calls
│   └── exportService.js        # Export API calls
│
├── components/
│   ├── ui/                     # Shadcn UI components (provided)
│   │
│   ├── layout/
│   │   ├── Sidebar.jsx         # Main navigation sidebar
│   │   ├── Header.jsx          # Top header bar
│   │   ├── Footer.jsx          # Footer component
│   │   └── MainLayout.jsx      # Layout wrapper
│   │
│   ├── common/
│   │   ├── LoadingSpinner.jsx
│   │   ├── EmptyState.jsx
│   │   ├── StatusBadge.jsx
│   │   ├── DataTable.jsx
│   │   ├── Pagination.jsx
│   │   ├── SearchInput.jsx
│   │   ├── FilterDropdown.jsx
│   │   └── ConfirmDialog.jsx
│   │
│   ├── auth/
│   │   ├── LoginForm.jsx
│   │   ├── RegisterForm.jsx
│   │   ├── ForgotPasswordForm.jsx
│   │   └── ProtectedRoute.jsx
│   │
│   ├── dashboard/
│   │   ├── StatsCard.jsx
│   │   ├── ComplianceChart.jsx
│   │   ├── RecentActivity.jsx
│   │   ├── UpcomingDueDates.jsx
│   │   └── QuickActions.jsx
│   │
│   ├── projects/
│   │   ├── ProjectCard.jsx
│   │   ├── ProjectList.jsx
│   │   ├── ProjectForm.jsx
│   │   ├── ProjectDetails.jsx
│   │   ├── TeamAssignment.jsx
│   │   └── ComplianceStatus.jsx
│   │
│   ├── forms/
│   │   ├── FormWizard.jsx       # Multi-step form wizard
│   │   ├── FormPreview.jsx
│   │   ├── FormList.jsx
│   │   ├── FormCard.jsx
│   │   ├── FormSection.jsx
│   │   ├── SignaturePanel.jsx
│   │   ├── ValidationErrors.jsx
│   │   │
│   │   ├── form-types/          # Specific form components
│   │   │   ├── Form1Architect.jsx
│   │   │   ├── Form2ArchitectCompletion.jsx
│   │   │   ├── Form3Engineer.jsx
│   │   │   ├── Form4CA.jsx
│   │   │   ├── Form5CACompliance.jsx
│   │   │   ├── Form6Auditor.jsx
│   │   │   └── AnnexureAReceivables.jsx
│   │   │
│   │   └── fields/              # Form field components
│   │       ├── TextField.jsx
│   │       ├── NumberField.jsx
│   │       ├── DateField.jsx
│   │       ├── SelectField.jsx
│   │       ├── TextAreaField.jsx
│   │       ├── TableField.jsx
│   │       └── CurrencyField.jsx
│   │
│   ├── excel/
│   │   ├── ExcelUploader.jsx
│   │   ├── UploadProgress.jsx
│   │   ├── SheetPreview.jsx
│   │   ├── MappingConfig.jsx
│   │   ├── ValidationResults.jsx
│   │   └── UploadHistory.jsx
│   │
│   ├── exports/
│   │   ├── ExportDropdown.jsx
│   │   ├── ExportProgress.jsx
│   │   ├── PreviewModal.jsx
│   │   └── DownloadHistory.jsx
│   │
│   └── admin/
│       ├── UserManagement.jsx
│       ├── UserForm.jsx
│       ├── TemplateManager.jsx
│       ├── OrgSettings.jsx
│       └── AuditLog.jsx
│
└── pages/
    ├── auth/
    │   ├── LoginPage.jsx
    │   ├── RegisterPage.jsx
    │   └── ForgotPasswordPage.jsx
    │
    ├── DashboardPage.jsx
    │
    ├── projects/
    │   ├── ProjectsListPage.jsx
    │   ├── ProjectDetailPage.jsx
    │   ├── CreateProjectPage.jsx
    │   └── EditProjectPage.jsx
    │
    ├── forms/
    │   ├── FormsListPage.jsx
    │   ├── FormDetailPage.jsx
    │   ├── CreateFormPage.jsx
    │   └── EditFormPage.jsx
    │
    ├── excel/
    │   └── ExcelUploadPage.jsx
    │
    ├── reports/
    │   └── ReportsPage.jsx
    │
    ├── admin/
    │   ├── UsersPage.jsx
    │   ├── TemplatesPage.jsx
    │   ├── SettingsPage.jsx
    │   └── AuditLogPage.jsx
    │
    └── NotFoundPage.jsx
```

## 2. Page Wireframes & Descriptions

### 2.1 Authentication Pages

#### Login Page (`/login`)
```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  ┌─────────────────────────────┬────────────────────────────────────┐   │
│  │                             │                                    │   │
│  │   [Background Image:        │   ┌────────────────────────────┐  │   │
│  │    Modern Architecture]     │   │  RERA COMPLIANCE MANAGER   │  │   │
│  │                             │   │                            │  │   │
│  │                             │   │  Welcome back              │  │   │
│  │                             │   │  Sign in to your account   │  │   │
│  │                             │   │                            │  │   │
│  │                             │   │  ┌──────────────────────┐  │  │   │
│  │                             │   │  │ Email                │  │  │   │
│  │                             │   │  └──────────────────────┘  │  │   │
│  │                             │   │                            │  │   │
│  │                             │   │  ┌──────────────────────┐  │  │   │
│  │                             │   │  │ Password             │  │  │   │
│  │                             │   │  └──────────────────────┘  │  │   │
│  │                             │   │                            │  │   │
│  │                             │   │  [ ] Remember me           │  │   │
│  │                             │   │                            │  │   │
│  │                             │   │  [     Sign In Button    ] │  │   │
│  │                             │   │                            │  │   │
│  │                             │   │  Forgot password?          │  │   │
│  │                             │   │  Don't have account?       │  │   │
│  │                             │   └────────────────────────────┘  │   │
│  │                             │                                    │   │
│  └─────────────────────────────┴────────────────────────────────────┘   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Dashboard Page (`/dashboard`)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ ┌──────┐ RERA Compliance Manager                    [User ▼] [Notif]    │
│ │ Logo │                                                                 │
├──────────┬───────────────────────────────────────────────────────────────┤
│          │                                                               │
│  MENU    │  Good morning, Rajesh                     Q4 2024 · Goa RERA │
│          │                                                               │
│ Dashboard│  ┌─────────────────────────────────────────────────────────┐ │
│          │  │  BENTO GRID LAYOUT - Stats Overview                     │ │
│ Projects │  │                                                         │ │
│          │  │  ┌───────────────────────┐  ┌─────────┐  ┌─────────┐   │ │
│ Forms    │  │  │                       │  │  Total  │  │ Pending │   │ │
│  ├ Form 1│  │  │   Compliance Score    │  │Projects │  │  Forms  │   │ │
│  ├ Form 2│  │  │       78%             │  │   12    │  │   23    │   │ │
│  ├ Form 3│  │  │   [Progress Ring]     │  │         │  │         │   │ │
│  ├ Form 4│  │  │                       │  └─────────┘  └─────────┘   │ │
│  ├ Form 5│  │  │                       │  ┌─────────┐  ┌─────────┐   │ │
│  ├ Form 6│  │  │                       │  │Submitted│  │ Overdue │   │ │
│  └ Ann-A │  │  │                       │  │  Forms  │  │  Forms  │   │ │
│          │  │  └───────────────────────┘  │   45    │  │    3    │   │ │
│ Excel    │  │                             └─────────┘  └─────────┘   │ │
│ Upload   │  └─────────────────────────────────────────────────────────┘ │
│          │                                                               │
│ Reports  │  ┌────────────────────────────┐  ┌────────────────────────┐ │
│          │  │  Upcoming Due Dates        │  │   Recent Activity      │ │
│ ─────────│  │                            │  │                        │ │
│          │  │  • Form 1 - Sunset Heights │  │  • Form submitted...   │ │
│ Admin    │  │    Due: Jan 31, 2024       │  │  • Project created...  │ │
│  ├ Users │  │                            │  │  • Excel uploaded...   │ │
│  ├ Templ │  │  • Annexure A - Marina...  │  │                        │ │
│  └ Settin│  │    Due: Feb 15, 2024       │  │                        │ │
│          │  └────────────────────────────┘  └────────────────────────┘ │
│          │                                                               │
│ [Logout] │  ┌─────────────────────────────────────────────────────────┐ │
│          │  │  Quick Actions                                          │ │
│          │  │  [+ New Project] [Upload Excel] [Generate Report]       │ │
│          │  └─────────────────────────────────────────────────────────┘ │
└──────────┴───────────────────────────────────────────────────────────────┘
```

### 2.3 Projects List Page (`/projects`)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ [Sidebar] │  Projects                                    [+ New Project] │
├───────────┼──────────────────────────────────────────────────────────────┤
│           │                                                              │
│           │  ┌─────────────────────────────────────────────────────────┐│
│           │  │ [Search...        ]  [State ▼]  [Status ▼]  [Sort ▼]   ││
│           │  └─────────────────────────────────────────────────────────┘│
│           │                                                              │
│           │  ┌─────────────────────────────────────────────────────────┐│
│           │  │  PROJECT CARD                                           ││
│           │  │  ┌───────────────────────────────────────────────────┐  ││
│           │  │  │  Sunset Heights Phase 2              [Compliant]  │  ││
│           │  │  │  RERA: PRGO12345 · Goa                           │  ││
│           │  │  │                                                   │  ││
│           │  │  │  Completion: 58%  ████████░░░░░░░░░               │  ││
│           │  │  │  Due: Jan 31, 2024                                │  ││
│           │  │  │                                                   │  ││
│           │  │  │  Forms: ✓6/7 complete    [View] [Edit] [...]     │  ││
│           │  │  └───────────────────────────────────────────────────┘  ││
│           │  │                                                         ││
│           │  │  ┌───────────────────────────────────────────────────┐  ││
│           │  │  │  Marina Bay Residences                [Pending]   │  ││
│           │  │  │  RERA: PRGO67890 · Goa                           │  ││
│           │  │  │  ...                                              │  ││
│           │  │  └───────────────────────────────────────────────────┘  ││
│           │  │                                                         ││
│           │  └─────────────────────────────────────────────────────────┘│
│           │                                                              │
│           │  [< Prev]  Page 1 of 5  [Next >]                           │
│           │                                                              │
└───────────┴──────────────────────────────────────────────────────────────┘
```

### 2.4 Form Creation Page - Wizard Layout (`/forms/new`)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ [Sidebar] │  Create Form 1 - Architect Certificate                       │
├───────────┼──────────────────────────────────────────────────────────────┤
│           │                                                              │
│           │  ┌─────────────────────────────────────────────────────────┐│
│           │  │  WIZARD PROGRESS                                        ││
│           │  │  ┌──────┐ → ┌──────┐ → ┌──────┐ → ┌──────┐ → ┌──────┐  ││
│           │  │  │ 1.   │   │ 2.   │   │ 3.   │   │ 4.   │   │ 5.   │  ││
│           │  │  │Basic │   │Const │   │Dev   │   │Review│   │Sign  │  ││
│           │  │  │Info  │   │Status│   │iations│  │      │   │      │  ││
│           │  │  └──────┘   └──────┘   └──────┘   └──────┘   └──────┘  ││
│           │  │    ●           ○           ○           ○         ○     ││
│           │  └─────────────────────────────────────────────────────────┘│
│           │                                                              │
│           │  ┌─────────────────────────────────────────────────────────┐│
│           │  │  Step 1: Basic Information                              ││
│           │  │                                                         ││
│           │  │  Project *                                              ││
│           │  │  ┌───────────────────────────────────────────────────┐  ││
│           │  │  │ Sunset Heights Phase 2                        ▼   │  ││
│           │  │  └───────────────────────────────────────────────────┘  ││
│           │  │                                                         ││
│           │  │  Reporting Period *                                     ││
│           │  │  ┌─────────────────┐  ┌─────────────────┐              ││
│           │  │  │ Q4           ▼  │  │ 2024         ▼  │              ││
│           │  │  └─────────────────┘  └─────────────────┘              ││
│           │  │                                                         ││
│           │  │  Certificate Number *                                   ││
│           │  │  ┌───────────────────────────────────────────────────┐  ││
│           │  │  │ ARCH/2024/001                                     │  ││
│           │  │  └───────────────────────────────────────────────────┘  ││
│           │  │                                                         ││
│           │  └─────────────────────────────────────────────────────────┘│
│           │                                                              │
│           │  [Cancel]                              [Save Draft] [Next →]│
│           │                                                              │
└───────────┴──────────────────────────────────────────────────────────────┘
```

### 2.5 Excel Upload Page (`/excel/upload`)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ [Sidebar] │  Excel Upload                                                │
├───────────┼──────────────────────────────────────────────────────────────┤
│           │                                                              │
│           │  ┌─────────────────────────────────────────────────────────┐│
│           │  │  Upload Financial Data                                  ││
│           │  │                                                         ││
│           │  │  Select Project *                                       ││
│           │  │  ┌───────────────────────────────────────────────────┐  ││
│           │  │  │ Sunset Heights Phase 2                        ▼   │  ││
│           │  │  └───────────────────────────────────────────────────┘  ││
│           │  │                                                         ││
│           │  │  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐  ││
│           │  │                                                         ││
│           │  │  │         📄 Drag & drop Excel file here              │  ││
│           │  │                or                                       ││
│           │  │  │              [Browse Files]                         │  ││
│           │  │                                                         ││
│           │  │  │         Supported: .xlsx, .xls                      │  ││
│           │  │             Max size: 10MB                              ││
│           │  │  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘  ││
│           │  │                                                         ││
│           │  │  [Download Template]   What sheets are supported?       ││
│           │  │                                                         ││
│           │  └─────────────────────────────────────────────────────────┘│
│           │                                                              │
│           │  ┌─────────────────────────────────────────────────────────┐│
│           │  │  Recent Uploads                                         ││
│           │  │  ┌───────────────────────────────────────────────────┐  ││
│           │  │  │ Filename           Project        Date      Status│  ││
│           │  │  │ Q3_Data.xlsx       Sunset...    Dec 15    ✓ Done │  ││
│           │  │  │ Receivables.xlsx   Marina...    Dec 10    ✓ Done │  ││
│           │  │  └───────────────────────────────────────────────────┘  ││
│           │  └─────────────────────────────────────────────────────────┘│
│           │                                                              │
└───────────┴──────────────────────────────────────────────────────────────┘
```

### 2.6 Form Preview with Export (`/forms/{id}`)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ [Sidebar] │  Form 1 - Architect Certificate          [Export ▼] [Edit]  │
├───────────┼──────────────────────────────────────────────────────────────┤
│           │                                                              │
│           │  ┌──────────────────────────────┐ ┌────────────────────────┐│
│           │  │  Status: ✓ Submitted         │ │ Export Options:        ││
│           │  │  Quarter: Q4 2024            │ │ • Download PDF         ││
│           │  │  Project: Sunset Heights     │ │ • Download Word        ││
│           │  └──────────────────────────────┘ │ • Download Excel       ││
│           │                                    │ • Print                ││
│           │  ┌─────────────────────────────────└────────────────────────┤
│           │  │                                                          │
│           │  │  ╔══════════════════════════════════════════════════╗   │
│           │  │  ║           GOA REAL ESTATE REGULATORY             ║   │
│           │  │  ║                   AUTHORITY                      ║   │
│           │  │  ║                                                  ║   │
│           │  │  ║              FORM 1                              ║   │
│           │  │  ║     ARCHITECT'S CERTIFICATE                      ║   │
│           │  │  ║                                                  ║   │
│           │  │  ║  Project: Sunset Heights Phase 2                 ║   │
│           │  │  ║  RERA No: PRGO12345                              ║   │
│           │  │  ║                                                  ║   │
│           │  │  ║  I, Ar. Rajesh Sharma (COA/2020/12345),          ║   │
│           │  │  ║  hereby certify that as on 31st December 2024:  ║   │
│           │  │  ║                                                  ║   │
│           │  │  ║  1. Construction Status: 58% complete            ║   │
│           │  │  ║  2. Current Stage: Structural work - 7th floor   ║   │
│           │  │  ║  3. Deviations from sanctioned plan: None        ║   │
│           │  │  ║                                                  ║   │
│           │  │  ║                                                  ║   │
│           │  │  ║  Signature: ____________________                 ║   │
│           │  │  ║  Date: December 31, 2024                         ║   │
│           │  │  ╚══════════════════════════════════════════════════╝   │
│           │  │                                                          │
│           │  └──────────────────────────────────────────────────────────┤
│           │                                                              │
└───────────┴──────────────────────────────────────────────────────────────┘
```

## 3. Route Configuration

```javascript
// App.js - Route Structure

const routes = [
  // Public Routes
  { path: "/login", element: <LoginPage />, public: true },
  { path: "/register", element: <RegisterPage />, public: true },
  { path: "/forgot-password", element: <ForgotPasswordPage />, public: true },
  
  // Protected Routes
  { path: "/", element: <Navigate to="/dashboard" /> },
  { path: "/dashboard", element: <DashboardPage />, roles: ["all"] },
  
  // Project Routes
  { path: "/projects", element: <ProjectsListPage />, roles: ["all"] },
  { path: "/projects/new", element: <CreateProjectPage />, roles: ["admin", "developer"] },
  { path: "/projects/:id", element: <ProjectDetailPage />, roles: ["all"] },
  { path: "/projects/:id/edit", element: <EditProjectPage />, roles: ["admin", "developer"] },
  
  // Form Routes
  { path: "/forms", element: <FormsListPage />, roles: ["all"] },
  { path: "/forms/new", element: <CreateFormPage />, roles: ["all"] },
  { path: "/forms/:id", element: <FormDetailPage />, roles: ["all"] },
  { path: "/forms/:id/edit", element: <EditFormPage />, roles: ["role-based"] },
  
  // Excel Upload
  { path: "/excel/upload", element: <ExcelUploadPage />, roles: ["developer", "ca"] },
  
  // Reports
  { path: "/reports", element: <ReportsPage />, roles: ["all"] },
  
  // Admin Routes
  { path: "/admin/users", element: <UsersPage />, roles: ["admin"] },
  { path: "/admin/templates", element: <TemplatesPage />, roles: ["admin"] },
  { path: "/admin/settings", element: <SettingsPage />, roles: ["admin"] },
  { path: "/admin/audit-log", element: <AuditLogPage />, roles: ["admin"] },
  
  // 404
  { path: "*", element: <NotFoundPage /> }
];
```

## 4. State Management

```javascript
// AuthContext - Authentication State
{
  user: {
    user_id: string,
    email: string,
    role: string,
    profile: object,
    organization_id: string
  },
  isAuthenticated: boolean,
  isLoading: boolean,
  token: string
}

// AppContext - Application State
{
  projects: [],
  selectedProject: null,
  forms: [],
  selectedForm: null,
  templates: [],
  notifications: [],
  filters: {
    state: string,
    status: string,
    dateRange: object
  }
}
```

## 5. Key UI Components Behavior

### Form Wizard
- Multi-step navigation
- Auto-save on step change
- Progress indicator
- Validation per step
- Back/Next navigation
- Final review step

### Export Dropdown
- Format selection (PDF/Word/Excel)
- Options modal (watermark, signatures)
- Progress indicator
- Download trigger

### Data Tables
- Column sorting
- Filtering
- Pagination
- Row selection
- Bulk actions
- Export functionality
