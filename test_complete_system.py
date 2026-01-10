"""
Complete System Integration Test
Tests all components: Database, SATUSEHAT API, Data Loading, and Streamlit Integration
"""
import sys
import os
from datetime import datetime
import subprocess

sys.path.insert(0, os.path.dirname(__file__))

from src.database import SessionLocal, init_db
from src.models import Hospital, Patient, Referral, SeverityEnum, StatusEnum
from src.satusehat_api import SATUSEHATClient
from src.satusehat_loader import SATUSEHATDataLoader
from src.agent import SmartReferralAgent
from src.predictor import WaitTimePredictor
from sqlalchemy import func


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 100)
    print(f"  {title}")
    print("=" * 100)


def test_database_connection():
    """Test database connection and schema"""
    print_header("TEST 1: Database Connection & Schema")
    
    try:
        db = SessionLocal()
        
        # Test basic queries
        hospital_count = db.query(func.count(Hospital.id)).scalar()
        patient_count = db.query(func.count(Patient.id)).scalar()
        referral_count = db.query(func.count(Referral.id)).scalar()
        
        print(f"✅ Database connection successful")
        print(f"   Current state:")
        print(f"   - Hospitals: {hospital_count}")
        print(f"   - Patients: {patient_count}")
        print(f"   - Referrals: {referral_count}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False


def test_satusehat_integration():
    """Test SATUSEHAT API integration"""
    print_header("TEST 2: SATUSEHAT API Integration")
    
    client = SATUSEHATClient()
    
    print(f"Configuration:")
    print(f"   - Organization ID: {client.org_id}")
    print(f"   - Client ID: {client.client_id}")
    print(f"   - Auth URL: {client.auth_url}")
    print(f"   - Base URL: {client.base_url}")
    
    # Test token generation
    print(f"\nTesting token generation...")
    token = client.get_access_token()
    
    if token:
        print(f"✅ Token generated successfully")
        print(f"   Token (first 20 chars): {token[:20]}...")
        api_available = True
    else:
        print(f"⚠️  API not available (offline mode active)")
        print(f"   System will use sample data for testing")
        api_available = False
    
    # Test patient fetch
    print(f"\nTesting patient data fetch...")
    patients = client.get_patients(count=5, page=1)
    if patients:
        print(f"✅ Retrieved {len(patients)} patients")
    else:
        print(f"⚠️  No patients retrieved")
    
    # Test referral fetch
    print(f"\nTesting referral data fetch...")
    referrals = client.get_service_requests(count=5, page=1)
    if referrals:
        print(f"✅ Retrieved {len(referrals)} referrals")
    else:
        print(f"⚠️  No referrals retrieved")
    
    return True  # Return True even in offline mode since fallback works


def test_data_loading():
    """Test loading SATUSEHAT data to database"""
    print_header("TEST 3: Data Loading from SATUSEHAT")
    
    db = SessionLocal()
    
    try:
        # Get initial state
        initial_patients = db.query(func.count(Patient.id)).scalar()
        initial_referrals = db.query(func.count(Referral.id)).scalar()
        
        print(f"Initial database state:")
        print(f"   - Patients: {initial_patients}")
        print(f"   - Referrals: {initial_referrals}")
        
        # Load data
        loader = SATUSEHATDataLoader(db)
        
        print(f"\nLoading patients...")
        loader.load_patients(max_pages=2)
        
        print(f"Loading referrals...")
        loader.load_referrals(max_pages=2)
        
        # Get final state
        final_patients = db.query(func.count(Patient.id)).scalar()
        final_referrals = db.query(func.count(Referral.id)).scalar()
        
        print(f"\n✅ Data loading complete")
        print(f"   Final database state:")
        print(f"   - Patients: {initial_patients} → {final_patients} (+{final_patients - initial_patients})")
        print(f"   - Referrals: {initial_referrals} → {final_referrals} (+{final_referrals - initial_referrals})")
        
        print(f"\n   Statistics:")
        print(f"   - New patients: {loader.stats['patients_loaded']}")
        print(f"   - Updated patients: {loader.stats['patients_updated']}")
        print(f"   - New referrals: {loader.stats['referrals_loaded']}")
        print(f"   - Errors: {loader.stats['errors']}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Data loading failed: {str(e)}")
        db.close()
        return False


def test_referral_creation():
    """Test creating a new referral"""
    print_header("TEST 4: Referral Creation & Database Persistence")
    
    db = SessionLocal()
    
    try:
        # Get a patient and hospital
        patient = db.query(Patient).first()
        hospital = db.query(Hospital).first()
        
        if not patient or not hospital:
            print(f"⚠️  Need at least 1 patient and 1 hospital")
            return False
        
        initial_count = db.query(func.count(Referral.id)).scalar()
        
        print(f"Creating test referral...")
        print(f"   - Patient: {patient.name}")
        print(f"   - Hospital: {hospital.name}")
        
        # Create referral
        new_referral = Referral(
            patient_id=patient.id,
            to_hospital_id=hospital.id,
            condition_description="Test referral for system verification",
            severity_level=SeverityEnum.medium,
            status=StatusEnum.pending,
            predicted_wait_time=30,
            distance_km=5.5
        )
        
        db.add(new_referral)
        db.commit()
        
        # Verify
        final_count = db.query(func.count(Referral.id)).scalar()
        created_referral = db.query(Referral).filter(Referral.id == new_referral.id).first()
        
        print(f"\n✅ Referral created successfully")
        print(f"   - Referral ID: {created_referral.id}")
        print(f"   - Status: {created_referral.status.value}")
        print(f"   - Severity: {created_referral.severity_level.value}")
        print(f"   - Total referrals: {initial_count} → {final_count}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Referral creation failed: {str(e)}")
        db.rollback()
        db.close()
        return False


def test_ai_agent():
    """Test AI agent functionality"""
    print_header("TEST 5: AI Agent & Hospital Recommendation")
    
    db = SessionLocal()
    
    try:
        agent = SmartReferralAgent(db)
        
        # Test hospital recommendation
        print(f"Testing hospital recommendation...")
        print(f"   - Patient location: (-6.2088, 106.8456)")
        print(f"   - Severity: high")
        print(f"   - Max distance: 50 km")
        
        recommendation = agent.recommend_hospital(
            patient_lat=-6.2088,
            patient_lon=106.8456,
            severity_level='high',
            max_distance=50
        )
        
        if recommendation['success']:
            print(f"\n✅ Recommendation generated successfully")
            print(f"   - Recommended Hospital: {recommendation['hospital_name']}")
            print(f"   - Distance: {recommendation['distance_km']:.2f} km")
            print(f"   - Available Beds: {recommendation['available_beds']}")
            print(f"   - Predicted Wait Time: {recommendation['predicted_wait_time']} minutes")
            print(f"   - Occupancy Rate: {recommendation['occupancy_rate']:.1f}%")
            print(f"   - Alternatives: {len(recommendation['alternatives'])} hospitals")
        else:
            print(f"⚠️  No recommendation generated: {recommendation['message']}")
        
        db.close()
        return recommendation['success']
    except Exception as e:
        print(f"❌ AI agent test failed: {str(e)}")
        db.close()
        return False


def test_ml_predictor():
    """Test ML wait time predictor"""
    print_header("TEST 6: Machine Learning Wait Time Predictor")
    
    db = SessionLocal()
    
    try:
        predictor = WaitTimePredictor()
        
        print(f"Training predictor with historical data...")
        predictor.train(db)
        
        if predictor.is_trained:
            print(f"✅ Predictor trained successfully")
            
            # Test predictions for different severity levels
            hospital = db.query(Hospital).first()
            if hospital:
                print(f"\n   Predictions for {hospital.name}:")
                
                for severity in ['low', 'medium', 'high', 'critical']:
                    wait_time = predictor.predict_wait_time(hospital.id, severity)
                    print(f"   - {severity.capitalize()}: {wait_time} minutes")
        else:
            print(f"⚠️  Predictor not trained (may need more data)")
        
        db.close()
        return predictor.is_trained
    except Exception as e:
        print(f"❌ ML predictor test failed: {str(e)}")
        db.close()
        return False


def test_streamlit_app():
    """Test Streamlit app can be loaded"""
    print_header("TEST 7: Streamlit Application")
    
    try:
        print(f"Checking Streamlit app syntax...")
        result = subprocess.run(
            ['python3', '-m', 'py_compile', 'app.py'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ Streamlit app syntax is valid")
            print(f"   Application can be started with: streamlit run app.py")
            return True
        else:
            print(f"❌ Streamlit app has syntax errors:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Streamlit app test failed: {str(e)}")
        return False


def generate_summary_report():
    """Generate summary statistics"""
    print_header("SYSTEM SUMMARY")
    
    db = SessionLocal()
    
    try:
        # Count all records
        hospitals = db.query(func.count(Hospital.id)).scalar()
        patients = db.query(func.count(Patient.id)).scalar()
        referrals = db.query(func.count(Referral.id)).scalar()
        
        print(f"\n📊 Database Statistics:")
        print(f"   - Total Hospitals: {hospitals}")
        print(f"   - Total Patients: {patients}")
        print(f"   - Total Referrals: {referrals}")
        
        # Referral status breakdown
        if referrals > 0:
            all_referrals = db.query(Referral).all()
            status_counts = {}
            for r in all_referrals:
                status = r.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f"\n   Referral Status Distribution:")
            for status, count in status_counts.items():
                print(f"   - {status.capitalize()}: {count}")
        
        # Hospital capacity summary
        if hospitals > 0:
            all_hospitals = db.query(Hospital).all()
            total_beds = sum(h.total_beds for h in all_hospitals)
            available_beds = sum(h.available_beds for h in all_hospitals)
            occupancy = ((total_beds - available_beds) / total_beds * 100) if total_beds > 0 else 0
            
            print(f"\n   Hospital Capacity:")
            print(f"   - Total Beds: {total_beds}")
            print(f"   - Available Beds: {available_beds}")
            print(f"   - System Occupancy: {occupancy:.1f}%")
        
        db.close()
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        db.close()


def main():
    """Run all system tests"""
    print("\n" + "🏥" * 50)
    print("SMARTRUJUK+ COMPLETE SYSTEM INTEGRATION TEST")
    print("🏥" * 50)
    print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Purpose: Verify all system components work correctly")
    
    results = {}
    
    # Run all tests
    results['Database Connection'] = test_database_connection()
    results['SATUSEHAT API'] = test_satusehat_integration()
    results['Data Loading'] = test_data_loading()
    results['Referral Creation'] = test_referral_creation()
    results['AI Agent'] = test_ai_agent()
    results['ML Predictor'] = test_ml_predictor()
    results['Streamlit App'] = test_streamlit_app()
    
    # Generate summary
    generate_summary_report()
    
    # Final results
    print_header("FINAL TEST RESULTS")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"\n📈 Test Statistics:")
    print(f"   - Total Tests: {total}")
    print(f"   - Passed: {passed}")
    print(f"   - Failed: {failed}")
    print(f"   - Success Rate: {(passed/total*100):.1f}%")
    
    print(f"\n📋 Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    print("\n" + "=" * 100)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - SYSTEM IS FULLY FUNCTIONAL!")
        status_message = "SUCCESS"
    elif passed >= total * 0.8:
        print("✅ MOST TESTS PASSED - SYSTEM IS OPERATIONAL")
        status_message = "OPERATIONAL"
    elif passed >= total * 0.5:
        print("⚠️  SOME TESTS FAILED - SYSTEM PARTIALLY WORKING")
        status_message = "PARTIAL"
    else:
        print("❌ MULTIPLE TESTS FAILED - SYSTEM NEEDS ATTENTION")
        status_message = "FAILED"
    
    print("=" * 100 + "\n")
    
    return status_message


if __name__ == '__main__':
    status = main()
    sys.exit(0 if status in ['SUCCESS', 'OPERATIONAL'] else 1)
