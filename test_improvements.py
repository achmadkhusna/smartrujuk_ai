"""
Test script for codebase improvements
Tests CSV loading, API fallback, and configuration management
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import SessionLocal
from src.models import Hospital, APIConfig
from src.csv_loader import CSVDataLoader
from src.maps_api import GoogleMapsClient
from src.satusehat_api import SATUSEHATClient
import tempfile
import pandas as pd


def test_database_schema():
    """Test that APIConfig table exists"""
    print("\n=== Testing Database Schema ===")
    db = SessionLocal()
    try:
        # Query APIConfig table
        configs = db.query(APIConfig).all()
        print(f"✅ APIConfig table exists with {len(configs)} entries")
        return True
    except Exception as e:
        print(f"❌ Error accessing APIConfig table: {str(e)}")
        return False
    finally:
        db.close()


def test_csv_loader():
    """Test CSV data loading functionality"""
    print("\n=== Testing CSV Data Loader ===")
    db = SessionLocal()
    loader = CSVDataLoader(db)
    
    try:
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_content = """name,address,latitude,longitude,type,class,total_beds,phone,province
Test Hospital 1,Test Address 1,-6.2088,106.8456,Rumah Sakit Umum,B,100,021-1234567,DKI Jakarta
Test Hospital 2,Test Address 2,-6.9175,107.6191,Rumah Sakit Umum,C,80,022-7654321,Jawa Barat"""
            f.write(csv_content)
            temp_csv = f.name
        
        # Load CSV
        count = loader.load_bpjs_faskes_csv(temp_csv)
        print(f"✅ CSV loader successfully loaded {count} hospitals")
        
        # Verify data was loaded
        test_hospital = db.query(Hospital).filter(
            Hospital.name == "Test Hospital 1"
        ).first()
        
        if test_hospital:
            print(f"✅ Verified hospital in database: {test_hospital.name}")
            # Clean up test data
            db.query(Hospital).filter(Hospital.name.like("Test Hospital%")).delete()
            db.commit()
            print("✅ Test data cleaned up")
        else:
            print("❌ Could not verify loaded data")
            return False
        
        # Clean up temp file
        os.unlink(temp_csv)
        return True
        
    except Exception as e:
        print(f"❌ CSV loader test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_google_maps_offline_fallback():
    """Test Google Maps offline fallback"""
    print("\n=== Testing Google Maps Offline Fallback ===")
    
    # Create client without API key (should trigger offline mode)
    original_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    os.environ['GOOGLE_MAPS_API_KEY'] = ''
    
    try:
        client = GoogleMapsClient()
        
        if client.offline_mode:
            print("✅ Offline mode activated correctly")
        else:
            print("⚠️  Offline mode not activated (API key may be present)")
        
        # Test geocoding fallback
        coords = client.geocode_address("Jakarta Pusat")
        if coords:
            print(f"✅ Offline geocoding works: Jakarta Pusat -> {coords}")
        else:
            print("❌ Offline geocoding failed")
            return False
        
        # Test distance calculation (always available)
        distance = client.calculate_distance(-6.2088, 106.8456, -6.9175, 107.6191)
        if distance > 0:
            print(f"✅ Distance calculation works: {distance} km")
        else:
            print("❌ Distance calculation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Google Maps fallback test failed: {str(e)}")
        return False
    finally:
        # Restore original key
        if original_key:
            os.environ['GOOGLE_MAPS_API_KEY'] = original_key


def test_satusehat_offline_fallback():
    """Test SATUSEHAT API offline fallback"""
    print("\n=== Testing SATUSEHAT API Offline Fallback ===")
    
    # Create client without credentials (should trigger offline mode)
    original_org = os.environ.get('SATUSEHAT_ORG_ID')
    original_client = os.environ.get('SATUSEHAT_CLIENT_ID')
    original_secret = os.environ.get('SATUSEHAT_CLIENT_SECRET')
    
    os.environ['SATUSEHAT_ORG_ID'] = ''
    os.environ['SATUSEHAT_CLIENT_ID'] = ''
    os.environ['SATUSEHAT_CLIENT_SECRET'] = ''
    
    try:
        client = SATUSEHATClient()
        
        if client.offline_mode:
            print("✅ Offline mode activated correctly")
        else:
            print("⚠️  Offline mode not activated (credentials may be present)")
        
        # Test get organizations with sample data
        orgs = client.get_organizations()
        if orgs and len(orgs) > 0:
            print(f"✅ Offline organizations data works: {len(orgs)} sample organizations")
            print(f"   Sample: {orgs[0]['resource']['name']}")
        else:
            print("❌ Offline organizations data failed")
            return False
        
        # Test get location with sample data
        location = client.get_location("sample-loc-1")
        if location and 'resourceType' in location:
            print(f"✅ Offline location data works: {location['resourceType']}")
        else:
            print("❌ Offline location data failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ SATUSEHAT fallback test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore original values
        if original_org:
            os.environ['SATUSEHAT_ORG_ID'] = original_org
        if original_client:
            os.environ['SATUSEHAT_CLIENT_ID'] = original_client
        if original_secret:
            os.environ['SATUSEHAT_CLIENT_SECRET'] = original_secret


def test_api_config_extraction():
    """Test API configuration extraction from soal.txt"""
    print("\n=== Testing API Config Extraction ===")
    
    try:
        from database.load_api_config import extract_api_credentials_from_soal
        
        credentials = extract_api_credentials_from_soal()
        
        if credentials:
            print(f"✅ Extracted {len(credentials)} credentials from soal.txt")
            for key in credentials.keys():
                print(f"   - {key}: {'*' * 20}")
        else:
            print("⚠️  No credentials extracted (soal.txt may be empty or not found)")
        
        return True
        
    except Exception as e:
        print(f"❌ API config extraction failed: {str(e)}")
        return False


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("SmartRujuk+ Codebase Improvements Test Suite")
    print("="*60)
    
    results = {
        'Database Schema': test_database_schema(),
        'CSV Data Loader': test_csv_loader(),
        'Google Maps Offline Fallback': test_google_maps_offline_fallback(),
        'SATUSEHAT Offline Fallback': test_satusehat_offline_fallback(),
        'API Config Extraction': test_api_config_extraction()
    }
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print("\n" + "="*60)
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {total_tests - passed_tests} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
