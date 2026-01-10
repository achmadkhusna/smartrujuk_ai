# SmartRujuk+ Data Loading Guide 📂

**UPDATED**: Panduan ini telah diperbarui dengan support untuk 2 dataset Kaggle lengkap!

> **📚 New Comprehensive Guides Available**:
> - [DATASET_GUIDE.md](DATASET_GUIDE.md) - Panduan lengkap dataset Kaggle (BPJS Faskes & Bed Ratio)
> - [TRAINING_GUIDE.md](TRAINING_GUIDE.md) - Panduan training ML models
> - [README.md](README.md) - Main documentation dengan quick start

This guide explains how to load hospital data from CSV files into the SmartRujuk+ system.

## 🚀 Quick Start: Complete Data Pipeline

**NEW**: Sekarang ada pipeline lengkap untuk download dan load semua dataset!

```bash
# Option 1: Download + Load + Train dalam satu command
python database/load_all_datasets.py --download-first

# Option 2: Load dataset yang sudah didownload manual
python database/load_all_datasets.py

# Option 3: Load tanpa training ML models
python database/load_all_datasets.py --no-train
```

**Hasil yang Diharapkan**:
- 1,500-4,000 hospitals loaded
- Training data generated
- ML models trained
- Ready to use!

Lihat [DATASET_GUIDE.md](DATASET_GUIDE.md) untuk detail lengkap.

## Features

### 1. CSV Data Loading Module

The CSV data loader supports:
- Multiple CSV file formats
- Province-specific filtering
- Auto-detection of file types
- Batch loading from directories
- Support for various column naming conventions
- **NEW**: ZIP archives with multiple CSV files (v2.1+)

### 2. Supported CSV Formats

#### BPJS Faskes Format
Expected columns (flexible naming):
- `nama`, `nama_rs`, `nama_rumah_sakit` → Hospital name
- `alamat`, `alamat_rs` → Address
- `lat`, `latitude` → Latitude
- `lon`, `lng`, `longitude` → Longitude
- `tipe`, `type`, `jenis` → Hospital type
- `kelas`, `class` → Hospital class (A, B, C, D)
- `telepon`, `telp`, `phone` → Phone number
- `tempat_tidur`, `jumlah_bed`, `total_beds` → Number of beds
- `provinsi`, `province` → Province name

#### Bed Ratio Format
Expected columns:
- `nama_rs`, `rumah_sakit`, `name` → Hospital name
- `jumlah_bed`, `total_beds`, `tempat_tidur` → Number of beds
- `provinsi`, `province` → Province name

### 3. API Configuration Storage

API credentials are automatically extracted from `soal.txt` and stored in the database:
- SATUSEHAT API credentials (Organization ID, Client ID, Client Secret)
- Google Maps API key

This allows for centralized credential management and easier updates.

### 4. Offline Fallback Mechanisms

#### Google Maps API Fallback
When the Google Maps API is unavailable or credentials are missing:
- Automatic offline mode activation
- Built-in geocoding for major Indonesian cities
- Haversine formula for distance calculations (always available)
- Seamless fallback without system interruption

Supported offline locations:
- Jakarta (all regions: Pusat, Selatan, Timur, Barat, Utara)
- Bekasi, Tangerang, Depok, Bogor
- Bandung, Surabaya, Medan, Semarang
- Yogyakarta, Makassar, Palembang, Malang, Solo, Batam

#### SATUSEHAT API Fallback
When the SATUSEHAT API is unavailable:
- Sample organization data provided
- Sample location data for testing
- Automatic detection and fallback
- No disruption to system operation

## Usage

### Initial Setup

1. **Initialize Database** (includes API config loading):
```bash
python database/init_db.py
```

This will:
- Create all database tables
- Load API credentials from soal.txt
- Add sample hospital data
- Add sample patient data
- Generate historical data for predictions

### Loading CSV Data

#### 1. Create Sample CSV
```bash
python database/load_csv_data.py
```
(Running without arguments creates a sample CSV file)

#### 2. Load Single CSV File
```bash
python database/load_csv_data.py --file path/to/hospitals.csv
```

#### 3. Load ZIP Archives (NEW in v2.1)
The system now supports ZIP files containing multiple CSV files:

```bash
# Load ZIP file with multiple CSVs
python database/load_csv_data.py --file path/to/dataset.zip
```

**Features:**
- ✅ Automatically extracts all CSV files from ZIP
- ✅ Processes each CSV file individually
- ✅ Skips files that don't match expected schema
- ✅ Cleans up temporary files automatically
- ✅ Works with "Dataset Rasio Bed to Population Faskes II.zip" from Kaggle

**Example with Kaggle Dataset:**
```bash
# This now works without manual extraction!
python database/load_all_datasets.py --download-first
```

The loader will:
1. Detect ZIP file by extension
2. Extract all CSV files to temporary directory
3. Process each CSV file (e.g., data_rs.csv, bed_ratio.csv)
4. Skip non-relevant files (e.g., population data)
5. Clean up temporary files

#### 4. Load All CSV Files from Directory
```bash
python database/load_csv_data.py --dir path/to/csv_folder
```

