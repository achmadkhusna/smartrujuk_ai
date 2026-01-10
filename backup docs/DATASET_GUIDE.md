# Dataset Guide - SmartRujuk+ AI Agent 📊

Panduan lengkap untuk mengelola dan memproses dataset dalam sistem SmartRujuk+.

## 📋 Daftar Isi

1. [Sumber Dataset](#sumber-dataset)
2. [Download Dataset](#download-dataset)
3. [Format Dataset](#format-dataset)
4. [Loading Data ke Database](#loading-data-ke-database)
5. [Validasi Data](#validasi-data)
6. [Training ML Models](#training-ml-models)
7. [Troubleshooting](#troubleshooting)

## 📦 Sumber Dataset

SmartRujuk+ menggunakan 2 sumber dataset utama dari Kaggle:

### 1. BPJS Faskes Indonesia Dataset

**Source**: [israhabibi/list-faskes-bpjs-indonesia](https://www.kaggle.com/datasets/israhabibi/list-faskes-bpjs-indonesia)

**Deskripsi**: 
- Daftar lengkap fasilitas kesehatan yang bekerja sama dengan BPJS
- Mencakup Rumah Sakit, Puskesmas, dan Klinik di seluruh Indonesia
- Data tahun 2019

**File**: `Data Faskes BPJS 2019.csv`

**Kolom Penting**:
- `NoLink`: Nomor urut
- `Provinsi`: Nama provinsi
- `KotaKab`: Nama kota/kabupaten
- `TipeFaskes`: Jenis fasilitas (Rumah Sakit, Puskesmas, Klinik, dll)
- `KodeFaskes`: Kode unik faskes
- `NamaFaskes`: Nama lengkap faskes
- `LatLongFaskes`: Link Google Maps dengan koordinat
- `AlamatFaskes`: Alamat lengkap

**Total Records**: ~28,000+ fasilitas kesehatan

**Statistik**:
- Rumah Sakit: ~4,000
- Puskesmas: ~10,000
- Klinik Pratama: ~6,500
- Lainnya: ~7,500

### 2. Bed to Population Ratio Dataset

**Source**: [yafethtb/dataset-rasio-bed-to-population-faskes-ii](https://www.kaggle.com/datasets/yafethtb/dataset-rasio-bed-to-population-faskes-ii)

**Deskripsi**:
- Dataset rasio tempat tidur rumah sakit per populasi
- Fokus pada RS Kelas C dan D (Faskes Tingkat II)
- Data tahun 2020

**Files**:
1. `Rasio Bed To Population Rumah Sakit Kelas C dan D tiap Provinsi Di Indonesia.csv`
2. `data_rs.csv`
3. `Jumlah Penduduk Hasil Proyeksi Menurut Provinsi dan Jenis Kelamin.xlsx`

**Kolom Penting**:
- Nama RS/Provinsi
- Jumlah tempat tidur
- Populasi penduduk
- Rasio bed-to-population

## 🔽 Download Dataset

### Metode 1: Menggunakan Script Downloader (Otomatis)

**Prerequisites**:
```bash
pip install kaggle
```

**Setup Kaggle API**:
1. Login ke Kaggle: https://www.kaggle.com
2. Go to Account Settings: https://www.kaggle.com/settings/account
3. Klik "Create New API Token"
4. Download `kaggle.json`
5. Letakkan di:
   - Linux/Mac: `~/.kaggle/kaggle.json`
   - Windows: `C:\Users\<username>\.kaggle\kaggle.json`

**Download dengan Script**:
```bash
# Download semua dataset
python database/dataset_downloader.py

# Download dengan force re-download
python database/dataset_downloader.py --force

# Lihat info dataset
python database/dataset_downloader.py --info

# List file yang tersedia
python database/dataset_downloader.py --list
```

### Metode 2: Manual Download

**Jika Kaggle API tidak tersedia**:

1. **Download BPJS Faskes**:
   - Kunjungi: https://www.kaggle.com/datasets/israhabibi/list-faskes-bpjs-indonesia
   - Klik "Download"
   - Extract `Data Faskes BPJS 2019.csv`
   - Letakkan di: `data/kaggle_datasets/`

2. **Download Bed Ratio**:
   - Kunjungi: https://www.kaggle.com/datasets/yafethtb/dataset-rasio-bed-to-population-faskes-ii
   - Klik "Download"
   - Extract semua file CSV dan XLSX
   - Letakkan di: `data/kaggle_datasets/`

## 📝 Format Dataset

### BPJS Faskes CSV Format

```csv
NoLink,Provinsi,KotaKab,Link,TipeFaskes,No,KodeFaskes,NamaFaskes,LatLongFaskes,AlamatFaskes
0,Nanggroe Aceh Darussalam,Kode Faskes...,https://lovia.life/...,Rumah Sakit,1,0001R001,RSU Cut Nyak Dhien,http://maps.google.co.id/?q=4.488058,97.947963,Jl. Tm Bahrum No. 1 Langsa
```

**Karakteristik**:
- Encoding: UTF-8, Latin-1, atau CP1252
- Delimiter: Koma (,)
- Header: Ya
- Koordinat dalam Google Maps link format

### Bed Ratio CSV Format

```csv
Provinsi,Nama_RS,Kelas,Jumlah_Bed,Populasi,Rasio
DKI Jakarta,RSUD Pasar Rebo,C,200,10000000,0.02
```

**Karakteristik**:
- Encoding: UTF-8
- Delimiter: Koma (,)
- Header: Ya
- Numeric values untuk bed count dan population

## 🔄 Loading Data ke Database

### Pipeline Lengkap (Recommended)

**Jalankan pipeline lengkap** yang akan:
1. Setup database
2. Load BPJS Faskes dataset
3. Load Bed Ratio dataset
4. Generate training data
5. Train ML models

```bash
python database/load_all_datasets.py
```

**Dengan download otomatis**:
```bash
python database/load_all_datasets.py --download-first
```

**Skip training**:
```bash
python database/load_all_datasets.py --no-train
```

**Skip synthetic data generation**:
```bash
python database/load_all_datasets.py --no-training-data
```

### Load Individual Files

**Load single CSV file**:
```bash
python database/load_csv_data.py --file "data/kaggle_datasets/Data Faskes BPJS 2019.csv"
```

**Load dengan filter provinsi**:
```bash
python database/load_csv_data.py --file "data/kaggle_datasets/Data Faskes BPJS 2019.csv" --province "DKI Jakarta"
```

**Load semua CSV dari directory**:
```bash
python database/load_csv_data.py --dir data/kaggle_datasets
```

**Specify file type**:
```bash
python database/load_csv_data.py --file data.csv --type faskes
```

### Proses Loading

**Step by Step**:

1. **Baca CSV** dengan multiple encoding support
2. **Standardisasi kolom** dengan column mapping
3. **Ekstrak koordinat** dari Google Maps links
4. **Validasi data**:
   - Check required fields
   - Validate coordinates (Indonesia bounds)
   - Skip invalid records
5. **Check duplicates** berdasarkan nama dan alamat
6. **Insert to database** dengan batch commit
7. **Show statistics** dan summary

**Output Example**:
```
Loading BPJS Faskes data from Data Faskes BPJS 2019.csv
Successfully read CSV with utf-8 encoding
Loaded 28137 rows from CSV
Columns: nolink, provinsi, kotakab, link, tipefaskes, no, kodefaskes, namafaskes, latlongfaskes, alamatfaskes
Filtered from 28137 to 4234 rows by facility type
Progress: 100 hospitals loaded...
Progress: 200 hospitals loaded...
...
✅ Successfully loaded 1523 hospitals from BPJS Faskes CSV
   Skipped: 2711 records
```

## ✅ Validasi Data

### Automatic Validation

Sistem melakukan validasi otomatis:

1. **Required Fields Check**:
   - Nama faskes tidak boleh kosong
   - Alamat tidak boleh kosong

2. **Coordinate Validation**:
   - Latitude: -11° to 6° (Indonesia bounds)
   - Longitude: 95° to 141° (Indonesia bounds)
   - Skip jika (0, 0)

3. **Duplicate Detection**:
   - Check by name + address
   - Skip jika sudah ada

4. **Data Type Validation**:
   - Numeric fields (beds, coordinates)
   - Text fields sanitization

### Manual Verification

**Check loaded data**:
```sql
-- Count hospitals by province
SELECT 
    class_, COUNT(*) as count 
FROM hospitals 
GROUP BY class_ 
ORDER BY count DESC;

-- Check coordinates validity
SELECT 
    name, latitude, longitude 
FROM hospitals 
WHERE latitude = 0 OR longitude = 0;

-- Hospital distribution by type
SELECT 
    type, COUNT(*) as count 
FROM hospitals 
GROUP BY type 
ORDER BY count DESC;
```

**Python verification**:
```python
from src.database import SessionLocal
from src.models import Hospital

db = SessionLocal()

# Total hospitals
total = db.query(Hospital).count()
print(f"Total hospitals: {total}")

# By type
rs_count = db.query(Hospital).filter(
    Hospital.type.like('%Rumah Sakit%')
).count()
print(f"Rumah Sakit: {rs_count}")

# Invalid coordinates
invalid = db.query(Hospital).filter(
    (Hospital.latitude == 0) | (Hospital.longitude == 0)
).count()
print(f"Invalid coordinates: {invalid}")
```

## 🤖 Training ML Models

### Automatic Training

Pipeline otomatis akan:
1. Generate synthetic training data (500+ records)
2. Train Random Forest model untuk wait time prediction
3. Validate model performance

```bash
python database/load_all_datasets.py
```

### Manual Training

**Generate training data**:
```python
from database.load_all_datasets import DataPipeline

pipeline = DataPipeline()
pipeline.generate_training_data(num_records=1000)
```

**Train models**:
```python
from src.predictor import WaitTimePredictor
from src.database import SessionLocal

db = SessionLocal()
predictor = WaitTimePredictor()

# Train model
success = predictor.train(db)

if success:
    # Test prediction
    wait_time = predictor.predict_wait_time(
        hospital_id=1,
        severity_level='high'
    )
    print(f"Predicted wait time: {wait_time} minutes")
```

### Training Data Generation

**Synthetic data includes**:
- Wait time history (500 records)
- Capacity history (250 records)
- Time-based patterns (peak vs non-peak hours)
- Severity-based variations

**Features used for prediction**:
- Hospital ID
- Severity level (encoded: low=1, medium=2, high=3, critical=4)
- Hour of day (0-23)
- Day of week (0-6)

**Model**: Random Forest Regressor
- n_estimators: 100
- random_state: 42

## 🔧 Troubleshooting

### Issue 1: Kaggle API Not Configured

**Error**:
```
⚠️  Kaggle API not configured
```

**Solution**:
1. Install kaggle: `pip install kaggle`
2. Setup kaggle.json (see [Download Dataset](#download-dataset))
3. Verify: `kaggle datasets list`

### Issue 2: CSV Encoding Error

**Error**:
```
UnicodeDecodeError: 'utf-8' codec can't decode
```

**Solution**:
Sistem sudah handle multiple encodings otomatis. Jika masih error:
```python
# Manual load dengan encoding spesifik
import pandas as pd
df = pd.read_csv('file.csv', encoding='latin-1')
```

### Issue 3: Invalid Coordinates

**Error**:
```
Skipping [hospital] - invalid coordinates
```

**Solution**:
- Normal jika banyak faskes tidak memiliki koordinat valid
- Sistem akan skip records dengan koordinat (0, 0)
- Hanya Rumah Sakit, Puskesmas, dan Klinik Utama yang di-load

### Issue 4: Database Connection Error

**Error**:
```
Can't connect to MySQL server
```

**Solution**:
1. Check MySQL service: `sudo service mysql status`
2. Verify credentials di `.env`
3. Create database: `CREATE DATABASE smartrujuk_db;`
4. Check firewall/port 3306

### Issue 5: Duplicate Records

**Info**:
```
Hospital [name] already exists, skipping
```

**Solution**:
- Normal behavior - sistem skip duplicates otomatis
- Jika ingin re-load, truncate table dulu:
```sql
TRUNCATE TABLE hospitals;
```

### Issue 6: Insufficient Training Data

**Warning**:
```
Not enough data to train the model
```

**Solution**:
```bash
# Generate more training data
python database/load_all_datasets.py --no-train
python -c "from database.load_all_datasets import DataPipeline; p = DataPipeline(); p.generate_training_data(1000)"
```

## 📊 Data Statistics

### Expected Data Volume

**After full load**:
- Total Facilities: ~1,500 - 4,000 (tergantung filter)
- Rumah Sakit: ~400 - 800
- Puskesmas: ~800 - 2,000
- Klinik: ~300 - 1,200
- Training Data: 500+ records

**Storage**:
- Database size: ~50-100 MB
- CSV files: ~10 MB compressed
- Total: ~110 MB

### Performance

**Loading time** (approximate):
- BPJS Faskes CSV (full): 2-5 minutes
- Bed Ratio CSV: 1-2 minutes
- Training data generation: 30 seconds
- Model training: 10-30 seconds
- **Total**: ~5-10 minutes

**Optimization tips**:
- Use province filter untuk dataset lebih kecil
- Batch commit setiap 100 records
- Index pada nama dan alamat kolom
- Use SSD untuk database storage

## 🎯 Best Practices

### 1. Regular Data Updates

```bash
# Update datasets quarterly
python database/dataset_downloader.py --force
python database/load_all_datasets.py
```

### 2. Data Backup

```bash
# Backup database
mysqldump -u root -p smartrujuk_db > backup_$(date +%Y%m%d).sql

# Restore
mysql -u root -p smartrujuk_db < backup_20231210.sql
```

### 3. Data Quality Monitoring

```sql
-- Check data quality metrics
SELECT 
    COUNT(*) as total,
    COUNT(DISTINCT name) as unique_names,
    SUM(CASE WHEN latitude = 0 THEN 1 ELSE 0 END) as invalid_coords,
    AVG(total_beds) as avg_beds
FROM hospitals;
```

### 4. Incremental Updates

```python
# Load only new data
loader = CSVDataLoader(db)
loader.load_bpjs_faskes_csv('new_data.csv', province='DKI Jakarta')
```

## 📚 Additional Resources

- [Data Loading Guide](DATA_LOADING_GUIDE.md) - Original guide
- [README.md](README.md) - Main documentation
- [TRAINING_GUIDE.md](TRAINING_GUIDE.md) - ML training guide
- [API Documentation](https://satusehat.kemkes.go.id/platform/docs/id/playbook/)

## 🤝 Contributing

Untuk menambahkan sumber dataset baru:

1. Tambahkan di `dataset_downloader.py`:
```python
self.datasets['new_source'] = {
    'name': 'Dataset Name',
    'source': 'https://kaggle.com/...',
    'files': ['file1.csv'],
    'description': 'Description'
}
```

2. Tambahkan loader method di `csv_loader.py`:
```python
def load_new_source_csv(self, csv_path: str) -> int:
    # Implementation
    pass
```

3. Update pipeline di `load_all_datasets.py`

---

**SmartRujuk+ Dataset Guide** - Memastikan data berkualitas untuk sistem rujukan yang lebih baik! 📊✨
