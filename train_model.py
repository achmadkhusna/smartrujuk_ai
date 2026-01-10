#!/usr/bin/env python3
"""
Train prediction models with real data from database
"""
import sys
import numpy as np
from datetime import datetime, timedelta
import random

from src.database import SessionLocal, init_db
from src.models import (
    Patient, Referral, Hospital, WaitTimeHistory, CapacityHistory,
    SeverityEnum, StatusEnum
)
from src.predictor import WaitTimePredictor, CapacityAnalyzer
from sqlalchemy import func

print("=" * 80)
print("MODEL TRAINING SCRIPT")
print("=" * 80)

# Initialize database
print("\n1. Initializing database...")
init_db()
db = SessionLocal()

# Check data availability
print("\n2. Checking data availability...")
patient_count = db.query(func.count(Patient.id)).scalar()
referral_count = db.query(func.count(Referral.id)).scalar()
hospital_count = db.query(func.count(Hospital.id)).scalar()

print(f"   - Patients: {patient_count}")
print(f"   - Referrals: {referral_count}")
print(f"   - Hospitals: {hospital_count}")

if hospital_count == 0:
    print("\n✗ No hospitals in database. Please run test_satusehat_integration.py first.")
    sys.exit(1)

# Generate synthetic wait time history for training
print("\n3. Generating synthetic wait time history for training...")
try:
    # Check if we already have wait time history
    wait_time_count = db.query(func.count(WaitTimeHistory.id)).scalar()
    
    if wait_time_count < 100:
        hospitals = db.query(Hospital).all()
        severities = [SeverityEnum.low, SeverityEnum.medium, SeverityEnum.high, SeverityEnum.critical]
        
        # Generate data for the past 30 days
        start_date = datetime.now() - timedelta(days=30)
        
        for day in range(30):
            current_date = start_date + timedelta(days=day)
            
            for hour in range(24):
                timestamp = current_date.replace(hour=hour, minute=0, second=0)
                
                for hospital in hospitals:
                    for severity in severities:
                        # Generate realistic wait times based on severity and time
                        base_wait_times = {
                            SeverityEnum.low: 45,
                            SeverityEnum.medium: 75,
                            SeverityEnum.high: 120,
                            SeverityEnum.critical: 20
                        }
                        
                        # Add variation based on time of day
                        time_factor = 1.0
                        if 8 <= hour <= 12 or 17 <= hour <= 20:  # Peak hours
                            time_factor = 1.5
                        elif 0 <= hour <= 6:  # Night hours
                            time_factor = 0.7
                        
                        base_time = base_wait_times[severity]
                        wait_time = int(base_time * time_factor + random.uniform(-10, 10))
                        wait_time = max(5, wait_time)  # Minimum 5 minutes
                        
                        history_entry = WaitTimeHistory(
                            hospital_id=hospital.id,
                            severity_level=severity,
                            wait_time_minutes=wait_time,
                            timestamp=timestamp
                        )
                        db.add(history_entry)
        
        db.commit()
        final_count = db.query(func.count(WaitTimeHistory.id)).scalar()
        print(f"   ✓ Generated {final_count} wait time history entries")
    else:
        print(f"   ✓ Using existing {wait_time_count} wait time history entries")
        
except Exception as e:
    print(f"   ✗ Error generating wait time history: {str(e)}")
    db.rollback()

# Generate synthetic capacity history
print("\n4. Generating synthetic capacity history for training...")
try:
    capacity_count = db.query(func.count(CapacityHistory.id)).scalar()
    
    if capacity_count < 100:
        hospitals = db.query(Hospital).all()
        start_date = datetime.now() - timedelta(days=30)
        
        for day in range(30):
            current_date = start_date + timedelta(days=day)
            
            for hour in range(24):
                timestamp = current_date.replace(hour=hour, minute=0, second=0)
                
                for hospital in hospitals:
                    # Calculate occupied beds based on time
                    time_factor = 0.6  # Base occupancy
                    if 8 <= hour <= 18:  # Day time
                        time_factor = 0.8
                    
                    occupied = int(hospital.total_beds * time_factor + random.uniform(-20, 20))
                    occupied = max(0, min(occupied, hospital.total_beds))
                    available = hospital.total_beds - occupied
                    
                    capacity_entry = CapacityHistory(
                        hospital_id=hospital.id,
                        available_beds=available,
                        occupied_beds=occupied,
                        timestamp=timestamp
                    )
                    db.add(capacity_entry)
        
        db.commit()
        final_count = db.query(func.count(CapacityHistory.id)).scalar()
        print(f"   ✓ Generated {final_count} capacity history entries")
    else:
        print(f"   ✓ Using existing {capacity_count} capacity history entries")
        
