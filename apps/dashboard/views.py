from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from apps.contracts.models import Contract
from apps.accounts.models import User
from apps.alerts.models import Alert
from apps.core.permissions import IsTenantMember


class DashboardView(views.APIView):
    """
    Dashboard analytics view
    
    GET /api/v2/dashboard/
    """
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get(self, request):
        tenant = request.user.tenant

        # Contract statistics
        total_contracts = Contract.objects.filter(tenant=tenant).count()
        contracts_completed = Contract.objects.filter(
            tenant=tenant, status='completed'
        ).count()
        contracts_pending = Contract.objects.filter(
            tenant=tenant, status='pending'
        ).count()
        contracts_processing = Contract.objects.filter(
            tenant=tenant, status='processing'
        ).count()

        # Risk statistics
        high_risk_contracts = Contract.objects.filter(
            tenant=tenant,
            risk_score__gte=70
        ).count()

        avg_risk_score = Contract.objects.filter(
            tenant=tenant,
            risk_score__isnull=False
        ).aggregate(avg_score=Avg('risk_score'))['avg_score'] or 0

        # Recent contracts (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_contracts = Contract.objects.filter(
            tenant=tenant,
            created_at__gte=thirty_days_ago
        ).count()

        # Expiring contracts (next 90 days)
        ninety_days_ahead = timezone.now().date() + timedelta(days=90)
        expiring_soon = Contract.objects.filter(
            tenant=tenant,
            expiry_date__lte=ninety_days_ahead,
            expiry_date__gte=timezone.now().date()
        ).count()

        # User statistics
        total_users = User.objects.filter(tenant=tenant).count()
        active_users = User.objects.filter(tenant=tenant, is_active=True).count()

        # Alert statistics
        open_alerts = Alert.objects.filter(
            tenant=tenant,
            status='open'
        ).count() if hasattr(Alert, 'objects') else 0

        return Response({
            'contracts': {
                'total': total_contracts,
                'completed': contracts_completed,
                'pending': contracts_pending,
                'processing': contracts_processing,
                'recent_30_days': recent_contracts,
                'expiring_soon_90_days': expiring_soon,
            },
            'risk': {
                'high_risk_count': high_risk_contracts,
                'average_risk_score': round(avg_risk_score, 2),
            },
            'users': {
                'total': total_users,
                'active': active_users,
            },
            'alerts': {
                'open': open_alerts,
            },
            'tenant': {
                'name': tenant.name,
                'plan_type': tenant.plan_type,
                'max_contracts': tenant.max_contracts,
                'usage_percentage': round((total_contracts / tenant.max_contracts) * 100, 2) if tenant.max_contracts > 0 else 0,
            }
        })


class ContractTrendsView(views.APIView):
    """
    Contract trends analytics
    
    GET /api/v2/dashboard/trends/
    """
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get(self, request):
        tenant = request.user.tenant
        period = request.query_params.get('period', '30')  # days

        try:
            days = int(period)
        except ValueError:
            days = 30

        start_date = timezone.now() - timedelta(days=days)

        # Contracts by status over time
        contracts_by_date = Contract.objects.filter(
            tenant=tenant,
            created_at__gte=start_date
        ).extra(
            select={'date': 'DATE(created_at)'}
        ).values('date').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            pending=Count('id', filter=Q(status='pending'))
        ).order_by('date')

        return Response({
            'period_days': days,
            'trends': list(contracts_by_date)
        })


class RiskDistributionView(views.APIView):
    """
    Risk distribution analytics
    
    GET /api/v2/dashboard/risk-distribution/
    """
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get(self, request):
        tenant = request.user.tenant

        # Risk score distribution
        risk_distribution = {
            'low': Contract.objects.filter(tenant=tenant, risk_score__lt=30).count(),
            'medium': Contract.objects.filter(tenant=tenant, risk_score__gte=30, risk_score__lt=70).count(),
            'high': Contract.objects.filter(tenant=tenant, risk_score__gte=70).count(),
        }

        # Industry breakdown
        industry_breakdown = Contract.objects.filter(
            tenant=tenant
        ).values('industry').annotate(
            count=Count('id'),
            avg_risk=Avg('risk_score')
        ).order_by('-count')

        return Response({
            'risk_distribution': risk_distribution,
            'by_industry': list(industry_breakdown)
        })

