import requests
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ERPIntegrationService:
    """
    ERP system integration service (SAP, Oracle, NetSuite, etc.)
    """
    
    def __init__(self, integration):
        self.integration = integration
        self.config = integration.config
        self.credentials = integration.credentials
    
    def sync_vendors(self):
        """
        Sync vendors from ERP to ChainSight as counterparties
        """
        try:
            vendors = self._fetch_vendors_from_erp()
            
            synced_count = 0
            for vendor_data in vendors:
                counterparty = self._create_or_update_counterparty(vendor_data)
                
                # Create ERP entity mapping
                from apps.integrations.models import ERPEntity
                ERPEntity.objects.update_or_create(
                    integration=self.integration,
                    entity_type='vendor',
                    external_id=vendor_data['id'],
                    defaults={
                        'tenant': self.integration.tenant,
                        'entity_data': vendor_data,
                        'counterparty': counterparty,
                        'sync_status': 'synced'
                    }
                )
                synced_count += 1
            
            # Log success
            self._log_integration_activity('sync', 'success', {
                'synced_count': synced_count,
                'entity_type': 'vendors'
            })
            
            return {
                'success': True,
                'synced_count': synced_count
            }
            
        except Exception as e:
            logger.error(f"Error syncing vendors: {str(e)}")
            self._log_integration_activity('sync', 'failed', {
                'error': str(e)
            })
            raise
    
    def sync_purchase_orders(self):
        """
        Sync purchase orders from ERP
        """
        try:
            purchase_orders = self._fetch_purchase_orders_from_erp()
            
            synced_count = 0
            for po_data in purchase_orders:
                # Try to match with existing contract
                contract = self._match_contract_with_po(po_data)
                
                # Create ERP entity
                from apps.integrations.models import ERPEntity
                ERPEntity.objects.update_or_create(
                    integration=self.integration,
                    entity_type='purchase_order',
                    external_id=po_data['po_number'],
                    defaults={
                        'tenant': self.integration.tenant,
                        'entity_data': po_data,
                        'contract': contract,
                        'sync_status': 'synced'
                    }
                )
                synced_count += 1
            
            return {
                'success': True,
                'synced_count': synced_count
            }
            
        except Exception as e:
            logger.error(f"Error syncing purchase orders: {str(e)}")
            raise
    
    def push_contract_to_erp(self, contract):
        """
        Push ChainSight contract data to ERP
        """
        try:
            # Prepare contract data for ERP
            erp_data = self._transform_contract_to_erp_format(contract)
            
            # Send to ERP
            result = self._send_to_erp(erp_data)
            
            # Create ERP entity mapping
            from apps.integrations.models import ERPEntity
            ERPEntity.objects.update_or_create(
                integration=self.integration,
                entity_type='contract',
                external_id=result['external_id'],
                defaults={
                    'tenant': contract.tenant,
                    'entity_data': erp_data,
                    'contract': contract,
                    'sync_status': 'synced'
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error pushing contract to ERP: {str(e)}")
            raise
    
    def _fetch_vendors_from_erp(self) -> List[Dict[str, Any]]:
        """
        Fetch vendors from ERP system
        """
        # Implementation depends on ERP type (SAP, Oracle, etc.)
        if self.integration.integration_type == 'sap':
            return self._fetch_from_sap_api('/vendors')
        elif self.integration.integration_type == 'oracle':
            return self._fetch_from_oracle_api('/suppliers')
        elif self.integration.integration_type == 'netsuite':
            return self._fetch_from_netsuite_api('/vendor')
        else:
            # Generic REST API
            return self._fetch_from_generic_api('/vendors')
    
    def _fetch_purchase_orders_from_erp(self) -> List[Dict[str, Any]]:
        """
        Fetch purchase orders from ERP
        """
        # Similar to vendors, but for POs
        if self.integration.integration_type == 'sap':
            return self._fetch_from_sap_api('/purchase-orders')
        else:
            return self._fetch_from_generic_api('/purchase-orders')
    
    def _fetch_from_sap_api(self, endpoint: str) -> List[Dict[str, Any]]:
        """
        Fetch data from SAP OData API
        """
        try:
            base_url = self.config.get('api_url')
            url = f"{base_url}{endpoint}"
            
            headers = {
                'Authorization': f"Basic {self.credentials.get('api_key')}",
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get('d', {}).get('results', [])
            
        except Exception as e:
            logger.error(f"Error fetching from SAP: {str(e)}")
            return []
    
    def _fetch_from_generic_api(self, endpoint: str) -> List[Dict[str, Any]]:
        """
        Fetch data from generic REST API
        """
        try:
            base_url = self.config.get('api_url')
            url = f"{base_url}{endpoint}"
            
            headers = {
                'Authorization': f"Bearer {self.credentials.get('api_key')}",
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json().get('data', [])
            
        except Exception as e:
            logger.error(f"Error fetching from API: {str(e)}")
            return []
    
    def _create_or_update_counterparty(self, vendor_data: Dict[str, Any]):
        """
        Create or update counterparty from vendor data
        """
        from apps.counterparties.models import Counterparty
        
        counterparty, created = Counterparty.objects.update_or_create(
            tenant=self.integration.tenant,
            registration_number=vendor_data.get('vendor_id'),
            defaults={
                'name': vendor_data.get('name'),
                'legal_name': vendor_data.get('legal_name', vendor_data.get('name')),
                'address': vendor_data.get('address', ''),
                'city': vendor_data.get('city', ''),
                'country': vendor_data.get('country', ''),
                'contact_email': vendor_data.get('email', ''),
                'contact_phone': vendor_data.get('phone', ''),
                'metadata': {
                    'erp_data': vendor_data,
                    'synced_from_erp': True
                }
            }
        )
        
        return counterparty
    
    def _match_contract_with_po(self, po_data: Dict[str, Any]):
        """
        Try to match purchase order with existing contract
        """
        from apps.contracts.models import Contract
        
        # Try to match by PO reference in contract metadata
        contract = Contract.objects.filter(
            tenant=self.integration.tenant,
            metadata__po_number=po_data.get('po_number')
        ).first()
        
        return contract
    
    def _transform_contract_to_erp_format(self, contract) -> Dict[str, Any]:
        """
        Transform contract data to ERP format
        """
        return {
            'contract_number': str(contract.id),
            'contract_name': contract.original_filename,
            'contract_type': contract.contract_type,
            'effective_date': str(contract.effective_date) if contract.effective_date else None,
            'expiry_date': str(contract.expiry_date) if contract.expiry_date else None,
            'contract_value': str(contract.contract_value) if contract.contract_value else None,
            'currency': contract.currency,
            'status': contract.status,
            'vendor_id': None,  # Get from counterparty
            'metadata': contract.metadata
        }
    
    def _send_to_erp(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send data to ERP system
        """
        try:
            base_url = self.config.get('api_url')
            url = f"{base_url}/contracts"
            
            headers = {
                'Authorization': f"Bearer {self.credentials.get('api_key')}",
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error sending to ERP: {str(e)}")
            raise
    
    def _log_integration_activity(self, action: str, status: str, data: Dict[str, Any]):
        """
        Log integration activity
        """
        from apps.integrations.models import IntegrationLog
        
        IntegrationLog.objects.create(
            tenant=self.integration.tenant,
            integration=self.integration,
            action=action,
            status=status,
            request_data=data,
            response_data={}
        )

