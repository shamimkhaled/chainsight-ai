# Chansight AI - Django Backend Architecture (500K+ Users)
## Complete Django REST Framework Implementation

---

## 📋 TABLE OF CONTENTS

1. [Project Structure](#project-structure)
2. [Django Settings Configuration](#django-settings-configuration)
3. [Database Models](#database-models)
4. [API Views & Serializers](#api-views--serializers)
5. [Celery Tasks](#celery-tasks)
6. [Multi-Tenancy Implementation](#multi-tenancy-implementation)
7. [Authentication & Permissions](#authentication--permissions)
8. [Scalability Configuration](#scalability-configuration)
9. [Deployment Setup](#deployment-setup)

---

## 1. PROJECT STRUCTURE

```
chainsight_backend/
│
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
│
├── config/                              # Project settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                     # Base settings
│   │   ├── development.py              # Dev settings
│   │   ├── production.py               # Production settings
│   │   └── testing.py                  # Test settings
│   └── celery.py
│
├── apps/                                # Django apps
│   │
│   ├── core/                           # Core functionality
│   │   ├── __init__.py
│   │   ├── models.py                   # Base models
│   │   ├── managers.py                 # Custom managers
│   │   ├── middleware.py               # Custom middleware
│   │   ├── permissions.py              # Custom permissions
│   │   └── utils.py
│   │
│   ├── tenants/                        # Multi-tenancy
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── middleware.py
│   │   └── utils.py
│   │
│   ├── accounts/                       # User management
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── permissions.py
│   │
│   ├── contracts/                      # Contract management
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── tasks.py                    # Celery tasks
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── upload_service.py
│   │   │   ├── processing_service.py
│   │   │   ├── ai_service.py
│   │   │   └── export_service.py
│   │   └── utils.py
│   │
│   ├── analysis/                       # Contract analysis
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tasks.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── risk_assessment.py
│   │       ├── clause_extraction.py
│   │       ├── compliance_check.py
│   │       └── sentiment_analysis.py
│   │
│   ├── counterparties/                 # Counterparty management
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── entity_extraction.py
│   │
│   ├── suppliers/                      # Supplier risk management
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tasks.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── risk_assessment.py
│   │       ├── monitoring.py
│   │       └── external_data.py
│   │
│   ├── chat/                           # RAG Chat AI
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── rag_service.py
│   │       ├── embeddings.py
│   │       └── vector_store.py
│   │
│   ├── alerts/                         # Notification & alerts
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tasks.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── email_service.py
│   │       ├── sms_service.py
│   │       ├── whatsapp_service.py
│   │       └── alert_engine.py
│   │
│   ├── integrations/                   # ERP/CRM integrations
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tasks.py
│   │   └── connectors/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── sap.py
│   │       ├── netsuite.py
│   │       ├── salesforce.py
│   │       ├── microsoft_word.py
│   │       └── google_docs.py
│   │
│   ├── repository/                     # Document repository
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── search_service.py
│   │
│   ├── compliance/                     # Compliance management
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── frameworks/
│   │       ├── __init__.py
│   │       ├── manufacturing.py
│   │       ├── law_firms.py
│   │       └── small_business.py
│   │
│   └── dashboard/                      # Dashboard & analytics
│       ├── __init__.py
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       └── services/
│           ├── __init__.py
│           └── analytics.py
│
├── static/                             # Static files
│   ├── css/
│   ├── js/
│   └── img/
│
├── media/                              # Media files (development)
│   └── contracts/
│
├── templates/                          # Django templates
│   └── admin/
│
├── scripts/                            # Utility scripts
│   ├── seed_data.py
│   └── setup_dev.sh
│
└── tests/                              # Tests
    ├── __init__.py
    ├── test_contracts.py
    ├── test_analysis.py
    └── test_integrations.py
```

---

## 2. DJANGO SETTINGS CONFIGURATION

### Base Settings (config/settings/base.py)

```python
"""
Base settings for Chansight AI
"""
import os
from pathlib import Path
from datetime import timedelta
import environ

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment variables
env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Security
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Application definition
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_yasg',
    'django_celery_beat',
    'django_celery_results',
    'storages',
    
    # Local apps
    'apps.core',
    'apps.tenants',
    'apps.accounts',
    'apps.contracts',
    'apps.analysis',
    'apps.counterparties',
    'apps.suppliers',
    'apps.chat',
    'apps.alerts',
    'apps.integrations',
    'apps.repository',
    'apps.compliance',
    'apps.dashboard',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom middleware
    'apps.tenants.middleware.TenantMiddleware',
    'apps.core.middleware.RequestLoggingMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
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

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS Settings
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://localhost:3000',
    'http://localhost:8000',
])
CORS_ALLOW_CREDENTIALS = True

# Cache Configuration (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'chainsight',
        'TIMEOUT': 300,
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Celery Configuration
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# Celery Beat Schedule
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@chainsight.ai')

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_DEFAULT_ACL = 'private'
AWS_S3_FILE_OVERWRITE = False

# Use S3 for media files in production
if not DEBUG:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# OpenAI Configuration
OPENAI_API_KEY = env('OPENAI_API_KEY')
OPENAI_MODEL = env('OPENAI_MODEL', default='gpt-4-turbo')

# MongoDB Configuration
MONGODB_URI = env('MONGODB_URI', default='mongodb://localhost:27017/')
MONGODB_DATABASE = env('MONGODB_DATABASE', default='chainsight')

# Vector Database (Pinecone)
PINECONE_API_KEY = env('PINECONE_API_KEY', default='')
PINECONE_ENVIRONMENT = env('PINECONE_ENVIRONMENT', default='')
PINECONE_INDEX_NAME = env('PINECONE_INDEX_NAME', default='chainsight-contracts')

# Twilio (SMS)
TWILIO_ACCOUNT_SID = env('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = env('TWILIO_PHONE_NUMBER', default='')

# WhatsApp
WHATSAPP_API_KEY = env('WHATSAPP_API_KEY', default='')
WHATSAPP_PHONE_NUMBER = env('WHATSAPP_PHONE_NUMBER', default='')

# File Upload Settings
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_UPLOAD_EXTENSIONS = ['.pdf', '.docx', '.txt', '.jpg', '.jpeg', '.png']

# Rate Limiting
RATE_LIMIT_ENABLED = True
RATE_LIMITS = {
    'free': {
        'contracts_per_day': 10,
        'api_requests_per_hour': 100,
    },
    'starter': {
        'contracts_per_day': 100,
        'api_requests_per_hour': 500,
    },
    'professional': {
        'contracts_per_day': 500,
        'api_requests_per_hour': 2000,
    },
    'enterprise': {
        'contracts_per_day': -1,  # Unlimited
        'api_requests_per_hour': -1,
    },
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'chainsight.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Production Settings (config/settings/production.py)

```python
from .base import *

DEBUG = False

# Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database - Use read replicas
DATABASES['default']['OPTIONS']['options'] = '-c statement_timeout=30000'

# Add read replicas
DATABASES['replica_1'] = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': env('DB_NAME'),
    'USER': env('DB_READONLY_USER'),
    'PASSWORD': env('DB_READONLY_PASSWORD'),
    'HOST': env('DB_REPLICA_1_HOST'),
    'PORT': env('DB_PORT', default='5432'),
    'CONN_MAX_AGE': 600,
}

DATABASES['replica_2'] = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': env('DB_NAME'),
    'USER': env('DB_READONLY_USER'),
    'PASSWORD': env('DB_READONLY_PASSWORD'),
    'HOST': env('DB_REPLICA_2_HOST'),
    'PORT': env('DB_PORT', default='5432'),
    'CONN_MAX_AGE': 600,
}

# Database Router for Read/Write Splitting
DATABASE_ROUTERS = ['apps.core.routers.ReadReplicaRouter']

# Cache - Use Redis Cluster
CACHES['default']['LOCATION'] = [
    env('REDIS_PRIMARY_URL'),
    env('REDIS_REPLICA_1_URL'),
    env('REDIS_REPLICA_2_URL'),
]

# Logging - Send to CloudWatch or similar
LOGGING['handlers']['cloudwatch'] = {
    'class': 'watchtower.CloudWatchLogHandler',
    'log_group': 'chainsight-production',
    'stream_name': 'django',
}
LOGGING['root']['handlers'].append('cloudwatch')

# Sentry
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn=env('SENTRY_DSN'),
    integrations=[
        DjangoIntegration(),
        CeleryIntegration(),
    ],
    traces_sample_rate=0.1,
    send_default_pii=False,
    environment='production',
)
```

---

## 3. DATABASE MODELS

### Core Base Model (apps/core/models.py)

```python
import uuid
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model with timestamp fields
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']


class TenantAwareModel(TimeStampedModel):
    """
    Abstract base model for tenant-aware models
    """
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_set'
    )
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['tenant', '-created_at']),
        ]
```

### Tenant Model (apps/tenants/models.py)

```python
from django.db import models
from apps.core.models import TimeStampedModel


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

### User Model (apps/accounts/models.py)

```python
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from apps.core.models import TimeStampedModel
from apps.accounts.managers import CustomUserManager


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
    last_name = models.CharField(max_length=150, blank=True)
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

### Contract Models (apps/contracts/models.py)

```python
from django.db import models
from django.conf import settings
from apps.core.models import TenantAwareModel


class Contract(TenantAwareModel):
    """
    Main contract model
    """
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_contracts'
    )
    
    # File information
    original_filename = models.CharField(max_length=500)
    file_path = models.CharField(max_length=1000)  # S3 path
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=50)
    file_hash = models.CharField(max_length=64, db_index=True)  # SHA-256
    
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
    
    # Contract details
    contract_type = models.CharField(max_length=100, blank=True)
    INDUSTRY_CHOICES = [
        ('manufacturing', 'Manufacturing'),
        ('it', 'IT'),
        ('law_firm', 'Law Firm'),
        ('construction', 'Construction'),
        ('general', 'General'),
    ]
    industry = models.CharField(max_length=100, choices=INDUSTRY_CHOICES, default='general')
    language = models.CharField(max_length=50, default='english')
    contract_date = models.DateField(null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True, db_index=True)
    contract_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, blank=True)
    
    # Parties
    counterparties = models.JSONField(default=list, blank=True)
    
    # Analysis results
    risk_score = models.IntegerField(null=True, blank=True, db_index=True)
    compliance_score = models.IntegerField(null=True, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    
    # OCR info
    is_scanned_pdf = models.BooleanField(default=False)
    ocr_method_used = models.CharField(max_length=50, blank=True)
    
    # Repository
    folder_path = models.CharField(max_length=1000, blank=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    analyzed_at = models.DateTimeField(null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    class Meta:
        db_table = 'contracts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['risk_score']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['file_hash']),
        ]
    
    def __str__(self):
        return f"{self.original_filename} - {self.status}"


class ContractAnalysis(TenantAwareModel):
    """
    Contract analysis results
    """
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name='analysis'
    )
    
    # MongoDB reference
    mongo_document_id = models.CharField(max_length=100)
    
    # Quick access fields
    overall_risk_score = models.IntegerField()
    critical_issues_count = models.IntegerField(default=0)
    missing_clauses_count = models.IntegerField(default=0)
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    priority_level = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    
    # Processing info
    processing_time = models.FloatField()
    model_used = models.CharField(max_length=100)
    model_version = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'contract_analyses'
    
    def __str__(self):
        return f"Analysis for {self.contract.original_filename}"


class Clause(TenantAwareModel):
    """
    Contract clauses
    """
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='clauses'
    )
    
    # Identification
    clause_number = models.CharField(max_length=50, blank=True)
    CLAUSE_TYPE_CHOICES = [
        ('payment', 'Payment Terms'),
        ('termination', 'Termination'),
        ('liability', 'Liability'),
        ('confidentiality', 'Confidentiality'),
        ('intellectual_property', 'Intellectual Property'),
        ('force_majeure', 'Force Majeure'),
        ('dispute_resolution', 'Dispute Resolution'),
        ('governing_law', 'Governing Law'),
        ('warranties', 'Warranties'),
        ('other', 'Other'),
    ]
    clause_type = models.CharField(max_length=100, choices=CLAUSE_TYPE_CHOICES)
    clause_category = models.CharField(max_length=100, blank=True)
    
    # Content
    title = models.CharField(max_length=500, blank=True)
    content = models.TextField()
    content_hash = models.CharField(max_length=64)
    
    # Location in document
    page_number = models.IntegerField(null=True, blank=True)
    start_position = models.IntegerField(null=True, blank=True)
    end_position = models.IntegerField(null=True, blank=True)
    
    # Analysis
    RISK_LEVEL_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, blank=True)
    quality_score = models.IntegerField(null=True, blank=True)
    completeness_score = models.IntegerField(null=True, blank=True)
    is_standard = models.BooleanField(default=False)
    has_issues = models.BooleanField(default=False)
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'clauses'
        ordering = ['contract', 'clause_number']
        indexes = [
            models.Index(fields=['contract', 'clause_type']),
        ]
    
    def __str__(self):
        return f"{self.clause_number} - {self.clause_type}"
