from django.db import models
from apps.core.models import TimeStampedModel


class Tenant(TimeStampedModel):
    """
    Multi-tenant organization model
    """
    name = models.CharField(max_length=200)
    subdomain = models.CharField(max_length=100, unique=True, db_index=True)

    # Plan & limits
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    max_users = models.IntegerField(default=10)
    max_contracts = models.IntegerField(default=1000)
    max_storage_gb = models.IntegerField(default=100)

    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)

    # Billing
    billing_email = models.EmailField(blank=True)
    billing_info = models.JSONField(default=dict, blank=True)

    # Settings
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'tenants'
        ordering = ['name']
        indexes = [
            models.Index(fields=['subdomain']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.name

    def get_rate_limits(self):
        """Get rate limits for tenant's plan"""
        from django.conf import settings
        return settings.RATE_LIMITS.get(self.plan_type, settings.RATE_LIMITS['free'])