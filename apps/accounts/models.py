from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from apps.core.models import TimeStampedModel
from apps.accounts.managers import CustomUserManager


class WaitlistEntry(TimeStampedModel):
    """
    Waitlist for interested users before full launch
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)

    # Interest level
    INTEREST_CHOICES = [
        ('low', 'Just curious'),
        ('medium', 'Planning to use soon'),
        ('high', 'Need this urgently'),
    ]
    interest_level = models.CharField(max_length=20, choices=INTEREST_CHOICES, default='medium')

    # Source tracking
    referral_source = models.CharField(max_length=100, blank=True)
    signup_source = models.CharField(max_length=100, default='website')

    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('converted', 'Converted'),
        ('unsubscribed', 'Unsubscribed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Communication preferences
    email_opt_in = models.BooleanField(default=True)
    sms_opt_in = models.BooleanField(default=False)

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'waitlist_entries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['interest_level']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.email} - {self.company_name or 'Individual'}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email


class DemoRequest(TimeStampedModel):
    """
    Demo booking requests from potential customers
    """
    # Contact information
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)

    # Demo preferences
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')

    # Demo details
    company_size = models.CharField(max_length=50, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    current_solution = models.CharField(max_length=200, blank=True)

    # Specific interests
    INTEREST_CHOICES = [
        ('contract_analysis', 'Contract Analysis'),
        ('risk_assessment', 'Risk Assessment'),
        ('compliance_monitoring', 'Compliance Monitoring'),
        ('multi_tenant_setup', 'Multi-Tenant Setup'),
        ('integration_apis', 'API Integrations'),
        ('full_platform', 'Full Platform Demo'),
    ]
    interests = models.JSONField(default=list, blank=True)  # Array of interests

    # Additional requirements
    special_requirements = models.TextField(blank=True)
    attendees = models.IntegerField(default=1)

    # Status tracking
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Scheduling
    scheduled_date = models.DateTimeField(null=True, blank=True)
    meeting_link = models.URLField(blank=True)
    calendar_event_id = models.CharField(max_length=200, blank=True)

    # Follow-up
    notes = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)

    # Communication
    email_opt_in = models.BooleanField(default=True)

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referral_source = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'demo_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['preferred_date']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} - {self.company_name or 'Individual'}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def get_meeting_datetime(self):
        if self.scheduled_date:
            return self.scheduled_date
        elif self.preferred_date and self.preferred_time:
            # Combine date and time in user's timezone
            from datetime import datetime
            return datetime.combine(self.preferred_date, self.preferred_time)
        return None


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Custom user model
    """
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='users'
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=50, blank=True)

    # Role & permissions
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('user', 'User'),
        ('viewer', 'Viewer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    # Status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    # Security
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=100, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        unique_together = ['tenant', 'email']
        indexes = [
            models.Index(fields=['tenant', 'email']),
            models.Index(fields=['tenant', 'role']),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email