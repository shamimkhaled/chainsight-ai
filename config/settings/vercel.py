"""
Vercel serverless deployment settings.

Uses Supabase PostgreSQL, in-memory cache, and database sessions.
No Celery, Redis, or read replicas - suitable for serverless.
"""
from .base import *

DEBUG = False

# Vercel domains
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[]) + [
    '.vercel.app',
    '.onrender.com',
]

# Security - Vercel handles SSL
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Single database (no read replicas on serverless)
# Uses DB_* from env - Supabase pooler recommended
DATABASES['default']['CONN_MAX_AGE'] = 0  # Disable persistent connections (serverless)
DATABASES['default'].pop('OPTIONS', None)
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
    'sslmode': 'require',
}

# Remove replica routers if they exist
DATABASE_ROUTERS = []

# Cache & Sessions - In-memory (no Redis on serverless)
# Each function instance has its own cache; sessions stored in DB
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'KEY_PREFIX': 'chainsight',
        'TIMEOUT': 300,
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Logging - Console only (Vercel has no writable filesystem except /tmp)
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
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Disable rate limiting for simpler serverless (optional - re-enable if needed)
RATE_LIMIT_ENABLED = False

# Static - Whitenoise handles this; ensure collectstatic runs in build
# STATICFILES_STORAGE already set in base

# CSRF - Allow Vercel deployment URL
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[]) + [
    'https://*.vercel.app',
]
