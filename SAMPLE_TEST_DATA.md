# 📝 ChainSight AI - Sample Test Data

## 🎯 Quick Copy-Paste Test Data

### 1. Register Tenant
```json
{
  "company_name": "Acme Corporation",
  "subdomain": "acmecorp",
  "admin_email": "admin@acmecorp.com",
  "admin_password": "SecurePassword123!",
  "admin_first_name": "John",
  "admin_last_name": "Doe",
  "admin_phone": "+1-555-0123",
  "plan_type": "professional",
  "billing_email": "billing@acmecorp.com",
  "industry": "manufacturing"
}
```

### 2. Login
```json
{
  "email": "admin@acmecorp.com",
  "password": "SecurePassword123!"
}
```

### 3. Create Additional Users

**Manager:**
```json
{
  "email": "jane.manager@acmecorp.com",
  "password": "SecurePassword123!",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "manager",
  "phone": "+1-555-0124"
}
```

**Regular User:**
```json
{
  "email": "bob.user@acmecorp.com",
  "password": "SecurePassword123!",
  "first_name": "Bob",
  "last_name": "Johnson",
  "role": "user",
  "phone": "+1-555-0125"
}
```

**Viewer:**
```json
{
  "email": "alice.viewer@acmecorp.com",
  "password": "SecurePassword123!",
  "first_name": "Alice",
  "last_name": "Williams",
  "role": "viewer",
  "phone": "+1-555-0126"
}
```

---

## 💬 Sample Chat Questions

### Basic Questions
```
What are the payment terms in this contract?
```
```
When does this contract expire?
```
```
Who are the parties involved in this agreement?
```
```
What is the total contract value?
```
```
What is the effective date of this contract?
```

### Clause-Specific Questions
```
What are the termination conditions?
```
```
Are there any liability limitations?
```
```
What are the confidentiality requirements?
```
```
What happens in case of force majeure?
```
```
Are there any indemnification clauses?
```

### Analytical Questions
```
What are the main risks in this contract?
```
```
Are there any missing critical clauses?
```
```
How does the liability cap compare to the contract value?
```
```
What are the renewal terms?
```
```
Are there any unusual or non-standard clauses?
```

### Comparison Questions
```
How do the payment terms compare to our standard agreements?
```
```
Is the notice period reasonable?
```
```
Are the warranties sufficient?
```

### Multi-Part Questions
```
What are the payment terms, and how do they compare to industry standards?
```
```
Summarize the key risks and provide recommendations for mitigation.
```
```
What are the termination clauses, and what are the financial implications?
```

---

## 🚨 Sample Alert Rules

### 1. High Risk Alert
```json
{
  "name": "High Risk Contract Alert",
  "description": "Alert when contract risk score exceeds 80",
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
  "recipients": [
    "legal@acmecorp.com",
    "compliance@acmecorp.com"
  ],
  "is_active": true,
  "check_frequency": "realtime",
  "cooldown_period": 3600,
  "max_alerts_per_day": 10
}
```

### 2. Compliance Alert
```json
{
  "name": "Low Compliance Score Alert",
  "description": "Alert when compliance score falls below 60",
  "alert_type": "compliance",
  "category": "compliance",
  "conditions": {
    "field": "compliance_score",
    "operator": "lt",
    "value": 60
  },
  "threshold_value": 60.0,
  "comparison_operator": "lt",
  "severity": "critical",
  "priority": 10,
  "notify_email": true,
  "notify_sms": true,
  "recipients": [
    "compliance@acmecorp.com"
  ],
  "is_active": true,
  "check_frequency": "realtime"
}
```

### 3. Contract Expiry Alert
```json
{
  "name": "Contract Expiry Warning",
  "description": "Alert 90 days before contract expires",
  "alert_type": "expiry",
  "category": "contract_management",
  "conditions": {
    "days_before": 90
  },
  "severity": "medium",
  "priority": 6,
  "notify_email": true,
  "recipients": [
    "contracts@acmecorp.com"
  ],
  "is_active": true,
  "check_frequency": "daily"
}
```

### 4. Missing Clause Alert
```json
{
  "name": "Missing Critical Clause",
  "description": "Alert when critical clauses are missing",
  "alert_type": "missing_clause",
  "category": "risk_management",
  "conditions": {
    "required_clauses": [
      "termination",
      "liability",
      "confidentiality"
    ]
  },
  "severity": "high",
  "priority": 8,
  "notify_email": true,
  "recipients": [
    "legal@acmecorp.com"
  ],
  "is_active": true
}
```

---

## 🏪 Sample Counterparties

### 1. Vendor
```json
{
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
  }
}
```

### 2. Customer
```json
{
  "name": "Global Retail Corp",
  "legal_name": "Global Retail Corporation",
  "registration_number": "REG-54321",
  "tax_id": "TAX-09876",
  "contact_email": "contracts@globalretail.com",
  "contact_phone": "+1-555-0300",
  "website": "https://www.globalretail.com",
  "address": {
    "street": "456 Commerce Ave",
    "city": "Business City",
    "state": "NY",
    "postal_code": "10001",
    "country": "USA"
  }
}
```

