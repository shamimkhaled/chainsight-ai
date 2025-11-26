# ChainSight AI - Complete API Endpoints Summary

## Base URL
```
http://127.0.0.1:8000/api/v2/
```

## Authentication Required
Unless marked as `[Public]`, all endpoints require:
- **Authorization**: `Bearer <access_token>`
- **X-Tenant-ID**: `<tenant_id>`

---

## 🔐 Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/token/` | Get JWT access and refresh tokens | No |
| POST | `/auth/token/refresh/` | Refresh access token | No |

---

## 👤 User Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/users/register/` | Register new user | No |
| POST | `/users/login/` | Login user | No |
| GET | `/users/me/` | Get current user profile | Yes |
| POST | `/users/change_password/` | Change password | Yes |
| GET | `/users/` | List users (filtered by tenant) | Yes |
| POST | `/users/` | Create new user (admin) | Yes |
| GET | `/users/{id}/` | Get user details | Yes |
| PATCH | `/users/{id}/` | Update user | Yes |
| DELETE | `/users/{id}/` | Delete user | Yes |

---

## 📄 Contract Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/contracts/upload/` | Upload contract for analysis | Yes |
| GET | `/contracts/` | List contracts with filters | Yes |
| GET | `/contracts/{id}/` | Get contract details | Yes |
| GET | `/contracts/{id}/results/` | Get AI analysis results | Yes |
| PATCH | `/contracts/{id}/` | Update contract metadata | Yes |
| DELETE | `/contracts/{id}/` | Delete contract | Yes |
| POST | `/contracts/{id}/reanalyze/` | Re-analyze contract | Yes |
| POST | `/contracts/{id}/export/pdf/` | Export report as PDF | Yes |
| POST | `/contracts/{id}/export/docx/` | Export report as DOCX | Yes |
| POST | `/contracts/{id}/archive/` | Archive contract | Yes |
| POST | `/contracts/{id}/restore/` | Restore archived contract | Yes |
| GET | `/contracts/{id}/clauses/` | Get contract clauses | Yes |

**Query Parameters for List:**
- `page`: Page number (pagination)
- `page_size`: Items per page (default: 20)
- `status`: Filter by status (`pending`, `processing`, `completed`, `failed`)
- `industry`: Filter by industry
- `risk_score__gte`: Filter by minimum risk score
- `search`: Search in filename and contract type
- `ordering`: Order by field (prefix with `-` for descending)

---

## 🏢 Counterparty Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/counterparties/` | List counterparties | Yes |
| POST | `/counterparties/` | Create counterparty | Yes |
| GET | `/counterparties/{id}/` | Get counterparty details | Yes |
| PATCH | `/counterparties/{id}/` | Update counterparty | Yes |
| DELETE | `/counterparties/{id}/` | Delete counterparty | Yes |
| POST | `/counterparties/{id}/verify/` | Verify counterparty | Yes |
| GET | `/counterparties/{id}/contracts/` | Get contracts for counterparty | Yes |

**Query Parameters for List:**
- `risk_level`: Filter by risk level
- `is_verified`: Filter verified counterparties
- `country`: Filter by country
- `search`: Search in name, legal name, registration number

---

## 🏠 Tenant Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/tenants/` | List tenants (admin/own) | Yes |
| POST | `/tenants/` | Create tenant (superuser) | Yes |
| GET | `/tenants/{id}/` | Get tenant details | Yes |
| PATCH | `/tenants/{id}/` | Update tenant | Yes |
| DELETE | `/tenants/{id}/` | Delete tenant (superuser) | Yes |
| GET | `/tenants/me/` | Get current user's tenant | Yes |
| POST | `/tenants/{id}/activate/` | Activate tenant (superuser) | Yes |
| POST | `/tenants/{id}/suspend/` | Suspend tenant (superuser) | Yes |
| GET | `/tenants/{id}/usage/` | Get tenant usage statistics | Yes |

---

## 📊 Dashboard & Analytics

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/dashboard/` | Get dashboard statistics | Yes |
| GET | `/dashboard/trends/` | Get contract trends over time | Yes |
| GET | `/dashboard/risk-distribution/` | Get risk distribution analytics | Yes |

**Query Parameters for Trends:**
- `period`: Number of days (default: 30)

---

## 📋 Waitlist & Demo

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/waitlist/join/` | Join waitlist | No |
| GET | `/waitlist/count/` | Get waitlist count | No |
| GET | `/waitlist/` | List waitlist entries (admin) | Yes |
| GET | `/waitlist/{id}/` | Get waitlist entry | Yes |
| PATCH | `/waitlist/{id}/` | Update waitlist entry | Yes |
| DELETE | `/waitlist/{id}/` | Delete waitlist entry | Yes |
| POST | `/demos/book/` | Book a demo | No |
| GET | `/demos/availability/` | Get demo availability | No |
| GET | `/demos/` | List demo requests (admin) | Yes |
| GET | `/demos/{id}/` | Get demo request details | Yes |
| POST | `/demos/{id}/schedule/` | Schedule demo (admin) | Yes |
| POST | `/demos/{id}/complete/` | Mark demo completed (admin) | Yes |

