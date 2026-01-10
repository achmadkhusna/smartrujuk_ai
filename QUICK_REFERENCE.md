# 📋 QUICK REFERENCE - For Presentation

## TEKNOLOGI YANG DIGUNAKAN (Quick Table)

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Language** | Python | 3.8+ | Core development |
| **Frontend** | Streamlit | 1.29.0+ | Web UI/Dashboard |
| **Backend** | FastAPI/Flask | Latest | REST API (optional) |
| **AI/Agent** | LangChain | 0.1.0+ | ⭐ Autonomous decision making |
| **ML/Prediction** | scikit-learn | 1.3.2+ | Random Forest model |
| **Database** | MySQL | 8.0+ | Data persistence |
| **ORM** | SQLAlchemy | 2.0.23+ | Database layer |
| **Data Tools** | Pandas, NumPy | Latest | Data processing |
| **Maps** | Google Maps API | Latest | Geolocation |
| **Health API** | SATUSEHAT API | FHIR R4 | Patient & referral data |
| **Maps UI** | Folium | 0.15.1+ | Interactive maps |
| **Config** | python-dotenv | 1.0.0+ | Environment management |

---

## INTEGRASI KE MANA SAJA? (Integration Points)

### 1. **Google Maps API**
- **Fungsi**: Geolocation, distance, routing
- **Methods**: 
  - Geocoding (address → lat/lon)
  - Distance Matrix (calculate distances)
  - Routes API (get directions)
- **Fallback**: Haversine formula (offline)
- **File**: `src/maps_api.py`

### 2. **SATUSEHAT API** (Kemenkes Platform)
- **Fungsi**: Real-time patient & referral data
- **Auth**: OAuth2 Client Credentials
- **Endpoints**:
  - `/oauth2/v1/accesstoken` (authentication)
  - `/fhir-r4/v1/Patient` (patient data)
  - `/fhir-r4/v1/ServiceRequest` (referral data)
  - `/fhir-r4/v1/Organization` (facility data - reference)
- **Format**: FHIR R4 (JSON)
- **Fallback**: Sample data (offline)
- **Files**: `src/satusehat_api.py`, `src/satusehat_loader.py`

### 3. **OpenAI GPT-3.5** (Optional)
- **Fungsi**: Advanced AI reasoning
- **Model**: gpt-3.5-turbo
- **Usage**: LLM-powered agent decision making
- **File**: `src/agent.py`

### 4. **Kaggle Datasets** (CSV Import)
- **Dataset 1**: BPJS Faskes Indonesia (1,500+ hospitals)
- **Dataset 2**: Bed-to-Population Ratio (34 provinces)
- **Method**: Direct CSV load via Python
- **Files**: `src/csv_loader.py`, `database/load_csv_data.py`

---

## DATASET YANG DIGUNAKAN

### Dataset 1: BPJS Faskes Indonesia
```
Source: Kaggle (israhabibi/list-faskes-bpjs-indonesia)
Format: CSV
Records: ~1,523 healthcare facilities
Fields: 
  - NamaFaskes (Hospital name)
  - AlamatFaskes (Address)
  - GMaps (Coordinates via Google Maps link)
  - TipeFaskes (Type: RS/Puskesmas/Klinik)
  - Provinsi (Province)

Loading:
  python database/load_csv_data.py --file "Data Faskes BPJS 2019.csv"

Stored In:
  MySQL: hospitals table (1,523 records)
```

### Dataset 2: Bed-to-Population Ratio
```
Source: Kaggle (yafethtb/dataset-rasio-bed-to-population-faskes-ii)
Format: CSV
Coverage: 34 Provinces Indonesia
Year: 2020
Fields:
  - Provinsi (Province)
  - Total_Beds
  - Population
  - Bed_to_Population_Ratio

Purpose:
  Update hospital bed capacity

Stored In:
  MySQL: hospitals table (capacity fields)
```

### Dataset 3: SATUSEHAT Real-time
```
Source: SATUSEHAT Platform (Kemenkes)
Format: FHIR R4 (JSON via REST API)
Update: Real-time
Data:
  - Patient profiles (from national registry)
  - Referral records (historical)
  - Organization details

Loaded Via:
  src/satusehat_loader.py

Stored In:
  MySQL: patients table, referrals table
```

### Dataset 4: Generated/Synthetic
```
Type: Wait Time History, Capacity History
Purpose: ML Training
Records: ~500 synthetic entries
Generated: Via database initialization script

Stored In:
  MySQL: wait_time_history, capacity_history tables
```

---

## BLOCK KODE TERPENTING

### 1. AI Agent (LangChain) - `src/agent.py`

