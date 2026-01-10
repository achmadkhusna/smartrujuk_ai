#!/usr/bin/env python3
"""
Test SATUSEHAT API Integration
"""
import sys
from src.database import init_db, SessionLocal
from src.satusehat_api import SATUSEHATClient
from src.satusehat_loader import SATUSEHATDataLoader
from src.models import Patient, Referral, Hospital
from sqlalchemy import func

print("=" * 80)
print("SATUSEHAT API INTEGRATION TEST")
print("=" * 80)

# Step 1: Initialize database
print("\n1. Initializing database...")
try:
    init_db()
    print("   ✓ Database initialized successfully")
except Exception as e:
    print(f"   ✗ Error initializing database: {str(e)}")
    sys.exit(1)

# Step 2: Test SATUSEHAT API token generation
print("\n2. Testing SATUSEHAT API token generation...")
try:
    client = SATUSEHATClient()
    token = client.get_access_token()
    if token:
        print(f"   ✓ Token generated successfully")
        print(f"   Token (first 20 chars): {token[:20]}...")
    else:
        print("   ! Operating in offline mode (no credentials or API unavailable)")
except Exception as e:
    print(f"   ✗ Error generating token: {str(e)}")

# Step 3: Add sample hospital data
print("\n3. Adding sample hospital data...")
try:
    db = SessionLocal()
    
    # Check if hospitals exist
    hospital_count = db.query(func.count(Hospital.id)).scalar()
    
    if hospital_count == 0:
        sample_hospitals = [
            Hospital(
                name="RSUP Dr. Cipto Mangunkusumo",
                address="Jl. Diponegoro No.71, Jakarta Pusat",
                latitude=-6.1866,
                longitude=106.8312,
                type="Hospital",
                class_="A",
                total_beds=500,
                available_beds=150,
                phone="(021) 3149340",
                emergency_available=True
            ),
            Hospital(
                name="RS Fatmawati",
                address="Jl. RS Fatmawati No.4, Jakarta Selatan",
                latitude=-6.2942,
                longitude=106.7944,
                type="Hospital",
                class_="A",
                total_beds=400,
                available_beds=120,
                phone="(021) 7501524",
                emergency_available=True
            ),
            Hospital(
                name="RSUP Persahabatan",
                address="Jl. Persahabatan Raya No.1, Jakarta Timur",
                latitude=-6.2088,
                longitude=106.8986,
                type="Hospital",
                class_="A",
                total_beds=350,
                available_beds=100,
                phone="(021) 4891708",
                emergency_available=True
            )
        ]
        
        for hospital in sample_hospitals:
            db.add(hospital)
        
        db.commit()
        print(f"   ✓ Added {len(sample_hospitals)} sample hospitals")
    else:
        print(f"   ✓ Database already has {hospital_count} hospitals")
    
    db.close()
except Exception as e:
    print(f"   ✗ Error adding hospitals: {str(e)}")

# Step 4: Test patient data fetching
print("\n4. Testing patient data fetching...")
try:
    client = SATUSEHATClient()
    patients = client.get_patients(count=5, page=1)
    if patients:
        print(f"   ✓ Retrieved {len(patients)} patients")
        if len(patients) > 0:
            first_patient = patients[0].get('resource', {})
            print(f"   Sample patient ID: {first_patient.get('id', 'N/A')}")
    else:
        print("   ! Using sample patient data (offline mode)")
except Exception as e:
    print(f"   ✗ Error fetching patients: {str(e)}")

# Step 5: Test referral data fetching
print("\n5. Testing referral data fetching...")
try:
    client = SATUSEHATClient()
    referrals = client.get_service_requests(count=5, page=1)
    if referrals:
        print(f"   ✓ Retrieved {len(referrals)} service requests")
    else:
        print("   ! Using sample referral data (offline mode)")
except Exception as e:
    print(f"   ✗ Error fetching referrals: {str(e)}")

# Step 6: Load data into database
print("\n6. Loading SATUSEHAT data into database...")
try:
    loader = SATUSEHATDataLoader()
    stats = loader.load_all_data(max_pages=2)
    
    print(f"   ✓ Data loading complete:")
    print(f"     - Total patients in DB: {stats['total_patients']}")
    print(f"     - Total referrals in DB: {stats['total_referrals']}")
    print(f"     - New patients loaded: {stats['new_patients']}")
    print(f"     - New referrals loaded: {stats['new_referrals']}")
    
    loader.close()
except Exception as e:
    print(f"   ✗ Error loading data: {str(e)}")
    import traceback
    traceback.print_exc()

# Step 7: Verify data in database
print("\n7. Verifying data in database...")
try:
    db = SessionLocal()
    
    patient_count = db.query(func.count(Patient.id)).scalar()
    referral_count = db.query(func.count(Referral.id)).scalar()
    hospital_count = db.query(func.count(Hospital.id)).scalar()
    
    print(f"   ✓ Database statistics:")
    print(f"     - Patients: {patient_count}")
    print(f"     - Referrals: {referral_count}")
    print(f"     - Hospitals: {hospital_count}")
    
    if patient_count > 0:
        sample_patient = db.query(Patient).first()
        print(f"   ✓ Sample patient: {sample_patient.name} (BPJS: {sample_patient.bpjs_number})")
    
    if referral_count > 0:
        sample_referral = db.query(Referral).first()
        print(f"   ✓ Sample referral: Severity={sample_referral.severity_level.value}, Status={sample_referral.status.value}")
    
    db.close()
except Exception as e:
    print(f"   ✗ Error verifying data: {str(e)}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
