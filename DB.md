# ChainSight AI Database Architecture & ORM Guide

## Overview 🎯
ChainSight AI uses Django ORM with PostgreSQL as the primary database, MongoDB for document storage, and Redis for caching. This guide explains the complete database setup, ORM usage, and deployment strategies.

## Database Architecture 🏗️

### 1. **Primary Database: PostgreSQL**
- **Purpose**: Structured data, relationships, user management
- **ORM**: Django ORM (Object-Relational Mapping)
- **Features**: ACID compliance, complex queries, transactions

### 2. **Document Database: MongoDB**
- **Purpose**: Contract analysis results, unstructured data
- **Usage**: Store AI analysis results, document metadata
- **Integration**: Direct Python driver (no ORM)

### 3. **Cache Database: Redis**
- **Purpose**: Session storage, caching, Celery broker
- **Usage**: Fast data access, background job queuing

## Django ORM vs Raw SQL 📊

### When to Use Django ORM ✅
```python
# ✅ GOOD: Complex relationships, CRUD operations
contracts = Contract.objects.filter(
    tenant=request.tenant,
    status='completed'
).select_related('uploaded_by').order_by('-created_at')

# ✅ GOOD: Simple queries with filtering
user = User.objects.get(email='user@example.com')

# ✅ GOOD: Bulk operations
Contract.objects.filter(status='pending').update(status='processing')
```

### When to Use Raw SQL ⚡
```python
# ⚡ GOOD: Complex analytics queries
from django.db import connection

def get_contract_analytics(tenant_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                DATE_TRUNC('month', created_at) as month,
                COUNT(*) as contracts,
                AVG(risk_score) as avg_risk
            FROM contracts_contract
            WHERE tenant_id = %s
            GROUP BY DATE_TRUNC('month', created_at)
            ORDER BY month DESC
        """, [tenant_id])
        return cursor.fetchall()

# ⚡ GOOD: Performance-critical operations
def bulk_update_contract_statuses(contract_ids, new_status):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE contracts_contract
            SET status = %s, updated_at = NOW()
            WHERE id = ANY(%s)
        """, [new_status, contract_ids])
```

## Database Models & Relationships 🔗

### Core Models Structure

#### 1. **Tenant Model** (Multi-tenancy foundation)
```python
class Tenant(TimeStampedModel):
    """
    Multi-tenant organization model
    """
    name = models.CharField(max_length=200)
    subdomain = models.CharField(max_length=100, unique=True, db_index=True)

    # Plan & limits
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    max_users = models.IntegerField(default=10)
    max_contracts = models.IntegerField(default=1000)
    max_storage_gb = models.IntegerField(default=100)

    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)

    # Billing
    billing_email = models.EmailField(blank=True)
    billing_info = models.JSONField(default=dict, blank=True)

    # Settings
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'tenants'
        ordering = ['name']
        indexes = [
            models.Index(fields=['subdomain']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.name

    def get_rate_limits(self):
        """Get rate limits for tenant's plan"""
        from django.conf import settings
        return settings.RATE_LIMITS.get(self.plan_type, settings.RATE_LIMITS['free'])
```

#### 2. **User Model** (Authentication & tenant relationship)
```python
class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Custom user model
    """
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='users'
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=50, blank=True)

    # Role & permissions
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('user', 'User'),
        ('viewer', 'Viewer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    # Status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    # Security
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=100, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        unique_together = ['tenant', 'email']
        indexes = [
            models.Index(fields=['tenant', 'email']),
            models.Index(fields=['tenant', 'role']),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
```

#### 3. **Contract Model** (Main business entity)
```python
class Contract(TimeStampedModel):
    """
    Contract document model
    """
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='contracts'
    )
    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='uploaded_contracts'
    )

    # File information
    original_filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=100)
    file_hash = models.CharField(max_length=128, unique=True)

    # Processing status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processing_stage = models.CharField(max_length=100, blank=True)
    progress_percentage = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)

    # Contract metadata
    contract_type = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100)
    language = models.CharField(max_length=50, default='english')
    contract_date = models.DateField(null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    contract_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')

    # Counterparties (JSON field for flexibility)
    counterparties = models.JSONField(default=list, blank=True)

    # Analysis results
    risk_score = models.IntegerField(null=True, blank=True)
    compliance_score = models.IntegerField(null=True, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)

    # OCR and scanning
    is_scanned_pdf = models.BooleanField(default=False)
    ocr_method_used = models.CharField(max_length=50, blank=True)

    # Organization
    folder_path = models.CharField(max_length=500, blank=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    # Analysis metadata
    analyzed_at = models.DateTimeField(null=True, blank=True)
    processing_time = models.IntegerField(null=True, blank=True)  # seconds

    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'contracts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'uploaded_by']),
            models.Index(fields=['tenant', 'risk_score']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.original_filename} ({self.tenant.name})"

    def save(self, *args, **kwargs):
        # Auto-generate folder path if not set
        if not self.folder_path:
            self.folder_path = f"tenant_{self.tenant.id}/contracts/{self.created_at.year}/{self.created_at.month}/"
        super().save(*args, **kwargs)
```

