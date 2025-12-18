from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from apps.contracts.models import Contract, ContractAnalysis, Clause


class ClauseInline(admin.TabularInline):
    """Inline admin for Clauses"""
    model = Clause
    extra = 0
    fields = ['clause_type', 'title', 'risk_level', 'page_number']
    readonly_fields = ['clause_type', 'title', 'risk_level', 'page_number']
    can_delete = False
    max_num = 10
    
    def has_add_permission(self, request, obj=None):
        return False


class ContractAnalysisInline(admin.StackedInline):
    """Inline admin for Contract Analysis"""
    model = ContractAnalysis
    extra = 0
    fields = [
        'overall_risk_score', 'priority_level',
        'critical_issues_count', 'missing_clauses_count'
    ]
    readonly_fields = fields
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """Admin interface for Contract model"""
    
    list_display = [
        'original_filename', 'tenant_link', 'contract_type',
        'status_badge', 'risk_score', 'contract_value',
        'effective_date', 'expiry_date', 'created_at'
    ]
    
    list_filter = [
        'status', 'contract_type', 'industry',
        'is_archived', 'created_at', 'effective_date',
        'expiry_date', 'tenant'
    ]
    
    search_fields = [
        'original_filename', 'contract_type', 'industry',
        'file_hash'
    ]
    
    readonly_fields = [
        'id', 'file_hash', 'file_size', 'created_at', 'updated_at',
        'analyzed_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id', 'tenant', 'original_filename',
                'contract_type', 'industry'
            )
        }),
        ('File Details', {
            'fields': (
                'file_path', 'file_hash', 'file_size',
                'file_type', 'is_scanned_pdf'
            ),
            'classes': ('collapse',)
        }),
        ('Contract Details', {
            'fields': (
                'contract_date', 'effective_date', 'expiry_date',
                'contract_value', 'currency'
            )
        }),
        ('Analysis', {
            'fields': (
                'status', 'progress_percentage',
                'risk_score', 'compliance_score', 'sentiment_score'
            )
        }),
        ('Status', {
            'fields': (
                'is_archived', 'archived_at', 'error_message'
            )
        }),
        ('Metadata', {
            'fields': ('tags', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'analyzed_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [ContractAnalysisInline, ClauseInline]
    
    actions = [
        'reanalyze_contracts', 'archive_contracts',
        'unarchive_contracts', 'mark_as_active'
    ]
    
    def tenant_link(self, obj):
        """Display tenant as link"""
        if obj.tenant:
            url = reverse('admin:tenants_tenant_change', args=[obj.tenant.id])
            return format_html('<a href="{}">{}</a>', url, obj.tenant.name)
        return '-'
    tenant_link.short_description = 'Tenant'
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'pending': '#FFA500',
            'processing': '#1E90FF',
            'completed': '#28A745',
            'failed': '#DC3545',
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.status.upper()
        )
    status_badge.short_description = 'Status'
    
    def contract_value(self, obj):
        """Display contract value with currency"""
        if obj.contract_value:
            return f"{obj.currency} {obj.contract_value:,.2f}"
        return '-'
    contract_value.short_description = 'Value'
    
    def reanalyze_contracts(self, request, queryset):
        """Trigger re-analysis"""
        from apps.contracts.tasks import analyze_contract_task
        count = 0
        for contract in queryset:
            analyze_contract_task.delay(str(contract.id))
            count += 1
        self.message_user(request, f'{count} contract(s) queued for analysis.')
    reanalyze_contracts.short_description = 'Re-analyze selected contracts'
    
    def archive_contracts(self, request, queryset):
        """Archive contracts"""
        from django.utils import timezone
        updated = queryset.update(
            is_archived=True,
            archived_at=timezone.now()
        )
        self.message_user(request, f'{updated} contract(s) archived.')
    archive_contracts.short_description = 'Archive selected contracts'
    
    def unarchive_contracts(self, request, queryset):
        """Unarchive contracts"""
        updated = queryset.update(
            is_archived=False,
            archived_at=None
        )
        self.message_user(request, f'{updated} contract(s) unarchived.')
    unarchive_contracts.short_description = 'Unarchive selected contracts'
    
    def mark_as_active(self, request, queryset):
        """Mark as active"""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} contract(s) marked as active.')
    mark_as_active.short_description = 'Mark as active'


@admin.register(ContractAnalysis)
class ContractAnalysisAdmin(admin.ModelAdmin):
    """Admin interface for Contract Analysis"""
    
    list_display = [
        'contract_link', 'overall_risk_score', 'priority_level',
        'critical_issues_count', 'missing_clauses_count', 'created_at'
    ]
    
    list_filter = [
        'priority_level', 'created_at', 'contract__tenant'
    ]
    
    search_fields = [
        'contract__original_filename', 'mongo_document_id'
    ]
    
    readonly_fields = [
        'id', 'contract', 'mongo_document_id', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Contract', {
            'fields': ('id', 'contract', 'mongo_document_id')
        }),
        ('Scores & Metrics', {
            'fields': (
                'overall_risk_score', 'priority_level',
                'critical_issues_count', 'missing_clauses_count'
            )
        }),
        ('Processing', {
            'fields': (
                'processing_time', 'model_used', 'model_version'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def contract_link(self, obj):
        """Display contract as link"""
        url = reverse('admin:contracts_contract_change', args=[obj.contract.id])
        return format_html(
            '<a href="{}">{}</a>',
            url, obj.contract.original_filename
        )
    contract_link.short_description = 'Contract'


@admin.register(Clause)
class ClauseAdmin(admin.ModelAdmin):
    """Admin interface for Clauses"""
    
    list_display = [
        'title', 'contract_link', 'clause_type',
        'risk_level', 'page_number', 'created_at'
    ]
    
    list_filter = [
        'clause_type', 'risk_level', 'is_standard',
        'created_at', 'contract__tenant'
    ]
    
    search_fields = [
        'title', 'text', 'contract__original_filename'
    ]
    
    readonly_fields = [
        'id', 'contract', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id', 'contract', 'clause_type',
                'title', 'text'
            )
        }),
        ('Details', {
            'fields': (
                'risk_level', 'is_standard', 'page_number',
                'start_position', 'end_position'
            )
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def contract_link(self, obj):
        """Display contract as link"""
        url = reverse('admin:contracts_contract_change', args=[obj.contract.id])
        return format_html(
            '<a href="{}">{}</a>',
            url, obj.contract.original_filename
        )
    contract_link.short_description = 'Contract'
