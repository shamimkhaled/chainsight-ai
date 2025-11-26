# ChainSight AI - Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will get your ChainSight AI backend up and running quickly.

---

## Prerequisites

- Python 3.12+ installed
- Virtual environment activated
- Database migrations completed

---

## Step 1: Create Superuser (If Not Done)

```bash
cd /home/shamimkhaled/ChainSightAI
source venv/bin/activate
python manage.py createsuperuser --settings=config.settings.development
```

**Enter these details:**
- Email: `admin@chainsight.ai`
- Password: `AdminPass123!` (or your secure password)

---

## Step 2: Start the Server

```bash
python manage.py runserver --settings=config.settings.development
```

✅ Server running at: **http://127.0.0.1:8000**

---

## Step 3: Test the API

### Option A: Using Browser

1. **API Documentation**: http://127.0.0.1:8000/api/docs/
2. **Health Check**: http://127.0.0.1:8000/api/health/
3. **API Info**: http://127.0.0.1:8000/api/health/info/

### Option B: Using cURL

```bash
# 1. Login
curl -X POST http://127.0.0.1:8000/api/v2/users/login/ \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: 1" \
  -d '{"email":"admin@chainsight.ai","password":"AdminPass123!"}'
```

**Copy the `access` token from response**

```bash
# 2. Get Dashboard Stats (replace <token> with actual token)
curl -X GET http://127.0.0.1:8000/api/v2/dashboard/ \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: 1"
```

---

## Step 4: (Optional) Start Celery Workers

For full AI analysis features, start Celery workers in separate terminals:

```bash
# Terminal 2: Celery Worker
cd /home/shamimkhaled/ChainSightAI
source venv/bin/activate
celery -A config worker -l info
```

```bash
# Terminal 3: Celery Beat (Scheduled Tasks)
cd /home/shamimkhaled/ChainSightAI
source venv/bin/activate
celery -A config beat -l info
```

---

## Available Endpoints

### 🔐 Authentication
- `POST /api/v2/users/login/` - Login
- `POST /api/v2/users/register/` - Register
- `GET /api/v2/users/me/` - Get current user

### 📄 Contracts
- `POST /api/v2/contracts/upload/` - Upload contract
- `GET /api/v2/contracts/` - List contracts
- `GET /api/v2/contracts/{id}/` - Get contract details
- `GET /api/v2/contracts/{id}/results/` - Get analysis

### 📊 Dashboard
- `GET /api/v2/dashboard/` - Get statistics
- `GET /api/v2/dashboard/trends/` - Get trends
- `GET /api/v2/dashboard/risk-distribution/` - Get risk data

### 🏢 Counterparties
- `GET /api/v2/counterparties/` - List counterparties
- `POST /api/v2/counterparties/` - Create counterparty

### 🏥 Health
- `GET /api/health/` - Health check
- `GET /api/health/ready/` - Readiness check

**See `API_ENDPOINTS_SUMMARY.md` for complete list**

---

## Frontend Integration

### Step 1: Create Frontend Project

```bash
npx create-next-app@latest chainsight-frontend --typescript
cd chainsight-frontend
npm install axios
```

### Step 2: Create API Client

Create `src/api/axiosConfig.ts`:

```typescript
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000/api/v2';

const axiosInstance = axios.create({
  baseURL: API_BASE,
});

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  config.headers['X-Tenant-ID'] = '1';
  return config;
});

export default axiosInstance;
```

### Step 3: Create Login Page

Create `src/pages/login.tsx`:

```typescript
import { useState } from 'react';
import axios from '../api/axiosConfig';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post('/users/login/', {
        email,
        password,
      });
      localStorage.setItem('access_token', response.data.tokens.access);
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

**See `FRONTEND_INTEGRATION_GUIDE.md` for complete examples**

---

## Testing Workflow

### 1. Register a User

```bash
curl -X POST http://127.0.0.1:8000/api/v2/users/register/ \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: 1" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "first_name": "Test",
    "last_name": "User",
    "role": "user"
  }'
