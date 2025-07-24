
import openai
import json
from datetime import datetime
from typing import Dict
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Industry-specific knowledge base (from your notebook)
INDUSTRY_CONTEXTS = {
    "garment": {
        "critical_clauses": [
            "Quality Standards and Specifications",
            "Delivery Timelines and Penalties",
            "Material Sourcing Requirements",
            "Labor Compliance Standards",
            "Environmental Regulations",
            "Force Majeure for Supply Chain",
            "Payment Terms for Bulk Orders",
            "Inspection and Quality Control"
        ],
        "risk_factors": [
            "Supply chain disruption",
            "Quality control failures",
            "Labor law violations",
            "Environmental compliance",
            "Seasonal demand fluctuations"
        ]
    },
    "it": {
        "critical_clauses": [
            "Data Protection and Privacy",
            "Intellectual Property Rights",
            "Software Licensing Terms",
            "Service Level Agreements",
            "Liability Limitations",
            "Confidentiality and NDAs",
            "Maintenance and Support",
            "Termination and Data Return"
        ],
        "risk_factors": [
            "Data breaches and privacy violations",
            "IP infringement disputes",
            "Technology obsolescence",
            "Service interruptions",
            "Cybersecurity threats"
        ]
    },
    "construction": {
        "critical_clauses": [
            "Safety Regulations and Protocols",
            "Milestone Payment Schedules",
            "Material Quality Standards",
            "Weather and Delay Provisions",
            "Subcontractor Management",
            "Insurance and Bonding",
            "Change Order Procedures",
            "Final Inspection and Acceptance"
        ],
        "risk_factors": [
            "Construction delays and overruns",
            "Safety incidents and liability",
            "Material price fluctuations",
            "Weather-related delays",
            "Regulatory compliance issues"
        ]
    },
    
    "general": {
        "critical_clauses": [
            "Governing Law and Jurisdiction",
            "Dispute Resolution Mechanisms",
            "Confidentiality Obligations",
            "Termination Conditions",
            "Indemnification Provisions",
            "Force Majeure Clauses",
            "Payment Terms and Conditions",
            "Intellectual Property Rights"
        ],
        "risk_factors": [
            "Breach of contract",
            "Dispute over terms and conditions",
            "Non-compliance with regulations",
            "Financial instability of parties",
            "Market volatility affecting terms"
        ]
    }
}

class ContractAIAnalyzer:
    """Main AI analyzer using GPT-4 for contract intelligence"""

    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-4o"
        self.max_tokens = 4000

    def create_analysis_prompt(self, contract_text: str, industry: str, language: str) -> str:
        """Create specialized prompt for contract analysis"""

        industry_context = INDUSTRY_CONTEXTS.get(industry.lower(), {})
        critical_clauses = industry_context.get("critical_clauses", [])
        risk_factors = industry_context.get("risk_factors", [])

        prompt = f"""
You are an expert ChainSight Contract AI Intelligence Analyst specializing in {industry.upper()} industry contracts.

DOCUMENT LANGUAGE: {language}
TARGET INDUSTRY: {industry.upper()}

CRITICAL CLAUSES FOR {industry.upper()} INDUSTRY:
{chr(10).join([f"- {clause}" for clause in critical_clauses])}

COMMON RISK FACTORS:
{chr(10).join([f"- {risk}" for risk in risk_factors])}

CONTRACT TEXT TO ANALYZE:
{contract_text}

ANALYSIS REQUIREMENTS:
1. Perform comprehensive risk assessment (scale 1-10)
2. Identify missing critical clauses specific to {industry} industry
3. Detect potential legal, financial, and operational risks
4. Provide industry-specific recommendations
5. Suggest specific contract improvements

OUTPUT FORMAT (JSON):
{{
    "document_analysis": {{
        "industry": "{industry}",
        "language": "{language}",
        "analysis_date": "{datetime.now().strftime('%Y-%m-%d')}",
        "overall_risk_score": [1-10],
        "executive_summary": {{
            "critical_issues_count": [number],
            "missing_clauses_count": [number],
            "priority_level": "[High/Medium/Low]"
        }},
        "risk_assessment": [
            {{
                "category": "[Legal/Financial/Operational]",
                "severity": "[High/Medium/Low]",
                "description": "[detailed description]",
                "potential_impact": "[impact description]",
                "likelihood": "[High/Medium/Low]"
            }}
        ],
        "missing_critical_clauses": [
            {{
                "clause_name": "[clause name]",
                "importance": "[Critical/Important/Recommended]",
                "reason": "[why this clause is needed]",
                "suggested_text": "[sample clause text]"
            }}
        ],
        "identified_risks": [
            {{
                "risk_type": "[specific risk]",
                "severity": "[High/Medium/Low]",
                "current_protection": "[existing protection if any]",
                "mitigation_suggestion": "[how to address]"
            }}
        ],
        "improvement_recommendations": [
            {{
                "priority": [1-3],
                "category": "[Addition/Modification/Clarification]",
                "description": "[what needs to be changed]",
                "justification": "[why this change is needed]",
                "suggested_implementation": "[how to implement]"
            }}
        ],
        "compliance_check": {{
            "industry_standards": "[compliant/non-compliant/partial]",
            "regulatory_requirements": "[analysis of regulatory compliance]",
            "best_practices": "[adherence to industry best practices]"
        }}
    }}
}}

Provide thorough, industry-specific analysis with actionable recommendations.
"""
        return prompt

    def analyze_contract(self, contract_text: str, industry: str, language: str) -> Dict:
        """Analyze contract using GPT-4"""

        try:
            prompt = self.create_analysis_prompt(contract_text, industry, language)

            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Contract AI Intelligence Analyst with deep expertise in legal contract analysis, risk assessment, and industry-specific knowledge. Provide detailed, actionable analysis in the specified JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.3,  # Lower temperature for more consistent analysis
                response_format={"type": "json_object"}
            )

            analysis_result = json.loads(response.choices[0].message.content)
            logger.info("Contract analysis completed successfully")
            return analysis_result

        except Exception as e:
            logger.error(f"Contract analysis failed: {str(e)}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }