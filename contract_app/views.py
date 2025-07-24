from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import os
import logging
from datetime import datetime, timedelta

from .models import ContractAnalysis, RateLimitTracker
from .serializers import ContractUploadSerializer, ContractAnalysisSerializer, ContractAnalysisListSerializer
from .document_processors import ContractDocumentProcessor
from .ai_analyzers import ContractAIAnalyzer
# from .tasks import process_contract_async



logger = logging.getLogger(__name__)




def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



def check_daily_limit(ip_address):
    """Check if user has exceeded daily limit"""
    today = timezone.now().date()
    
    tracker, created = RateLimitTracker.objects.get_or_create(
        user_ip=ip_address,
        defaults={'daily_count': 0, 'last_reset_date': today}
    )
    
    # Reset count if it's a new day
    if tracker.last_reset_date < today:
        tracker.daily_count = 0
        tracker.last_reset_date = today
        tracker.save()
    
    # Check if limit exceeded
    if tracker.daily_count >= 5:
        return False, tracker.daily_count
    
    return True, tracker.daily_count



def increment_daily_count(ip_address):
    """Increment daily count for user"""
    today = timezone.now().date()
    tracker, created = RateLimitTracker.objects.get_or_create(
        user_ip=ip_address,
        defaults={'daily_count': 1, 'last_reset_date': today}
    )
    
    if not created:
        if tracker.last_reset_date < today:
            tracker.daily_count = 1
            tracker.last_reset_date = today
        else:
            tracker.daily_count += 1
        tracker.save()
        
        
        

class ContractAnalysisViewSet(viewsets.ModelViewSet):
    queryset = ContractAnalysis.objects.all()
    serializer_class = ContractAnalysisSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ContractAnalysisListSerializer
        elif self.action == 'create':
            return ContractUploadSerializer
        return ContractAnalysisSerializer

    @swagger_auto_schema(
        operation_description="Upload and analyze a contract document",
        # request_body=openapi.Schema(
        #     type=openapi.TYPE_OBJECT,
        #     properties={
        #         'file': openapi.Schema(type=openapi.TYPE_FILE, description='Contract document (PDF, DOCX, TXT, JPG, PNG)'),
        #         'industry': openapi.Schema(type=openapi.TYPE_STRING, enum=['garment', 'it', 'construction'], description='Industry type'),
        #         'language': openapi.Schema(type=openapi.TYPE_STRING, enum=['english', 'spanish', 'french', 'german', 'chinese'], description='Document language'),
        #     },
        #     required=['file', 'industry']
        # ),
        responses={
            201: ContractAnalysisSerializer,
            400: 'Bad Request',
            429: 'Rate limit exceeded',
        }
    )
    def create(self, request, *args, **kwargs):
        """Upload and analyze a contract document"""
        
        # Get client IP
        client_ip = get_client_ip(request)
        
        # Check daily rate limit
        can_proceed, current_count = check_daily_limit(client_ip)
        if not can_proceed:
            return Response({
                'error': 'Daily limit exceeded',
                'message': f'You have reached the daily limit of 5 document analyses. Current count: {current_count}/5. Please try again tomorrow.',
                'retry_after': 86400  # 24 hours in seconds
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Validate input
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Invalid input',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = serializer.validated_data['file']
        industry = serializer.validated_data['industry']
        language = serializer.validated_data.get('language', 'english')
        
        try:
            with transaction.atomic():
                # Create analysis record
                analysis = ContractAnalysis.objects.create(
                    user_ip=client_ip,
                    file=uploaded_file,
                    original_filename=uploaded_file.name,
                    file_size=uploaded_file.size,
                    industry=industry,
                    language=language,
                    status='processing',
                    processing_started_at=timezone.now()
                )
                
                # Increment daily count
                increment_daily_count(client_ip)
                
                logger.info(f"Created analysis record {analysis.id} for IP {client_ip}")
        
        except Exception as e:
            logger.error(f"Failed to create analysis record: {str(e)}")
            return Response({
                'error': 'Failed to create analysis record',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Process contract synchronously (you can make this async using Celery)
        try:
            self._process_contract_sync(analysis)
        except Exception as e:
            logger.error(f"Contract processing failed for {analysis.id}: {str(e)}")
            analysis.status = 'failed'
            analysis.error_message = str(e)
            analysis.save()
        
        # Return response
        response_serializer = ContractAnalysisSerializer(analysis)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def _process_contract_sync(self, analysis):
        """Process contract synchronously"""
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
            
        except Exception as e:
            logger.error(f"Contract processing failed: {str(e)}")
            analysis.status = 'failed'
            analysis.error_message = str(e)
            analysis.processing_completed_at = timezone.now()
            analysis.processing_time_seconds = (datetime.now() - start_time).total_seconds()
            analysis.save()
            raise

    @swagger_auto_schema(
        operation_description="Get analysis result by ID",
        responses={
            200: ContractAnalysisSerializer,
            404: 'Analysis not found'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Get analysis result by ID"""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="List all contract analyses",
        responses={200: ContractAnalysisListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List all contract analyses"""
        return super().list(request, *args, **kwargs)
    
    
    
    
    
    

@swagger_auto_schema(
    method='get',
    operation_description="Get API health status",
    responses={200: openapi.Response('API is healthy')}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """API health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })
    
    
    
    
    
    

@swagger_auto_schema(
    method='get',
    operation_description="Get rate limit status for current IP",
    responses={200: openapi.Response('Rate limit status')}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def rate_limit_status(request):
    """Get rate limit status for current IP"""
    client_ip = get_client_ip(request)
    can_proceed, current_count = check_daily_limit(client_ip)
    
    return Response({
        'ip_address': client_ip,
        'daily_limit': 5,
        'current_count': current_count,
        'remaining': max(0, 5 - current_count),
        'can_proceed': can_proceed,
        'reset_time': timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    })
