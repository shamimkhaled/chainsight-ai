from rest_framework import serializers
from apps.alerts.models import AlertRule, Alert, NotificationLog


class AlertRuleSerializer(serializers.ModelSerializer):
    """Serializer for alert rules"""
    
    class Meta:
        model = AlertRule
        fields = [
            'id', 'name', 'description', 'alert_type', 'category',
            'conditions', 'threshold_value', 'comparison_operator',
            'severity', 'priority', 'recipients',
            'notify_email', 'notify_sms', 'notify_whatsapp',
            'notify_erp', 'notify_webhook',
            'is_active', 'check_frequency',
            'cooldown_period', 'max_alerts_per_day',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at'
        ]


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for alerts"""
    rule_name = serializers.CharField(source='alert_rule.name', read_only=True, allow_null=True)
    contract_filename = serializers.CharField(
        source='contract.original_filename',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = Alert
        fields = [
            'id', 'alert_rule', 'rule_name', 'alert_type',
            'severity', 'title', 'message', 'contract',
            'contract_filename', 'supplier', 'status',
            'trigger_data', 'context',
            'acknowledged_by', 'acknowledged_at',
            'resolved_by', 'resolved_at',
            'email_sent', 'sms_sent', 'whatsapp_sent',
            'erp_sent', 'webhook_sent',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'rule_name', 'contract_filename',
            'created_at', 'updated_at'
        ]


class NotificationLogSerializer(serializers.ModelSerializer):
    """Serializer for notification logs"""
    
    class Meta:
        model = NotificationLog
        fields = [
            'id', 'alert', 'channel', 'recipient',
            'status', 'sent_at', 'delivered_at',
            'error_message', 'external_id'
        ]
        read_only_fields = fields
