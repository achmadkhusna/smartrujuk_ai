"""
SATUSEHAT Data Loader
Loads patient and referral data from SATUSEHAT API into local MySQL database
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.satusehat_api import SATUSEHATClient
from src.models import Patient, Referral, Hospital, GenderEnum, SeverityEnum, StatusEnum
from src.database import SessionLocal, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SATUSEHATDataLoader:
    def __init__(self, db: Session = None):
        """
        Initialize SATUSEHAT data loader
        Args:
            db: Database session (optional, will create new if not provided)
        """
        self.db = db or SessionLocal()
        self.client = SATUSEHATClient()
        self.stats = {
            'patients_loaded': 0,
            'patients_updated': 0,
            'referrals_loaded': 0,
            'referrals_updated': 0,
            'errors': 0
        }
    
    def _parse_fhir_date(self, date_str: str) -> Optional[datetime]:
        """Parse FHIR date string to datetime"""
        if not date_str:
            return None
        try:
            # Handle different date formats
            if 'T' in date_str:
                # ISO datetime format
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                # Date only format
                return datetime.strptime(date_str, '%Y-%m-%d')
        except Exception as e:
            logger.warning(f"Error parsing date {date_str}: {str(e)}")
            return None
    
    def _map_fhir_gender(self, fhir_gender: str) -> Optional[GenderEnum]:
        """Map FHIR gender to local enum"""
        gender_map = {
            'male': GenderEnum.M,
            'female': GenderEnum.F,
            'M': GenderEnum.M,
            'F': GenderEnum.F
        }
        return gender_map.get(fhir_gender)
    
    def _extract_patient_data(self, fhir_patient: Dict) -> Optional[Dict]:
        """
        Extract patient data from FHIR resource
        Args:
            fhir_patient: FHIR Patient resource
        Returns:
            Dictionary with patient data or None if invalid
        """
        try:
            resource = fhir_patient.get('resource', fhir_patient)
            
            # Extract identifiers
            identifiers = resource.get('identifier', [])
            bpjs_number = None
            for identifier in identifiers:
                system = identifier.get('system', '')
                if 'nik' in system.lower() or 'bpjs' in system.lower():
                    bpjs_number = identifier.get('value')
                    break
            
            # Use patient ID if no BPJS number found
            if not bpjs_number:
                bpjs_number = f"FHIR-{resource.get('id', 'unknown')}"
            
            # Extract name
            names = resource.get('name', [])
            name = 'Unknown'
            if names:
                name_obj = names[0]
                if 'text' in name_obj:
                    name = name_obj['text']
                else:
                    given = ' '.join(name_obj.get('given', []))
                    family = name_obj.get('family', '')
                    name = f"{given} {family}".strip()
            
            # Extract gender
            gender = self._map_fhir_gender(resource.get('gender', 'male'))
            if not gender:
                gender = GenderEnum.M  # Default
            
            # Extract birth date
            birth_date = self._parse_fhir_date(resource.get('birthDate'))
            
            # Extract address
            addresses = resource.get('address', [])
            address = None
            if addresses:
                addr_obj = addresses[0]
                lines = addr_obj.get('line', [])
                city = addr_obj.get('city', '')
                postal = addr_obj.get('postalCode', '')
                address = ', '.join([*lines, city, postal])
            
            # Extract phone
            telecoms = resource.get('telecom', [])
            phone = None
            for telecom in telecoms:
                if telecom.get('system') == 'phone':
                    phone = telecom.get('value')
                    break
            
            return {
                'bpjs_number': bpjs_number,
                'name': name,
                'date_of_birth': birth_date,
                'gender': gender,
                'address': address,
                'phone': phone
            }
            
        except Exception as e:
            logger.error(f"Error extracting patient data: {str(e)}")
            return None
    
    def _extract_referral_data(self, fhir_service_request: Dict) -> Optional[Dict]:
        """
        Extract referral data from FHIR ServiceRequest resource
        Args:
            fhir_service_request: FHIR ServiceRequest resource
        Returns:
            Dictionary with referral data or None if invalid
        """
        try:
            resource = fhir_service_request.get('resource', fhir_service_request)
            
            # Extract patient reference
            subject = resource.get('subject', {})
            patient_ref = subject.get('reference', '')
            patient_id = patient_ref.split('/')[-1] if '/' in patient_ref else patient_ref
            
            # Extract requester (from hospital)
            requester = resource.get('requester', {})
            from_org_ref = requester.get('reference', '')
            
            # Extract performer (to hospital)
            performers = resource.get('performer', [])
            to_org_ref = ''
            if performers:
                to_org_ref = performers[0].get('reference', '')
            
            # Extract condition description
            reason_codes = resource.get('reasonCode', [])
            condition = 'Medical referral'
            if reason_codes:
                condition = reason_codes[0].get('text', condition)
            
            # Map FHIR status to local status
            fhir_status = resource.get('status', 'active')
            status_map = {
                'active': StatusEnum.pending,
                'completed': StatusEnum.completed,
                'revoked': StatusEnum.rejected,
                'entered-in-error': StatusEnum.rejected
            }
            status = status_map.get(fhir_status, StatusEnum.pending)
            
            # Determine severity from priority or condition text
            priority = resource.get('priority', 'routine')
            severity_map = {
                'routine': SeverityEnum.low,
                'urgent': SeverityEnum.high,
                'asap': SeverityEnum.critical,
                'stat': SeverityEnum.critical
            }
            severity = severity_map.get(priority, SeverityEnum.medium)
            
            # Extract dates
            referral_date = self._parse_fhir_date(resource.get('authoredOn'))
            
            return {
                'patient_fhir_id': patient_id,
                'condition_description': condition,
                'severity_level': severity,
                'status': status,
                'referral_date': referral_date or datetime.now(),
                'from_org_ref': from_org_ref,
                'to_org_ref': to_org_ref
            }
            
        except Exception as e:
            logger.error(f"Error extracting referral data: {str(e)}")
            return None
    
    def load_patients(self, max_pages: int = 5) -> int:
        """
        Load patients from SATUSEHAT API into database
        Args:
            max_pages: Maximum number of pages to fetch
        Returns:
            Number of patients loaded
        """
        logger.info("Starting patient data load from SATUSEHAT API")
        
        for page in range(1, max_pages + 1):
            try:
                # Fetch patients from API
                fhir_patients = self.client.get_patients(count=100, page=page)
                
                if not fhir_patients:
                    logger.info(f"No more patients found at page {page}")
                    break
                
                logger.info(f"Processing page {page} with {len(fhir_patients)} patients")
                
                for fhir_patient in fhir_patients:
                    try:
                        patient_data = self._extract_patient_data(fhir_patient)
                        
                        if not patient_data:
                            continue
                        
                        # Check if patient already exists
                        existing_patient = self.db.query(Patient).filter(
                            Patient.bpjs_number == patient_data['bpjs_number']
                        ).first()
                        
                        if existing_patient:
                            # Update existing patient
                            for key, value in patient_data.items():
                                if value is not None:
                                    setattr(existing_patient, key, value)
                            self.stats['patients_updated'] += 1
                            logger.debug(f"Updated patient: {patient_data['name']}")
                        else:
                            # Create new patient
                            new_patient = Patient(**patient_data)
                            self.db.add(new_patient)
                            self.stats['patients_loaded'] += 1
                            logger.debug(f"Added new patient: {patient_data['name']}")
                        
                        self.db.commit()
                        
                    except Exception as e:
                        logger.error(f"Error processing patient: {str(e)}")
                        self.stats['errors'] += 1
                        self.db.rollback()
                        continue
                
            except Exception as e:
                logger.error(f"Error loading patients page {page}: {str(e)}")
                self.stats['errors'] += 1
                break
        
        logger.info(f"Patient load complete. Loaded: {self.stats['patients_loaded']}, Updated: {self.stats['patients_updated']}")
        return self.stats['patients_loaded'] + self.stats['patients_updated']
    
    def load_referrals(self, max_pages: int = 5) -> int:
        """
        Load referrals from SATUSEHAT API into database
        Args:
            max_pages: Maximum number of pages to fetch
        Returns:
            Number of referrals loaded
        """
        logger.info("Starting referral data load from SATUSEHAT API")
        
        # Get a default hospital for referrals without clear hospital mapping
        default_hospital = self.db.query(Hospital).first()
        if not default_hospital:
            logger.warning("No hospitals in database. Please load hospital data first.")
            return 0
        
        for page in range(1, max_pages + 1):
            try:
                # Fetch service requests from API
                fhir_requests = self.client.get_service_requests(count=100, page=page)
                
                if not fhir_requests:
                    logger.info(f"No more referrals found at page {page}")
                    break
                
                logger.info(f"Processing page {page} with {len(fhir_requests)} referrals")
                
                for fhir_request in fhir_requests:
                    try:
                        referral_data = self._extract_referral_data(fhir_request)
                        
                        if not referral_data:
                            continue
                        
                        # Find patient by FHIR ID or BPJS number
                        patient_fhir_id = referral_data.pop('patient_fhir_id')
                        patient = self.db.query(Patient).filter(
                            Patient.bpjs_number.like(f"%{patient_fhir_id}%")
                        ).first()
                        
                        if not patient:
                            # Use first patient as fallback
                            patient = self.db.query(Patient).first()
                            if not patient:
                                logger.warning("No patients in database, skipping referral")
                                continue
                        
                        referral_data['patient_id'] = patient.id
                        referral_data.pop('from_org_ref', None)
                        referral_data.pop('to_org_ref', None)
                        
                        # Assign hospitals (use default for now)
                        referral_data['to_hospital_id'] = default_hospital.id
                        
                        # Create new referral
                        new_referral = Referral(**referral_data)
                        self.db.add(new_referral)
                        self.stats['referrals_loaded'] += 1
                        logger.debug(f"Added new referral for patient: {patient.name}")
                        
                        self.db.commit()
                        
                    except Exception as e:
                        logger.error(f"Error processing referral: {str(e)}")
                        self.stats['errors'] += 1
                        self.db.rollback()
                        continue
                
            except Exception as e:
                logger.error(f"Error loading referrals page {page}: {str(e)}")
                self.stats['errors'] += 1
                break
        
        logger.info(f"Referral load complete. Loaded: {self.stats['referrals_loaded']}")
        return self.stats['referrals_loaded']
    
    def load_all_data(self, max_pages: int = 5) -> Dict[str, int]:
        """
        Load all data from SATUSEHAT API
        Args:
            max_pages: Maximum number of pages to fetch per resource type
        Returns:
            Dictionary with loading statistics
        """
        logger.info("=" * 80)
        logger.info("Starting complete SATUSEHAT data load")
        logger.info("=" * 80)
        
        # Load patients first
        self.load_patients(max_pages=max_pages)
        
        # Load referrals
        self.load_referrals(max_pages=max_pages)
        
        # Get final counts from database
        total_patients = self.db.query(func.count(Patient.id)).scalar()
        total_referrals = self.db.query(func.count(Referral.id)).scalar()
        
        logger.info("=" * 80)
        logger.info("Data load summary:")
        logger.info(f"  Patients in DB: {total_patients}")
        logger.info(f"  Referrals in DB: {total_referrals}")
        logger.info(f"  New patients: {self.stats['patients_loaded']}")
        logger.info(f"  Updated patients: {self.stats['patients_updated']}")
        logger.info(f"  New referrals: {self.stats['referrals_loaded']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        logger.info("=" * 80)
        
        return {
            'total_patients': total_patients,
            'total_referrals': total_referrals,
            'new_patients': self.stats['patients_loaded'],
            'updated_patients': self.stats['patients_updated'],
            'new_referrals': self.stats['referrals_loaded'],
            'errors': self.stats['errors']
        }
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()


def main():
    """Main function for testing"""
    # Initialize database
    init_db()
    
    # Create loader
    loader = SATUSEHATDataLoader()
    
    try:
        # Load all data
        stats = loader.load_all_data(max_pages=3)
        
        print("\n" + "=" * 80)
        print("SATUSEHAT DATA LOAD COMPLETE")
        print("=" * 80)
        print(f"Total Patients: {stats['total_patients']}")
        print(f"Total Referrals: {stats['total_referrals']}")
        print(f"New Patients: {stats['new_patients']}")
        print(f"Updated Patients: {stats['updated_patients']}")
        print(f"New Referrals: {stats['new_referrals']}")
        print(f"Errors: {stats['errors']}")
        print("=" * 80)
        
    finally:
        loader.close()


if __name__ == '__main__':
    main()
