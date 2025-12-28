# 🧪 ChainSight AI - Complete Postman Testing Guide

## 📦 Quick Setup

### Step 1: Import Collection & Environment

1. **Open Postman**
2. **Import Collection**:
   - Click "Import" button
   - Select `ChainSight_AI_Postman_Collection.json`
   - Click "Import"

3. **Import Environment**:
   - Click "Import" button
   - Select `ChainSight_AI_Environment.postman_environment.json`
   - Click "Import"

4. **Activate Environment**:
   - Click environment dropdown (top-right)
   - Select "ChainSight AI - Local Development"

---

## 🚀 Complete Testing Workflow

### Phase 1: Authentication & Setup

#### Test 1: Register New Tenant
```
Request: POST {{base_url}}/tenants/register/
```

**What happens:**
- Creates new company (tenant)
- Creates admin user
- Returns JWT tokens
- Auto-saves tokens to environment

**Success Response (201):**
```json
{
  "tenant": {
    "id": "uuid-here",
    "name": "Acme Corporation",
    "subdomain": "acmecorp"
  },
  "admin_user": {
    "id": "user-uuid",
    "email": "admin@acmecorp.com"
  },
  "access_token": "eyJ0eXAi...",
  "refresh_token": "eyJ0eXAi..."
}
```

**Check:**
- ✅ Response code: 201
- ✅ `tenant_id` saved to environment
- ✅ `access_token` saved to environment

---

#### Test 2: Login (Alternative)
```
Request: POST {{base_url}}/auth/token/
Body: {
  "email": "admin@acmecorp.com",
  "password": "SecurePassword123!"
}
```

**Use this if:**
- You already registered
- Testing login flow
- Token expired

---

### Phase 2: Contract Upload & Analysis

#### Test 3: Upload Contract
```
Request: POST {{base_url}}/contracts/
Headers:
  - Authorization: Bearer {{access_token}}
  - X-Tenant-ID: {{tenant_id}}
Body (form-data):
  - file: [Select PDF file]
  - contract_type: Vendor Agreement
  - industry: manufacturing
```

**What happens:**
- File uploaded to S3
- Queued for AI processing
- Returns contract ID
- Auto-saves `contract_id` to environment

**Success Response (201):**
```json
{
  "id": "contract-uuid",
  "original_filename": "vendor_agreement.pdf",
  "status": "pending",
  "processing_stage": "uploaded",
  "progress_percentage": 0
}
```

---

#### Test 4: Check Processing Status
```
Request: GET {{base_url}}/contracts/{{contract_id}}/
```

**Poll this endpoint every 5 seconds:**

**Processing States:**
1. `status: "pending"` - Waiting in queue
2. `status: "processing"` - AI analyzing
   - `processing_stage: "ocr"` - OCR if needed
   - `processing_stage: "extraction"` - Extracting data
   - `processing_stage: "clause_extraction"` - Finding clauses
   - `processing_stage: "embeddings"` - Creating vectors
   - `processing_stage: "analysis"` - AI analysis
3. `status: "completed"` - Done!

**Completed Response:**
```json
{
  "id": "contract-uuid",
  "status": "completed",
  "progress_percentage": 100,
  "risk_score": 72,
  "compliance_score": 85,
  "clauses": [...],
  "analysis": {
    "overall_risk_score": 72,
    "critical_issues_count": 2,
    "issues": [...]
  }
}
```

**Check:**
- ✅ `status`: "completed"
- ✅ `risk_score`: 0-100
- ✅ `clauses` array populated
- ✅ `analysis` object present

---

### Phase 3: RAG Chat (Most Impressive!)

#### Test 5: Create Chat Session
```
Request: POST {{base_url}}/chat/sessions/
Body: {
  "title": "Questions about Vendor Agreement",
  "contracts": ["{{contract_id}}"],
  "model_used": "gpt-4"
}
```

**What happens:**
- Creates chat session
- Links to contract(s)
- Prepares RAG context
- Auto-saves `session_id`

---

#### Test 6: Ask Questions (RAG Magic!)
```
Request: POST {{base_url}}/chat/sessions/{{session_id}}/message/
Body: {
  "content": "What are the payment terms?"
}
```

**Try these questions:**

1. **Basic Questions:**
   - "What are the payment terms?"
   - "When does this contract expire?"
   - "Who are the parties involved?"

