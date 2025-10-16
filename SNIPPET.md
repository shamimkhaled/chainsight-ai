# ChainSight AI Project Code Snippets & Structure Guide

## Project Overview 📁

ChainSight AI is a **Django-based SaaS platform** for contract analysis using AI. It uses **multi-tenancy architecture** to serve multiple organizations securely.

```
ChainSightAI/
├── config/           # Django project settings
├── apps/            # Django applications (modular)
├── scripts/         # Utility scripts
├── tests/           # Test files
├── logs/            # Application logs
├── requirements.txt # Python dependencies
└── manage.py        # Django management script
```

## Database Architecture Breakdown 🗄️

### 1. **PostgreSQL** (Primary Database - Structured Data)
- **Purpose**: User accounts, contracts metadata, tenant information
- **ORM**: Django ORM (90% of operations)
- **Tables**: tenants, users, contracts, contract_analysis, clauses

### 2. **MongoDB** (Document Database - AI Results)
- **Purpose**: Store complex AI analysis results, unstructured data
- **Usage**: Contract analysis outputs, clause extractions, recommendations
- **Access**: Direct Python driver (pymongo)

### 3. **Redis** (Cache & Queue Database)
- **Purpose**: Fast caching, session storage, background job queuing
- **Usage**: User sessions, API response caching, Celery broker

## Apps Folder Structure & Database Usage 📂

### 1. **apps/tenants/** - Multi-Tenancy Core
**Database**: PostgreSQL (ORM)
**Purpose**: Organization management and tenant isolation

```python
# apps/tenants/models.py - Line by line explanation
from django.db import models
from apps.core.models import TimeStampedModel

class Tenant(TimeStampedModel):  # Inherits created_at, updated_at fields
    """
    Multi-tenant organization model - FOUNDATION of the entire system
    """
    name = models.CharField(max_length=200)  # Company name (e.g., "ABC Corp")

    # Unique subdomain for URL routing (abc.chainsight.ai)
    subdomain = models.CharField(max_length=100, unique=True, db_index=True)

    # Subscription plans with different limits
    PLAN_CHOICES = [
        ('free', 'Free'),           # 10 users, 1k contracts
        ('starter', 'Starter'),     # 100 users, 10k contracts
        ('professional', 'Professional'),  # 500 users, 50k contracts
        ('enterprise', 'Enterprise'),       # Unlimited
    ]
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')

    # Resource limits based on plan
    max_users = models.IntegerField(default=10)
    max_contracts = models.IntegerField(default=1000)
    max_storage_gb = models.IntegerField(default=100)

    # Account status management
    STATUS_CHOICES = [
        ('active', 'Active'),       # Normal operation
        ('suspended', 'Suspended'), # Payment issues
        ('inactive', 'Inactive'),   # Deactivated
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)  # Quick enable/disable

    # Billing information stored as JSON for flexibility
    billing_email = models.EmailField(blank=True)
    billing_info = models.JSONField(default=dict, blank=True)

    # Tenant-specific settings (theme, notifications, etc.)
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'tenants'  # Actual table name in database
        ordering = ['name']   # Default ordering for queries
        indexes = [
            models.Index(fields=['subdomain']),  # Fast subdomain lookups
            models.Index(fields=['status']),     # Fast status filtering
        ]

    def __str__(self):
        return self.name  # Display name in Django admin

    def get_rate_limits(self):
        """Get rate limits for tenant's plan - USED for API throttling"""
        from django.conf import settings
        return settings.RATE_LIMITS.get(self.plan_type, settings.RATE_LIMITS['free'])
```

