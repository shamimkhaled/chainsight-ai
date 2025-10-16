from apps.tenants.models import Tenant
from apps.tenants.middleware import get_current_tenant


def get_tenant_from_request(request):
    """Get tenant from request"""
    return getattr(request, 'tenant', None)


def get_current_tenant_safe():
    """Get current tenant safely, returns None if not set"""
    return get_current_tenant()


def create_tenant(name, subdomain, plan_type='free'):
    """Create a new tenant"""
    tenant = Tenant.objects.create(
        name=name,
        subdomain=subdomain,
        plan_type=plan_type
    )
    return tenant


def get_tenant_by_subdomain(subdomain):
    """Get tenant by subdomain"""
    try:
        return Tenant.objects.get(subdomain=subdomain, is_active=True)
    except Tenant.DoesNotExist:
        return None


def get_tenant_by_id(tenant_id):
    """Get tenant by ID"""
    try:
        return Tenant.objects.get(id=tenant_id, is_active=True)
    except Tenant.DoesNotExist:
        return None