```python
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

class SmartReferralAgent:
    def __init__(self, db):
        self.tools = [
            Tool(name="FindNearestHospitals", 
                 func=self.find_nearest_hospitals),
            Tool(name="CheckHospitalCapacity", 
                 func=self.check_hospital_capacity),
            Tool(name="PredictWaitTime", 
                 func=self.predict_wait_time),
            Tool(name="CalculateDistance", 
                 func=self.calculate_distance)
        ]
        self.llm = ChatOpenAI(model="gpt-3.5-turbo")
        self.agent = initialize_agent(self.tools, self.llm)
    
    def recommend_hospital(self, lat, lon, severity, max_distance):
        """AI Agent autonomous recommendation"""
        prompt = f"""
        Patient at ({lat}, {lon}) with {severity} condition.
        Max distance: {max_distance} km.
        Find best hospital using available tools.
        """
        return self.agent.run(prompt)
```

### 2. ML Model (Random Forest) - `src/predictor.py`

```python
from sklearn.ensemble import RandomForestRegressor

class WaitTimePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100, 
            random_state=42
        )
    
    def train(self, db):
        """Train on historical wait time data"""
        wait_times = db.query(WaitTimeHistory).all()
        
        X = []  # Features
        y = []  # Labels
        
        for wt in wait_times:
            severity_map = {'low': 1, 'medium': 2, 
                          'high': 3, 'critical': 4}
            features = [
                wt.hospital_id,
                severity_map[wt.severity_level.value],
                wt.timestamp.hour,
                wt.timestamp.weekday()
            ]
            X.append(features)
            y.append(wt.wait_time_minutes)
        
        self.model.fit(np.array(X), np.array(y))
        self.is_trained = True
    
    def predict(self, hospital_id, severity):
        """Predict wait time in minutes"""
        severity_map = {'low': 1, 'medium': 2, 
                       'high': 3, 'critical': 4}
        hour = datetime.now().hour
        day = datetime.now().weekday()
        
        features = np.array([[
            hospital_id,
            severity_map[severity],
            hour, day
        ]])
        
        return int(self.model.predict(features)[0])
```

### 3. SATUSEHAT Integration - `src/satusehat_api.py`

```python
import requests
from datetime import datetime, timedelta

class SATUSEHATClient:
    def __init__(self):
        self.org_id = os.getenv('SATUSEHAT_ORG_ID')
        self.client_id = os.getenv('SATUSEHAT_CLIENT_ID')
        self.client_secret = os.getenv('SATUSEHAT_CLIENT_SECRET')
        self.auth_url = 'https://api-satusehat-stg.dto.kemkes.go.id/oauth2/v1'
        self.base_url = 'https://api-satusehat-stg.dto.kemkes.go.id/fhir-r4/v1'
    
    def get_access_token(self):
        """OAuth2 Client Credentials flow"""
        url = f"{self.auth_url}/accesstoken?grant_type=client_credentials"
        auth = (self.client_id, self.client_secret)
        
        response = requests.post(url, auth=auth, timeout=30)
        data = response.json()
        
        self.access_token = data.get('access_token')
        self.token_expires_at = datetime.now() + \
            timedelta(seconds=data.get('expires_in', 3600))
        
        return self.access_token
    
    def get_patients(self, count=100, page=1):
        """Fetch patient data from FHIR API"""
        params = {'_count': count, '_page': page}
        data = self._make_fhir_request('Patient', params)
        
        return data.get('entry', []) if data else []
    
    def get_service_requests(self, count=100, page=1):
        """Fetch referral data from FHIR API"""
        params = {'_count': count, '_page': page}
        data = self._make_fhir_request('ServiceRequest', params)
        
        return data.get('entry', []) if data else []
    
    def _make_fhir_request(self, endpoint, params=None):
        """Make authenticated FHIR API call"""
        if not self.access_token:
            self.get_access_token()
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers, 
                               params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        return None
```

### 4. Database Models - `src/models.py`

```python
from sqlalchemy import Column, Integer, String, Float, \
                       DateTime, Enum, ForeignKey

class Hospital(Base):
    __tablename__ = 'hospitals'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    total_beds = Column(Integer, default=0)
    available_beds = Column(Integer, default=0)
    type = Column(String(100))
    phone = Column(String(50))
    emergency_available = Column(Boolean, default=True)

class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True)
    bpjs_number = Column(String(50))
    name = Column(String(255), nullable=False)
    gender = Column(Enum(GenderEnum))
    date_of_birth = Column(DateTime)
    address = Column(Text)
    phone = Column(String(50))

class Referral(Base):
    __tablename__ = 'referrals'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    to_hospital_id = Column(Integer, ForeignKey('hospitals.id'))
    condition_description = Column(Text)
    severity_level = Column(Enum(SeverityEnum))
    predicted_wait_time = Column(Integer)
    status = Column(Enum(StatusEnum))
    referral_date = Column(DateTime)
```

### 5. Streamlit UI - `app.py`

