from django.db import models
from django.conf import settings
from apps.core.models import TenantAwareModel


class ContractTemplate(TenantAwareModel):
    """
    Contract templates for quick creation
    """
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    
    # Template content
    template_text = models.TextField()
    
    CATEGORY_CHOICES = [
        ('nda', 'Non-Disclosure Agreement'),
        ('service', 'Service Agreement'),
        ('employment', 'Employment Contract'),
        ('lease', 'Lease Agreement'),
        ('sales', 'Sales Contract'),
        ('partnership', 'Partnership Agreement'),
        ('other', 'Other'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    
    # Template variables (JSON list of variables to replace)
    variables = models.JSONField(default=list, blank=True)
    
    # Template clauses
    clauses = models.JSONField(default=list, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)  # Shared templates
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    
    # File attachments
    file_path = models.CharField(max_length=1000, blank=True)
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'contract_templates'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'category']),
            models.Index(fields=['is_active', 'is_public']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.category})"


class AIAgent(TenantAwareModel):
    """
    AI agents for automated contract processing
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    AGENT_TYPE_CHOICES = [
        ('review', 'Contract Review Agent'),
        ('compliance', 'Compliance Check Agent'),
        ('extraction', 'Data Extraction Agent'),
        ('comparison', 'Document Comparison Agent'),
        ('summarization', 'Summarization Agent'),
        ('risk_assessment', 'Risk Assessment Agent'),
        ('translation', 'Translation Agent'),
        ('redlining', 'Redlining Agent'),
    ]
    agent_type = models.CharField(max_length=50, choices=AGENT_TYPE_CHOICES)
    
    # Configuration
    config = models.JSONField(default=dict, blank=True)
    
    # Automation rules
    trigger_conditions = models.JSONField(default=dict, blank=True)
    actions = models.JSONField(default=list, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Execution tracking
    total_executions = models.IntegerField(default=0)
    successful_executions = models.IntegerField(default=0)
    failed_executions = models.IntegerField(default=0)
    last_execution_at = models.DateTimeField(null=True, blank=True)
    
    # AI model configuration
    model_used = models.CharField(max_length=100, default='gpt-4')
    temperature = models.FloatField(default=0.3)
    max_tokens = models.IntegerField(default=2000)
    
    class Meta:
        db_table = 'ai_agents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'agent_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.agent_type})"


class AgentExecution(TenantAwareModel):
    """
    Track AI agent executions
    """
    agent = models.ForeignKey(
        AIAgent,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='agent_executions',
        null=True,
        blank=True
    )
    
    # Execution details
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Input/Output
    input_data = models.JSONField(default=dict, blank=True)
    output_data = models.JSONField(default=dict, blank=True)
    
    # Performance metrics
    execution_time = models.FloatField(null=True, blank=True)  # seconds
    tokens_used = models.IntegerField(null=True, blank=True)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    
    # Results
    result_summary = models.TextField(blank=True)
    
    class Meta:
        db_table = 'agent_executions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent', '-created_at']),
            models.Index(fields=['contract']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.agent.name} - {self.status}"


class DocumentComparison(TenantAwareModel):
    """
    Document and clause comparison results
    """
    name = models.CharField(max_length=500)
    
    # Documents being compared
    source_contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='comparisons_as_source'
    )
    target_contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='comparisons_as_target'
    )
    
    # Comparison type
    COMPARISON_TYPE_CHOICES = [
        ('full_document', 'Full Document'),
        ('specific_clauses', 'Specific Clauses'),
        ('key_terms', 'Key Terms Only'),
    ]
    comparison_type = models.CharField(max_length=50, choices=COMPARISON_TYPE_CHOICES)
    
    # Results
    differences = models.JSONField(default=list, blank=True)
    similarities = models.JSONField(default=list, blank=True)
    similarity_score = models.FloatField(null=True, blank=True)  # 0-100
    
    # Redline document
    redline_document_path = models.CharField(max_length=1000, blank=True)
    
    # Analysis
    risk_changes = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    
    # Metadata
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'document_comparisons'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', '-created_at']),
            models.Index(fields=['source_contract']),
            models.Index(fields=['target_contract']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.similarity_score}% similar"


class WorkflowTemplate(TenantAwareModel):
    """
    Due diligence and review workflow templates
    """
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    
    WORKFLOW_TYPE_CHOICES = [
        ('due_diligence', 'Due Diligence'),
        ('contract_review', 'Contract Review'),
        ('compliance_check', 'Compliance Check'),
        ('approval_process', 'Approval Process'),
        ('negotiation', 'Negotiation'),
    ]
    workflow_type = models.CharField(max_length=50, choices=WORKFLOW_TYPE_CHOICES)
    
    # Workflow steps
    steps = models.JSONField(default=list, blank=True)
    
    # Assignments
    default_assignees = models.JSONField(default=dict, blank=True)
    
    # SLAs
    sla_hours = models.IntegerField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'workflow_templates'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class WorkflowInstance(TenantAwareModel):
    """
    Active workflow instances
    """
    template = models.ForeignKey(
        WorkflowTemplate,
        on_delete=models.SET_NULL,
        null=True,
        related_name='instances'
    )
    
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='workflows'
    )
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Current step
    current_step = models.IntegerField(default=0)
    
    # Assignments
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='assigned_workflows'
    )
    
    # Deadlines
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Progress
    progress_percentage = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'workflow_instances'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['contract']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.template.name if self.template else 'Workflow'} - {self.contract.original_filename}"


class ContractComment(TenantAwareModel):
    """
    Comments and annotations on contracts
    """
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contract_comments'
    )
    
    # Comment content
    content = models.TextField()
    
    # Location in document
    clause_id = models.UUIDField(null=True, blank=True)
    page_number = models.IntegerField(null=True, blank=True)
    highlighted_text = models.TextField(blank=True)
    
    # Comment type
    COMMENT_TYPE_CHOICES = [
        ('general', 'General Comment'),
        ('question', 'Question'),
        ('issue', 'Issue/Concern'),
        ('suggestion', 'Suggestion'),
        ('approval', 'Approval'),
    ]
    comment_type = models.CharField(max_length=50, choices=COMMENT_TYPE_CHOICES, default='general')
    
    # Thread
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    # Resolution
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_comments'
    )
    
    class Meta:
        db_table = 'contract_comments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['contract', '-created_at']),
            models.Index(fields=['user']),
            models.Index(fields=['is_resolved']),
        ]
    
    def __str__(self):
        return f"Comment by {self.user.email} on {self.contract.original_filename}"

