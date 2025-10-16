from django.contrib import admin
from apps.suppliers.models import Supplier, SupplierRiskAssessment


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = [
        'counterparty', 'supplier_code', 'tier', 'status',
        'is_monitored', 'last_assessment_date', 'tenant'
    ]
    list_filter = ['tier', 'status', 'is_monitored', 'tenant']
    search_fields = ['counterparty__name', 'supplier_code']
    ordering = ['counterparty__name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('tenant', 'counterparty', 'supplier_code', 'category', 'tier')
        }),
        ('Performance Metrics', {
            'fields': ('on_time_delivery_rate', 'quality_score', 'responsiveness_score')
        }),
        ('Financial', {
            'fields': ('annual_spend', 'payment_terms_days')
        }),
        ('Status', {
            'fields': ('status', 'is_active', 'is_approved')
        }),
        ('Risk Monitoring', {
            'fields': ('is_monitored', 'monitoring_frequency',
                      'last_assessment_date', 'next_assessment_date')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']


@admin.register(SupplierRiskAssessment)
class SupplierRiskAssessmentAdmin(admin.ModelAdmin):
    list_display = [
        'supplier', 'assessment_date', 'assessment_type',
        'overall_risk_score', 'overall_risk_level', 'assessed_by'
    ]
    list_filter = ['assessment_type', 'overall_risk_level', 'assessment_date']
    search_fields = ['supplier__counterparty__name', 'supplier__supplier_code']
    ordering = ['-assessment_date']

    fieldsets = (
        ('Basic Information', {
            'fields': ('supplier', 'assessment_date', 'assessment_type')
        }),
        ('Overall Risk', {
            'fields': ('overall_risk_score', 'overall_risk_level', 'risk_category')
        }),
        ('Risk Categories', {
            'fields': ('financial_risk_score', 'operational_risk_score',
                      'compliance_risk_score', 'reputational_risk_score',
                      'geopolitical_risk_score', 'cyber_security_risk_score')
        }),
        ('Detailed Findings', {
            'fields': ('risk_factors', 'strengths', 'weaknesses', 'recommendations'),
            'classes': ('collapse',)
        }),
        ('Data & Assessment', {
            'fields': ('data_sources', 'external_data_fetched', 'assessed_by', 'assessment_method')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']