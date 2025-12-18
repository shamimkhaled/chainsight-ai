from rest_framework import serializers
from apps.chat.models import ChatSession, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'session', 'role', 'content', 'sources',
            'tokens_used', 'processing_time', 'helpful',
            'feedback', 'created_at'
        ]
        read_only_fields = [
            'id', 'tokens_used', 'processing_time', 'created_at'
        ]


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat sessions"""
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'title', 'contracts', 'is_active',
            'last_message_at', 'message_count', 'messages',
            'model_used', 'temperature', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'last_message_at', 'message_count',
            'created_at', 'updated_at'
        ]


class ChatSessionListSerializer(serializers.ModelSerializer):
    """Serializer for chat session list"""
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'title', 'is_active', 'last_message_at',
            'message_count', 'created_at'
        ]
        read_only_fields = fields


class ChatQuerySerializer(serializers.Serializer):
    """Serializer for chat query"""
    message = serializers.CharField()
    contract_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False
    )
    use_history = serializers.BooleanField(default=True)

