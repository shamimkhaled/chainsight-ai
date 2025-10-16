from django.db import models
from django.conf import settings
from apps.core.models import TenantAwareModel


class AlertRule(TenantAwareModel):
    """
    Alert rule configuration
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Rule type
    ALERT_TYPE_CHOICES = [
        ('risk_threshold', 'Risk Threshold'),
        ('expiry', 'Contract Expiry'),
        ('compliance', 'Compliance Violation'),
        ('supplier_risk', 'Supplier Risk'),
        ('custom', 'Custom'),
    ]
    alert_type = models.CharField(max_length=100, choices=ALERT_TYPE_CHOICES)
    category = models.CharField(max_length=100, blank=True)

    # Conditions
    conditions = models.JSONField(default=dict, blank=True)
    threshold_value = models.FloatField(null=True, blank=True)
    comparison_operator = models.CharField(max_length=20, blank=True)

    # Alert configuration
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    priority = models.IntegerField(default=5)

    # Notification channels
    notify_email = models.BooleanField(default=True)
    notify_sms = models.BooleanField(default=False)
    notify_whatsapp = models.BooleanField(default=False)
    notify_erp = models.BooleanField(default=False)
    notify_webhook = models.BooleanField(default=False)

    # Recipients
    recipients = models.JSONField(default=list, blank=True)

    # Scheduling
    is_active = models.BooleanField(default=True)
    FREQUENCY_CHOICES = [
        ('realtime', 'Real-time'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    check_frequency = models.CharField(max_length=50, choices=FREQUENCY_CHOICES)

    # Rate limiting
    cooldown_period = models.IntegerField(default=3600)  # seconds
    max_alerts_per_day = models.IntegerField(default=10)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_alert_rules'
    )

    class Meta:
        db_table = 'alert_rules'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['alert_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.alert_type})"


class Alert(TenantAwareModel):
    """
    Alert instance
    """
    alert_rule = models.ForeignKey(
        AlertRule,
        on_delete=models.SET_NULL,
        null=True,
        related_name='alerts'
    )

    # Alert details
    alert_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=20)
    title = models.CharField(max_length=500)
    message = models.TextField()

    # Related objects
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alerts'
    )
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alerts'
    )

    # Alert data
    trigger_data = models.JSONField(default=dict, blank=True)
    context = models.JSONField(default=dict, blank=True)

    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Notification tracking
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    whatsapp_sent = models.BooleanField(default=False)
    erp_sent = models.BooleanField(default=False)
    webhook_sent = models.BooleanField(default=False)

    class Meta:
        db_table = 'alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', '-created_at']),
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['contract']),
            models.Index(fields=['supplier']),
        ]

    def __str__(self):
        return f"{self.title} - {self.severity}"


class NotificationLog(models.Model):
    """
    Notification delivery log
    """
    alert = models.ForeignKey(
        Alert,
        on_delete=models.CASCADE,
        related_name='notification_logs'
    )

    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('erp', 'ERP'),
        ('webhook', 'Webhook'),
    ]
    channel = models.CharField(max_length=50, choices=CHANNEL_CHOICES)
    recipient = models.CharField(max_length=500)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True)

    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Tracking IDs
    external_id = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'notification_logs'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['alert', 'channel']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.channel} to {self.recipient} - {self.status}"