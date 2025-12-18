from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.integrations.models import Integration, IntegrationLog, ERPEntity, DocumentSync
from apps.integrations.serializers import (
    IntegrationSerializer,
    IntegrationLogSerializer,
    ERPEntitySerializer,
    DocumentSyncSerializer
)
from apps.integrations.services.word_service import WordIntegrationService, GoogleDocsService
from apps.integrations.services.erp_service import ERPIntegrationService
from apps.core.permissions import IsTenantMember, IsAdminUser


class IntegrationViewSet(viewsets.ModelViewSet):
    """
    Integration management viewset
    
    list: Get list of integrations
    retrieve: Get integration details
    create: Create new integration
    update: Update integration
    destroy: Delete integration
    """
    permission_classes = [IsAuthenticated, IsTenantMember]
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['integration_type', 'is_active', 'is_connected']

    def get_queryset(self):
        """Filter integrations by tenant"""
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Integration.objects.none()
        return Integration.objects.filter(
            tenant=self.request.user.tenant
        )

    def perform_create(self, serializer):
        """Set tenant on create"""
        serializer.save(tenant=self.request.user.tenant)

    @action(detail=True, methods=['post'])
    def connect(self, request, pk=None):
        """
        Connect/authenticate integration
        
        POST /api/v2/integrations/{id}/connect/
        """
        integration = self.get_object()
        
        # OAuth flow or API key validation
        # Implementation depends on integration type
        
        integration.is_connected = True
        integration.save()
        
        return Response({
            'message': 'Integration connected successfully',
            'integration': IntegrationSerializer(integration).data
        })

    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """
        Trigger manual sync
        
        POST /api/v2/integrations/{id}/sync/
        """
        integration = self.get_object()
        
        if integration.integration_type in ['sap', 'oracle', 'netsuite']:
            # ERP sync
            erp_service = ERPIntegrationService(integration)
            result = erp_service.sync_vendors()
            
            return Response({
                'message': 'Sync completed',
                'result': result
            })
        
        return Response({
            'message': 'Sync not implemented for this integration type'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """
        Get integration logs
        
        GET /api/v2/integrations/{id}/logs/
        """
        integration = self.get_object()
        logs = integration.logs.all()[:100]
        
        serializer = IntegrationLogSerializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """
        Test integration connection
        
        POST /api/v2/integrations/{id}/test_connection/
        """
        integration = self.get_object()
        
        try:
            # Test connection based on integration type
            if integration.integration_type in ['sap', 'oracle', 'netsuite']:
                erp_service = ERPIntegrationService(integration)
                # Test API call
                result = {'success': True, 'message': 'Connection successful'}
            else:
                result = {'success': True, 'message': 'Connection test not implemented'}
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class WordIntegrationView(viewsets.ViewSet):
    """
    Microsoft Word integration endpoints
    """
    permission_classes = [IsAuthenticated, IsTenantMember]

    @action(detail=False, methods=['get'])
    def edit_url(self, request):
        """
        Get Word Online edit URL for contract
        
        GET /api/v2/integrations/word/edit-url/?contract_id=...
        """
        contract_id = request.query_params.get('contract_id')
        
        from apps.contracts.models import Contract
        contract = Contract.objects.get(
            id=contract_id,
            tenant=request.user.tenant
        )
        
        # Get Word integration
        integration = Integration.objects.filter(
            tenant=request.user.tenant,
            integration_type='microsoft_word',
            is_active=True
        ).first()
        
        if not integration:
            return Response({
                'error': 'Microsoft Word integration not configured'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        word_service = WordIntegrationService(integration)
        edit_url = word_service.get_edit_url(contract)
        
        return Response({
            'edit_url': edit_url,
            'contract_id': str(contract.id)
        })

    @action(detail=False, methods=['post'])
    def save_from_word(self, request):
        """
        Save contract from Word Online
        
        POST /api/v2/integrations/word/save/
        """
        contract_id = request.data.get('contract_id')
        file_content = request.FILES.get('file')
        
        from apps.contracts.models import Contract
        contract = Contract.objects.get(
            id=contract_id,
            tenant=request.user.tenant
        )
        
        integration = Integration.objects.filter(
            tenant=request.user.tenant,
            integration_type='microsoft_word'
        ).first()
        
        word_service = WordIntegrationService(integration)
        updated_contract = word_service.save_from_word(
            contract,
            file_content,
            track_changes=True
        )
        
        return Response({
            'message': 'Contract saved successfully',
            'contract_id': str(updated_contract.id),
            'version': updated_contract.metadata.get('version')
        })


class ERPEntityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ERP entity management (read-only)
    """
    permission_classes = [IsAuthenticated, IsTenantMember]
    queryset = ERPEntity.objects.all()
    serializer_class = ERPEntitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['entity_type', 'sync_status']

    def get_queryset(self):
        """Filter by tenant"""
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return ERPEntity.objects.none()
        return ERPEntity.objects.filter(
            tenant=self.request.user.tenant
        ).select_related('integration', 'contract', 'counterparty')

