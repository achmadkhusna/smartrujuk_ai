"""
Integration Tests for Data Pipeline
Tests the complete data loading and training pipeline
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import modules to test
from database.dataset_downloader import DatasetDownloader
from src.csv_loader import CSVDataLoader


class TestDatasetDownloader(unittest.TestCase):
    """Test DatasetDownloader functionality"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.test_dir = Path('/tmp/test_smartrujuk_data')
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.downloader = DatasetDownloader(data_dir=str(self.test_dir))
    
    def tearDown(self):
        """Cleanup test fixtures"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test downloader initialization"""
        self.assertIsNotNone(self.downloader)
        self.assertTrue(self.downloader.data_dir.exists())
        self.assertEqual(len(self.downloader.datasets), 2)
    
    def test_dataset_info(self):
        """Test dataset information structure"""
        self.assertIn('bpjs_faskes', self.downloader.datasets)
        self.assertIn('bed_ratio', self.downloader.datasets)
        
        # Check BPJS Faskes info
        bpjs = self.downloader.datasets['bpjs_faskes']
        self.assertIn('name', bpjs)
        self.assertIn('source', bpjs)
        self.assertIn('filename', bpjs)
        
        # Check Bed Ratio info
        bed = self.downloader.datasets['bed_ratio']
        self.assertIn('name', bed)
        self.assertIn('files', bed)
        self.assertIsInstance(bed['files'], list)
    
    def test_check_kaggle_setup(self):
        """Test Kaggle API setup check"""
        # This may fail if Kaggle is not configured, which is expected
        result = self.downloader.check_kaggle_setup()
        self.assertIsInstance(result, bool)
    
    def test_list_available_files(self):
        """Test listing available files"""
        # Create test CSV file
        test_csv = self.test_dir / 'test_faskes.csv'
        test_csv.write_text('name,address\nTest Hospital,Test Address')
        
        available = self.downloader.list_available_files()
        
        self.assertIsInstance(available, dict)
        self.assertIn('bpjs_faskes', available)
        self.assertIn('bed_ratio', available)
        self.assertIn('other', available)


class TestCSVLoader(unittest.TestCase):
    """Test CSV Loader functionality"""
    
    def setUp(self):
        """Setup test fixtures"""
        # Mock database session
        self.mock_db = Mock()
        self.loader = CSVDataLoader(self.mock_db)
    
    def test_initialization(self):
        """Test loader initialization"""
        self.assertIsNotNone(self.loader)
        self.assertIsNotNone(self.loader.stats)
        self.assertEqual(self.loader.stats['total_processed'], 0)
    
    def test_coordinate_extraction(self):
        """Test GPS coordinate extraction from Google Maps links"""
        test_cases = [
            ('http://maps.google.co.id/?q=-6.1744,106.8294', (-6.1744, 106.8294)),
            ('http://maps.google.co.id/?q=4.488058,97.947963', (4.488058, 97.947963)),
            ('http://maps.google.co.id/?q=-7.2687,112.7521', (-7.2687, 112.7521)),
            ('http://maps.google.co.id/?q=0.0,0.0', (0.0, 0.0)),  # Invalid
            ('invalid_link', (0.0, 0.0)),  # Invalid
            ('', (0.0, 0.0)),  # Empty
        ]
        
        for link, expected in test_cases:
            result = self.loader.extract_coordinates_from_gmaps_link(link)
            self.assertEqual(result, expected, f"Failed for link: {link}")
    
    def test_coordinate_validation(self):
        """Test coordinate validation for Indonesia bounds"""
        # Valid Indonesia coordinates
        valid_coords = [
            (-6.1744, 106.8294),   # Jakarta
            (3.5952, 98.6722),     # Medan
            (-7.7956, 110.3695),   # Yogyakarta
            (-0.9471, 100.4172),   # Padang
        ]
        
        for lat, lon in valid_coords:
            link = f'http://maps.google.co.id/?q={lat},{lon}'
            result = self.loader.extract_coordinates_from_gmaps_link(link)
            self.assertNotEqual(result, (0.0, 0.0), f"Valid coords {lat},{lon} rejected")
    
    def test_stats_tracking(self):
        """Test statistics tracking"""
        stats = self.loader.get_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_processed', stats)
        self.assertIn('total_inserted', stats)
        self.assertIn('total_skipped', stats)
        self.assertIn('errors', stats)
    
    def test_stats_reset(self):
        """Test statistics reset"""
        self.loader.stats['total_processed'] = 10
        self.loader.stats['total_inserted'] = 5
        
        self.loader.reset_stats()
        
        self.assertEqual(self.loader.stats['total_processed'], 0)
        self.assertEqual(self.loader.stats['total_inserted'], 0)


