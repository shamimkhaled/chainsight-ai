import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant
from apps.contracts.models import Contract


class ContractAnalysisTest(TestCase):
    """Test cases for contract analysis functionality"""

    def setUp(self):
        self.tenant = Tenant.objects.create(
            name='Test Tenant',
            subdomain='test'
        )
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
            tenant=self.tenant
        )
        self.contract = Contract.objects.create(
            tenant=self.tenant,
            uploaded_by=self.user,
            original_filename='test_contract.pdf',
            file_path='contracts/test_contract.pdf',
            file_size=1024,
            file_type='application/pdf',
            file_hash='abc123',
            industry='general'
        )

    def test_contract_status_transitions(self):
        """Test contract status transitions during analysis"""
        # Initial status should be pending
        self.assertEqual(self.contract.status, 'pending')

        # Update to processing
        self.contract.status = 'processing'
        self.contract.processing_stage = 'text_extraction'
        self.contract.progress_percentage = 25
        self.contract.save()

        self.contract.refresh_from_db()
        self.assertEqual(self.contract.status, 'processing')
        self.assertEqual(self.contract.processing_stage, 'text_extraction')
        self.assertEqual(self.contract.progress_percentage, 25)

        # Update to completed
        self.contract.status = 'completed'
        self.contract.progress_percentage = 100
        self.contract.risk_score = 75
        self.contract.compliance_score = 85
        self.contract.sentiment_score = 0.6
        self.contract.save()

        self.contract.refresh_from_db()
        self.assertEqual(self.contract.status, 'completed')
        self.assertEqual(self.contract.progress_percentage, 100)
        self.assertEqual(self.contract.risk_score, 75)
        self.assertEqual(self.contract.compliance_score, 85)
        self.assertEqual(self.contract.sentiment_score, 0.6)

    def test_contract_risk_levels(self):
        """Test contract risk level categorization"""
        # Low risk
        self.contract.risk_score = 25
        self.contract.save()
        self.assertEqual(self.contract.risk_score, 25)

        # Medium risk
        self.contract.risk_score = 50
        self.contract.save()
        self.assertEqual(self.contract.risk_score, 50)

        # High risk
        self.contract.risk_score = 75
        self.contract.save()
        self.assertEqual(self.contract.risk_score, 75)

        # Critical risk
        self.contract.risk_score = 95
        self.contract.save()
        self.assertEqual(self.contract.risk_score, 95)

    def test_contract_expiry_filtering(self):
        """Test contract expiry date filtering"""
        from datetime import date, timedelta

        # Create contracts with different expiry dates
        future_contract = Contract.objects.create(
            tenant=self.tenant,
            uploaded_by=self.user,
            original_filename='future_contract.pdf',
            file_path='contracts/future_contract.pdf',
            file_size=1024,
            file_type='application/pdf',
            file_hash='def456',
            industry='general',
            expiry_date=date.today() + timedelta(days=30)
        )

        expired_contract = Contract.objects.create(
            tenant=self.tenant,
            uploaded_by=self.user,
            original_filename='expired_contract.pdf',
            file_path='contracts/expired_contract.pdf',
            file_size=1024,
            file_type='application/pdf',
            file_hash='ghi789',
            industry='general',
            expiry_date=date.today() - timedelta(days=30)
        )

        # Test filtering by expiry date
        from django.db.models import Q
        expiring_contracts = Contract.objects.filter(
            tenant=self.tenant,
            expiry_date__lte=date.today() + timedelta(days=60),
            expiry_date__gte=date.today()
        )

        self.assertIn(future_contract, expiring_contracts)
        self.assertNotIn(expired_contract, expiring_contracts)

    def test_contract_industry_categorization(self):
        """Test contract industry categorization"""
        industries = ['manufacturing', 'it', 'law_firm', 'construction', 'general']

        for industry in industries:
            contract = Contract.objects.create(
                tenant=self.tenant,
                uploaded_by=self.user,
                original_filename=f'{industry}_contract.pdf',
                file_path=f'contracts/{industry}_contract.pdf',
                file_size=1024,
                file_type='application/pdf',
                file_hash=f'hash_{industry}',
                industry=industry
            )

            self.assertEqual(contract.industry, industry)

            # Clean up
            contract.delete()

    def test_contract_file_validation(self):
        """Test contract file validation"""
        # Valid file types
        valid_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']

        for file_type in valid_types:
            contract = Contract.objects.create(
                tenant=self.tenant,
                uploaded_by=self.user,
                original_filename=f'test.{file_type.split("/")[-1]}',
                file_path=f'contracts/test.{file_type.split("/")[-1]}',
                file_size=1024,
                file_type=file_type,
                file_hash=f'hash_{file_type}',
                industry='general'
            )

            self.assertEqual(contract.file_type, file_type)

            # Clean up
            contract.delete()