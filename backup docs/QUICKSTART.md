# Quick Start Guide - SmartRujuk+ AI Agent

⏱️ **Get started in 5 minutes!**

## Prerequisites

- ✅ Python 3.8+
- ✅ MySQL 5.7+
- ✅ 10 minutes of your time

## Step 1: Clone & Setup (2 min)

```bash
# Clone repository
git clone https://github.com/myaasiinh/smart-rujuk-ai-agent.git
cd smart-rujuk-ai-agent

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Database Setup (2 min)

```bash
# Create database
mysql -u root -p -e "CREATE DATABASE smartrujuk_db;"

# Configure environment
cp .env.example .env
# Edit .env: Set your DB_PASSWORD
```

## Step 3: Initialize Data (1 min)

```bash
python database/init_db.py
```

This will create:
- ✅ Database tables
- ✅ 10 sample hospitals in Jakarta
- ✅ 5 sample patients
- ✅ Historical data for predictions

## Step 4: Run Application (< 1 min)

### Option A: Using run script (Easiest)

**Linux/Mac:**
```bash
./run.sh
```

**Windows:**
```bash
run.bat
```

### Option B: Direct command

```bash
streamlit run app.py
```

## Step 5: Access & Explore! 🎉

Open browser: **http://localhost:8501**

### Try These Features:

1. **Dashboard** 🏠
   - View statistics
   - See hospitals on map

2. **Create Referral** 🚑
   - Select "Rujukan Baru"
   - Use existing patient or create new one
   - Enter location: `-6.2088, 106.8456` (Jakarta)
   - Describe condition: "Pasien demam tinggi"
   - Severity: "high"
   - Click "Cari Rumah Sakit Terbaik"
   - ✨ See AI recommendation!

3. **View Analytics** 📊
   - Go to "Analisis & Prediksi"
   - See capacity analysis
   - Check wait time predictions

## Common Issues & Solutions

### ❌ "Can't connect to MySQL"

**Solution:**
```bash
# Start MySQL service
# Windows: net start MySQL80
# Linux: sudo systemctl start mysql
# Mac: brew services start mysql

# Verify connection
mysql -u root -p -e "SELECT 1;"
```

### ❌ "ModuleNotFoundError"

**Solution:**
```bash
pip install -r requirements.txt
```

### ❌ "Database smartrujuk_db doesn't exist"

**Solution:**
```bash
mysql -u root -p -e "CREATE DATABASE smartrujuk_db;"
python database/init_db.py
```

## What's Next?

- 📚 Read [README.md](README.md) for detailed documentation
- 🏗️ Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- 🧪 See [TESTING.md](TESTING.md) for testing guide
- ⚙️ Review [SETUP.md](SETUP.md) for advanced configuration

## Need Help?

- 📖 Check documentation files
- 🐛 Open an issue on GitHub
- 💬 Contact repository owner

## Sample Data

The initialization script adds these sample hospitals in Jakarta:

1. RSUP Dr. Cipto Mangunkusumo (Class A)
2. RS Fatmawati (Class A)
3. RSUP Persahabatan (Class A)
4. RS Harapan Kita (Class A - Cardiac)
5. RSUD Tarakan (Class B)
6. RS Pelni (Class B)
7. RSUD Pasar Minggu (Class C)
8. RS Islam Jakarta Cempaka Putih (Class B)
9. RSUD Budhi Asih (Class B)
10. RS Hermina Bekasi (Class B)

And 5 sample patients with valid BPJS numbers.

## Configuration Tips

### Use Custom Port

```bash
streamlit run app.py --server.port 8502
```

### Enable Dark Mode

Add to `.streamlit/config.toml`:
```toml
[theme]
base = "dark"
```

### Add More Hospitals

Option 1: Use the UI
- Go to "Data Rumah Sakit"
- Click "Tambah Rumah Sakit Baru"
- Fill the form

Option 2: Import from CSV
```python
import pandas as pd
from src.database import SessionLocal
from src.models import Hospital

df = pd.read_csv('hospitals.csv')
db = SessionLocal()

for _, row in df.iterrows():
    hospital = Hospital(**row.to_dict())
    db.add(hospital)

db.commit()
```

## Pro Tips

1. **Get Better Predictions**
   - Add more historical data
   - Run system for a few weeks to collect real data
   - Model will improve over time

2. **Optimize Performance**
   - Add database indexes
   - Use caching for frequent queries
   - Enable connection pooling

3. **Customize Maps**
   - Edit `app.py` for custom map styles
   - Change marker colors and icons
   - Add custom overlays

## Architecture at a Glance

```
User Browser
    ↓
Streamlit UI (app.py)
    ↓
AI Agent (src/agent.py) ← LangChain
    ↓
ML Models (src/predictor.py) ← Scikit-learn
    ↓
Database (MySQL) ← SQLAlchemy
    ↓
External APIs (Google Maps, SATUSEHAT)
```

## Key Features Enabled

✅ Smart hospital recommendations using AI
✅ Wait time prediction using ML
✅ Geolocation with Google Maps
✅ Interactive dashboard
✅ Real-time capacity monitoring
✅ Patient & hospital management
✅ Analytics & visualization

---

**Congratulations! You're now running SmartRujuk+ AI Agent! 🎉**

Ready to help save lives through better healthcare coordination! 🏥💙
