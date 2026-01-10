# SmartRujuk+ AI Agent 🏥

Sistem Rujukan Otomatis dengan Geolokasi, Prediksi Waktu Tunggu, dan Analisis Kapasitas Rumah Sakit untuk mempercepat proses rujukan pasien JKN.

## ✅ Test Status: **100% SUCCESS**
> **All tests passed!** The codebase is fully functional with zero critical issues.  
> See [TEST_SUMMARY.md](TEST_SUMMARY.md) for quick results or [TEST_REPORT.md](TEST_REPORT.md) for detailed report.  
> Run `python3 verify_system.py` to verify the system yourself.

## 🌟 Fitur Utama

- **AI Agent** dengan LangChain untuk rekomendasi rumah sakit cerdas
- **Prediksi Waktu Tunggu** menggunakan Machine Learning
- **Geolokasi & Peta Interaktif** dengan Google Maps API
- **Analisis Kapasitas** rumah sakit real-time
- **Dataset Kaggle** untuk data faskes (BPJS Faskes Indonesia)
- **Integrasi SATUSEHAT API** untuk data pasien & rujukan
- **Dashboard Interaktif** dengan Streamlit
- **Database MySQL** untuk penyimpanan data
- **CSV Data Loader** untuk import data dari multiple provinces
- **Offline Fallback** untuk Google Maps & SATUSEHAT API
- **API Configuration Management** dengan database storage

## 🏗️ Arsitektur Sistem

```
SmartRujuk+ AI Agent
├── Frontend (Streamlit)
│   ├── Dashboard
│   ├── Form Rujukan
│   ├── Data Management
│   └── Analytics
├── Backend (Python)
│   ├── AI Agent (LangChain)
│   ├── Predictive Models (Scikit-learn)
│   ├── API Integrations
│   │   ├── SATUSEHAT API
│   │   └── Google Maps API
│   └── Database Layer (SQLAlchemy)
└── Database (MySQL)
    ├── Hospitals
    ├── Patients
    ├── Referrals
    └── Historical Data
```

## 📋 Prerequisites

- Python 3.8 atau lebih baru (termasuk Python 3.13 ✅)
- MySQL 5.7 atau lebih baru
- Google Maps API Key
- SATUSEHAT API Credentials (opsional)
- OpenAI API Key (opsional, untuk AI Agent)

## 🚀 Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/myaasiinh/smart-rujuk-ai-agent.git
cd smart-rujuk-ai-agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> **✅ Python 3.13 Compatible!** Requirements updated to work seamlessly with Python 3.13 without needing C++ compilers. See [INSTALLATION_FIX.md](INSTALLATION_FIX.md) for details.

### 3. Setup MySQL Database

Buat database MySQL baru:

```sql
CREATE DATABASE smartrujuk_db;
```

Atau jalankan script SQL:

```bash
mysql -u root -p < database/schema.sql
```

### 4. Konfigurasi Environment Variables

Copy file `.env.example` menjadi `.env`:

```bash
cp .env.example .env
```

Edit file `.env` dan isi dengan credentials Anda:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=smartrujuk_db
DB_USER=root
DB_PASSWORD=your_password

# SATUSEHAT API Configuration (optional)
SATUSEHAT_ORG_ID=your_satusehat_org_id
SATUSEHAT_CLIENT_ID=your_satusehat_client_id
SATUSEHAT_CLIENT_SECRET=your_satusehat_client_secret
SATUSEHAT_BASE_URL=https://api-satusehat.kemkes.go.id

# Google Maps API Configuration (optional)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# OpenAI API Configuration (optional)
OPENAI_API_KEY=your_openai_api_key
```

### 5. Inisialisasi Database

Jalankan script inisialisasi untuk membuat tabel dan mengisi data sampel:

```bash
python database/init_db.py
```

Script ini akan:
- Membuat semua tabel database (termasuk tabel API config)
- Memuat konfigurasi API dari soal.txt ke database
- Menambahkan 10 rumah sakit sampel di area Jakarta
- Menambahkan 5 pasien sampel
- Menambahkan data historis untuk prediksi

### 6. Load Dataset Kaggle (PENTING! 🔥)

**SmartRujuk+ memerlukan data dari 2 sumber Kaggle**. Pilih salah satu metode:

#### Metode A: Automatic Download + Load (Recommended)

```bash
# Install Kaggle API dulu
pip install kaggle

# Setup Kaggle credentials (download kaggle.json dari Kaggle.com/settings)
# Letakkan di ~/.kaggle/kaggle.json (Linux/Mac) atau C:\Users\<username>\.kaggle\kaggle.json (Windows)

