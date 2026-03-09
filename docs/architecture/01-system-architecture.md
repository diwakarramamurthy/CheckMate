# RERA Compliance Manager - System Architecture

## 1. System Overview

The RERA Compliance Manager is a multi-tenant SaaS application designed to automate RERA (Real Estate Regulatory Authority) compliance reporting for real estate developers in India.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              RERA COMPLIANCE MANAGER                             │
│                            System Architecture Diagram                           │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                 CLIENT LAYER                                     │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐     │
│  │   Web Application   │  │    Mobile Web       │  │   Admin Portal      │     │
│  │   (React + Vite)    │  │   (Responsive)      │  │   (Role-based)      │     │
│  └──────────┬──────────┘  └──────────┬──────────┘  └──────────┬──────────┘     │
└─────────────┼────────────────────────┼────────────────────────┼─────────────────┘
              │                        │                        │
              └────────────────────────┼────────────────────────┘
                                       │ HTTPS/REST
┌──────────────────────────────────────┼──────────────────────────────────────────┐
│                              API GATEWAY LAYER                                   │
│  ┌───────────────────────────────────┴───────────────────────────────────┐     │
│  │                    Kubernetes Ingress Controller                       │     │
│  │                    (Route /api/* to Backend:8001)                      │     │
│  └───────────────────────────────────┬───────────────────────────────────┘     │
└──────────────────────────────────────┼──────────────────────────────────────────┘
                                       │
┌──────────────────────────────────────┼──────────────────────────────────────────┐
│                             APPLICATION LAYER                                    │
│  ┌───────────────────────────────────┴───────────────────────────────────┐     │
│  │                     FastAPI Backend (Python 3.11+)                     │     │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     │     │
│  │  │ Auth Module │ │ Project Mgmt│ │Excel Parser │ │Report Engine│     │     │
│  │  │   (JWT)     │ │   Module    │ │   Module    │ │   Module    │     │     │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘     │     │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     │     │
│  │  │ Template    │ │ Validation  │ │ Export      │ │ Audit       │     │     │
│  │  │  Manager    │ │   Engine    │ │  Service    │ │  Logger     │     │     │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘     │     │
│  └───────────────────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────┬──────────────────────────────────────────┘
                                       │
┌──────────────────────────────────────┼──────────────────────────────────────────┐
│                              DATA LAYER                                          │
│  ┌─────────────────────┐  ┌──────────┴──────────┐  ┌─────────────────────┐     │
│  │     MongoDB         │  │   File Storage      │  │   Redis Cache       │     │
│  │   (Primary DB)      │  │   (Generated Docs)  │  │   (Sessions/Queue)  │     │
│  │                     │  │                     │  │                     │     │
│  │ - Users             │  │ - PDF Files         │  │ - JWT Tokens        │     │
│  │ - Projects          │  │ - Excel Exports     │  │ - Report Cache      │     │
│  │ - Forms             │  │ - Word Documents    │  │ - Rate Limiting     │     │
│  │ - Templates         │  │ - Upload Temp       │  │                     │     │
│  │ - Audit Logs        │  │                     │  │                     │     │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL SERVICES                                      │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐     │
│  │   Email Service     │  │   PDF Generator     │  │   State RERA APIs   │     │
│  │   (Notifications)   │  │   (WeasyPrint)      │  │   (Future Integration)│   │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 2. Technology Stack

### Frontend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | React 18+ | UI Component Library |
| Styling | TailwindCSS + Shadcn/UI | Design System |
| State Management | React Context + useState | Application State |
| HTTP Client | Axios | API Communication |
| Form Handling | React Hook Form | Form Validation |
| Routing | React Router v6 | Client-side Navigation |
| File Upload | React Dropzone | Excel Upload |
| Export Preview | React-PDF | PDF Preview |

### Backend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | FastAPI | REST API Server |
| Runtime | Python 3.11+ | Server Runtime |
| Authentication | PyJWT + bcrypt | JWT Token Auth |
| Database ODM | Motor (async) | MongoDB Driver |
| Excel Processing | openpyxl, pandas | Excel Parsing |
| PDF Generation | WeasyPrint, ReportLab | PDF Export |
| Word Generation | python-docx | Word Export |
| Excel Generation | openpyxl | Excel Export |
| Validation | Pydantic v2 | Data Validation |

### Database
| Component | Technology | Purpose |
|-----------|------------|---------|
| Primary DB | MongoDB | Document Storage |
| Cache | Redis (optional) | Session/Cache |

### Infrastructure
| Component | Technology | Purpose |
|-----------|------------|---------|
| Container | Docker | Containerization |
| Orchestration | Kubernetes | Deployment |
| Process Manager | Supervisor | Service Management |
| Reverse Proxy | Nginx/Ingress | Load Balancing |

## 3. Core Modules

### 3.1 Authentication Module
- JWT-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Token refresh mechanism
- Session management

### 3.2 Project Management Module
- CRUD operations for projects
- Project status tracking
- Team assignment
- Timeline management
- Document association

### 3.3 Excel Parser Module
- Multi-sheet Excel parsing
- Data validation against templates
- Error reporting with cell references
- Data transformation pipeline
- Column mapping configuration

### 3.4 Report Engine Module
- Template-based report generation
- Multi-format export (PDF/Excel/Word)
- Dynamic field population
- State-specific formatting
- Digital signature placeholders

### 3.5 Template Manager Module
- State-wise template storage
- Version control for templates
- Template preview
- Custom field definitions
- Validation rule configuration

### 3.6 Validation Engine Module
- Business rule validation
- Cross-field validation
- State-specific rules
- Error aggregation
- Validation report generation

### 3.7 Export Service Module
- PDF generation with WeasyPrint
- Word document generation with python-docx
- Excel export with openpyxl
- Batch export capability
- Download management

### 3.8 Audit Logger Module
- Action logging
- User activity tracking
- Change history
- Compliance audit trail
- Report access logs

## 4. Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                               │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: Transport Security                                     │
│  - HTTPS/TLS 1.3 encryption                                     │
│  - Certificate management                                        │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: Authentication                                         │
│  - JWT tokens (access + refresh)                                 │
│  - Secure password hashing (bcrypt, 12 rounds)                  │
│  - Token expiration (access: 30min, refresh: 7 days)            │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: Authorization                                          │
│  - Role-based access control (RBAC)                             │
│  - Resource-level permissions                                    │
│  - Project-level access control                                  │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4: Data Security                                          │
│  - Input validation (Pydantic)                                   │
│  - SQL/NoSQL injection prevention                                │
│  - XSS protection                                                │
│  - File upload validation                                        │
├─────────────────────────────────────────────────────────────────┤
│  Layer 5: Audit & Compliance                                     │
│  - Complete audit trail                                          │
│  - Access logging                                                │
│  - Data retention policies                                       │
└─────────────────────────────────────────────────────────────────┘
```

## 5. Scalability Considerations

### Horizontal Scaling
- Stateless API design
- External session storage (Redis)
- Load balancer ready
- Database connection pooling

### Vertical Scaling
- Async I/O operations
- Background task processing
- Efficient memory management
- Query optimization

### Multi-tenancy
- Organization-level isolation
- Shared infrastructure
- Tenant-specific configurations
- Data segregation

## 6. High Availability

- Multiple API replicas
- Database replica sets
- Health check endpoints
- Graceful degradation
- Error recovery mechanisms
