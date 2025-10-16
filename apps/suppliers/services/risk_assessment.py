import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class RiskAssessmentService:
    """
    Service for assessing supplier risk
    """

    def __init__(self):
        self.api_keys = {
            'duns': settings.DUNS_API_KEY if hasattr(settings, 'DUNS_API_KEY') else None,
            'credit': settings.CREDIT_API_KEY if hasattr(settings, 'CREDIT_API_KEY') else None,
        }

    def assess_supplier_risk(self, supplier):
        """
        Perform comprehensive risk assessment for a supplier
        """
        risk_scores = {
            'financial_risk': self._assess_financial_risk(supplier),
            'operational_risk': self._assess_operational_risk(supplier),
            'compliance_risk': self._assess_compliance_risk(supplier),
            'reputational_risk': self._assess_reputational_risk(supplier),
            'geopolitical_risk': self._assess_geopolitical_risk(supplier),
            'cyber_security_risk': self._assess_cyber_security_risk(supplier),
        }

        # Calculate overall risk score (weighted average)
        weights = {
            'financial_risk': 0.25,
            'operational_risk': 0.20,
            'compliance_risk': 0.20,
            'reputational_risk': 0.15,
            'geopolitical_risk': 0.10,
            'cyber_security_risk': 0.10,
        }

        overall_score = sum(
            risk_scores[category] * weights[category]
            for category in risk_scores
        )

        # Determine risk level
        if overall_score >= 80:
            risk_level = 'critical'
        elif overall_score >= 60:
            risk_level = 'high'
        elif overall_score >= 40:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        return {
            'overall_risk_score': int(overall_score),
            'overall_risk_level': risk_level,
            'risk_scores': risk_scores,
            'risk_factors': self._identify_risk_factors(supplier, risk_scores),
            'recommendations': self._generate_recommendations(risk_scores),
        }

    def _assess_financial_risk(self, supplier):
        """Assess financial risk based on credit score and payment history"""
        score = 50  # Default medium risk

        if supplier.counterparty.credit_score:
            if supplier.counterparty.credit_score >= 800:
                score = 20  # Low risk
            elif supplier.counterparty.credit_score >= 600:
                score = 40  # Medium risk
            else:
                score = 80  # High risk

        # Adjust based on payment terms
        if supplier.payment_terms_days and supplier.payment_terms_days > 90:
            score += 10

        return min(score, 100)

    def _assess_operational_risk(self, supplier):
        """Assess operational risk based on performance metrics"""
        score = 50  # Default

        if supplier.on_time_delivery_rate is not None:
            if supplier.on_time_delivery_rate >= 95:
                score -= 20
            elif supplier.on_time_delivery_rate < 80:
                score += 20

        if supplier.quality_score is not None:
            if supplier.quality_score >= 90:
                score -= 15
            elif supplier.quality_score < 70:
                score += 15

        return max(0, min(score, 100))

    def _assess_compliance_risk(self, supplier):
        """Assess compliance risk"""
        score = 30  # Default low-moderate

        # Check if supplier is verified
        if not supplier.counterparty.is_verified:
            score += 30

        # Check country risk (simplified)
        high_risk_countries = ['North Korea', 'Iran', 'Syria']
        if supplier.counterparty.country in high_risk_countries:
            score += 40

        return min(score, 100)

    def _assess_reputational_risk(self, supplier):
        """Assess reputational risk"""
        score = 40  # Default moderate

        # Check if blacklisted
        if supplier.status == 'blacklisted':
            score = 100

        # Check tier (higher tier = lower risk)
        if supplier.tier == 'tier1':
            score -= 20
        elif supplier.tier == 'tier3':
            score += 10

        return max(0, min(score, 100))

    def _assess_geopolitical_risk(self, supplier):
        """Assess geopolitical risk based on location"""
        score = 20  # Default low

        high_risk_regions = ['Middle East', 'Eastern Europe', 'Asia']
        if supplier.counterparty.country:
            # Simplified country to region mapping
            country_regions = {
                'Russia': 'Eastern Europe',
                'Ukraine': 'Eastern Europe',
                'China': 'Asia',
                'North Korea': 'Asia',
                'Iran': 'Middle East',
                'Iraq': 'Middle East',
                'Syria': 'Middle East',
            }

            region = country_regions.get(supplier.counterparty.country)
            if region in high_risk_regions:
                score += 50

        return min(score, 100)

    def _assess_cyber_security_risk(self, supplier):
        """Assess cyber security risk"""
        score = 30  # Default moderate

        # Larger companies might have better security
        if supplier.annual_spend and supplier.annual_spend > 1000000:
            score -= 10

        # Companies in tech industry might be more vulnerable
        if supplier.category and 'technology' in supplier.category.lower():
            score += 20

        return max(0, min(score, 100))

    def _identify_risk_factors(self, supplier, risk_scores):
        """Identify specific risk factors"""
        factors = []

        if risk_scores['financial_risk'] > 60:
            factors.append("Poor financial health indicated by low credit score")

        if risk_scores['operational_risk'] > 60:
            factors.append("Poor operational performance metrics")

        if risk_scores['compliance_risk'] > 60:
            factors.append("Compliance concerns or unverified status")

        if risk_scores['geopolitical_risk'] > 60:
            factors.append(f"High geopolitical risk in {supplier.counterparty.country}")

        return factors

    def _generate_recommendations(self, risk_scores):
        """Generate risk mitigation recommendations"""
        recommendations = []

        if risk_scores['financial_risk'] > 60:
            recommendations.append("Implement stricter payment terms and monitoring")

        if risk_scores['operational_risk'] > 60:
            recommendations.append("Increase quality inspections and performance monitoring")

        if risk_scores['compliance_risk'] > 60:
            recommendations.append("Conduct thorough compliance verification")

        if risk_scores['cyber_security_risk'] > 60:
            recommendations.append("Implement additional cyber security measures")

        return recommendations