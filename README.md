# ChainSight Contract AI Intelligence Analyst - Django REST API

AI-powered contract analysis API with GPT-4.1 and OCR support for scanned documents.

## Features

- 🔍 **Smart Document Processing**: Automatically detects scanned vs searchable PDFs
- 🤖 **AI-Powered Analysis**: Uses OpenAI model GPT-4.1 for comprehensive contract analysis
- 🏭 **Industry-Specific**: Tailored analysis for Garment, IT, General, and Construction industries
- 📊 **Structured Output**: Detailed JSON responses with risk scores and recommendations
- 🚦 **Rate Limiting**: 5 documents per day per IP address
- 🔒 **Secure**: Built-in security features and validation
- 📚 **API Documentation**: Auto-generated Swagger/OpenAPI docs

## Supported File Types

- PDF (searchable and scanned/image-based)
- DOCX (Word documents)
- TXT (Text files)
- JPG/JPEG/PNG (Images with text)

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd chainsight_api

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings
```

### 2. Environment Variables

Create a `.env` file with:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
OPENAI_API_KEY=your-openai-api-key
DB_NAME=chainsight_db
DB_USER=chainsight_user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
```

### 3. Database Setup

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE chainsight_db;
CREATE USER chainsight_user WITH PASSWORD 'your-db-password';
GRANT ALL PRIVILEGES ON DATABASE chainsight_db TO chainsight_user;
\q

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

### 4. Install System Dependencies (for OCR)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
sudo apt install poppler-utils

# macOS
brew install tesseract
brew install poppler
```

### 5. Start the Server

```bash
# Development server
python manage.py runserver

# Production with Gunicorn
gunicorn chainsight_api.wsgi:application --bind 0.0.0.0:8000
```

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1/
```

### Main Endpoints

1. **Upload & Analyze Contract**
   ```
   POST /api/v1/contracts/
   ```

2. **Get Analysis Result**
   ```
   GET /api/v1/contracts/{analysis_id}/
   ```

3. **List All Analyses**
   ```
   GET /api/v1/contracts/
   ```

4. **Health Check**
   ```
   GET /api/v1/health/
   ```

5. **Rate Limit Status**
   ```
   GET /api/v1/rate-limit/
   ```

## API Documentation

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

## Usage Examples

### Upload a Contract for Analysis

```python
import requests

url = "http://localhost:8000/api/v1/contracts/"

files = {
    'file': open('contract.pdf', 'rb')
}

data = {
    'industry': 'it',
    'language': 'english'
}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"Analysis ID: {result['id']}")
print(f"Status: {result['status']}")
print(f"Risk Score: {result['risk_score']}/10")
```

### Using cURL

```bash
curl -X POST \
  http://localhost:8000/api/v1/contracts/ \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@contract.pdf' \
  -F 'industry=it' \
  -F 'language=english'
```

### JavaScript/Fetch Example

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('industry', 'it');
formData.append('language', 'english');