```python
import streamlit as st
from streamlit_folium import folium_static
import folium

st.set_page_config(page_title="SmartRujuk AI", layout="wide")

with st.sidebar:
    st.markdown("### SmartRujuk+ AI")
    menu = st.selectbox("Menu", [
        "🏠 Dashboard",
        "🚑 Rujukan Baru",
        "🏥 Data Rumah Sakit",
        "👤 Data Pasien",
        "📊 Analisis & Prediksi"
    ])

def show_referral_form():
    st.subheader("🚑 Buat Rujukan Baru")
    
    # Input
    patient_name = st.text_input("Nama Pasien")
    bpjs_number = st.text_input("Nomor BPJS")
    patient_lat = st.number_input("Latitude")
    patient_lon = st.number_input("Longitude")
    condition = st.text_area("Deskripsi Kondisi")
    severity = st.selectbox("Tingkat Keparahan", 
                           ["low", "medium", "high", "critical"])
    
    # AI Recommendation
    if st.button("🔍 Cari Rumah Sakit Terbaik"):
        with st.spinner("Analyzing..."):
            recommendation = agent.recommend_hospital(
                patient_lat, patient_lon, severity, 50
            )
            
            # Display
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Hospital", 
                         recommendation['hospital_name'])
            with col2:
                st.metric("Distance", 
                         f"{recommendation['distance_km']:.2f} km")
            with col3:
                st.metric("Wait Time", 
                         f"{recommendation['predicted_wait_time']} min")
            
            # Map
            m = folium.Map(location=[patient_lat, patient_lon])
            folium.Marker([patient_lat, patient_lon], 
                         popup="Patient").add_to(m)
            folium.Marker([rec_lat, rec_lon], 
                         popup=recommendation['hospital_name']).add_to(m)
            folium_static(m, width=800, height=400)

if menu == "🚑 Rujukan Baru":
    show_referral_form()
```

### 6. CSV Data Loader - `src/csv_loader.py`

```python
import pandas as pd

class CSVDataLoader:
    def load_bpjs_faskes_csv(self, csv_path: str) -> int:
        """Load BPJS Faskes data from CSV"""
        df = pd.read_csv(csv_path)
        
        count = 0
        for _, row in df.iterrows():
            # Extract coordinates from Google Maps link
            lat, lon = self.extract_coordinates_from_gmaps_link(
                row['GMaps']
            )
            
            hospital = Hospital(
                name=row['NamaFaskes'],
                address=row['AlamatFaskes'],
                latitude=lat,
                longitude=lon,
                type=row['TipeFaskes']
            )
            self.db.add(hospital)
            count += 1
        
        self.db.commit()
        return count
    
    def extract_coordinates_from_gmaps_link(self, 
                                           gmaps_link: str):
        """Extract lat/lon from Google Maps URL"""
        # Pattern: ?q=LAT,LON
        match = re.search(r'q=(-?\d+\.?\d*),\s*(-?\d+\.?\d*)', 
                         str(gmaps_link))
        if match:
            return float(match.group(1)), float(match.group(2))
        return (0.0, 0.0)
```

---

## FILE STRUKTUR UNTUK PRESENTASI

```
smart-rujuk-agent-ai/
│
├── 🔴 app.py [MAIN] ← Jalankan ini
│
├── 📁 src/ [CORE LOGIC]
│   ├── agent.py           ← AI Agent (LangChain)
│   ├── predictor.py       ← ML Model (Random Forest)
│   ├── models.py          ← Database Models
│   ├── maps_api.py        ← Google Maps Integration
│   ├── satusehat_api.py   ← SATUSEHAT Integration
│   └── csv_loader.py      ← CSV Data Loading
│
├── 📁 database/ [DATA]
│   ├── init_db.py         ← Initialize database
│   ├── schema.sql         ← Database schema
│   └── load_all_datasets.py ← Complete pipeline
│
├── 📄 requirements.txt     ← Dependencies
├── 📄 .env.example        ← Config template
└── 📄 README.md           ← Documentation
```

---

## RINGKASAN: TEKNOLOGI vs FUNGSI

| Teknologi | Digunakan Untuk |
|-----------|-----------------|
| **Streamlit** | UI/Dashboard |
| **LangChain** | AI decision making |
| **scikit-learn** | Wait time prediction |
| **Google Maps** | Geolocation & routing |
| **SATUSEHAT API** | Patient & referral data |
| **MySQL** | Data persistence |
| **Folium** | Interactive maps |
| **Pandas/NumPy** | Data processing |
| **SQLAlchemy** | Database ORM |

---

## QUICK START (5 Menit Setup)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Setup
cp .env.example .env
# Edit credentials

# 3. Database
python database/init_db.py

# 4. Load Data
python database/load_all_datasets.py

# 5. Run
streamlit run app.py
# → http://localhost:8501
```

---

**SELESAI!** Gunakan file ini untuk presentasi yang cepat dan efektif. ✅
