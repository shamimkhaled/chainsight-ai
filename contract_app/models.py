from django.db import models
from django.contrib.auth.models import User
import uuid

class ContractAnalysis(models.Model):
    INDUSTRY_CHOICES = [
        ('garment', 'Garment'),
        ('it', 'Information Technology'),
        ('construction', 'Construction'),
        ('general', 'General'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    LANGUAGE_CHOICES = [
        ('english', 'English'),
        ('bengali', 'Bengali'),
        # ('french', 'French'),
        # ('german', 'German'),
        # ('chinese', 'Chinese'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_ip = models.GenericIPAddressField()
    file = models.FileField(upload_to='contracts/%Y/%m/%d/')
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='english')
    
    # Analysis Results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    extracted_text = models.TextField(blank=True)
    risk_score = models.IntegerField(null=True, blank=True)
    analysis_result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    is_scanned_pdf = models.BooleanField(null=True, blank=True)
    ocr_method_used = models.CharField(max_length=50, blank=True)
    processing_time_seconds = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_ip', 'created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['industry']),
        ]
    
    def __str__(self):
        return f"{self.original_filename} - {self.status}"

class RateLimitTracker(models.Model):
    user_ip = models.GenericIPAddressField(unique=True)
    daily_count = models.PositiveIntegerField(default=0)
    last_reset_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user_ip} - {self.daily_count}/5"
