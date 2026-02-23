# ChainSight AI API Documentation

## Overview
ChainSight AI is a multi-tenant contract analysis platform that provides AI-powered contract review, risk assessment, and compliance monitoring.

## Multi-Tenancy Architecture

### How Multi-Tenancy Works
ChainSight AI uses **row-level security multi-tenancy** to ensure complete data isolation between organizations:

1. **Tenant Model**: Each organization has a unique `Tenant` record
2. **User Isolation**: Users belong to specific tenants
3. **Automatic Filtering**: Middleware filters data by tenant context
4. **Subdomain Support**: `tenant.yourdomain.com` routing
5. **API Headers**: `X-Tenant-ID` header for API requests

### Tenant Identification Methods
1. **Subdomain**: `demo.chainsight.ai` → tenant "demo"
2. **API Header**: `X-Tenant-ID: 123`
3. **User Context**: Authenticated user's tenant

### Plan Tiers
- **Free**: 10 users, 1,000 contracts/month, 100GB storage
- **Starter**: 100 users, 10,000 contracts/month, 1TB storage
- **Professional**: 500 users, 50,000 contracts/month, 5TB storage
- **Enterprise**: Unlimited usage

## Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL
- Redis
- AWS S3 (for file storage)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd ChainSightAI

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate --settings=config.settings.development

# Create superuser
python manage.py createsuperuser --settings=config.settings.development

# Start server
python manage.py runserver --settings=config.settings.development
```

### Creating Demo Data
```bash
# Create demo tenant and user
python manage.py shell --settings=config.settings.development -c "
from apps.tenants.models import Tenant
from apps.accounts.models import User
t = Tenant.objects.create(name='Demo Company', subdomain='demo')
u = User.objects.create_user(email='admin@demo.com', password='password123', tenant=t, role='admin')
print('Demo tenant and admin user created')
"
```

## API Endpoints

### Authentication

#### Register User
```http
POST /api/v2/accounts/users/register/
Content-Type: application/json
X-Tenant-ID: 1


{
  "email": "shamimkhaled@gmail.com",
  "password": "shamimkhaled9999",
  "password_confirm": "shamimkhaled9999",
  "username": "shamim",
  "first_name": "shamim",
  "last_name": "khaled",
  "phone": "987654",
  "role": "admin/user",
  "is_active": true
}
```

**Response (201):**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@demo.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "is_active": true,
    "is_verified": false,
    "full_name": "John Doe",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

#### Login User
```http
POST /api/v1/accounts/users/login/
Content-Type: application/json
X-Tenant-ID: 1

