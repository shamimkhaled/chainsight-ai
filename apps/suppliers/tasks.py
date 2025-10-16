from celery import shared_task
from django.utils import timezone
from apps.suppliers.models import Supplier, SupplierRiskAssessment
from apps.suppliers.services.risk_assessment import RiskAssessmentService
from apps.suppliers.services.monitoring import SupplierMonitoringService
import logging

logger = logging.getLogger(__name__)


@shared_task
def assess_supplier_risk(supplier_id, assessment_type='periodic'):
    """
    Perform risk assessment for a supplier
    """
    try:
        supplier = Supplier.objects.get(id=supplier_id)

        logger.info(f"Starting risk assessment for supplier: {supplier.counterparty.name}")

        # Initialize services
        risk_service = RiskAssessmentService()

        # Perform assessment
        assessment_result = risk_service.assess_supplier_risk(supplier)

        # Create assessment record
        assessment = SupplierRiskAssessment.objects.create(
            tenant=supplier.tenant,
            supplier=supplier,
            assessment_type=assessment_type,
            overall_risk_score=assessment_result['overall_risk_score'],
            overall_risk_level=assessment_result['overall_risk_level'],
            financial_risk_score=assessment_result['risk_scores']['financial_risk'],
            operational_risk_score=assessment_result['risk_scores']['operational_risk'],
            compliance_risk_score=assessment_result['risk_scores']['compliance_risk'],
            reputational_risk_score=assessment_result['risk_scores']['reputational_risk'],
            geopolitical_risk_score=assessment_result['risk_scores']['geopolitical_risk'],
            cyber_security_risk_score=assessment_result['risk_scores']['cyber_security_risk'],
            risk_factors=assessment_result['risk_factors'],
            recommendations=assessment_result['recommendations'],
            data_sources=['internal_metrics', 'credit_data'],
            external_data_fetched=False,
            assessment_method='automated'
        )

        # Update supplier's last assessment date
        supplier.last_assessment_date = timezone.now()
        supplier.save()

        # Schedule next assessment
        monitoring_service = SupplierMonitoringService()
        monitoring_service.schedule_next_assessment(supplier)

        # Check if alerts need to be triggered
        check_supplier_alerts.delay(supplier_id)

        logger.info(f"Risk assessment completed for supplier: {supplier.counterparty.name}")

        return {
            'supplier_id': supplier_id,
            'assessment_id': str(assessment.id),
            'risk_score': assessment.overall_risk_score,
            'risk_level': assessment.overall_risk_level
        }

    except Supplier.DoesNotExist:
        logger.error(f"Supplier not found: {supplier_id}")
        raise
    except Exception as e:
        logger.error(f"Error assessing supplier risk: {str(e)}")
        raise


@shared_task
def check_supplier_alerts(supplier_id):
    """
    Check if supplier triggers any alert rules
    """
    try:
        from apps.alerts.services.alert_engine import AlertEngine

        supplier = Supplier.objects.get(id=supplier_id)
        alert_engine = AlertEngine()

        # Check alert rules for supplier
        alert_engine.check_supplier_alerts(supplier)

        logger.info(f"Alert check completed for supplier: {supplier.counterparty.name}")

    except Exception as e:
        logger.error(f"Error checking supplier alerts: {str(e)}")


@shared_task
def monitor_suppliers():
    """
    Periodic task to check suppliers due for assessment
    """
    try:
        monitoring_service = SupplierMonitoringService()
        due_suppliers = monitoring_service.check_suppliers_due_for_assessment()

        logger.info(f"Found {len(due_suppliers)} suppliers due for assessment")

        # Trigger assessments for due suppliers
        for supplier in due_suppliers:
            assess_supplier_risk.delay(str(supplier.id), 'periodic')

        return {'suppliers_assessed': len(due_suppliers)}

    except Exception as e:
        logger.error(f"Error in supplier monitoring: {str(e)}")
        raise


@shared_task
def update_supplier_metrics():
    """
    Periodic task to update supplier performance metrics
    """
    try:
        # This would typically fetch data from ERP systems
        # For now, it's a placeholder
        logger.info("Supplier metrics update task started")

        # Placeholder logic - in production, this would:
        # 1. Connect to ERP systems
        # 2. Fetch latest performance data
        # 3. Update supplier records

        suppliers_updated = 0

        # Example: Update a few suppliers with mock data
        suppliers = Supplier.objects.filter(is_active=True)[:5]  # Limit for demo

        for supplier in suppliers:
            # Mock performance data update
            mock_metrics = {
                'on_time_delivery_rate': 95.5,
                'quality_score': 88.2,
                'annual_spend': supplier.annual_spend or 50000,
            }

            monitoring_service = SupplierMonitoringService()
            monitoring_service.update_supplier_metrics(supplier, mock_metrics)
            suppliers_updated += 1

        logger.info(f"Updated metrics for {suppliers_updated} suppliers")
        return {'suppliers_updated': suppliers_updated}

    except Exception as e:
        logger.error(f"Error updating supplier metrics: {str(e)}")
        raise