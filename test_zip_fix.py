#!/usr/bin/env python3
"""
Verification Test: ZIP File Multi-CSV Support Fix

This test verifies that the fix for handling ZIP files with multiple CSVs
works correctly. It simulates the exact error scenario from the training log.

Error was: "Multiple files found in ZIP file. Only one file per ZIP"
Fix: CSV loader now extracts and processes each CSV file from ZIP individually
"""
import sys
import os
import tempfile
import pandas as pd
import zipfile
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.csv_loader import CSVDataLoader


def create_kaggle_dataset_zip():
    """
    Create a ZIP file matching the actual Kaggle dataset structure
    that was causing the error: "Dataset Rasio Bed to Population Faskes II.zip"
    """
    test_dir = tempfile.mkdtemp()
    
    # File 1: Bed ratio data (main dataset)
    df1 = pd.DataFrame({
        'Provinsi': ['DKI Jakarta', 'Jawa Barat', 'Jawa Timur', 'Bali'],
        'Kelas': ['C', 'D', 'C', 'D'],
        'Jumlah_Bed': [100, 50, 120, 80],
        'Populasi': [10000000, 45000000, 38000000, 4000000],
        'Rasio': [0.001, 0.0011, 0.0032, 0.002]
    })
    csv1_path = os.path.join(test_dir, 'Rasio Bed To Population Rumah Sakit Kelas C dan D tiap Provinsi Di Indonesia.csv')
    df1.to_csv(csv1_path, index=False)
    
    # File 2: Hospital data (contains actual facility information)
    df2 = pd.DataFrame({
        'NamaFaskes': [
            'RSUD Jakarta Pusat', 
            'RSUD Bandung', 
            'RSUD Surabaya',
            'Puskesmas Jakarta Selatan',
            'RSUD Denpasar'
        ],
        'AlamatFaskes': [
            'Jl. Jakarta No. 1',
            'Jl. Bandung No. 2', 
            'Jl. Surabaya No. 3',
            'Jl. Jakarta Selatan No. 4',
            'Jl. Denpasar No. 5'
        ],
        'LatLongFaskes': [
            'http://maps.google.co.id/?q=-6.1744,106.8294',
            'http://maps.google.co.id/?q=-6.9175,107.6191',
            'http://maps.google.co.id/?q=-7.2687,112.7521',
            'http://maps.google.co.id/?q=-6.2088,106.8456',
            'http://maps.google.co.id/?q=-8.6705,115.2126'
        ],
        'TipeFaskes': ['Rumah Sakit', 'Rumah Sakit', 'Rumah Sakit', 'Puskesmas', 'Rumah Sakit'],
        'Provinsi': ['DKI Jakarta', 'Jawa Barat', 'Jawa Timur', 'DKI Jakarta', 'Bali']
    })
    csv2_path = os.path.join(test_dir, 'data_rs.csv')
    df2.to_csv(csv2_path, index=False)
    
    # File 3: Population projection data (not hospital data)
    df3 = pd.DataFrame({
        'Provinsi': ['DKI Jakarta', 'Jawa Barat', 'Jawa Timur', 'Bali'],
        'Tahun': [2024, 2024, 2024, 2024],
        'Laki_Laki': [5000000, 22500000, 19000000, 2000000],
        'Perempuan': [5000000, 22500000, 19000000, 2000000],
        'Total': [10000000, 45000000, 38000000, 4000000]
    })
    csv3_path = os.path.join(test_dir, 'Jumlah Penduduk Hasil Proyeksi Menurut Provinsi dan Jenis Kelamin.csv')
    df3.to_csv(csv3_path, index=False)
    
    # Create ZIP with all three files (matching Kaggle dataset structure)
    zip_path = os.path.join(test_dir, 'Dataset Rasio Bed to Population Faskes II.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(csv1_path, os.path.basename(csv1_path))
        zipf.write(csv2_path, os.path.basename(csv2_path))
        zipf.write(csv3_path, os.path.basename(csv3_path))
    
    return test_dir, zip_path


def test_fix():
    """
    Main test function that verifies the fix works
    """
    print("="*70)
    print("SmartRujuk+ ZIP Multi-CSV Fix Verification")
    print("="*70)
    print("\n📦 Creating test ZIP file (simulating Kaggle dataset)...")
    
    test_dir, zip_path = create_kaggle_dataset_zip()
    
    try:
        # Verify ZIP contents
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            files = zipf.namelist()
            print(f"\n✅ Created ZIP with {len(files)} files:")
            for f in files:
                print(f"   - {f}")
        
        print("\n" + "="*70)
        print("Testing CSV Loader with Multi-File ZIP")
        print("="*70)
        
        # Create mock database
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None
        
        # Track added hospitals
        added_hospitals = []
        def track_add(hospital):
            added_hospitals.append(hospital)
        mock_db.add = track_add
        
        # Create loader
        loader = CSVDataLoader(mock_db)
        
        # Load the ZIP file - THIS IS THE KEY TEST
        print("\n🔄 Loading ZIP file...")
        print("   (Previously this would fail with 'Multiple files found in ZIP file')")
        print()
        
        count = loader.load_bpjs_faskes_csv(zip_path)
        
        print("\n" + "="*70)
        print("Results")
        print("="*70)
        
        print(f"\n✅ SUCCESS: Loaded {count} hospitals from ZIP file!")
        print(f"   Total hospitals added: {len(added_hospitals)}")
        
        if count > 0:
            print("\n📊 Loaded Hospitals:")
            for i, hospital in enumerate(added_hospitals, 1):
                print(f"\n   {i}. {hospital.name}")
                print(f"      📍 Location: ({hospital.latitude}, {hospital.longitude})")
                print(f"      🏥 Type: {hospital.type}")
                print(f"      🛏️  Beds: {hospital.total_beds}")
        
        # Get statistics
        stats = loader.get_stats()
        print(f"\n📈 Loading Statistics:")
        print(f"   Total Processed: {stats['total_processed']}")
        print(f"   Total Inserted: {stats['total_inserted']}")
        print(f"   Total Skipped: {stats['total_skipped']}")
        print(f"   Errors: {len(stats['errors'])}")
        
        # Verify the fix
        print("\n" + "="*70)
        print("Verification")
        print("="*70)
        
        checks = [
            (count > 0, "✅ Hospitals were loaded from ZIP"),
            (len(added_hospitals) == count, "✅ Hospital count matches"),
            (stats['total_inserted'] == count, "✅ Statistics match"),
            (all(h.latitude != 0.0 for h in added_hospitals), "✅ All hospitals have valid coordinates"),
            (all(h.total_beds > 0 for h in added_hospitals), "✅ All hospitals have valid bed counts"),
        ]
        
        all_passed = True
        for check, message in checks:
            if check:
                print(f"   {message}")
            else:
                print(f"   ❌ FAILED: {message}")
                all_passed = False
        
        if all_passed:
            print("\n" + "="*70)
            print("🎉 ALL TESTS PASSED!")
            print("="*70)
            print("\n✅ The fix successfully handles ZIP files with multiple CSVs")
            print("✅ Original error 'Multiple files found in ZIP file' is now fixed")
            print("✅ System can now load 'Dataset Rasio Bed to Population Faskes II.zip'")
            print("✅ Training pipeline will work smoothly")
            return True
        else:
            print("\n❌ Some verification checks failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


if __name__ == '__main__':
    print("\n" + "="*70)
    print("Test Purpose: Verify ZIP Multi-CSV Support Fix")
    print("="*70)
    print("\nOriginal Issue:")
    print("  ERROR: Multiple files found in ZIP file. Only one file per ZIP")
    print("\nFix Applied:")
    print("  Enhanced csv_loader.py to extract and process each CSV individually")
    print("\n" + "="*70)
    print()
    
    success = test_fix()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