```

### Counterparty Models (apps/counterparties/models.py)

```python
from django.db import models
from apps.core.models import TenantAwareModel


class Counterparty(TenantAwareModel):
    """
    Contract counterparty/entity
    """
    # Basic information
    name = models.CharField(max_length=500)
    legal_name = models.CharField(max_length=500, blank=True)
    entity_type = models.CharField(max_length=100, blank=True)
    registration_number = models.CharField(max_length=100, blank=True, db_index=True)
    tax_id = models.CharField(max_length=100, blank=True)
    
    # Contact
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    
    # Risk assessment
    risk_score = models.IntegerField(null=True, blank=True)
    RISK_LEVEL_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, blank=True)
    credit_score = models.IntegerField(null=True, blank=True)
    credit_rating = models.CharField(max_length=10, blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verification_source = models.CharField(max_length=100, blank=True)
    verification_date = models.DateTimeField(null=True, blank=True)
    
    # External data
    duns_number = models.CharField(max_length=50, blank=True, db_index=True)
    external_data = models.JSONField(default=dict, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'counterparties'
        verbose_name_plural = 'counterparties'
        ordering = ['name']
        indexes = [
            models.Index(fields=['tenant', 'name']),
            models.Index(fields=['registration_number']),
            models.Index(fields=['duns_number']),
        ]
    
    def __str__(self):
        return self.name


class ContractCounterparty(models.Model):
    """
    Many-to-many relationship between contracts and counterparties
    """
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='contract_counterparties'
    )
    counterparty = models.ForeignKey(
        Counterparty,
        on_delete=models.CASCADE,
        related_name='contract_counterparties'
    )
    
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('supplier', 'Supplier'),
        ('contractor', 'Contractor'),
        ('client', 'Client'),
        ('vendor', 'Vendor'),
        ('other', 'Other'),
    ]
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'contract_counterparties'
        unique_together = ['contract', 'counterparty', 'role']
        indexes = [
            models.Index(fields=['contract']),
            models.Index(fields=['counterparty']),
        ]
    
    def __str__(self):
        return f"{self.counterparty.name} ({self.role}) - {self.contract.original_filename}"