```python
# apps/tenants/middleware.py - Line by line explanation
from django.utils.deprecation import MiddlewareMixin
from django.db import OperationalError
from apps.tenants.models import Tenant
import threading

# Thread-local storage for tenant (each request gets its own tenant)
_thread_local = threading.local()

def get_current_tenant():
    """Get current tenant from thread-local storage"""
    return getattr(_thread_local, 'tenant', None)

def set_current_tenant(tenant):
    """Set current tenant in thread-local storage"""
    _thread_local.tenant = tenant

class TenantMiddleware(MiddlewareMixin):
    """
    CRITICAL: Automatically identifies tenant for each request
    This ensures data isolation between organizations
    """

    def process_request(self, request):
        tenant = None

        # Method 1: API Header (most common for API calls)
        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            try:
                tenant = Tenant.objects.get(id=tenant_id, is_active=True)
            except Tenant.DoesNotExist:
                pass  # Continue to other methods

        # Method 2: Subdomain (for web interface)
        if not tenant:
            host = request.get_host().split(':')[0]  # Remove port
            subdomain = host.split('.')[0]  # Get subdomain part

            try:
                tenant = Tenant.objects.get(subdomain=subdomain, is_active=True)
            except (Tenant.DoesNotExist, OperationalError):
                pass  # Database might not be ready during migrations

        # Method 3: User's tenant (fallback for authenticated users)
        if not tenant and request.user.is_authenticated:
            tenant = request.user.tenant

        # Store tenant in thread-local and request object
        if tenant:
            set_current_tenant(tenant)
            request.tenant = tenant  # Available in views
        else:
            set_current_tenant(None)
            request.tenant = None

    def process_response(self, request, response):
        # Clean up thread-local storage
        set_current_tenant(None)
        return response
```

### 2. **apps/accounts/** - User Management
**Database**: PostgreSQL (ORM)
**Purpose**: Authentication, user roles, tenant relationships

```python
# apps/accounts/models.py - Line by line explanation
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from apps.core.models import TimeStampedModel
from apps.accounts.managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Custom user model with tenant relationship - CORE of user system
    """
    # CRITICAL: Links user to their organization
    tenant = models.ForeignKey(
        'tenants.Tenant',           # Reference to Tenant model
        on_delete=models.CASCADE,   # Delete user if tenant is deleted
        related_name='users'        # Access: tenant.users.all()
    )

    # Authentication fields
    email = models.EmailField(unique=True)  # Login username
    username = models.CharField(max_length=150, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=50, blank=True)

    # Role-based access control
    ROLE_CHOICES = [
        ('admin', 'Admin'),       # Full access to tenant
        ('manager', 'Manager'),   # Manage contracts and users
        ('user', 'User'),         # Upload and view contracts
        ('viewer', 'Viewer'),     # Read-only access
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    # Account status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)    # Django admin access
    is_verified = models.BooleanField(default=False) # Email verification
    last_login = models.DateTimeField(null=True, blank=True)

    # Security features
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=100, blank=True)

    # Use custom manager for tenant-aware operations
    objects = CustomUserManager()

    # Django authentication settings
    USERNAME_FIELD = 'email'      # Login with email
    REQUIRED_FIELDS = []          # No additional required fields

    class Meta:
        db_table = 'users'
        # Email must be unique per tenant (same email can exist in different tenants)
        unique_together = ['tenant', 'email']
        indexes = [
            models.Index(fields=['tenant', 'email']),  # Fast user lookups
            models.Index(fields=['tenant', 'role']),   # Fast role filtering
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
```

```python
# apps/accounts/managers.py - Line by line explanation
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    """
    Custom user manager for tenant-aware user creation
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Base user creation method
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)

        # Create user instance
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save()  # Save to database
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create regular user - set default permissions
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create superuser - set admin permissions
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # CRITICAL: Create default tenant for superuser if none exists
        from apps.tenants.models import Tenant
        if not extra_fields.get('tenant'):
            tenant, created = Tenant.objects.get_or_create(
                subdomain='default',
                defaults={
                    'name': 'Default Organization',
                    'plan_type': 'enterprise'  # Superuser gets enterprise
                }
            )
            extra_fields['tenant'] = tenant

        return self._create_user(email, password, **extra_fields)
```

### 3. **apps/contracts/** - Contract Management
**Database**: PostgreSQL (ORM) + MongoDB (Analysis Results)
**Purpose**: Contract upload, processing, and analysis

