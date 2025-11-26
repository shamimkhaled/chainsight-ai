# ChainSight AI - Postman Testing Guide & API Documentation

## 📋 Table of Contents

1. [Setup Postman Environment](#setup-postman-environment)
2. [Authentication APIs](#authentication-apis)
3. [Contract Management APIs](#contract-management-apis)
4. [User Management APIs](#user-management-apis)
5. [Testing Workflows](#testing-workflows)
6. [Error Handling](#error-handling)

---

## 1. Setup Postman Environment

### Create Environment Variables

In Postman, create a new environment with these variables:

```json
{
  "base_url": "http://127.0.0.1:8000",
  "tenant_id": "1",
  "access_token": "",
  "refresh_token": "",
  "contract_id": ""
}
```

### How to Set Variables

1. Click the "Environments" tab in Postman
2. Click "Create Environment"
3. Add each variable with initial values
4. Select the environment before testing

---

## 2. Authentication APIs

### 2.1 Register New User

**Endpoint**: `POST {{base_url}}/api/v2/accounts/users/register/`

**Headers**:
```json
{
  "Content-Type": "application/json",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Request Body**:
```json
{
  "email": "john.doe@demo.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user"
}
```

**Response (201 Created)**:
```json
{
  "user": {
    "id": "f7e3c2a1-4b5d-4e6f-8a9b-0c1d2e3f4g5h",
    "email": "john.doe@demo.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "is_active": true,
    "is_verified": false,
    "full_name": "John Doe",
    "created_at": "2025-11-20T10:30:00Z",
    "updated_at": "2025-11-20T10:30:00Z"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYzNzc2...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjM3Njc..."
  }
}
```

**Postman Test Script** (Auto-save tokens):
```javascript
// Save tokens to environment
if (pm.response.code === 201) {
    var jsonData = pm.response.json();
    pm.environment.set("access_token", jsonData.tokens.access);
    pm.environment.set("refresh_token", jsonData.tokens.refresh);
    console.log("Access token saved:", jsonData.tokens.access);
}
```

**Error Responses**:

```json
// 400 - Password mismatch
{
  "password_confirm": ["Passwords do not match."]
}

// 400 - User already exists
{
  "email": ["User with this email already exists."]
}
```

---

### 2.2 Login User

**Endpoint**: `POST {{base_url}}/api/v2/accounts/users/login/`

**Headers**:
```json
{
  "Content-Type": "application/json",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Request Body**:
```json
{
  "email": "john.doe@demo.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK)**:
```json
{
  "user": {
    "id": "f7e3c2a1-4b5d-4e6f-8a9b-0c1d2e3f4g5h",
    "email": "john.doe@demo.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "is_active": true,
    "is_verified": false,
    "full_name": "John Doe"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

**Postman Test Script**:
```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("access_token", jsonData.tokens.access);
    pm.environment.set("refresh_token", jsonData.tokens.refresh);
    console.log("Login successful!");
}
```

**Error Responses**:
```json
// 401 - Invalid credentials
{
  "detail": "Invalid email or password."
}

// 403 - Account inactive
{
  "detail": "User account is disabled."
}
```

---

### 2.3 Get Current User Profile

**Endpoint**: `GET {{base_url}}/api/v2/accounts/users/me/`

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Response (200 OK)**:
```json
{
  "id": "f7e3c2a1-4b5d-4e6f-8a9b-0c1d2e3f4g5h",
  "email": "john.doe@demo.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "full_name": "John Doe",
  "created_at": "2025-11-20T10:30:00Z",
  "updated_at": "2025-11-20T10:30:00Z"
}
```

---

### 2.4 Refresh Access Token

**Endpoint**: `POST {{base_url}}/api/v2/auth/token/refresh/`

**Headers**:
```json
{
  "Content-Type": "application/json"
}
```

**Request Body**:
```json
{
  "refresh": "{{refresh_token}}"
}
```

**Response (200 OK)**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Postman Test Script**:
```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("access_token", jsonData.access);
}
```

---

### 2.5 Change Password

**Endpoint**: `POST {{base_url}}/api/v2/accounts/users/change_password/`

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Request Body**:
```json
{
  "old_password": "SecurePass123!",
  "new_password": "NewSecurePass456!",
  "new_password_confirm": "NewSecurePass456!"
}
```

**Response (200 OK)**:
```json
{
  "message": "Password changed successfully"
}
```

---

## 3. Contract Management APIs

### 3.1 Upload Contract

**Endpoint**: `POST {{base_url}}/api/v2/contracts/upload/`

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Request Body** (multipart/form-data):
```
file: [Select your PDF/DOCX file]
industry: "technology"
language: "english"
contract_type: "service_agreement" (optional)
contract_date: "2024-01-01" (optional)
expiry_date: "2025-01-01" (optional)
tags: ["nda", "confidential"] (optional, JSON array)
```

**How to Set Up in Postman**:
1. Select "Body" tab
2. Choose "form-data"
3. Add key "file" → Select "File" type → Choose your PDF
4. Add other keys as "Text" type

**Response (201 Created)**:
```json
{
  "contract_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  "message": "Contract uploaded successfully. Analysis in progress."
}
```

**Postman Test Script**:
```javascript
if (pm.response.code === 201) {
    var jsonData = pm.response.json();
    pm.environment.set("contract_id", jsonData.contract_id);
    console.log("Contract ID saved:", jsonData.contract_id);
}
```

**Error Responses**:
```json
// 400 - Invalid file type
{
  "file": ["File type not supported. Allowed: .pdf, .docx, .txt"]
}

// 400 - File too large
{
  "file": ["File size exceeds maximum allowed size of 50MB"]
}

// 429 - Rate limit exceeded
{
  "detail": "Contract upload limit exceeded for your plan"
}
```

---

### 3.2 List Contracts

**Endpoint**: `GET {{base_url}}/api/v2/contracts/`

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Query Parameters**:
```
?page=1                          # Pagination
&page_size=20                    # Items per page
&status=completed                # Filter by status
&industry=technology             # Filter by industry
&risk_score__gte=50              # Risk score >= 50
&search=agreement                # Search in filename/type
&ordering=-created_at            # Order by created_at descending
```

**Example Full URL**:
```
{{base_url}}/api/v2/contracts/?status=completed&ordering=-risk_score&page=1&page_size=10
```

**Response (200 OK)**:
```json
{
  "count": 25,
  "next": "http://127.0.0.1:8000/api/v2/contracts/?page=2",
  "previous": null,
  "results": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "original_filename": "service_agreement.pdf",
      "file_size": 1024000,
      "file_type": "application/pdf",
      "status": "completed",
      "progress_percentage": 100,
      "industry": "technology",
      "language": "english",
      "contract_type": "service_agreement",
      "risk_score": 75,
      "compliance_score": 85,
      "sentiment_score": 0.2,
      "contract_date": "2024-01-01",
      "expiry_date": "2025-01-01",
      "contract_value": null,
      "currency": null,
      "is_archived": false,
      "uploaded_by_name": "John Doe",
      "created_at": "2025-11-20T10:35:00Z",
      "analyzed_at": "2025-11-20T10:40:00Z"
    }
  ]
}
```

---

### 3.3 Get Contract Details

**Endpoint**: `GET {{base_url}}/api/v2/contracts/{{contract_id}}/`

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Response (200 OK)**:
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "original_filename": "service_agreement.pdf",
  "file_size": 1024000,
  "file_type": "application/pdf",
  "file_hash": "abc123def456...",
  "status": "completed",
  "processing_stage": "analysis_complete",
  "progress_percentage": 100,
  "error_message": null,
  "contract_type": "service_agreement",
  "industry": "technology",
  "language": "english",
  "contract_date": "2024-01-01",
  "effective_date": null,
  "expiry_date": "2025-01-01",
  "contract_value": "50000.00",
  "currency": "USD",
  "counterparties": [
    {
      "name": "ABC Corporation",
      "type": "vendor"
    }
  ],
  "risk_score": 75,
  "compliance_score": 85,
  "sentiment_score": 0.2,
  "is_scanned_pdf": false,
  "ocr_method_used": null,
  "folder_path": "tenant_1/contracts/2025/11/",
  "is_archived": false,
  "archived_at": null,
  "analyzed_at": "2025-11-20T10:40:00Z",
  "processing_time": 300.5,
  "metadata": {
    "page_count": 15,
    "word_count": 3500
  },
  "tags": ["nda", "confidential"],
  "uploaded_by_name": "John Doe",
  "created_at": "2025-11-20T10:35:00Z",
  "updated_at": "2025-11-20T10:40:00Z",
  "download_url": "https://s3.amazonaws.com/bucket/path/to/file.pdf?signature=...",
  "analysis": {
    "id": "analysis-id",
    "overall_risk_score": 75,
    "critical_issues_count": 2,
    "missing_clauses_count": 1,
    "priority_level": "medium",
    "processing_time": 300.5,
    "model_used": "gpt-4-turbo",
    "model_version": "1.0",
    "created_at": "2025-11-20T10:40:00Z"
  },
  "clauses": [
    {
      "id": "clause-id-1",
      "clause_number": "1.1",
      "clause_type": "payment",
      "clause_category": "payment_terms",
      "title": "Payment Terms",
      "content": "Payment shall be made within 30 days of invoice date...",
      "page_number": 3,
      "risk_level": "medium",
      "quality_score": 85,
      "completeness_score": 90,
      "is_standard": true,
      "has_issues": false,
      "tags": ["payment", "net30"],
      "created_at": "2025-11-20T10:40:00Z"
    },
    {
      "id": "clause-id-2",
      "clause_number": "2.1",
      "clause_type": "termination",
      "clause_category": "contract_termination",
      "title": "Termination",
      "content": "Either party may terminate this agreement...",
      "page_number": 5,
      "risk_level": "high",
      "quality_score": 72,
      "completeness_score": 80,
      "is_standard": false,
      "has_issues": true,
      "tags": ["termination", "notice"],
      "created_at": "2025-11-20T10:40:00Z"
    }
  ]
}
```

---

### 3.4 Get Contract Analysis Results

**Endpoint**: `GET {{base_url}}/api/v2/contracts/{{contract_id}}/results/`

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Response (200 OK)** - When analysis is complete:
```json
{
  "contract_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "risk_score": 75,
  "compliance_score": 85,
  "sentiment_score": 0.2,
  "analysis": {
    "summary": "This service agreement contains standard clauses with moderate risk level...",
    "executive_summary": {
      "overall_assessment": "Medium Risk",
      "priority_level": "medium",
      "recommendation": "Review liability and termination clauses before signing"
    },
    "risk_assessment": [
      {
        "type": "high_risk",
        "category": "liability",
        "description": "Unlimited liability clause present",
        "severity": "high",
        "page_number": 8,
        "recommendation": "Negotiate liability cap or insurance requirements",
        "potential_impact": "Significant financial exposure"
      },
      {
        "type": "medium_risk",
        "category": "termination",
        "description": "Short termination notice period",
        "severity": "medium",
        "page_number": 5,
        "recommendation": "Request 60-day notice period instead of 30 days",
        "potential_impact": "Limited time to transition"
      }
    ],
    "clauses": [
      {
        "type": "payment",
        "title": "Payment Terms",
        "content": "Payment shall be made within 30 days...",
        "risk_level": "low",
        "page_number": 3,
        "issues": [],
        "recommendations": []
      },
      {
        "type": "liability",
        "title": "Limitation of Liability",
        "content": "Party shall be liable for all damages...",
        "risk_level": "high",
        "page_number": 8,
        "issues": [
          "No liability cap specified",
          "No force majeure protection"
        ],
        "recommendations": [
          "Add liability cap clause",
          "Include force majeure provisions"
        ]
      }
    ],
    "compliance_check": {
      "score": 85,
      "compliant_areas": [
        "Governing law specified",
        "Dispute resolution mechanism included",
        "Confidentiality provisions present"
      ],
      "non_compliant_areas": [
        "No data protection clause (GDPR)",
        "Missing intellectual property rights section"
      ]
    },
    "missing_clauses": [
      {
        "type": "force_majeure",
        "importance": "high",
        "description": "No force majeure clause to protect against unforeseen events",
        "recommendation": "Add standard force majeure provision"
      },
      {
        "type": "data_protection",
        "importance": "critical",
        "description": "No GDPR/data protection compliance clause",
        "recommendation": "Add data protection and privacy clause"
      }
    ],
    "recommendations": [
      "Add liability cap of 2x annual contract value",
      "Include force majeure clause",
      "Extend termination notice to 60 days",
      "Add data protection compliance clause",
      "Specify intellectual property ownership"
    ],
    "key_dates": {
      "effective_date": "2024-01-01",
      "expiry_date": "2025-01-01",
      "notice_period": "30 days",
      "renewal_date": "2024-12-01"
    },
    "parties": [
      {
        "name": "ABC Corporation",
        "role": "Client",
        "obligations": [
          "Timely payment",
          "Provide necessary information"
        ]
      },
      {
        "name": "XYZ Services Ltd",
        "role": "Service Provider",
        "obligations": [
          "Deliver services as specified",
          "Maintain confidentiality"
        ]
      }
    ]
  }
}
```

**Response (200 OK)** - When analysis is still in progress:
```json
{
  "contract_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "processing",
  "progress": 65,
  "message": "Analysis in progress"
}
```

---

### 3.5 Update Contract Metadata

**Endpoint**: `PATCH {{base_url}}/api/v2/contracts/{{contract_id}}/`

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Request Body**:
```json
{
  "contract_type": "updated_service_agreement",
  "tags": ["updated", "reviewed", "approved"],
  "metadata": {
    "reviewed_by": "Legal Team",
    "review_date": "2025-11-20",
    "status": "approved"
  }
}
```

**Response (200 OK)**:
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "contract_type": "updated_service_agreement",
  "tags": ["updated", "reviewed", "approved"],
  "metadata": {
    "reviewed_by": "Legal Team",
    "review_date": "2025-11-20",
    "status": "approved"
  },
  // ... other fields
}
```

---

### 3.6 Re-analyze Contract

**Endpoint**: `POST {{base_url}}/api/v2/contracts/{{contract_id}}/reanalyze/`

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Response (200 OK)**:
```json
{
  "message": "Contract re-analysis started",
  "contract_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 3.7 Export Contract Report (PDF)

**Endpoint**: `POST {{base_url}}/api/v2/contracts/{{contract_id}}/export/pdf/`

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Response (200 OK)**:
```json
{
  "download_url": "https://s3.amazonaws.com/bucket/reports/contract_a1b2c3d4_report.pdf?signature=...",
  "expires_in": 3600
}
```

---

### 3.8 Export Contract Report (DOCX)

**Endpoint**: `POST {{base_url}}/api/v2/contracts/{{contract_id}}/export/docx/`

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Response (200 OK)**:
```json
{
  "download_url": "https://s3.amazonaws.com/bucket/reports/contract_a1b2c3d4_report.docx?signature=...",
  "expires_in": 3600
}
```

---

### 3.9 Archive Contract

**Endpoint**: `POST {{base_url}}/api/v2/contracts/{{contract_id}}/archive/`

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Response (200 OK)**:
```json
{
  "message": "Contract archived successfully"
}
```

---

### 3.10 Restore Archived Contract

**Endpoint**: `POST {{base_url}}/api/v2/contracts/{{contract_id}}/restore/`

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Response (200 OK)**:
```json
{
  "message": "Contract restored successfully"
}
```

---

### 3.11 Get Contract Clauses

**Endpoint**: `GET {{base_url}}/api/v2/contracts/{{contract_id}}/clauses/`

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Response (200 OK)**:
```json
[
  {
    "id": "clause-id-1",
    "clause_number": "1.1",
    "clause_type": "payment",
    "clause_category": "payment_terms",
    "title": "Payment Terms",
    "content": "Payment shall be made within 30 days of invoice date...",
    "page_number": 3,
    "risk_level": "low",
    "quality_score": 85,
    "completeness_score": 90,
    "is_standard": true,
    "has_issues": false,
    "tags": ["payment", "net30"],
    "metadata": {},
    "created_at": "2025-11-20T10:40:00Z"
  },
  {
    "id": "clause-id-2",
    "clause_number": "2.1",
    "clause_type": "liability",
    "clause_category": "limitation_of_liability",
    "title": "Limitation of Liability",
    "content": "Party shall be liable for all damages arising from...",
    "page_number": 8,
    "risk_level": "high",
    "quality_score": 65,
    "completeness_score": 70,
    "is_standard": false,
    "has_issues": true,
    "tags": ["liability", "high-risk"],
    "metadata": {
      "issues": ["No liability cap", "No exclusions"]
    },
    "created_at": "2025-11-20T10:40:00Z"
  }
]
```

---

### 3.12 Delete Contract

**Endpoint**: `DELETE {{base_url}}/api/v2/contracts/{{contract_id}}/`

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Response (204 No Content)**: No response body

---

## 4. User Management APIs

### 4.1 List Users (Admin Only)

**Endpoint**: `GET {{base_url}}/api/v2/accounts/users/`

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Query Parameters**:
```
?role=admin                   # Filter by role
&is_active=true               # Filter by active status
&search=john                  # Search in email/name
```

**Response (200 OK)**:
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "user-id-1",
      "email": "john.doe@demo.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "user",
      "is_active": true,
      "is_verified": false,
      "full_name": "John Doe",
      "created_at": "2025-11-20T10:30:00Z",
      "updated_at": "2025-11-20T10:30:00Z"
    }
  ]
}
```

---

### 4.2 Create User (Admin Only)

**Endpoint**: `POST {{base_url}}/api/v2/accounts/users/`

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Request Body**:
```json
{
  "email": "jane.smith@demo.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "manager"
}
```

**Response (201 Created)**:
```json
{
  "id": "user-id-2",
  "email": "jane.smith@demo.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "manager",
  "is_active": true,
  "is_verified": false,
  "full_name": "Jane Smith",
  "created_at": "2025-11-20T11:00:00Z",
  "updated_at": "2025-11-20T11:00:00Z"
}
```

---

### 4.3 Update User (Admin Only)

**Endpoint**: `PATCH {{base_url}}/api/v2/accounts/users/{{user_id}}/`

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}",
  "X-Tenant-ID": "{{tenant_id}}"
}
```

**Request Body**:
```json
{
  "first_name": "Jane Updated",
  "role": "admin",
  "is_active": true
}
```

**Response (200 OK)**:
```json
{
  "id": "user-id-2",
  "email": "jane.smith@demo.com",
  "first_name": "Jane Updated",
  "last_name": "Smith",
  "role": "admin",
  "is_active": true,
  "is_verified": false,
  "full_name": "Jane Updated Smith",
  "created_at": "2025-11-20T11:00:00Z",
  "updated_at": "2025-11-20T11:05:00Z"
}
```

---

## 5. Testing Workflows

### Workflow 1: Complete Contract Upload and Analysis

```
Step 1: Register/Login
POST /api/v2/accounts/users/login/
→ Save access_token

Step 2: Upload Contract
POST /api/v2/contracts/upload/
→ Save contract_id

Step 3: Check Status (Poll every 5 seconds)
GET /api/v2/contracts/{contract_id}/
→ Wait until status = "completed"

Step 4: Get Analysis Results
GET /api/v2/contracts/{contract_id}/results/
→ View full analysis

Step 5: Get Clauses
GET /api/v2/contracts/{contract_id}/clauses/
→ View extracted clauses

Step 6: Export Report
POST /api/v2/contracts/{contract_id}/export/pdf/
→ Download PDF report
```

### Workflow 2: Multi-User Collaboration

```
Step 1: Admin creates users
POST /api/v2/accounts/users/
→ Create manager, users, viewers

Step 2: Manager uploads contracts
POST /api/v2/contracts/upload/

Step 3: Users view contracts
GET /api/v2/contracts/
→ See only tenant's contracts

Step 4: Admin archives old contracts
POST /api/v2/contracts/{contract_id}/archive/
```

---

## 6. Error Handling

### Common HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| **200** | OK | Request successful |
| **201** | Created | Resource created successfully |
| **204** | No Content | Request successful, no body returned |
| **400** | Bad Request | Invalid request data |
| **401** | Unauthorized | Invalid or missing authentication |
| **403** | Forbidden | Insufficient permissions |
| **404** | Not Found | Resource not found |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Server Error | Server error |

### Error Response Format

**Standard Error**:
```json
{
  "detail": "Authentication credentials were not provided.",
  "code": "not_authenticated"
}
```

**Validation Error**:
```json
{
  "email": ["This field is required."],
  "password": ["Password must be at least 12 characters."],
  "non_field_errors": ["Passwords don't match."]
}
```

**Rate Limit Error**:
```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds.",
  "code": "throttled"
}
```

---

## Quick Reference: All Endpoints

### Authentication
- `POST /api/v2/accounts/users/register/` - Register user
- `POST /api/v2/accounts/users/login/` - Login
- `GET /api/v2/accounts/users/me/` - Get current user
- `POST /api/v2/auth/token/refresh/` - Refresh token
- `POST /api/v2/accounts/users/change_password/` - Change password

### Contracts
- `POST /api/v2/contracts/upload/` - Upload contract
- `GET /api/v2/contracts/` - List contracts
- `GET /api/v2/contracts/{id}/` - Get contract details
- `GET /api/v2/contracts/{id}/results/` - Get analysis results
- `PATCH /api/v2/contracts/{id}/` - Update contract
- `DELETE /api/v2/contracts/{id}/` - Delete contract
- `POST /api/v2/contracts/{id}/reanalyze/` - Re-analyze
- `POST /api/v2/contracts/{id}/export/pdf/` - Export PDF
- `POST /api/v2/contracts/{id}/export/docx/` - Export DOCX
- `POST /api/v2/contracts/{id}/archive/` - Archive
- `POST /api/v2/contracts/{id}/restore/` - Restore
- `GET /api/v2/contracts/{id}/clauses/` - Get clauses

### Users (Admin)
- `GET /api/v2/accounts/users/` - List users
- `POST /api/v2/accounts/users/` - Create user
- `PATCH /api/v2/accounts/users/{id}/` - Update user

---

**Happy Testing! 🚀**


