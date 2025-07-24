# Gunicorn configuration file for ChainSight AI

import multiprocessing
import os

# Server socket
# port = os.environ.get("PORT", "8000")  # Render provides PORT automatically

bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Logging
loglevel = "info"
accesslog = "/app/logs/gunicorn_access.log"
errorlog = "/app/logs/gunicorn_error.log"
access_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'chainsightai_api'

# Server mechanics
preload_app = True
daemon = False
raw_env = [
    'DJANGO_SETTINGS_MODULE=chainsightai_api.settings',
]

# Worker recycling
max_requests = 1000
max_requests_jitter = 50

# SSL (if using HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Render-specific optimizations
forwarded_allow_ips = "*"
proxy_allow_ips = "*"