```python
# apps/contracts/models.py - Line by line explanation
from django.db import models
from apps.core.models import TimeStampedModel

class Contract(TimeStampedModel):
    """
    Contract document model - MAIN BUSINESS ENTITY
    """
    # Multi-tenancy: Every contract belongs to a tenant
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='contracts'
    )

    # Who uploaded this contract
    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='uploaded_contracts'
    )

    # File information
    original_filename = models.CharField(max_length=255)  # "service_agreement.pdf"
    file_path = models.CharField(max_length=500)          # S3 path
    file_size = models.BigIntegerField()                  # File size in bytes
    file_type = models.CharField(max_length=100)          # "application/pdf"
    file_hash = models.CharField(max_length=128, unique=True)  # SHA256 hash

    # Processing status - tracks AI analysis progress
    STATUS_CHOICES = [
        ('pending', 'Pending'),        # Just uploaded
        ('processing', 'Processing'),  # AI analyzing
        ('completed', 'Completed'),    # Analysis done
        ('failed', 'Failed'),          # Analysis failed
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processing_stage = models.CharField(max_length=100, blank=True)  # "extracting_text"
    progress_percentage = models.IntegerField(default=0)  # 0-100
    error_message = models.TextField(blank=True)  # Error details if failed

    # Contract metadata
    contract_type = models.CharField(max_length=100, blank=True)  # "service_agreement"
    industry = models.CharField(max_length=100)  # "technology", "healthcare"
    language = models.CharField(max_length=50, default='english')
    contract_date = models.DateField(null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    contract_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')

    # Counterparties stored as JSON for flexibility
    counterparties = models.JSONField(default=list, blank=True)

    # AI Analysis Results (stored in PostgreSQL for fast queries)
    risk_score = models.IntegerField(null=True, blank=True)      # 0-100
    compliance_score = models.IntegerField(null=True, blank=True) # 0-100
    sentiment_score = models.FloatField(null=True, blank=True)    # -1 to 1

    # OCR and scanning info
    is_scanned_pdf = models.BooleanField(default=False)
    ocr_method_used = models.CharField(max_length=50, blank=True)

    # Organization
    folder_path = models.CharField(max_length=500, blank=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    # Analysis metadata
    analyzed_at = models.DateTimeField(null=True, blank=True)
    processing_time = models.IntegerField(null=True, blank=True)  # seconds

    # Additional flexible data
    metadata = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'contracts'
        ordering = ['-created_at']
        indexes = [
            # Most common queries: tenant + status
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'uploaded_by']),
            models.Index(fields=['tenant', 'risk_score']),
            # Global indexes for admin queries
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.original_filename} ({self.tenant.name})"

    def save(self, *args, **kwargs):
        # Auto-generate folder path for S3 organization
        if not self.folder_path:
            self.folder_path = f"tenant_{self.tenant.id}/contracts/{self.created_at.year}/{self.created_at.month}/"
        super().save(*args, **kwargs)
```

```python
# apps/contracts/tasks.py - BACKGROUND PROCESSING
from celery import shared_task
from apps.contracts.models import Contract
from apps.contracts.services.processing_service import ProcessingService

@shared_task
def analyze_contract_task(contract_id):
    """
    BACKGROUND TASK: Analyze contract with AI
    This runs asynchronously so users don't wait
    """
    try:
        # Get contract from database
        contract = Contract.objects.get(id=contract_id)

        # Update status to processing
        contract.status = 'processing'
        contract.save()

        # Initialize AI processing service
        processing_service = ProcessingService()

        # Step 1: Extract text from PDF
        text_content = processing_service.extract_text(contract.file_path)

        # Step 2: AI Analysis (GPT-4, risk scoring, etc.)
        analysis_result = processing_service.analyze_contract(text_content)

        # Step 3: Store detailed results in MongoDB
        mongo_result = processing_service.store_analysis_results(
            contract_id,
            analysis_result
        )

        # Step 4: Update contract record with summary
        contract.status = 'completed'
        contract.risk_score = analysis_result.get('risk_score')
        contract.compliance_score = analysis_result.get('compliance_score')
        contract.sentiment_score = analysis_result.get('sentiment_score')
        contract.analyzed_at = timezone.now()
        contract.processing_time = analysis_result.get('processing_time')
        contract.save()

        return f"Contract {contract_id} analysis completed"

    except Exception as e:
        # Mark contract as failed
        contract.status = 'failed'
        contract.error_message = str(e)
        contract.save()
        raise e
```

