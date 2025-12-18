from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from apps.alerts.models import AlertRule, Alert, NotificationLog


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    """Admin interface for Alert Rules"""
    
    list_display = [
        'name', 'tenant_link', 'alert_type',
        'severity_badge', 'is_active', 'created_at'
    ]
    
    list_filter = [
        'alert_type', 'severity', 'is_active',
        'created_at', 'tenant'
    ]
    
    search_fields = [
        'name', 'description', 'recipients'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id', 'tenant', 'name', 'description',
                'alert_type', 'severity', 'is_active'
            )
        }),
        ('Conditions', {
            'fields': ('conditions',)
        }),
        ('Notifications', {
            'fields': (
                'notify_email', 'notify_sms', 'notify_whatsapp',
                'notify_erp', 'notify_webhook', 'recipients'
            )
        }),
        ('Scheduling', {
            'fields': (
                'check_frequency', 'cooldown_period',
                'max_alerts_per_day'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_rules', 'deactivate_rules', 'test_rules']
    
    def tenant_link(self, obj):
        """Display tenant as link"""
        if obj.tenant:
            url = reverse('admin:tenants_tenant_change', args=[obj.tenant.id])
            return format_html('<a href="{}">{}</a>', url, obj.tenant.name)
        return '-'
    tenant_link.short_description = 'Tenant'
    
    def severity_badge(self, obj):
        """Display severity as colored badge"""
        colors = {
            'critical': '#DC3545',
            'high': '#FD7E14',
            'medium': '#FFC107',
            'low': '#28A745'
        }
        color = colors.get(obj.severity, '#6C757D')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.severity.upper()
        )
    severity_badge.short_description = 'Severity'
    
    def activate_rules(self, request, queryset):
        """Activate rules"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} rule(s) activated.')
    activate_rules.short_description = 'Activate selected rules'
    
    def deactivate_rules(self, request, queryset):
        """Deactivate rules"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} rule(s) deactivated.')
    deactivate_rules.short_description = 'Deactivate selected rules'
    
    def test_rules(self, request, queryset):
        """Test alert rules"""
        for rule in queryset:
            # Create test alert
            Alert.objects.create(
                tenant=rule.tenant,
                rule=rule,
                alert_type=rule.alert_type,
                severity=rule.severity,
                title=f"TEST: {rule.name}",
                message="This is a test alert",
                status='open',
                priority='medium'
            )
        count = queryset.count()
        self.message_user(request, f'{count} test alert(s) created.')
    test_rules.short_description = 'Test selected rules'


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Admin interface for Alerts"""
    
    list_display = [
        'title', 'rule_link', 'alert_type', 'severity_badge',
        'status_badge', 'contract_link',
        'created_at'
    ]
    
    list_filter = [
        'alert_type', 'severity', 'status',
        'created_at', 'acknowledged_at', 'resolved_at', 'tenant'
    ]
    
    search_fields = [
        'title', 'message', 'rule__name',
        'contract__original_filename'
    ]
    
    readonly_fields = [
        'id', 'tenant', 'alert_rule', 'contract', 'supplier',
        'created_at', 'updated_at', 'acknowledged_at',
        'resolved_at'
    ]
    
    fieldsets = (
        ('Alert Information', {
            'fields': (
                'id', 'tenant', 'alert_rule', 'alert_type',
                'severity', 'title', 'message'
            )
        }),
        ('Related Objects', {
            'fields': ('contract', 'supplier')
        }),
        ('Status', {
            'fields': (
                'status', 'trigger_data', 'context'
            )
        }),
        ('Actions', {
            'fields': (
                'acknowledged_by', 'acknowledged_at',
                'resolved_by', 'resolved_at'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'acknowledge_alerts', 'resolve_alerts',
        'dismiss_alerts'
    ]
    
    def rule_link(self, obj):
        """Display rule as link"""
        if obj.rule:
            url = reverse('admin:alerts_alertrule_change', args=[obj.rule.id])
            return format_html('<a href="{}">{}</a>', url, obj.rule.name)
        return '-'
    rule_link.short_description = 'Rule'
    
    def contract_link(self, obj):
        """Display contract as link"""
        if obj.contract:
            url = reverse('admin:contracts_contract_change', args=[obj.contract.id])
            return format_html(
                '<a href="{}">{}</a>',
                url, obj.contract.original_filename
            )
        return '-'
    contract_link.short_description = 'Contract'
    
    def severity_badge(self, obj):
        """Display severity as colored badge"""
        colors = {
            'critical': '#DC3545',
            'high': '#FD7E14',
            'medium': '#FFC107',
            'low': '#28A745'
        }
        color = colors.get(obj.severity, '#6C757D')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.severity.upper()
        )
    severity_badge.short_description = 'Severity'
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'open': '#DC3545',
            'acknowledged': '#FFC107',
            'resolved': '#28A745',
            'dismissed': '#6C757D'
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.status.upper()
        )
    status_badge.short_description = 'Status'
    
    def acknowledge_alerts(self, request, queryset):
        """Acknowledge alerts"""
        from django.utils import timezone
        updated = queryset.filter(status='open').update(
            status='acknowledged',
            acknowledged_by=request.user,
            acknowledged_at=timezone.now()
        )
        self.message_user(request, f'{updated} alert(s) acknowledged.')
    acknowledge_alerts.short_description = 'Acknowledge selected alerts'
    
    def resolve_alerts(self, request, queryset):
        """Resolve alerts"""
        from django.utils import timezone
        updated = queryset.filter(
            status__in=['open', 'acknowledged']
        ).update(
            status='resolved',
            resolved_by=request.user,
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} alert(s) resolved.')
    resolve_alerts.short_description = 'Resolve selected alerts'
    
    def dismiss_alerts(self, request, queryset):
        """Dismiss alerts"""
        updated = queryset.update(status='dismissed')
        self.message_user(request, f'{updated} alert(s) dismissed.')
    dismiss_alerts.short_description = 'Dismiss selected alerts'


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """Admin interface for Notification Logs"""
    
    list_display = [
        'alert_link', 'channel', 'recipient',
        'status_badge', 'sent_at', 'delivered_at'
    ]
    
    list_filter = [
        'channel', 'status', 'sent_at', 'delivered_at'
    ]
    
    search_fields = [
        'recipient', 'alert__title', 'error_message'
    ]
    
    readonly_fields = [
        'id', 'alert', 'channel', 'recipient',
        'status', 'sent_at', 'delivered_at', 'error_message',
        'external_id'
    ]
    
    fieldsets = (
        ('Notification Information', {
            'fields': (
                'id', 'alert', 'channel',
                'recipient', 'status'
            )
        }),
        ('Timing', {
            'fields': ('sent_at', 'delivered_at')
        }),
        ('Error Details', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('external_id',),
            'classes': ('collapse',)
        })
    )
    
    def alert_link(self, obj):
        """Display alert as link"""
        if obj.alert:
            url = reverse('admin:alerts_alert_change', args=[obj.alert.id])
            return format_html('<a href="{}">{}</a>', url, obj.alert.title)
        return '-'
    alert_link.short_description = 'Alert'
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'sent': '#1E90FF',
            'delivered': '#28A745',
            'failed': '#DC3545',
            'pending': '#FFC107'
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.status.upper()
        )
    status_badge.short_description = 'Status'
