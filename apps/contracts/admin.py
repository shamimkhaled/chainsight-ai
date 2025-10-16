from django.contrib import admin
from apps.contracts.models import Contract, ContractAnalysis, Clause


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = [
        'original_filename', 'status', 'risk_score', 'industry',
        'uploaded_by', 'tenant', 'created_at'
    ]
    list_filter = ['status', 'industry', 'risk_score', 'tenant', 'is_archived']
    search_fields = ['original_filename', 'contract_type']
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('tenant', 'uploaded_by', 'original_filename')
        }),
        ('File Information', {
            'fields': ('file_path', 'file_size', 'file_type', 'file_hash')
        }),
        ('Processing Status', {
            'fields': ('status', 'processing_stage', 'progress_percentage', 'error_message')
        }),
        ('Contract Details', {
            'fields': ('contract_type', 'industry', 'language', 'contract_date',
                      'effective_date', 'expiry_date', 'contract_value', 'currency')
        }),
        ('Analysis Results', {
            'fields': ('risk_score', 'compliance_score', 'sentiment_score', 'analyzed_at')
        }),
        ('Repository', {
            'fields': ('folder_path', 'is_archived', 'archived_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata', 'tags', 'counterparties'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'file_hash']


@admin.register(ContractAnalysis)
class ContractAnalysisAdmin(admin.ModelAdmin):
    list_display = [
        'contract', 'overall_risk_score', 'priority_level',
        'processing_time', 'created_at'
    ]
    list_filter = ['priority_level', 'overall_risk_score']
    search_fields = ['contract__original_filename']
    ordering = ['-created_at']

    readonly_fields = ['created_at', 'updated_at']


@admin.register(Clause)
class ClauseAdmin(admin.ModelAdmin):
    list_display = [
        'contract', 'clause_number', 'clause_type',
        'risk_level', 'quality_score', 'is_standard'
    ]
    list_filter = ['clause_type', 'risk_level', 'is_standard', 'has_issues']
    search_fields = ['contract__original_filename', 'title', 'content']
    ordering = ['contract', 'clause_number']

    fieldsets = (
        ('Basic Information', {
            'fields': ('contract', 'clause_number', 'clause_type', 'clause_category')
        }),
        ('Content', {
            'fields': ('title', 'content', 'content_hash')
        }),
        ('Location', {
            'fields': ('page_number', 'start_position', 'end_position')
        }),
        ('Analysis', {
            'fields': ('risk_level', 'quality_score', 'completeness_score',
                      'is_standard', 'has_issues')
        }),
        ('Metadata', {
            'fields': ('tags', 'metadata'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'content_hash']