class TestDataPipelineIntegration(unittest.TestCase):
    """Integration tests for complete data pipeline"""
    
    def test_sample_csv_processing(self):
        """Test processing of sample CSV data"""
        import pandas as pd
        import tempfile
        
        # Create sample data
        sample_data = [
            {
                'NamaFaskes': 'RS Test Jakarta',
                'AlamatFaskes': 'Jl. Test No.1, Jakarta',
                'LatLongFaskes': 'http://maps.google.co.id/?q=-6.1744,106.8294',
                'TipeFaskes': 'Rumah Sakit',
                'Provinsi': 'DKI Jakarta'
            }
        ]
        
        df = pd.DataFrame(sample_data)
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            csv_path = f.name
        
        try:
            # Test that file exists and is readable
            self.assertTrue(os.path.exists(csv_path))
            
            # Test reading CSV
            df_read = pd.read_csv(csv_path)
            self.assertEqual(len(df_read), 1)
            self.assertIn('NamaFaskes', df_read.columns)
            
            # Test coordinate extraction from the data
            loader = CSVDataLoader(None)
            coords = loader.extract_coordinates_from_gmaps_link(
                df_read['LatLongFaskes'].iloc[0]
            )
            self.assertNotEqual(coords, (0.0, 0.0))
            
        finally:
            # Cleanup
            if os.path.exists(csv_path):
                os.unlink(csv_path)
    
    def test_multiple_csv_handling(self):
        """Test handling multiple CSV files"""
        import tempfile
        import pandas as pd
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create multiple test CSV files
            for i in range(3):
                df = pd.DataFrame([{
                    'NamaFaskes': f'Hospital {i}',
                    'AlamatFaskes': f'Address {i}',
                    'LatLongFaskes': f'http://maps.google.co.id/?q=-6.{i},106.{i}',
                }])
                df.to_csv(f'{temp_dir}/test_{i}.csv', index=False)
            
            # List files
            csv_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]
            self.assertEqual(len(csv_files), 3)
            
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)


class TestDataValidation(unittest.TestCase):
    """Test data validation functions"""
    
    def test_indonesia_bounds_validation(self):
        """Test Indonesia geographic bounds validation"""
        # Valid coordinates should be within:
        # Latitude: -11° to 6°
        # Longitude: 95° to 141°
        
        valid_cases = [
            (-6.1744, 106.8294),   # Jakarta
            (-10.0, 96.0),         # Southern border
            (5.0, 140.0),          # Eastern border
        ]
        
        invalid_cases = [
            (-12.0, 106.0),        # Too far south
            (7.0, 106.0),          # Too far north
            (-6.0, 94.0),          # Too far west
            (-6.0, 142.0),         # Too far east
        ]
        
        for lat, lon in valid_cases:
            # Check if within bounds
            valid = (-11 <= lat <= 6) and (95 <= lon <= 141)
            self.assertTrue(valid, f"Valid coords {lat},{lon} rejected")
        
        for lat, lon in invalid_cases:
            # Check if outside bounds
            invalid = not ((-11 <= lat <= 6) and (95 <= lon <= 141))
            self.assertTrue(invalid, f"Invalid coords {lat},{lon} accepted")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestDatasetDownloader))
    suite.addTests(loader.loadTestsFromTestCase(TestCSVLoader))
    suite.addTests(loader.loadTestsFromTestCase(TestDataPipelineIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
