"""
Database initialization script
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import engine, Base, SessionLocal
from src.models import Hospital, Patient, Referral, CapacityHistory, WaitTimeHistory, APIConfig
from datetime import datetime, timedelta
import random

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

def add_sample_hospitals():
    """Add sample hospital data"""
    db = SessionLocal()
    
    print("Adding sample hospitals...")
    
    hospitals = [
        {
            'name': 'RSUP Dr. Cipto Mangunkusumo',
            'address': 'Jl. Diponegoro No.71, Jakarta Pusat',
            'latitude': -6.1862,
            'longitude': 106.8311,
            'type': 'Rumah Sakit Umum',
            'class_': 'A',
            'total_beds': 250,
            'available_beds': 45,
            'phone': '021-3142323',
            'emergency_available': True
        },
        {
            'name': 'RS Fatmawati',
            'address': 'Jl. RS Fatmawati No.4, Jakarta Selatan',
            'latitude': -6.2921,
            'longitude': 106.7970,
            'type': 'Rumah Sakit Umum',
            'class_': 'A',
            'total_beds': 200,
            'available_beds': 30,
            'phone': '021-7501524',
            'emergency_available': True
        },
        {
            'name': 'RSUP Persahabatan',
            'address': 'Jl. Persahabatan Raya No.1, Jakarta Timur',
            'latitude': -6.1890,
            'longitude': 106.8941,
            'type': 'Rumah Sakit Umum',
            'class_': 'A',
            'total_beds': 180,
            'available_beds': 55,
            'phone': '021-4891708',
            'emergency_available': True
        },
        {
            'name': 'RS Harapan Kita',
            'address': 'Jl. Letjen S. Parman Kav.87, Jakarta Barat',
            'latitude': -6.1746,
            'longitude': 106.7857,
            'type': 'Rumah Sakit Khusus Jantung',
            'class_': 'A',
            'total_beds': 150,
            'available_beds': 20,
            'phone': '021-5684093',
            'emergency_available': True
        },
        {
            'name': 'RSUD Tarakan',
            'address': 'Jl. Letjen Suprapto, Jakarta Pusat',
            'latitude': -6.1496,
            'longitude': 106.8600,
            'type': 'Rumah Sakit Umum',
            'class_': 'B',
            'total_beds': 120,
            'available_beds': 38,
            'phone': '021-4244446',
            'emergency_available': True
        },
        {
            'name': 'RS Pelni',
            'address': 'Jl. Aipda K.S. Tubun No.92-94, Jakarta Pusat',
            'latitude': -6.1623,
            'longitude': 106.8115,
            'type': 'Rumah Sakit Umum',
            'class_': 'B',
            'total_beds': 100,
            'available_beds': 42,
            'phone': '021-5483030',
            'emergency_available': True
        },
        {
            'name': 'RSUD Pasar Minggu',
            'address': 'Jl. TB Simatupang No.1, Jakarta Selatan',
            'latitude': -6.2943,
            'longitude': 106.8363,
            'type': 'Rumah Sakit Umum',
            'class_': 'C',
            'total_beds': 90,
            'available_beds': 60,
            'phone': '021-7806722',
            'emergency_available': True
        },
        {
            'name': 'RS Islam Jakarta Cempaka Putih',
            'address': 'Jl. Cempaka Putih Tengah I/1, Jakarta Pusat',
            'latitude': -6.1737,
            'longitude': 106.8687,
            'type': 'Rumah Sakit Umum',
            'class_': 'B',
            'total_beds': 110,
            'available_beds': 25,
            'phone': '021-4244614',
            'emergency_available': True
        },
        {
            'name': 'RSUD Budhi Asih',
            'address': 'Jl. Dewi Sartika No.200, Jakarta Timur',
            'latitude': -6.2345,
            'longitude': 106.8936,
            'type': 'Rumah Sakit Umum',
            'class_': 'B',
            'total_beds': 130,
            'available_beds': 48,
            'phone': '021-8004142',
            'emergency_available': True
        },
        {
            'name': 'RS Hermina Bekasi',
            'address': 'Jl. Chairil Anwar No.2, Bekasi',
            'latitude': -6.2383,
            'longitude': 107.0012,
            'type': 'Rumah Sakit Umum',
            'class_': 'B',
            'total_beds': 85,
            'available_beds': 35,
            'phone': '021-88956800',
            'emergency_available': True
        }
    ]
    
    for h_data in hospitals:
        hospital = Hospital(**h_data)
        db.add(hospital)
    
    db.commit()
    print(f"{len(hospitals)} sample hospitals added!")
    
    db.close()

def add_sample_patients():
    """Add sample patient data"""
    db = SessionLocal()
    
    print("Adding sample patients...")
    
    patients = [
        {
            'bpjs_number': '0001234567890',
            'name': 'Ahmad Suryadi',
            'date_of_birth': datetime(1980, 5, 15),
            'gender': 'M',
            'address': 'Jl. Merdeka No.10, Jakarta Pusat',
            'phone': '081234567890'
        },
        {
            'bpjs_number': '0001234567891',
            'name': 'Siti Nurhaliza',
            'date_of_birth': datetime(1992, 8, 22),
            'gender': 'F',
            'address': 'Jl. Sudirman No.45, Jakarta Selatan',
            'phone': '081234567891'
        },
        {
            'bpjs_number': '0001234567892',
            'name': 'Budi Santoso',
            'date_of_birth': datetime(1975, 3, 10),
            'gender': 'M',
            'address': 'Jl. Gatot Subroto No.88, Jakarta Timur',
            'phone': '081234567892'
        },
        {
            'bpjs_number': '0001234567893',
            'name': 'Dewi Lestari',
            'date_of_birth': datetime(1988, 11, 5),
            'gender': 'F',
            'address': 'Jl. Thamrin No.12, Jakarta Pusat',
            'phone': '081234567893'
        },
        {
            'bpjs_number': '0001234567894',
            'name': 'Rudi Hartono',
            'date_of_birth': datetime(1985, 7, 18),
            'gender': 'M',
            'address': 'Jl. Ahmad Yani No.25, Jakarta Utara',
            'phone': '081234567894'
        }
    ]
    
    for p_data in patients:
        patient = Patient(**p_data)
        db.add(patient)
    
    db.commit()
    print(f"{len(patients)} sample patients added!")
    
    db.close()

def add_sample_history_data():
    """Add sample historical data for predictions"""
    db = SessionLocal()
    
    print("Adding sample history data...")
    
    hospitals = db.query(Hospital).all()
    
    # Add capacity history
    for hospital in hospitals:
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            occupied = random.randint(
                int(hospital.total_beds * 0.4), 
                int(hospital.total_beds * 0.9)
            )
            available = hospital.total_beds - occupied
            
            capacity_hist = CapacityHistory(
                hospital_id=hospital.id,
                available_beds=available,
                occupied_beds=occupied,
                timestamp=date
            )
            db.add(capacity_hist)
    
    # Add wait time history
    severity_levels = ['low', 'medium', 'high', 'critical']
    base_wait_times = {
        'low': 30,
        'medium': 60,
        'high': 90,
        'critical': 15
    }
    
    for hospital in hospitals:
        for severity in severity_levels:
            for i in range(20):
                date = datetime.now() - timedelta(days=i)
                base_time = base_wait_times[severity]
                wait_time = base_time + random.randint(-15, 30)
                wait_time = max(5, wait_time)  # Minimum 5 minutes
                
                wait_hist = WaitTimeHistory(
                    hospital_id=hospital.id,
                    severity_level=severity,
                    wait_time_minutes=wait_time,
                    timestamp=date
                )
                db.add(wait_hist)
    
    db.commit()
    print("Historical data added!")
    
    db.close()

def load_api_config():
    """Load API configuration from soal.txt"""
    print("Loading API configuration...")
    try:
        from database.load_api_config import load_api_config_to_db
        load_api_config_to_db()
        print("API configuration loaded!")
    except Exception as e:
        print(f"Warning: Could not load API config: {str(e)}")


def main():
    """Main initialization function"""
    print("=== SmartRujuk+ Database Initialization ===")
    
    try:
        create_tables()
        load_api_config()
        add_sample_hospitals()
        add_sample_patients()
        add_sample_history_data()
        
        print("\n✅ Database initialization completed successfully!")
        print("\nYou can now:")
        print("  1. Load CSV data: python database/load_csv_data.py --help")
        print("  2. Run the Streamlit app: streamlit run app.py")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
