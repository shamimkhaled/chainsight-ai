from rest_framework import serializers
from apps.counterparties.models import Counterparty, ContractCounterparty


class CounterpartySerializer(serializers.ModelSerializer):
    """Serializer for counterparty details"""

    class Meta:
        model = Counterparty
        fields = [
            'id', 'name', 'legal_name', 'entity_type',
            'registration_number', 'tax_id', 'address', 'city',
            'state', 'country', 'postal_code', 'contact_email',
            'contact_phone', 'website', 'risk_score', 'risk_level',
            'credit_score', 'credit_rating', 'is_verified',
            'verification_source', 'verification_date',
            'duns_number', 'external_data', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'risk_score', 'risk_level', 'credit_score',
            'credit_rating', 'is_verified', 'verification_source',
            'verification_date', 'created_at', 'updated_at'
        ]


class CounterpartyListSerializer(serializers.ModelSerializer):
    """Serializer for counterparty list view"""

    class Meta:
        model = Counterparty
        fields = [
            'id', 'name', 'legal_name', 'entity_type',
            'country', 'risk_score', 'risk_level',
            'is_verified', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ContractCounterpartySerializer(serializers.ModelSerializer):
    """Serializer for contract-counterparty relationship"""
    counterparty = CounterpartySerializer(read_only=True)
    counterparty_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = ContractCounterparty
        fields = [
            'id', 'contract', 'counterparty', 'counterparty_id',
            'role', 'is_primary'
        ]
        read_only_fields = ['id']
