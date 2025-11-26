# ChainSight AI - Complete System Guide

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture & Technology Stack](#architecture--technology-stack)
3. [Database Schema & Relations](#database-schema--relations)
4. [Data Pipeline Workflow](#data-pipeline-workflow)
5. [Feature Overview](#feature-overview)
6. [Getting Started](#getting-started)
7. [Scalability & Performance](#scalability--performance)
8. [Development Guide](#development-guide)

---

## 1. System Overview

### What is ChainSight AI?

ChainSight AI is a **multi-tenant SaaS platform** for AI-powered contract analysis and management. It helps legal teams, SMEs, and compliance officers automate contract review, risk assessment, and compliance monitoring.

### Key Features

- **AI Contract Analysis**: GPT-4 powered analysis for risk, compliance, and clause extraction
- **Multi-Tenancy**: Complete tenant isolation with subdomain support
- **Document Processing**: PDF, DOCX, images with OCR support
- **Real-time Alerts**: Configurable alerts for risks and compliance
- **Export Reports**: PDF/DOCX report generation
- **Scalable Infrastructure**: Built to handle 500K+ users

### Who Uses ChainSight AI?

| User Type | Problem | Solution | Value |
|-----------|---------|----------|-------|
| **Legal Departments** | Manual review takes weeks | AI analyzes in minutes | 90% faster review |
| **SMEs** | Can't afford legal teams | Affordable AI analysis | Professional review at SMB prices |
| **Contract Managers** | Scattered contracts | Centralized repository | Complete lifecycle management |
| **Compliance Officers** | Manual compliance checking | Automated risk scoring | Proactive compliance |

---

## 2. Architecture & Technology Stack

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                  (React/Next.js - Separate)                  │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────┴────────────────────────────────────┐
│                    Django REST API                           │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Accounts   │  │  Contracts   │  │   Tenants    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Alerts    │  │   Suppliers  │  │     Chat     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                    Background Tasks                          │
│                    (Celery Workers)                          │
│  - Contract Analysis                                         │
│  - Email Notifications                                       │
│  - Alert Processing                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                     Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │   MongoDB    │  │     Redis    │      │
│  │  (Primary)   │  │  (Analysis)  │  │   (Cache)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                 External Services                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    AWS S3    │  │   OpenAI     │  │   SendGrid   │      │
│  │  (Storage)   │  │   (AI/ML)    │  │   (Email)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### Backend
- **Framework**: Django 5.0, Django REST Framework
- **Language**: Python 3.12
- **Authentication**: JWT (Simple JWT)
- **API Documentation**: drf-yasg (Swagger/OpenAPI)

#### Databases
- **PostgreSQL**: Primary database for structured data
- **MongoDB**: Document storage for analysis results
- **Redis**: Caching, session storage, Celery broker

#### Async Processing
- **Celery**: Distributed task queue
- **RabbitMQ**: Message broker (alternative to Redis)
- **Celery Beat**: Scheduled tasks

#### AI/ML
- **OpenAI GPT-4**: Contract analysis
- **Pinecone**: Vector database for RAG chat
- **Tiktoken**: Token counting

#### Document Processing
- **PyPDF2**: PDF text extraction
- **python-docx**: Word document processing
- **Pillow**: Image processing
- **pytesseract**: OCR for scanned documents

#### File Storage
- **AWS S3**: Cloud file storage
- **django-storages**: Django S3 integration

#### Communications
- **SendGrid**: Email notifications
- **Twilio**: SMS notifications (optional)

#### DevOps
- **Docker**: Containerization
- **Gunicorn**: WSGI server
- **Whitenoise**: Static file serving
- **Sentry**: Error tracking

---

## 3. Database Schema & Relations

### Entity Relationship Diagram

```
┌─────────────────┐
│     Tenant      │
│─────────────────│
│ id (PK)         │
│ name            │
│ subdomain       │◄────────┐
│ plan_type       │         │
│ max_users       │         │
│ max_contracts   │         │
│ status          │         │
└─────────────────┘         │
        ▲                   │
        │                   │
        │ tenant_id (FK)    │
        │                   │
┌─────────────────┐         │
│      User       │         │
│─────────────────│         │
│ id (PK)         │         │
│ tenant_id (FK)  │─────────┤
│ email           │         │
│ password        │         │
│ role            │         │
│ is_active       │         │
└─────────────────┘         │
        ▲                   │
        │                   │
        │ uploaded_by (FK)  │
        │                   │
┌─────────────────┐         │
│    Contract     │         │
│─────────────────│         │
│ id (PK)         │         │
│ tenant_id (FK)  │─────────┘
│ uploaded_by(FK) │─────────┘
│ file_path       │
│ file_hash       │
│ status          │
│ risk_score      │
│ industry        │
└─────────────────┘
        ▲
        │ contract_id (FK)
        │
┌─────────────────┐
│ContractAnalysis │
│─────────────────│
│ id (PK)         │
│ contract_id(FK) │─────────┘
│ mongo_doc_id    │
│ risk_score      │
│ priority_level  │
└─────────────────┘
        │
┌─────────────────┐
│     Clause      │
│─────────────────│
│ id (PK)         │
│ contract_id(FK) │─────────┘
│ clause_type     │
│ content         │
│ risk_level      │
└─────────────────┘
```

### Core Models

#### 1. Tenant Model
```python
class Tenant(TimeStampedModel):
    name = models.CharField(max_length=200)
    subdomain = models.CharField(max_length=100, unique=True)
    plan_type = models.CharField(choices=PLAN_CHOICES)  # free, starter, professional, enterprise
    max_users = models.IntegerField(default=10)
    max_contracts = models.IntegerField(default=1000)
    status = models.CharField(choices=STATUS_CHOICES)  # active, suspended, inactive
```

**Purpose**: Multi-tenant organization model. Each company using ChainSight AI has one Tenant record.

**Relations**: 
- One-to-Many with User
- One-to-Many with Contract

#### 2. User Model
```python
class User(AbstractBaseUser, PermissionsMixin):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    role = models.CharField(choices=ROLE_CHOICES)  # admin, manager, user, viewer
    is_active = models.BooleanField(default=True)
    mfa_enabled = models.BooleanField(default=False)
```

**Purpose**: Custom user model with tenant relationship and role-based permissions.

**Relations**:
- Many-to-One with Tenant
- One-to-Many with Contract (as uploader)

#### 3. Contract Model
```python
class Contract(TenantAwareModel):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL)
    
    # File info
    original_filename = models.CharField(max_length=500)
    file_path = models.CharField(max_length=1000)  # S3 path
    file_hash = models.CharField(max_length=64)  # SHA-256
    
    # Status
    status = models.CharField(choices=STATUS_CHOICES)  # pending, processing, completed, failed
    progress_percentage = models.IntegerField(default=0)
    
    # Contract details
    industry = models.CharField(choices=INDUSTRY_CHOICES)
    contract_type = models.CharField(max_length=100)
    expiry_date = models.DateField(null=True)
    
    # Analysis results
    risk_score = models.IntegerField(null=True)
    compliance_score = models.IntegerField(null=True)
    sentiment_score = models.FloatField(null=True)
```

**Purpose**: Main contract document model storing file info, metadata, and analysis results.

**Relations**:
- Many-to-One with Tenant
- Many-to-One with User (uploader)
- One-to-One with ContractAnalysis
- One-to-Many with Clause

#### 4. ContractAnalysis Model
```python
class ContractAnalysis(TenantAwareModel):
    contract = models.OneToOneField('Contract', on_delete=models.CASCADE)
    mongo_document_id = models.CharField(max_length=100)  # Reference to MongoDB doc
    overall_risk_score = models.IntegerField()
    critical_issues_count = models.IntegerField(default=0)
    priority_level = models.CharField(choices=PRIORITY_CHOICES)
    processing_time = models.FloatField()
    model_used = models.CharField(max_length=100)  # e.g., "gpt-4-turbo"
```

**Purpose**: Stores quick-access analysis summary. Full analysis details stored in MongoDB.

**Relations**:
- One-to-One with Contract

#### 5. Clause Model
```python
class Clause(TenantAwareModel):
    contract = models.ForeignKey('Contract', on_delete=models.CASCADE)
    clause_number = models.CharField(max_length=50)
    clause_type = models.CharField(choices=CLAUSE_TYPE_CHOICES)
    title = models.CharField(max_length=500)
    content = models.TextField()
    risk_level = models.CharField(choices=RISK_LEVEL_CHOICES)
    quality_score = models.IntegerField(null=True)
    is_standard = models.BooleanField(default=False)
    has_issues = models.BooleanField(default=False)
```

**Purpose**: Individual contract clauses extracted by AI.

**Relations**:
- Many-to-One with Contract

### Database Indexes

Optimized indexes for performance:

```python
# Contract indexes
indexes = [
    models.Index(fields=['tenant', '-created_at']),  # List contracts by tenant
    models.Index(fields=['status']),                  # Filter by status
    models.Index(fields=['risk_score']),              # Sort by risk
    models.Index(fields=['expiry_date']),             # Expiring contracts
    models.Index(fields=['file_hash']),               # Duplicate detection
]

# User indexes
indexes = [
    models.Index(fields=['tenant', 'email']),         # Login lookup
    models.Index(fields=['tenant', 'role']),          # Role-based queries
]

# Tenant indexes
indexes = [
    models.Index(fields=['subdomain']),               # Subdomain routing
    models.Index(fields=['status']),                  # Active tenants
]
```

---

## 4. Data Pipeline Workflow

### Complete Contract Analysis Pipeline

```
┌────────────────────────────────────────────────────────────────┐
│  STEP 1: USER UPLOADS CONTRACT                                 │
├────────────────────────────────────────────────────────────────┤
│  POST /api/v2/contracts/upload/                                │
│  FormData: file=contract.pdf, industry=technology              │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────┐
│  STEP 2: FILE PROCESSING                                       │
├────────────────────────────────────────────────────────────────┤
│  1. Validate file (type, size, virus scan)                     │
│  2. Calculate SHA-256 hash                                     │
│  3. Check for duplicates                                       │
│  4. Upload to S3: s3://bucket/tenant_1/contracts/file.pdf      │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────┐
│  STEP 3: DATABASE RECORD CREATION                              │
├────────────────────────────────────────────────────────────────┤
│  Contract.objects.create(                                      │
│      tenant=request.tenant,                                    │
│      uploaded_by=request.user,                                 │
│      file_path=s3_path,                                        │
│      status='pending'                                          │
│  )                                                             │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────┐
│  STEP 4: ASYNC TASK QUEUED                                     │
├────────────────────────────────────────────────────────────────┤
│  analyze_contract_task.delay(contract_id)                      │
│  → Task sent to Celery via Redis                               │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────┐
│  STEP 5: TEXT EXTRACTION (Celery Worker)                       │
├────────────────────────────────────────────────────────────────┤
│  - Download file from S3                                       │
│  - Detect if scanned PDF (OCR needed)                          │
│  - Extract text using PyPDF2 or pytesseract                    │
│  - Progress: 30%                                               │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────┐
│  STEP 6: AI ANALYSIS (OpenAI GPT-4)                            │
├────────────────────────────────────────────────────────────────┤
│  Send to OpenAI:                                               │
│  - Overall risk assessment (1-100)                             │
│  - Compliance score                                            │
│  - Critical issues identification                              │
│  - Missing clauses detection                                   │
│  - Progress: 60%                                               │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────┐
│  STEP 7: CLAUSE EXTRACTION                                     │
├────────────────────────────────────────────────────────────────┤
│  AI extracts individual clauses:                               │
│  - Payment terms                                               │
│  - Termination clauses                                         │
│  - Liability clauses                                           │
│  - Confidentiality clauses                                     │
│  - Each clause saved to PostgreSQL                             │
│  - Progress: 80%                                               │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────┐
│  STEP 8: SENTIMENT ANALYSIS                                    │
├────────────────────────────────────────────────────────────────┤
│  Analyze contract tone/sentiment (-1 to 1)                     │
│  - Aggressive vs. Balanced                                     │
│  - One-sided vs. Fair                                          │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────┐
│  STEP 9: SAVE TO MONGODB                                       │
├────────────────────────────────────────────────────────────────┤
│  Full analysis results → MongoDB                               │
│  {                                                             │
│    contract_id: "uuid",                                        │
│    analysis: {...},                                            │
│    clauses: [...],                                             │
│    full_text: "...",                                           │
│    recommendations: [...]                                      │
│  }                                                             │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────┐
│  STEP 10: UPDATE POSTGRESQL                                    │
├────────────────────────────────────────────────────────────────┤
│  Contract.objects.update(                                      │
│      status='completed',                                       │
│      risk_score=75,                                            │
│      compliance_score=85,                                      │
│      progress_percentage=100                                   │
│  )                                                             │
│  ContractAnalysis.objects.create(...)                          │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────┐
│  STEP 11: NOTIFICATIONS & ALERTS                               │
├────────────────────────────────────────────────────────────────┤
│  - Send email to uploader: "Analysis complete"                 │
│  - Check alert rules (high risk, expiring soon)                │
│  - Trigger webhooks (if configured)                            │
└────────────────────────────────────────────────────────────────┘
```

### Multi-Tenancy Flow

Every request follows this flow to ensure tenant isolation:

```
┌────────────────────────────────────────────────────────────────┐
│  1. API REQUEST                                                │
├────────────────────────────────────────────────────────────────┤
│  GET /api/v2/contracts/                                        │
│  Headers:                                                      │
│    Authorization: Bearer <jwt_token>                           │
│    X-Tenant-ID: 1                                              │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────┐
│  2. AUTHENTICATION MIDDLEWARE                                  │
├────────────────────────────────────────────────────────────────┤
│  - Validate JWT token                                          │
│  - Extract user from token                                     │
│  - request.user = User object                                  │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────┐
│  3. TENANT MIDDLEWARE                                          │
├────────────────────────────────────────────────────────────────┤
│  - Get X-Tenant-ID header                                      │
│  - Verify user belongs to tenant                               │
│  - request.tenant = Tenant object                              │
│  - Set thread-local tenant context                             │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────┐
│  4. VIEW PROCESSING                                            │
├────────────────────────────────────────────────────────────────┤
│  def get_queryset(self):                                       │
│      return Contract.objects.filter(                           │
│          tenant=self.request.user.tenant                       │
│      )                                                         │
│  # Automatically filtered by tenant!                           │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────┐
│  5. RESPONSE                                                   │
├────────────────────────────────────────────────────────────────┤
│  {                                                             │
│    "count": 15,                                                │
│    "results": [                                                │
│      // Only contracts from tenant 1                           │
│    ]                                                           │
│  }                                                             │
└────────────────────────────────────────────────────────────────┘
```

Continue in POSTMAN_TESTING.md...


