from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.counterparties.models import Counterparty
from apps.counterparties.serializers import (
    CounterpartySerializer,
    CounterpartyListSerializer
)
from apps.core.permissions import IsTenantMember


class CounterpartyViewSet(viewsets.ModelViewSet):
    """
    Counterparty management viewset
    
    list: Get list of counterparties
    retrieve: Get counterparty details
    create: Create new counterparty
    update: Update counterparty
    destroy: Delete counterparty
    """
    permission_classes = [IsAuthenticated, IsTenantMember]
    queryset = Counterparty.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['risk_level', 'is_verified', 'country']
    search_fields = ['name', 'legal_name', 'registration_number']
    ordering_fields = ['name', 'risk_score', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Filter queryset by tenant"""
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Counterparty.objects.none()
        return Counterparty.objects.filter(
            tenant=self.request.user.tenant
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return CounterpartyListSerializer
        return CounterpartySerializer

    def perform_create(self, serializer):
        """Set tenant on create"""
        serializer.save(tenant=self.request.user.tenant)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        Verify counterparty
        
        POST /api/v2/counterparties/{id}/verify/
        """
        from django.utils import timezone
        
        counterparty = self.get_object()
        counterparty.is_verified = True
        counterparty.verification_source = request.data.get('source', 'manual')
        counterparty.verification_date = timezone.now()
        counterparty.save()

        return Response({
            'message': 'Counterparty verified successfully',
            'counterparty': CounterpartySerializer(counterparty).data
        })

    @action(detail=True, methods=['get'])
    def contracts(self, request, pk=None):
        """
        Get contracts associated with counterparty
        
        GET /api/v2/counterparties/{id}/contracts/
        """
        counterparty = self.get_object()
        contracts = counterparty.contract_counterparties.all().select_related('contract')

        from apps.contracts.serializers import ContractListSerializer
        contract_list = [cc.contract for cc in contracts]

        serializer = ContractListSerializer(contract_list, many=True)
        return Response(serializer.data)