## Database Setup & Migration 🛠️

### 1. **Local Development Setup**
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE chainsight_db;
CREATE USER chainsight_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE chainsight_db TO chainsight_user;

# Install Redis
sudo apt-get install redis-server

# Install MongoDB (optional for development)
# wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
# echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
# sudo apt-get update
# sudo apt-get install -y mongodb-org
```

### 2. **Django Database Configuration**
```python
# config/settings/base.py
if env('DB_ENGINE', default='django.db.backends.postgresql') == 'django.db.backends.sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST'),
            'PORT': env('DB_PORT', default='5432'),
            'ATOMIC_REQUESTS': True,
            'CONN_MAX_AGE': 600,
            'OPTIONS': {
                'connect_timeout': 10,
                'sslmode': 'require',
            },
        }
    }
```

### 3. **Environment Variables**
```bash
# .env file
DB_ENGINE=django.db.backends.postgresql
DB_NAME=chainsight_db
DB_USER=chainsight_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=chainsight
```

### 4. **Running Migrations**
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Deployment: DigitalOcean App Platform 🌊

### 1. **Database Setup**
```yaml
# .do/app.yaml
databases:
  - name: chainsight-db
    engine: PG
    version: "15"
    size: professional-xs
    num_nodes: 1

  - name: chainsight-redis
    engine: REDIS
    version: "7"
    size: professional-xs
    num_nodes: 1
```

### 2. **App Configuration**
```yaml
# .do/app.yaml
name: chainsight-ai
services:
  - name: web
    source_dir: /
    github:
      repo: yourusername/chainsight-ai
      branch: main
    run_command: |
      python manage.py migrate --settings=config.settings.production
      python manage.py collectstatic --noinput --settings=config.settings.production
      gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
    environment_slug: python
    instance_count: 1
    instance_size_slug: professional-xs
    envs:
      - key: DJANGO_SETTINGS_MODULE
        value: config.settings.production
      - key: SECRET_KEY
        type: SECRET
        value: your-secret-key
      - key: DB_NAME
        value: ${chainsight-db.DATABASE_URL}
      - key: REDIS_URL
        value: ${chainsight-redis.REDIS_URL}
      - key: AWS_ACCESS_KEY_ID
        type: SECRET
      - key: AWS_SECRET_ACCESS_KEY
        type: SECRET
```

### 3. **Production Settings**
```python
# config/settings/production.py
from .base import *

DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['your-app-name.ondigitalocean.app'])

# Database
DATABASES['default'].update({
    'HOST': env('DB_HOST'),
    'PORT': env('DB_PORT'),
    'NAME': env('DB_NAME'),
    'USER': env('DB_USER'),
    'PASSWORD': env('DB_PASSWORD'),
})

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# AWS S3 for file storage
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
```

## Deployment: AWS 🚀

### 1. **RDS PostgreSQL Setup**
```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier chainsight-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username chainsight \
  --master-user-password your-password \
  --allocated-storage 20

# Create security group
aws ec2 create-security-group \
  --group-name chainsight-db-sg \
  --description "ChainSight Database Security Group"

# Add inbound rule for your IP
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 5432 \
  --cidr your-ip/32
```

### 2. **ElastiCache Redis Setup**
```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id chainsight-redis \
  --cache-node-type cache.t3.micro \
  --num-cache-nodes 1 \
  --engine redis \
  --engine-version 7.0
```

### 3. **S3 Bucket for File Storage**
```bash
# Create S3 bucket
aws s3 mb s3://chainsight-files

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket chainsight-files \
  --versioning-configuration Status=Enabled

# Create IAM user for S3 access
aws iam create-user --user-name chainsight-s3-user
aws iam attach-user-policy \
  --user-name chainsight-s3-user \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

### 4. **EC2/ECS Deployment**
```yaml
# docker-compose.yml for ECS
version: '3.8'
services:
  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DB_HOST=chainsight-db.xxxx.rds.amazonaws.com
      - REDIS_URL=redis://chainsight-redis.xxxx.cache.amazonaws.com:6379
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=chainsight
      - POSTGRES_USER=chainsight
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## How ChainSight AI Works: Complete Flow 🔄

### 1. **User Registration & Authentication**
```python
# User signs up
POST /api/v2/accounts/users/register/
{
  "email": "admin@company.com",
  "password": "password123",
  "company_name": "ABC Corp",
  "subdomain": "abc"
}

# Backend creates tenant and user
tenant = Tenant.objects.create(name="ABC Corp", subdomain="abc")
user = User.objects.create_user(
    email="admin@company.com",
    password="password123",
    tenant=tenant,
    role="admin"
)
```

### 2. **Contract Upload Process**
```python
# User uploads contract
POST /api/v2/contracts/upload/
Headers: X-Tenant-ID: 1
FormData: file=contract.pdf, industry=technology

