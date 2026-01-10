"""
CSV Data Loader Module
Comprehensive loader for multiple Kaggle dataset formats
Supports:
- BPJS Faskes Indonesia (israhabibi/list-faskes-bpjs-indonesia)
- Bed to Population Ratio (yafethtb/dataset-rasio-bed-to-population-faskes-ii)
"""
import pandas as pd
import os
import re
import zipfile
import tempfile
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from src.models import Hospital
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVDataLoader:
    """
    Comprehensive CSV data loader for hospital datasets
    Supports multiple Kaggle dataset formats
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize CSV data loader
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.stats = {
            'total_processed': 0,
            'total_inserted': 0,
            'total_updated': 0,
            'total_skipped': 0,
            'errors': []
        }
        
    def extract_coordinates_from_gmaps_link(self, gmaps_link: str) -> Tuple[float, float]:
        """
        Extract latitude and longitude from Google Maps link
        Format: http://maps.google.co.id/?q=LAT,LON
        
        Args:
            gmaps_link: Google Maps URL
            
        Returns:
            Tuple of (latitude, longitude) or (0.0, 0.0) if extraction fails
        """
        if pd.isna(gmaps_link) or not gmaps_link:
            return (0.0, 0.0)
        
        try:
            # Pattern: ?q=LAT,LON or similar
            pattern = r'q=(-?\d+\.?\d*),\s*(-?\d+\.?\d*)'
            match = re.search(pattern, str(gmaps_link))
            
            if match:
                lat = float(match.group(1))
                lon = float(match.group(2))
                
                # Validate coordinates (Indonesia bounds approximately)
                if -11 <= lat <= 6 and 95 <= lon <= 141:
                    return (lat, lon)
        except Exception as e:
            logger.debug(f"Error extracting coordinates from {gmaps_link}: {str(e)}")
        
        return (0.0, 0.0)
    
    def extract_csv_from_zip(self, zip_path: str) -> List[str]:
        """
        Extract CSV files from a ZIP archive
        
        Args:
            zip_path: Path to ZIP file
            
        Returns:
            List of paths to extracted CSV files
        """
        extracted_files = []
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Get list of CSV files in the ZIP
                csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv') and not f.startswith('__MACOSX')]
                
                if not csv_files:
                    logger.warning(f"No CSV files found in ZIP: {zip_path}")
                    return []
                
                # Create a temporary directory to extract files
                temp_dir = tempfile.mkdtemp()
                
                logger.info(f"Found {len(csv_files)} CSV file(s) in ZIP: {', '.join(csv_files)}")
                
                # Extract only CSV files
                for csv_file in csv_files:
                    extracted_path = zip_ref.extract(csv_file, temp_dir)
                    extracted_files.append(extracted_path)
                    logger.debug(f"Extracted: {csv_file} to {extracted_path}")
                
        except Exception as e:
            logger.error(f"Error extracting ZIP file {zip_path}: {str(e)}")
            return []
        
        return extracted_files
    
    def load_bpjs_faskes_csv(self, csv_path: str, province: Optional[str] = None) -> int:
        """
        Load BPJS Faskes data from CSV (Kaggle: israhabibi/list-faskes-bpjs-indonesia)
        Expected columns from dataset:
        - NoLink, Provinsi, KotaKab, Link, TipeFaskes, No, KodeFaskes, NamaFaskes, 
          LatLongFaskes, AlamatFaskes
        
        Args:
            csv_path: Path to CSV file or ZIP file
            province: Filter by province name (optional)
            
        Returns:
            Number of hospitals loaded
        """
        try:
            logger.info(f"Loading BPJS Faskes data from {csv_path}")
            
            # Check if file is a ZIP archive
            if csv_path.endswith('.zip'):
                logger.info(f"Detected ZIP file, extracting CSV files...")
                csv_files = self.extract_csv_from_zip(csv_path)
                
                if not csv_files:
                    logger.error("No CSV files found in ZIP archive")
                    return 0
                
                # Process each CSV file in the ZIP
                total_loaded = 0
                for csv_file in csv_files:
                    logger.info(f"Processing extracted file: {os.path.basename(csv_file)}")
                    count = self._load_single_csv(csv_file, province)
                    total_loaded += count
                    
                    # Clean up extracted file
                    try:
                        os.remove(csv_file)
                    except:
                        pass
                
                return total_loaded
            else:
                # Single CSV file
                return self._load_single_csv(csv_path, province)
                
        except Exception as e:
            logger.error(f"❌ Error loading CSV: {str(e)}")
            self.db.rollback()
            return 0
    
    def _load_single_csv(self, csv_path: str, province: Optional[str] = None) -> int:
        """
        Load a single CSV file with BPJS Faskes data
        
        Args:
            csv_path: Path to CSV file
            province: Filter by province name (optional)
            
        Returns:
            Number of hospitals loaded
        """
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_path, encoding=encoding)
                    logger.info(f"Successfully read CSV with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise ValueError("Could not read CSV file with any supported encoding")
            
            logger.info(f"Loaded {len(df)} rows from CSV")
            logger.info(f"Columns: {', '.join(df.columns)}")
            
            # Standardize column names (handle various CSV formats)
            df.columns = df.columns.str.lower().str.strip()
            
            # Map BPJS Faskes specific columns
            column_mapping = {
                'namafaskes': 'name',
                'nama': 'name',
                'nama_rs': 'name',
                'alamatfaskes': 'address',
                'alamat': 'address',
                'latlongfaskes': 'gmaps_link',
                'latlong': 'gmaps_link',
                'tipefaskes': 'type',
                'tipe': 'type',
                'kodefaskes': 'code',
                'kode': 'code',
                'provinsi': 'province',
                'kotakab': 'city',
                'kota': 'city'
            }
            
            # Rename columns based on mapping
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns and new_col not in df.columns:
                    df.rename(columns={old_col: new_col}, inplace=True)
            
            # Filter by province if specified
            if province and 'province' in df.columns:
                original_count = len(df)
                df = df[df['province'].str.contains(province, case=False, na=False)]
                logger.info(f"Filtered from {original_count} to {len(df)} rows by province: {province}")
            
            # Filter only Rumah Sakit types
            if 'type' in df.columns:
                original_count = len(df)
                # Keep Rumah Sakit, Puskesmas, and Klinik Utama
                df = df[df['type'].str.contains('Rumah Sakit|Puskesmas|Klinik Utama', case=False, na=False)]
                logger.info(f"Filtered from {original_count} to {len(df)} rows by facility type")
            
            # Validate required columns
            if 'name' not in df.columns or 'address' not in df.columns:
                raise ValueError("Required columns 'name' or 'address' not found in CSV")
            
            count = 0
            skipped = 0
            
            for idx, row in df.iterrows():
                try:
                    self.stats['total_processed'] += 1
                    
                    # Skip if name or address is empty
                    if pd.isna(row.get('name')) or pd.isna(row.get('address')):
                        skipped += 1
                        self.stats['total_skipped'] += 1
                        continue
                    
                    # Extract coordinates from Google Maps link if available
                    lat, lon = 0.0, 0.0
                    if 'gmaps_link' in row and pd.notna(row.get('gmaps_link')):
                        lat, lon = self.extract_coordinates_from_gmaps_link(row.get('gmaps_link'))
                    
                    # Skip if coordinates are invalid (0,0)
                    if lat == 0.0 and lon == 0.0:
                        skipped += 1
                        self.stats['total_skipped'] += 1
                        logger.debug(f"Skipping {row.get('name')} - invalid coordinates")
                        continue
                    
                    # Check if hospital already exists (by name and address)
                    existing = self.db.query(Hospital).filter(
                        Hospital.name == str(row.get('name')),
                        Hospital.address == str(row.get('address'))
                    ).first()
                    
                    if existing:
                        skipped += 1
                        self.stats['total_skipped'] += 1
                        logger.debug(f"Hospital {row.get('name')} already exists, skipping")
                        continue
                    
                    # Determine facility type and class
                    facility_type = str(row.get('type', 'Rumah Sakit'))
                    facility_class = 'C'  # Default class
                    
                    # Estimate bed capacity based on facility type
                    if 'rumah sakit' in facility_type.lower():
                        total_beds = 100
                        if 'tipe a' in facility_type.lower() or 'kelas a' in facility_type.lower():
                            total_beds = 200
                            facility_class = 'A'
                        elif 'tipe b' in facility_type.lower() or 'kelas b' in facility_type.lower():
                            total_beds = 150
                            facility_class = 'B'
                        elif 'tipe d' in facility_type.lower() or 'kelas d' in facility_type.lower():
                            total_beds = 50
                            facility_class = 'D'
                    elif 'puskesmas' in facility_type.lower():
                        total_beds = 20
                        facility_class = 'Puskesmas'
                    elif 'klinik' in facility_type.lower():
                        total_beds = 10
                        facility_class = 'Klinik'
                    else:
                        total_beds = 50
                    
                    # Create hospital record
                    hospital = Hospital(
                        name=str(row.get('name')),
                        address=str(row.get('address')),
                        latitude=lat,
                        longitude=lon,
                        type=facility_type,
                        class_=facility_class,
                        total_beds=total_beds,
                        available_beds=int(total_beds * 0.5),  # Assume 50% available
                        phone=None,
                        emergency_available=True
                    )
                    
                    self.db.add(hospital)
                    count += 1
                    self.stats['total_inserted'] += 1
                    
                    if count % 100 == 0:
                        self.db.commit()
                        logger.info(f"Progress: {count} hospitals loaded...")
                    
                except Exception as e:
                    self.stats['errors'].append(f"Row {idx}: {str(e)}")
                    logger.error(f"Error processing row {idx}: {str(e)}")
                    continue
            
            self.db.commit()
            logger.info(f"✅ Successfully loaded {count} hospitals from BPJS Faskes CSV")
            logger.info(f"   Skipped: {skipped} records")
            return count
            
        except Exception as e:
            logger.error(f"❌ Error loading CSV: {str(e)}")
            self.db.rollback()
            return 0
    
    def load_bed_ratio_csv(self, csv_path: str, province: Optional[str] = None) -> int:
        """
        Load hospital bed ratio data from CSV
        Updates existing hospitals with bed information
        
        Args:
            csv_path: Path to CSV file
            province: Filter by province name (optional)
            
        Returns:
            Number of hospitals updated
        """
        try:
            logger.info(f"Loading bed ratio data from {csv_path}")
            df = pd.read_csv(csv_path, encoding='utf-8')
            
            # Standardize column names
            df.columns = df.columns.str.lower().str.strip()
            
            # Filter by province if specified
            if province and 'provinsi' in df.columns:
                df = df[df['provinsi'].str.contains(province, case=False, na=False)]
            
            count = 0
            for _, row in df.iterrows():
                try:
                    # Try to match hospital by name
                    hospital_name = row.get('nama_rs') or row.get('rumah_sakit') or row.get('name')
                    if pd.isna(hospital_name):
                        continue
                    
                    # Find hospital in database
                    hospital = self.db.query(Hospital).filter(
                        Hospital.name.contains(hospital_name)
                    ).first()
                    
                    if hospital:
                        # Update bed information
                        total_beds = row.get('jumlah_bed') or row.get('total_beds') or row.get('tempat_tidur')
                        if pd.notna(total_beds):
                            hospital.total_beds = int(total_beds)
                            hospital.available_beds = int(total_beds * 0.5)  # Assume 50% available
                            count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing bed ratio row: {str(e)}")
                    continue
            
            self.db.commit()
            logger.info(f"Successfully updated {count} hospitals with bed ratio data")
            return count
            
        except Exception as e:
            logger.error(f"Error loading bed ratio CSV: {str(e)}")
            self.db.rollback()
            return 0
    
    def get_stats(self) -> Dict:
        """
        Get loading statistics
        Returns:
            Dictionary with statistics
        """
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset statistics counters"""
        self.stats = {
            'total_processed': 0,
            'total_inserted': 0,
            'total_updated': 0,
            'total_skipped': 0,
            'errors': []
        }
    
    def load_from_directory(self, directory_path: str, pattern: str = "*.csv") -> Dict[str, int]:
        """
        Load all CSV files from a directory
        
        Args:
            directory_path: Path to directory containing CSV files
            pattern: File pattern to match (default: *.csv)
            
        Returns:
            Dictionary with filename and count of records loaded
        """
        import glob
        
        results = {}
        csv_files = glob.glob(os.path.join(directory_path, pattern))
        
        logger.info(f"Found {len(csv_files)} CSV files in {directory_path}")
        
        for csv_file in csv_files:
            filename = os.path.basename(csv_file)
            logger.info(f"Processing {filename}")
            
            # Try to detect file type and load accordingly
            if 'faskes' in filename.lower() or 'bpjs' in filename.lower():
                count = self.load_bpjs_faskes_csv(csv_file)
            elif 'bed' in filename.lower() or 'ratio' in filename.lower():
                count = self.load_bed_ratio_csv(csv_file)
            else:
                # Default to BPJS faskes format
                count = self.load_bpjs_faskes_csv(csv_file)
            
            results[filename] = count
        
        return results
