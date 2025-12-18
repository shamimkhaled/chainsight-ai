from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from apps.integrations.models import Integration, IntegrationLog, ERPEntity, DocumentSync


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    """Admin interface for Integrations"""
    
    list_display = [
        'name', 'tenant_link', 'integration_type',
        'status_badges', 'last_sync_at', 'error_count',
        'created_at'
    ]
    
    list_filter = [
        'integration_type', 'is_active', 'is_connected',
        'auto_sync', 'sync_interval', 'created_at', 'tenant'
    ]
    
    search_fields = [
        'name', 'integration_type', 'tenant__name'
    ]
    
    readonly_fields = [
        'id', 'is_connected', 'last_sync_at',
        'last_error', 'error_count', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id', 'tenant', 'name', 'integration_type',
                'is_active', 'is_connected'
            )
        }),
        ('Configuration', {
            'fields': ('config', 'credentials'),
            'classes': ('collapse',)
        }),
        ('OAuth Tokens', {
            'fields': (
                'access_token', 'refresh_token', 'token_expires_at'
            ),
            'classes': ('collapse',)
        }),
        ('Sync Settings', {
            'fields': (
                'auto_sync', 'sync_interval', 'last_sync_at'
            )
        }),
        ('Error Tracking', {
            'fields': ('last_error', 'error_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'connect_integrations', 'trigger_sync',
        'activate_integrations', 'deactivate_integrations'
    ]
    
    def tenant_link(self, obj):
        """Display tenant as link"""
        if obj.tenant:
            url = reverse('admin:tenants_tenant_change', args=[obj.tenant.id])
            return format_html('<a href="{}">{}</a>', url, obj.tenant.name)
        return '-'
    tenant_link.short_description = 'Tenant'
    
    def status_badges(self, obj):
        """Display active and connected status"""
        badges = []
        if obj.is_active:
            badges.append('<span style="background-color: #28A745; color: white; '
                         'padding: 2px 6px; border-radius: 3px; font-size: 10px;">ACTIVE</span>')
        else:
            badges.append('<span style="background-color: #6C757D; color: white; '
                         'padding: 2px 6px; border-radius: 3px; font-size: 10px;">INACTIVE</span>')
        
        if obj.is_connected:
            badges.append('<span style="background-color: #1E90FF; color: white; '
                         'padding: 2px 6px; border-radius: 3px; font-size: 10px;">CONNECTED</span>')
        else:
            badges.append('<span style="background-color: #DC3545; color: white; '
                         'padding: 2px 6px; border-radius: 3px; font-size: 10px;">NOT CONNECTED</span>')
        
        return format_html(' '.join(badges))
    status_badges.short_description = 'Status'
    
    def connect_integrations(self, request, queryset):
        """Mark as connected"""
        updated = queryset.update(is_connected=True)
        self.message_user(request, f'{updated} integration(s) marked as connected.')
    connect_integrations.short_description = 'Mark as connected'
    
    def trigger_sync(self, request, queryset):
        """Trigger manual sync"""
        from django.utils import timezone
        updated = queryset.filter(is_active=True, is_connected=True).update(
            last_sync_at=timezone.now()
        )
        self.message_user(request, f'{updated} integration(s) synced.')
    trigger_sync.short_description = 'Trigger sync'
    
    def activate_integrations(self, request, queryset):
        """Activate integrations"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} integration(s) activated.')
    activate_integrations.short_description = 'Activate'
    
    def deactivate_integrations(self, request, queryset):
        """Deactivate integrations"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} integration(s) deactivated.')
    deactivate_integrations.short_description = 'Deactivate'


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    """Admin interface for Integration Logs"""
    
    list_display = [
        'integration_link', 'action', 'status_badge',
        'execution_time', 'created_at'
    ]
    
    list_filter = [
        'action', 'status', 'created_at', 'integration__integration_type', 'tenant'
    ]
    
    search_fields = [
        'integration__name', 'error_message'
    ]
    
    readonly_fields = [
        'id', 'tenant', 'integration', 'action', 'status',
        'request_data', 'response_data', 'error_message',
        'execution_time', 'created_at'
    ]
    
    fieldsets = (
        ('Log Information', {
            'fields': (
                'id', 'tenant', 'integration',
                'action', 'status', 'execution_time'
            )
        }),
        ('Request Data', {
            'fields': ('request_data',),
            'classes': ('collapse',)
        }),
        ('Response Data', {
            'fields': ('response_data',),
            'classes': ('collapse',)
        }),
        ('Error', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def integration_link(self, obj):
        """Display integration as link"""
        if obj.integration:
            url = reverse('admin:integrations_integration_change', args=[obj.integration.id])
            return format_html('<a href="{}">{}</a>', url, obj.integration.name)
        return '-'
    integration_link.short_description = 'Integration'
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'success': '#28A745',
            'failed': '#DC3545',
            'pending': '#FFC107'
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.status.upper()
        )
    status_badge.short_description = 'Status'


@admin.register(ERPEntity)
class ERPEntityAdmin(admin.ModelAdmin):
    """Admin interface for ERP Entities"""
    
    list_display = [
        'external_id', 'integration_link', 'entity_type',
        'contract_link', 'counterparty_link', 'sync_status',
        'last_synced_at'
    ]
    
    list_filter = [
        'entity_type', 'sync_status', 'last_synced_at',
        'integration__integration_type', 'tenant'
    ]
    
    search_fields = [
        'external_id', 'external_reference',
        'contract__original_filename', 'counterparty__name'
    ]
    
    readonly_fields = [
        'id', 'last_synced_at', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Entity Information', {
            'fields': (
                'id', 'tenant', 'integration', 'entity_type',
                'external_id', 'external_reference'
            )
        }),
        ('Mapping', {
            'fields': ('contract', 'counterparty')
        }),
        ('Data', {
            'fields': ('entity_data',),
            'classes': ('collapse',)
        }),
        ('Sync', {
            'fields': ('sync_status', 'last_synced_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def integration_link(self, obj):
        """Display integration as link"""
        if obj.integration:
            url = reverse('admin:integrations_integration_change', args=[obj.integration.id])
            return format_html('<a href="{}">{}</a>', url, obj.integration.name)
        return '-'
    integration_link.short_description = 'Integration'
    
    def contract_link(self, obj):
        """Display contract as link"""
        if obj.contract:
            url = reverse('admin:contracts_contract_change', args=[obj.contract.id])
            return format_html(
                '<a href="{}">{}</a>',
                url, obj.contract.original_filename
            )
        return '-'
    contract_link.short_description = 'Contract'
    
    def counterparty_link(self, obj):
        """Display counterparty as link"""
        if obj.counterparty:
            url = reverse('admin:counterparties_counterparty_change', args=[obj.counterparty.id])
            return format_html('<a href="{}">{}</a>', url, obj.counterparty.name)
        return '-'
    counterparty_link.short_description = 'Counterparty'


@admin.register(DocumentSync)
class DocumentSyncAdmin(admin.ModelAdmin):
    """Admin interface for Document Syncs"""
    
    list_display = [
        'contract_link', 'integration_link', 'sync_direction',
        'auto_sync', 'version_info', 'has_conflicts', 'last_synced_at'
    ]
    
    list_filter = [
        'sync_direction', 'auto_sync', 'has_conflicts',
        'last_synced_at', 'integration__integration_type', 'tenant'
    ]
    
    search_fields = [
        'contract__original_filename', 'external_document_id',
        'external_document_url'
    ]
    
    readonly_fields = [
        'id', 'local_version', 'external_version',
        'last_synced_at', 'has_conflicts', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Sync Information', {
            'fields': (
                'id', 'tenant', 'integration', 'contract',
                'sync_direction', 'auto_sync'
            )
        }),
        ('External Document', {
            'fields': (
                'external_document_id', 'external_document_url'
            )
        }),
        ('Versions', {
            'fields': (
                'local_version', 'external_version', 'last_synced_at'
            )
        }),
        ('Conflicts', {
            'fields': ('has_conflicts', 'conflict_data'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def contract_link(self, obj):
        """Display contract as link"""
        if obj.contract:
            url = reverse('admin:contracts_contract_change', args=[obj.contract.id])
            return format_html(
                '<a href="{}">{}</a>',
                url, obj.contract.original_filename
            )
        return '-'
    contract_link.short_description = 'Contract'
    
    def integration_link(self, obj):
        """Display integration as link"""
        if obj.integration:
            url = reverse('admin:integrations_integration_change', args=[obj.integration.id])
            return format_html('<a href="{}">{}</a>', url, obj.integration.name)
        return '-'
    integration_link.short_description = 'Integration'
    
    def version_info(self, obj):
        """Display version information"""
        return f"Local: v{obj.local_version} / External: v{obj.external_version}"
    version_info.short_description = 'Versions'

