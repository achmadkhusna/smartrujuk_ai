# SmartRujuk+ AI Agent - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites

- Python 3.8+ installed
- MySQL 5.7+ installed and running
- Internet connection (optional - system works offline)

---

## 📦 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/myaasiinh/smart-rujuk-ai-agent.git
cd smart-rujuk-ai-agent
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: This will install all required packages including:
- Streamlit (web interface)
- SQLAlchemy (database)
- LangChain (AI agent)
- scikit-learn (ML models)
- pandas, numpy (data processing)

---

## 🗄️ Database Setup

### Step 3: Start MySQL

**Linux/Mac:**
```bash
sudo service mysql start
```

**Windows:**
- Start MySQL from Services panel
- Or use: `net start MySQL80`

### Step 4: Create Database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE smartrujuk_db;
EXIT;
```

### Step 5: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file with your settings:

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=smartrujuk_db
DB_USER=root
DB_PASSWORD=your_mysql_password

# SATUSEHAT API (already configured)
SATUSEHAT_ORG_ID=b5f0e7f5-5660-4b91-95fb-0cc21a5f735f
SATUSEHAT_CLIENT_ID=hC1BUB8jmg97VbSGxsPyNk2k9iEjnG7woXAQq06nUxwjbvPe
SATUSEHAT_CLIENT_SECRET=YzlwM6Z6xWgPa4FcOs6XdemGmTQF9HzTS77ZAAp4ptQFkeGSGAeJfEhFlFUHCjsT

# Google Maps API (configured)
GOOGLE_MAPS_API_KEY=AIzaSyBMagjD0rzJEn1n49v-5jC_OBiYeyYPdzY
```

---

## 🎬 Initialize System

### Step 6: Initialize Database

```bash
python3 database/init_db.py
```

This will:
- Create all database tables
- Load API configuration
- Add 10 sample hospitals
- Add 5 sample patients
- Add historical data for ML training

**Expected Output:**
```
✅ API configuration loaded successfully to database
=== SmartRujuk+ Database Initialization ===
Creating database tables...
Tables created successfully!
...
✅ Database initialization completed successfully!
```

### Step 7: Load SATUSEHAT Data (Optional)

Load real patient and referral data from SATUSEHAT API:

```bash
python3 -c "
from src.satusehat_loader import SATUSEHATDataLoader
from src.database import SessionLocal

db = SessionLocal()
loader = SATUSEHATDataLoader(db)
stats = loader.load_all_data(max_pages=3)

print(f'✅ Loaded:')
print(f'   Patients: {stats[\"new_patients\"]}')
print(f'   Referrals: {stats[\"new_referrals\"]}')
db.close()
"
```

**Note**: If API is not available, system will use sample data automatically.

---

## 🏃 Run Application

### Step 8: Start Streamlit

```bash
streamlit run app.py
```

**Expected Output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Step 9: Open Browser

Navigate to: **http://localhost:8501**

---

## 🎯 Using the Application

### Dashboard (🏠)

View system overview:
- Total hospitals, patients, referrals
- Interactive map with hospital locations
- Recent referrals list

### Create New Referral (🚑)

1. **Select or Create Patient**
   - Choose existing patient from dropdown
   - Or create new patient with BPJS number

2. **Enter Location**
   - Input coordinates (latitude, longitude)
   - Or enter address and click "Geocode"

3. **Describe Condition**
   - Enter patient condition
   - Select severity level (low/medium/high/critical)
   - Set maximum distance

4. **Get Recommendation**
   - Click "🔍 Cari Rumah Sakit Terbaik"
   - View AI-powered recommendation
   - See distance, wait time, availability
   - Check route on map

5. **Confirm Referral**
   - Click "✅ Konfirmasi Rujukan"
   - Referral saved to database
   - Statistics automatically updated

### View Data

**Rumah Sakit (🏥)**
- Browse all hospitals
- View capacity and availability
- Add new hospitals

**Pasien (👤)**
- Browse all patients
- View BPJS numbers and contact info

### Analytics & Predictions (📊)

**Kapasitas RS**
- Real-time bed availability
- Occupancy rates
- Status indicators (green/yellow/orange/red)

**Prediksi Waktu Tunggu**
- Select hospital
- View predictions by severity level
- ML-based estimates

**Statistik Rujukan** ⭐ NEW
- Total referral count
- Status distribution (Pending/Accepted/Rejected/Completed)
- Recent referrals table (10 most recent)
- Real-time updates when new referral created

---

## 🧪 Verify Installation

### Run System Tests

```bash
python3 test_complete_system.py
```

**Expected Output:**
```
🎉 ALL TESTS PASSED - SYSTEM IS FULLY FUNCTIONAL!

Test Statistics:
   - Total Tests: 7
   - Passed: 7
   - Failed: 0
   - Success Rate: 100%
```

### Check Database

