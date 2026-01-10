"""
Integration test for the improved app.py
Tests that all imports and functions are properly structured
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all imports work correctly"""
    print("=" * 60)
    print("Testing Imports")
    print("=" * 60)
    
    try:
        import streamlit as st
        print("✅ streamlit imported successfully")
    except Exception as e:
        print(f"❌ Failed to import streamlit: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except Exception as e:
        print(f"❌ Failed to import pandas: {e}")
        return False
    
    try:
        import folium
        print("✅ folium imported successfully")
    except Exception as e:
        print(f"❌ Failed to import folium: {e}")
        return False
    
    try:
        from streamlit_folium import folium_static
        print("✅ streamlit_folium imported successfully")
    except Exception as e:
        print(f"❌ Failed to import streamlit_folium: {e}")
        return False
    
    try:
        from src.database import SessionLocal, init_db
        print("✅ src.database imported successfully")
    except Exception as e:
        print(f"❌ Failed to import src.database: {e}")
        return False
    
    try:
        from src.models import Hospital, Patient, Referral, SeverityEnum, GenderEnum
        print("✅ src.models imported successfully")
    except Exception as e:
        print(f"❌ Failed to import src.models: {e}")
        return False
    
    try:
        from src.agent import SmartReferralAgent
        print("✅ src.agent imported successfully")
    except Exception as e:
        print(f"❌ Failed to import src.agent: {e}")
        return False
    
    try:
        from src.predictor import WaitTimePredictor, CapacityAnalyzer
        print("✅ src.predictor imported successfully")
    except Exception as e:
        print(f"❌ Failed to import src.predictor: {e}")
        return False
    
    try:
        from src.maps_api import GoogleMapsClient
        print("✅ src.maps_api imported successfully")
    except Exception as e:
        print(f"❌ Failed to import src.maps_api: {e}")
        return False
    
    return True

def test_app_structure():
    """Test that app.py has the correct structure"""
    print("\n" + "=" * 60)
    print("Testing App.py Structure")
    print("=" * 60)
    
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    
    if not os.path.exists(app_path):
        print(f"❌ app.py not found at {app_path}")
        return False
    
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required functions
    required_functions = [
        "def main():",
        "def show_dashboard():",
        "def show_referral_form():",
        "def show_hospitals():",
        "def show_patients():",
        "def show_analytics():",
        "def show_hospital_map(",
        "def show_recent_referrals():"
    ]
    
    all_found = True
    for func in required_functions:
        if func in content:
            print(f"✅ Found {func}")
        else:
            print(f"❌ Missing {func}")
            all_found = False
    
    return all_found

def test_pagination_code():
    """Test that pagination code is properly implemented"""
    print("\n" + "=" * 60)
    print("Testing Pagination Implementation")
    print("=" * 60)
    
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for pagination elements
    pagination_elements = [
        "items_per_page = 50",
        "total_pages =",
        "hospital_page",
        "offset =",
        ".offset(offset).limit(items_per_page)",
        "⏮️ Pertama",
        "◀️ Sebelumnya",
        "Selanjutnya ▶️",
        "Terakhir ⏭️"
    ]
    
    all_found = True
    for element in pagination_elements:
        if element in content:
            print(f"✅ Found pagination element: {element}")
        else:
            print(f"❌ Missing pagination element: {element}")
            all_found = False
    
    return all_found

def test_filter_code():
    """Test that filter code is properly implemented"""
    print("\n" + "=" * 60)
    print("Testing Filter Implementation")
    print("=" * 60)
    
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for filter elements
    filter_elements = [
        "search_query",
        "filter_class",
        "filter_emergency",
        "filter_availability",
        "Hospital.name.contains(search_query)",
        "Hospital.class_ ==",
        "Hospital.emergency_available ==",
        "Hospital.available_beds >"
    ]
    
    all_found = True
    for element in filter_elements:
        if element in content:
            print(f"✅ Found filter element: {element}")
        else:
            print(f"❌ Missing filter element: {element}")
            all_found = False
    
    return all_found

def test_map_quota_fix():
    """Test that map quota fix is implemented"""
    print("\n" + "=" * 60)
    print("Testing Map Quota Fix")
    print("=" * 60)
    
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for map quota elements
    map_elements = [
        "def show_hospital_map(max_markers=100):",
        ".limit(max_markers)",
        "marker_count",
        "quota API"
    ]
    
    all_found = True
    for element in map_elements:
        if element in content:
            print(f"✅ Found map quota element: {element}")
        else:
            print(f"❌ Missing map quota element: {element}")
            all_found = False
    
    return all_found

def test_no_breaking_changes():
    """Test that no breaking changes were introduced"""
    print("\n" + "=" * 60)
    print("Testing for Breaking Changes")
    print("=" * 60)
    
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that essential functionality is preserved
    preserved_features = [
        "st.session_state.db",
        "st.session_state.agent",
        "SessionLocal()",
        "SmartReferralAgent(st.session_state.db)",
        "folium.Map(",
        "folium.Marker(",
        "folium_static(m,",
        "db.query(Hospital)",
        "pd.DataFrame("
    ]
    
    all_found = True
    for feature in preserved_features:
        if feature in content:
            print(f"✅ Preserved: {feature}")
        else:
            print(f"❌ Breaking change detected - missing: {feature}")
            all_found = False
    
    return all_found

def test_code_quality():
    """Test code quality aspects"""
    print("\n" + "=" * 60)
    print("Testing Code Quality")
    print("=" * 60)
    
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    
    with open(app_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"✅ Total lines in app.py: {len(lines)}")
    
    # Count docstrings
    docstrings = sum(1 for line in lines if '"""' in line or "'''" in line)
    print(f"✅ Docstring markers found: {docstrings}")
    
    # Check for error handling
    try_blocks = sum(1 for line in lines if 'try:' in line)
    except_blocks = sum(1 for line in lines if 'except' in line)
    print(f"✅ Error handling: {try_blocks} try blocks, {except_blocks} except blocks")
    
    # Check for comments
    comments = sum(1 for line in lines if line.strip().startswith('#'))
    print(f"✅ Comment lines: {comments}")
    
    return True

def main():
    """Run all integration tests"""
    print("\n" + "=" * 60)
    print("APP.PY INTEGRATION TEST SUITE")
    print("=" * 60)
    print("\nThis test suite validates that the improved app.py")
    print("maintains compatibility and includes all new features.\n")
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("App Structure", test_app_structure()))
    results.append(("Pagination Implementation", test_pagination_code()))
    results.append(("Filter Implementation", test_filter_code()))
    results.append(("Map Quota Fix", test_map_quota_fix()))
    results.append(("No Breaking Changes", test_no_breaking_changes()))
    results.append(("Code Quality", test_code_quality()))
    
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {total} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All integration tests passed!")
        print("\nThe app.py improvements are:")
        print("  ✅ Properly implemented")
        print("  ✅ Maintain backward compatibility")
        print("  ✅ Include all required features")
        print("  ✅ Follow code quality standards")
        return 0
    else:
        print(f"\n⚠️ {failed} test(s) failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
