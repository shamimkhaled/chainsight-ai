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
    "id": "uuid-here",
    "original_filename": "contract.pdf",
    "file_size": 1024000,
    "industry": "it",
    "language": "english",
    "status": "completed",
    "risk_score": 7,
    "analysis_result": {
        "document_analysis": {
            "industry": "it",
            "language": "English",
            "analysis_date": "2025-07-21",
            "overall_risk_score": 7,
            "executive_summary": {
                "critical_issues_count": 5,
                "missing_clauses_count": 4,
                "priority_level": "High"
            },
            "risk_assessment": [...],
            "missing_critical_clauses": [...],
            "identified_risks": [...],
            "improvement_recommendations": [...],
            "compliance_check": {...}
        }
    },
    "created_at": "2025-07-21T10:00:00Z",
    "updated_at": "2025-07-21T10:02:00Z",
    "processing_time": 45.2,
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