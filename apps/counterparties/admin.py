from django.contrib import admin
from apps.counterparties.models import Counterparty, ContractCounterparty


@admin.register(Counterparty)
class CounterpartyAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'entity_type', 'risk_level', 'is_verified',
        'country', 'tenant', 'created_at'
    ]
    list_filter = ['entity_type', 'risk_level', 'is_verified', 'country', 'tenant']
    search_fields = ['name', 'legal_name', 'registration_number', 'duns_number']
    ordering = ['name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('tenant', 'name', 'legal_name', 'entity_type')
        }),
        ('Registration', {
            'fields': ('registration_number', 'tax_id', 'duns_number')
        }),
        ('Contact Information', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code',
                      'contact_email', 'contact_phone', 'website')
        }),
        ('Risk Assessment', {
            'fields': ('risk_score', 'risk_level', 'credit_score', 'credit_rating')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_source', 'verification_date')
        }),
        ('External Data', {
            'fields': ('external_data',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']


@admin.register(ContractCounterparty)
class ContractCounterpartyAdmin(admin.ModelAdmin):
    list_display = ['contract', 'counterparty', 'role', 'is_primary']
    list_filter = ['role', 'is_primary']
    search_fields = ['contract__original_filename', 'counterparty__name']