# ChainSight AI - Complete API Documentation

**Version**: 1.0  
**Base URL**: `http://localhost:8000/api/v1/`  
**Authentication**: JWT Bearer Token  
**Content-Type**: `application/json`

---

## 📑 Table of Contents

1. [Authentication & Multi-Tenancy](#authentication--multi-tenancy)
2. [User Management](#user-management)
3. [Tenant Management](#tenant-management)
4. [Contract Management](#contract-management)
5. [RAG Chat System](#rag-chat-system)
6. [Alerts & Notifications](#alerts--notifications)
7. [Integrations](#integrations)
8. [Counterparties](#counterparties)
9. [Dashboard & Analytics](#dashboard--analytics)
10. [Error Handling](#error-handling)
11. [Rate Limiting](#rate-limiting)
12. [Pagination & Filtering](#pagination--filtering)

---

## 🔐 Authentication & Multi-Tenancy

### Overview

ChainSight AI uses **JWT (JSON Web Tokens)** for authentication and implements **row-level multi-tenancy** with the `X-Tenant-ID` header.

### Authentication Flow

```
1. Register tenant/user
2. Login with email/password
3. Receive access_token and refresh_token
4. Include access_token in Authorization header
5. Include X-Tenant-ID header for all requests
```

### Obtain JWT Token

**Endpoint**: `POST /api/v1/auth/token/`

**Description**: Authenticate user and obtain JWT access and refresh tokens.

**Request Body**:
```json
{
  "email": "admin@acmecorp.com",
  "password": "SecurePassword123!"
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "admin@acmecorp.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "admin",
    "tenant": {
      "id": "tenant-uuid",
      "name": "Acme Corporation",
      "subdomain": "acmecorp",
      "plan_type": "enterprise"
    }
  }
}
```

**Validation Rules**:
- `email`: Required, valid email format
- `password`: Required, minimum 12 characters

**Error Responses**:
```json
// 401 Unauthorized - Invalid credentials
{
  "detail": "Invalid email or password"
}

// 403 Forbidden - Account inactive
{
  "detail": "User account is inactive"
}
```

---

### Refresh Token

**Endpoint**: `POST /api/v1/auth/token/refresh/`

**Description**: Obtain a new access token using refresh token.

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### Using Authentication

**All authenticated requests must include**:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
X-Tenant-ID: tenant-uuid
Content-Type: application/json
```

**Example cURL**:
```bash
curl -X GET http://localhost:8000/api/v1/contracts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-Tenant-ID: YOUR_TENANT_ID" \
  -H "Content-Type: application/json"
```

---

## 👥 User Management

### List Users

**Endpoint**: `GET /api/v1/users/`

**Description**: Get list of users in the tenant.

**Query Parameters**:
- `role` (string): Filter by role (admin, manager, user, viewer)
- `is_active` (boolean): Filter by active status
- `search` (string): Search by name or email
- `page` (integer): Page number (default: 1)
- `page_size` (integer): Items per page (default: 20)

**Response** (200 OK):
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/v1/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": "user-uuid-1",
      "email": "john.doe@acmecorp.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "admin",
      "is_active": true,
      "is_verified": true,
      "mfa_enabled": false,
      "last_login": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "user-uuid-2",
      "email": "jane.smith@acmecorp.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "role": "manager",
      "is_active": true,
      "is_verified": true,
      "mfa_enabled": true,
      "last_login": "2024-01-15T09:15:00Z",
      "created_at": "2024-01-02T00:00:00Z"
    }
  ]
}
```

---

### Create User

**Endpoint**: `POST /api/v1/users/`

**Description**: Create a new user in the tenant.

**Permissions**: Admin only

**Request Body**:
```json
{
  "email": "new.user@acmecorp.com",
  "password": "SecurePassword123!",
  "first_name": "New",
  "last_name": "User",
  "role": "user",
  "phone": "+1-555-0100"
}
```

**Validation Rules**:
- `email`: Required, unique within tenant, valid email format
- `password`: Required, minimum 12 characters, must include uppercase, lowercase, number, special char
- `first_name`: Optional, max 150 characters
- `last_name`: Optional, max 150 characters
- `role`: Required, one of: admin, manager, user, viewer
- `phone`: Optional, valid phone format

**Response** (201 Created):
```json
{
  "id": "user-uuid-3",
  "email": "new.user@acmecorp.com",
  "first_name": "New",
  "last_name": "User",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "mfa_enabled": false,
  "created_at": "2024-01-15T12:00:00Z"
}
```

**Error Responses**:
```json
// 400 Bad Request - Validation error
{
  "email": ["User with this email already exists"],
  "password": ["Password must be at least 12 characters"]
}

// 403 Forbidden - Insufficient permissions
{
  "detail": "You do not have permission to perform this action."
}
```

---

### Get User Details

**Endpoint**: `GET /api/v1/users/{user_id}/`

**Response** (200 OK):
```json
{
  "id": "user-uuid-1",
  "email": "john.doe@acmecorp.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1-555-0123",
  "role": "admin",
  "is_active": true,
  "is_verified": true,
  "mfa_enabled": false,
  "last_login": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-10T15:20:00Z"
}
```

---

### Update User

**Endpoint**: `PATCH /api/v1/users/{user_id}/`

**Permissions**: Admin or self (limited fields)

**Request Body**:
```json
{
  "first_name": "John",
  "last_name": "Doe Updated",
  "phone": "+1-555-0199",
  "role": "manager"
}
```

**Response** (200 OK):
```json
{
  "id": "user-uuid-1",
  "email": "john.doe@acmecorp.com",
  "first_name": "John",
  "last_name": "Doe Updated",
  "phone": "+1-555-0199",
  "role": "manager",
  "is_active": true,
  "updated_at": "2024-01-15T12:30:00Z"
}
```

---

### Delete User

**Endpoint**: `DELETE /api/v1/users/{user_id}/`

**Permissions**: Admin only

**Response** (204 No Content)

---

## 🏢 Tenant Management

### List Tenants

**Endpoint**: `GET /api/v1/tenants/`

**Description**: Get list of tenants (superuser sees all, regular users see their own).

**Response** (200 OK):
```json
{
  "count": 1,
  "results": [
    {
      "id": "tenant-uuid",
      "name": "Acme Corporation",
      "subdomain": "acmecorp",
      "plan_type": "enterprise",
      "status": "active",
      "is_active": true,
      "max_users": 1000,
      "max_contracts": 100000,
      "max_storage_gb": 1000,
      "billing_email": "billing@acmecorp.com",
      "settings": {
        "features": {
          "rag_chat": true,
          "ai_agents": true,
          "integrations": true
        },
        "branding": {
          "logo_url": "https://cdn.acmecorp.com/logo.png",
          "primary_color": "#1E40AF"
        }
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### Get Tenant Details

**Endpoint**: `GET /api/v1/tenants/{tenant_id}/`

**Response** (200 OK):
```json
{
  "id": "tenant-uuid",
  "name": "Acme Corporation",
  "subdomain": "acmecorp",
  "plan_type": "enterprise",
  "status": "active",
  "is_active": true,
  "max_users": 1000,
  "max_contracts": 100000,
  "max_storage_gb": 1000,
  "billing_email": "billing@acmecorp.com",
  "billing_info": {
    "payment_method": "card",
    "last_payment_date": "2024-01-01",
    "next_billing_date": "2024-02-01"
  },
  "settings": {
    "features": {
      "rag_chat": true,
      "ai_agents": true,
      "integrations": true,
      "advanced_analytics": true
    },
    "branding": {
      "logo_url": "https://cdn.acmecorp.com/logo.png",
      "primary_color": "#1E40AF",
      "secondary_color": "#3B82F6"
    },
    "notifications": {
      "email": true,
      "sms": true,
      "whatsapp": false
    }
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-10T00:00:00Z"
}
```

---

### Update Tenant

**Endpoint**: `PATCH /api/v1/tenants/{tenant_id}/`

**Permissions**: Admin only

**Request Body**:
```json
{
  "name": "Acme Corporation Inc.",
  "billing_email": "billing@acmecorp.com",
  "settings": {
    "features": {
      "rag_chat": true,
      "ai_agents": true
    },
    "branding": {
      "primary_color": "#2563EB"
    }
  }
}
```

**Response** (200 OK):
```json
{
  "id": "tenant-uuid",
  "name": "Acme Corporation Inc.",
  "subdomain": "acmecorp",
  "plan_type": "enterprise",
  "billing_email": "billing@acmecorp.com",
  "settings": {
    "features": {
      "rag_chat": true,
      "ai_agents": true
    },
    "branding": {
      "primary_color": "#2563EB"
    }
  },
  "updated_at": "2024-01-15T13:00:00Z"
}
```

---

## 📄 Contract Management

### List Contracts

**Endpoint**: `GET /api/v1/contracts/`

**Description**: Get list of contracts for the tenant.

**Query Parameters**:
- `status` (string): Filter by status (pending, processing, completed, failed)
- `contract_type` (string): Filter by contract type
- `risk_score_min` (integer): Minimum risk score (0-100)
- `risk_score_max` (integer): Maximum risk score (0-100)
- `search` (string): Search in filename
- `ordering` (string): Sort by field (created_at, risk_score, expiry_date)
- `is_archived` (boolean): Include archived contracts
- `page` (integer): Page number
- `page_size` (integer): Items per page

**Response** (200 OK):
```json
{
  "count": 523,
  "next": "http://localhost:8000/api/v1/contracts/?page=2",
  "previous": null,
  "results": [
    {
      "id": "contract-uuid-1",
      "original_filename": "Vendor_Agreement_2024.pdf",
      "file_type": "application/pdf",
      "file_size": 2458963,
      "status": "completed",
      "processing_stage": "analysis_complete",
      "progress_percentage": 100,
      "contract_type": "Vendor Agreement",
      "industry": "manufacturing",
      "language": "english",
      "contract_date": "2024-01-01",
      "effective_date": "2024-01-15",
      "expiry_date": "2025-01-15",
      "contract_value": "500000.00",
      "currency": "USD",
      "risk_score": 72,
      "compliance_score": 85,
      "sentiment_score": 0.65,
      "counterparties": [
        {
          "name": "Acme Suppliers Inc.",
          "type": "vendor",
          "role": "supplier"
        }
      ],
      "is_scanned_pdf": false,
      "is_archived": false,
      "uploaded_by": {
        "id": "user-uuid-1",
        "email": "john.doe@acmecorp.com",
        "full_name": "John Doe"
      },
      "analyzed_at": "2024-01-10T15:30:00Z",
      "processing_time": 45.3,
      "created_at": "2024-01-10T15:00:00Z",
      "updated_at": "2024-01-10T15:30:00Z"
    }
  ]
}
```

---

### Upload Contract

**Endpoint**: `POST /api/v1/contracts/`

**Description**: Upload a new contract for processing.

**Content-Type**: `multipart/form-data`

**Request Body** (Form Data):
```
file: (binary file data)
contract_type: "Vendor Agreement"
industry: "manufacturing"
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/v1/contracts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-Tenant-ID: YOUR_TENANT_ID" \
  -F "file=@/path/to/contract.pdf" \
  -F "contract_type=Vendor Agreement" \
  -F "industry=manufacturing"
```

**Response** (201 Created):
```json
{
  "id": "contract-uuid-2",
  "original_filename": "contract.pdf",
  "file_type": "application/pdf",
  "file_size": 1458963,
  "status": "pending",
  "processing_stage": "uploaded",
  "progress_percentage": 0,
  "contract_type": "Vendor Agreement",
  "industry": "manufacturing",
  "uploaded_by": {
    "id": "user-uuid-1",
    "email": "john.doe@acmecorp.com"
  },
  "created_at": "2024-01-15T14:00:00Z"
}
```

**Validation Rules**:
- `file`: Required, max size 50MB
- Allowed extensions: `.pdf`, `.docx`, `.txt`, `.jpg`, `.jpeg`, `.png`
- File content validation (not empty, valid format)

**Error Responses**:
```json
// 400 Bad Request - Invalid file
{
  "file": ["File type not allowed. Allowed types: pdf, docx, txt, jpg, jpeg, png"]
}

// 413 Payload Too Large
{
  "detail": "File size exceeds maximum allowed size of 50MB"
}
```

---

### Batch Upload Contracts

**Endpoint**: `POST /api/v1/contracts/batch_upload/`

**Description**: Upload multiple contracts at once.

**Content-Type**: `multipart/form-data`

**Request Body** (Form Data):
```
files[]: (binary file data 1)
files[]: (binary file data 2)
files[]: (binary file data 3)
industry: "manufacturing"
```

**Response** (201 Created):
```json
{
  "success": 3,
  "failed": 0,
  "contracts": [
    {
      "id": "contract-uuid-3",
      "original_filename": "contract1.pdf",
      "status": "pending"
    },
    {
      "id": "contract-uuid-4",
      "original_filename": "contract2.pdf",
      "status": "pending"
    },
    {
      "id": "contract-uuid-5",
      "original_filename": "contract3.pdf",
      "status": "pending"
    }
  ]
}
```

---

### Get Contract Details

**Endpoint**: `GET /api/v1/contracts/{contract_id}/`

**Description**: Get detailed information about a contract including analysis results.

**Response** (200 OK):
```json
{
  "id": "contract-uuid-1",
  "original_filename": "Vendor_Agreement_2024.pdf",
  "file_path": "s3://bucket/tenant-uuid/contracts/contract-uuid-1.pdf",
  "file_type": "application/pdf",
  "file_size": 2458963,
  "file_hash": "sha256:a3d5f8...",
  "status": "completed",
  "processing_stage": "analysis_complete",
  "progress_percentage": 100,
  "contract_type": "Vendor Agreement",
  "industry": "manufacturing",
  "language": "english",
  "contract_date": "2024-01-01",
  "effective_date": "2024-01-15",
  "expiry_date": "2025-01-15",
  "contract_value": "500000.00",
  "currency": "USD",
  "risk_score": 72,
  "compliance_score": 85,
  "sentiment_score": 0.65,
  "counterparties": [
    {
      "name": "Acme Suppliers Inc.",
      "type": "vendor",
      "role": "supplier",
      "contact": "procurement@acmesuppliers.com"
    }
  ],
  "is_scanned_pdf": false,
  "ocr_method_used": "",
  "folder_path": "/contracts/vendors/2024/",
  "is_archived": false,
  "uploaded_by": {
    "id": "user-uuid-1",
    "email": "john.doe@acmecorp.com",
    "full_name": "John Doe"
  },
  "analyzed_at": "2024-01-10T15:30:00Z",
  "processing_time": 45.3,
  "metadata": {
    "pages": 25,
    "word_count": 5432,
    "auto_renewal": true,
    "notice_period_days": 90
  },
  "tags": ["vendor", "manufacturing", "high-value"],
  "analysis": {
    "overall_risk_score": 72,
    "critical_issues_count": 2,
    "missing_clauses_count": 1,
    "priority_level": "high",
    "processing_time": 42.1,
    "model_used": "gpt-4-turbo",
    "issues": [
      {
        "type": "missing_clause",
        "severity": "high",
        "description": "Force Majeure clause is missing",
        "recommendation": "Add comprehensive Force Majeure clause"
      },
      {
        "type": "liability_cap",
        "severity": "critical",
        "description": "Liability cap is too low for contract value",
        "recommendation": "Increase liability cap to at least 2x contract value"
      }
    ]
  },
  "clauses": [
    {
      "id": "clause-uuid-1",
      "clause_number": "1.1",
      "clause_type": "payment",
      "title": "Payment Terms",
      "content": "Payment shall be made within 30 days...",
      "page_number": 3,
      "risk_level": "low",
      "quality_score": 85,
      "is_standard": true,
      "has_issues": false
    },
    {
      "id": "clause-uuid-2",
      "clause_number": "5.2",
      "clause_type": "liability",
      "title": "Limitation of Liability",
      "content": "In no event shall either party's liability...",
      "page_number": 12,
      "risk_level": "high",
      "quality_score": 55,
      "is_standard": false,
      "has_issues": true
    }
  ],
  "created_at": "2024-01-10T15:00:00Z",
  "updated_at": "2024-01-10T15:30:00Z"
}
```

---

### Analyze Contract

**Endpoint**: `POST /api/v1/contracts/{contract_id}/analyze/`

**Description**: Trigger AI analysis for a contract (if not already analyzed).

**Response** (200 OK):
```json
{
  "message": "Contract analysis started",
  "contract_id": "contract-uuid-1",
  "status": "processing",
  "task_id": "celery-task-uuid"
}
```

---

### Export Contract

**Endpoint**: `GET /api/v1/contracts/{contract_id}/export/`

**Description**: Export contract with analysis to PDF or DOCX.

**Query Parameters**:
- `format` (string): Export format (pdf, docx)
- `include_analysis` (boolean): Include analysis results (default: true)

**Response** (200 OK):
```json
{
  "download_url": "https://s3.amazonaws.com/bucket/exports/contract-uuid-1-export.pdf",
  "expires_at": "2024-01-15T18:00:00Z",
  "format": "pdf"
}
```

---

### Archive Contract

**Endpoint**: `POST /api/v1/contracts/{contract_id}/archive/`

**Description**: Archive a contract.

**Response** (200 OK):
```json
{
  "id": "contract-uuid-1",
  "is_archived": true,
  "archived_at": "2024-01-15T14:30:00Z"
}
```

---

### Restore Contract

**Endpoint**: `POST /api/v1/contracts/{contract_id}/restore/`

**Description**: Restore an archived contract.

**Response** (200 OK):
```json
{
  "id": "contract-uuid-1",
  "is_archived": false,
  "archived_at": null
}
```

---

### Delete Contract

**Endpoint**: `DELETE /api/v1/contracts/{contract_id}/`

**Permissions**: Admin or contract owner

**Response** (204 No Content)

---

## 💬 RAG Chat System

### List Chat Sessions

**Endpoint**: `GET /api/v1/chat/sessions/`

**Description**: Get list of chat sessions for the current user.

**Query Parameters**:
- `is_active` (boolean): Filter by active status
- `search` (string): Search in title
- `page` (integer): Page number

**Response** (200 OK):
```json
{
  "count": 15,
  "results": [
    {
      "id": "session-uuid-1",
      "title": "Questions about Vendor Agreement",
      "is_active": true,
      "last_message_at": "2024-01-15T14:30:00Z",
      "message_count": 12,
      "model_used": "gpt-4",
      "contracts": [
        {
          "id": "contract-uuid-1",
          "original_filename": "Vendor_Agreement_2024.pdf"
        }
      ],
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

---

### Create Chat Session

**Endpoint**: `POST /api/v1/chat/sessions/`

**Description**: Create a new chat session with optional contract context.

**Request Body**:
```json
{
  "title": "Questions about Vendor Agreement",
  "contracts": ["contract-uuid-1", "contract-uuid-2"],
  "model_used": "gpt-4"
}
```

**Response** (201 Created):
```json
{
  "id": "session-uuid-2",
  "title": "Questions about Vendor Agreement",
  "is_active": true,
  "last_message_at": "2024-01-15T15:00:00Z",
  "message_count": 0,
  "model_used": "gpt-4",
  "temperature": 0.7,
  "contracts": [
    {
      "id": "contract-uuid-1",
      "original_filename": "Vendor_Agreement_2024.pdf"
    }
  ],
  "created_at": "2024-01-15T15:00:00Z"
}
```

---

### Get Chat Session Details

**Endpoint**: `GET /api/v1/chat/sessions/{session_id}/`

**Response** (200 OK):
```json
{
  "id": "session-uuid-1",
  "title": "Questions about Vendor Agreement",
  "is_active": true,
  "last_message_at": "2024-01-15T14:30:00Z",
  "message_count": 12,
  "model_used": "gpt-4",
  "temperature": 0.7,
  "contracts": [
    {
      "id": "contract-uuid-1",
      "original_filename": "Vendor_Agreement_2024.pdf",
      "contract_type": "Vendor Agreement"
    }
  ],
  "messages": [
    {
      "id": "message-uuid-1",
      "role": "user",
      "content": "What are the payment terms in this contract?",
      "created_at": "2024-01-15T14:00:00Z"
    },
    {
      "id": "message-uuid-2",
      "role": "assistant",
      "content": "Based on clause 1.1, the payment terms are Net 30 days...",
      "sources": [
        {
          "contract_id": "contract-uuid-1",
          "clause_id": "clause-uuid-1",
          "clause_number": "1.1",
          "page_number": 3
        }
      ],
      "tokens_used": 234,
      "processing_time": 2.3,
      "created_at": "2024-01-15T14:00:05Z"
    }
  ],
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

### Send Chat Message

**Endpoint**: `POST /api/v1/chat/sessions/{session_id}/message/`

**Description**: Send a message in a chat session and get AI response with RAG.

**Request Body**:
```json
{
  "content": "What are the termination conditions in this contract?"
}
```

**Response** (200 OK):
```json
{
  "user_message": {
    "id": "message-uuid-3",
    "role": "user",
    "content": "What are the termination conditions in this contract?",
    "created_at": "2024-01-15T14:30:00Z"
  },
  "assistant_message": {
    "id": "message-uuid-4",
    "role": "assistant",
    "content": "The contract can be terminated under the following conditions:\n\n1. Either party may terminate with 90 days written notice (Clause 8.1)\n2. Immediate termination for material breach (Clause 8.2)\n3. Termination for insolvency (Clause 8.3)\n\nAdditionally, there's an automatic renewal clause unless either party provides notice 90 days before the anniversary date.",
    "sources": [
      {
        "contract_id": "contract-uuid-1",
        "contract_filename": "Vendor_Agreement_2024.pdf",
        "clause_id": "clause-uuid-15",
        "clause_number": "8.1",
        "clause_type": "termination",
        "page_number": 18,
        "relevance_score": 0.95
      },
      {
        "contract_id": "contract-uuid-1",
        "contract_filename": "Vendor_Agreement_2024.pdf",
        "clause_id": "clause-uuid-16",
        "clause_number": "8.2",
        "clause_type": "termination",
        "page_number": 18,
        "relevance_score": 0.89
      }
    ],
    "context_used": "Clause 8.1: Termination for Convenience...",
    "tokens_used": 456,
    "processing_time": 3.1,
    "created_at": "2024-01-15T14:30:05Z"
  }
}
```

---

### Provide Feedback on Message

**Endpoint**: `POST /api/v1/chat/messages/{message_id}/feedback/`

**Description**: Provide feedback on AI response quality.

**Request Body**:
```json
{
  "helpful": true,
  "feedback": "Very accurate response with good source citations"
}
```

**Response** (200 OK):
```json
{
  "id": "message-uuid-4",
  "helpful": true,
  "feedback": "Very accurate response with good source citations",
  "updated_at": "2024-01-15T14:35:00Z"
}
```

---

### Delete Chat Session

**Endpoint**: `DELETE /api/v1/chat/sessions/{session_id}/`

**Response** (204 No Content)

---

## 🔔 Alerts & Notifications

### List Alert Rules

**Endpoint**: `GET /api/v1/alerts/rules/`

**Description**: Get list of alert rules configured for the tenant.

**Query Parameters**:
- `alert_type` (string): Filter by type
- `is_active` (boolean): Filter by active status
- `severity` (string): Filter by severity

**Response** (200 OK):
```json
{
  "count": 8,
  "results": [
    {
      "id": "rule-uuid-1",
      "name": "High Risk Contract Alert",
      "description": "Alert when a contract has risk score above 80",
      "alert_type": "risk_threshold",
      "category": "risk_management",
      "conditions": {
        "field": "risk_score",
        "operator": "gt",
        "value": 80
      },
      "threshold_value": 80.0,
      "comparison_operator": "gt",
      "severity": "high",
      "priority": 8,
      "notify_email": true,
      "notify_sms": false,
      "notify_whatsapp": false,
      "notify_erp": true,
      "notify_webhook": false,
      "recipients": [
        "legal@acmecorp.com",
        "compliance@acmecorp.com"
      ],
      "is_active": true,
      "check_frequency": "realtime",
      "cooldown_period": 3600,
      "max_alerts_per_day": 10,
      "created_by": {
        "id": "user-uuid-1",
        "email": "admin@acmecorp.com"
      },
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "rule-uuid-2",
      "name": "Contract Expiry Warning",
      "description": "Alert 90 days before contract expiry",
      "alert_type": "expiry",
      "severity": "medium",
      "notify_email": true,
      "notify_sms": true,
      "is_active": true,
      "check_frequency": "daily",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### Create Alert Rule

**Endpoint**: `POST /api/v1/alerts/rules/`

**Description**: Create a new alert rule.

**Permissions**: Admin or Manager

**Request Body**:
```json
{
  "name": "Critical Compliance Issue Alert",
  "description": "Alert for compliance scores below 50",
  "alert_type": "compliance",
  "category": "compliance",
  "conditions": {
    "field": "compliance_score",
    "operator": "lt",
    "value": 50
  },
  "threshold_value": 50.0,
  "comparison_operator": "lt",
  "severity": "critical",
  "priority": 10,
  "notify_email": true,
  "notify_sms": true,
  "notify_whatsapp": false,
  "notify_erp": true,
  "notify_webhook": false,
  "recipients": [
    "compliance@acmecorp.com",
    "legal@acmecorp.com"
  ],
  "is_active": true,
  "check_frequency": "realtime",
  "cooldown_period": 1800,
  "max_alerts_per_day": 20
}
```

**Response** (201 Created):
```json
{
  "id": "rule-uuid-3",
  "name": "Critical Compliance Issue Alert",
  "description": "Alert for compliance scores below 50",
  "alert_type": "compliance",
  "severity": "critical",
  "is_active": true,
  "created_at": "2024-01-15T15:00:00Z"
}
```

---

### Get Alert Rule Details

**Endpoint**: `GET /api/v1/alerts/rules/{rule_id}/`

**Response** (200 OK):
```json
{
  "id": "rule-uuid-1",
  "name": "High Risk Contract Alert",
  "description": "Alert when a contract has risk score above 80",
  "alert_type": "risk_threshold",
  "category": "risk_management",
  "conditions": {
    "field": "risk_score",
    "operator": "gt",
    "value": 80
  },
  "severity": "high",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Update Alert Rule

**Endpoint**: `PATCH /api/v1/alerts/rules/{rule_id}/`

**Request Body**:
```json
{
  "is_active": false,
  "severity": "critical"
}
```

**Response** (200 OK):
```json
{
  "id": "rule-uuid-1",
  "name": "High Risk Contract Alert",
  "is_active": false,
  "severity": "critical",
  "updated_at": "2024-01-15T15:30:00Z"
}
```

---

### Delete Alert Rule

**Endpoint**: `DELETE /api/v1/alerts/rules/{rule_id}/`

**Response** (204 No Content)

---

### List Alerts

**Endpoint**: `GET /api/v1/alerts/`

**Description**: Get list of triggered alerts.

**Query Parameters**:
- `status` (string): Filter by status (active, acknowledged, resolved, dismissed)
- `severity` (string): Filter by severity (low, medium, high, critical)
- `alert_type` (string): Filter by type
- `contract` (uuid): Filter by contract
- `start_date` (date): Filter by date range start
- `end_date` (date): Filter by date range end

**Response** (200 OK):
```json
{
  "count": 42,
  "results": [
    {
      "id": "alert-uuid-1",
      "alert_rule": {
        "id": "rule-uuid-1",
        "name": "High Risk Contract Alert"
      },
      "alert_type": "risk_threshold",
      "severity": "high",
      "title": "High Risk Score Detected",
      "message": "Contract 'Vendor_Agreement_2024.pdf' has a risk score of 87, exceeding the threshold of 80",
      "contract": {
        "id": "contract-uuid-1",
        "original_filename": "Vendor_Agreement_2024.pdf"
      },
      "trigger_data": {
        "risk_score": 87,
        "threshold": 80,
        "critical_issues": 3
      },
      "context": {
        "issues": [
          "Missing Force Majeure clause",
          "Low liability cap",
          "Unclear termination conditions"
        ]
      },
      "status": "active",
      "email_sent": true,
      "sms_sent": false,
      "whatsapp_sent": false,
      "erp_sent": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### Get Alert Details

**Endpoint**: `GET /api/v1/alerts/{alert_id}/`

**Response** (200 OK):
```json
{
  "id": "alert-uuid-1",
  "alert_rule": {
    "id": "rule-uuid-1",
    "name": "High Risk Contract Alert",
    "description": "Alert when a contract has risk score above 80"
  },
  "alert_type": "risk_threshold",
  "severity": "high",
  "title": "High Risk Score Detected",
  "message": "Contract 'Vendor_Agreement_2024.pdf' has a risk score of 87, exceeding the threshold of 80",
  "contract": {
    "id": "contract-uuid-1",
    "original_filename": "Vendor_Agreement_2024.pdf",
    "contract_type": "Vendor Agreement"
  },
  "supplier": null,
  "trigger_data": {
    "risk_score": 87,
    "threshold": 80,
    "critical_issues": 3
  },
  "context": {
    "issues": [
      "Missing Force Majeure clause",
      "Low liability cap",
      "Unclear termination conditions"
    ],
    "recommendations": [
      "Add comprehensive Force Majeure clause",
      "Increase liability cap to match contract value",
      "Clarify termination notice periods"
    ]
  },
  "status": "active",
  "acknowledged_by": null,
  "acknowledged_at": null,
  "resolved_by": null,
  "resolved_at": null,
  "email_sent": true,
  "sms_sent": false,
  "whatsapp_sent": false,
  "erp_sent": true,
  "webhook_sent": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### Acknowledge Alert

**Endpoint**: `POST /api/v1/alerts/{alert_id}/acknowledge/`

**Description**: Mark alert as acknowledged.

**Response** (200 OK):
```json
{
  "id": "alert-uuid-1",
  "status": "acknowledged",
  "acknowledged_by": {
    "id": "user-uuid-1",
    "email": "john.doe@acmecorp.com"
  },
  "acknowledged_at": "2024-01-15T11:00:00Z"
}
```

---

### Resolve Alert

**Endpoint**: `POST /api/v1/alerts/{alert_id}/resolve/`

**Description**: Mark alert as resolved.

**Request Body** (Optional):
```json
{
  "resolution_notes": "Updated contract with Force Majeure clause and increased liability cap"
}
```

**Response** (200 OK):
```json
{
  "id": "alert-uuid-1",
  "status": "resolved",
  "resolved_by": {
    "id": "user-uuid-1",
    "email": "john.doe@acmecorp.com"
  },
  "resolved_at": "2024-01-15T15:00:00Z"
}
```

---

### Dismiss Alert

**Endpoint**: `POST /api/v1/alerts/{alert_id}/dismiss/`

**Description**: Dismiss alert (not actionable).

**Response** (200 OK):
```json
{
  "id": "alert-uuid-1",
  "status": "dismissed",
  "updated_at": "2024-01-15T11:30:00Z"
}
```

---

## 🔗 Integrations

### List Integrations

**Endpoint**: `GET /api/v1/integrations/`

**Description**: Get list of configured integrations.

**Response** (200 OK):
```json
{
  "count": 5,
  "results": [
    {
      "id": "integration-uuid-1",
      "name": "Microsoft Word Online",
      "integration_type": "microsoft_word",
      "is_active": true,
      "is_connected": true,
      "last_sync_at": "2024-01-15T10:00:00Z",
      "auto_sync": true,
      "sync_interval": "hourly",
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "integration-uuid-2",
      "name": "SAP ERP Production",
      "integration_type": "sap",
      "is_active": true,
      "is_connected": true,
      "last_sync_at": "2024-01-15T09:00:00Z",
      "auto_sync": true,
      "sync_interval": "daily",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### Create Integration

**Endpoint**: `POST /api/v1/integrations/`

**Description**: Configure a new integration.

**Request Body** (Microsoft Word Example):
```json
{
  "name": "Microsoft Word Online",
  "integration_type": "microsoft_word",
  "config": {
    "tenant_id": "microsoft-tenant-id",
    "client_id": "microsoft-client-id"
  },
  "auto_sync": true,
  "sync_interval": "hourly"
}
```

**Response** (201 Created):
```json
{
  "id": "integration-uuid-3",
  "name": "Microsoft Word Online",
  "integration_type": "microsoft_word",
  "is_active": true,
  "is_connected": false,
  "authorization_url": "https://login.microsoftonline.com/oauth2/v2.0/authorize?client_id=...",
  "created_at": "2024-01-15T16:00:00Z"
}
```

---

### Connect Integration (OAuth Callback)

**Endpoint**: `POST /api/v1/integrations/{integration_id}/connect/`

**Description**: Complete OAuth connection for integration.

**Request Body**:
```json
{
  "code": "oauth-authorization-code",
  "state": "oauth-state-parameter"
}
```

**Response** (200 OK):
```json
{
  "id": "integration-uuid-3",
  "name": "Microsoft Word Online",
  "integration_type": "microsoft_word",
  "is_active": true,
  "is_connected": true,
  "last_sync_at": null,
  "updated_at": "2024-01-15T16:05:00Z"
}
```

---

### Sync Integration

**Endpoint**: `POST /api/v1/integrations/{integration_id}/sync/`

**Description**: Manually trigger integration sync.

**Response** (200 OK):
```json
{
  "message": "Sync initiated",
  "integration_id": "integration-uuid-1",
  "task_id": "celery-task-uuid"
}
```

---

### Export to Word

**Endpoint**: `POST /api/v1/integrations/word/export/`

**Description**: Export contract to Microsoft Word Online.

**Request Body**:
```json
{
  "contract_id": "contract-uuid-1",
  "include_analysis": true,
  "folder_path": "/Contracts/Vendors/"
}
```

**Response** (200 OK):
```json
{
  "document_id": "microsoft-doc-id",
  "document_url": "https://onedrive.live.com/edit.aspx?id=...",
  "sync_id": "sync-uuid-1"
}
```

---

### Export to Google Docs

**Endpoint**: `POST /api/v1/integrations/google/export/`

**Description**: Export contract to Google Docs.

**Request Body**:
```json
{
  "contract_id": "contract-uuid-1",
  "include_analysis": true,
  "folder_id": "google-drive-folder-id"
}
```

**Response** (200 OK):
```json
{
  "document_id": "google-doc-id",
  "document_url": "https://docs.google.com/document/d/.../edit",
  "sync_id": "sync-uuid-2"
}
```

---

### Push to ERP

**Endpoint**: `POST /api/v1/integrations/erp/push/`

**Description**: Push contract data to ERP system.

**Request Body**:
```json
{
  "contract_id": "contract-uuid-1",
  "entity_type": "contract",
  "mapping": {
    "vendor_code": "V12345",
    "cost_center": "CC-1000",
    "purchase_order": "PO-2024-001"
  }
}
```

**Response** (200 OK):
```json
{
  "erp_entity_id": "erp-entity-uuid-1",
  "external_id": "ERP-CONTRACT-12345",
  "sync_status": "synced",
  "synced_at": "2024-01-15T16:30:00Z"
}
```

---

## 🏪 Counterparties

### List Counterparties

**Endpoint**: `GET /api/v1/counterparties/`

**Description**: Get list of counterparties (vendors, suppliers, customers).

**Query Parameters**:
- `search` (string): Search by name
- `risk_level` (string): Filter by risk level
- `is_verified` (boolean): Filter by verification status

**Response** (200 OK):
```json
{
  "count": 127,
  "results": [
    {
      "id": "counterparty-uuid-1",
      "name": "Acme Suppliers Inc.",
      "legal_name": "Acme Suppliers Incorporated",
      "registration_number": "REG-12345",
      "tax_id": "TAX-67890",
      "contact_email": "procurement@acmesuppliers.com",
      "contact_phone": "+1-555-0200",
      "address": {
        "street": "123 Industrial Blvd",
        "city": "Manufacturing City",
        "state": "CA",
        "postal_code": "90210",
        "country": "USA"
      },
      "risk_level": "medium",
      "credit_rating": "BBB",
      "is_verified": true,
      "verification_date": "2024-01-01",
      "is_blacklisted": false,
      "contract_count": 15,
      "total_contract_value": "7500000.00",
      "created_at": "2023-06-15T00:00:00Z"
    }
  ]
}
```

---

### Create Counterparty

**Endpoint**: `POST /api/v1/counterparties/`

**Request Body**:
```json
{
  "name": "New Vendor Inc.",
  "legal_name": "New Vendor Incorporated",
  "registration_number": "REG-54321",
  "tax_id": "TAX-09876",
  "contact_email": "contact@newvendor.com",
  "contact_phone": "+1-555-0300",
  "address": {
    "street": "456 Commerce Ave",
    "city": "Business City",
    "state": "NY",
    "postal_code": "10001",
    "country": "USA"
  }
}
```

**Response** (201 Created):
```json
{
  "id": "counterparty-uuid-2",
  "name": "New Vendor Inc.",
  "legal_name": "New Vendor Incorporated",
  "is_verified": false,
  "created_at": "2024-01-15T17:00:00Z"
}
```

---

### Get Counterparty Details

**Endpoint**: `GET /api/v1/counterparties/{counterparty_id}/`

**Response** (200 OK):
```json
{
  "id": "counterparty-uuid-1",
  "name": "Acme Suppliers Inc.",
  "legal_name": "Acme Suppliers Incorporated",
  "registration_number": "REG-12345",
  "tax_id": "TAX-67890",
  "contact_email": "procurement@acmesuppliers.com",
  "contact_phone": "+1-555-0200",
  "website": "https://www.acmesuppliers.com",
  "address": {
    "street": "123 Industrial Blvd",
    "city": "Manufacturing City",
    "state": "CA",
    "postal_code": "90210",
    "country": "USA"
  },
  "risk_level": "medium",
  "credit_rating": "BBB",
  "is_verified": true,
  "verification_date": "2024-01-01",
  "is_blacklisted": false,
  "blacklist_reason": null,
  "contract_count": 15,
  "total_contract_value": "7500000.00",
  "active_contracts": 8,
  "contracts": [
    {
      "id": "contract-uuid-1",
      "original_filename": "Vendor_Agreement_2024.pdf",
      "contract_type": "Vendor Agreement",
      "contract_value": "500000.00",
      "effective_date": "2024-01-15",
      "expiry_date": "2025-01-15"
    }
  ],
  "metadata": {
    "industry": "Manufacturing",
    "employee_count": 500,
    "annual_revenue": "50000000.00"
  },
  "created_at": "2023-06-15T00:00:00Z",
  "updated_at": "2024-01-10T00:00:00Z"
}
```

---

## 📊 Dashboard & Analytics

### Get Dashboard Overview

**Endpoint**: `GET /api/v1/dashboard/overview/`

**Description**: Get dashboard overview with key metrics.

**Response** (200 OK):
```json
{
  "tenant": {
    "id": "tenant-uuid",
    "name": "Acme Corporation",
    "plan_type": "enterprise"
  },
  "summary": {
    "total_contracts": 523,
    "active_contracts": 412,
    "archived_contracts": 111,
    "pending_analysis": 8,
    "total_contract_value": "125000000.00",
    "average_risk_score": 58.5,
    "high_risk_contracts": 45,
    "expiring_soon": 12
  },
  "risk_distribution": {
    "critical": 8,
    "high": 37,
    "medium": 198,
    "low": 280
  },
  "contract_types": {
    "Vendor Agreement": 180,
    "Service Agreement": 145,
    "NDA": 98,
    "Employment Contract": 75,
    "Other": 25
  },
  "recent_activity": {
    "uploads_today": 15,
    "analyses_today": 12,
    "alerts_today": 3,
    "chat_sessions_today": 28
  },
  "compliance": {
    "average_compliance_score": 82.3,
    "compliant_contracts": 456,
    "non_compliant_contracts": 67
  },
  "alerts": {
    "active_alerts": 12,
    "critical_alerts": 2,
    "pending_acknowledgment": 7
  },
  "generated_at": "2024-01-15T18:00:00Z"
}
```

---

### Get Contract Analytics

**Endpoint**: `GET /api/v1/dashboard/analytics/contracts/`

**Description**: Get detailed contract analytics and trends.

**Query Parameters**:
- `start_date` (date): Analytics period start
- `end_date` (date): Analytics period end
- `group_by` (string): Group by period (day, week, month)

**Response** (200 OK):
```json
{
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-15",
    "group_by": "day"
  },
  "upload_trends": [
    {
      "date": "2024-01-15",
      "uploads": 15,
      "successful": 14,
      "failed": 1
    }
  ],
  "analysis_trends": [
    {
      "date": "2024-01-15",
      "analyzed": 12,
      "average_processing_time": 45.3,
      "average_risk_score": 61.2
    }
  ],
  "value_trends": [
    {
      "date": "2024-01-15",
      "total_value": "2500000.00",
      "contract_count": 15
    }
  ],
  "risk_trends": [
    {
      "date": "2024-01-15",
      "critical": 1,
      "high": 3,
      "medium": 7,
      "low": 4
    }
  ],
  "top_counterparties": [
    {
      "id": "counterparty-uuid-1",
      "name": "Acme Suppliers Inc.",
      "contract_count": 15,
      "total_value": "7500000.00"
    }
  ],
  "generated_at": "2024-01-15T18:00:00Z"
}
```

---

### Get Risk Report

**Endpoint**: `GET /api/v1/dashboard/reports/risk/`

**Description**: Generate comprehensive risk assessment report.

**Query Parameters**:
- `format` (string): Report format (json, pdf, excel)
- `include_details` (boolean): Include detailed contract information

**Response** (200 OK):
```json
{
  "report_id": "report-uuid-1",
  "report_type": "risk_assessment",
  "generated_at": "2024-01-15T18:00:00Z",
  "generated_by": {
    "id": "user-uuid-1",
    "email": "admin@acmecorp.com"
  },
  "summary": {
    "total_contracts_analyzed": 523,
    "average_risk_score": 58.5,
    "high_risk_contracts": 45,
    "critical_issues": 67,
    "recommendations": 234
  },
  "risk_breakdown": {
    "critical": {
      "count": 8,
      "percentage": 1.5,
      "total_value": "5000000.00",
      "contracts": [
        {
          "id": "contract-uuid-10",
          "filename": "High_Risk_Contract.pdf",
          "risk_score": 95,
          "critical_issues": 5
        }
      ]
    },
    "high": {
      "count": 37,
      "percentage": 7.1,
      "total_value": "28000000.00"
    },
    "medium": {
      "count": 198,
      "percentage": 37.9,
      "total_value": "62000000.00"
    },
    "low": {
      "count": 280,
      "percentage": 53.5,
      "total_value": "30000000.00"
    }
  },
  "common_issues": [
    {
      "issue_type": "missing_clause",
      "count": 45,
      "severity": "high",
      "description": "Force Majeure clause missing"
    },
    {
      "issue_type": "liability_cap",
      "count": 32,
      "severity": "critical",
      "description": "Liability cap too low for contract value"
    }
  ],
  "recommendations": [
    {
      "priority": "high",
      "description": "Review and update all contracts missing Force Majeure clauses",
      "affected_contracts": 45
    }
  ],
  "download_url": "https://s3.amazonaws.com/bucket/reports/risk-report-uuid-1.pdf",
  "expires_at": "2024-01-16T18:00:00Z"
}
```

---

## ⚠️ Error Handling

### Error Response Format

All errors follow a consistent JSON structure:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "details": {
    "field": ["Specific error details"]
  },
  "timestamp": "2024-01-15T18:00:00Z",
  "request_id": "req-uuid-12345"
}
```

### HTTP Status Codes

| Code | Description | When Used |
|------|-------------|-----------|
| **200** | OK | Successful GET, PATCH requests |
| **201** | Created | Successful POST (resource created) |
| **204** | No Content | Successful DELETE |
| **400** | Bad Request | Validation errors, malformed request |
| **401** | Unauthorized | Missing or invalid authentication token |
| **403** | Forbidden | Insufficient permissions |
| **404** | Not Found | Resource doesn't exist |
| **409** | Conflict | Resource already exists |
| **413** | Payload Too Large | File size exceeds limit |
| **422** | Unprocessable Entity | Business logic validation failed |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Server Error | Server-side error |
| **503** | Service Unavailable | Maintenance or overload |

### Common Error Examples

**401 Unauthorized** - Missing token:
```json
{
  "error": "AuthenticationFailed",
  "message": "Authentication credentials were not provided",
  "details": {},
  "timestamp": "2024-01-15T18:00:00Z"
}
```

**401 Unauthorized** - Invalid token:
```json
{
  "error": "InvalidToken",
  "message": "Token is invalid or expired",
  "details": {
    "token_type": "access_token",
    "expired_at": "2024-01-15T17:00:00Z"
  },
  "timestamp": "2024-01-15T18:00:00Z"
}
```

**403 Forbidden** - Insufficient permissions:
```json
{
  "error": "PermissionDenied",
  "message": "You do not have permission to perform this action",
  "details": {
    "required_role": "admin",
    "user_role": "user"
  },
  "timestamp": "2024-01-15T18:00:00Z"
}
```

**404 Not Found**:
```json
{
  "error": "NotFound",
  "message": "Contract not found",
  "details": {
    "contract_id": "non-existent-uuid"
  },
  "timestamp": "2024-01-15T18:00:00Z"
}
```

**400 Bad Request** - Validation errors:
```json
{
  "error": "ValidationError",
  "message": "Invalid request data",
  "details": {
    "email": ["Enter a valid email address"],
    "password": ["Password must be at least 12 characters"],
    "role": ["Invalid choice. Choose from: admin, manager, user, viewer"]
  },
  "timestamp": "2024-01-15T18:00:00Z"
}
```

**429 Too Many Requests** - Rate limit exceeded:
```json
{
  "error": "RateLimitExceeded",
  "message": "Rate limit exceeded",
  "details": {
    "limit": 1000,
    "period": "hour",
    "retry_after": 1800
  },
  "timestamp": "2024-01-15T18:00:00Z",
  "retry_after": "2024-01-15T18:30:00Z"
}
```

---

## ⚡ Rate Limiting

### Rate Limits by Plan

| Plan | API Requests/Hour | Contracts/Day | Concurrent Uploads |
|------|-------------------|---------------|-------------------|
| **Free** | 100 | 10 | 2 |
| **Starter** | 500 | 100 | 5 |
| **Professional** | 2,000 | 500 | 10 |
| **Enterprise** | Unlimited | Unlimited | 50 |

### Rate Limit Headers

Every API response includes rate limit information:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 856
X-RateLimit-Reset: 2024-01-15T19:00:00Z
```

### Handling Rate Limits

When rate limit is exceeded (429 status):
1. Check `X-RateLimit-Reset` header for reset time
2. Implement exponential backoff
3. Consider upgrading plan if consistently hitting limits

---

## 📄 Pagination & Filtering

### Pagination

All list endpoints support pagination with consistent parameters:

**Query Parameters**:
- `page` (integer): Page number (default: 1)
- `page_size` (integer): Items per page (default: 20, max: 100)

**Response Format**:
```json
{
  "count": 523,
  "next": "http://localhost:8000/api/v1/contracts/?page=2",
  "previous": null,
  "results": [...]
}
```

### Filtering

Most list endpoints support filtering:

**Common Filters**:
- `search` (string): Full-text search
- `ordering` (string): Sort by field (prefix with `-` for descending)
- Date ranges: `created_after`, `created_before`
- Status filters: Vary by endpoint

**Example**:
```
GET /api/v1/contracts/?search=vendor&ordering=-risk_score&page=1&page_size=50
```

### Ordering

Sort results using `ordering` parameter:

```
GET /api/v1/contracts/?ordering=-created_at
GET /api/v1/contracts/?ordering=risk_score
GET /api/v1/contracts/?ordering=-expiry_date,risk_score
```

---

## 🚀 Quick Start Example

### Complete Authentication & First Contract Flow

```bash
# 1. Obtain JWT token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@acmecorp.com",
    "password": "SecurePassword123!"
  }'

# Response: Save access token and tenant ID

# 2. Upload contract
curl -X POST http://localhost:8000/api/v1/contracts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-Tenant-ID: YOUR_TENANT_ID" \
  -F "file=@contract.pdf" \
  -F "contract_type=Vendor Agreement"

# 3. Check contract status
curl -X GET http://localhost:8000/api/v1/contracts/CONTRACT_ID/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-Tenant-ID: YOUR_TENANT_ID"

# 4. Start RAG chat session
curl -X POST http://localhost:8000/api/v1/chat/sessions/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-Tenant-ID: YOUR_TENANT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Questions about contract",
    "contracts": ["CONTRACT_ID"]
  }'

# 5. Ask question
curl -X POST http://localhost:8000/api/v1/chat/sessions/SESSION_ID/message/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-Tenant-ID: YOUR_TENANT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "What are the payment terms?"
  }'
```

---

## 📚 Additional Resources

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/docs/redoc/
- **Health Check**: http://localhost:8000/api/health/
- **GitHub Repository**: [Your Repository URL]
- **Support Email**: support@chainsight.ai

---

**Last Updated**: January 2024  
**API Version**: 1.0  
**Documentation Version**: 1.0

