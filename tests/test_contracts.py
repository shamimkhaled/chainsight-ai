import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant
from apps.contracts.models import Contract, ContractAnalysis, Clause


class ContractModelTest(TestCase):
    """Test cases for Contract model"""

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

    def test_contract_creation(self):
        """Test contract creation"""
        contract = Contract.objects.create(
            tenant=self.tenant,
            uploaded_by=self.user,
            original_filename='test_contract.pdf',
            file_path='contracts/test_contract.pdf',
            file_size=1024,
            file_type='application/pdf',
            file_hash='abc123',
            industry='general'
        )

        self.assertEqual(contract.original_filename, 'test_contract.pdf')
        self.assertEqual(contract.status, 'pending')
        self.assertEqual(contract.tenant, self.tenant)
        self.assertEqual(contract.uploaded_by, self.user)

    def test_contract_str_method(self):
        """Test contract string representation"""
        contract = Contract.objects.create(
            tenant=self.tenant,
            uploaded_by=self.user,
            original_filename='test_contract.pdf',
            file_path='contracts/test_contract.pdf',
            file_size=1024,
            file_type='application/pdf',
            file_hash='abc123',
            industry='general'
        )

        expected_str = f"{contract.original_filename} - {contract.status}"
        self.assertEqual(str(contract), expected_str)


class ContractAnalysisModelTest(TestCase):
    """Test cases for ContractAnalysis model"""

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

    def test_analysis_creation(self):
        """Test contract analysis creation"""
        analysis = ContractAnalysis.objects.create(
            tenant=self.tenant,
            contract=self.contract,
            mongo_document_id='mongo123',
            overall_risk_score=75,
            critical_issues_count=2,
            missing_clauses_count=1,
            priority_level='high',
            processing_time=30.5,
            model_used='gpt-4-turbo'
        )

        self.assertEqual(analysis.overall_risk_score, 75)
        self.assertEqual(analysis.priority_level, 'high')
        self.assertEqual(analysis.contract, self.contract)

    def test_analysis_str_method(self):
        """Test analysis string representation"""
        analysis = ContractAnalysis.objects.create(
            tenant=self.tenant,
            contract=self.contract,
            mongo_document_id='mongo123',
            overall_risk_score=75,
            critical_issues_count=2,
            missing_clauses_count=1,
            priority_level='high',
            processing_time=30.5,
            model_used='gpt-4-turbo'
        )

        expected_str = f"Analysis for {self.contract.original_filename}"
        self.assertEqual(str(analysis), expected_str)


class ClauseModelTest(TestCase):
    """Test cases for Clause model"""

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

    def test_clause_creation(self):
        """Test clause creation"""
        clause = Clause.objects.create(
            tenant=self.tenant,
            contract=self.contract,
            clause_number='1.1',
            clause_type='payment',
            title='Payment Terms',
            content='Payment shall be made within 30 days...',
            content_hash='hash123',
            risk_level='medium',
            quality_score=85,
            completeness_score=90,
            is_standard=True,
            has_issues=False
        )

        self.assertEqual(clause.clause_number, '1.1')
        self.assertEqual(clause.clause_type, 'payment')
        self.assertEqual(clause.risk_level, 'medium')
        self.assertEqual(clause.contract, self.contract)

    def test_clause_str_method(self):
        """Test clause string representation"""
        clause = Clause.objects.create(
            tenant=self.tenant,
            contract=self.contract,
            clause_number='1.1',
            clause_type='payment',
            title='Payment Terms',
            content='Payment shall be made within 30 days...',
            content_hash='hash123'
        )

        expected_str = f"{clause.clause_number} - {clause.clause_type}"
        self.assertEqual(str(clause), expected_str)