# 🚀 Quick Start Guide - SmartRujuk+ AI Agent

**Status:** ✅ System is 100% operational and PRD-compliant

---

## 📋 Prerequisites Checklist

✅ Python 3.8+ installed (tested on 3.12.3)  
✅ MySQL 5.7+ installed (tested on 8.0.43)  
✅ Dependencies installed  
✅ Database initialized  
✅ API keys configured  

---

## ⚡ Quick Start (3 Commands)

### 1. Start MySQL
```bash
sudo systemctl start mysql
```

### 2. Verify System (Optional but Recommended)
```bash
python3 verify_system.py
```

Expected output:
```
Results: 6/6 tests passed
🎉 All tests passed! System is ready to use.
```

### 3. Launch Application
```bash
streamlit run app.py
```

### 4. Open Browser
Navigate to: http://localhost:8501

---

## 🧪 Run Tests

### System Verification Test
```bash
python3 verify_system.py
```

### PRD Compliance Test
```bash
python3 test_prd_compliance.py
```

Expected result for both:
```
✅ 100% Success Rate
✅ All tests passed
```

---

## 📊 Database Setup (Already Done)

If you need to reinitialize:
```bash
python3 database/init_db.py
```

This creates:
- ✅ All required tables
- ✅ 10 sample hospitals
- ✅ 5 sample patients
- ✅ Historical data for ML training
- ✅ API configuration

---

## 📁 Load Additional Data (Optional)

### Load BPJS Faskes Data
```bash
python3 database/load_csv_data.py --file path/to/bpjs_faskes.csv
```

### Load Bed Ratio Data
```bash
python3 database/load_csv_data.py --file path/to/bed_ratio.csv
```

### Load Multiple Files from Directory
```bash
python3 database/load_csv_data.py --dir path/to/csv_folder
```

---

## 🎯 Using the Application

### Available Features

1. **Dashboard (🏠)**
   - View system statistics
   - Interactive map with all hospitals
   - Recent referrals

2. **Rujukan Baru (🚑)**
   - Create new patient or select existing
   - Input location (coordinates or address)
   - Get AI-powered hospital recommendations
   - View route on map
   - Confirm and create referral

3. **Data Rumah Sakit (🏥)**
   - View all hospitals
   - Add new hospitals
   - Check capacity and availability

4. **Data Pasien (👤)**
   - View all patients
   - Patient information and BPJS details

5. **Analisis & Prediksi (📊)**
   - Hospital capacity analysis
   - Wait time predictions
   - Referral statistics

---

## 🔧 Configuration

### Environment Variables (.env)
All configured and ready to use:

```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=smartrujuk_db
DB_USER=root
DB_PASSWORD=

SATUSEHAT_ORG_ID=b5f0e7f5-5660-4b91-95fb-0cc21a5f735f
SATUSEHAT_CLIENT_ID=hC1BUB8jmg97VbSGxsPyNk2k9iEjnG7woXAQq06nUxwjbvPe
SATUSEHAT_CLIENT_SECRET=YzlwM6Z6xWgPa4FcOs6XdemGmTQF9HzTS77ZAAp4ptQFkeGSGAeJfEhFlFUHCjsT

GOOGLE_MAPS_API_KEY=AIzaSyBMagjD0rzJEn1n49v-5jC_OBiYeyYPdzY
```

✅ All credentials verified to match soal.txt

---

## 📖 Documentation

### Core Documentation
- `README.md` - Complete system documentation
- `FINAL_REPORT.md` - Executive summary of implementation
- `PRD_COMPLIANCE_REPORT.md` - Detailed PRD compliance verification
- `IMPLEMENTATION_SUCCESS_REPORT.md` - Implementation details
- `TEST_EXECUTION_SUMMARY.txt` - Test results summary

### Setup & Usage
- `SETUP.md` - Detailed setup instructions
- `QUICKSTART.md` - Original quick start guide
- `QUICK_START_GUIDE.md` - This guide

### Technical Documentation
- `ARCHITECTURE.md` - System architecture
- `TESTING.md` - Testing guide
- `DATA_LOADING_GUIDE.md` - Data loading instructions

### Test Reports
- `TEST_REPORT.md` - Detailed test report
- `TEST_SUMMARY.md` - Test summary

---

## ⚠️ Troubleshooting

### MySQL Connection Error
```bash
# Check if MySQL is running
sudo systemctl status mysql

# Start MySQL if not running
sudo systemctl start mysql
```

### Port 8501 Already in Use
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### Missing Dependencies
```bash
pip3 install -r requirements.txt
```

### Database Not Initialized
```bash
python3 database/init_db.py
```

---

## ✅ Verification Commands

### Check System Status
```bash
python3 verify_system.py
```

### Check PRD Compliance
```bash
python3 test_prd_compliance.py
```

### Check Database
```bash
mysql -u root -e "USE smartrujuk_db; SHOW TABLES;"
```

### Check Application
```bash
streamlit run app.py
# Then open http://localhost:8501 in browser
```

---

## 📊 Expected Test Results

All tests should show **100% success**:

```
System Tests:        6/6   passed (100%) ✅
PRD Compliance:      12/12 passed (100%) ✅
Total Tests:         18/18 passed (100%) ✅
```

---

## 🎯 Success Criteria

The system is working correctly when:

✅ All tests pass (18/18)  
✅ MySQL database is active  
✅ Streamlit app starts without errors  
✅ Web interface loads on port 8501  
✅ Hospital recommendations work  
✅ Maps display correctly  

---

## 📞 Need Help?

1. Check documentation in the repository
2. Review error messages in terminal
3. Run verification tests to diagnose issues
4. Check logs in the application

---

## 🎉 Success Confirmation

If you see this when running tests:
```
🎉 100% PRD COMPLIANCE ACHIEVED!
✅ All Product Requirements Document requirements are met
```

Then your system is **fully operational** and ready to use!

---

**Quick Start Guide**  
**Status:** ✅ System Ready  
**Version:** SmartRujuk+ AI Agent v1.0  
**Last Updated:** October 10, 2025