except Exception as e:
    print(f"   ✗ Error generating capacity history: {str(e)}")
    db.rollback()

# Train wait time prediction model
print("\n5. Training wait time prediction model...")
try:
    predictor = WaitTimePredictor()
    success = predictor.train(db)
    
    if success:
        print("   ✓ Model trained successfully")
        
        # Test the model
        print("\n   Testing model predictions:")
        test_cases = [
            (1, 'low'),
            (1, 'medium'),
            (1, 'high'),
            (1, 'critical')
        ]
        
        for hospital_id, severity in test_cases:
            predicted_time = predictor.predict_wait_time(hospital_id, severity)
            print(f"     - Hospital {hospital_id}, Severity {severity}: {predicted_time} minutes")
    else:
        print("   ! Model training skipped (insufficient data)")
        
except Exception as e:
    print(f"   ✗ Error training model: {str(e)}")
    import traceback
    traceback.print_exc()

# Analyze hospital capacity
print("\n6. Analyzing hospital capacity...")
try:
    analyzer = CapacityAnalyzer()
    hospitals = db.query(Hospital).all()
    
    print("\n   Hospital capacity analysis:")
    for hospital in hospitals:
        utilization = analyzer.calculate_utilization(hospital)
        trend = analyzer.predict_capacity_trend(db, hospital.id)
        
        print(f"\n     {hospital.name}:")
        print(f"       - Utilization: {utilization:.1%}")
        print(f"       - Available beds: {hospital.available_beds}/{hospital.total_beds}")
        print(f"       - Trend: {trend}")
        
except Exception as e:
    print(f"   ✗ Error analyzing capacity: {str(e)}")

# Update referrals with predicted wait times
print("\n7. Updating referrals with predicted wait times...")
try:
    predictor = WaitTimePredictor()
    if predictor.is_trained:
        referrals = db.query(Referral).filter(Referral.predicted_wait_time == None).all()
        
        updated_count = 0
        for referral in referrals:
            predicted_time = predictor.predict_wait_time(
                referral.to_hospital_id,
                referral.severity_level.value
            )
            referral.predicted_wait_time = predicted_time
            updated_count += 1
        
        db.commit()
        print(f"   ✓ Updated {updated_count} referrals with predicted wait times")
    else:
        print("   ! Skipped (model not trained)")
        
except Exception as e:
    print(f"   ✗ Error updating referrals: {str(e)}")
    db.rollback()

# Generate summary statistics
print("\n8. Generating summary statistics...")
try:
    total_patients = db.query(func.count(Patient.id)).scalar()
    total_referrals = db.query(func.count(Referral.id)).scalar()
    total_hospitals = db.query(func.count(Hospital.id)).scalar()
    
    pending_referrals = db.query(func.count(Referral.id)).filter(
        Referral.status == StatusEnum.pending
    ).scalar()
    
    completed_referrals = db.query(func.count(Referral.id)).filter(
        Referral.status == StatusEnum.completed
    ).scalar()
    
    print(f"\n   System Statistics:")
    print(f"     - Total Patients: {total_patients}")
    print(f"     - Total Referrals: {total_referrals}")
    print(f"       • Pending: {pending_referrals}")
    print(f"       • Completed: {completed_referrals}")
    print(f"     - Total Hospitals: {total_hospitals}")
    
    # Calculate average wait time
    avg_wait = db.query(func.avg(WaitTimeHistory.wait_time_minutes)).scalar()
    if avg_wait:
        print(f"     - Average Wait Time: {avg_wait:.1f} minutes")
    
except Exception as e:
    print(f"   ✗ Error generating statistics: {str(e)}")

db.close()

print("\n" + "=" * 80)
print("MODEL TRAINING COMPLETE")
print("=" * 80)
print("\nYou can now run the Streamlit app with:")
print("  streamlit run app.py")
print("=" * 80)
