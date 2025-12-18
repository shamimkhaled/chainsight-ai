from django.db import models
from django.conf import settings
from apps.core.models import TenantAwareModel


class Integration(TenantAwareModel):
    """
    External system integrations
    """
    name = models.CharField(max_length=200)
    
    INTEGRATION_TYPE_CHOICES = [
        ('microsoft_word', 'Microsoft Word'),
        ('google_docs', 'Google Docs'),
        ('microsoft_teams', 'Microsoft Teams'),
        ('slack', 'Slack'),
        ('salesforce', 'Salesforce'),
        ('hubspot', 'HubSpot'),
        ('sap', 'SAP ERP'),
        ('oracle', 'Oracle ERP'),
        ('netsuite', 'NetSuite'),
        ('docusign', 'DocuSign'),
        ('adobe_sign', 'Adobe Sign'),
        ('sharepoint', 'SharePoint'),
        ('dropbox', 'Dropbox'),
        ('box', 'Box'),
        ('webhook', 'Custom Webhook'),
    ]
    integration_type = models.CharField(max_length=50, choices=INTEGRATION_TYPE_CHOICES)
    
    # Configuration
    config = models.JSONField(default=dict, blank=True)
    credentials = models.JSONField(default=dict, blank=True)  # Encrypted in production
    
    # OAuth tokens
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_connected = models.BooleanField(default=False)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    
    # Sync settings
    auto_sync = models.BooleanField(default=False)
    sync_interval = models.CharField(max_length=50, default='daily')  # hourly, daily, weekly
    
    # Error tracking
    last_error = models.TextField(blank=True)
    error_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'integrations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'integration_type']),
            models.Index(fields=['is_active', 'is_connected']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.integration_type})"


class IntegrationLog(TenantAwareModel):
    """
    Integration activity logs
    """
    integration = models.ForeignKey(
        Integration,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    
    ACTION_CHOICES = [
        ('sync', 'Sync'),
        ('import', 'Import'),
        ('export', 'Export'),
        ('webhook', 'Webhook'),
        ('error', 'Error'),
    ]
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    
    # Request/Response
    request_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    
    # Performance
    execution_time = models.FloatField(null=True, blank=True)  # seconds
    
    class Meta:
        db_table = 'integration_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['integration', '-created_at']),
            models.Index(fields=['status']),
        ]


class ERPEntity(TenantAwareModel):
    """
    ERP system entities (vendors, purchase orders, etc.)
    """
    integration = models.ForeignKey(
        Integration,
        on_delete=models.CASCADE,
        related_name='erp_entities'
    )
    
    ENTITY_TYPE_CHOICES = [
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
        ('purchase_order', 'Purchase Order'),
        ('invoice', 'Invoice'),
        ('contract', 'Contract'),
    ]
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPE_CHOICES)
    
    # External IDs
    external_id = models.CharField(max_length=200, db_index=True)
    external_reference = models.CharField(max_length=200, blank=True)
    
    # Entity data
    entity_data = models.JSONField(default=dict, blank=True)
    
    # ChainSight mapping
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='erp_entities'
    )
    
    counterparty = models.ForeignKey(
        'counterparties.Counterparty',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='erp_entities'
    )
    
    # Sync info
    last_synced_at = models.DateTimeField(auto_now=True)
    sync_status = models.CharField(max_length=50, default='synced')
    
    class Meta:
        db_table = 'erp_entities'
        ordering = ['-created_at']
        unique_together = ['integration', 'entity_type', 'external_id']
        indexes = [
            models.Index(fields=['integration', 'entity_type']),
            models.Index(fields=['external_id']),
        ]
    
    def __str__(self):
        return f"{self.entity_type} - {self.external_id}"


class DocumentSync(TenantAwareModel):
    """
    Document sync with cloud storage (Google Docs, Word Online, etc.)
    """
    integration = models.ForeignKey(
        Integration,
        on_delete=models.CASCADE,
        related_name='document_syncs'
    )
    
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='document_syncs'
    )
    
    # External document info
    external_document_id = models.CharField(max_length=500)
    external_document_url = models.URLField(max_length=1000)
    
    # Sync settings
    sync_direction = models.CharField(
        max_length=50,
        choices=[
            ('to_external', 'ChainSight to External'),
            ('from_external', 'External to ChainSight'),
            ('bidirectional', 'Bidirectional'),
        ],
        default='bidirectional'
    )
    
    auto_sync = models.BooleanField(default=True)
    
    # Version tracking
    local_version = models.IntegerField(default=1)
    external_version = models.IntegerField(default=1)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    
    # Conflict resolution
    has_conflicts = models.BooleanField(default=False)
    conflict_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'document_syncs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['integration', 'contract']),
            models.Index(fields=['external_document_id']),
        ]

