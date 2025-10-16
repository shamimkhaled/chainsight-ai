import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending email notifications
    """

    def send_email(self, to, subject, template, context=None, html_content=None):
        """
        Send email using template or HTML content
        """
        try:
            context = context or {}

            # Render HTML content
            if template:
                html_content = render_to_string(f'alerts/emails/{template}.html', context)
                text_content = render_to_string(f'alerts/emails/{template}.txt', context)
            elif not html_content:
                raise ValueError("Either template or html_content must be provided")

            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content or '',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to] if isinstance(to, str) else to
            )

            # Attach HTML content
            if html_content:
                email.attach_alternative(html_content, "text/html")

            # Send email
            email.send()

            logger.info(f"Email sent successfully to {to}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to}: {str(e)}")
            return False

    def send_alert_notification(self, alert, recipients):
        """
        Send alert notification email
        """
        subject = f"Alert: {alert.title}"

        context = {
            'alert': alert,
            'contract': alert.contract,
            'supplier': alert.supplier,
            'tenant': alert.tenant,
        }

        return self.send_email(
            to=recipients,
            subject=subject,
            template='alert_notification',
            context=context
        )

    def send_analysis_complete_notification(self, contract, user):
        """
        Send contract analysis completion notification
        """
        subject = f"Contract Analysis Complete: {contract.original_filename}"

        context = {
            'contract': contract,
            'user': user,
            'tenant': contract.tenant,
            'risk_score': contract.risk_score,
            'compliance_score': contract.compliance_score,
        }

        return self.send_email(
            to=user.email,
            subject=subject,
            template='analysis_complete',
            context=context
        )

    def send_bulk_notification(self, alerts, recipients):
        """
        Send bulk alert notifications
        """
        subject = f"Multiple Alerts - {len(alerts)} new alerts"

        context = {
            'alerts': alerts,
            'alert_count': len(alerts),
            'tenant': alerts[0].tenant if alerts else None,
        }

        return self.send_email(
            to=recipients,
            subject=subject,
            template='bulk_alert_notification',
            context=context
        )