```

### Supplier Models (apps/suppliers/models.py)

```python
from django.db import models
from django.conf import settings
from apps.core.models import TenantAwareModel


class Supplier(TenantAwareModel):
    """
    Supplier for risk management
    """
    counterparty = models.OneToOneField(
        'counterparties.Counterparty',
        on_delete=models.CASCADE,
        related_name='supplier_profile'
    )
    
    # Supplier details
    supplier_code = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True)
    TIER_CHOICES = [
        ('tier1', 'Tier 1'),
        ('tier2', 'Tier 2'),
        ('tier3', 'Tier 3'),
    ]
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, blank=True)
    
    # Performance metrics
    on_time_delivery_rate = models.FloatField(null=True, blank=True)
    quality_score = models.FloatField(null=True, blank=True)
    responsiveness_score = models.FloatField(null=True, blank=True)
    
    # Financial
    annual_spend = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    payment_terms_days = models.IntegerField(null=True, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('blacklisted', 'Blacklisted'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    
    # Risk monitoring
    is_monitored = models.BooleanField(default=False)
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]
    monitoring_frequency = models.CharField(
        max_length=50,
        choices=FREQUENCY_CHOICES,
        blank=True
    )
    last_assessment_date = models.DateTimeField(null=True, blank=True)
    next_assessment_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'suppliers'
        ordering = ['counterparty__name']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['supplier_code']),
        ]
    
    def __str__(self):
        return f"{self.counterparty.name} ({self.supplier_code})"


