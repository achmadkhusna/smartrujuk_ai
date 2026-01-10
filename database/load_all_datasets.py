"""
Comprehensive Data Loading Script
Loads all Kaggle datasets into the database and trains ML models
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal, engine
from src.csv_loader import CSVDataLoader
from src.models import Hospital, WaitTimeHistory, CapacityHistory, Base
from src.predictor import WaitTimePredictor
from database.dataset_downloader import DatasetDownloader
import logging
from pathlib import Path
from datetime import datetime, timedelta
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataPipeline:
    """
    Comprehensive data pipeline for SmartRujuk+ system
    """
    
    def __init__(self):
        """Initialize data pipeline"""
        self.db = SessionLocal()
        self.loader = CSVDataLoader(self.db)
        self.downloader = DatasetDownloader()
        self.stats = {
            'datasets_loaded': 0,
            'total_hospitals': 0,
            'total_records': 0,
            'training_data_generated': 0
        }
    
    def setup_database(self):
        """Initialize database tables"""
        logger.info("Setting up database tables...")
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created/verified")
            return True
        except Exception as e:
            logger.error(f"❌ Error setting up database: {str(e)}")
            return False
    
    def load_bpjs_faskes_dataset(self):
        """Load BPJS Faskes dataset"""
        logger.info("\n" + "="*60)
        logger.info("Loading BPJS Faskes Dataset")
        logger.info("="*60)
        
        # Find the dataset file
        available = self.downloader.list_available_files()
        
        if not available['bpjs_faskes']:
            logger.warning("⚠️  BPJS Faskes dataset not found")
            logger.info("Please run: python database/dataset_downloader.py")
            return 0
        
        total_loaded = 0
        for csv_file in available['bpjs_faskes']:
            logger.info(f"Loading: {os.path.basename(csv_file)}")
            count = self.loader.load_bpjs_faskes_csv(csv_file)
            total_loaded += count
            
        logger.info(f"✅ Loaded {total_loaded} hospitals from BPJS Faskes dataset")
        self.stats['datasets_loaded'] += 1
        self.stats['total_records'] += total_loaded
        
        return total_loaded
    
    def load_bed_ratio_dataset(self):
        """Load Bed to Population Ratio dataset"""
        logger.info("\n" + "="*60)
        logger.info("Loading Bed Ratio Dataset")
        logger.info("="*60)
        
        available = self.downloader.list_available_files()
        
        if not available['bed_ratio']:
            logger.warning("⚠️  Bed Ratio dataset not found")
            logger.info("Please run: python database/dataset_downloader.py")
            return 0
        
        total_updated = 0
        for csv_file in available['bed_ratio']:
            if csv_file.endswith('.csv'):
                logger.info(f"Loading: {os.path.basename(csv_file)}")
                count = self.loader.load_bed_ratio_csv(csv_file)
                total_updated += count
        
        logger.info(f"✅ Updated {total_updated} hospitals with bed ratio data")
        self.stats['datasets_loaded'] += 1
        
        return total_updated
    
    def generate_training_data(self, num_records: int = 500):
        """
        Generate synthetic training data for ML models
        Args:
            num_records: Number of training records to generate
        """
        logger.info("\n" + "="*60)
        logger.info("Generating Training Data for ML Models")
        logger.info("="*60)
        
        try:
            # Get all hospitals
            hospitals = self.db.query(Hospital).all()
            
            if not hospitals:
                logger.warning("⚠️  No hospitals in database, skipping training data generation")
                return 0
            
            logger.info(f"Generating {num_records} training records for {len(hospitals)} hospitals...")
            
            severity_levels = ['low', 'medium', 'high', 'critical']
            severity_weights = {
                'low': (20, 60),      # min, max wait time
                'medium': (40, 120),
                'high': (60, 180),
                'critical': (10, 30)
            }
            
            records_generated = 0
            
            # Generate wait time history
            for _ in range(num_records):
                hospital = random.choice(hospitals)
                severity = random.choice(severity_levels)
                
                # Random timestamp within last 90 days
                days_ago = random.randint(0, 90)
                hours_ago = random.randint(0, 23)
                timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
                
                # Generate wait time based on severity
                min_wait, max_wait = severity_weights[severity]
                wait_time = random.randint(min_wait, max_wait)
                
                # Add some variance based on time of day
                hour = timestamp.hour
                if 8 <= hour <= 12 or 16 <= hour <= 20:  # Peak hours
                    wait_time = int(wait_time * 1.3)
                
                wait_record = WaitTimeHistory(
                    hospital_id=hospital.id,
                    severity_level=severity,
                    wait_time_minutes=wait_time,
                    timestamp=timestamp
                )
                
                self.db.add(wait_record)
                records_generated += 1
                
                if records_generated % 100 == 0:
                    self.db.commit()
            
            # Generate capacity history
            for _ in range(num_records // 2):
                hospital = random.choice(hospitals)
                
                days_ago = random.randint(0, 90)
                hours_ago = random.randint(0, 23)
                timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
                
                # Random occupancy
                occupied = random.randint(0, hospital.total_beds)
                available = hospital.total_beds - occupied
                
                capacity_record = CapacityHistory(
                    hospital_id=hospital.id,
                    available_beds=available,
                    occupied_beds=occupied,
                    timestamp=timestamp
                )
                
                self.db.add(capacity_record)
            
            self.db.commit()
            
            logger.info(f"✅ Generated {records_generated} wait time records")
            logger.info(f"✅ Generated {num_records // 2} capacity records")
            
            self.stats['training_data_generated'] = records_generated
            
            return records_generated
            
        except Exception as e:
            logger.error(f"❌ Error generating training data: {str(e)}")
            self.db.rollback()
            return 0
    
    def train_ml_models(self):
        """Train ML models with loaded data"""
        logger.info("\n" + "="*60)
        logger.info("Training ML Models")
        logger.info("="*60)
        
        try:
            predictor = WaitTimePredictor()
            success = predictor.train(self.db)
            
            if success:
                logger.info("✅ ML models trained successfully")
                return True
            else:
                logger.warning("⚠️  Not enough data to train ML models")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error training ML models: {str(e)}")
            return False
    
    def show_summary(self):
        """Display summary of loaded data"""
        logger.info("\n" + "="*60)
        logger.info("Data Loading Summary")
        logger.info("="*60)
        
        try:
            # Count hospitals
            total_hospitals = self.db.query(Hospital).count()
            
            # Count by type
            rs_count = self.db.query(Hospital).filter(
                Hospital.type.like('%Rumah Sakit%')
            ).count()
            
            puskesmas_count = self.db.query(Hospital).filter(
                Hospital.type.like('%Puskesmas%')
            ).count()
            
            klinik_count = self.db.query(Hospital).filter(
                Hospital.type.like('%Klinik%')
            ).count()
            
            # Count training data
            wait_time_records = self.db.query(WaitTimeHistory).count()
            capacity_records = self.db.query(CapacityHistory).count()
            
            logger.info(f"\n📊 Database Statistics:")
            logger.info(f"   Total Facilities: {total_hospitals}")
            logger.info(f"   - Rumah Sakit: {rs_count}")
            logger.info(f"   - Puskesmas: {puskesmas_count}")
            logger.info(f"   - Klinik: {klinik_count}")
            logger.info(f"\n📈 Training Data:")
            logger.info(f"   Wait Time Records: {wait_time_records}")
            logger.info(f"   Capacity Records: {capacity_records}")
            logger.info(f"\n✅ Pipeline Statistics:")
            logger.info(f"   Datasets Loaded: {self.stats['datasets_loaded']}")
            logger.info(f"   Total Records Processed: {self.stats['total_records']}")
            logger.info(f"   Training Data Generated: {self.stats['training_data_generated']}")
            
            # Show loader stats
            loader_stats = self.loader.get_stats()
            logger.info(f"\n📋 Loader Statistics:")
            logger.info(f"   Total Processed: {loader_stats['total_processed']}")
            logger.info(f"   Successfully Inserted: {loader_stats['total_inserted']}")
            logger.info(f"   Updated: {loader_stats['total_updated']}")
            logger.info(f"   Skipped: {loader_stats['total_skipped']}")
            
            if loader_stats['errors']:
                logger.info(f"   Errors: {len(loader_stats['errors'])}")
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
    
    def run_full_pipeline(self, generate_training_data: bool = True, train_models: bool = True):
        """
        Run the complete data loading and training pipeline
        Args:
            generate_training_data: Whether to generate synthetic training data
            train_models: Whether to train ML models
        """
        logger.info("\n" + "="*60)
        logger.info("SmartRujuk+ Data Pipeline")
        logger.info("="*60)
        logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Step 1: Setup database
            if not self.setup_database():
                logger.error("Failed to setup database, aborting")
                return False
            
            # Step 2: Load BPJS Faskes dataset
            self.load_bpjs_faskes_dataset()
            
            # Step 3: Load Bed Ratio dataset
            self.load_bed_ratio_dataset()
            
            # Step 4: Generate training data if requested
            if generate_training_data:
                self.generate_training_data()
            
            # Step 5: Train ML models if requested
            if train_models:
                self.train_ml_models()
            
            # Step 6: Show summary
            self.show_summary()
            
            logger.info("\n" + "="*60)
            logger.info("✅ Pipeline completed successfully!")
            logger.info("="*60)
            logger.info("\nNext steps:")
            logger.info("1. Run the application: streamlit run app.py")
            logger.info("2. Or verify the system: python verify_system.py")
            logger.info("="*60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.db.close()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Load all datasets and train models')
    parser.add_argument('--no-training-data', action='store_true', 
                       help='Skip generating synthetic training data')
    parser.add_argument('--no-train', action='store_true',
                       help='Skip ML model training')
    parser.add_argument('--download-first', action='store_true',
                       help='Download datasets before loading')
    
    args = parser.parse_args()
    
    # Download datasets if requested
    if args.download_first:
        logger.info("Downloading datasets first...")
        downloader = DatasetDownloader()
        downloader.download_all()
        logger.info("")
    
    # Run pipeline
    pipeline = DataPipeline()
    
    generate_training = not args.no_training_data
    train_models = not args.no_train
    
    success = pipeline.run_full_pipeline(
        generate_training_data=generate_training,
        train_models=train_models
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