### 4. **apps/core/** - Shared Functionality
**Database**: PostgreSQL (ORM)
**Purpose**: Common models, middleware, permissions

```python
# apps/core/models.py - BASE MODEL
from django.db import models
from django.utils import timezone

class TimeStampedModel(models.Model):
    """
    BASE MODEL: Automatically adds created_at and updated_at to all models
    """
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # This is not a real table, just a template
```

```python
# apps/core/permissions.py - PERMISSIONS
from rest_framework import permissions

class IsTenantMember(permissions.BasePermission):
    """
    PERMISSION: Ensure user belongs to the same tenant as the resource
    CRITICAL for multi-tenancy security
    """

    def has_object_permission(self, request, view, obj):
        # Check if object's tenant matches user's tenant
        return obj.tenant == request.user.tenant

    def has_permission(self, request, view):
        # For list views, check if user has a tenant
        return request.user.is_authenticated and hasattr(request.user, 'tenant')
```

### 5. **Database Query Examples** 🔍

#### **ORM Queries (Django ORM)**
```python
# Get all contracts for current tenant
contracts = Contract.objects.filter(tenant=request.tenant)

# Get completed high-risk contracts
high_risk = Contract.objects.filter(
    tenant=request.tenant,
    status='completed',
    risk_score__gte=70
).order_by('-risk_score')

# Get contract statistics (ORM)
stats = Contract.objects.filter(tenant=request.tenant).aggregate(
    total=Count('id'),
    avg_risk=Avg('risk_score'),
    completed=Count('id', filter=Q(status='completed'))
)
```

#### **Raw SQL Queries (Complex Analytics)**
```python
# Monthly contract analysis (Raw SQL for performance)
def get_contract_analytics(tenant_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                DATE_TRUNC('month', created_at) as month,
                COUNT(*) as contracts_uploaded,
                AVG(risk_score) as avg_risk_score,
                COUNT(CASE WHEN risk_score >= 70 THEN 1 END) as high_risk_count
            FROM contracts_contract
            WHERE tenant_id = %s AND status = 'completed'
            GROUP BY DATE_TRUNC('month', created_at)
            ORDER BY month DESC
            LIMIT 12
        """, [tenant_id])

        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
```

#### **MongoDB Queries (Analysis Results)**
```python
# Get detailed analysis from MongoDB
def get_contract_analysis(contract_id):
    from pymongo import MongoClient

    client = MongoClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DATABASE]

    # Find analysis document
    analysis = db.contracts_analysis.find_one({'contract_id': contract_id})

    if analysis:
        return {
            'risk_score': analysis.get('risk_score'),
            'clauses': analysis.get('clauses', []),
            'recommendations': analysis.get('recommendations', []),
            'issues': analysis.get('issues', [])
        }
    return None
```

## How ChainSight AI Works: Complete Flow 🔄

### **User Journey Example**

#### **Step 1: Company Signup**
```python
# User visits website and signs up
POST /api/v2/accounts/users/register/
{
  "email": "admin@techcorp.com",
  "password": "secure123!",
  "first_name": "John",
  "last_name": "Admin",
  "company_name": "Tech Corp",
  "subdomain": "techcorp"
}

# Backend creates tenant and user
tenant = Tenant.objects.create(
    name="Tech Corp",
    subdomain="techcorp",
    plan_type="starter"
)

user = User.objects.create_user(
    email="admin@techcorp.com",
    password="secure123!",
    tenant=tenant,
    role="admin"
)
```

#### **Step 2: Contract Upload**
```python
# User uploads contract via API
POST /api/v2/contracts/upload/
Headers: X-Tenant-ID: 1
FormData: file=contract.pdf, industry=technology

# Backend processes
contract = Contract.objects.create(
    tenant_id=1,  # From X-Tenant-ID header
    uploaded_by=user,
    original_filename="contract.pdf",
    status="pending"
)

# Queue for AI analysis
analyze_contract_task.delay(str(contract.id))
```