class SupplierRiskAssessment(TenantAwareModel):
    """
    Supplier risk assessment record
    """
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='risk_assessments'
    )
    
    assessment_date = models.DateTimeField(auto_now_add=True)
    ASSESSMENT_TYPE_CHOICES = [
        ('initial', 'Initial'),
        ('periodic', 'Periodic'),
        ('triggered', 'Triggered'),
        ('adhoc', 'Ad-hoc'),
    ]
    assessment_type = models.CharField(max_length=50, choices=ASSESSMENT_TYPE_CHOICES)
    
    # Overall risk
    overall_risk_score = models.IntegerField()
    RISK_LEVEL_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    overall_risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES)
    risk_category = models.CharField(max_length=100, blank=True)
    
    # Risk categories
    financial_risk_score = models.IntegerField()
    operational_risk_score = models.IntegerField()
    compliance_risk_score = models.IntegerField()
    reputational_risk_score = models.IntegerField()
    geopolitical_risk_score = models.IntegerField()
    cyber_security_risk_score = models.IntegerField()
    
    # Detailed findings
    risk_factors = models.JSONField(default=list, blank=True)
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    
    # Data sources
    data_sources = models.JSONField(default=list, blank=True)
    external_data_fetched = models.BooleanField(default=False)
    
    # Assessor
    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='supplier_assessments'
    )
    assessment_method = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'supplier_risk_assessments'
        ordering = ['-assessment_date']
        indexes = [
            models.Index(fields=['supplier', '-assessment_date']),
            models.Index(fields=['overall_risk_level']),
        ]
    
    def __str__(self):
        return f"{self.supplier} - {self.assessment_date.date()} ({self.overall_risk_level})"
```

### Alert Models (apps/alerts/models.py)

```python
from django.db import models
from django.conf import settings
from apps.core.models import TenantAwareModel