2. **Complex Questions:**
   - "What are the termination conditions?"
   - "Are there any liability limitations?"
   - "What happens in case of force majeure?"

3. **Analytical Questions:**
   - "What are the main risks in this contract?"
   - "Are there any missing clauses?"
   - "How does the liability compare to the contract value?"

**Response with Sources:**
```json
{
  "user_message": {
    "content": "What are the payment terms?"
  },
  "assistant_message": {
    "content": "Based on Clause 1.1, the payment terms are Net 30 days...",
    "sources": [
      {
        "contract_filename": "vendor_agreement.pdf",
        "clause_number": "1.1",
        "page_number": 3,
        "relevance_score": 0.95,
        "excerpt": "Payment shall be made within 30 days..."
      }
    ],
    "tokens_used": 456,
    "processing_time": 3.1
  }
}
```

**Check:**
- ✅ AI provides detailed answer
- ✅ `sources` array with citations
- ✅ References specific clauses
- ✅ Page numbers included

---

### Phase 4: Alerts & Monitoring

#### Test 7: Create Alert Rule
```
Request: POST {{base_url}}/alerts/rules/
Body: {
  "name": "High Risk Contract Alert",
  "alert_type": "risk_threshold",
  "threshold_value": 80.0,
  "severity": "high",
  "notify_email": true,
  "recipients": ["legal@acmecorp.com"],
  "is_active": true
}
```

**Alert Types to Test:**
1. `risk_threshold` - Risk score exceeds limit
2. `compliance` - Compliance score too low
3. `expiry` - Contract expiring soon
4. `missing_clause` - Required clause missing

---

#### Test 8: Check Active Alerts
```
Request: GET {{base_url}}/alerts/?status=active
```

**Filter Options:**
- `?status=active` - Active alerts
- `?severity=critical` - Critical only
- `?alert_type=risk_threshold` - By type

---

#### Test 9: Acknowledge Alert
```
Request: POST {{base_url}}/alerts/{{alert_id}}/acknowledge/
```

---

### Phase 5: Analytics & Dashboard

#### Test 10: Dashboard Overview
```
Request: GET {{base_url}}/dashboard/overview/
```

**Returns:**
- Total contracts
- Risk distribution
- Active alerts
- Recent activity
- Compliance scores

**Response:**
```json
{
  "summary": {
    "total_contracts": 523,
    "active_contracts": 412,
    "high_risk_contracts": 45
  },
  "risk_distribution": {
    "critical": 8,
    "high": 37,
    "medium": 198,
    "low": 280
  },
  "alerts": {
    "active_alerts": 12,
    "critical_alerts": 2
  }
}
```

---

#### Test 11: Generate Risk Report
```
Request: GET {{base_url}}/dashboard/reports/risk/?format=pdf
```

---

### Phase 6: Advanced Features

#### Test 12: Batch Upload
```
Request: POST {{base_url}}/contracts/batch_upload/
Body (form-data):
  - files[]: [file1.pdf]
  - files[]: [file2.pdf]
  - files[]: [file3.pdf]
  - industry: manufacturing
```

---

#### Test 13: Export to Word
```
Request: POST {{base_url}}/integrations/word/export/
Body: {
  "contract_id": "{{contract_id}}",
  "include_analysis": true
}
```

---

#### Test 14: Create Counterparty
```
Request: POST {{base_url}}/counterparties/
Body: {
  "name": "Vendor Inc.",
  "contact_email": "vendor@example.com",
  "address": {
    "city": "New York",
    "country": "USA"
  }
}
```

---

## 🎯 Testing Scenarios

### Scenario 1: Complete Contract Workflow
```
1. Register Tenant
2. Login
3. Upload Contract
4. Wait for Processing (poll status)
5. Create Chat Session
6. Ask 3-5 Questions
7. Review Clauses
8. Check Alerts
9. View Dashboard
10. Export Report
```

**Time:** ~5-10 minutes

---

### Scenario 2: Multi-User Collaboration
```
1. Login as Admin
2. Create Manager User
3. Create Regular User
4. Upload Contract as Admin
5. Login as Manager (new request)
6. Comment on Contract
7. Request Approval
8. Login as Admin
9. Approve Contract
```

---

