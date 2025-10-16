from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from apps.contracts.models import Contract, Clause
from apps.contracts.serializers import (
    ContractListSerializer,
    ContractDetailSerializer,
    ContractUploadSerializer,
    ClauseSerializer
)
from apps.contracts.tasks import analyze_contract_task
from apps.contracts.services.upload_service import UploadService
from apps.contracts.services.export_service import ExportService
from apps.core.permissions import IsTenantMember


class ContractViewSet(viewsets.ModelViewSet):
    """
    Contract management viewset

    list: Get list of contracts
    retrieve: Get contract details
    create: Upload new contract
    update: Update contract metadata
    destroy: Delete contract
    """
    permission_classes = [IsAuthenticated, IsTenantMember]
    queryset = Contract.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'industry', 'risk_score']
    search_fields = ['original_filename', 'contract_type']
    ordering_fields = ['created_at', 'risk_score', 'expiry_date']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter queryset by tenant"""
        return Contract.objects.filter(
            tenant=self.request.user.tenant
        ).select_related(
            'analysis', 'uploaded_by'
        ).prefetch_related('clauses')

    def get_serializer_class(self):
        if self.action == 'list':
            return ContractListSerializer
        elif self.action == 'upload':
            return ContractUploadSerializer
        return ContractDetailSerializer

    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        """
        Upload a contract for analysis

        POST /api/v2/contracts/upload/
        """
        serializer = ContractUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Upload file to S3
        upload_service = UploadService()
        file = serializer.validated_data['file']

        file_path, file_hash = upload_service.upload_to_s3(
            file,
            request.user.tenant.id
        )

        # Create contract record
        contract = Contract.objects.create(
            tenant=request.user.tenant,
            uploaded_by=request.user,
            original_filename=file.name,
            file_path=file_path,
            file_size=file.size,
            file_type=file.content_type,
            file_hash=file_hash,
            industry=serializer.validated_data['industry'],
            language=serializer.validated_data['language'],
            contract_type=serializer.validated_data.get('contract_type', ''),
            contract_date=serializer.validated_data.get('contract_date'),
            expiry_date=serializer.validated_data.get('expiry_date'),
            tags=serializer.validated_data.get('tags', []),
            status='pending'
        )

        # Trigger async analysis
        analyze_contract_task.delay(str(contract.id))

        return Response(
            {
                'contract_id': str(contract.id),
                'status': 'pending',
                'message': 'Contract uploaded successfully. Analysis in progress.'
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'], url_path='results')
    def results(self, request, pk=None):
        """
        Get contract analysis results

        GET /api/v2/contracts/{id}/results/
        """
        contract = self.get_object()

        if contract.status != 'completed':
            return Response({
                'contract_id': str(contract.id),
                'status': contract.status,
                'progress': contract.progress_percentage,
                'message': 'Analysis in progress'
            })

        # Get detailed results from MongoDB
        from apps.contracts.services.processing_service import ProcessingService
        processing_service = ProcessingService()

        analysis_results = processing_service.get_analysis_results(
            contract.analysis.mongo_document_id
        )

        return Response({
            'contract_id': str(contract.id),
            'status': 'completed',
            'risk_score': contract.risk_score,
            'compliance_score': contract.compliance_score,
            'sentiment_score': contract.sentiment_score,
            'analysis': analysis_results
        })

    @action(detail=True, methods=['post'], url_path='reanalyze')
    def reanalyze(self, request, pk=None):
        """
        Re-analyze contract

        POST /api/v2/contracts/{id}/reanalyze/
        """
        contract = self.get_object()

        # Reset status
        contract.status = 'pending'
        contract.progress_percentage = 0
        contract.save()

        # Trigger analysis
        analyze_contract_task.delay(str(contract.id))

        return Response({
            'message': 'Contract re-analysis started',
            'contract_id': str(contract.id)
        })

    @action(detail=True, methods=['post'], url_path='export/docx')
    def export_docx(self, request, pk=None):
        """
        Export analysis report to DOCX

        POST /api/v2/contracts/{id}/export/docx/
        """
        contract = self.get_object()

        if contract.status != 'completed':
            return Response(
                {'error': 'Contract analysis not completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate DOCX report
        export_service = ExportService()
        docx_url = export_service.generate_docx_report(contract)

        return Response({
            'download_url': docx_url,
            'expires_in': 3600  # 1 hour
        })

    @action(detail=True, methods=['post'], url_path='export/pdf')
    def export_pdf(self, request, pk=None):
        """
        Export analysis report to PDF

        POST /api/v2/contracts/{id}/export/pdf/
        """
        contract = self.get_object()

        if contract.status != 'completed':
            return Response(
                {'error': 'Contract analysis not completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate PDF report
        export_service = ExportService()
        pdf_url = export_service.generate_pdf_report(contract)

        return Response({
            'download_url': pdf_url,
            'expires_in': 3600  # 1 hour
        })

    @action(detail=True, methods=['post'], url_path='archive')
    def archive(self, request, pk=None):
        """Archive contract"""
        from django.utils import timezone

        contract = self.get_object()
        contract.is_archived = True
        contract.archived_at = timezone.now()
        contract.save()

        return Response({'message': 'Contract archived successfully'})

    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        """Restore archived contract"""
        contract = self.get_object()
        contract.is_archived = False
        contract.archived_at = None
        contract.save()

        return Response({'message': 'Contract restored successfully'})

    @action(detail=True, methods=['get'], url_path='clauses')
    def clauses(self, request, pk=None):
        """Get contract clauses"""
        contract = self.get_object()
        clauses = contract.clauses.all()
        serializer = ClauseSerializer(clauses, many=True)
        return Response(serializer.data)