import openai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """
    Service for AI-powered contract analysis
    """

    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL

    def analyze_contract(self, text, industry, language):
        """
        Perform comprehensive contract analysis using AI
        """
        try:
            prompt = f"""
            Analyze the following contract text for a {industry} company.
            Language: {language}

            Please provide a comprehensive analysis including:

            1. Overall risk assessment (score 1-100, where 100 is highest risk)
            2. Compliance score (1-100, where 100 is fully compliant)
            3. Critical issues identified
            4. Missing critical clauses
            5. Executive summary with priority level (critical/high/medium/low)

            Contract text:
            {text[:10000]}  # Limit text length for API

            Return the analysis in JSON format.
            """

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a legal contract analysis expert. Provide detailed, accurate analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )

            # Parse the response (simplified for this example)
            analysis_result = self._parse_analysis_response(response.choices[0].message.content)

            return analysis_result

        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            # Return default analysis
            return {
                'overall_risk_score': 50,
                'compliance_score': 70,
                'critical_issues': [],
                'missing_critical_clauses': [],
                'executive_summary': {
                    'priority_level': 'medium',
                    'summary': 'Analysis completed with default values due to processing error.'
                }
            }

    def extract_clauses(self, text):
        """
        Extract and categorize clauses from contract text
        """
        try:
            prompt = f"""
            Extract and categorize all clauses from the following contract text.
            For each clause, provide:
            - Clause number/title
            - Clause type (payment, termination, liability, confidentiality, etc.)
            - Full text content
            - Risk level (critical/high/medium/low)

            Contract text:
            {text[:8000]}

            Return in JSON format as a list of clause objects.
            """

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a legal expert specializing in contract clause identification."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.2
            )

            # Parse clauses (simplified)
            clauses = self._parse_clauses_response(response.choices[0].message.content)

            return clauses

        except Exception as e:
            logger.error(f"Error extracting clauses: {str(e)}")
            return []

    def analyze_sentiment(self, text, clauses):
        """
        Perform sentiment analysis on contract text
        """
        try:
            prompt = f"""
            Analyze the sentiment of the following contract text and clauses.
            Provide an overall sentiment score (-1 to 1, where -1 is very negative, 0 is neutral, 1 is very positive).

            Contract text:
            {text[:5000]}

            Return sentiment analysis in JSON format.
            """

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis expert for legal documents."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )

            # Parse sentiment (simplified)
            sentiment = self._parse_sentiment_response(response.choices[0].message.content)

            return sentiment

        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return {
                'overall_score': 0.0,
                'confidence': 0.5
            }

    def _parse_analysis_response(self, response_text):
        """Parse AI analysis response (simplified implementation)"""
        # In a real implementation, this would properly parse JSON
        return {
            'overall_risk_score': 45,
            'compliance_score': 78,
            'critical_issues': ['Potential liability clause', 'Termination terms'],
            'missing_critical_clauses': ['Force majeure', 'Governing law'],
            'executive_summary': {
                'priority_level': 'medium',
                'summary': 'Contract analysis completed. Moderate risk identified.'
            }
        }

    def _parse_clauses_response(self, response_text):
        """Parse clauses response (simplified implementation)"""
        # In a real implementation, this would properly parse JSON
        return [
            {
                'clause_number': '1.1',
                'clause_type': 'payment',
                'title': 'Payment Terms',
                'content': 'Payment shall be made within 30 days...',
                'risk_level': 'medium',
                'quality_score': 85,
                'is_standard': True
            },
            {
                'clause_number': '2.1',
                'clause_type': 'termination',
                'title': 'Termination',
                'content': 'Either party may terminate...',
                'risk_level': 'high',
                'quality_score': 72,
                'is_standard': False
            }
        ]

    def _parse_sentiment_response(self, response_text):
        """Parse sentiment response (simplified implementation)"""
        return {
            'overall_score': 0.1,
            'confidence': 0.8
        }