#### 4. Filter by Province
```bash
python database/load_csv_data.py --file hospitals.csv --province "DKI Jakarta"
```

#### 5. Specify CSV Type
```bash
python database/load_csv_data.py --file data.csv --type faskes
```

Options for `--type`:
- `auto` (default): Auto-detect based on filename
- `faskes`: BPJS Faskes format
- `bed_ratio`: Bed ratio format

### Loading API Configuration

API credentials are automatically loaded during database initialization. To reload manually:

```bash
python database/load_api_config.py
```

This extracts credentials from `soal.txt` and stores them in the `api_config` table.

## Data Directory Structure

Recommended structure for organizing CSV files:

```
data/
├── provinces/
│   ├── jakarta/
│   │   ├── hospitals_jakarta.csv
│   │   └── bed_ratio_jakarta.csv
│   ├── jawa_barat/
│   │   ├── hospitals_bandung.csv
│   │   └── bed_ratio_jabar.csv
│   └── jawa_timur/
│       ├── hospitals_surabaya.csv
│       └── bed_ratio_jatim.csv
└── national/
    ├── bpjs_faskes_all.csv
    └── bed_ratio_national.csv
```

### Loading Multiple Provinces

```bash
# Load all provinces
python database/load_csv_data.py --dir data/provinces

# Load specific province
python database/load_csv_data.py --dir data/provinces/jakarta
```

## CSV File Preparation

### Example BPJS Faskes CSV

```csv
name,address,latitude,longitude,type,class,total_beds,phone,province
RSUP Dr. Cipto Mangunkusumo,Jl. Diponegoro No.71,-6.1862,106.8311,Rumah Sakit Umum,A,250,021-3142323,DKI Jakarta
RS Fatmawati,Jl. RS Fatmawati No.4,-6.2921,106.7970,Rumah Sakit Umum,A,200,021-7501524,DKI Jakarta
```

### Example Bed Ratio CSV

```csv
nama_rs,provinsi,jumlah_bed
RSUP Dr. Cipto Mangunkusumo,DKI Jakarta,250
RS Fatmawati,DKI Jakarta,200
```

## Data Validation

The loader automatically:
- Skips records with empty names or addresses
- Validates coordinates (skips 0,0 coordinates)
- Checks for duplicate hospitals
- Handles missing or invalid data gracefully
- Logs all operations for debugging

## Troubleshooting

### Common Issues

#### 1. CSV Encoding Error
```bash
# If you get encoding errors, try:
# - Save CSV as UTF-8 encoding
# - Use Excel "CSV UTF-8" format when exporting
```

#### 2. Column Not Found
```
Error: Required column 'name' not found in CSV
```
**Solution**: Check your CSV headers and ensure they match one of the supported naming conventions.

#### 3. Invalid Coordinates
```
Warning: Skipping Hospital X - invalid coordinates
```
**Solution**: Ensure latitude and longitude are valid numbers. The system will skip hospitals with 0,0 coordinates.

#### 4. Duplicate Hospitals
```
Hospital X already exists, skipping
```
**Solution**: This is normal. The loader prevents duplicate entries based on name and address.

### Offline Mode

The system automatically enters offline mode when:
- API keys are not configured
- API endpoints are unreachable
- Network connectivity issues occur

In offline mode:
- Geocoding uses built-in location database
- SATUSEHAT data uses sample records
- Distance calculations still work (using Haversine formula)
- All core features remain functional

## Database Schema Updates

The system now includes an `api_config` table:

```sql
CREATE TABLE api_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL UNIQUE,
    config_key VARCHAR(255) NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

This stores:
- Service name (e.g., "SATUSEHAT", "GOOGLE_MAPS")
- Configuration key (e.g., "credentials", "api_key")
- Configuration value (encrypted in production)
- Description and active status

## Integration with Existing System

The CSV loader integrates seamlessly with:
- Existing database models
- Hospital capacity tracking
- Wait time predictions
- Geolocation features
- AI Agent recommendations

After loading CSV data, the system will:
- Use new hospital data in search results
- Include them in distance calculations
- Apply predictive models
- Display them on interactive maps

## Performance Tips

1. **Batch Loading**: Use `--dir` to load multiple files at once
2. **Province Filtering**: Use `--province` to reduce processing time
3. **Large Files**: The loader processes records one at a time, so memory usage is minimal
4. **Incremental Updates**: The loader skips existing hospitals, so you can re-run safely

## Best Practices

1. **Regular Backups**: Backup your database before bulk loading
2. **Test Data**: Test with sample CSV first
3. **Validation**: Review loaded data in the web interface
4. **Updates**: For updates, it's better to modify records directly than reload
5. **Logging**: Check logs for any skipped or failed records

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify CSV format matches examples
3. Test with sample CSV first
4. Review the console output for warnings

## Next Steps

After loading CSV data:
1. Verify data in web interface: `streamlit run app.py`
2. Check hospital locations on the map
3. Test search and recommendation features
4. Review capacity and availability information
5. Run predictions to ensure models work with new data