# Download + Load + Train dalam 1 command!
python database/load_all_datasets.py --download-first
```

#### Metode B: Manual Download + Load

**Step 1**: Download manual dari Kaggle:
- Dataset 1: https://www.kaggle.com/datasets/israhabibi/list-faskes-bpjs-indonesia
- Dataset 2: https://www.kaggle.com/datasets/yafethtb/dataset-rasio-bed-to-population-faskes-ii

**Step 2**: Extract semua file CSV ke `data/kaggle_datasets/`

**Step 3**: Load ke database:
```bash
python database/load_all_datasets.py
```

#### Hasil yang Diharapkan:
```
✅ Successfully loaded 1,523 hospitals from BPJS Faskes CSV
✅ Updated 245 hospitals with bed ratio data
✅ Generated 500 wait time records
✅ ML models trained successfully

📊 Database Statistics:
   Total Facilities: 1,523
   - Rumah Sakit: 458
   - Puskesmas: 821
   - Klinik: 244
```

**Panduan lengkap**: [DATASET_GUIDE.md](DATASET_GUIDE.md) | [TRAINING_GUIDE.md](TRAINING_GUIDE.md)

## 🎯 Cara Menggunakan

### Menjalankan Aplikasi

```bash
streamlit run app.py
```

Aplikasi akan terbuka di browser pada `http://localhost:8501`

### Fitur-Fitur Utama

#### 1. Dashboard
- Melihat statistik umum (total RS, pasien, rujukan)
- Peta interaktif dengan lokasi semua rumah sakit
- Daftar rujukan terbaru

#### 2. Rujukan Baru
- Input data pasien (baru atau existing)
- Input lokasi pasien (koordinat atau alamat)
- Deskripsi kondisi dan tingkat keparahan
- AI Agent akan merekomendasikan rumah sakit terbaik berdasarkan:
  - Jarak terdekat
  - Ketersediaan tempat tidur
  - Prediksi waktu tunggu
  - Tingkat okupansi
- Peta rute dari lokasi pasien ke RS
- Alternatif rumah sakit lain
- Konfirmasi dan simpan rujukan

#### 3. Data Rumah Sakit
- Lihat semua data rumah sakit
- Tambah rumah sakit baru
- Info kapasitas dan status

#### 4. Data Pasien
- Lihat semua data pasien
- Info BPJS dan kontak

#### 5. Analisis & Prediksi
- **Analisis Kapasitas**: Status real-time kapasitas semua RS
- **Prediksi Waktu Tunggu**: Prediksi waktu tunggu per tingkat keparahan
- **Statistik Rujukan**: Distribusi status rujukan

## 📊 Data Sources

Sistem ini terintegrasi dengan 2 dataset utama dari Kaggle dan API eksternal:

### Dataset Kaggle (Primary Data Sources)

#### 1. **BPJS Faskes Indonesia Dataset** 
   - **Source**: https://www.kaggle.com/datasets/israhabibi/list-faskes-bpjs-indonesia
   - **Description**: Daftar lengkap ~28,000+ fasilitas kesehatan yang bekerja sama dengan BPJS
   - **Coverage**: Seluruh Indonesia (34 provinsi)
   - **Data Year**: 2019
   - **Includes**: Rumah Sakit, Puskesmas, Klinik, dengan koordinat GPS
   - ✨ **Auto Loader**: Import otomatis dengan ekstraksi koordinat dari Google Maps links
   - ✨ **Province Filter**: Load data spesifik per provinsi
   
#### 2. **Hospital Bed to Population Ratio Dataset**
   - **Source**: https://www.kaggle.com/datasets/yafethtb/dataset-rasio-bed-to-population-faskes-ii
   - **Description**: Dataset rasio tempat tidur rumah sakit per populasi untuk RS Kelas C dan D
   - **Coverage**: 34 provinsi Indonesia
   - **Data Year**: 2020
   - **Includes**: Jumlah bed, populasi, rasio bed-to-population per provinsi
   - ✨ **Bed Capacity**: Update otomatis kapasitas tempat tidur rumah sakit
   - ✨ **Population Data**: Data proyeksi penduduk per provinsi

### API Integration

#### 3. **SATUSEHAT API** - Data pasien dan rujukan dari Kemenkes
   - Dokumentasi: https://satusehat.kemkes.go.id/platform/docs/id/postman-workshop/forking/
   - ✨ **Offline Fallback**: Sistem tetap berjalan dengan sample data jika API tidak tersedia
   
#### 4. **Google Maps API** - Geolokasi dan routing
   - Documentation: https://developers.google.com/maps/documentation
   - API Key: Configured in soal.txt
   - ✨ **Offline Geocoding**: Fallback otomatis ke database lokasi built-in

### Comprehensive Data Pipeline

```bash
# Download datasets dari Kaggle
python database/dataset_downloader.py

# Load semua dataset + train ML models (ONE COMMAND!)
python database/load_all_datasets.py

# Output: 1,500-4,000 hospitals + trained ML models
```

