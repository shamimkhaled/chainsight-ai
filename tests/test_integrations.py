import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant


class IntegrationTest(TestCase):
    """Integration tests for the application"""

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

    def test_tenant_isolation(self):
        """Test that tenants are properly isolated"""
        # Create another tenant
        other_tenant = Tenant.objects.create(
            name='Other Tenant',
            subdomain='other'
        )
        other_user = get_user_model().objects.create_user(
            email='other@example.com',
            password='testpass123',
            tenant=other_tenant
        )

        # Users should be isolated by tenant
        tenant_users = get_user_model().objects.filter(tenant=self.tenant)
        other_tenant_users = get_user_model().objects.filter(tenant=other_tenant)

        self.assertIn(self.user, tenant_users)
        self.assertNotIn(self.user, other_tenant_users)
        self.assertIn(other_user, other_tenant_users)
        self.assertNotIn(other_user, tenant_users)

    def test_user_permissions_by_role(self):
        """Test user permissions based on roles"""
        # Test admin user
        admin_user = get_user_model().objects.create_user(
            email='admin@example.com',
            password='testpass123',
            tenant=self.tenant,
            role='admin'
        )

        # Test manager user
        manager_user = get_user_model().objects.create_user(
            email='manager@example.com',
            password='testpass123',
            tenant=self.tenant,
            role='manager'
        )

        # Test regular user
        regular_user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            tenant=self.tenant,
            role='user'
        )

        # Test viewer user
        viewer_user = get_user_model().objects.create_user(
            email='viewer@example.com',
            password='testpass123',
            tenant=self.tenant,
            role='viewer'
        )

        # Verify roles
        self.assertEqual(admin_user.role, 'admin')
        self.assertEqual(manager_user.role, 'manager')
        self.assertEqual(regular_user.role, 'user')
        self.assertEqual(viewer_user.role, 'viewer')

    def test_contract_workflow(self):
        """Test complete contract upload and analysis workflow"""
        from apps.contracts.models import Contract
        from apps.contracts.serializers import ContractUploadSerializer
        from io import BytesIO
        from django.core.files.base import ContentFile

        # Create a mock file
        mock_file = ContentFile(b'fake pdf content', name='test_contract.pdf')

        # Create contract via serializer
        data = {
            'file': mock_file,
            'industry': 'general',
            'language': 'english'
        }

        serializer = ContractUploadSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # Create contract
        contract = Contract.objects.create(
            tenant=self.tenant,
            uploaded_by=self.user,
            original_filename='test_contract.pdf',
            file_path='contracts/test_contract.pdf',
            file_size=1024,
            file_type='application/pdf',
            file_hash='test_hash',
            industry='general',
            language='english'
        )

        # Verify contract creation
        self.assertEqual(contract.tenant, self.tenant)
        self.assertEqual(contract.uploaded_by, self.user)
        self.assertEqual(contract.status, 'pending')

        # Simulate analysis completion
        contract.status = 'completed'
        contract.risk_score = 65
        contract.compliance_score = 80
        contract.sentiment_score = 0.7
        contract.save()

        contract.refresh_from_db()
        self.assertEqual(contract.status, 'completed')
        self.assertEqual(contract.risk_score, 65)

    def test_alert_system_integration(self):
        """Test alert system integration"""
        from apps.alerts.models import AlertRule, Alert

        # Create an alert rule
        alert_rule = AlertRule.objects.create(
            tenant=self.tenant,
            name='High Risk Alert',
            alert_type='risk_threshold',
            severity='high',
            threshold_value=70.0,
            comparison_operator='gte',
            is_active=True
        )

        # Create a contract that should trigger the alert
        from apps.contracts.models import Contract
        contract = Contract.objects.create(
            tenant=self.tenant,
            uploaded_by=self.user,
            original_filename='high_risk_contract.pdf',
            file_path='contracts/high_risk_contract.pdf',
            file_size=1024,
            file_type='application/pdf',
            file_hash='high_risk_hash',
            industry='general',
            risk_score=85  # Above threshold
        )

        # Create alert
        alert = Alert.objects.create(
            tenant=self.tenant,
            alert_rule=alert_rule,
            alert_type='risk_threshold',
            severity='high',
            title='High Risk Contract Detected',
            message=f'Contract {contract.original_filename} has risk score of {contract.risk_score}',
            contract=contract
        )

        # Verify alert creation
        self.assertEqual(alert.tenant, self.tenant)
        self.assertEqual(alert.alert_rule, alert_rule)
        self.assertEqual(alert.contract, contract)
        self.assertEqual(alert.status, 'active')

    def test_supplier_management_integration(self):
        """Test supplier management integration"""
        from apps.counterparties.models import Counterparty
        from apps.suppliers.models import Supplier

        # Create a counterparty
        counterparty = Counterparty.objects.create(
            tenant=self.tenant,
            name='Test Supplier Corp',
            entity_type='company',
            country='US'
        )

        # Create supplier profile
        supplier = Supplier.objects.create(
            tenant=self.tenant,
            counterparty=counterparty,
            supplier_code='SUP001',
            category='IT Services',
            tier='tier1'
        )

        # Verify integration
        self.assertEqual(supplier.counterparty, counterparty)
        self.assertEqual(supplier.tenant, self.tenant)
        self.assertEqual(supplier.supplier_code, 'SUP001')

        # Test reverse relationship
        self.assertEqual(counterparty.supplier_profile, supplier)