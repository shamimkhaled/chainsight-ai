# ChainSight API - Request & Response Formats

## System Architechture - All
Click to [overview](system_architecture_diagram.html)

## 📡 API Base URL
```
Production: https://chainsightai.com/api/v1/
Development: http://localhost:8000/api/v1/
```

## 🔐 Authentication
Currently, the API uses **IP-based rate limiting** without authentication tokens. All endpoints are publicly accessible but limited to 5 requests per IP per day.

---

## 1. 📄 Contract Analysis Endpoint

### **POST** `/api/v1/contracts/`
Upload and analyze a contract document with AI-powered analysis.

#### Request Format
**Content-Type:** `multipart/form-data`

**Form Fields:**
```javascript
{
  file: File,           // Required: Contract document
  industry: string,     // Required: Industry type
 
}
```

**Field Details:**
- **file**: Contract document file
  - **Supported formats**: PDF, DOCX, TXT, JPG, JPEG, PNG
  - **Max size**: 10MB
  - **Processing limit**: 100MB (for large PDFs with OCR)

- **industry**: Industry-specific analysis type
  - **Values**: `"garment"`, `"it"`, `"construction"`, `"general"`
  - **Required**: Yes

- **language**: Document language for analysis
  - **Values**: `"english"`, `"bengali"`
  - **Default**: `"english"`

#### Example Request (JavaScript/Fetch)
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('industry', 'it');
formData.append('language', 'english');

const response = await fetch('/api/v1/contracts/', {
    method: 'POST',
    body: formData
});

const result = await response.json();
```

#### Example Request (cURL)
```bash
curl -X POST \
  http://localhost:8000/api/v1/contracts/ \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@contract.pdf' \
  -F 'industry=it' \
  -F 'language=english'
```

#### Example Request (Python)
```python
import requests

url = "http://localhost:8000/api/v1/contracts/"
files = {'file': open('contract.pdf', 'rb')}
data = {
    'industry': 'it',
    'language': 'english'
}

response = requests.post(url, files=files, data=data)
result = response.json()
```

#### Success Response (201 Created)
```json
{
  "id": "7127a097-26d8-45b6-978b-73def227ef3b",
  "original_filename": "sample-contract.pdf",
  "file_size": 235826,
  "industry": "it",
  "language": "english",
  "status": "completed",
  "risk_score": 7,
  "analysis_result": {
    "document_analysis": {
      "industry": "it",
      "language": "english",
      "analysis_date": "2025-07-25",
      "overall_risk_score": 7,
      "executive_summary": {
        "critical_issues_count": 3,
        "missing_clauses_count": 2,
        "priority_level": "High"
      },
      "risk_assessment": [
        {
          "category": "Legal",
          "severity": "High",
          "description": "Missing comprehensive data protection clause",
          "potential_impact": "GDPR compliance violations, data breach liability",
          "likelihood": "Medium"
        },
        {
          "category": "Financial",
          "severity": "Medium",
          "description": "Unclear payment terms and penalty structure",
          "potential_impact": "Payment disputes, cash flow issues",
          "likelihood": "High"
        }
      ],
      "missing_critical_clauses": [
        {
          "clause_name": "Data Protection and Privacy",
          "importance": "Critical",
          "reason": "Essential for IT contracts handling personal data",
          "suggested_text": "The Service Provider shall comply with all applicable data protection laws..."
        },
        {
          "clause_name": "Intellectual Property Rights",
          "importance": "Critical",
          "reason": "Protects custom software development and IP ownership",
          "suggested_text": "All intellectual property developed under this agreement..."
        }
      ],
      "identified_risks": [
        {
          "risk_type": "Data breach liability",
          "severity": "High",
          "current_protection": "Basic confidentiality clause",
          "mitigation_suggestion": "Add comprehensive data protection and breach notification procedures"
        },
        {
          "risk_type": "IP ownership disputes",
          "severity": "Medium",
          "current_protection": "General work product clause",
          "mitigation_suggestion": "Specify detailed IP ownership and licensing terms"
        }
      ],
      "improvement_recommendations": [
        {
          "priority": 1,
          "category": "Addition",
          "description": "Add comprehensive data protection clause",
          "justification": "Critical for IT contracts in current regulatory environment",
          "suggested_implementation": "Insert new section after general obligations"
        },
        {
          "priority": 2,
          "category": "Modification",
          "description": "Clarify intellectual property ownership terms",
          "justification": "Prevents disputes over custom development work",
          "suggested_implementation": "Expand existing IP section with detailed provisions"
        }
      ],
      "compliance_check": {
        "industry_standards": "partial",
        "regulatory_requirements": "The contract lacks specific GDPR and data protection compliance measures required for IT services.",
        "best_practices": "Partially adheres to IT industry best practices but requires additional security and IP protection clauses."
      }
    }
  },
  "error_message": "",
  "created_at": "2025-07-25T10:30:00.000Z",
  "updated_at": "2025-07-25T10:30:45.500Z",
  "processing_time": 45.5,
  "file_url": "/media/contracts/2025/07/25/sample-contract.pdf",
  "is_scanned_pdf": false,
  "ocr_method_used": "standard"
}
```

#### Error Responses

**Rate Limit Exceeded (429)**
```json
{
  "error": "Rate limit exceeded",
  "message": "You have reached the daily limit of 5 document analyses. Current count: 5/5. Please try again tomorrow.",
  "retry_after": 86400
}
```

**File Validation Error (400)**
```json
{
  "error": "Invalid input",
  "details": {
    "file": ["File size must not exceed 10MB."],
    "industry": ["Invalid industry. Must be one of: garment, it, construction, general"]
  }
}
```

**Processing Error (500)**
```json
{
  "error": "Document processing failed",
  "message": "OCR extraction failed: timeout"
}
```

---

## 2. 📋 Get Analysis Result

### **GET** `/api/v1/contracts/{id}/`
Retrieve a specific contract analysis by ID.

#### Request Format
**URL Parameters:**
- `id`: UUID of the contract analysis

#### Example Request
```bash
GET /api/v1/contracts/7127a097-26d8-45b6-978b-73def227ef3b/
```

#### Success Response (200 OK)
```json
{
  "id": "7127a097-26d8-45b6-978b-73def227ef3b",
  "original_filename": "sample-contract.pdf",
  "file_size": 235826,
  "industry": "it",
  "language": "english",
  "status": "completed",
  "risk_score": 7,
  "analysis_result": {
    // Full analysis object (same as POST response)
  },
  "error_message": "",
  "created_at": "2025-07-25T10:30:00.000Z",
  "updated_at": "2025-07-25T10:30:45.500Z",
  "processing_time": 45.5,
  "file_url": "/media/contracts/2025/07/25/sample-contract.pdf",
  "is_scanned_pdf": false,
  "ocr_method_used": "standard"
}
```

#### Error Response (404)
```json
{
  "detail": "Not found."
}
```

---

## 3. 📊 List All Analyses

### **GET** `/api/v1/contracts/`
List all contract analyses with pagination.

#### Query Parameters
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

#### Example Request
```bash
GET /api/v1/contracts/?page=1&page_size=10
```

#### Success Response (200 OK)
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/v1/contracts/?page=2",
  "previous": null,
  "results": [
    {
      "id": "7127a097-26d8-45b6-978b-73def227ef3b",
      "original_filename": "sample-contract.pdf",
      "industry": "it",
      "language": "english",
      "status": "completed",
      "risk_score": 7,
      "created_at": "2025-07-25T10:30:00.000Z"
    },
    {
      "id": "8238b108-37e9-56c7-a89c-84eff338f0c4",
      "original_filename": "construction-agreement.docx",
      "industry": "construction",
      "language": "english",
      "status": "completed",
      "risk_score": 5,
      "created_at": "2025-07-25T09:15:00.000Z"
    }
  ]
}
```

