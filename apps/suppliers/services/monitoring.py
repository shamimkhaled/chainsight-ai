from datetime import datetime, timedelta
from django.utils import timezone
from apps.suppliers.models import Supplier, SupplierRiskAssessment
import logging

logger = logging.getLogger(__name__)


class SupplierMonitoringService:
    """
    Service for monitoring supplier performance and risk
    """

    def check_suppliers_due_for_assessment(self):
        """
        Get suppliers that are due for risk assessment
        """
        now = timezone.now()
        due_suppliers = []

        suppliers = Supplier.objects.filter(
            is_active=True,
            is_monitored=True
        ).exclude(
            next_assessment_date__isnull=True
        )

        for supplier in suppliers:
            if supplier.next_assessment_date <= now:
                due_suppliers.append(supplier)

        return due_suppliers

    def schedule_next_assessment(self, supplier):
        """
        Schedule the next risk assessment based on monitoring frequency
        """
        if not supplier.monitoring_frequency:
            return

        frequency_map = {
            'daily': 1,
            'weekly': 7,
            'monthly': 30,
            'quarterly': 90,
        }

        days = frequency_map.get(supplier.monitoring_frequency, 30)
        supplier.next_assessment_date = timezone.now() + timedelta(days=days)
        supplier.save()

    def update_supplier_metrics(self, supplier, metrics_data):
        """
        Update supplier performance metrics
        """
        update_fields = []

        if 'on_time_delivery_rate' in metrics_data:
            supplier.on_time_delivery_rate = metrics_data['on_time_delivery_rate']
            update_fields.append('on_time_delivery_rate')

        if 'quality_score' in metrics_data:
            supplier.quality_score = metrics_data['quality_score']
            update_fields.append('quality_score')

        if 'responsiveness_score' in metrics_data:
            supplier.responsiveness_score = metrics_data['responsiveness_score']
            update_fields.append('responsiveness_score')

        if 'annual_spend' in metrics_data:
            supplier.annual_spend = metrics_data['annual_spend']
            update_fields.append('annual_spend')

        if update_fields:
            supplier.save(update_fields=update_fields)

    def get_supplier_performance_trend(self, supplier, days=90):
        """
        Get supplier performance trend over time
        """
        start_date = timezone.now() - timedelta(days=days)

        assessments = SupplierRiskAssessment.objects.filter(
            supplier=supplier,
            assessment_date__gte=start_date
        ).order_by('assessment_date')

        trend_data = []
        for assessment in assessments:
            trend_data.append({
                'date': assessment.assessment_date.date(),
                'overall_risk_score': assessment.overall_risk_score,
                'financial_risk': assessment.financial_risk_score,
                'operational_risk': assessment.operational_risk_score,
                'compliance_risk': assessment.compliance_risk_score,
            })

        return trend_data

    def identify_underperforming_suppliers(self, threshold=70):
        """
        Identify suppliers with risk scores above threshold
        """
        recent_assessments = SupplierRiskAssessment.objects.filter(
            assessment_date__gte=timezone.now() - timedelta(days=30)
        ).select_related('supplier')

        underperforming = []
        for assessment in recent_assessments:
            if assessment.overall_risk_score >= threshold:
                underperforming.append({
                    'supplier': assessment.supplier,
                    'risk_score': assessment.overall_risk_score,
                    'risk_level': assessment.overall_risk_level,
                    'assessment_date': assessment.assessment_date,
                })

        return underperforming

    def generate_supplier_report(self, supplier):
        """
        Generate comprehensive supplier report
        """
        # Get latest assessment
        latest_assessment = SupplierRiskAssessment.objects.filter(
            supplier=supplier
        ).order_by('-assessment_date').first()

        # Get performance trend
        trend = self.get_supplier_performance_trend(supplier)

        report = {
            'supplier_info': {
                'name': supplier.counterparty.name,
                'code': supplier.supplier_code,
                'tier': supplier.tier,
                'status': supplier.status,
                'category': supplier.category,
            },
            'performance_metrics': {
                'on_time_delivery_rate': supplier.on_time_delivery_rate,
                'quality_score': supplier.quality_score,
                'responsiveness_score': supplier.responsiveness_score,
                'annual_spend': supplier.annual_spend,
            },
            'latest_assessment': {
                'date': latest_assessment.assessment_date if latest_assessment else None,
                'overall_risk_score': latest_assessment.overall_risk_score if latest_assessment else None,
                'risk_level': latest_assessment.overall_risk_level if latest_assessment else None,
                'risk_factors': latest_assessment.risk_factors if latest_assessment else [],
                'recommendations': latest_assessment.recommendations if latest_assessment else [],
            } if latest_assessment else None,
            'performance_trend': trend,
            'monitoring_info': {
                'is_monitored': supplier.is_monitored,
                'monitoring_frequency': supplier.monitoring_frequency,
                'next_assessment_date': supplier.next_assessment_date,
            }
        }

        return report