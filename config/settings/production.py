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