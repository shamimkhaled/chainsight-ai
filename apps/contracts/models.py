from django.db import models
from django.conf import settings
from apps.core.models import TenantAwareModel


class Contract(TenantAwareModel):
    """
    Main contract model
    """
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_contracts'
    )

    # File information
    original_filename = models.CharField(max_length=500)
    file_path = models.CharField(max_length=1000)  # S3 path
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=50)
    file_hash = models.CharField(max_length=64, db_index=True)  # SHA-256

    # Processing status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processing_stage = models.CharField(max_length=100, blank=True)
    progress_percentage = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)

    # Contract details
    contract_type = models.CharField(max_length=100, blank=True)
    INDUSTRY_CHOICES = [
        ('manufacturing', 'Manufacturing'),
        ('it', 'IT'),
        ('law_firm', 'Law Firm'),
        ('construction', 'Construction'),
        ('general', 'General'),
    ]
    industry = models.CharField(max_length=100, choices=INDUSTRY_CHOICES, default='general')
    language = models.CharField(max_length=50, default='english')
    contract_date = models.DateField(null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True, db_index=True)
    contract_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, blank=True)

    # Parties
    counterparties = models.JSONField(default=list, blank=True)

    # Analysis results
    risk_score = models.IntegerField(null=True, blank=True, db_index=True)
    compliance_score = models.IntegerField(null=True, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)

    # OCR info
    is_scanned_pdf = models.BooleanField(default=False)
    ocr_method_used = models.CharField(max_length=50, blank=True)

    # Repository
    folder_path = models.CharField(max_length=1000, blank=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    analyzed_at = models.DateTimeField(null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'contracts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['risk_score']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['file_hash']),
        ]

    def __str__(self):
        return f"{self.original_filename} - {self.status}"


class ContractAnalysis(TenantAwareModel):
    """
    Contract analysis results
    """
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name='analysis'
    )

    # MongoDB reference
    mongo_document_id = models.CharField(max_length=100)

    # Quick access fields
    overall_risk_score = models.IntegerField()
    critical_issues_count = models.IntegerField(default=0)
    missing_clauses_count = models.IntegerField(default=0)
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    priority_level = models.CharField(max_length=20, choices=PRIORITY_CHOICES)

    # Processing info
    processing_time = models.FloatField()
    model_used = models.CharField(max_length=100)
    model_version = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'contract_analyses'

    def __str__(self):
        return f"Analysis for {self.contract.original_filename}"


class Clause(TenantAwareModel):
    """
    Contract clauses
    """
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='clauses'
    )

    # Identification
    clause_number = models.CharField(max_length=50, blank=True)
    CLAUSE_TYPE_CHOICES = [
        ('payment', 'Payment Terms'),
        ('termination', 'Termination'),
        ('liability', 'Liability'),
        ('confidentiality', 'Confidentiality'),
        ('intellectual_property', 'Intellectual Property'),
        ('force_majeure', 'Force Majeure'),
        ('dispute_resolution', 'Dispute Resolution'),
        ('governing_law', 'Governing Law'),
        ('warranties', 'Warranties'),
        ('other', 'Other'),
    ]
    clause_type = models.CharField(max_length=100, choices=CLAUSE_TYPE_CHOICES)
    clause_category = models.CharField(max_length=100, blank=True)

    # Content
    title = models.CharField(max_length=500, blank=True)
    content = models.TextField()
    content_hash = models.CharField(max_length=64)

    # Location in document
    page_number = models.IntegerField(null=True, blank=True)
    start_position = models.IntegerField(null=True, blank=True)
    end_position = models.IntegerField(null=True, blank=True)

    # Analysis
    RISK_LEVEL_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, blank=True)
    quality_score = models.IntegerField(null=True, blank=True)
    completeness_score = models.IntegerField(null=True, blank=True)
    is_standard = models.BooleanField(default=False)
    has_issues = models.BooleanField(default=False)

    # Metadata
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'clauses'
        ordering = ['contract', 'clause_number']
        indexes = [
            models.Index(fields=['contract', 'clause_type']),
        ]

    def __str__(self):
        return f"{self.clause_number} - {self.clause_type}"