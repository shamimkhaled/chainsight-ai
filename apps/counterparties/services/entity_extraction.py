import re
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EntityExtractionService:
    """
    Service for extracting counterparty entities from contract text
    """

    def __init__(self):
        self.entity_patterns = {
            'company_name': [
                r'(?i)(?:company|corporation|corp|inc|llc|ltd|limited|plc|gmbh|ag|sa|bv|nv)\s+["\']?([A-Z][A-Za-z0-9\s,&.-]+?)["\']?(?:\s+(?:company|corporation|corp|inc|llc|ltd|limited|plc|gmbh|ag|sa|bv|nv))?',
                r'(?i)["\']([A-Z][A-Za-z0-9\s,&.-]+?)["\'](?:\s+(?:company|corporation|corp|inc|llc|ltd|limited|plc|gmbh|ag|sa|bv|nv))',
            ],
            'person_name': [
                r'(?i)(?:mr\.|mrs\.|ms\.|dr\.|prof\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
                r'(?i)([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})(?:\s*,?\s*(?:esq\.|jd|phd|md))?',
            ],
            'address': [
                r'\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Place|Pl|Court|Ct)\s*,?\s*[A-Za-z\s]+,?\s*\d{5}',
            ],
            'email': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            ],
            'phone': [
                r'(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?',
            ],
        }

    def extract_entities(self, text):
        """
        Extract entities from contract text
        """
        entities = {
            'companies': [],
            'persons': [],
            'addresses': [],
            'emails': [],
            'phones': [],
        }

        try:
            # Extract companies
            for pattern in self.entity_patterns['company_name']:
                matches = re.findall(pattern, text)
                entities['companies'].extend(matches)

            # Extract persons
            for pattern in self.entity_patterns['person_name']:
                matches = re.findall(pattern, text)
                entities['persons'].extend(matches)

            # Extract addresses
            for pattern in self.entity_patterns['address']:
                matches = re.findall(pattern, text)
                entities['addresses'].extend(matches)

            # Extract emails
            for pattern in self.entity_patterns['email']:
                matches = re.findall(pattern, text)
                entities['emails'].extend(matches)

            # Extract phones
            for pattern in self.entity_patterns['phone']:
                matches = re.findall(pattern, text)
                entities['phones'].extend(matches)

            # Remove duplicates and clean
            for key in entities:
                entities[key] = list(set(entities[key]))
                entities[key] = [e.strip() for e in entities[key] if e.strip()]

        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")

        return entities

    def identify_counterparties(self, text, industry='general'):
        """
        Identify and classify counterparties from contract text
        """
        entities = self.extract_entities(text)

        counterparties = []

        # Process companies as primary counterparties
        for company in entities['companies'][:5]:  # Limit to top 5
            counterparty = {
                'name': company,
                'entity_type': 'company',
                'contact_email': entities['emails'][0] if entities['emails'] else None,
                'contact_phone': entities['phones'][0] if entities['phones'] else None,
                'address': entities['addresses'][0] if entities['addresses'] else None,
                'metadata': {
                    'extraction_method': 'regex',
                    'confidence': 0.8,
                    'industry': industry
                }
            }
            counterparties.append(counterparty)

        # Process persons as individual counterparties
        for person in entities['persons'][:3]:  # Limit to top 3
            counterparty = {
                'name': person,
                'entity_type': 'individual',
                'contact_email': None,  # Would need more sophisticated extraction
                'metadata': {
                    'extraction_method': 'regex',
                    'confidence': 0.7,
                    'industry': industry
                }
            }
            counterparties.append(counterparty)

        return counterparties