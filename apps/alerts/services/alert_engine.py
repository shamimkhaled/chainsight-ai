from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from apps.alerts.models import AlertRule, Alert, NotificationLog
import logging

logger = logging.getLogger(__name__)


class AlertEngine:
    """
    Engine for processing alert rules and generating alerts
    """

    def check_contract_alerts(self, contract):
        """
        Check all active alert rules for a contract
        """
        try:
            # Get active alert rules for this tenant
            alert_rules = AlertRule.objects.filter(
                tenant=contract.tenant,
                is_active=True,
                alert_type__in=['risk_threshold', 'expiry', 'compliance']
            )

            alerts_created = 0

            for rule in alert_rules:
                if self._should_trigger_alert(rule, contract):
                    self._create_alert(rule, contract)
                    alerts_created += 1

            logger.info(f"Created {alerts_created} alerts for contract: {contract.id}")
            return alerts_created

        except Exception as e:
            logger.error(f"Error checking contract alerts: {str(e)}")
            return 0

    def check_supplier_alerts(self, supplier):
        """
        Check all active alert rules for a supplier
        """
        try:
            # Get active supplier alert rules
            alert_rules = AlertRule.objects.filter(
                tenant=supplier.tenant,
                is_active=True,
                alert_type='supplier_risk'
            )

            alerts_created = 0

            for rule in alert_rules:
                if self._should_trigger_supplier_alert(rule, supplier):
                    self._create_supplier_alert(rule, supplier)
                    alerts_created += 1

            logger.info(f"Created {alerts_created} alerts for supplier: {supplier.id}")
            return alerts_created

        except Exception as e:
            logger.error(f"Error checking supplier alerts: {str(e)}")
            return 0

    def _should_trigger_alert(self, rule, contract):
        """
        Check if alert rule should trigger for contract
        """
        if rule.alert_type == 'risk_threshold':
            return self._check_risk_threshold(rule, contract)
        elif rule.alert_type == 'expiry':
            return self._check_expiry_alert(rule, contract)
        elif rule.alert_type == 'compliance':
            return self._check_compliance_alert(rule, contract)

        return False

    def _check_risk_threshold(self, rule, contract):
        """Check if contract risk exceeds threshold"""
        if not contract.risk_score or not rule.threshold_value:
            return False

        if rule.comparison_operator == 'gt':
            return contract.risk_score > rule.threshold_value
        elif rule.comparison_operator == 'gte':
            return contract.risk_score >= rule.threshold_value
        elif rule.comparison_operator == 'lt':
            return contract.risk_score < rule.threshold_value
        elif rule.comparison_operator == 'lte':
            return contract.risk_score <= rule.threshold_value

        return False

    def _check_expiry_alert(self, rule, contract):
        """Check if contract is expiring soon"""
        if not contract.expiry_date:
            return False

        days_until_expiry = (contract.expiry_date - timezone.now().date()).days

        # Default to 30 days if no threshold specified
        threshold_days = rule.threshold_value or 30

        return days_until_expiry <= threshold_days

    def _check_compliance_alert(self, rule, contract):
        """Check for compliance violations"""
        if not contract.compliance_score:
            return False

        # Alert if compliance score is below threshold
        threshold = rule.threshold_value or 70

        return contract.compliance_score < threshold

    def _should_trigger_supplier_alert(self, rule, supplier):
        """Check if alert rule should trigger for supplier"""
        # Get latest risk assessment
        latest_assessment = supplier.risk_assessments.order_by('-assessment_date').first()

        if not latest_assessment:
            return False

        # Check risk score threshold
        if rule.threshold_value and latest_assessment.overall_risk_score >= rule.threshold_value:
            return True

        return False

    def _create_alert(self, rule, contract):
        """Create an alert for contract"""
        try:
            # Check for recent similar alerts to avoid duplicates
            recent_alert = Alert.objects.filter(
                tenant=contract.tenant,
                alert_rule=rule,
                contract=contract,
                created_at__gte=timezone.now() - timedelta(seconds=rule.cooldown_period)
            ).first()

            if recent_alert:
                logger.info(f"Skipping duplicate alert for rule {rule.id} and contract {contract.id}")
                return

            # Create alert
            alert = Alert.objects.create(
                tenant=contract.tenant,
                alert_rule=rule,
                alert_type=rule.alert_type,
                severity=rule.severity,
                title=self._generate_alert_title(rule, contract),
                message=self._generate_alert_message(rule, contract),
                contract=contract,
                trigger_data=self._get_trigger_data(rule, contract),
                context={'contract_id': str(contract.id)}
            )

            # Send notifications
            self._send_notifications(alert)

            logger.info(f"Created alert {alert.id} for contract {contract.id}")

        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")

    def _create_supplier_alert(self, rule, supplier):
        """Create an alert for supplier"""
        try:
            # Check for recent similar alerts
            recent_alert = Alert.objects.filter(
                tenant=supplier.tenant,
                alert_rule=rule,
                supplier=supplier,
                created_at__gte=timezone.now() - timedelta(seconds=rule.cooldown_period)
            ).first()

            if recent_alert:
                logger.info(f"Skipping duplicate supplier alert for rule {rule.id}")
                return

            # Create alert
            alert = Alert.objects.create(
                tenant=supplier.tenant,
                alert_rule=rule,
                alert_type=rule.alert_type,
                severity=rule.severity,
                title=self._generate_supplier_alert_title(rule, supplier),
                message=self._generate_supplier_alert_message(rule, supplier),
                supplier=supplier,
                trigger_data=self._get_supplier_trigger_data(rule, supplier),
                context={'supplier_id': str(supplier.id)}
            )

            # Send notifications
            self._send_notifications(alert)

            logger.info(f"Created supplier alert {alert.id} for supplier {supplier.id}")

        except Exception as e:
            logger.error(f"Error creating supplier alert: {str(e)}")

    def _generate_alert_title(self, rule, contract):
        """Generate alert title"""
        if rule.alert_type == 'risk_threshold':
            return f"High Risk Contract: {contract.original_filename}"
        elif rule.alert_type == 'expiry':
            return f"Contract Expiring Soon: {contract.original_filename}"
        elif rule.alert_type == 'compliance':
            return f"Compliance Issue: {contract.original_filename}"
        return f"Alert: {contract.original_filename}"

    def _generate_alert_message(self, rule, contract):
        """Generate alert message"""
        if rule.alert_type == 'risk_threshold':
            return f"Contract '{contract.original_filename}' has a risk score of {contract.risk_score}, which exceeds the threshold."
        elif rule.alert_type == 'expiry':
            days = (contract.expiry_date - timezone.now().date()).days
            return f"Contract '{contract.original_filename}' expires in {days} days."
        elif rule.alert_type == 'compliance':
            return f"Contract '{contract.original_filename}' has a compliance score of {contract.compliance_score}."
        return f"An alert has been triggered for contract '{contract.original_filename}'."

    def _generate_supplier_alert_title(self, rule, supplier):
        """Generate supplier alert title"""
        return f"High Risk Supplier: {supplier.counterparty.name}"

    def _generate_supplier_alert_message(self, rule, supplier):
        """Generate supplier alert message"""
        latest_assessment = supplier.risk_assessments.order_by('-assessment_date').first()
        if latest_assessment:
            return f"Supplier '{supplier.counterparty.name}' has a risk score of {latest_assessment.overall_risk_score} ({latest_assessment.overall_risk_level})."
        return f"Supplier '{supplier.counterparty.name}' has triggered a risk alert."

    def _get_trigger_data(self, rule, contract):
        """Get trigger data for contract alert"""
        return {
            'rule_id': str(rule.id),
            'contract_id': str(contract.id),
            'risk_score': contract.risk_score,
            'compliance_score': contract.compliance_score,
            'expiry_date': contract.expiry_date.isoformat() if contract.expiry_date else None,
        }

    def _get_supplier_trigger_data(self, rule, supplier):
        """Get trigger data for supplier alert"""
        latest_assessment = supplier.risk_assessments.order_by('-assessment_date').first()
        return {
            'rule_id': str(rule.id),
            'supplier_id': str(supplier.id),
            'risk_score': latest_assessment.overall_risk_score if latest_assessment else None,
            'assessment_date': latest_assessment.assessment_date.isoformat() if latest_assessment else None,
        }

    def _send_notifications(self, alert):
        """Send notifications for alert"""
        try:
            # Email notifications
            if alert.alert_rule.notify_email:
                self._send_email_notification(alert)

            # SMS notifications
            if alert.alert_rule.notify_sms:
                self._send_sms_notification(alert)

            # WhatsApp notifications
            if alert.alert_rule.notify_whatsapp:
                self._send_whatsapp_notification(alert)

        except Exception as e:
            logger.error(f"Error sending notifications for alert {alert.id}: {str(e)}")

    def _send_email_notification(self, alert):
        """Send email notification"""
        try:
            from apps.alerts.services.email_service import EmailService
            email_service = EmailService()

            recipients = alert.alert_rule.recipients or []
            if not recipients:
                # Get admin users from tenant
                admin_users = alert.tenant.users.filter(role='admin', is_active=True)
                recipients = [user.email for user in admin_users]

            for recipient in recipients:
                email_service.send_email(
                    to=recipient,
                    subject=f"Alert: {alert.title}",
                    template='alert_notification',
                    context={
                        'alert': alert,
                        'recipient': recipient
                    }
                )

            alert.email_sent = True
            alert.save()

            # Log notification
            NotificationLog.objects.create(
                alert=alert,
                channel='email',
                recipient=', '.join(recipients),
                status='sent'
            )

        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            NotificationLog.objects.create(
                alert=alert,
                channel='email',
                recipient=', '.join(recipients) if 'recipients' in locals() else 'unknown',
                status='failed',
                error_message=str(e)
            )

    def _send_sms_notification(self, alert):
        """Send SMS notification (placeholder)"""
        # Implementation would use Twilio or similar service
        logger.info(f"SMS notification for alert {alert.id} (placeholder)")

    def _send_whatsapp_notification(self, alert):
        """Send WhatsApp notification (placeholder)"""
        # Implementation would use WhatsApp Business API
        logger.info(f"WhatsApp notification for alert {alert.id} (placeholder)")