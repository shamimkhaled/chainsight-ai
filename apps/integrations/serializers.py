from rest_framework import serializers
from apps.integrations.models import Integration, IntegrationLog, ERPEntity, DocumentSync


class IntegrationSerializer(serializers.ModelSerializer):
    """Serializer for integrations"""
    
    class Meta:
        model = Integration
        fields = [
            'id', 'name', 'integration_type', 'config',
            'is_active', 'is_connected', 'last_sync_at',
            'auto_sync', 'sync_interval', 'last_error',
            'error_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_connected', 'last_sync_at',
            'last_error', 'error_count', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'credentials': {'write_only': True}
        }


class IntegrationLogSerializer(serializers.ModelSerializer):
    """Serializer for integration logs"""
    
    class Meta:
        model = IntegrationLog
        fields = [
            'id', 'integration', 'action', 'status',
            'error_message', 'execution_time', 'created_at'
        ]
        read_only_fields = fields


class ERPEntitySerializer(serializers.ModelSerializer):
    """Serializer for ERP entities"""
    
    class Meta:
        model = ERPEntity
        fields = [
            'id', 'integration', 'entity_type', 'external_id',
            'external_reference', 'entity_data', 'contract',
            'counterparty', 'last_synced_at', 'sync_status',
            'created_at'
        ]
        read_only_fields = ['id', 'last_synced_at', 'created_at']


class DocumentSyncSerializer(serializers.ModelSerializer):
    """Serializer for document syncs"""
    
    class Meta:
        model = DocumentSync
        fields = [
            'id', 'integration', 'contract', 'external_document_id',
            'external_document_url', 'sync_direction', 'auto_sync',
            'local_version', 'external_version', 'last_synced_at',
            'has_conflicts', 'conflict_data', 'created_at'
        ]
        read_only_fields = [
            'id', 'local_version', 'external_version',
            'last_synced_at', 'has_conflicts', 'created_at'
        ]

