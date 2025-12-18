from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone

from apps.alerts.models import AlertRule, Alert, NotificationLog
from apps.alerts.serializers import (
    AlertRuleSerializer,
    AlertSerializer,
    NotificationLogSerializer
)
from apps.core.permissions import IsTenantMember, IsManagerOrAdmin


class AlertRuleViewSet(viewsets.ModelViewSet):
    """
    Alert rule management
    
    list: Get list of alert rules
    retrieve: Get alert rule details
    create: Create new alert rule
    update: Update alert rule
    destroy: Delete alert rule
    """
    permission_classes = [IsAuthenticated, IsTenantMember, IsManagerOrAdmin]
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['alert_type', 'severity', 'is_active']

    def get_queryset(self):
        """Filter by tenant"""
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return AlertRule.objects.none()
        return AlertRule.objects.filter(
            tenant=self.request.user.tenant
        )

    def perform_create(self, serializer):
        """Set tenant on create"""
        serializer.save(tenant=self.request.user.tenant)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate alert rule
        
        POST /api/v2/alerts/rules/{id}/activate/
        """
        rule = self.get_object()
        rule.is_active = True
        rule.save()
        
        return Response({
            'message': 'Alert rule activated',
            'rule': AlertRuleSerializer(rule).data
        })

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Deactivate alert rule
        
        POST /api/v2/alerts/rules/{id}/deactivate/
        """
        rule = self.get_object()
        rule.is_active = False
        rule.save()
        
        return Response({
            'message': 'Alert rule deactivated',
            'rule': AlertRuleSerializer(rule).data
        })

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """
        Test alert rule
        
        POST /api/v2/alerts/rules/{id}/test/
        """
        rule = self.get_object()
        
        # Create test alert
        alert = Alert.objects.create(
            tenant=rule.tenant,
            rule=rule,
            alert_type=rule.alert_type,
            severity=rule.severity,
            title=f"TEST: {rule.name}",
            message="This is a test alert",
            status='open',
            priority='medium'
        )
        
        # Send notifications
        from apps.alerts.services.alert_engine import AlertEngine
        alert_engine = AlertEngine()
        alert_engine.send_notifications(alert, rule.channels, rule.recipients)
        
        return Response({
            'message': 'Test alert created and sent',
            'alert_id': str(alert.id)
        })


class AlertViewSet(viewsets.ModelViewSet):
    """
    Alert management
    
    list: Get list of alerts
    retrieve: Get alert details
    """
    permission_classes = [IsAuthenticated, IsTenantMember]
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['alert_type', 'severity', 'status']

    def get_queryset(self):
        """Filter by tenant"""
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Alert.objects.none()
        return Alert.objects.filter(
            tenant=self.request.user.tenant
        ).select_related('alert_rule', 'contract', 'acknowledged_by', 'resolved_by')

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """
        Acknowledge alert
        
        POST /api/v2/alerts/{id}/acknowledge/
        """
        alert = self.get_object()
        
        alert.status = 'acknowledged'
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        return Response({
            'message': 'Alert acknowledged',
            'alert': AlertSerializer(alert).data
        })

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Resolve alert
        
        POST /api/v2/alerts/{id}/resolve/
        Body: { "resolution_notes": "..." }
        """
        alert = self.get_object()
        
        alert.status = 'resolved'
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.data['resolution_notes'] = request.data.get('resolution_notes', '')
        alert.save()
        
        return Response({
            'message': 'Alert resolved',
            'alert': AlertSerializer(alert).data
        })

    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """
        Dismiss alert
        
        POST /api/v2/alerts/{id}/dismiss/
        """
        alert = self.get_object()
        alert.status = 'dismissed'
        alert.save()
        
        return Response({
            'message': 'Alert dismissed'
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get alert statistics
        
        GET /api/v2/alerts/stats/
        """
        tenant = request.user.tenant
        
        stats = {
            'total': Alert.objects.filter(tenant=tenant).count(),
            'open': Alert.objects.filter(tenant=tenant, status='open').count(),
            'acknowledged': Alert.objects.filter(tenant=tenant, status='acknowledged').count(),
            'resolved': Alert.objects.filter(tenant=tenant, status='resolved').count(),
            'by_severity': {
                'critical': Alert.objects.filter(tenant=tenant, severity='critical', status='open').count(),
                'high': Alert.objects.filter(tenant=tenant, severity='high', status='open').count(),
                'medium': Alert.objects.filter(tenant=tenant, severity='medium', status='open').count(),
                'low': Alert.objects.filter(tenant=tenant, severity='low', status='open').count(),
            },
            'by_type': Alert.objects.filter(tenant=tenant, status='open').values('alert_type').annotate(
                count=Count('id')
            )
        }
        
        return Response(stats)

    @action(detail=False, methods=['post'])
    def bulk_acknowledge(self, request):
        """
        Acknowledge multiple alerts
        
        POST /api/v2/alerts/bulk_acknowledge/
        Body: { "alert_ids": [...] }
        """
        alert_ids = request.data.get('alert_ids', [])
        
        updated = Alert.objects.filter(
            id__in=alert_ids,
            tenant=request.user.tenant
        ).update(
            status='acknowledged',
            acknowledged_by=request.user,
            acknowledged_at=timezone.now()
        )
        
        return Response({
            'message': f'{updated} alerts acknowledged'
        })


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Notification log management (read-only)
    """
    permission_classes = [IsAuthenticated, IsTenantMember]
    queryset = NotificationLog.objects.all()
    serializer_class = NotificationLogSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['channel', 'status']

    def get_queryset(self):
        """Filter by tenant through alert relationship"""
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return NotificationLog.objects.none()
        return NotificationLog.objects.filter(
            alert__tenant=self.request.user.tenant
        ).select_related('alert')

