from rest_framework import serializers
from apps.tenants.models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for tenant list"""
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'subdomain', 'plan_type',
            'max_users', 'max_contracts', 'max_storage_gb',
            'status', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TenantDetailSerializer(serializers.ModelSerializer):
    """Serializer for tenant detail"""
    user_count = serializers.SerializerMethodField()
    contract_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'subdomain', 'plan_type',
            'max_users', 'max_contracts', 'max_storage_gb',
            'status', 'is_active', 'billing_email', 'billing_info',
            'settings', 'user_count', 'contract_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_count', 'contract_count']

    def get_user_count(self, obj):
        return obj.users.count()

    def get_contract_count(self, obj):
        return obj.contract_set.count()

