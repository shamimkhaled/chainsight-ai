from django.contrib import admin
from apps.tenants.models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'subdomain', 'plan_type', 'status', 'is_active', 'created_at']
    list_filter = ['plan_type', 'status', 'is_active']
    search_fields = ['name', 'subdomain']
    ordering = ['name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'subdomain')
        }),
        ('Plan & Limits', {
            'fields': ('plan_type', 'max_users', 'max_contracts', 'max_storage_gb')
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
        ('Billing', {
            'fields': ('billing_email', 'billing_info'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('settings',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']