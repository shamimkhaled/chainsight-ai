from rest_framework import serializers
from .models import ContractAnalysis
import os

class ContractUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)
    
    class Meta:
        model = ContractAnalysis
        fields = ['file', 'industry']
    
    def validate_file(self, value):
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size must not exceed 10MB.")
        
        # Check file extension
        ext = os.path.splitext(value.name)[1].lower()
        allowed_extensions = ['.pdf', '.docx', '.txt', '.jpg', '.jpeg', '.png']
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        return value
    
    def validate_industry(self, value):
        valid_industries = ['garment', 'it', 'construction', 'general']
        if value not in valid_industries:
            raise serializers.ValidationError(
                f"Invalid industry. Must be one of: {', '.join(valid_industries)}"
            )
        return value

class ContractAnalysisSerializer(serializers.ModelSerializer):
    processing_time = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ContractAnalysis
        fields = [
            'id', 'original_filename', 'file_size', 'industry', 'language',
            'status', 'risk_score', 'analysis_result', 'error_message',
            'created_at', 'updated_at', 'processing_time', 'file_url',
            'is_scanned_pdf', 'ocr_method_used'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_processing_time(self, obj):
        return obj.processing_time_seconds
    
    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None

class ContractAnalysisListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractAnalysis
        fields = [
            'id', 'original_filename', 'industry', 'language',
            'status', 'risk_score', 'created_at'
        ]