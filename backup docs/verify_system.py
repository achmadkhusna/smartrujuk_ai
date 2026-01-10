#!/usr/bin/env python3
"""
SmartRujuk+ System Verification Script
Run this script to verify all components are working correctly
"""

import sys
import os

def print_header(text):
    print("\n" + "="*60)
    print(text)
    print("="*60)

def print_section(text):
    print(f"\n{text}")
    print("-" * len(text))

def test_environment():
    """Test environment setup"""
    print_section("1. Environment Setup")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'GOOGLE_MAPS_API_KEY']
        missing = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            print(f"❌ Missing environment variables: {', '.join(missing)}")
            return False
        else:
            print("✅ All required environment variables present")
            return True
    except Exception as e:
        print(f"❌ Environment setup failed: {e}")
        return False

def test_database():
    """Test database connection"""
    print_section("2. Database Connection")
    try:
        from src.database import engine, SessionLocal
        from src.models import Hospital, Patient
        
        # Test connection
        connection = engine.connect()
        connection.close()
        
        # Test queries
        db = SessionLocal()
        hospitals = db.query(Hospital).count()
        patients = db.query(Patient).count()
        db.close()
        
        print(f"✅ Database connected successfully")
        print(f"   - Hospitals: {hospitals}")
        print(f"   - Patients: {patients}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Make sure MySQL is running and database is initialized")
        print("   Run: python3 database/init_db.py")
        return False

def test_imports():
    """Test all module imports"""
    print_section("3. Module Imports")
    try:
        from src.database import SessionLocal
        from src.models import Hospital, Patient, Referral
        from src.agent import SmartReferralAgent
        from src.predictor import WaitTimePredictor, CapacityAnalyzer
        from src.maps_api import GoogleMapsClient
        from src.satusehat_api import SATUSEHATClient
        
        print("✅ All modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        print("   Run: pip install -r requirements.txt")
        return False

def test_ai_agent():
    """Test AI Agent functionality"""
    print_section("4. AI Agent")
    try:
        from src.database import SessionLocal
        from src.agent import SmartReferralAgent
        
        db = SessionLocal()
        agent = SmartReferralAgent(db)
        
        result = agent.recommend_hospital(
            patient_lat=-6.2088,
            patient_lon=106.8456,
            severity_level='high',
            max_distance=50.0
        )
        
        db.close()
        
        if result['success']:
            print(f"✅ AI Agent working")
            print(f"   - Recommended: {result.get('hospital_name', 'N/A')}")
            print(f"   - Distance: {result.get('distance_km', 'N/A')} km")
            return True
        else:
            print(f"❌ AI Agent failed: {result.get('error', 'Unknown')}")
            return False
    except Exception as e:
        print(f"❌ AI Agent test failed: {e}")
        return False

def test_predictors():
    """Test ML predictors"""
    print_section("5. ML Predictors")
    try:
        from src.database import SessionLocal
        from src.predictor import WaitTimePredictor, CapacityAnalyzer
        
        db = SessionLocal()
        
        # Test wait time predictor
        predictor = WaitTimePredictor()
        predictor.train(db)
        wait_time = predictor.predict_wait_time(hospital_id=1, severity_level='critical')
        
        # Test capacity analyzer
        analyzer = CapacityAnalyzer()
        capacity = analyzer.analyze_hospital_capacity(db, hospital_id=1)
        
        db.close()
        
        print("✅ Predictors working")
        print(f"   - Wait time prediction: {wait_time} minutes")
        print(f"   - Capacity status: {capacity['status']}")
        return True
    except Exception as e:
        print(f"❌ Predictors test failed: {e}")
        return False

def test_streamlit():
    """Test Streamlit app"""
    print_section("6. Streamlit Application")
    try:
        import py_compile
        py_compile.compile('app.py', doraise=True)
        print("✅ Streamlit app has no syntax errors")
        print("   Run with: streamlit run app.py")
        return True
    except Exception as e:
        print(f"❌ Streamlit app has errors: {e}")
        return False

def main():
    """Run all tests"""
    print_header("SmartRujuk+ System Verification")
    
    results = []
    
    # Run all tests
    results.append(("Environment", test_environment()))
    results.append(("Database", test_database()))
    results.append(("Imports", test_imports()))
    results.append(("AI Agent", test_ai_agent()))
    results.append(("Predictors", test_predictors()))
    results.append(("Streamlit", test_streamlit()))
    
    # Summary
    print_header("Verification Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:12} {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nTo start the application:")
        print("  streamlit run app.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
