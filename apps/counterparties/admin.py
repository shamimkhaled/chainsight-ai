from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from apps.counterparties.models import Counterparty, ContractCounterparty


class ContractCounterpartyInline(admin.TabularInline):
    """Inline admin for Contract Counterparties"""
    model = ContractCounterparty
    extra = 0
    fields = ['contract', 'role', 'is_primary']
    readonly_fields = ['contract']
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Counterparty)
class CounterpartyAdmin(admin.ModelAdmin):
    """Admin interface for Counterparties"""
    
    list_display = [
        'name', 'tenant_link', 'entity_type',
        'is_verified', 'risk_score', 'contract_count_display',
        'contact_email', 'created_at'
    ]
    
    list_filter = [
        'is_verified', 'risk_level', 'country', 'created_at', 'tenant'
    ]
    
    search_fields = [
        'name', 'legal_name', 'registration_number',
        'tax_id', 'contact_email', 'contact_phone',
        'address', 'city', 'country'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'verification_date'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id', 'tenant', 'name', 'legal_name',
                'entity_type'
            )
        }),
        ('Registration', {
            'fields': (
                'registration_number', 'tax_id',
                'duns_number', 'is_verified', 'verification_date'
            )
        }),
        ('Contact Information', {
            'fields': (
                'contact_email', 'contact_phone',
                'website', 'address', 'city',
                'state', 'postal_code', 'country'
            )
        }),
        ('Risk Assessment', {
            'fields': (
                'risk_score', 'risk_level',
                'credit_score', 'credit_rating'
            ),
            'classes': ('collapse',)
        }),
        ('External Data', {
            'fields': ('external_data',),
            'classes': ('collapse',)
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
    
    inlines = [ContractCounterpartyInline]
    
    actions = ['verify_counterparties', 'mark_as_high_risk']
    
    def tenant_link(self, obj):
        """Display tenant as link"""
        if obj.tenant:
            url = reverse('admin:tenants_tenant_change', args=[obj.tenant.id])
            return format_html('<a href="{}">{}</a>', url, obj.tenant.name)
        return '-'
    tenant_link.short_description = 'Tenant'
    
    def contract_count_display(self, obj):
        """Display contract count"""
        count = obj.contract_counterparties.count()
        return format_html(
            '<span style="background-color: #1E90FF; color: white; '
            'padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            count
        )
    contract_count_display.short_description = 'Contracts'
    
    def verify_counterparties(self, request, queryset):
        """Verify counterparties"""
        from django.utils import timezone
        updated = queryset.update(
            is_verified=True,
            verified_at=timezone.now()
        )
        self.message_user(request, f'{updated} counterparty(s) verified.')
    verify_counterparties.short_description = 'Verify selected'
    
    def mark_as_high_risk(self, request, queryset):
        """Mark as high risk"""
        updated = queryset.update(risk_score=80)
        self.message_user(request, f'{updated} counterparty(s) marked as high risk.')
    mark_as_high_risk.short_description = 'Mark as high risk'


@admin.register(ContractCounterparty)
class ContractCounterpartyAdmin(admin.ModelAdmin):
    """Admin interface for Contract-Counterparty relationships"""
    
    list_display = [
        'contract_link', 'counterparty_link',
        'role', 'is_primary'
    ]
    
    list_filter = [
        'role', 'is_primary',
        'contract__tenant'
    ]
    
    search_fields = [
        'contract__original_filename', 'counterparty__name'
    ]
    
    readonly_fields = ['id']
    
    fieldsets = (
        ('Relationship', {
            'fields': (
                'id', 'contract', 'counterparty',
                'role', 'is_primary'
            )
        }),
        ('Metadata', {
            'fields': ('metadata',),
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
    
    def counterparty_link(self, obj):
        """Display counterparty as link"""
        if obj.counterparty:
            url = reverse('admin:counterparties_counterparty_change', args=[obj.counterparty.id])
            return format_html('<a href="{}">{}</a>', url, obj.counterparty.name)
        return '-'
    counterparty_link.short_description = 'Counterparty'
