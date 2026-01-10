# Quick Start Guide - SmartRujuk+ with SATUSEHAT Integration

This guide will help you quickly set up and run the SmartRujuk+ AI Agent system with SATUSEHAT API integration.

## Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher
- Internet connection (for API access)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure MySQL Database

Start MySQL service:
```bash
# Linux/Ubuntu
sudo service mysql start

# macOS
brew services start mysql

# Windows
net start MySQL80
```

Create the database:
```bash
mysql -u root -e "CREATE DATABASE IF NOT EXISTS smartrujuk_db;"
```

### 3. Configure Environment Variables

The `.env` file is already configured with sandbox credentials:
```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=smartrujuk_db
DB_USER=root
DB_PASSWORD=

# SATUSEHAT API Configuration (Sandbox)
SATUSEHAT_ORG_ID=b5f0e7f5-5660-4b91-95fb-0cc21a5f735f
SATUSEHAT_CLIENT_ID=hC1BUB8jmg97VbSGxsPyNk2k9iEjnG7woXAQq06nUxwjbvPe
SATUSEHAT_CLIENT_SECRET=YzlwM6Z6xWgPa4FcOs6XdemGmTQF9HzTS77ZAAp4ptQFkeGSGAeJfEhFlFUHCjsT

# Google Maps API Configuration
GOOGLE_MAPS_API_KEY=AIzaSyBMagjD0rzJEn1n49v-5jC_OBiYeyYPdzY
```

### 4. Initialize Database and Load Data

Run the integration test to set up the database and load sample data:
```bash
python3 test_satusehat_integration.py
```

Expected output:
```
================================================================================
SATUSEHAT API INTEGRATION TEST
================================================================================

1. Initializing database...
   ✓ Database initialized successfully

2. Testing SATUSEHAT API token generation...
   ! Operating in offline mode (API unavailable)

3. Adding sample hospital data...
   ✓ Added 3 sample hospitals

4. Testing patient data fetching...
   ✓ Retrieved 2 patients

5. Testing referral data fetching...
   ✓ Retrieved 2 service requests

6. Loading SATUSEHAT data into database...
   ✓ Data loading complete:
     - Total patients in DB: 2
     - Total referrals in DB: 4

7. Verifying data in database...
   ✓ Database statistics:
     - Patients: 2
     - Referrals: 4
     - Hospitals: 3

================================================================================
TEST COMPLETE
================================================================================
```

### 5. Train the Prediction Model

Generate historical data and train the machine learning model:
```bash
python3 train_model.py
```

Expected output:
```
================================================================================
MODEL TRAINING SCRIPT
================================================================================

1. Initializing database...

2. Checking data availability...
   - Patients: 2
   - Referrals: 4
   - Hospitals: 3

3. Generating synthetic wait time history for training...
   ✓ Generated 8640 wait time history entries

4. Generating synthetic capacity history for training...
   ✓ Generated 2160 capacity history entries

5. Training wait time prediction model...
   ✓ Model trained successfully

   Testing model predictions:
     - Hospital 1, Severity low: 45 minutes
     - Hospital 1, Severity medium: 74 minutes
     - Hospital 1, Severity high: 120 minutes
     - Hospital 1, Severity critical: 19 minutes

8. Generating summary statistics...
   System Statistics:
     - Total Patients: 2
     - Total Referrals: 4
       • Pending: 2
       • Completed: 2
     - Total Hospitals: 3
     - Average Wait Time: 71.1 minutes

================================================================================
MODEL TRAINING COMPLETE
================================================================================
```

### 6. Start the Streamlit Application

```bash
streamlit run app.py
```

The application will start and open in your browser at http://localhost:8501

## Using the Application

### Dashboard
- View overall system statistics
- See hospital locations on interactive map
- Check recent referrals

### Rujukan Baru (New Referral)
- Create new patient referrals
- Get AI-powered hospital recommendations
- View predicted wait times

### Data Rumah Sakit (Hospital Data)
- View all hospitals in the system
- Check bed availability
- See emergency service status

### Data Pasien (Patient Data)
- View all patients
- Search and filter patient records
- Export data to CSV

### Analisis & Prediksi (Analysis & Prediction)
- View capacity trends
- Check wait time predictions
- Analyze referral patterns

## Troubleshooting

### MySQL Connection Error

If you get a MySQL connection error:
```bash
# Reset root password
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '';"
sudo mysql -e "FLUSH PRIVILEGES;"
```

### SATUSEHAT API Not Accessible

The system will automatically switch to offline mode if the API is not accessible. This is normal in restricted network environments. The system will work with sample data.

### Port Already in Use

If port 8501 is already in use:
```bash
streamlit run app.py --server.port 8502
```

## Data Management

### Load More Data from SATUSEHAT API

To load additional data from SATUSEHAT API (when available):
```python
from src.satusehat_loader import SATUSEHATDataLoader

loader = SATUSEHATDataLoader()
stats = loader.load_all_data(max_pages=5)
print(f"Loaded {stats['total_patients']} patients")
```

### Retrain the Model

After adding new data, retrain the model:
```bash
python3 train_model.py
```

### Reset Database

To start fresh:
```bash
mysql -u root smartrujuk_db -e "DROP DATABASE smartrujuk_db; CREATE DATABASE smartrujuk_db;"
python3 test_satusehat_integration.py
python3 train_model.py
```

## System Architecture

```
┌─────────────────────────────────────────┐
│       Streamlit Web Interface           │
│  (Dashboard, Forms, Data Management)    │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│         Python Backend                   │
│  - AI Agent (LangChain)                 │
│  - ML Models (Scikit-learn)             │
│  - API Clients (SATUSEHAT, Maps)        │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│         MySQL Database                   │
│  - patients                              │
│  - referrals                             │
│  - hospitals                             │
│  - wait_time_history                     │
│  - capacity_history                      │
└─────────────────────────────────────────┘
```

## Key Features

✅ **SATUSEHAT API Integration** - Fetch real patient and referral data  
✅ **Machine Learning Predictions** - Wait time and capacity forecasting  
✅ **Interactive Dashboard** - Real-time data visualization  
✅ **Google Maps Integration** - Hospital location mapping  
✅ **Offline Mode** - Works without API access  
✅ **Data Export** - CSV export functionality  

## Next Steps

1. ✅ System is ready to use!
2. Explore all menu options in the Streamlit interface
3. Try creating a new referral
4. View patient and hospital data
5. Check the analytics and predictions

## Documentation

- Full Integration Report: `SATUSEHAT_INTEGRATION_REPORT.md`
- README: `README.md`
- Architecture: `ARCHITECTURE.md`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the integration report for detailed information
3. Check the logs in the terminal where you started Streamlit

---

**Enjoy using SmartRujuk+ AI Agent! 🏥**
