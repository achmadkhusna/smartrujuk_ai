"""
Comprehensive SATUSEHAT API Integration Test
Tests token generation, data loading, and database integration
"""
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.satusehat_api import SATUSEHATClient
from src.satusehat_loader import SATUSEHATDataLoader
from src.database import SessionLocal
from src.models import Patient, Referral, Hospital
from sqlalchemy import func


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_token_generation():
    """Test SATUSEHAT OAuth2 token generation"""
    print_section("TEST 1: SATUSEHAT Token Generation")
    
    client = SATUSEHATClient()
    
    print(f"Organization ID: {client.org_id}")
    print(f"Client ID: {client.client_id}")
    print(f"Auth URL: {client.auth_url}")
    print(f"Base URL: {client.base_url}")
    
    print("\nAttempting to generate access token...")
    token = client.get_access_token()
    
    if token:
        print(f"✅ Token generated successfully")
        print(f"   Token: {token[:20]}...")
        print(f"   Expires at: {client.token_expires_at}")
        return True
    else:
        print(f"⚠️  Token generation failed - using offline mode")
        print(f"   Offline mode: {client.offline_mode}")
        return False


def test_patient_fetch():
    """Test fetching patient data from API"""
    print_section("TEST 2: Fetch Patient Data")
    
    client = SATUSEHATClient()
    
    print("Fetching patients from SATUSEHAT API...")
    patients = client.get_patients(count=10, page=1)
    
    if patients:
        print(f"✅ Retrieved {len(patients)} patients")
        
        # Show sample patient
        if len(patients) > 0:
            sample = patients[0].get('resource', patients[0])
            print(f"\nSample Patient:")
            print(f"  ID: {sample.get('id')}")
            
            names = sample.get('name', [])
            if names:
                name_text = names[0].get('text', 'N/A')
                print(f"  Name: {name_text}")
            
            print(f"  Gender: {sample.get('gender', 'N/A')}")
            print(f"  Birth Date: {sample.get('birthDate', 'N/A')}")
        
        return True
    else:
        print("⚠️  No patients retrieved (using sample data)")
        return False


def test_referral_fetch():
    """Test fetching referral data from API"""
    print_section("TEST 3: Fetch Referral Data")
    
    client = SATUSEHATClient()
    
    print("Fetching service requests (referrals) from SATUSEHAT API...")
    referrals = client.get_service_requests(count=10, page=1)
    
    if referrals:
        print(f"✅ Retrieved {len(referrals)} referrals")
        
        # Show sample referral
        if len(referrals) > 0:
            sample = referrals[0].get('resource', referrals[0])
            print(f"\nSample Referral:")
            print(f"  ID: {sample.get('id')}")
            print(f"  Status: {sample.get('status', 'N/A')}")
            print(f"  Intent: {sample.get('intent', 'N/A')}")
            
            reason_codes = sample.get('reasonCode', [])
            if reason_codes:
                print(f"  Reason: {reason_codes[0].get('text', 'N/A')}")
        
        return True
    else:
        print("⚠️  No referrals retrieved (using sample data)")
        return False


def test_data_loading():
    """Test loading data from API to database"""
    print_section("TEST 4: Load Data to Database")
    
    db = SessionLocal()
    
    try:
        # Get initial counts
        initial_patients = db.query(func.count(Patient.id)).scalar()
        initial_referrals = db.query(func.count(Referral.id)).scalar()
        
        print(f"Initial state:")
        print(f"  Patients: {initial_patients}")
        print(f"  Referrals: {initial_referrals}")
        
        # Create data loader
        loader = SATUSEHATDataLoader(db)
        
        print("\nLoading patients from SATUSEHAT API...")
        patients_loaded = loader.load_patients(max_pages=2)
        
        print(f"\nLoading referrals from SATUSEHAT API...")
        referrals_loaded = loader.load_referrals(max_pages=2)
        
        # Get final counts
        final_patients = db.query(func.count(Patient.id)).scalar()
        final_referrals = db.query(func.count(Referral.id)).scalar()
        
        print(f"\n✅ Data loading complete:")
        print(f"  Patients: {initial_patients} → {final_patients} (+{final_patients - initial_patients})")
        print(f"  Referrals: {initial_referrals} → {final_referrals} (+{final_referrals - initial_referrals})")
        
        print(f"\n📊 Loading statistics:")
        print(f"  New patients: {loader.stats['patients_loaded']}")
        print(f"  Updated patients: {loader.stats['patients_updated']}")
        print(f"  New referrals: {loader.stats['referrals_loaded']}")
        print(f"  Errors: {loader.stats['errors']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during data loading: {str(e)}")
        return False
    finally:
        db.close()


def test_database_state():
    """Check final database state"""
    print_section("TEST 5: Verify Database State")
    
    db = SessionLocal()
    
    try:
        # Count records
        hospital_count = db.query(func.count(Hospital.id)).scalar()
        patient_count = db.query(func.count(Patient.id)).scalar()
        referral_count = db.query(func.count(Referral.id)).scalar()
        
        print("📊 Final Database State:")
        print(f"  Hospitals: {hospital_count}")
        print(f"  Patients: {patient_count}")
        print(f"  Referrals: {referral_count}")
        
        # Show sample records
        if patient_count > 0:
            print("\n👤 Sample Patients:")
            patients = db.query(Patient).limit(3).all()
            for p in patients:
                print(f"  - {p.name} ({p.gender.value}, BPJS: {p.bpjs_number})")
        
        if referral_count > 0:
            print("\n🚑 Sample Referrals:")
            referrals = db.query(Referral).limit(3).all()
            for r in referrals:
                patient = db.query(Patient).filter(Patient.id == r.patient_id).first()
                hospital = db.query(Hospital).filter(Hospital.id == r.to_hospital_id).first()
                print(f"  - Patient: {patient.name if patient else 'Unknown'}")
                print(f"    → Hospital: {hospital.name if hospital else 'Unknown'}")
                print(f"    Severity: {r.severity_level.value}, Status: {r.status.value}")
        
        success = (hospital_count > 0 and patient_count > 0)
        if success:
            print("\n✅ Database is properly populated")
        else:
            print("\n⚠️  Database may need more data")
        
        return success
        
    except Exception as e:
        print(f"❌ Error checking database: {str(e)}")
        return False
    finally:
        db.close()


def main():
    """Run all tests"""
    print("\n" + "🏥" * 40)
    print("SMARTRUJUK+ SATUSEHAT INTEGRATION - COMPREHENSIVE TEST")
    print("🏥" * 40)
    print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        'Token Generation': test_token_generation(),
        'Patient Fetch': test_patient_fetch(),
        'Referral Fetch': test_referral_fetch(),
        'Data Loading': test_data_loading(),
        'Database State': test_database_state()
    }
    
    # Summary
    print_section("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "⚠️  WARN"
        print(f"  {status} - {test_name}")
    
    print("\n" + "=" * 80)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    elif passed >= total * 0.6:
        print("⚠️  SOME TESTS PASSED (Offline mode or limited API access)")
    else:
        print("❌ MULTIPLE TESTS FAILED")
    
    print("=" * 80 + "\n")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
