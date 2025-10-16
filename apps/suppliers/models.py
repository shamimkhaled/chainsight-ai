from django.db import models
from django.conf import settings
from apps.core.models import TenantAwareModel


class Supplier(TenantAwareModel):
    """
    Supplier for risk management
    """
    counterparty = models.OneToOneField(
        'counterparties.Counterparty',
        on_delete=models.CASCADE,
        related_name='supplier_profile'
    )

    # Supplier details
    supplier_code = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True)
    TIER_CHOICES = [
        ('tier1', 'Tier 1'),
        ('tier2', 'Tier 2'),
        ('tier3', 'Tier 3'),
    ]
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, blank=True)

    # Performance metrics
    on_time_delivery_rate = models.FloatField(null=True, blank=True)
    quality_score = models.FloatField(null=True, blank=True)
    responsiveness_score = models.FloatField(null=True, blank=True)

    # Financial
    annual_spend = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    payment_terms_days = models.IntegerField(null=True, blank=True)

    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('blacklisted', 'Blacklisted'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)

    # Risk monitoring
    is_monitored = models.BooleanField(default=False)
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]
    monitoring_frequency = models.CharField(
        max_length=50,
        choices=FREQUENCY_CHOICES,
        blank=True
    )
    last_assessment_date = models.DateTimeField(null=True, blank=True)
    next_assessment_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'suppliers'
        ordering = ['counterparty__name']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['supplier_code']),
        ]

    def __str__(self):
        return f"{self.counterparty.name} ({self.supplier_code})"


class SupplierRiskAssessment(TenantAwareModel):
    """
    Supplier risk assessment record
    """
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='risk_assessments'
    )

    assessment_date = models.DateTimeField(auto_now_add=True)
    ASSESSMENT_TYPE_CHOICES = [
        ('initial', 'Initial'),
        ('periodic', 'Periodic'),
        ('triggered', 'Triggered'),
        ('adhoc', 'Ad-hoc'),
    ]
    assessment_type = models.CharField(max_length=50, choices=ASSESSMENT_TYPE_CHOICES)

    # Overall risk
    overall_risk_score = models.IntegerField()
    RISK_LEVEL_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    overall_risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES)
    risk_category = models.CharField(max_length=100, blank=True)

    # Risk categories
    financial_risk_score = models.IntegerField()
    operational_risk_score = models.IntegerField()
    compliance_risk_score = models.IntegerField()
    reputational_risk_score = models.IntegerField()
    geopolitical_risk_score = models.IntegerField()
    cyber_security_risk_score = models.IntegerField()

    # Detailed findings
    risk_factors = models.JSONField(default=list, blank=True)
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)

    # Data sources
    data_sources = models.JSONField(default=list, blank=True)
    external_data_fetched = models.BooleanField(default=False)

    # Assessor
    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='supplier_assessments'
    )
    assessment_method = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'supplier_risk_assessments'
        ordering = ['-assessment_date']
        indexes = [
            models.Index(fields=['supplier', '-assessment_date']),
            models.Index(fields=['overall_risk_level']),
        ]

    def __str__(self):
        return f"{self.supplier} - {self.assessment_date.date()} ({self.overall_risk_level})"