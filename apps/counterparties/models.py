from django.db import models
from apps.core.models import TenantAwareModel


class Counterparty(TenantAwareModel):
    """
    Contract counterparty/entity
    """
    # Basic information
    name = models.CharField(max_length=500)
    legal_name = models.CharField(max_length=500, blank=True)
    entity_type = models.CharField(max_length=100, blank=True)
    registration_number = models.CharField(max_length=100, blank=True, db_index=True)
    tax_id = models.CharField(max_length=100, blank=True)

    # Contact
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)

    # Risk assessment
    risk_score = models.IntegerField(null=True, blank=True)
    RISK_LEVEL_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, blank=True)
    credit_score = models.IntegerField(null=True, blank=True)
    credit_rating = models.CharField(max_length=10, blank=True)

    # Verification
    is_verified = models.BooleanField(default=False)
    verification_source = models.CharField(max_length=100, blank=True)
    verification_date = models.DateTimeField(null=True, blank=True)

    # External data
    duns_number = models.CharField(max_length=50, blank=True, db_index=True)
    external_data = models.JSONField(default=dict, blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'counterparties'
        verbose_name_plural = 'counterparties'
        ordering = ['name']
        indexes = [
            models.Index(fields=['tenant', 'name']),
            models.Index(fields=['registration_number']),
            models.Index(fields=['duns_number']),
        ]

    def __str__(self):
        return self.name


class ContractCounterparty(models.Model):
    """
    Many-to-many relationship between contracts and counterparties
    """
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='contract_counterparties'
    )
    counterparty = models.ForeignKey(
        Counterparty,
        on_delete=models.CASCADE,
        related_name='contract_counterparties'
    )

    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('supplier', 'Supplier'),
        ('contractor', 'Contractor'),
        ('client', 'Client'),
        ('vendor', 'Vendor'),
        ('other', 'Other'),
    ]
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'contract_counterparties'
        unique_together = ['contract', 'counterparty', 'role']
        indexes = [
            models.Index(fields=['contract']),
            models.Index(fields=['counterparty']),
        ]

    def __str__(self):
        return f"{self.counterparty.name} ({self.role}) - {self.contract.original_filename}"