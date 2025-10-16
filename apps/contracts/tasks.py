from celery import shared_task
from django.utils import timezone
import logging

from apps.contracts.models import Contract, ContractAnalysis
from apps.contracts.services.processing_service import ProcessingService
from apps.contracts.services.ai_service import AIAnalysisService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def analyze_contract_task(self, contract_id):
    """
    Analyze contract using AI

    This task orchestrates the entire analysis pipeline:
    1. Extract text from document
    2. Perform AI analysis
    3. Extract clauses
    4. Assess compliance
    5. Perform sentiment analysis
    6. Generate report
    """

    try:
        # Get contract
        contract = Contract.objects.get(id=contract_id)
        logger.info(f"Starting analysis for contract: {contract_id}")

        # Initialize services
        processing_service = ProcessingService()
        ai_service = AIAnalysisService()

        # Update status
        contract.status = 'processing'
        contract.processing_stage = 'text_extraction'
        contract.progress_percentage = 10
        contract.save()

        # Step 1: Extract text from document
        text_content = processing_service.extract_text(contract.file_path)

        contract.progress_percentage = 30
        contract.save()

        # Step 2: Perform AI analysis
        contract.processing_stage = 'ai_analysis'
        contract.save()

        analysis_result = ai_service.analyze_contract(
            text=text_content,
            industry=contract.industry,
            language=contract.language
        )

        contract.progress_percentage = 60
        contract.save()

        # Step 3: Extract and analyze clauses
        contract.processing_stage = 'clause_extraction'
        contract.save()

        clauses_data = ai_service.extract_clauses(text_content)

        # Save clauses to database
        from apps.contracts.models import Clause
        for clause_data in clauses_data:
            Clause.objects.create(
                tenant=contract.tenant,
                contract=contract,
                **clause_data
            )

        contract.progress_percentage = 80
        contract.save()

        # Step 4: Perform sentiment analysis
        contract.processing_stage = 'sentiment_analysis'
        contract.save()

        sentiment_result = ai_service.analyze_sentiment(text_content, clauses_data)

        # Step 5: Save results to MongoDB
        contract.processing_stage = 'saving_results'
        contract.save()

        mongo_doc_id = processing_service.save_to_mongodb({
            'contract_id': contract_id,
            'tenant_id': str(contract.tenant_id),
            'analysis': analysis_result,
            'clauses': clauses_data,
            'sentiment': sentiment_result,
            'full_text': text_content
        })

        # Step 6: Update contract record
        contract.status = 'completed'
        contract.progress_percentage = 100
        contract.risk_score = analysis_result.get('overall_risk_score')
        contract.compliance_score = analysis_result.get('compliance_score', 0)
        contract.sentiment_score = sentiment_result.get('overall_score')
        contract.analyzed_at = timezone.now()
        contract.save()

        # Create analysis record
        ContractAnalysis.objects.create(
            tenant=contract.tenant,
            contract=contract,
            mongo_document_id=mongo_doc_id,
            overall_risk_score=analysis_result.get('overall_risk_score'),
            critical_issues_count=len(analysis_result.get('risk_assessment', [])),
            missing_clauses_count=len(analysis_result.get('missing_critical_clauses', [])),
            priority_level=analysis_result.get('executive_summary', {}).get('priority_level', 'medium').lower(),
            processing_time=contract.processing_time or 0,
            model_used='gpt-4-turbo'
        )

        logger.info(f"Analysis completed for contract: {contract_id}")

        # Trigger notifications
        send_analysis_complete_notification.delay(contract_id)

        # Check for alerts
        check_contract_alerts.delay(contract_id)

        return {
            'contract_id': contract_id,
            'status': 'completed',
            'risk_score': contract.risk_score
        }

    except Contract.DoesNotExist:
        logger.error(f"Contract not found: {contract_id}")
        raise

    except Exception as e:
        logger.error(f"Analysis error for contract {contract_id}: {str(e)}")

        # Update contract status
        try:
            contract = Contract.objects.get(id=contract_id)
            contract.status = 'failed'
            contract.error_message = str(e)
            contract.save()
        except:
            pass

        # Retry task
        raise self.retry(exc=e, countdown=60)


@shared_task
def send_analysis_complete_notification(contract_id):
    """Send notification when analysis is complete"""
    try:
        contract = Contract.objects.get(id=contract_id)

        # Send email to uploader
        from apps.alerts.services.email_service import EmailService
        email_service = EmailService()

        email_service.send_email(
            to=contract.uploaded_by.email,
            subject=f"Contract Analysis Complete: {contract.original_filename}",
            template='analysis_complete',
            context={
                'contract': contract,
                'user': contract.uploaded_by
            }
        )

        logger.info(f"Analysis complete notification sent for contract: {contract_id}")

    except Exception as e:
        logger.error(f"Error sending analysis notification: {str(e)}")


@shared_task
def check_contract_alerts(contract_id):
    """Check if contract triggers any alert rules"""
    try:
        from apps.alerts.services.alert_engine import AlertEngine

        contract = Contract.objects.get(id=contract_id)
        alert_engine = AlertEngine()

        # Check alert rules
        alert_engine.check_contract_alerts(contract)

        logger.info(f"Alert check completed for contract: {contract_id}")

    except Exception as e:
        logger.error(f"Error checking alerts: {str(e)}")