fetch('http://localhost:8000/api/v1/contracts/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## Response Format

```json

{
  "id": "7127a097-26d8-45b6-978b-73def227ef3b",
  "original_filename": "annex-beechwoodmsbkyssamplecontract.pdf",
  "file_size": 235826,
  "industry": "general",
  "language": "english",
  "status": "completed",
  "risk_score": 7,
  "analysis_result": {
    "document_analysis": {
      "industry": "general",
      "language": "english",
      "analysis_date": "2025-07-24",
      "overall_risk_score": 7,
      "executive_summary": {
        "critical_issues_count": 5,
        "missing_clauses_count": 3,
        "priority_level": "High"
      },
      "risk_assessment": [
        {
          "category": "Legal",
          "severity": "High",
          "description": "The contract lacks a clear Governing Law and Jurisdiction clause, leaving uncertainty as to which legal system will apply in the event of a dispute.",
          "potential_impact": "Difficulty in enforcing contractual rights, increased litigation costs, and potential forum shopping.",
          "likelihood": "High"
        },
        {
          "category": "Legal",
          "severity": "Medium",
          "description": "Absence of a comprehensive Confidentiality clause exposes sensitive information to potential unauthorized disclosure.",
          "potential_impact": "Loss of sensitive data, reputational damage, and potential regulatory penalties.",
          "likelihood": "Medium"
        },
        {
          "category": "Financial",
          "severity": "Medium",
          "description": "Payment terms are outlined but lack specificity regarding late payments, penalties, and dispute over commission rates.",
          "potential_impact": "Delayed payments, disputes over amounts owed, and cash flow issues.",
          "likelihood": "Medium"
        },
        {
          "category": "Operational",
          "severity": "High",
          "description": "The contract involves cross-border money transfers in high-risk regions, with potential exposure to anti-money laundering (AML) and counter-terrorism financing (CTF) violations.",
          "potential_impact": "Legal sanctions, loss of license, and reputational harm.",
          "likelihood": "High"
        },
        {
          "category": "Legal",
          "severity": "Medium",
          "description": "No clear indemnification or liability allocation provisions.",
          "potential_impact": "Unclear responsibility for losses, damages, or third-party claims.",
          "likelihood": "Medium"
        }
      ],
      "missing_critical_clauses": [
        {
          "clause_name": "Governing Law and Jurisdiction",
          "importance": "Critical",
          "reason": "Determines which country's laws apply and where disputes will be resolved.",
          "suggested_text": "This Agreement shall be governed by and construed in accordance with the laws of [insert jurisdiction]. Any disputes arising out of or in connection with this Agreement shall be subject to the exclusive jurisdiction of the courts of [insert jurisdiction]."
        },
        {
          "clause_name": "Confidentiality Obligations",
          "importance": "Critical",
          "reason": "Protects sensitive information exchanged between the parties.",
          "suggested_text": "Each party agrees to keep confidential all information received from the other party in connection with this Agreement and not to disclose such information to any third party without prior written consent, except as required by law."
        },
        {
          "clause_name": "Indemnification Provisions",
          "importance": "Critical",
          "reason": "Clarifies responsibility for losses or damages arising from breaches or third-party claims.",
          "suggested_text": "Each party shall indemnify and hold harmless the other party from and against any and all claims, damages, losses, and expenses arising out of or resulting from any breach of this Agreement or the negligence or willful misconduct of the indemnifying party."
        }
      ],
      "identified_risks": [
        {
          "risk_type": "Breach of contract",
          "severity": "Medium",
          "current_protection": "General obligations and notice requirements for termination.",
          "mitigation_suggestion": "Add detailed breach and remedy provisions, including cure periods and consequences."
        },
        {
          "risk_type": "Dispute over terms and conditions",
          "severity": "High",
          "current_protection": "Basic dispute resolution clause (consultation and mediation).",
          "mitigation_suggestion": "Include escalation procedures and specify governing law and jurisdiction."
        },
        {
          "risk_type": "Non-compliance with regulations (AML/CTF)",
          "severity": "High",
          "current_protection": "Reference to due diligence and risk assessment, but lacks detailed compliance obligations.",
          "mitigation_suggestion": "Incorporate explicit compliance representations and warranties, and audit rights."
        },
        {
          "risk_type": "Financial instability of parties",
          "severity": "Medium",
          "current_protection": "Requirement for bank guarantees or bonds in some cases.",
          "mitigation_suggestion": "Add financial reporting and solvency representations, and right to request additional security."
        },
        {
          "risk_type": "Market volatility affecting terms (exchange rates)",
          "severity": "Medium",
          "current_protection": "Exchange rate provisions, with some flexibility for revision.",
          "mitigation_suggestion": "Define a clear mechanism for exchange rate determination and dispute resolution."
        }
      ],
      "improvement_recommendations": [
        {
          "priority": 1,
          "category": "Addition",
          "description": "Insert a comprehensive Governing Law and Jurisdiction clause.",
          "justification": "Essential for legal certainty and enforceability of the contract.",
          "suggested_implementation": "Add as a new article or section at the end of the contract."
        },
        {
          "priority": 1,
          "category": "Addition",
          "description": "Add a Confidentiality clause covering all information exchanged under the agreement.",
          "justification": "Protects both parties from unauthorized disclosure of sensitive data.",
          "suggested_implementation": "Insert as a new article before or after the obligations section."
        },
        {
          "priority": 2,
          "category": "Addition",
          "description": "Include an Indemnification clause specifying liability for breaches and third-party claims.",
          "justification": "Clarifies risk allocation and protects parties from unforeseen liabilities.",
          "suggested_implementation": "Add as a new article after the modification and cancellation section."
        },
        {
          "priority": 2,
          "category": "Modification",
          "description": "Clarify payment terms, including timelines, penalties for late payment, and dispute mechanisms.",
          "justification": "Reduces risk of payment disputes and cash flow interruptions.",
          "suggested_implementation": "Expand Article 2 and 3 to include detailed payment provisions."
        },
        {
          "priority": 3,
          "category": "Addition",
          "description": "Add a Force Majeure clause.",
          "justification": "Protects parties from liability for events beyond their control.",
          "suggested_implementation": "Insert as a new article before or after the duration section."
        }
      ],
      "compliance_check": {
        "industry_standards": "partial",
        "regulatory_requirements": "The contract references due diligence and risk assessment for AML/CTF, but lacks explicit compliance clauses and audit rights. It is not fully compliant with international standards for cross-border financial transactions.",
        "best_practices": "The contract partially adheres to best practices by outlining obligations and some risk mitigation steps, but falls short on legal certainty, confidentiality, and indemnification. Inclusion of missing critical clauses is necessary for full alignment with industry best practices."
      }
    }
  },
  "error_message": "",
  "created_at": "2025-07-24T18:05:07.715526Z",
  "updated_at": "2025-07-24T18:05:37.761751Z",
  "processing_time": 28.761296,
  "file_url": "/media/contracts/2025/07/24/annex-beechwoodmsbkyssamplecontract.pdf",
  "is_scanned_pdf": false,
  "ocr_method_used": "standard"
}
      
```

## Rate Limiting

- **Daily Limit**: 5 documents per IP address
- **Reset Time**: Midnight UTC each day
- **Status Endpoint**: Check your current usage at `/api/v1/rate-limit/`

## Industries Supported

1. **Garment**: Quality standards, labor compliance, supply chain risks
2. **IT**: Data protection, IP rights, service level agreements
3. **Construction**: Safety protocols, milestone payments, regulatory compliance
4. **General**: For Miscellaneous or Mixed Contracts

## Error Handling

The API returns structured error responses:

```json
{
    "error": "Rate limit exceeded",
    "message": "You have reached the daily limit of 5 document analyses.",
    "retry_after": 86400
}
```