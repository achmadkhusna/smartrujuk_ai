"""
Dataset Downloader Module
Downloads and prepares datasets from Kaggle sources for SmartRujuk+ system
"""
import os
import sys
import logging
import requests
import zipfile
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DatasetDownloader:
    """
    Download and prepare datasets from various sources
    Supports:
    - BPJS Faskes Indonesia dataset (Kaggle)
    - Bed to Population Ratio dataset (Kaggle)
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize dataset downloader
        Args:
            data_dir: Directory to store downloaded datasets
        """
        if data_dir is None:
            # Use data directory in project root
            project_root = Path(__file__).parent.parent
            data_dir = project_root / "data" / "kaggle_datasets"
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.datasets = {
            'bpjs_faskes': {
                'name': 'List Faskes BPJS Indonesia',
                'source': 'https://www.kaggle.com/datasets/israhabibi/list-faskes-bpjs-indonesia',
                'filename': 'Data Faskes BPJS 2019.csv',
                'description': 'Daftar fasilitas kesehatan yang bekerja sama dengan BPJS'
            },
            'bed_ratio': {
                'name': 'Dataset Rasio Bed to Population Faskes II',
                'source': 'https://www.kaggle.com/datasets/yafethtb/dataset-rasio-bed-to-population-faskes-ii',
                'files': [
                    'Rasio Bed To Population Rumah Sakit Kelas C dan D tiap Provinsi Di Indonesia.csv',
                    'data_rs.csv',
                    'Jumlah Penduduk Hasil Proyeksi Menurut Provinsi dan Jenis Kelamin.xlsx'
                ],
                'description': 'Dataset rasio tempat tidur rumah sakit per populasi'
            }
        }
        
        logger.info(f"Dataset downloader initialized. Data directory: {self.data_dir}")
    
    def check_kaggle_setup(self) -> bool:
        """
        Check if Kaggle API is properly configured
        Returns:
            True if kaggle is available, False otherwise
        """
        try:
            import kaggle
            # Try to authenticate
            from kaggle.api.kaggle_api_extended import KaggleApi
            api = KaggleApi()
            api.authenticate()
            logger.info("✅ Kaggle API is configured and authenticated")
            return True
        except ImportError:
            logger.warning("⚠️  Kaggle package not installed. Install with: pip install kaggle")
            return False
        except Exception as e:
            logger.warning(f"⚠️  Kaggle API not configured: {str(e)}")
            logger.info("To configure Kaggle API:")
            logger.info("1. Go to https://www.kaggle.com/settings/account")
            logger.info("2. Create API token (download kaggle.json)")
            logger.info("3. Place kaggle.json in ~/.kaggle/ (Linux/Mac) or C:\\Users\\<username>\\.kaggle\\ (Windows)")
            return False
    
    def download_bpjs_faskes(self, force: bool = False) -> Optional[str]:
        """
        Download BPJS Faskes dataset from Kaggle
        Args:
            force: Force re-download even if file exists
        Returns:
            Path to downloaded CSV file or None if failed
        """
        dataset_info = self.datasets['bpjs_faskes']
        csv_path = self.data_dir / dataset_info['filename']
        
        # Check if already exists
        if csv_path.exists() and not force:
            logger.info(f"✅ Dataset already exists: {csv_path}")
            return str(csv_path)
        
        # Check Kaggle API
        if not self.check_kaggle_setup():
            logger.error("Cannot download without Kaggle API configured")
            logger.info("\n📝 Manual download instructions:")
            logger.info(f"1. Visit: {dataset_info['source']}")
            logger.info(f"2. Download the dataset")
            logger.info(f"3. Extract '{dataset_info['filename']}' to: {self.data_dir}")
            return None
        
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            api = KaggleApi()
            api.authenticate()
            
            logger.info("Downloading BPJS Faskes dataset...")
            api.dataset_download_files(
                'israhabibi/list-faskes-bpjs-indonesia',
                path=str(self.data_dir),
                unzip=True
            )
            
            logger.info(f"✅ Downloaded: {csv_path}")
            return str(csv_path)
            
        except Exception as e:
            logger.error(f"Error downloading dataset: {str(e)}")
            return None
    
    def download_bed_ratio(self, force: bool = False) -> List[str]:
        """
        Download Bed to Population Ratio dataset from Kaggle
        Args:
            force: Force re-download even if files exist
        Returns:
            List of paths to downloaded files
        """
        dataset_info = self.datasets['bed_ratio']
        downloaded_files = []
        
        # Check if files already exist
        all_exist = True
        for filename in dataset_info['files']:
            file_path = self.data_dir / filename
            if file_path.exists():
                downloaded_files.append(str(file_path))
            else:
                all_exist = False
        
        if all_exist and not force:
            logger.info(f"✅ All bed ratio dataset files already exist")
            return downloaded_files
        
        # Check Kaggle API
        if not self.check_kaggle_setup():
            logger.error("Cannot download without Kaggle API configured")
            logger.info("\n📝 Manual download instructions:")
            logger.info(f"1. Visit: {dataset_info['source']}")
            logger.info(f"2. Download the dataset")
            logger.info(f"3. Extract all files to: {self.data_dir}")
            return downloaded_files if downloaded_files else []
        
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            api = KaggleApi()
            api.authenticate()
            
            logger.info("Downloading Bed to Population Ratio dataset...")
            api.dataset_download_files(
                'yafethtb/dataset-rasio-bed-to-population-faskes-ii',
                path=str(self.data_dir),
                unzip=True
            )
            
            # Return paths to all downloaded files
            downloaded_files = []
            for filename in dataset_info['files']:
                file_path = self.data_dir / filename
                if file_path.exists():
                    downloaded_files.append(str(file_path))
            
            logger.info(f"✅ Downloaded {len(downloaded_files)} files")
            return downloaded_files
            
        except Exception as e:
            logger.error(f"Error downloading dataset: {str(e)}")
            return downloaded_files if downloaded_files else []
    
    def download_all(self, force: bool = False) -> Dict[str, List[str]]:
        """
        Download all datasets
        Args:
            force: Force re-download even if files exist
        Returns:
            Dictionary with dataset names and paths to downloaded files
        """
        results = {}
        
        logger.info("=" * 60)
        logger.info("SmartRujuk+ Dataset Downloader")
        logger.info("=" * 60)
        
        # Download BPJS Faskes
        logger.info("\n[1/2] Downloading BPJS Faskes dataset...")
        faskes_path = self.download_bpjs_faskes(force)
        if faskes_path:
            results['bpjs_faskes'] = [faskes_path]
        else:
            results['bpjs_faskes'] = []
        
        # Download Bed Ratio
        logger.info("\n[2/2] Downloading Bed Ratio dataset...")
        bed_ratio_paths = self.download_bed_ratio(force)
        results['bed_ratio'] = bed_ratio_paths
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("Download Summary:")
        logger.info("=" * 60)
        total_files = sum(len(files) for files in results.values())
        logger.info(f"Total files downloaded/available: {total_files}")
        
        for dataset_name, files in results.items():
            logger.info(f"\n{dataset_name}:")
            if files:
                for f in files:
                    logger.info(f"  ✅ {os.path.basename(f)}")
            else:
                logger.info(f"  ⚠️  No files available")
        
        logger.info("\n" + "=" * 60)
        logger.info("Next steps:")
        logger.info("=" * 60)
        logger.info("Run the data loader to import datasets into database:")
        logger.info("  python database/load_all_datasets.py")
        logger.info("=" * 60)
        
        return results
    
    def list_available_files(self) -> Dict[str, List[str]]:
        """
        List all available dataset files in the data directory
        Returns:
            Dictionary with file categories and paths
        """
        available = {
            'bpjs_faskes': [],
            'bed_ratio': [],
            'other': []
        }
        
        if not self.data_dir.exists():
            return available
        
        for file_path in self.data_dir.glob('*'):
            if not file_path.is_file():
                continue
            
            filename = file_path.name.lower()
            
            if 'faskes' in filename or 'bpjs' in filename:
                available['bpjs_faskes'].append(str(file_path))
            elif 'bed' in filename or 'ratio' in filename or 'populasi' in filename:
                available['bed_ratio'].append(str(file_path))
            elif filename.endswith(('.csv', '.xlsx', '.xls')):
                available['other'].append(str(file_path))
        
        return available
    
    def show_dataset_info(self):
        """Display information about available datasets"""
        logger.info("\n" + "=" * 60)
        logger.info("SmartRujuk+ Dataset Information")
        logger.info("=" * 60)
        
        for key, info in self.datasets.items():
            logger.info(f"\n📊 {info['name']}")
            logger.info(f"   Source: {info['source']}")
            logger.info(f"   Description: {info['description']}")
            
            if key == 'bpjs_faskes':
                file_path = self.data_dir / info['filename']
                if file_path.exists():
                    logger.info(f"   Status: ✅ Downloaded")
                    logger.info(f"   Location: {file_path}")
                else:
                    logger.info(f"   Status: ⚠️  Not downloaded")
            else:
                files_exist = sum(1 for f in info['files'] if (self.data_dir / f).exists())
                logger.info(f"   Status: {files_exist}/{len(info['files'])} files available")
        
        logger.info("\n" + "=" * 60)


def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Download datasets for SmartRujuk+')
    parser.add_argument('--force', action='store_true', help='Force re-download existing files')
    parser.add_argument('--info', action='store_true', help='Show dataset information')
    parser.add_argument('--list', action='store_true', help='List available files')
    parser.add_argument('--data-dir', type=str, help='Custom data directory')
    
    args = parser.parse_args()
    
    downloader = DatasetDownloader(data_dir=args.data_dir)
    
    if args.info:
        downloader.show_dataset_info()
    elif args.list:
        available = downloader.list_available_files()
        logger.info("\n📁 Available files:")
        for category, files in available.items():
            if files:
                logger.info(f"\n{category}:")
                for f in files:
                    logger.info(f"  - {os.path.basename(f)}")
    else:
        # Download all datasets
        downloader.download_all(force=args.force)


if __name__ == "__main__":
    main()
