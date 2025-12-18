from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from apps.chat.models import ChatSession, ChatMessage, ContractEmbedding


class ChatMessageInline(admin.TabularInline):
    """Inline admin for Chat Messages"""
    model = ChatMessage
    extra = 0
    fields = ['role', 'message_preview', 'helpful', 'created_at']
    readonly_fields = fields
    can_delete = False
    max_num = 10
    
    def message_preview(self, obj):
        """Show preview of message"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    message_preview.short_description = 'Message'
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """Admin interface for Chat Sessions"""
    
    list_display = [
        'title', 'tenant_link', 'user_link',
        'message_count', 'contract_count', 'is_active',
        'created_at', 'last_message_at'
    ]
    
    list_filter = [
        'is_active', 'created_at', 'last_message_at', 'tenant'
    ]
    
    search_fields = [
        'title', 'user__email', 'tenant__name'
    ]
    
    readonly_fields = [
        'id', 'message_count', 'created_at',
        'updated_at', 'last_message_at'
    ]
    
    fieldsets = (
        ('Session Information', {
            'fields': (
                'id', 'tenant', 'user', 'title',
                'is_active', 'metadata'
            )
        }),
        ('Contracts', {
            'fields': ('contracts',)
        }),
        ('Statistics', {
            'fields': (
                'message_count', 'last_message_at'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    filter_horizontal = ['contracts']
    inlines = [ChatMessageInline]
    
    actions = ['archive_sessions', 'activate_sessions']
    
    def tenant_link(self, obj):
        """Display tenant as link"""
        if obj.tenant:
            url = reverse('admin:tenants_tenant_change', args=[obj.tenant.id])
            return format_html('<a href="{}">{}</a>', url, obj.tenant.name)
        return '-'
    tenant_link.short_description = 'Tenant'
    
    def user_link(self, obj):
        """Display user as link"""
        if obj.user:
            url = reverse('admin:accounts_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return '-'
    user_link.short_description = 'User'
    
    def contract_count(self, obj):
        """Count of contracts"""
        return obj.contracts.count()
    contract_count.short_description = 'Contracts'
    
    def archive_sessions(self, request, queryset):
        """Archive sessions"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} session(s) archived.')
    archive_sessions.short_description = 'Archive selected sessions'
    
    def activate_sessions(self, request, queryset):
        """Activate sessions"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} session(s) activated.')
    activate_sessions.short_description = 'Activate selected sessions'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin interface for Chat Messages"""
    
    list_display = [
        'session_link', 'role', 'message_preview',
        'helpful_badge', 'created_at'
    ]
    
    list_filter = [
        'role', 'helpful', 'created_at', 'session__tenant'
    ]
    
    search_fields = [
        'content', 'session__title', 'session__user__email'
    ]
    
    readonly_fields = [
        'id', 'session', 'role', 'content',
        'sources', 'context_used', 'created_at'
    ]
    
    fieldsets = (
        ('Message Information', {
            'fields': (
                'id', 'session', 'role',
                'content', 'helpful'
            )
        }),
        ('RAG Context', {
            'fields': ('sources', 'context_used'),
            'classes': ('collapse',)
        }),
        ('AI Metadata', {
            'fields': ('tokens_used', 'processing_time'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def session_link(self, obj):
        """Display session as link"""
        url = reverse('admin:chat_chatsession_change', args=[obj.session.id])
        return format_html('<a href="{}">{}</a>', url, obj.session.title)
    session_link.short_description = 'Session'
    
    def message_preview(self, obj):
        """Show preview of message"""
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
    message_preview.short_description = 'Message'
    
    def helpful_badge(self, obj):
        """Display helpful as emoji"""
        if obj.helpful is True:
            return '👍'
        elif obj.helpful is False:
            return '👎'
        return '-'
    helpful_badge.short_description = 'Feedback'


@admin.register(ContractEmbedding)
class ContractEmbeddingAdmin(admin.ModelAdmin):
    """Admin interface for Contract Embeddings"""
    
    list_display = [
        'contract_link', 'chunk_index', 'page_number',
        'embedding_model', 'created_at'
    ]
    
    list_filter = [
        'embedding_model', 'created_at', 'contract__tenant'
    ]
    
    search_fields = [
        'contract__original_filename', 'text_chunk',
        'vector_id'
    ]
    
    readonly_fields = [
        'id', 'contract', 'vector_id', 'created_at'
    ]
    
    fieldsets = (
        ('Embedding Information', {
            'fields': (
                'id', 'contract', 'chunk_index',
                'text_chunk', 'page_number'
            )
        }),
        ('Vector Data', {
            'fields': (
                'vector_id', 'embedding_model', 'metadata'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def contract_link(self, obj):
        """Display contract as link"""
        url = reverse('admin:contracts_contract_change', args=[obj.contract.id])
        return format_html(
            '<a href="{}">{}</a>',
            url, obj.contract.original_filename
        )
    contract_link.short_description = 'Contract'