{
  "email": "user@demo.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@demo.com",
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

#### Get Current User
```http
GET /api/v2/accounts/users/me/
Authorization: Bearer <access_token>
X-Tenant-ID: 1
```

**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@demo.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "full_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Change Password
```http
POST /api/v2/accounts/users/change_password/
Authorization: Bearer <access_token>
X-Tenant-ID: 1
Content-Type: application/json

{
  "old_password": "oldpassword123",
  "new_password": "newpassword123",
  "new_password_confirm": "newpassword123"
}
```

**Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

### Contracts

#### Upload Contract
```http
POST /api/v2/contracts/upload/
Authorization: Bearer <access_token>
X-Tenant-ID: 1
Content-Type: multipart/form-data

Form Data:
- file: [contract.pdf] (required)
- industry: "technology" (required)
- language: "english" (default: "english")
- contract_type: "service_agreement" (optional)
- contract_date: "2024-01-01" (optional)
- expiry_date: "2025-01-01" (optional)
- tags: ["nda", "confidential"] (optional)
```

**Response (201):**
```json
{
  "contract_id": "uuid",
  "status": "pending",
  "message": "Contract uploaded successfully. Analysis in progress."
}
```

#### List Contracts
```http
GET /api/v2/contracts/
Authorization: Bearer <access_token>
X-Tenant-ID: 1

Query Parameters:
- page: 1 (pagination)
- page_size: 20 (pagination)
- status: "completed" (filter)
- industry: "technology" (filter)
- risk_score__gte: 50 (filter)
- search: "agreement" (search in filename, contract_type)
- ordering: "-created_at" (ordering)
```

**Response (200):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "original_filename": "service_agreement.pdf",
      "file_size": 1024000,
      "file_type": "application/pdf",
      "status": "completed",
      "progress_percentage": 100,
      "industry": "technology",
      "language": "english",
      "risk_score": 75,
      "compliance_score": 85,
      "sentiment_score": 0.2,
      "contract_date": "2024-01-01",
      "expiry_date": "2025-01-01",
      "contract_value": null,
      "currency": null,
      "uploaded_by_name": "John Doe",
      "created_at": "2024-01-01T00:00:00Z",
      "analyzed_at": "2024-01-01T00:05:00Z"
    }
  ]
}
```

#### Get Contract Details
```http
GET /api/v2/contracts/{contract_id}/
Authorization: Bearer <access_token>
X-Tenant-ID: 1
```

**Response (200):**
```json
{
  "id": "uuid",
  "original_filename": "service_agreement.pdf",
  "file_size": 1024000,
  "file_type": "application/pdf",
  "file_hash": "abc123...",
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
  "contract_value": null,
  "currency": null,
  "counterparties": [],
  "risk_score": 75,
  "compliance_score": 85,
  "sentiment_score": 0.2,
  "is_scanned_pdf": false,
  "ocr_method_used": null,
  "folder_path": null,
  "is_archived": false,
  "archived_at": null,
  "analyzed_at": "2024-01-01T00:05:00Z",
  "processing_time": 300,
  "metadata": {},
  "tags": ["nda", "confidential"],
  "uploaded_by_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:05:00Z",
  "download_url": "https://s3.amazonaws.com/...",
  "analysis": {
    "id": "uuid",
    "overall_risk_score": 75,
    "critical_issues_count": 2,
    "missing_clauses_count": 1,
    "priority_level": "medium",
    "processing_time": 300,
    "model_used": "gpt-4-turbo",
    "model_version": "1.0",
    "created_at": "2024-01-01T00:05:00Z"
  },
  "clauses": [
    {
      "id": "uuid",
      "clause_number": 1,
      "clause_type": "termination",
      "clause_category": "contract_termination",
      "title": "Termination Clause",
      "content": "Either party may terminate...",
      "page_number": 5,
      "risk_level": "medium",
      "quality_score": 85,
      "completeness_score": 90,
      "is_standard": true,
      "has_issues": false,
      "tags": ["termination", "breach"],
      "metadata": {},
      "created_at": "2024-01-01T00:05:00Z"
    }
  ]
}
```

#### Get Contract Analysis Results
```http
GET /api/v2/contracts/{contract_id}/results/
Authorization: Bearer <access_token>
X-Tenant-ID: 1
```

**Response (200):**
```json
{
  "contract_id": "uuid",
  "status": "completed",
  "risk_score": 75,
  "compliance_score": 85,
  "sentiment_score": 0.2,
  "analysis": {
    "summary": "This service agreement contains standard clauses...",
    "risks": [
      {
        "type": "high_risk",
        "description": "Unlimited liability clause",
        "severity": "high",
        "recommendation": "Consider liability caps"
      }
    ],
    "clauses": [
      {
        "type": "termination",
        "content": "Either party may terminate...",
        "risk_level": "medium",
        "issues": []
      }
    ],
    "recommendations": [
      "Add force majeure clause",
      "Specify governing law",
      "Include dispute resolution mechanism"
    ],
    "compliance_score": 85,
    "missing_clauses": ["force_majeure", "governing_law"]
  }
}
```

#### Update Contract
```http
PUT /api/v2/contracts/{contract_id}/
Authorization: Bearer <access_token>
X-Tenant-ID: 1
Content-Type: application/json

{
  "contract_type": "updated_type",
  "tags": ["updated", "tags"]
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "original_filename": "service_agreement.pdf",
  // ... updated contract data
}
```

#### Delete Contract
```http
DELETE /api/v2/contracts/{contract_id}/
Authorization: Bearer <access_token>
X-Tenant-ID: 1
```

**Response (204):** No Content

#### Re-analyze Contract
```http
POST /api/v2/contracts/{contract_id}/reanalyze/
Authorization: Bearer <access_token>
X-Tenant-ID: 1
```

**Response (200):**
```json
{
  "message": "Contract re-analysis started",
  "contract_id": "uuid"
}
```

#### Export Contract Report (PDF)
```http
POST /api/v2/contracts/{contract_id}/export/pdf/
Authorization: Bearer <access_token>
X-Tenant-ID: 1
```

**Response (200):**
```json
{
  "download_url": "https://s3.amazonaws.com/bucket/reports/contract_uuid_report.pdf?signature...",
  "expires_in": 3600
}
```

#### Export Contract Report (DOCX)
```http
POST /api/v2/contracts/{contract_id}/export/docx/
Authorization: Bearer <access_token>
X-Tenant-ID: 1
```

**Response (200):**
```json
{
  "download_url": "https://s3.amazonaws.com/bucket/reports/contract_uuid_report.docx?signature...",
  "expires_in": 3600
}
```

#### Archive Contract
```http
POST /api/v2/contracts/{contract_id}/archive/
Authorization: Bearer <access_token>
X-Tenant-ID: 1
```

**Response (200):**
```json
{
  "message": "Contract archived successfully"
}
```

#### Restore Contract
```http
POST /api/v2/contracts/{contract_id}/restore/
Authorization: Bearer <access_token>
X-Tenant-ID: 1
```

**Response (200):**
```json
{
  "message": "Contract restored successfully"
}
```

#### Get Contract Clauses
```http
GET /api/v2/contracts/{contract_id}/clauses/
Authorization: Bearer <access_token>
X-Tenant-ID: 1
```

**Response (200):**
```json
[
  {
    "id": "uuid",
    "clause_number": 1,
    "clause_type": "termination",
    "clause_category": "contract_termination",
    "title": "Termination Clause",
    "content": "Either party may terminate this agreement...",
    "page_number": 5,
    "risk_level": "medium",
    "quality_score": 85,
    "completeness_score": 90,
    "is_standard": true,
    "has_issues": false,
    "tags": ["termination", "breach"],
    "metadata": {},
    "created_at": "2024-01-01T00:05:00Z"
  }
]
```

### Users Management

#### List Users
```http
GET /api/v2/accounts/users/
Authorization: Bearer <access_token>
X-Tenant-ID: 1

