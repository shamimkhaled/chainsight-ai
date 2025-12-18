from django.db import models
from django.conf import settings
from apps.core.models import TenantAwareModel


class ChatSession(TenantAwareModel):
    """
    RAG chat session for contract queries
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions'
    )
    
    # Session info
    title = models.CharField(max_length=500, blank=True)
    
    # Associated contracts for context
    contracts = models.ManyToManyField(
        'contracts.Contract',
        related_name='chat_sessions',
        blank=True
    )
    
    # Session metadata
    is_active = models.BooleanField(default=True)
    last_message_at = models.DateTimeField(auto_now=True)
    message_count = models.IntegerField(default=0)
    
    # AI model configuration
    model_used = models.CharField(max_length=100, default='gpt-4')
    temperature = models.FloatField(default=0.7)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-last_message_at']
        indexes = [
            models.Index(fields=['tenant', 'user', '-last_message_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Chat Session: {self.title or self.id} - {self.user.email}"


class ChatMessage(TenantAwareModel):
    """
    Individual messages in a chat session
    """
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    # Message content
    content = models.TextField()
    
    # References (for RAG)
    sources = models.JSONField(default=list, blank=True)  # Source documents/clauses
    context_used = models.TextField(blank=True)  # Context retrieved from vector DB
    
    # AI metadata
    tokens_used = models.IntegerField(null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True)  # seconds
    
    # User feedback
    helpful = models.BooleanField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class ContractEmbedding(models.Model):
    """
    Vector embeddings for contract content (for RAG)
    """
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='embeddings'
    )
    
    # Text chunk
    chunk_text = models.TextField()
    chunk_index = models.IntegerField()
    
    # Pinecone reference
    vector_id = models.CharField(max_length=200, unique=True)
    
    # Metadata for retrieval
    clause_type = models.CharField(max_length=100, blank=True)
    page_number = models.IntegerField(null=True, blank=True)
    
    # Embedding metadata
    embedding_model = models.CharField(max_length=100, default='text-embedding-ada-002')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'contract_embeddings'
        ordering = ['contract', 'chunk_index']
        indexes = [
            models.Index(fields=['contract', 'chunk_index']),
            models.Index(fields=['vector_id']),
        ]
    
    def __str__(self):
        return f"Embedding {self.chunk_index} for {self.contract.original_filename}"

