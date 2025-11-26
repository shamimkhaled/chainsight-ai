from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
import sys


class HealthCheckView(views.APIView):
    """
    Health check endpoint for monitoring
    
    GET /api/health/
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        health_status = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'services': {}
        }

        # Check database
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status['services']['database'] = 'healthy'
        except Exception as e:
            health_status['services']['database'] = f'unhealthy: {str(e)}'
            health_status['status'] = 'degraded'

        # Check cache
        try:
            cache.set('health_check', 'ok', 10)
            cache_value = cache.get('health_check')
            if cache_value == 'ok':
                health_status['services']['cache'] = 'healthy'
            else:
                health_status['services']['cache'] = 'unhealthy: cache test failed'
                health_status['status'] = 'degraded'
        except Exception as e:
            health_status['services']['cache'] = f'unhealthy: {str(e)}'
            health_status['status'] = 'degraded'

        # System info
        health_status['system'] = {
            'python_version': sys.version.split()[0],
            'platform': sys.platform,
        }

        return Response(health_status)


class ReadinessCheckView(views.APIView):
    """
    Readiness check endpoint for deployment
    
    GET /api/ready/
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        ready_status = {
            'ready': True,
            'timestamp': timezone.now().isoformat(),
        }

        # Check database connectivity
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception:
            ready_status['ready'] = False
            return Response(ready_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(ready_status)


class APIInfoView(views.APIView):
    """
    API information endpoint
    
    GET /api/info/
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            'name': 'ChainSight AI API',
            'version': 'v2.0.0',
            'description': 'AI-powered contract analysis and management platform',
            'documentation': request.build_absolute_uri('/api/docs/'),
            'endpoints': {
                'authentication': '/api/v2/auth/token/',
                'users': '/api/v2/users/',
                'contracts': '/api/v2/contracts/',
                'counterparties': '/api/v2/counterparties/',
                'tenants': '/api/v2/tenants/',
                'dashboard': '/api/v2/dashboard/',
            },
            'support': {
                'email': 'support@chainsight.ai',
                'docs': 'https://docs.chainsight.ai'
            }
        })

