from django.contrib import admin
from apps.alerts.models import AlertRule, Alert, NotificationLog


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'alert_type', 'severity', 'is_active',
        'check_frequency', 'created_by', 'tenant'
    ]
    list_filter = ['alert_type', 'severity', 'is_active', 'check_frequency', 'tenant']
    search_fields = ['name', 'description']
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('tenant', 'name', 'description', 'alert_type', 'category')
        }),
        ('Conditions', {
            'fields': ('conditions', 'threshold_value', 'comparison_operator')
        }),
        ('Configuration', {
            'fields': ('severity', 'priority', 'is_active', 'check_frequency')
        }),
        ('Notifications', {
            'fields': ('notify_email', 'notify_sms', 'notify_whatsapp',
                      'notify_erp', 'notify_webhook', 'recipients')
        }),
        ('Rate Limiting', {
            'fields': ('cooldown_period', 'max_alerts_per_day'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'alert_type', 'severity', 'status',
        'contract', 'supplier', 'created_at'
    ]
    list_filter = ['alert_type', 'severity', 'status', 'tenant']
    search_fields = ['title', 'message']
    ordering = ['-created_at']

    fieldsets = (
        ('Alert Information', {
            'fields': ('alert_rule', 'alert_type', 'severity', 'title', 'message')
        }),
        ('Related Objects', {
            'fields': ('contract', 'supplier')
        }),
        ('Data', {
            'fields': ('trigger_data', 'context'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'acknowledged_by', 'acknowledged_at',
                      'resolved_by', 'resolved_at')
        }),
        ('Notifications', {
            'fields': ('email_sent', 'sms_sent', 'whatsapp_sent',
                      'erp_sent', 'webhook_sent'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['alert', 'channel', 'recipient', 'status', 'sent_at']
    list_filter = ['channel', 'status', 'sent_at']
    search_fields = ['recipient', 'alert__title']
    ordering = ['-sent_at']

    readonly_fields = ['sent_at', 'delivered_at']

    fieldsets = (
        ('Notification Details', {
            'fields': ('alert', 'channel', 'recipient', 'status')
        }),
        ('Delivery Information', {
            'fields': ('error_message', 'external_id', 'sent_at', 'delivered_at')
        }),
    )