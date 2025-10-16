from django.utils.deprecation import MiddlewareMixin
from django.db import OperationalError
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
            except (Tenant.DoesNotExist, OperationalError):
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