Lihat [DATASET_GUIDE.md](DATASET_GUIDE.md) untuk panduan lengkap.

## 🔧 Teknologi yang Digunakan

### Backend
- **Python 3.8+** - Programming language
- **SQLAlchemy** - ORM untuk database
- **MySQL** - Relational database
- **LangChain** - AI Agent framework
- **Scikit-learn** - Machine learning untuk prediksi
- **OpenAI GPT** - Language model (optional)

### APIs & Services
- **Google Maps API** - Geolocation & routing
- **SATUSEHAT API** - Healthcare facility data
- **googlemaps** - Python client untuk Google Maps

### Frontend
- **Streamlit** - Web application framework
- **Folium** - Interactive maps
- **Pandas** - Data manipulation
- **streamlit-folium** - Streamlit component untuk Folium

## 📁 Struktur Proyek

```
tubes-biomedis-tema2-smart-rujuk-agent-ai/
├── 📄 Core Application
│   ├── app.py                      # Main Streamlit application
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example               # Environment variables template
│   └── soal.txt                   # Original requirements
│
├── 📂 Source Code (src/)
│   ├── database.py                # Database connection
│   ├── models.py                  # SQLAlchemy models
│   ├── agent.py                   # LangChain AI Agent
│   ├── predictor.py               # ML prediction models
│   ├── maps_api.py                # Google Maps integration (+ offline)
│   ├── satusehat_api.py           # SATUSEHAT API (+ offline)
│   └── csv_loader.py              # CSV data loading module
│
├── 📂 Database Scripts (database/)
│   ├── schema.sql                 # Database schema
│   ├── init_db.py                 # Database initialization
│   ├── dataset_downloader.py     # 🆕 Download Kaggle datasets
│   ├── load_all_datasets.py      # 🆕 Complete data pipeline
│   ├── load_csv_data.py           # Individual CSV loader
│   └── load_api_config.py         # API config loader
│
├── 📂 Data Directory (data/)
│   ├── kaggle_datasets/           # 🆕 Downloaded datasets
│   └── README.md
│
├── 📂 Documentation (Comprehensive!)
│   ├── README.md                  # Main documentation (this file)
│   ├── PROJECT_OVERVIEW.md        # 🆕 Complete project overview
│   ├── DATASET_GUIDE.md           # 🆕 Dataset management guide
│   ├── TRAINING_GUIDE.md          # 🆕 ML training guide
│   ├── DATA_LOADING_GUIDE.md      # CSV loading guide
│   ├── QUICKSTART.md              # Quick start guide
│   ├── ARCHITECTURE.md            # System architecture
│   ├── SETUP.md                   # Setup instructions
│   ├── TESTING.md                 # Testing guide
│   └── [15+ more documentation files...]
│
└── 📂 Tests
    ├── test_improvements.py       # Improvement tests
    ├── test_prd_compliance.py     # Compliance tests
    └── verify_system.py           # System verification
```

## 🤖 AI Agent

Sistem menggunakan LangChain AI Agent yang dilengkapi dengan tools:

1. **FindNearestHospitals** - Mencari RS terdekat dari lokasi
2. **CheckHospitalCapacity** - Cek kapasitas RS spesifik
3. **PredictWaitTime** - Prediksi waktu tunggu
4. **CalculateDistance** - Hitung jarak antar lokasi

Agent menggunakan algoritma scoring untuk merekomendasikan RS terbaik berdasarkan:
- Jarak (40% weight untuk non-critical, 70% untuk critical)
- Waktu tunggu (30% weight)
- Kapasitas tersedia (30% weight untuk non-critical)

## 📈 Machine Learning

### Wait Time Prediction
- **Algorithm**: Random Forest Regressor
- **Features**: 
  - Hospital ID
  - Severity level (encoded)
  - Hour of day
  - Day of week
- **Training**: Otomatis menggunakan data historis
- **Fallback**: Default values jika model belum trained

### Capacity Analysis
- Real-time calculation berdasarkan available beds
- Status levels: low, moderate, high, critical
- Occupancy rate tracking

## ✨ Fitur Baru: Codebase Improvements

### 1. CSV Data Loading Module
- Load data rumah sakit dari multiple CSV files
- Support berbagai format CSV (BPJS Faskes, Bed Ratio, dll)
- Filter by province
- Batch loading dari directory
- Auto-detect file type
- Validasi dan error handling

### 2. API Configuration Management
- Ekstrak credentials dari soal.txt otomatis
- Store API config di database (centralized)
- Easy update dan management
- Support multiple API services

### 3. Offline Fallback Mechanisms
**Google Maps API:**
- Auto-detect offline mode
- Built-in geocoding untuk 20+ kota besar Indonesia
- Haversine formula untuk distance calculation
- Zero disruption saat API unavailable