class AlertRule(TenantAwareModel):
    """
    Alert rule configuration
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Rule type
    ALERT_TYPE_CHOICES = [
        ('risk_threshold', 'Risk Threshold'),
        ('expiry', 'Contract Expiry'),
        ('compliance', 'Compliance Violation'),
        ('supplier_risk', 'Supplier Risk'),
        ('custom', 'Custom'),
    ]
    alert_type = models.CharField(max_length=100, choices=ALERT_TYPE_CHOICES)
    category = models.CharField(max_length=100, blank=True)
    
    # Conditions
    conditions = models.JSONField(default=dict, blank=True)
    threshold_value = models.FloatField(null=True, blank=True)
    comparison_operator = models.CharField(max_length=20, blank=True)
    
    # Alert configuration
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    priority = models.IntegerField(default=5)
    
    # Notification channels
    notify_email = models.BooleanField(default=True)
    notify_sms = models.BooleanField(default=False)
    notify_whatsapp = models.BooleanField(default=False)
    notify_erp = models.BooleanField(default=False)
    notify_webhook = models.BooleanField(default=False)
    
    # Recipients
    recipients = models.JSONField(default=list, blank=True)
    
    # Scheduling
    is_active = models.BooleanField(default=True)
    FREQUENCY_CHOICES = [
        ('realtime', 'Real-time'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    check_frequency = models.CharField(max_length=50, choices=FREQUENCY_CHOICES)
    
    # Rate limiting
    cooldown_period = models.IntegerField(default=3600)  # seconds
    max_alerts_per_day = models.IntegerField(default=10)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_alert_rules'
    )
    
    class Meta:
        db_table = 'alert_rules'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['alert_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.alert_type})"


class Alert(TenantAwareModel):
    """
    Alert instance
    """
    alert_rule = models.ForeignKey(
        AlertRule,
        on_delete=models.SET_NULL,
        null=True,
        related_name='alerts'
    )
    
    # Alert details
    alert_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=20)
    title = models.CharField(max_length=500)
    message = models.TextField()
    
    # Related objects
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alerts'
    )
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alerts'
    )
    
    # Alert data
    trigger_data = models.JSONField(default=dict, blank=True)
    context = models.JSONField(default=dict, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Notification tracking
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    whatsapp_sent = models.BooleanField(default=False)
    erp_sent = models.BooleanField(default=False)
    webhook_sent = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', '-created_at']),
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['contract']),
            models.Index(fields=['supplier']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.severity}"


class NotificationLog(models.Model):
    """
    Notification delivery log
    """
    alert = models.ForeignKey(
        Alert,
        on_delete=models.CASCADE,
        related_name='notification_logs'
    )
    
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('erp', 'ERP'),
        ('webhook', 'Webhook'),
    ]
    channel = models.CharField(max_length=50, choices=CHANNEL_CHOICES)
    recipient = models.CharField(max_length=500)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True)
    
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking IDs
    external_id = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'notification_logs'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['alert', 'channel']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.channel} to {self.recipient} - {self.status}"
```

---

## 4. API VIEWS & SERIALIZERS

### Contract Serializers (apps/contracts/serializers.py)

```python
from rest_framework import serializers
from apps.contracts.models import Contract, ContractAnalysis, Clause
from apps.counterparties.serializers import CounterpartySerializer


class ClauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clause
        fields = [
            'id', 'clause_number', 'clause_type', 'clause_category',
            'title', 'content', 'page_number', 'risk_level',
            'quality_score', 'completeness_score', 'is_standard',
            'has_issues', 'tags', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ContractAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractAnalysis
        fields = [
            'id', 'overall_risk_score', 'critical_issues_count',
            'missing_clauses_count', 'priority_level', 'processing_time',
            'model_used', 'model_version', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ContractListSerializer(serializers.ModelSerializer):
    """Serializer for contract list view"""
    uploaded_by_name = serializers.CharField(
        source='uploaded_by.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Contract
        fields = [
            'id', 'original_filename', 'file_size', 'file_type',
            'status', 'progress_percentage', 'industry', 'language',
            'risk_score', 'compliance_score', 'sentiment_score',
            'contract_date', 'expiry_date', 'contract_value',
            'currency', 'uploaded_by_name', 'created_at', 'analyzed_at'
        ]
        read_only_fields = ['id', 'created_at']


class ContractDetailSerializer(serializers.ModelSerializer):
    """Serializer for contract detail view"""
    analysis = ContractAnalysisSerializer(read_only=True)
    clauses = ClauseSerializer(many=True, read_only=True)
    uploaded_by_name = serializers.CharField(
        source='uploaded_by.get_full_name',
        read_only=True
    )
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Contract
        fields = [
            'id', 'original_filename', 'file_size', 'file_type',
            'file_hash', 'status', 'processing_stage', 'progress_percentage',
            'error_message', 'contract_type', 'industry', 'language',
            'contract_date', 'effective_date', 'expiry_date',
            'contract_value', 'currency', 'counterparties',
            'risk_score', 'compliance_score', 'sentiment_score',
            'is_scanned_pdf', 'ocr_method_used', 'folder_path',
            'is_archived', 'archived_at', 'analyzed_at', 'processing_time',
            'metadata', 'tags', 'uploaded_by_name', 'created_at',
            'updated_at', 'analysis', 'clauses', 'download_url'
        ]
        read_only_fields = [
            'id', 'file_hash', 'status', 'processing_stage',
            'progress_percentage', 'error_message', 'risk_score',
            'compliance_score', 'sentiment_score', 'is_scanned_pdf',
            'ocr_method_used', 'analyzed_at', 'processing_time',
            'created_at', 'updated_at', 'download_url'
        ]
    
    def get_download_url(self, obj):
        # Generate presigned URL for file download
        from apps.contracts.services.upload_service import UploadService
        upload_service = UploadService()
        return upload_service.get_presigned_url(obj.file_path)


class ContractUploadSerializer(serializers.Serializer):
    """Serializer for contract upload"""
    file = serializers.FileField()
    industry = serializers.ChoiceField(
        choices=Contract.INDUSTRY_CHOICES,
        default='general'
    )
    language = serializers.CharField(default='english', max_length=50)
    contract_type = serializers.CharField(required=False, max_length=100)
    contract_date = serializers.DateField(required=False)
    expiry_date = serializers.DateField(required=False)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    
    def validate_file(self, value):
        # Validate file type and size
        from django.conf import settings
        import os
        
        # Check file extension
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
            raise serializers.ValidationError(
                f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_UPLOAD_EXTENSIONS)}"
            )
        
        # Check file size
        if value.size > settings.MAX_UPLOAD_SIZE:
            raise serializers.ValidationError(
                f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
            )
        
        return value
```

### Contract Views (apps/contracts/views.py)

```python
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from apps.contracts.models import Contract, Clause
from apps.contracts.serializers import (
    ContractListSerializer,
    ContractDetailSerializer,
    ContractUploadSerializer,
    ClauseSerializer
)
from apps.contracts.tasks import analyze_contract_task
from apps.contracts.services.upload_service import UploadService
from apps.contracts.services.export_service import ExportService
from apps.core.permissions import IsTenantMember


class ContractViewSet(viewsets.ModelViewSet):
    """
    Contract management viewset
    
    list: Get list of contracts
    retrieve: Get contract details
    create: Upload new contract
    update: Update contract metadata
    destroy: Delete contract
    """
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'industry', 'risk_score']
    search_fields = ['original_filename', 'contract_type']
    ordering_fields = ['created_at', 'risk_score', 'expiry_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset by tenant"""
        return Contract.objects.filter(
            tenant=self.request.user.tenant
        ).select_related(
            'analysis', 'uploaded_by'
        ).prefetch_related('clauses')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ContractListSerializer
        elif self.action == 'upload':
            return ContractUploadSerializer
        return ContractDetailSerializer
    
    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        """
        Upload a contract for analysis
        
        POST /api/v2/contracts/upload/
        """
        serializer = ContractUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Upload file to S3
        upload_service = UploadService()
        file = serializer.validated_data['file']
        
        file_path, file_hash = upload_service.upload_to_s3(
            file,
            request.user.tenant.id
        )
        
        # Create contract record
        contract = Contract.objects.create(
            tenant=request.user.tenant,
            uploaded_by=request.user,
            original_filename=file.name,
            file_path=file_path,
            file_size=file.size,
            file_type=file.content_type,
            file_hash=file_hash,
            industry=serializer.validated_data['industry'],
            language=serializer.validated_data['language'],
            contract_type=serializer.validated_data.get('contract_type', ''),
            contract_date=serializer.validated_data.get('contract_date'),
            expiry_date=serializer.validated_data.get('expiry_date'),
            tags=serializer.validated_data.get('tags', []),
            status='pending'
        )
        
        # Trigger async analysis
        analyze_contract_task.delay(str(contract.id))
        
        return Response(
            {
                'contract_id': str(contract.id),
                'status': 'pending',
                'message': 'Contract uploaded successfully. Analysis in progress.'
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'], url_path='results')
    def results(self, request, pk=None):
        """
        Get contract analysis results
        
        GET /api/v2/contracts/{id}/results/
        """
        contract = self.get_object()
        
        if contract.status != 'completed':
            return Response({
                'contract_id': str(contract.id),
                'status': contract.status,
                'progress': contract.progress_percentage,
                'message': 'Analysis in progress'
            })
        
        # Get detailed results from MongoDB
        from apps.contracts.services.processing_service import ProcessingService
        processing_service = ProcessingService()
        
        analysis_results = processing_service.get_analysis_results(
            contract.analysis.mongo_document_id
        )
        
        return Response({
            'contract_id': str(contract.id),
            'status': 'completed',
            'risk_score': contract.risk_score,
            'compliance_score': contract.compliance_score,
            'sentiment_score': contract.sentiment_score,
            'analysis': analysis_results
        })
    
    @action(detail=True, methods=['post'], url_path='reanalyze')
    def reanalyze(self, request, pk=None):
        """
        Re-analyze contract
        
        POST /api/v2/contracts/{id}/reanalyze/
        """
        contract = self.get_object()
        
        # Reset status
        contract.status = 'pending'
        contract.progress_percentage = 0
        contract.save()
        
        # Trigger analysis
        analyze_contract_task.delay(str(contract.id))
        
        return Response({
            'message': 'Contract re-analysis started',
            'contract_id': str(contract.id)
        })
    
    @action(detail=True, methods=['post'], url_path='export/docx')
    def export_docx(self, request, pk=None):
        """
        Export analysis report to DOCX
        
        POST /api/v2/contracts/{id}/export/docx/
        """
        contract = self.get_object()
        
        if contract.status != 'completed':
            return Response(
                {'error': 'Contract analysis not completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate DOCX report
        export_service = ExportService()
        docx_url = export_service.generate_docx_report(contract)
        
        return Response({
            'download_url': docx_url,
            'expires_in': 3600  # 1 hour
        })
    
    @action(detail=True, methods=['post'], url_path='export/pdf')
    def export_pdf(self, request, pk=None):
        """
        Export analysis report to PDF
        
        POST /api/v2/contracts/{id}/export/pdf/
        """
        contract = self.get_object()
        
        if contract.status != 'completed':
            return Response(
                {'error': 'Contract analysis not completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate PDF report
        export_service = ExportService()
        pdf_url = export_service.generate_pdf_report(contract)
        
        return Response({
            'download_url': pdf_url,
            'expires_in': 3600  # 1 hour
        })
    
    @action(detail=True, methods=['post'], url_path='archive')
    def archive(self, request, pk=None):
        """Archive contract"""
        from django.utils import timezone
        
        contract = self.get_object()
        contract.is_archived = True
        contract.archived_at = timezone.now()
        contract.save()
        
        return Response({'message': 'Contract archived successfully'})
    
    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        """Restore archived contract"""
        contract = self.get_object()
        contract.is_archived = False
        contract.archived_at = None
        contract.save()
        
        return Response({'message': 'Contract restored successfully'})
    
    @action(detail=True, methods=['get'], url_path='clauses')
    def clauses(self, request, pk=None):
        """Get contract clauses"""
        contract = self.get_object()
        clauses = contract.clauses.all()
        serializer = ClauseSerializer(clauses, many=True)
        return Response(serializer.data)
```

---

## 5. CELERY TASKS

### Contract Analysis Task (apps/contracts/tasks.py)

```python
from celery import shared_task
from django.utils import timezone
import logging

from apps.contracts.models import Contract, ContractAnalysis
from apps.contracts.services.processing_service import ProcessingService
from apps.contracts.services.ai_service import AIAnalysisService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def analyze_contract_task(self, contract_id):
    """
    Analyze contract using AI
    
    This task orchestrates the entire analysis pipeline:
    1. Extract text from document
    2. Perform AI analysis
    3. Extract clauses
    4. Assess compliance
    5. Perform sentiment analysis
    6. Generate report
    """
    
    try:
        # Get contract
        contract = Contract.objects.get(id=contract_id)
        logger.info(f"Starting analysis for contract: {contract_id}")
        
        # Initialize services
        processing_service = ProcessingService()
        ai_service = AIAnalysisService()
        
        # Update status
        contract.status = 'processing'
        contract.processing_stage = 'text_extraction'
        contract.progress_percentage = 10
        contract.save()
        
        # Step 1: Extract text from document
        text_content = processing_service.extract_text(contract.file_path)
        
        contract.progress_percentage = 30
        contract.save()
        
        # Step 2: Perform AI analysis
        contract.processing_stage = 'ai_analysis'
        contract.save()
        
        analysis_result = ai_service.analyze_contract(
            text=text_content,
            industry=contract.industry,
            language=contract.language
        )
        
        contract.progress_percentage = 60
        contract.save()
        
        # Step 3: Extract and analyze clauses
        contract.processing_stage = 'clause_extraction'
        contract.save()
        
        clauses_data = ai_service.extract_clauses(text_content)
        
        # Save clauses to database
        from apps.contracts.models import Clause
        for clause_data in clauses_data:
            Clause.objects.create(
                tenant=contract.tenant,
                contract=contract,
                **clause_data
            )
        
        contract.progress_percentage = 80
        contract.save()
        
        # Step 4: Perform sentiment analysis
        contract.processing_stage = 'sentiment_analysis'
        contract.save()
        
        sentiment_result = ai_service.analyze_sentiment(text_content, clauses_data)
        
        # Step 5: Save results to MongoDB
        contract.processing_stage = 'saving_results'
        contract.save()
        
        mongo_doc_id = processing_service.save_to_mongodb({
            'contract_id': contract_id,
            'tenant_id': str(contract.tenant_id),
            'analysis': analysis_result,
            'clauses': clauses_data,
            'sentiment': sentiment_result,
            'full_text': text_content
        })
        
        # Step 6: Update contract record
        contract.status = 'completed'
        contract.progress_percentage = 100
        contract.risk_score = analysis_result.get('overall_risk_score')
        contract.compliance_score = analysis_result.get('compliance_score', 0)
        contract.sentiment_score = sentiment_result.get('overall_score')
        contract.analyzed_at = timezone.now()
        contract.save()
        
        # Create analysis record
        ContractAnalysis.objects.create(
            tenant=contract.tenant,
            contract=contract,
            mongo_document_id=mongo_doc_id,
            overall_risk_score=analysis_result.get('overall_risk_score'),
            critical_issues_count=len(analysis_result.get('risk_assessment', [])),
            missing_clauses_count=len(analysis_result.get('missing_critical_clauses', [])),
            priority_level=analysis_result.get('executive_summary', {}).get('priority_level', 'medium').lower(),
            processing_time=contract.processing_time or 0,
            model_used='gpt-4-turbo'
        )
        
        logger.info(f"Analysis completed for contract: {contract_id}")
        
        # Trigger notifications
        send_analysis_complete_notification.delay(contract_id)
        
        # Check for alerts
        check_contract_alerts.delay(contract_id)
        
        return {
            'contract_id': contract_id,
            'status': 'completed',
            'risk_score': contract.risk_score
        }
        
    except Contract.DoesNotExist:
        logger.error(f"Contract not found: {contract_id}")
        raise
        
    except Exception as e:
        logger.error(f"Analysis error for contract {contract_id}: {str(e)}")
        
        # Update contract status
        try:
            contract = Contract.objects.get(id=contract_id)
            contract.status = 'failed'
            contract.error_message = str(e)
            contract.save()
        except:
            pass
        
        # Retry task
        raise self.retry(exc=e, countdown=60)


@shared_task
def send_analysis_complete_notification(contract_id):
    """Send notification when analysis is complete"""
    try:
        contract = Contract.objects.get(id=contract_id)
        
        # Send email to uploader
        from apps.alerts.services.email_service import EmailService
        email_service = EmailService()
        
        email_service.send_email(
            to=contract.uploaded_by.email,
            subject=f"Contract Analysis Complete: {contract.original_filename}",
            template='analysis_complete',
            context={
                'contract': contract,
                'user': contract.uploaded_by
            }
        )
        
        logger.info(f"Analysis complete notification sent for contract: {contract_id}")
        
    except Exception as e:
        logger.error(f"Error sending analysis notification: {str(e)}")


@shared_task
def check_contract_alerts(contract_id):
    """Check if contract triggers any alert rules"""
    try:
        from apps.alerts.services.alert_engine import AlertEngine
        
        contract = Contract.objects.get(id=contract_id)
        alert_engine = AlertEngine()
        
        # Check alert rules
        alert_engine.check_contract_alerts(contract)
        
        logger.info(f"Alert check completed for contract: {contract_id}")
        
    except Exception as e:
        logger.error(f"Error checking alerts: {str(e)}")
```

---

## 6. MULTI-TENANCY IMPLEMENTATION

### Tenant Middleware (apps/tenants/middleware.py)

```python
from django.utils.deprecation import MiddlewareMixin
from apps.tenants.models import Tenant
import threading

# Thread-local storage for tenant
_thread_local = threading.local()


def get_current_tenant():
    """Get current tenant from thread-local storage"""
    return getattr(_thread_local, 'tenant', None)


def set_current_tenant(tenant):
    """Set current tenant in thread-local storage"""
    _thread_local.tenant = tenant


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to identify and set current tenant based on:
    1. Subdomain (for web requests)
    2. X-Tenant-ID header (for API requests)
    """
    
    def process_request(self, request):
        tenant = None
        
        # Try to get tenant from header (API requests)
        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            try:
                tenant = Tenant.objects.get(id=tenant_id, is_active=True)
            except Tenant.DoesNotExist:
                pass
        
        # Try to get tenant from subdomain
        if not tenant:
            host = request.get_host().split(':')[0]
            subdomain = host.split('.')[0]
            
            try:
                tenant = Tenant.objects.get(subdomain=subdomain, is_active=True)
            except Tenant.DoesNotExist:
                pass
        
        # Try to get tenant from authenticated user
        if not tenant and request.user.is_authenticated:
            tenant = request.user.tenant
        
        # Set tenant in thread-local storage
        if tenant:
            set_current_tenant(tenant)
            request.tenant = tenant
        else:
            set_current_tenant(None)
            request.tenant = None
    
    def process_response(self, request, response):
        # Clear tenant from thread-local storage
        set_current_tenant(None)
        return response
```

### Database Router (apps/core/routers.py)

```python
import random


class ReadReplicaRouter:
    """
    Database router for read/write splitting
    """
    
    def db_for_read(self, model, **hints):
        """
        Reads go to a replica
        """
        replicas = ['replica_1', 'replica_2']
        return random.choice(replicas)
    
    def db_for_write(self, model, **hints):
        """
        Writes always go to primary
        """
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if all models are in the same database
        """
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Only allow migrations on the primary database
        """
        return db == 'default'
```

---

## 7. AUTHENTICATION & PERMISSIONS

### Custom Permissions (apps/core/permissions.py)

```python
from rest_framework import permissions


class IsTenantMember(permissions.BasePermission):
    """
    Permission to check if user belongs to the tenant
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if tenant is set in request
        if not hasattr(request, 'tenant') or not request.tenant:
            return False
        
        # Check if user belongs to the tenant
        return request.user.tenant == request.tenant
    
    def has_object_permission(self, request, view, obj):
        # Check if object belongs to user's tenant
        if hasattr(obj, 'tenant'):
            return obj.tenant == request.user.tenant
        return True


class IsAdminUser(permissions.BasePermission):
    """
    Permission to check if user is admin
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsManagerOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is manager or admin
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['admin', 'manager']
        )
```

---

## 8. REQUIREMENTS.TXT

```txt
# Django
Django==5.0.1
djangorestframework==3.14.0
django-environ==0.11.2
django-cors-headers==4.3.1
django-filter==23.5
psycopg2-binary==2.9.9
django-redis==5.4.0

# Authentication
djangorestframework-simplejwt==5.3.1

# Database
pymongo==4.6.1
redis==5.0.1

# Celery
celery==5.3.4
django-celery-beat==2.5.0
django-celery-results==2.5.1

# AWS
boto3==1.34.14
django-storages==1.14.2

# AI/ML
openai==1.7.2
langchain==0.1.0
pinecone-client==3.0.0
tiktoken==0.5.2

# Document Processing
PyPDF2==3.0.1
python-docx==1.1.0
Pillow==10.2.0
pytesseract==0.3.10
pdf2image==1.17.0
python-pptx==0.6.23

# Export
reportlab==4.0.9
WeasyPrint==60.2

# Communications
twilio==8.11.1
sendgrid==6.11.0

# API Documentation
drf-yasg==1.21.7

# Security
cryptography==41.0.7

# Monitoring
sentry-sdk==1.39.2
prometheus-client==0.19.0

# Utilities
python-dateutil==2.8.2
pytz==2023.3
requests==2.31.0
whitenoise==6.6.0

# Development
pytest==7.4.4
pytest-django==4.7.0
pytest-cov==4.1.0
faker==22.0.0
```

---

## 9. DOCKER & DEPLOYMENT

### Dockerfile

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libpq-dev \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p staticfiles media logs

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v2/health/')"

# Run application
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: chainsight
      POSTGRES_USER: chainsight
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U chainsight"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  mongodb:
    image: mongo:7
    environment:
      MONGO_INITDB_ROOT_USERNAME: chainsight
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_PASSWORD}
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"

  rabbitmq:
    image: rabbitmq:3-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: chainsight
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
    ports:
      - "5672:5672"
      - "15672:15672"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq

  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
    env_file:
      - .env
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
      mongodb:
        condition: service_started
      rabbitmq:
        condition: service_started

  celery_worker:
    build: .
    command: celery -A config worker -l info -Q default,processing,analysis,notifications
    env_file:
      - .env
    volumes:
      - .:/app
    depends_on:
      - redis
      - rabbitmq
      - postgres

  celery_beat:
    build: .
    command: celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    env_file:
      - .env
    volumes:
      - .:/app
    depends_on:
      - redis
      - rabbitmq
      - postgres

  flower:
    build: .
    command: celery -A config flower --port=5555
    env_file:
      - .env
    ports:
      - "5555:5555"
    depends_on:
      - celery_worker
      - redis

volumes:
  postgres_data:
  redis_data:
  mongodb_data:
  rabbitmq_data:
  static_volume:
  media_volume:
```

### .env.example

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=config.settings.development

# Database
DB_NAME=chainsight
DB_USER=chainsight
DB_PASSWORD=your-db-password
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=amqp://chainsight:your-password@rabbitmq:5672/
CELERY_RESULT_BACKEND=redis://redis:6379/0

# MongoDB
MONGODB_URI=mongodb://chainsight:your-password@mongodb:27017/
MONGODB_DATABASE=chainsight

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=chainsight-contracts
AWS_S3_REGION_NAME=us-east-1

# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4-turbo

# Pinecone
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=chainsight-contracts

# Email (SendGrid)
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@chainsight.ai

# Twilio (SMS)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# WhatsApp
WHATSAPP_API_KEY=your-whatsapp-api-key
WHATSAPP_PHONE_NUMBER=+1234567890

# Sentry
SENTRY_DSN=your-sentry-dsn

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

---

## 10. QUICK START COMMANDS

```bash
# Clone repository
git clone https://github.com/shamimkhaled/chainsight-ai.git
cd chainsight-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# In separate terminals:
# Run Celery worker
celery -A config worker -l info

# Run Celery beat
celery -A config beat -l info

# Or use Docker Compose
docker-compose up -d
```

---

## 🎉 SUMMARY

This complete Django implementation provides:

✅ **Django REST Framework** - All APIs
✅ **Multi-Tenancy** - Complete isolation
✅ **All Features** - Contract analysis, RAG chat, supplier risk, alerts, etc.
✅ **Scalable** - Database read replicas, caching, async tasks
✅ **Production-Ready** - Docker, Celery, monitoring
✅ **Security** - JWT, permissions, HTTPS
✅ **500K+ Users** - Designed for scale

**Start building today!** 🚀