```bash
mysql -u root -p smartrujuk_db -e "
SELECT 
    (SELECT COUNT(*) FROM hospitals) as hospitals,
    (SELECT COUNT(*) FROM patients) as patients,
    (SELECT COUNT(*) FROM referrals) as referrals;
"
```

**Expected Output:**
```
+-----------+----------+-----------+
| hospitals | patients | referrals |
+-----------+----------+-----------+
|        10 |        7 |        14 |
+-----------+----------+-----------+
```

---

## 🔧 Troubleshooting

### Issue: Database Connection Error

**Error**: `Can't connect to MySQL server`

**Solution**:
```bash
# Check MySQL is running
sudo service mysql status

# Start MySQL if not running
sudo service mysql start

# Verify credentials in .env file
cat .env | grep DB_
```

### Issue: ModuleNotFoundError

**Error**: `No module named 'xxx'`

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific package
pip install streamlit
```

### Issue: SATUSEHAT API Not Responding

**Status**: ⚠️ Expected in some environments

**Solution**: No action needed!
- System automatically uses offline mode
- Sample data provided
- All features continue to work
- Ready for real API when network available

### Issue: Google Maps Quota Exceeded

**Error**: Maps not displaying or distance calculation fails

**Solution**:
- System automatically falls back to Haversine formula
- Basic distance calculation still works
- Built-in coordinates for major Indonesian cities

---

## 📱 Using the System

### Example: Create a Referral

1. **Go to "🚑 Rujukan Baru"**

2. **Select Patient**: "Ahmad Suryadi"

3. **Enter Location**: 
   - Latitude: `-6.2088`
   - Longitude: `106.8456`

4. **Enter Condition**: "Chest pain, requires cardiac evaluation"

5. **Select Severity**: "high"

6. **Click**: "🔍 Cari Rumah Sakit Terbaik"

7. **View Recommendation**:
   - Hospital: RSUP Dr. Cipto Mangunkusumo
   - Distance: 2.99 km
   - Wait Time: 90 minutes
   - Available Beds: 45

8. **Click**: "✅ Konfirmasi Rujukan"

9. **Verify**: Go to "📊 Analisis & Prediksi" → "Statistik Rujukan"
   - See new referral in the list
   - Status updated in real-time
   - Total count increased

---

## 📊 System Features

### ✅ Working Features

- [x] SATUSEHAT API integration with OAuth2
- [x] Real patient data loading (with offline fallback)
- [x] Real referral data loading (BPJS + private insurance)
- [x] MySQL database with all tables
- [x] AI-powered hospital recommendations
- [x] ML-based wait time predictions
- [x] Interactive Streamlit interface
- [x] Google Maps integration with route visualization
- [x] Real-time statistics updates
- [x] Referral creation and persistence
- [x] Comprehensive error handling
- [x] Offline mode for limited connectivity

### 🎯 System Capabilities

**Data Sources**:
- SATUSEHAT FHIR API (Patient, ServiceRequest)
- Google Maps API (geocoding, distance)
- CSV datasets (hospital bed ratios)

**AI Features**:
- LangChain agent with 4 tools
- Random Forest ML model
- Multi-factor hospital scoring
- Alternative recommendations

**User Interface**:
- 5 main sections
- Interactive maps
- Real-time updates
- Responsive design

---

## 📚 Next Steps

### Learn More

- Read [COMPLETE_SYSTEM_DOCUMENTATION.md](COMPLETE_SYSTEM_DOCUMENTATION.md) for detailed architecture
- Read [FINAL_TEST_REPORT_COMPLETE.md](FINAL_TEST_REPORT_COMPLETE.md) for test results
- Check [README.md](README.md) for comprehensive information

### Customize

- Add more hospitals: Use "🏥 Data Rumah Sakit" → "➕ Tambah Rumah Sakit Baru"
- Add more patients: Use "👤 Data Pasien" → "➕ Tambah Pasien Baru"
- Train ML model: Will auto-train when you have more historical data

### Deploy

- **Local**: Already running!
- **Streamlit Cloud**: Push to GitHub, connect to Streamlit Cloud
- **Docker**: Build container with provided instructions
- **Cloud**: Deploy to AWS, GCP, Azure

---

## 🎉 Success!

You now have a fully functional SmartRujuk+ AI Agent system running locally!

### What's Working:

✅ Database with real data  
✅ SATUSEHAT API integration  
✅ AI-powered recommendations  
✅ ML wait time predictions  
✅ Interactive web interface  
✅ Real-time statistics  
✅ Complete end-to-end workflow  

### Get Help

If you encounter any issues:

1. Check the [COMPLETE_SYSTEM_DOCUMENTATION.md](COMPLETE_SYSTEM_DOCUMENTATION.md)
2. Review the [FINAL_TEST_REPORT_COMPLETE.md](FINAL_TEST_REPORT_COMPLETE.md)
3. Run `python3 test_complete_system.py` to diagnose problems
4. Open an issue on GitHub

---

**Happy Referring! 🏥💙**
