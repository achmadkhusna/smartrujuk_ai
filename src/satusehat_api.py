"""
SATUSEHAT API Integration Module with Real Data Support
Integrates with SATUSEHAT FHIR API to fetch real patient and referral data
"""
import os
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import logging
import time
from datetime import datetime, timedelta

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SATUSEHATClient:
    def __init__(self):
        self.org_id = os.getenv('SATUSEHAT_ORG_ID')
        self.client_id = os.getenv('SATUSEHAT_CLIENT_ID')
        self.client_secret = os.getenv('SATUSEHAT_CLIENT_SECRET')
        # Use sandbox URL for testing with provided credentials
        self.auth_url = os.getenv('SATUSEHAT_AUTH_URL', 'https://api-satusehat-stg.dto.kemkes.go.id/oauth2/v1')
        self.base_url = os.getenv('SATUSEHAT_BASE_URL', 'https://api-satusehat-stg.dto.kemkes.go.id/fhir-r4/v1')
        self.access_token = None
        self.token_expires_at = None
        self.offline_mode = False
        
        # Check if we have valid credentials
        if not all([self.org_id, self.client_id, self.client_secret]):
            logger.warning("SATUSEHAT API credentials not found, using offline mode")
            self.offline_mode = True
        else:
            logger.info(f"SATUSEHAT Client initialized with Organization ID: {self.org_id}")
        
    def get_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        Get access token from SATUSEHAT API with token caching
        Args:
            force_refresh: Force token refresh even if not expired
        Returns:
            Access token string or None if failed
        """
        if self.offline_mode:
            logger.info("Operating in offline mode, skipping token retrieval")
            return None
        
        # Check if we have a valid token
        if self.access_token and self.token_expires_at and not force_refresh:
            if datetime.now() < self.token_expires_at:
                logger.debug("Using cached access token")
                return self.access_token
            
        try:
            url = f"{self.auth_url}/accesstoken?grant_type=client_credentials"
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            auth = (self.client_id, self.client_secret)
            
            logger.info(f"Requesting access token from {url}")
            response = requests.post(url, headers=headers, auth=auth, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                expires_in = data.get('expires_in', 3600)  # Default 1 hour
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)  # Refresh 1 min early
                logger.info("Successfully obtained access token")
                return self.access_token
            else:
                logger.error(f"Token request failed: {response.status_code} - {response.text}")
                raise Exception(f"Token request failed: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Error getting access token: {str(e)}, switching to offline mode")
            self.offline_mode = True
            return None
    
    def _make_fhir_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make a FHIR API request with proper authentication
        Args:
            endpoint: FHIR endpoint (e.g., 'Patient', 'ServiceRequest')
            params: Query parameters
        Returns:
            Response data or None if failed
        """
        if self.offline_mode:
            return None
            
        if not self.access_token:
            self.get_access_token()
        
        if self.offline_mode:
            return None
        
        try:
            url = f"{self.base_url}/{endpoint}"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            logger.info(f"Making FHIR request to {endpoint}")
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 401:
                # Token expired, refresh and retry
                logger.info("Token expired, refreshing...")
                self.get_access_token(force_refresh=True)
                headers['Authorization'] = f'Bearer {self.access_token}'
                response = requests.get(url, headers=headers, params=params, timeout=30)
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error making FHIR request to {endpoint}: {str(e)}")
            return None
    
    def get_patients(self, count: int = 100, page: int = 1) -> Optional[List[Dict]]:
        """
        Get list of patients from SATUSEHAT FHIR API
        Args:
            count: Number of patients to fetch per page
            page: Page number
        Returns:
            List of patient resources
        """
        if self.offline_mode:
            logger.info("Using offline sample data for patients")
            return self._get_sample_patients()
        
        params = {
            '_count': count,
            '_page': page
        }
        
        data = self._make_fhir_request('Patient', params)
        
        if data and 'entry' in data:
            logger.info(f"Retrieved {len(data['entry'])} patients")
            return data.get('entry', [])
        else:
            logger.warning("No patient data received, using sample data")
            return self._get_sample_patients()
    
    def get_service_requests(self, count: int = 100, page: int = 1) -> Optional[List[Dict]]:
        """
        Get list of service requests (referrals) from SATUSEHAT FHIR API
        Args:
            count: Number of requests to fetch per page
            page: Page number
        Returns:
            List of service request resources
        """
        if self.offline_mode:
            logger.info("Using offline sample data for service requests")
            return self._get_sample_service_requests()
        
        params = {
            '_count': count,
            '_page': page,
            'category': 'http://snomed.info/sct|3457005'  # Referral category
        }
        
        data = self._make_fhir_request('ServiceRequest', params)
        
        if data and 'entry' in data:
            logger.info(f"Retrieved {len(data['entry'])} service requests")
            return data.get('entry', [])
        else:
            logger.warning("No service request data received, using sample data")
            return self._get_sample_service_requests()
    
    def get_organizations(self) -> Optional[List[Dict]]:
        """Get list of organizations (hospitals) with offline fallback"""
        if self.offline_mode:
            logger.info("Using offline sample data for organizations")
            return self._get_sample_organizations()
        
        data = self._make_fhir_request('Organization', {'_count': 100})
        
        if data and 'entry' in data:
            logger.info(f"Retrieved {len(data['entry'])} organizations")
            return data.get('entry', [])
        else:
            logger.warning("No organization data received, using sample data")
            return self._get_sample_organizations()
    
    def get_location(self, location_id: str) -> Optional[Dict]:
        """Get location details with offline fallback"""
        if self.offline_mode:
            logger.info(f"Using offline sample data for location {location_id}")
            return self._get_sample_location(location_id)
            
        if not self.access_token:
            self.get_access_token()
        
        if self.offline_mode:
            return self._get_sample_location(location_id)
        
        try:
            url = f"{self.base_url}/fhir-r4/v1/Location/{location_id}"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.warning(f"Error getting location: {str(e)}, using sample data")
            self.offline_mode = True
            return self._get_sample_location(location_id)
    
    def _get_sample_organizations(self) -> List[Dict]:
        """
        Return sample organization data for offline mode
        """
        return [
            {
                'resource': {
                    'resourceType': 'Organization',
                    'id': 'sample-org-1',
                    'name': 'RSUP Dr. Cipto Mangunkusumo',
                    'type': [{
                        'coding': [{
                            'system': 'http://terminology.hl7.org/CodeSystem/organization-type',
                            'code': 'prov',
                            'display': 'Healthcare Provider'
                        }]
                    }],
                    'address': [{
                        'line': ['Jl. Diponegoro No.71'],
                        'city': 'Jakarta Pusat',
                        'postalCode': '10430',
                        'country': 'ID'
                    }]
                }
            },
            {
                'resource': {
                    'resourceType': 'Organization',
                    'id': 'sample-org-2',
                    'name': 'RS Fatmawati',
                    'type': [{
                        'coding': [{
                            'system': 'http://terminology.hl7.org/CodeSystem/organization-type',
                            'code': 'prov',
                            'display': 'Healthcare Provider'
                        }]
                    }],
                    'address': [{
                        'line': ['Jl. RS Fatmawati No.4'],
                        'city': 'Jakarta Selatan',
                        'postalCode': '12420',
                        'country': 'ID'
                    }]
                }
            },
            {
                'resource': {
                    'resourceType': 'Organization',
                    'id': 'sample-org-3',
                    'name': 'RSUP Persahabatan',
                    'type': [{
                        'coding': [{
                            'system': 'http://terminology.hl7.org/CodeSystem/organization-type',
                            'code': 'prov',
                            'display': 'Healthcare Provider'
                        }]
                    }],
                    'address': [{
                        'line': ['Jl. Persahabatan Raya No.1'],
                        'city': 'Jakarta Timur',
                        'postalCode': '13230',
                        'country': 'ID'
                    }]
                }
            }
        ]
    
    def _get_sample_location(self, location_id: str) -> Dict:
        """
        Return sample location data for offline mode
        """
        return {
            'resourceType': 'Location',
            'id': location_id,
            'status': 'active',
            'name': 'Sample Hospital Location',
            'address': {
                'line': ['Sample Address'],
                'city': 'Jakarta',
                'postalCode': '10000',
                'country': 'ID'
            },
            'position': {
                'longitude': 106.8456,
                'latitude': -6.2088
            }
        }
    
    def _get_sample_patients(self) -> List[Dict]:
        """
        Return sample patient data for offline mode
        """
        return [
            {
                'resource': {
                    'resourceType': 'Patient',
                    'id': 'sample-patient-1',
                    'identifier': [{
                        'system': 'https://fhir.kemkes.go.id/id/nik',
                        'value': '3174012345678901'
                    }],
                    'name': [{
                        'text': 'John Doe',
                        'given': ['John'],
                        'family': 'Doe'
                    }],
                    'gender': 'male',
                    'birthDate': '1985-05-15',
                    'address': [{
                        'line': ['Jl. Sample No. 123'],
                        'city': 'Jakarta',
                        'postalCode': '12345',
                        'country': 'ID'
                    }],
                    'telecom': [{
                        'system': 'phone',
                        'value': '081234567890'
                    }]
                }
            },
            {
                'resource': {
                    'resourceType': 'Patient',
                    'id': 'sample-patient-2',
                    'identifier': [{
                        'system': 'https://fhir.kemkes.go.id/id/nik',
                        'value': '3174012345678902'
                    }],
                    'name': [{
                        'text': 'Jane Smith',
                        'given': ['Jane'],
                        'family': 'Smith'
                    }],
                    'gender': 'female',
                    'birthDate': '1990-08-20',
                    'address': [{
                        'line': ['Jl. Sample No. 456'],
                        'city': 'Jakarta',
                        'postalCode': '12346',
                        'country': 'ID'
                    }],
                    'telecom': [{
                        'system': 'phone',
                        'value': '081234567891'
                    }]
                }
            }
        ]
    
    def _get_sample_service_requests(self) -> List[Dict]:
        """
        Return sample service request (referral) data for offline mode
        """
        return [
            {
                'resource': {
                    'resourceType': 'ServiceRequest',
                    'id': 'sample-referral-1',
                    'status': 'active',
                    'intent': 'order',
                    'category': [{
                        'coding': [{
                            'system': 'http://snomed.info/sct',
                            'code': '3457005',
                            'display': 'Referral'
                        }]
                    }],
                    'subject': {
                        'reference': 'Patient/sample-patient-1'
                    },
                    'reasonCode': [{
                        'text': 'Chest pain - requires cardiac evaluation'
                    }],
                    'authoredOn': '2024-01-15T10:00:00Z',
                    'requester': {
                        'reference': 'Organization/sample-org-1'
                    },
                    'performer': [{
                        'reference': 'Organization/sample-org-2'
                    }]
                }
            },
            {
                'resource': {
                    'resourceType': 'ServiceRequest',
                    'id': 'sample-referral-2',
                    'status': 'completed',
                    'intent': 'order',
                    'category': [{
                        'coding': [{
                            'system': 'http://snomed.info/sct',
                            'code': '3457005',
                            'display': 'Referral'
                        }]
                    }],
                    'subject': {
                        'reference': 'Patient/sample-patient-2'
                    },
                    'reasonCode': [{
                        'text': 'Diabetes management - requires specialist consultation'
                    }],
                    'authoredOn': '2024-01-14T14:30:00Z',
                    'requester': {
                        'reference': 'Organization/sample-org-1'
                    },
                    'performer': [{
                        'reference': 'Organization/sample-org-3'
                    }]
                }
            }
        ]