**SATUSEHAT API:**
- Sample organization data untuk testing
- Sample location data
- Seamless fallback ke offline mode
- Development-friendly

### 4. Comprehensive Documentation
- [DATA_LOADING_GUIDE.md](DATA_LOADING_GUIDE.md) - Panduan lengkap loading CSV
- Test suite untuk validasi functionality
- Usage examples dan troubleshooting

## 🔒 Security

- Environment variables untuk credentials
- `.gitignore` untuk file sensitif
- Database connection pooling dengan SQLAlchemy
- Input validation pada form
- API credentials stored in database (encrypted in production)

## 🐛 Troubleshooting

### Database Connection Error
```
Error: Can't connect to MySQL server
```
**Solution**: 
- Pastikan MySQL server berjalan
- Cek credentials di file `.env`
- Cek firewall/port 3306

### Google Maps API Error
```
Error: INVALID_REQUEST or ZERO_RESULTS
```
**Solution**:
- Verifikasi API key di `.env`
- Aktifkan APIs: Maps JavaScript API, Geocoding API, Distance Matrix API
- Cek billing di Google Cloud Console

### Import Error
```
ModuleNotFoundError: No module named 'xxx'
```
**Solution**:
```bash
pip install -r requirements.txt
```

### Installation Error on Python 3.13 (Windows)
```
ERROR: Unknown compiler(s): [['icl'], ['cl'], ['cc'], ['gcc'], ...
```
**Solution**: This has been fixed! The updated `requirements.txt` now works with Python 3.13 without needing C++ compilers.
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
See [INSTALLATION_FIX.md](INSTALLATION_FIX.md) for detailed explanation.

## 🤝 Contributing

Kontribusi sangat diterima! Silakan:
1. Fork repository
2. Buat branch baru (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📝 License

Project ini dibuat untuk keperluan tugas akademik Biomedical Engineering.

## 👥 Authors

- Muhammad Yaasiin Hidayatulloh / myaasiinh

## 🙏 Acknowledgments

- BPJS Kesehatan untuk data faskes
- Kementerian Kesehatan RI untuk SATUSEHAT API
- Google Maps Platform
- LangChain & OpenAI
- Streamlit Community

## 📚 Dokumentasi Lengkap

### 🚀 Getting Started
- [README.md](README.md) - Dokumentasi utama (ini)
- [QUICKSTART.md](QUICKSTART.md) - Panduan quick start
- [SETUP.md](SETUP.md) - Setup detail step-by-step
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - 🆕 Overview lengkap project

### 📊 Data & ML Training
- [DATASET_GUIDE.md](DATASET_GUIDE.md) - 🆕 Panduan lengkap dataset Kaggle
- [TRAINING_GUIDE.md](TRAINING_GUIDE.md) - 🆕 Panduan training ML models
- [DATA_LOADING_GUIDE.md](DATA_LOADING_GUIDE.md) - Panduan loading CSV

### 🏗️ Architecture & System
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arsitektur sistem
- [SYSTEM_FLOW.md](SYSTEM_FLOW.md) - Flow diagram sistem

### ✅ Testing & Validation
- [TESTING.md](TESTING.md) - Panduan testing
- [TEST_REPORT.md](TEST_REPORT.md) - Hasil testing
- [VERIFICATION_COMPLETE.md](VERIFICATION_COMPLETE.md) - Status verifikasi

### 📋 Reports & Compliance
- [PRD_COMPLIANCE_REPORT.md](PRD_COMPLIANCE_REPORT.md) - Compliance report
- [FINAL_REPORT.md](FINAL_REPORT.md) - Laporan akhir
- [IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md) - Summary improvements

## 📞 Support

Jika ada pertanyaan atau issues, silakan buka issue di GitHub repository.

## 🎯 What's New in v2.0

### 🆕 Major Updates
- ✅ **Comprehensive Dataset Support**: 2 Kaggle datasets fully integrated
- ✅ **Automated Data Pipeline**: One-command setup for all data
- ✅ **Enhanced Documentation**: 3 new comprehensive guides
- ✅ **ML Model Training**: Automatic training with real data
- ✅ **Better Data Processing**: Advanced CSV loader with GPS extraction
- ✅ **Offline Capabilities**: Enhanced fallback mechanisms

### 📈 Improvements
- Load 1,500-4,000 hospitals from BPJS Faskes dataset
- Automatic bed capacity data from Bed Ratio dataset
- GPS coordinate extraction from Google Maps links
- Synthetic training data generation (500+ records)
- Random Forest model for wait time prediction
- Complete data validation and quality checks

---

**SmartRujuk+ AI Agent v2.0** - Sistem rujukan yang lebih cerdas dengan data lengkap dari Kaggle! 🏥💙✨