---

## 4. 🏥 Health Check

### **GET** `/api/v1/health/`
Check API health status.

#### Success Response (200 OK)
```json
{
  "status": "healthy",
  "timestamp": "2025-07-25T10:30:00.000Z",
  "version": "1.0.0"
}
```

---

## 5. 🚦 Rate Limit Status

### **GET** `/api/v1/rate-limit/`
Check current rate limit status for your IP.

#### Success Response (200 OK)
```json
{
  "ip_address": "192.168.1.100",
  "daily_limit": 5,
  "current_count": 3,
  "remaining": 2,
  "can_proceed": true,
  "reset_time": "2025-07-26T00:00:00.000Z"
}
```

---

## 📝 Analysis Result Structure

### Executive Summary
```json
"executive_summary": {
  "critical_issues_count": 3,      // Number of high-severity issues
  "missing_clauses_count": 2,      // Number of missing critical clauses
  "priority_level": "High"         // Overall priority: High/Medium/Low
}
```

### Risk Assessment Array
```json
"risk_assessment": [
  {
    "category": "Legal|Financial|Operational",
    "severity": "High|Medium|Low",
    "description": "Detailed risk description",
    "potential_impact": "What could happen",
    "likelihood": "High|Medium|Low"
  }
]
```

### Missing Critical Clauses
```json
"missing_critical_clauses": [
  {
    "clause_name": "Name of missing clause",
    "importance": "Critical|Important|Recommended",
    "reason": "Why this clause is needed",
    "suggested_text": "Sample clause text to add"
  }
]
```

### Improvement Recommendations
```json
"improvement_recommendations": [
  {
    "priority": 1,                           // 1=highest, 3=lowest
    "category": "Addition|Modification|Clarification",
    "description": "What needs to be changed",
    "justification": "Why this change is needed",
    "suggested_implementation": "How to implement"
  }
]
```

### Compliance Check
```json
"compliance_check": {
  "industry_standards": "compliant|non-compliant|partial",
  "regulatory_requirements": "Detailed compliance analysis",
  "best_practices": "Industry best practices assessment"
}
```

---

## 🏭 Industry-Specific Analysis

### Garment Industry Focus
- Quality standards and specifications
- Supply chain risk assessment
- Labor compliance requirements
- Environmental regulations
- Delivery timelines and penalties

### IT Industry Focus
- Data protection and privacy (GDPR compliance)
- Intellectual property rights
- Software licensing terms
- Service level agreements (SLAs)
- Cybersecurity requirements

### Construction Industry Focus
- Safety regulations and protocols
- Milestone payment schedules
- Material quality standards
- Weather and delay provisions
- Insurance and bonding requirements

### General Contracts
- Standard legal clause analysis
- Governing law and jurisdiction
- Dispute resolution mechanisms
- Force majeure provisions
- General risk assessment

---

## 🔄 Status Values

- **`pending`**: Analysis request received, queued for processing
- **`processing`**: Document being processed and analyzed
- **`completed`**: Analysis finished successfully
- **`failed`**: Analysis failed due to error

---

## ⏱️ Processing Times

- **Simple text documents**: 5-15 seconds
- **Searchable PDFs**: 10-30 seconds  
- **Scanned PDFs (OCR)**: 30-120 seconds
- **Large documents**: May take up to 5 minutes

---

## 🚨 Error Handling

All API errors follow this format:
```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "details": {
    // Additional error details if applicable
  }
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `201`: Created successfully
- `400`: Bad request (validation error)
- `404`: Resource not found
- `429`: Rate limit exceeded
- `500`: Internal server error