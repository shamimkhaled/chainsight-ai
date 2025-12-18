from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from apps.tenants.models import Tenant
from apps.tenants.serializers import TenantSerializer, TenantDetailSerializer


class TenantViewSet(viewsets.ModelViewSet):
    """
    Tenant management viewset (Admin only)
    
    list: Get list of tenants
    retrieve: Get tenant details
    create: Create new tenant
    update: Update tenant
    destroy: Delete tenant
    """
    permission_classes = [IsAuthenticated]
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

    def get_queryset(self):
        """Superusers see all tenants, others see their own"""
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Tenant.objects.none()
        if self.request.user.is_superuser:
            return Tenant.objects.all()
        return Tenant.objects.filter(id=self.request.user.tenant.id)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TenantDetailSerializer
        return TenantSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user's tenant
        
        GET /api/v2/tenants/me/
        """
        serializer = TenantDetailSerializer(request.user.tenant)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate tenant (Admin only)
        
        POST /api/v2/tenants/{id}/activate/
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'Only superusers can activate tenants'},
                status=status.HTTP_403_FORBIDDEN
            )

        tenant = self.get_object()
        tenant.status = 'active'
        tenant.is_active = True
        tenant.save()

        return Response({
            'message': 'Tenant activated successfully',
            'tenant': TenantSerializer(tenant).data
        })

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """
        Suspend tenant (Admin only)
        
        POST /api/v2/tenants/{id}/suspend/
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'Only superusers can suspend tenants'},
                status=status.HTTP_403_FORBIDDEN
            )

        tenant = self.get_object()
        tenant.status = 'suspended'
        tenant.is_active = False
        tenant.save()

        return Response({
            'message': 'Tenant suspended successfully',
            'tenant': TenantSerializer(tenant).data
        })

    @action(detail=True, methods=['get'])
    def usage(self, request, pk=None):
        """
        Get tenant usage statistics
        
        GET /api/v2/tenants/{id}/usage/
        """
        tenant = self.get_object()

        # Calculate usage
        from apps.contracts.models import Contract
        from apps.accounts.models import User

        total_contracts = Contract.objects.filter(tenant=tenant).count()
        total_users = User.objects.filter(tenant=tenant).count()

        return Response({
            'tenant_id': tenant.id,
            'contracts': {
                'current': total_contracts,
                'limit': tenant.max_contracts,
                'percentage': round((total_contracts / tenant.max_contracts) * 100, 2) if tenant.max_contracts > 0 else 0,
            },
            'users': {
                'current': total_users,
                'limit': tenant.max_users,
                'percentage': round((total_users / tenant.max_users) * 100, 2) if tenant.max_users > 0 else 0,
            },
            'plan_type': tenant.plan_type,
        })

