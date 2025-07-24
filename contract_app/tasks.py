from celery import shared_task
from django.utils import timezone
from datetime import datetime
import logging

from .models import ContractAnalysis
from .document_processors import ContractDocumentProcessor
from .ai_analyzers import ContractAIAnalyzer

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_contract_async(self, analysis_id):
    """Process contract asynchronously using Celery"""
    
    try:
        analysis = ContractAnalysis.objects.get(id=analysis_id)
    except ContractAnalysis.DoesNotExist:
        logger.error(f"Analysis {analysis_id} not found")
        return {"error": "Analysis not found"}
    
    start_time = datetime.now()
    
    try:
        # Initialize processor and analyzer
        processor = ContractDocumentProcessor()
        analyzer = ContractAIAnalyzer()
        
        # Extract text from document
        file_path = analysis.file.path
        processing_result = processor.process_document(file_path)
        
        if processing_result['error']:
            raise Exception(processing_result['error'])
        
        extracted_text = processing_result['text']
        analysis.extracted_text = extracted_text
        analysis.is_scanned_pdf = processing_result['is_scanned']
        analysis.ocr_method_used = processing_result['ocr_method']
        
        # Analyze contract with AI
        ai_result = analyzer.analyze_contract(
            extracted_text,
            analysis.industry,
            analysis.language
        )
        
        if 'error' in ai_result:
            raise Exception(ai_result['error'])
        
        # Extract risk score
        risk_score = ai_result.get('document_analysis', {}).get('overall_risk_score', 0)
        
        # Update analysis record
        analysis.analysis_result = ai_result
        analysis.risk_score = risk_score
        analysis.status = 'completed'
        analysis.processing_completed_at = timezone.now()
        analysis.processing_time_seconds = (datetime.now() - start_time).total_seconds()
        analysis.save()
        
        logger.info(f"Successfully processed contract {analysis.id}")
        
        return {
            "status": "completed",
            "analysis_id": str(analysis.id),
            "processing_time": analysis.processing_time_seconds
        }
        
    except Exception as e:
        logger.error(f"Contract processing failed: {str(e)}")
        analysis.status = 'failed'
        analysis.error_message = str(e)
        analysis.processing_completed_at = timezone.now()
        analysis.processing_time_seconds = (datetime.now() - start_time).total_seconds()
        analysis.save()
        
        return {
            "status": "failed",
            "error": str(e),
            "analysis_id": str(analysis.id)
        }