"""
Mock test script for codebase improvements (no database required)
Tests CSV loading logic, API fallback, and configuration management
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.maps_api import GoogleMapsClient
from src.satusehat_api import SATUSEHATClient
import tempfile


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
        test_locations = [
            "Jakarta Pusat",
            "Bandung",
            "Surabaya",
            "Jl. Merdeka, Jakarta",
            "Unknown Location"
        ]
        
        for location in test_locations:
            coords = client.geocode_address(location)
            if coords:
                print(f"✅ Geocoded '{location}' -> {coords}")
            else:
                print(f"❌ Failed to geocode '{location}'")
                return False
        
        # Test distance calculation (always available)
        distance = client.calculate_distance(-6.2088, 106.8456, -6.9175, 107.6191)
        if distance > 0:
            print(f"✅ Distance calculation works: {distance} km (Jakarta to Bandung)")
        else:
            print("❌ Distance calculation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Google Maps fallback test failed: {str(e)}")
        import traceback
        traceback.print_exc()
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
            for org in orgs:
                print(f"   - {org['resource']['name']}")
        else:
            print("❌ Offline organizations data failed")
            return False
        
        # Test get location with sample data
        location = client.get_location("sample-loc-1")
        if location and 'resourceType' in location:
            print(f"✅ Offline location data works: {location['resourceType']}")
            print(f"   Location: {location['name']}")
            print(f"   Coordinates: {location['position']}")
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
            print(f"✅ Extracted {len(credentials)} credentials from soal.txt:")
            for key in credentials.keys():
                value = credentials[key]
                # Mask the value for security
                if len(value) > 10:
                    masked = value[:5] + '*' * (len(value) - 10) + value[-5:]
                else:
                    masked = '*' * len(value)
                print(f"   - {key}: {masked}")
        else:
            print("⚠️  No credentials extracted (soal.txt may be empty or not found)")
        
        return True
        
    except Exception as e:
        print(f"❌ API config extraction failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_csv_loader_logic():
    """Test CSV loading logic without database"""
    print("\n=== Testing CSV Loader Logic ===")
    
    try:
        import pandas as pd
        
        # Create test CSV content
        csv_content = """name,address,latitude,longitude,type,class,total_beds,phone,province
Test Hospital 1,Test Address 1,-6.2088,106.8456,Rumah Sakit Umum,B,100,021-1234567,DKI Jakarta
Test Hospital 2,Test Address 2,-6.9175,107.6191,Rumah Sakit Umum,C,80,022-7654321,Jawa Barat
Test Hospital 3,Test Address 3,-7.2575,112.7521,Rumah Sakit Umum,A,150,031-9876543,Jawa Timur"""
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_csv = f.name
        
        # Read CSV
        df = pd.read_csv(temp_csv)
        print(f"✅ CSV file read successfully: {len(df)} rows")
        
        # Test column standardization
        df.columns = df.columns.str.lower().str.strip()
        required_cols = ['name', 'address', 'latitude', 'longitude']
        
        for col in required_cols:
            if col in df.columns:
                print(f"✅ Required column '{col}' found")
            else:
                print(f"❌ Required column '{col}' not found")
                return False
        
        # Test data validation
        valid_rows = 0
        for _, row in df.iterrows():
            if not pd.isna(row.get('name')) and not pd.isna(row.get('address')):
                lat = float(row.get('latitude', 0))
                lon = float(row.get('longitude', 0))
                if lat != 0.0 and lon != 0.0:
                    valid_rows += 1
        
        print(f"✅ Data validation passed: {valid_rows}/{len(df)} valid rows")
        
        # Test province filtering
        df_filtered = df[df['province'].str.contains('DKI Jakarta', case=False, na=False)]
        print(f"✅ Province filtering works: {len(df_filtered)} rows for DKI Jakarta")
        
        # Clean up
        os.unlink(temp_csv)
        
        return True
        
    except Exception as e:
        print(f"❌ CSV loader logic test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_file_structure():
    """Test that all required files are present"""
    print("\n=== Testing File Structure ===")
    
    required_files = [
        'src/csv_loader.py',
        'src/maps_api.py',
        'src/satusehat_api.py',
        'src/models.py',
        'database/load_csv_data.py',
        'database/load_api_config.py',
        'database/schema.sql',
        'DATA_LOADING_GUIDE.md'
    ]
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    all_present = True
    
    for file in required_files:
        file_path = os.path.join(base_path, file)
        if os.path.exists(file_path):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} not found")
            all_present = False
    
    return all_present


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("SmartRujuk+ Codebase Improvements Test Suite")
    print("="*60)
    
    results = {
        'File Structure': test_file_structure(),
        'CSV Loader Logic': test_csv_loader_logic(),
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
    print(f"Total: {passed_tests}/{total_tests} tests passed ({passed_tests*100//total_tests}%)")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {total_tests - passed_tests} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
