"""
Data Statistics Viewer
Display comprehensive statistics about loaded datasets
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import SessionLocal
from src.models import Hospital, WaitTimeHistory, CapacityHistory, Referral, Patient
from sqlalchemy import func, distinct
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class DataStatistics:
    """Display data statistics"""
    
    def __init__(self):
        """Initialize statistics viewer"""
        self.db = SessionLocal()
    
    def get_hospital_stats(self):
        """Get hospital statistics"""
        logger.info("\n" + "="*60)
        logger.info("📊 Hospital Statistics")
        logger.info("="*60)
        
        # Total hospitals
        total = self.db.query(Hospital).count()
        logger.info(f"\nTotal Facilities: {total:,}")
        
        if total == 0:
            logger.warning("No hospitals in database. Run: python database/load_all_datasets.py")
            return
        
        # By type
        logger.info("\n📋 By Facility Type:")
        types = self.db.query(
            Hospital.type, func.count(Hospital.id)
        ).group_by(Hospital.type).all()
        
        for facility_type, count in sorted(types, key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            logger.info(f"  {facility_type}: {count:,} ({percentage:.1f}%)")
        
        # By class
        logger.info("\n🏥 By Hospital Class:")
        classes = self.db.query(
            Hospital.class_, func.count(Hospital.id)
        ).group_by(Hospital.class_).all()
        
        for cls, count in sorted(classes, key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            logger.info(f"  Class {cls}: {count:,} ({percentage:.1f}%)")
        
        # Capacity statistics
        logger.info("\n🛏️  Bed Capacity:")
        total_beds = self.db.query(func.sum(Hospital.total_beds)).scalar() or 0
        available_beds = self.db.query(func.sum(Hospital.available_beds)).scalar() or 0
        
        logger.info(f"  Total Beds: {total_beds:,}")
        logger.info(f"  Available Beds: {available_beds:,}")
        logger.info(f"  Occupied: {total_beds - available_beds:,}")
        
        if total_beds > 0:
            occupancy = ((total_beds - available_beds) / total_beds) * 100
            logger.info(f"  Occupancy Rate: {occupancy:.1f}%")
        
        # Average beds per hospital
        avg_beds = self.db.query(func.avg(Hospital.total_beds)).scalar() or 0
        logger.info(f"  Average Beds per Facility: {avg_beds:.1f}")
        
        # Geographic distribution (top provinces)
        logger.info("\n🗺️  Top 10 Provinces by Hospital Count:")
        # Note: We don't have province in Hospital model, but we can approximate
        # by grouping nearby coordinates
        
        # Emergency availability
        emergency_count = self.db.query(Hospital).filter(
            Hospital.emergency_available == True
        ).count()
        logger.info(f"\n🚑 Emergency Services Available: {emergency_count:,} ({(emergency_count/total)*100:.1f}%)")
    
    def get_training_data_stats(self):
        """Get training data statistics"""
        logger.info("\n" + "="*60)
        logger.info("📈 Training Data Statistics")
        logger.info("="*60)
        
        # Wait time history
        wait_time_count = self.db.query(WaitTimeHistory).count()
        logger.info(f"\nWait Time Records: {wait_time_count:,}")
        
        if wait_time_count > 0:
            # By severity
            logger.info("\n⏱️  By Severity Level:")
            severities = self.db.query(
                WaitTimeHistory.severity_level, 
                func.count(WaitTimeHistory.id),
                func.avg(WaitTimeHistory.wait_time_minutes)
            ).group_by(WaitTimeHistory.severity_level).all()
            
            for severity, count, avg_wait in severities:
                logger.info(f"  {severity.value}: {count:,} records, avg {avg_wait:.1f} minutes")
            
            # Time range
            oldest = self.db.query(func.min(WaitTimeHistory.timestamp)).scalar()
            newest = self.db.query(func.max(WaitTimeHistory.timestamp)).scalar()
            
            if oldest and newest:
                days = (newest - oldest).days
                logger.info(f"\n📅 Data Range: {days} days ({oldest.strftime('%Y-%m-%d')} to {newest.strftime('%Y-%m-%d')})")
        
        # Capacity history
        capacity_count = self.db.query(CapacityHistory).count()
        logger.info(f"\n🛏️  Capacity Records: {capacity_count:,}")
        
        if capacity_count > 0:
            avg_available = self.db.query(func.avg(CapacityHistory.available_beds)).scalar() or 0
            avg_occupied = self.db.query(func.avg(CapacityHistory.occupied_beds)).scalar() or 0
            
            logger.info(f"  Average Available: {avg_available:.1f} beds")
            logger.info(f"  Average Occupied: {avg_occupied:.1f} beds")
    
    def get_referral_stats(self):
        """Get referral statistics"""
        logger.info("\n" + "="*60)
        logger.info("🔄 Referral Statistics")
        logger.info("="*60)
        
        referral_count = self.db.query(Referral).count()
        logger.info(f"\nTotal Referrals: {referral_count:,}")
        
        if referral_count > 0:
            # By status
            logger.info("\n📋 By Status:")
            statuses = self.db.query(
                Referral.status, func.count(Referral.id)
            ).group_by(Referral.status).all()
            
            for status, count in statuses:
                percentage = (count / referral_count) * 100
                logger.info(f"  {status.value}: {count:,} ({percentage:.1f}%)")
            
            # By severity
            logger.info("\n⚠️  By Severity:")
            severities = self.db.query(
                Referral.severity_level, func.count(Referral.id)
            ).group_by(Referral.severity_level).all()
            
            for severity, count in severities:
                percentage = (count / referral_count) * 100
                logger.info(f"  {severity.value}: {count:,} ({percentage:.1f}%)")
            
            # Wait time accuracy (if we have actual wait times)
            with_actual = self.db.query(Referral).filter(
                Referral.actual_wait_time.isnot(None)
            ).count()
            
            if with_actual > 0:
                logger.info(f"\n✅ Referrals with Actual Wait Time: {with_actual:,}")
                
                # Calculate MAE
                referrals = self.db.query(Referral).filter(
                    Referral.actual_wait_time.isnot(None),
                    Referral.predicted_wait_time.isnot(None)
                ).all()
                
                if referrals:
                    errors = [abs(r.actual_wait_time - r.predicted_wait_time) for r in referrals]
                    mae = sum(errors) / len(errors)
                    logger.info(f"  Prediction MAE: {mae:.1f} minutes")
    
    def get_patient_stats(self):
        """Get patient statistics"""
        logger.info("\n" + "="*60)
        logger.info("👥 Patient Statistics")
        logger.info("="*60)
        
        patient_count = self.db.query(Patient).count()
        logger.info(f"\nTotal Patients: {patient_count:,}")
        
        if patient_count > 0:
            # By gender
            logger.info("\n⚥ By Gender:")
            genders = self.db.query(
                Patient.gender, func.count(Patient.id)
            ).group_by(Patient.gender).all()
            
            for gender, count in genders:
                percentage = (count / patient_count) * 100
                logger.info(f"  {gender.value}: {count:,} ({percentage:.1f}%)")
    
    def get_data_quality_metrics(self):
        """Get data quality metrics"""
        logger.info("\n" + "="*60)
        logger.info("✅ Data Quality Metrics")
        logger.info("="*60)
        
        total = self.db.query(Hospital).count()
        
        if total == 0:
            logger.warning("\nNo data to analyze")
            return
        
        # Coordinates validity
        invalid_coords = self.db.query(Hospital).filter(
            (Hospital.latitude == 0) | (Hospital.longitude == 0)
        ).count()
        
        valid_coords = total - invalid_coords
        logger.info(f"\n📍 Valid Coordinates: {valid_coords:,} / {total:,} ({(valid_coords/total)*100:.1f}%)")
        
        if invalid_coords > 0:
            logger.info(f"   ⚠️  Invalid: {invalid_coords:,}")
        
        # Phone numbers
        with_phone = self.db.query(Hospital).filter(
            Hospital.phone.isnot(None),
            Hospital.phone != ''
        ).count()
        logger.info(f"\n📞 With Phone: {with_phone:,} / {total:,} ({(with_phone/total)*100:.1f}%)")
        
        # Bed capacity data
        with_beds = self.db.query(Hospital).filter(
            Hospital.total_beds > 0
        ).count()
        logger.info(f"\n🛏️  With Bed Data: {with_beds:,} / {total:,} ({(with_beds/total)*100:.1f}%)")
    
    def show_all_stats(self):
        """Show all statistics"""
        try:
            logger.info("\n" + "="*60)
            logger.info("SmartRujuk+ Data Statistics Viewer")
            logger.info("="*60)
            logger.info(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            self.get_hospital_stats()
            self.get_training_data_stats()
            self.get_referral_stats()
            self.get_patient_stats()
            self.get_data_quality_metrics()
            
            logger.info("\n" + "="*60)
            logger.info("✅ Statistics generation complete!")
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"\n❌ Error generating statistics: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.db.close()


def main():
    """Main function"""
    stats = DataStatistics()
    stats.show_all_stats()


if __name__ == "__main__":
    main()
