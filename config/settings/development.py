from .base import *

DEBUG = True

# Development-specific settings
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database - Use local PostgreSQL
DATABASES['default'].update({
    'HOST': env('DB_HOST', default='localhost'),
    'PORT': env('DB_PORT', default='5432'),
})

# Cache & Sessions - Use local memory (no Redis required)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'KEY_PREFIX': 'chainsight',
        'TIMEOUT': 300,
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Celery - Use local Redis (optional; background tasks require Redis)
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')

# Email - Use console backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS - Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = ['http://localhost:3000', ]

# Logging - More verbose in development
# LOGGING['root']['level'] = 'DEBUG'
# LOGGING['loggers']['django']['level'] = 'DEBUG'
# LOGGING['loggers']['apps']['level'] = 'DEBUG'

# Disable rate limiting in development
RATE_LIMIT_ENABLED = False

# File storage - Use local storage in development
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'