Query Parameters:
- role: "admin" (filter)
- is_active: true (filter)
- search: "john" (search in email, name)
```

**Response (200):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "email": "user@demo.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "user",
      "is_active": true,
      "is_verified": false,
      "full_name": "John Doe",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Create User
```http
POST /api/v2/accounts/users/
Authorization: Bearer <access_token>
X-Tenant-ID: 1
Content-Type: application/json

{
  "email": "newuser@demo.com",
  "password": "password123",
  "password_confirm": "password123",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "user"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "newuser@demo.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "full_name": "Jane Smith",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Update User
```http
PUT /api/v2/accounts/users/{user_id}/
Authorization: Bearer <access_token>
X-Tenant-ID: 1
Content-Type: application/json

{
  "first_name": "Jane Updated",
  "role": "manager"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "email": "newuser@demo.com",
  "first_name": "Jane Updated",
  "last_name": "Smith",
  "role": "manager",
  "is_active": true,
  "is_verified": false,
  "full_name": "Jane Updated Smith",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:05:00Z"
}
```

## Postman Collection

### Import the following collection into Postman:

```json
{
  "info": {
    "name": "ChainSight AI API",
    "description": "Complete API collection for ChainSight AI contract analysis platform",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://127.0.0.1:8000",
      "type": "string"
    },
    {
      "key": "tenant_id",
      "value": "1",
      "type": "string"
    },
    {
      "key": "access_token",
      "value": "",
      "type": "string"
    }
  ],
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Register User",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              },
              {
                "key": "X-Tenant-ID",
                "value": "{{tenant_id}}"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"user@demo.com\",\n  \"password\": \"password123\",\n  \"password_confirm\": \"password123\",\n  \"first_name\": \"John\",\n  \"last_name\": \"Doe\",\n  \"role\": \"user\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/v2/accounts/users/register/",
              "host": ["{{base_url}}"],
              "path": ["api", "v2", "accounts", "users", "register", ""]
            }
          }
        },
        {
          "name": "Login User",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              },
              {
                "key": "X-Tenant-ID",
                "value": "{{tenant_id}}"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"user@demo.com\",\n  \"password\": \"password123\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/v2/accounts/users/login/",
              "host": ["{{base_url}}"],
              "path": ["api", "v2", "accounts", "users", "login", ""]
            }
          }
        }
      ]
    },
    {
      "name": "Contracts",
      "item": [
        {
          "name": "Upload Contract",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              },
              {
                "key": "X-Tenant-ID",
                "value": "{{tenant_id}}"
              }
            ],
            "body": {
              "mode": "formdata",
              "formdata": [
                {
                  "key": "file",
                  "type": "file",
                  "src": []
                },
                {
                  "key": "industry",
                  "value": "technology",
                  "type": "text"
                },
                {
                  "key": "language",
                  "value": "english",
                  "type": "text"
                }
              ]
            },
            "url": {
              "raw": "{{base_url}}/api/v2/contracts/upload/",
              "host": ["{{base_url}}"],
              "path": ["api", "v2", "contracts", "upload", ""]
            }
          }
        },
        {
          "name": "List Contracts",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              },
              {
                "key": "X-Tenant-ID",
                "value": "{{tenant_id}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/api/v2/contracts/",
              "host": ["{{base_url}}"],
              "path": ["api", "v2", "contracts", ""]
            }
          }
        }
      ]
    }
  ]
}
```

## Error Handling

### Common HTTP Status Codes
- **200**: Success
- **201**: Created
- **204**: No Content
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **429**: Too Many Requests
- **500**: Internal Server Error

### Error Response Format
```json
{
  "detail": "Authentication credentials were not provided.",
  "code": "not_authenticated"
}
```

### Validation Error Format
```json
{
  "field_name": [
    "This field is required."
  ],
  "non_field_errors": [
    "Passwords don't match."
  ]
}
```

## Rate Limiting

Rate limits are applied per tenant based on their plan:

- **Free**: 100 requests/hour per user
- **Starter**: 500 requests/hour per user
- **Professional**: 2000 requests/hour per user
- **Enterprise**: Unlimited

## File Upload Limits

- **Maximum file size**: 50MB
- **Allowed extensions**: .pdf, .docx, .txt, .jpg, .jpeg, .png
- **Supported formats**: PDF, Word documents, text files, images

## Webhooks (Future Feature)

ChainSight AI supports webhooks for real-time notifications:

- Contract analysis completed
- Risk threshold exceeded
- Compliance issues detected
- User account changes

## Support

For API support or questions:
- **Documentation**: http://127.0.0.1:8000/api/docs/
- **Email**: support@chainsight.ai
- **GitHub Issues**: Report bugs and feature requests

---

**Last Updated**: October 15, 2024
**Version**: 1.0.0