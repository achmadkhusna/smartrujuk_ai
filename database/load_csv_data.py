"""
CSV Data Loader Script for Multiple Province Datasets
Supports loading hospital data from various CSV formats
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal
from src.csv_loader import CSVDataLoader
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Main function for loading CSV data"""
    parser = argparse.ArgumentParser(description='Load hospital data from CSV files')
    parser.add_argument('--file', type=str, help='Path to a single CSV file')
    parser.add_argument('--dir', type=str, help='Path to directory containing CSV files')
    parser.add_argument('--province', type=str, help='Filter by province name (optional)')
    parser.add_argument('--type', type=str, choices=['faskes', 'bed_ratio', 'auto'], 
                       default='auto', help='Type of CSV data (default: auto-detect)')
    
    args = parser.parse_args()
    
    # Validate input
    if not args.file and not args.dir:
        print("Error: Either --file or --dir must be specified")
        parser.print_help()
        return
    
    # Initialize database session and loader
    db = SessionLocal()
    loader = CSVDataLoader(db)
    
    try:
        print("=== SmartRujuk+ CSV Data Loader ===\n")
        
        if args.file:
            # Load single file
            print(f"Loading data from: {args.file}")
            if args.province:
                print(f"Filtering by province: {args.province}")
            
            if not os.path.exists(args.file):
                print(f"Error: File not found: {args.file}")
                return
            
            # Determine loader type
            if args.type == 'auto':
                filename = os.path.basename(args.file).lower()
                if 'bed' in filename or 'ratio' in filename:
                    count = loader.load_bed_ratio_csv(args.file, args.province)
                else:
                    count = loader.load_bpjs_faskes_csv(args.file, args.province)
            elif args.type == 'faskes':
                count = loader.load_bpjs_faskes_csv(args.file, args.province)
            else:
                count = loader.load_bed_ratio_csv(args.file, args.province)
            
            print(f"\n✅ Successfully loaded {count} records from {os.path.basename(args.file)}")
        
        elif args.dir:
            # Load all files from directory
            print(f"Loading data from directory: {args.dir}")
            if args.province:
                print(f"Filtering by province: {args.province}")
            
            if not os.path.exists(args.dir):
                print(f"Error: Directory not found: {args.dir}")
                return
            
            results = loader.load_from_directory(args.dir)
            
            print("\n=== Loading Results ===")
            total_records = 0
            for filename, count in results.items():
                print(f"  {filename}: {count} records")
                total_records += count
            
            print(f"\n✅ Total: {total_records} records loaded from {len(results)} files")
        
        # Show summary
        from src.models import Hospital
        total_hospitals = db.query(Hospital).count()
        print(f"\n📊 Database Summary:")
        print(f"  Total hospitals in database: {total_hospitals}")
        
    except Exception as e:
        logger.error(f"Error loading CSV data: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def create_sample_csv():
    """
    Create a sample CSV file for testing
    """
    import pandas as pd
    
    sample_data = [
        {
            'name': 'RS Sample Jakarta Barat',
            'address': 'Jl. Sample No.1, Jakarta Barat',
            'latitude': -6.1746,
            'longitude': 106.7857,
            'type': 'Rumah Sakit Umum',
            'class': 'B',
            'total_beds': 100,
            'available_beds': 50,
            'phone': '021-12345678',
            'province': 'DKI Jakarta'
        },
        {
            'name': 'RS Sample Bandung',
            'address': 'Jl. Sample No.2, Bandung',
            'latitude': -6.9175,
            'longitude': 107.6191,
            'type': 'Rumah Sakit Umum',
            'class': 'C',
            'total_beds': 80,
            'available_beds': 40,
            'phone': '022-87654321',
            'province': 'Jawa Barat'
        },
        {
            'name': 'RS Sample Surabaya',
            'address': 'Jl. Sample No.3, Surabaya',
            'latitude': -7.2575,
            'longitude': 112.7521,
            'type': 'Rumah Sakit Umum',
            'class': 'B',
            'total_beds': 120,
            'available_beds': 60,
            'phone': '031-98765432',
            'province': 'Jawa Timur'
        }
    ]
    
    df = pd.DataFrame(sample_data)
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Save sample CSV
    csv_path = os.path.join(data_dir, 'sample_hospitals.csv')
    df.to_csv(csv_path, index=False, encoding='utf-8')
    
    print(f"✅ Sample CSV created: {csv_path}")
    print("\nTo load this sample data, run:")
    print(f"  python database/load_csv_data.py --file {csv_path}")
    
    return csv_path


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, show help and create sample
        print("No arguments provided. Creating sample CSV file...\n")
        create_sample_csv()
        print("\n" + "="*60)
        print("Usage Examples:")
        print("="*60)
        print("\n1. Load a single CSV file:")
        print("   python database/load_csv_data.py --file path/to/hospitals.csv")
        print("\n2. Load all CSV files from a directory:")
        print("   python database/load_csv_data.py --dir path/to/csv_folder")
        print("\n3. Load with province filter:")
        print("   python database/load_csv_data.py --file hospitals.csv --province 'DKI Jakarta'")
        print("\n4. Specify CSV type:")
        print("   python database/load_csv_data.py --file data.csv --type faskes")
        print()
    else:
        main()
