from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.chat.models import ChatSession, ChatMessage
from apps.chat.serializers import (
    ChatSessionSerializer,
    ChatSessionListSerializer,
    ChatMessageSerializer,
    ChatQuerySerializer
)
from apps.chat.services.rag_service import RAGChatService
from apps.core.permissions import IsTenantMember


class ChatSessionViewSet(viewsets.ModelViewSet):
    """
    RAG Chat session management
    
    list: Get list of chat sessions
    retrieve: Get session with full message history
    create: Create new chat session
    destroy: Delete chat session
    """
    permission_classes = [IsAuthenticated, IsTenantMember]
    queryset = ChatSession.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']

    def get_queryset(self):
        """Filter sessions by tenant and user"""
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return ChatSession.objects.none()
        return ChatSession.objects.filter(
            tenant=self.request.user.tenant,
            user=self.request.user
        ).prefetch_related('messages', 'contracts')

    def get_serializer_class(self):
        if self.action == 'list':
            return ChatSessionListSerializer
        return ChatSessionSerializer

    def perform_create(self, serializer):
        """Create session for current user"""
        serializer.save(
            tenant=self.request.user.tenant,
            user=self.request.user
        )

    @action(detail=True, methods=['post'])
    def query(self, request, pk=None):
        """
        Send a query to the RAG system
        
        POST /api/v2/chat/sessions/{id}/query/
        Body: { "message": "What are the payment terms?", "contract_ids": [...] }
        """
        session = self.get_object()
        serializer = ChatQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message = serializer.validated_data['message']
        contract_ids = serializer.validated_data.get('contract_ids', [])
        use_history = serializer.validated_data.get('use_history', True)
        
        # If no specific contracts, use all contracts in session
        if not contract_ids:
            contract_ids = list(session.contracts.values_list('id', flat=True))
        
        # Get chat history if needed
        chat_history = []
        if use_history:
            recent_messages = session.messages.all().order_by('-created_at')[:10]
            chat_history = [
                {
                    'role': msg.role,
                    'content': msg.content
                }
                for msg in reversed(recent_messages)
            ]
        
        # Save user message
        user_message = ChatMessage.objects.create(
            tenant=request.user.tenant,
            session=session,
            role='user',
            content=message
        )
        
        # Process with RAG service
        rag_service = RAGChatService()
        result = rag_service.query_contracts(
            query=message,
            contract_ids=[str(cid) for cid in contract_ids],
            chat_history=chat_history
        )
        
        # Save assistant response
        assistant_message = ChatMessage.objects.create(
            tenant=request.user.tenant,
            session=session,
            role='assistant',
            content=result['answer'],
            sources=result['sources'],
            context_used=result['context_used'],
            tokens_used=result['tokens_used']
        )
        
        # Update session
        session.message_count += 2
        session.save()
        
        return Response({
            'user_message': ChatMessageSerializer(user_message).data,
            'assistant_message': ChatMessageSerializer(assistant_message).data,
            'sources': result['sources']
        })

    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """
        Clear all messages in session
        
        POST /api/v2/chat/sessions/{id}/clear/
        """
        session = self.get_object()
        session.messages.all().delete()
        session.message_count = 0
        session.save()
        
        return Response({'message': 'Chat history cleared successfully'})

    @action(detail=True, methods=['post'])
    def add_contracts(self, request, pk=None):
        """
        Add contracts to session context
        
        POST /api/v2/chat/sessions/{id}/add_contracts/
        Body: { "contract_ids": [...] }
        """
        session = self.get_object()
        contract_ids = request.data.get('contract_ids', [])
        
        from apps.contracts.models import Contract
        contracts = Contract.objects.filter(
            id__in=contract_ids,
            tenant=request.user.tenant
        )
        
        session.contracts.add(*contracts)
        
        return Response({
            'message': f'{contracts.count()} contracts added to session',
            'total_contracts': session.contracts.count()
        })


class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Chat message management (read-only)
    
    list: Get messages for a session
    retrieve: Get specific message
    """
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = ChatMessageSerializer
    queryset = ChatMessage.objects.all()

    def get_queryset(self):
        """Filter messages by tenant"""
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return ChatMessage.objects.none()
        return ChatMessage.objects.filter(
            tenant=self.request.user.tenant
        ).select_related('session')

    @action(detail=True, methods=['post'])
    def feedback(self, request, pk=None):
        """
        Provide feedback on a message
        
        POST /api/v2/chat/messages/{id}/feedback/
        Body: { "helpful": true, "feedback": "Great answer!" }
        """
        message = self.get_object()
        
        message.helpful = request.data.get('helpful')
        message.feedback = request.data.get('feedback', '')
        message.save()
        
        return Response({
            'message': 'Feedback recorded successfully',
            'message_id': str(message.id)
        })