### 3. Partner
```json
{
  "name": "TechPartners LLC",
  "legal_name": "TechPartners Limited Liability Company",
  "registration_number": "REG-98765",
  "tax_id": "TAX-54321",
  "contact_email": "partnerships@techpartners.com",
  "contact_phone": "+1-555-0400",
  "address": {
    "street": "789 Innovation Drive",
    "city": "Tech City",
    "state": "CA",
    "postal_code": "94043",
    "country": "USA"
  }
}
```

---

## 🔗 Sample Integration Configs

### Microsoft Word Integration
```json
{
  "name": "Microsoft Word Online",
  "integration_type": "microsoft_word",
  "config": {
    "tenant_id": "your-microsoft-tenant-id",
    "client_id": "your-client-id"
  },
  "auto_sync": true,
  "sync_interval": "hourly"
}
```

### Google Docs Integration
```json
{
  "name": "Google Docs",
  "integration_type": "google_docs",
  "config": {
    "project_id": "your-google-project-id",
    "client_id": "your-google-client-id"
  },
  "auto_sync": true,
  "sync_interval": "realtime"
}
```

### SAP ERP Integration
```json
{
  "name": "SAP Production",
  "integration_type": "sap",
  "config": {
    "base_url": "https://sap.acmecorp.com",
    "system_id": "PRD",
    "client": "100"
  },
  "auto_sync": true,
  "sync_interval": "daily"
}
```

---

## 💼 Sample Contract Metadata

### Vendor Agreement
```
contract_type: Vendor Agreement
industry: manufacturing
contract_value: 500000
currency: USD
```

### Service Agreement
```
contract_type: Service Agreement
industry: technology
contract_value: 250000
currency: USD
```

### NDA
```
contract_type: Non-Disclosure Agreement
industry: general
```

### Employment Contract
```
contract_type: Employment Contract
industry: human_resources
```

---

## 📊 Sample Report Requests

### Risk Report
```
GET /dashboard/reports/risk/?format=pdf&include_details=true
```

### Compliance Report
```
GET /dashboard/reports/compliance/?format=excel&date_range=last_month
```

### Portfolio Report
```
GET /dashboard/reports/portfolio/?format=pdf&group_by=contract_type
```

---

## 🎯 Sample Filter Queries

### Filter Contracts by Status
```
GET /contracts/?status=completed&page=1&page_size=20
```

### Filter by Risk Score
```
GET /contracts/?risk_score_min=70&risk_score_max=100
```

### Filter by Date Range
```
GET /contracts/?created_after=2024-01-01&created_before=2024-12-31
```

### Search Contracts
```
GET /contracts/?search=vendor&ordering=-risk_score
```

### Filter Alerts
```
GET /alerts/?status=active&severity=high&alert_type=risk_threshold
```

---

## 🔄 Sample Workflow Scenarios

### Scenario 1: Vendor Onboarding
1. Create counterparty (vendor)
2. Upload vendor agreement
3. Wait for analysis
4. Review risks via chat
5. Create alert rule for this vendor
6. Export to ERP

### Scenario 2: Contract Renewal
1. Search for expiring contracts
2. Create alert rule (90 days before expiry)
3. Review contract via chat
4. Generate comparison with old version
5. Upload new agreement
6. Archive old version

### Scenario 3: Bulk Migration
1. Batch upload 10+ contracts
2. Monitor dashboard for processing
3. Create alert rules for all
4. Generate portfolio report
5. Export to Word for review

---

## 📝 Sample Comments

### For Contract Review
```json
{
  "content": "Please review clause 5.2 - liability cap seems too low. @jane.manager",
  "clause_id": "clause-uuid",
  "page_number": 12
}
```

### For Approval Request
```json
{
  "content": "Contract reviewed. Requesting final approval from legal team. @legal.team",
  "page_number": null
}
```

---

## 🧪 Test Sequences

### Quick Test (5 minutes)
1. Register → Login → Upload → Check Status → Chat

### Full Test (15 minutes)
1. Register → Login
2. Create Users → Upload Contract
3. Create Chat → Ask 5 Questions
4. Create Alert Rule → Check Alerts
5. View Dashboard → Generate Report

### Production Simulation (30 minutes)
1. Complete Multi-Tenant Setup
2. Upload 5+ Contracts
3. Create Multiple Alert Rules
4. Test All Integrations
5. Generate All Reports
6. Test Collaboration Features

---

## 📞 Quick Reference

### Required Headers
```
Authorization: Bearer {{access_token}}
X-Tenant-ID: {{tenant_id}}
Content-Type: application/json
```

### Environment Variables Needed
- `base_url`
- `access_token`
- `tenant_id`
- `contract_id`
- `session_id`
- `alert_id`

---

**Copy and paste these directly into Postman for quick testing!** 🚀