### Scenario 3: Alert Testing
```
1. Create Alert Rule (risk > 80)
2. Upload High-Risk Contract
3. Wait for Processing
4. Check Alerts (should trigger)
5. Acknowledge Alert
6. Resolve Alert
```

---

## 🔧 Troubleshooting

### Issue 1: 401 Unauthorized
**Cause:** Token expired or missing

**Fix:**
1. Check environment variable `access_token` is set
2. Try "Refresh Token" request
3. Or login again

---

### Issue 2: 403 Forbidden
**Cause:** Insufficient permissions

**Fix:**
1. Check user role (need admin/manager for some actions)
2. Verify `X-Tenant-ID` header is set
3. Ensure user belongs to tenant

---

### Issue 3: 404 Not Found
**Cause:** Invalid ID or resource doesn't exist

**Fix:**
1. Check environment variables are set correctly
2. Verify resource was created successfully
3. Use correct ID format (UUID)

---

### Issue 4: File Upload Fails
**Cause:** File too large or wrong format

**Fix:**
1. Check file size (max 50MB)
2. Verify file type (.pdf, .docx, .txt, .jpg, .png)
3. Ensure file is not corrupted

---

## 📊 Expected Response Times

| Operation | Time | Status |
|-----------|------|--------|
| Login | <500ms | Instant |
| Upload | 1-3s | Fast |
| List Contracts | <1s | Fast |
| Contract Analysis | 30-60s | Processing |
| RAG Chat Query | 2-5s | Fast |
| Dashboard | <2s | Fast |
| Report Generation | 5-10s | Processing |

---

## ✅ Test Checklist

### Authentication ✓
- [ ] Register tenant
- [ ] Login
- [ ] Refresh token
- [ ] Create user
- [ ] List users

### Contracts ✓
- [ ] Upload single contract
- [ ] Batch upload contracts
- [ ] List contracts with filters
- [ ] Get contract details
- [ ] Analyze contract
- [ ] Archive contract
- [ ] Export contract

### RAG Chat ✓
- [ ] Create session
- [ ] Send message (basic)
- [ ] Send message (complex)
- [ ] Get session history
- [ ] Provide feedback

### Alerts ✓
- [ ] Create alert rule
- [ ] List alert rules
- [ ] List triggered alerts
- [ ] Acknowledge alert
- [ ] Resolve alert

### Dashboard ✓
- [ ] Get overview
- [ ] Get analytics
- [ ] Generate report

### Integrations ✓
- [ ] List integrations
- [ ] Create integration
- [ ] Export to Word

### Counterparties ✓
- [ ] List counterparties
- [ ] Create counterparty
- [ ] Get details

---

## 🎨 Postman Tips

### 1. Auto-Save Variables
Add this to "Tests" tab of requests:
```javascript
if (pm.response.code === 201) {
    var jsonData = pm.response.json();
    pm.environment.set('contract_id', jsonData.id);
}
```

### 2. Auto-Refresh Token
Add this to Collection "Pre-request Script":
```javascript
// Check if token is about to expire
// Refresh if needed
```

### 3. Create Test Suites
Use Collection Runner to:
- Run all tests sequentially
- Generate reports
- Automate testing

### 4. Use Variables
Instead of hardcoding, use:
- `{{base_url}}`
- `{{access_token}}`
- `{{tenant_id}}`

---

## 📈 Performance Testing

### Load Testing Endpoints
Test these for performance:
1. `/contracts/` (List)
2. `/dashboard/overview/`
3. `/chat/sessions/{id}/message/`

**Tools:**
- Postman Collection Runner
- Apache JMeter
- K6

---

## 🎯 Success Criteria

After completing all tests, you should have:
- ✅ 1 Tenant registered
- ✅ 2-3 Users created
- ✅ 3-5 Contracts uploaded
- ✅ 1-2 Chat sessions active
- ✅ 2-3 Alert rules configured
- ✅ Several triggered alerts
- ✅ Dashboard showing data
- ✅ Reports generated

---

## 📞 Support

### API Documentation
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/docs/redoc/

### Files Reference
- Collection: `ChainSight_AI_Postman_Collection.json`
- Environment: `ChainSight_AI_Environment.postman_environment.json`
- API Docs: `COMPLETE_API_DOCUMENTATION.md`

---

**Happy Testing! 🚀**

Start with Phase 1, then progress through each phase. The RAG Chat in Phase 3 is the most impressive feature to demo!