---

## 🏥 Health & Monitoring

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/health/` | Health check | No |
| GET | `/api/health/ready/` | Readiness check | No |
| GET | `/api/health/info/` | API information | No |

---

## 📚 Documentation

| Endpoint | Description |
|----------|-------------|
| `/api/docs/` | Swagger UI documentation |
| `/api/docs/redoc/` | ReDoc documentation |

---

## Request & Response Examples

### Authentication

**POST /auth/token/**
```json
// Request
{
  "email": "user@example.com",
  "password": "password123"
}

// Response (200 OK)
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Upload Contract

**POST /contracts/upload/**
```
Content-Type: multipart/form-data

file: [contract.pdf]
industry: "technology"
language: "english"
tags: ["nda", "confidential"]
```

**Response (201 Created)**
```json
{
  "contract_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  "message": "Contract uploaded successfully. Analysis in progress."
}
```

### Dashboard Statistics

**GET /dashboard/**

**Response (200 OK)**
```json
{
  "contracts": {
    "total": 150,
    "completed": 120,
    "pending": 20,
    "processing": 10,
    "recent_30_days": 45,
    "expiring_soon_90_days": 12
  },
  "risk": {
    "high_risk_count": 15,
    "average_risk_score": 65.5
  },
  "users": {
    "total": 25,
    "active": 23
  },
  "alerts": {
    "open": 8
  },
  "tenant": {
    "name": "Acme Corporation",
    "plan_type": "professional",
    "max_contracts": 10000,
    "usage_percentage": 1.5
  }
}
```

---

## Error Response Format

**Validation Error (400)**
```json
{
  "email": ["This field is required."],
  "password": ["Password must be at least 12 characters."]
}
```

**Authentication Error (401)**
```json
{
  "detail": "Authentication credentials were not provided.",
  "code": "not_authenticated"
}
```

**Permission Error (403)**
```json
{
  "detail": "You do not have permission to perform this action.",
  "code": "permission_denied"
}
```

**Not Found Error (404)**
```json
{
  "detail": "Not found."
}
```

**Rate Limit Error (429)**
```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds.",
  "code": "throttled"
}
```

---

## Pagination

All list endpoints return paginated results:

```json
{
  "count": 100,
  "next": "http://127.0.0.1:8000/api/v2/contracts/?page=2",
  "previous": null,
  "results": [
    // Array of objects
  ]
}
```

---

## Filtering & Search

### Common Filters
- `status`: Filter by status
- `created_at__gte`: Filter by date greater than or equal
- `created_at__lte`: Filter by date less than or equal
- `search`: Full-text search

### Example
```
GET /api/v2/contracts/?status=completed&risk_score__gte=70&ordering=-created_at&page=1&page_size=20
```

---

## Rate Limits

| Plan | Rate Limit |
|------|------------|
| Free | 100 requests/hour |
| Starter | 500 requests/hour |
| Professional | 2000 requests/hour |
| Enterprise | Unlimited |

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 204 | No Content - Request successful, no body |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Invalid or missing authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

---

## Testing with cURL

```bash
# Get token
curl -X POST http://127.0.0.1:8000/api/v2/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@chainsight.ai","password":"yourpassword"}'

# List contracts
curl -X GET http://127.0.0.1:8000/api/v2/contracts/ \
  -H "Authorization: Bearer <access_token>" \
  -H "X-Tenant-ID: 1"

# Upload contract
curl -X POST http://127.0.0.1:8000/api/v2/contracts/upload/ \
  -H "Authorization: Bearer <access_token>" \
  -H "X-Tenant-ID: 1" \
  -F "file=@contract.pdf" \
  -F "industry=technology"

# Get dashboard stats
curl -X GET http://127.0.0.1:8000/api/v2/dashboard/ \
  -H "Authorization: Bearer <access_token>" \
  -H "X-Tenant-ID: 1"

# Health check
curl -X GET http://127.0.0.1:8000/api/health/
```

---

## Quick Start

1. **Create superuser**
   ```bash
   python manage.py createsuperuser --settings=config.settings.development
   ```

2. **Start server**
   ```bash
   python manage.py runserver --settings=config.settings.development
   ```

3. **Test endpoints**
   - Visit: http://127.0.0.1:8000/api/docs/
   - Health check: http://127.0.0.1:8000/api/health/
   - API info: http://127.0.0.1:8000/api/health/info/

---

**Documentation**: http://127.0.0.1:8000/api/docs/  
**Support**: support@chainsight.ai

---

**Last Updated**: November 26, 2025  
**API Version**: 2.0.0