```

### 2. Upload a Contract

```bash
curl -X POST http://127.0.0.1:8000/api/v2/contracts/upload/ \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: 1" \
  -F "file=@sample_contract.pdf" \
  -F "industry=technology" \
  -F "language=english"
```

### 3. Check Contract Status

```bash
curl -X GET http://127.0.0.1:8000/api/v2/contracts/<contract_id>/ \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: 1"
```

### 4. Get Dashboard Stats

```bash
curl -X GET http://127.0.0.1:8000/api/v2/dashboard/ \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: 1"
```

---

## Common Commands

```bash
# Start server
python manage.py runserver --settings=config.settings.development

# Create migrations
python manage.py makemigrations --settings=config.settings.development

# Apply migrations
python manage.py migrate --settings=config.settings.development

# Create superuser
python manage.py createsuperuser --settings=config.settings.development

# Run tests
python manage.py test --settings=config.settings.testing

# Start Celery worker
celery -A config worker -l info

# Start Celery beat
celery -A config beat -l info

# Check for issues
python manage.py check --settings=config.settings.development
```

---

## Directory Structure

```
ChainSightAI/
├── apps/                   # Django apps
│   ├── accounts/          # Users, auth, waitlist
│   ├── contracts/         # Contract management
│   ├── counterparties/    # Entity management
│   ├── tenants/           # Multi-tenancy
│   ├── dashboard/         # Analytics
│   └── core/              # Base functionality
├── config/                 # Settings
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   └── urls.py
├── tests/                  # Test cases
├── venv/                   # Virtual environment
├── manage.py              # Django CLI
└── *.md                   # Documentation files
```

---

## Documentation Files

| File | Description |
|------|-------------|
| `README.md` | Project overview |
| `QUICK_START.md` | This file - Get started fast |
| `API_ENDPOINTS_SUMMARY.md` | Complete API reference |
| `FRONTEND_INTEGRATION_GUIDE.md` | Frontend integration (TypeScript) |
| `POSTMAN_TESTING_GUIDE.md` | API testing with Postman |
| `COMPREHENSIVE_GUIDE.md` | Deep dive into architecture |
| `BACKEND_COMPLETE_SUMMARY.md` | Completion status |
| `DB.md` | Database architecture |
| `MULTI-TENANCY.md` | Multi-tenancy explained |

---

## Troubleshooting

### Issue: Server won't start

**Check:**
1. Virtual environment activated?
2. Dependencies installed? `pip install -r requirements.txt`
3. Migrations applied? `python manage.py migrate`

### Issue: Can't create superuser

**Solution:**
```bash
python manage.py migrate --settings=config.settings.development
python manage.py createsuperuser --settings=config.settings.development
```

### Issue: 401 Unauthorized

**Check:**
1. Token format: `Bearer <token>` (with space)
2. Token not expired (15 min lifetime)
3. Use refresh token to get new access token

### Issue: CORS errors from frontend

**Solution:** Add your frontend URL to `config/settings/base.py`:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Add your frontend URL
]
```

---

## Environment Variables

Create `.env` file in project root:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.sqlite3

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=your-openai-key

# AWS (optional for development)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
```

---

## Next Steps

1. ✅ **Backend is running** - You're here!
2. **Frontend Setup** - See `FRONTEND_INTEGRATION_GUIDE.md`
3. **API Testing** - Use Postman or cURL
4. **Build Features** - Start with login/dashboard
5. **Deploy** - When ready for production

---

## Need Help?

- **API Docs**: http://127.0.0.1:8000/api/docs/
- **Health Check**: http://127.0.0.1:8000/api/health/
- **Complete Guide**: See `BACKEND_COMPLETE_SUMMARY.md`
- **Frontend Guide**: See `FRONTEND_INTEGRATION_GUIDE.md`

---

**🎉 You're all set! Start building your frontend or test the API!**

---

**Last Updated**: November 26, 2025  
**Version**: 2.0.0

