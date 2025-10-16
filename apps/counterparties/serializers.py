from rest_framework import serializers
from apps.counterparties.models import Counterparty, ContractCounterparty


class CounterpartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Counterparty
        fields = [
            'id', 'name', 'legal_name', 'entity_type', 'registration_number',
            'tax_id', 'address', 'city', 'state', 'country', 'postal_code',
            'contact_email', 'contact_phone', 'website', 'risk_score',
            'risk_level', 'credit_score', 'credit_rating', 'is_verified',
            'verification_source', 'verification_date', 'duns_number',
            'external_data', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContractCounterpartySerializer(serializers.ModelSerializer):
    counterparty_name = serializers.CharField(source='counterparty.name', read_only=True)

    class Meta:
        model = ContractCounterparty
        fields = [
            'id', 'contract', 'counterparty', 'role', 'is_primary',
            'counterparty_name'
        ]
        read_only_fields = ['id']