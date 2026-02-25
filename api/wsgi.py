"""
Vercel serverless entry point.

Vercel's Python runtime looks for a module-level `app` variable (WSGI/ASGI).
All requests are routed here via vercel.json.
"""
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.vercel')

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