#### **Step 3: AI Analysis (Background)**
```python
# Celery task processes contract
@shared_task
def analyze_contract_task(contract_id):
    # 1. Extract text from PDF
    text = extract_text_from_pdf(contract.file_path)

    # 2. Send to GPT-4 for analysis
    analysis = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
            "role": "system",
            "content": "Analyze this contract for risks, clauses, and compliance..."
        }, {
            "role": "user",
            "content": text
        }]
    )

    # 3. Store results in MongoDB
    mongo_client.contracts.analysis.insert_one({
        'contract_id': contract_id,
        'risk_score': 75,
        'clauses': [...],
        'recommendations': [...]
    })

    # 4. Update PostgreSQL summary
    contract.risk_score = 75
    contract.status = 'completed'
    contract.save()
```

#### **Step 4: User Views Results**
```python
# User requests analysis results
GET /api/v2/contracts/{id}/results/
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

## Project Structure Deep Dive 📁

### **config/** - Django Project Configuration
```python
# config/settings/base.py - MAIN SETTINGS
import os
from pathlib import Path
from datetime import timedelta
import environ

# Environment variables
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Core Django settings
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Database configuration (PostgreSQL primary)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        # Connection pooling and timeouts
        'CONN_MAX_AGE': 600,
        'OPTIONS': {'connect_timeout': 10}
    }
}

# Redis for caching and sessions
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL'),
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'}
    }
}

# Celery for background tasks
CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND')
```

### **scripts/** - Utility Scripts
```bash
# scripts/setup_dev.sh - Development setup
#!/bin/bash

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data
python manage.py loaddata sample_data.json

echo "Development environment setup complete!"
```

### **Key Files Explanation**

#### **manage.py** - Django Management Script
```python
#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    # Add project directory to Python path
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    # Run Django management commands
    execute_from_command_line(sys.argv)
```

#### **requirements.txt** - Dependencies
```txt
# Django core
Django==5.2.7
djangorestframework==3.15.1

# Database
psycopg2-binary==2.9.9  # PostgreSQL adapter
pymongo==4.6.3          # MongoDB driver
redis==5.0.1            # Redis client

# Authentication & Security
djangorestframework-simplejwt==5.3.0
django-cors-headers==4.3.1

# Background tasks
celery==5.3.4
django-celery-beat==2.5.0
django-celery-results==2.6.0

# File storage & AI
boto3==1.34.101         # AWS S3
openai==1.12.0          # GPT-4 API
PyPDF2==3.0.1           # PDF processing

# Development
pytest==8.0.2
black==24.1.1
```

## Who Uses ChainSight AI & Business Value 💼

### **1. Legal Departments**
- **Problem**: Manual contract review takes weeks
- **Solution**: AI analyzes contracts in minutes
- **Value**: 90% faster review, catch 95% of issues

### **2. Small/Medium Businesses (SMBs)**
- **Problem**: Can't afford expensive legal teams
- **Solution**: Affordable AI-powered contract analysis
- **Value**: Professional contract review at SMB prices

### **3. Contract Managers**
- **Problem**: Scattered contracts across email/file shares
- **Solution**: Centralized repository with AI insights
- **Value**: Complete contract lifecycle management

### **4. Compliance Officers**
- **Problem**: Manual compliance checking
- **Solution**: Automated risk scoring and gap analysis
- **Value**: Proactive compliance management

### **5. Procurement Teams**
- **Problem**: Negotiating unfavorable terms
- **Solution**: AI highlights risky clauses before signing
- **Value**: Better negotiation outcomes, reduced liability

## Summary 🎯

**ChainSight AI** is a **multi-tenant SaaS platform** that uses:

- **PostgreSQL** for structured data (users, contracts, tenants)
- **MongoDB** for complex AI analysis results
- **Redis** for caching and background jobs
- **Django ORM** for 90% of database operations
- **Raw SQL** for analytics and performance-critical queries

The platform serves **legal departments, SMBs, contract managers, and compliance officers** by providing **AI-powered contract analysis** with complete **data isolation** between tenants.

**Key Architecture Decisions:**
1. **Multi-tenancy** ensures data security between organizations
2. **Hybrid database** approach optimizes for different data types
3. **Background processing** enables fast user experience
4. **RESTful APIs** provide flexible integration options

This architecture supports **scalability**, **security**, and **performance** for a SaaS business serving multiple organizations! 🚀