# Backend processes
contract = Contract.objects.create(
    tenant_id=1,  # From X-Tenant-ID header
    uploaded_by=request.user,
    original_filename="contract.pdf",
    status="pending"
)

# Queue for analysis
analyze_contract_task.delay(str(contract.id))
```

### 3. **AI Analysis Pipeline**
```python
# Celery task processes contract
@shared_task
def analyze_contract_task(contract_id):
    contract = Contract.objects.get(id=contract_id)

    # 1. Extract text from PDF
    text = extract_text_from_pdf(contract.file_path)

    # 2. AI Analysis (GPT-4, risk scoring, etc.)
    analysis_result = analyze_contract_with_ai(text)

    # 3. Store results in MongoDB
    mongo_client.contracts.analysis.insert_one({
        'contract_id': contract_id,
        'risk_score': analysis_result['risk_score'],
        'clauses': analysis_result['clauses'],
        'recommendations': analysis_result['recommendations']
    })

    # 4. Update PostgreSQL record
    contract.status = 'completed'
    contract.risk_score = analysis_result['risk_score']
    contract.save()
```

### 4. **Data Retrieval**
```python
# User requests contract details
GET /api/v2/contracts/{id}/
Headers: X-Tenant-ID: 1

# Backend fetches from both databases
contract = Contract.objects.get(id=id, tenant=request.tenant)
analysis = mongo_client.contracts.analysis.find_one({'contract_id': id})

return {
    'contract_id': id,
    'status': 'completed',
    'risk_score': contract.risk_score,
    'analysis': analysis
}
```

## Who Uses ChainSight AI & How 👥

### 1. **Legal Departments**
- **Problem**: Manual contract review takes weeks
- **Solution**: AI analyzes contracts in minutes
- **Value**: 90% faster review, catch 95% of issues

### 2. **SMEs (Small/Medium Enterprises)**
- **Problem**: Can't afford expensive legal teams
- **Solution**: Affordable AI-powered contract analysis
- **Value**: Professional contract review at SMB prices

### 3. **Contract Managers**
- **Problem**: Scattered contracts across email/file shares
- **Solution**: Centralized repository with AI insights
- **Value**: Complete contract lifecycle management

### 4. **Compliance Officers**
- **Problem**: Manual compliance checking
- **Solution**: Automated risk scoring and gap analysis
- **Value**: Proactive compliance management

## Database Performance Optimization ⚡

### 1. **Indexing Strategy**
```python
class Meta:
    indexes = [
        # Tenant-based queries (most common)
        models.Index(fields=['tenant', 'status']),
        models.Index(fields=['tenant', 'created_at']),

        # Global queries (less common)
        models.Index(fields=['status']),
        models.Index(fields=['created_at']),

        # Composite indexes for complex queries
        models.Index(fields=['tenant', 'risk_score', 'created_at']),
    ]
```

### 2. **Query Optimization**
```python
# ✅ GOOD: Select related to avoid N+1 queries
contracts = Contract.objects.filter(
    tenant=request.tenant
).select_related('uploaded_by').prefetch_related('clauses')

# ✅ GOOD: Use values/values_list for bulk operations
contract_ids = Contract.objects.filter(
    tenant=request.tenant,
    status='pending'
).values_list('id', flat=True)

# ✅ GOOD: Bulk updates
Contract.objects.filter(
    id__in=contract_ids
).update(status='processing')
```

### 3. **Caching Strategy**
```python
from django.core.cache import cache

def get_tenant_contracts(tenant_id, status=None):
    cache_key = f"tenant_{tenant_id}_contracts_{status or 'all'}"

    contracts = cache.get(cache_key)
    if contracts is None:
        queryset = Contract.objects.filter(tenant_id=tenant_id)
        if status:
            queryset = queryset.filter(status=status)
        contracts = list(queryset)
        cache.set(cache_key, contracts, 300)  # 5 minutes

    return contracts
```

## Summary 🎯

### **Database Choices:**
- **PostgreSQL**: For structured data, relationships, complex queries
- **MongoDB**: For flexible document storage (AI analysis results)
- **Redis**: For fast caching and background jobs

### **ORM Usage:**
- **Django ORM (90%)**: Most operations - easy, safe, productive
- **Raw SQL (10%)**: Analytics and performance-critical queries

### **Multi-Tenancy:**
- **Row-level security** via tenant_id foreign keys
- **Automatic filtering** through middleware
- **Complete isolation** between organizations

### **Deployment:**
- **Local**: SQLite/PostgreSQL + Redis + MongoDB
- **DigitalOcean**: Managed databases + App Platform
- **AWS**: RDS + ElastiCache + S3 + ECS/EC2

ChainSight AI combines the power of relational databases for structure, NoSQL for flexibility, and caching for performance to deliver a scalable, secure multi-tenant SaaS platform! 🚀