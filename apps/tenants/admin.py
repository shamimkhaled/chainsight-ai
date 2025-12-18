from django.contrib import admin
from apps.tenants.models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Admin interface for Tenant model"""
    
    list_display = [
        'name', 'subdomain', 'status', 'plan_type',
        'max_users', 'max_contracts', 'is_active', 'created_at'
    ]
    
    list_filter = [
        'status', 'plan_type', 'is_active',
        'created_at'
    ]
    
    search_fields = [
        'name', 'subdomain', 'billing_email'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id', 'name', 'subdomain', 'status', 'is_active'
            )
        }),
        ('Plan & Limits', {
            'fields': (
                'plan_type', 'max_users', 'max_contracts', 'max_storage_gb'
            )
        }),
        ('Billing', {
            'fields': (
                'billing_email', 'billing_info'
            )
        }),
        ('Settings', {
            'fields': ('settings',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_tenants', 'deactivate_tenants', 'change_to_free', 'change_to_starter', 'change_to_professional', 'change_to_enterprise']
    
    def activate_tenants(self, request, queryset):
        """Activate selected tenants"""
        updated = queryset.update(is_active=True, status='active')
        self.message_user(request, f'{updated} tenant(s) activated.')
    activate_tenants.short_description = 'Activate selected tenants'
    
    def deactivate_tenants(self, request, queryset):
        """Deactivate selected tenants"""
        updated = queryset.update(is_active=False, status='suspended')
        self.message_user(request, f'{updated} tenant(s) deactivated.')
    deactivate_tenants.short_description = 'Deactivate selected tenants'
    
    def change_to_free(self, request, queryset):
        """Change plan to free"""
        updated = queryset.update(plan_type='free')
        self.message_user(request, f'{updated} tenant(s) changed to free plan.')
    change_to_free.short_description = 'Change to free plan'
    
    def change_to_starter(self, request, queryset):
        """Change plan to starter"""
        updated = queryset.update(plan_type='starter')
        self.message_user(request, f'{updated} tenant(s) changed to starter plan.')
    change_to_starter.short_description = 'Change to starter plan'
    
    def change_to_professional(self, request, queryset):
        """Change plan to professional"""
        updated = queryset.update(plan_type='professional')
        self.message_user(request, f'{updated} tenant(s) changed to professional plan.')
    change_to_professional.short_description = 'Change to professional plan'
    
    def change_to_enterprise(self, request, queryset):
        """Change plan to enterprise"""
        updated = queryset.update(plan_type='enterprise')
        self.message_user(request, f'{updated} tenant(s) changed to enterprise plan.')
    change_to_enterprise.short_description = 'Change to enterprise plan'
