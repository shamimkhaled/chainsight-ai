from rest_framework import serializers
from apps.contracts.models import Contract, ContractAnalysis, Clause
from apps.counterparties.serializers import CounterpartySerializer


class ClauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clause
        fields = [
            'id', 'clause_number', 'clause_type', 'clause_category',
            'title', 'content', 'page_number', 'risk_level',
            'quality_score', 'completeness_score', 'is_standard',
            'has_issues', 'tags', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ContractAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractAnalysis
        fields = [
            'id', 'overall_risk_score', 'critical_issues_count',
            'missing_clauses_count', 'priority_level', 'processing_time',
            'model_used', 'model_version', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ContractListSerializer(serializers.ModelSerializer):
    """Serializer for contract list view"""
    uploaded_by_name = serializers.CharField(
        source='uploaded_by.get_full_name',
        read_only=True
    )

    class Meta:
        model = Contract
        fields = [
            'id', 'original_filename', 'file_size', 'file_type',
            'status', 'progress_percentage', 'industry', 'language',
            'risk_score', 'compliance_score', 'sentiment_score',
            'contract_date', 'expiry_date', 'contract_value',
            'currency', 'uploaded_by_name', 'created_at', 'analyzed_at'
        ]
        read_only_fields = ['id', 'created_at']


class ContractDetailSerializer(serializers.ModelSerializer):
    """Serializer for contract detail view"""
    analysis = ContractAnalysisSerializer(read_only=True)
    clauses = ClauseSerializer(many=True, read_only=True)
    uploaded_by_name = serializers.CharField(
        source='uploaded_by.get_full_name',
        read_only=True
    )
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            'id', 'original_filename', 'file_size', 'file_type',
            'file_hash', 'status', 'processing_stage', 'progress_percentage',
            'error_message', 'contract_type', 'industry', 'language',
            'contract_date', 'effective_date', 'expiry_date',
            'contract_value', 'currency', 'counterparties',
            'risk_score', 'compliance_score', 'sentiment_score',
            'is_scanned_pdf', 'ocr_method_used', 'folder_path',
            'is_archived', 'archived_at', 'analyzed_at', 'processing_time',
            'metadata', 'tags', 'uploaded_by_name', 'created_at',
            'updated_at', 'analysis', 'clauses', 'download_url'
        ]
        read_only_fields = [
            'id', 'file_hash', 'status', 'processing_stage',
            'progress_percentage', 'error_message', 'risk_score',
            'compliance_score', 'sentiment_score', 'is_scanned_pdf',
            'ocr_method_used', 'analyzed_at', 'processing_time',
            'created_at', 'updated_at', 'download_url'
        ]

    def get_download_url(self, obj):
        # Generate presigned URL for file download
        from apps.contracts.services.upload_service import UploadService
        upload_service = UploadService()
        return upload_service.get_presigned_url(obj.file_path)


class ContractUploadSerializer(serializers.Serializer):
    """Serializer for contract upload"""
    file = serializers.FileField()
    industry = serializers.ChoiceField(
        choices=Contract.INDUSTRY_CHOICES,
        default='general'
    )
    language = serializers.CharField(default='english', max_length=50)
    contract_type = serializers.CharField(required=False, max_length=100)
    contract_date = serializers.DateField(required=False)
    expiry_date = serializers.DateField(required=False)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    def validate_file(self, value):
        # Validate file type and size
        from django.conf import settings
        import os

        # Check file extension
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
            raise serializers.ValidationError(
                f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_UPLOAD_EXTENSIONS)}"
            )

        # Check file size
        if value.size > settings.MAX_UPLOAD_SIZE:
            raise serializers.ValidationError(
                f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
            )

        return value