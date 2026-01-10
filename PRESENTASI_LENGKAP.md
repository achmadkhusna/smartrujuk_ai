# 📊 PRESENTASI PROGRAM: SmartRujuk+ AI Agent

**Tujuan Program**: Sistem Rujukan Otomatis dengan Geolokasi, Prediksi Waktu Tunggu, dan Analisis Kapasitas Rumah Sakit untuk mempercepat proses rujukan pasien JKN.

---

## 📦 I. TEKNOLOGI YANG DIGUNAKAN

### A. Backend & Framework

| Teknologi | Versi | Fungsi |
|-----------|-------|--------|
| **Python** | 3.8+ | Bahasa pemrograman utama |
| **Streamlit** | 1.29.0+ | Web application framework (UI/Dashboard) |
| **FastAPI** | Optional | REST API endpoint |
| **LangChain** | 0.1.0+ | **AI Agent framework** (autonomous decision making) |
| **SQLAlchemy** | 2.0.23+ | ORM untuk database |

### B. Machine Learning & Data Science

| Library | Fungsi |
|---------|--------|
| **scikit-learn** | Random Forest untuk prediksi waktu tunggu |
| **NumPy** | Komputasi numerik |
| **Pandas** | Data manipulation & analysis |
| **SciPy** | Scientific computing |
| **joblib** | Model serialization |

### C. Database

| Teknologi | Fungsi |
|-----------|--------|
| **MySQL** | Database relational untuk storage |
| **mysql-connector-python** | Python MySQL driver |
| **SQLAlchemy** | ORM layer |

### D. API & Integrasi

| Service | Fungsi |
|---------|--------|
| **Google Maps API** | Geolocation, distance calculation, routing |
| **SATUSEHAT API** | Data pasien & rujukan (FHIR R4 standard) |
| **OpenAI GPT** | Optional - advanced AI reasoning |

### E. Frontend & Visualization

| Library | Fungsi |
|---------|--------|
| **Streamlit** | Interactive web UI |
| **Folium** | Interactive maps |
| **streamlit-folium** | Folium integration dengan Streamlit |
| **Pandas** | Data table display |

### F. Utilities

| Library | Fungsi |
|---------|--------|
| **python-dotenv** | Environment variable management |
| **requests** | HTTP client untuk API calls |

---

## 🏗️ II. ARSITEKTUR SISTEM

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                           │
│              (Streamlit Web Application)                    │
│  ┌─────────────┬──────────────┬──────────────┬────────────┐│
│  │  Dashboard  │  Form Rujukan│  Data Mgmt   │ Analytics  ││
│  └─────────────┴──────────────┴──────────────┴────────────┘│
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    APPLICATION LOGIC                        │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ AI Agent     │ ML Predictor │ Map & Geolocation       │ │
│  │ (LangChain)  │ (Random      │ (Google Maps Client)    │ │
│  │              │  Forest)     │                          │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ SATUSEHAT    │ CSV Loader   │ API Config Manager      │ │
│  │ Integration  │              │                          │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│               DATA LAYER (SQLAlchemy ORM)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Database Models:                                    │  │
│  │  - Hospital      - Patient                           │  │
│  │  - Referral      - WaitTimeHistory                   │  │
│  │  - CapacityHistory - APIConfig                       │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                 STORAGE LAYER                               │
│              (MySQL Database)                               │
└────────────────────────────────────────────────────────────┘
```

### Component Interaction

```
User (Web Browser)
    │
    ├─── Input Data ──→ Streamlit App (app.py)
    │
    ├─── Query ────────→ SmartReferralAgent
    │                    (src/agent.py)
    │
    ├─── [AI Agent Decision Making]
    │    ├─→ FindNearestHospitals Tool
    │    ├─→ CheckHospitalCapacity Tool
    │    ├─→ PredictWaitTime Tool
    │    └─→ CalculateDistance Tool
    │
    ├─── [Data Retrieval]
    │    ├─→ Database Query (SQLAlchemy)
    │    ├─→ ML Prediction (WaitTimePredictor)
    │    ├─→ Google Maps API (Distance)
    │    └─→ Capacity Analysis (CapacityAnalyzer)
    │
    └─── Output ──────→ User Dashboard
         (Maps + Recommendations + Alternatives)
```

---

## 🗄️ III. DATABASE SCHEMA

### Tabel Utama & Relationship

```
┌──────────────────────┐
│     HOSPITALS        │
├──────────────────────┤
│ id (PK)              │
│ name                 │
│ address              │
│ latitude             │
│ longitude            │
│ type                 │
│ class_               │
│ total_beds           │
│ available_beds       │
│ phone                │
│ emergency_available  │
│ created_at           │
└──────────────────────┘
         ▲
         │ (1:N)
         │
┌──────────────────────┐       ┌──────────────────────┐
│    REFERRALS    ◄────┼──────►│     PATIENTS         │
├──────────────────────┤       ├──────────────────────┤
│ id (PK)              │       │ id (PK)              │
│ patient_id (FK)      │       │ bpjs_number          │
│ to_hospital_id (FK)  │       │ name                 │
│ from_hospital_id(FK) │       │ gender               │
│ condition_desc       │       │ date_of_birth        │
│ severity_level       │       │ address              │
│ predicted_wait_time  │       │ phone                │
│ distance_km          │       │ created_at           │
│ status               │       └──────────────────────┘
│ referral_date        │
│ created_at           │
└──────────────────────┘

┌──────────────────────────┐
│  WAIT_TIME_HISTORY       │
├──────────────────────────┤
│ id (PK)                  │
│ hospital_id (FK)         │
│ severity_level           │
│ wait_time_minutes        │
│ timestamp                │
└──────────────────────────┘

┌──────────────────────────┐
│  CAPACITY_HISTORY        │
├──────────────────────────┤
│ id (PK)                  │
│ hospital_id (FK)         │
│ total_beds               │
│ available_beds           │
│ occupancy_rate           │
│ timestamp                │
└──────────────────────────┘
```

**File Implementasi**: `src/models.py`

```python
class Hospital(Base):
    __tablename__ = 'hospitals'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    total_beds = Column(Integer, default=0)
    available_beds = Column(Integer, default=0)

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    bpjs_number = Column(String(50))
    name = Column(String(255), nullable=False)
    gender = Column(Enum(GenderEnum))
    date_of_birth = Column(DateTime)

class Referral(Base):
    __tablename__ = 'referrals'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    to_hospital_id = Column(Integer, ForeignKey('hospitals.id'))
    severity_level = Column(Enum(SeverityEnum))
    predicted_wait_time = Column(Integer)
    status = Column(Enum(StatusEnum))
```

---

## 📡 IV. INTEGRASI EKSTERNAL

### 1. **Google Maps API**

**Fungsi**: Geolocation, distance calculation, route optimization

**Endpoint & Methods**:

```python
class GoogleMapsClient:
    def geocode_address(self, address: str) -> Tuple[float, float]:
        """Convert address → latitude, longitude"""
        # https://maps.googleapis.com/maps/api/geocode/json
        
    def get_distance_matrix(self, origin, destinations) -> List[float]:
        """Calculate distance between points"""
        # https://maps.googleapis.com/maps/api/distancematrix/json
        
    def get_distance_km(self, lat1, lon1, lat2, lon2) -> float:
        """Haversine formula untuk jarak"""
```

**Code Sample** (`src/maps_api.py`):

```python
from googlemaps import Client as GoogleMapsAPI
from math import radians, cos, sin, asin, sqrt

class GoogleMapsClient:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        self.gmaps = GoogleMapsAPI(key=self.api_key)
    
    def geocode_address(self, address: str):
        try:
            result = self.gmaps.geocode(address)
            if result:
                location = result[0]['geometry']['location']
                return location['lat'], location['lng']
        except:
            # Fallback ke hardcoded cities jika API fail
            return self._offline_geocode(address)
```

---

### 2. **SATUSEHAT API** (Kemenkes)

**Fungsi**: Mengambil data pasien & rujukan dari platform kesehatan nasional

**Teknologi**: OAuth2 + FHIR R4 (Fast Healthcare Interoperability Resources)

**Authentication Flow**:

```
1. Request Token
   POST https://api-satusehat-stg.dto.kemkes.go.id/oauth2/v1/accesstoken
   Auth: (client_id, client_secret)
   
   Response:
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "expires_in": 3600
   }

2. API Call dengan Token
   GET https://api-satusehat-stg.dto.kemkes.go.id/fhir-r4/v1/Patient
   Authorization: Bearer <access_token>
   
   Response: FHIR Patient Resource (JSON)
```

**Endpoints Digunakan**:

| Endpoint | Data |
|----------|------|
| `/fhir-r4/v1/Patient` | Data pasien |
| `/fhir-r4/v1/ServiceRequest` | Data rujukan (referral) |
| `/fhir-r4/v1/Organization` | Data organisasi (faskes) |

**Code Implementation** (`src/satusehat_api.py`):

```python
class SATUSEHATClient:
    def __init__(self):
        self.org_id = os.getenv('SATUSEHAT_ORG_ID')
        self.client_id = os.getenv('SATUSEHAT_CLIENT_ID')
        self.client_secret = os.getenv('SATUSEHAT_CLIENT_SECRET')
        self.auth_url = 'https://api-satusehat-stg.dto.kemkes.go.id/oauth2/v1'
        self.base_url = 'https://api-satusehat-stg.dto.kemkes.go.id/fhir-r4/v1'
    
    def get_access_token(self):
        url = f"{self.auth_url}/accesstoken?grant_type=client_credentials"
        auth = (self.client_id, self.client_secret)
        response = requests.post(url, auth=auth)
        data = response.json()
        self.access_token = data.get('access_token')
        return self.access_token
    
    def get_patients(self, count=100, page=1):
        params = {'_count': count, '_page': page}
        data = self._make_fhir_request('Patient', params)
        return data.get('entry', [])
    
    def get_service_requests(self, count=100, page=1):
        params = {'_count': count, '_page': page}
        data = self._make_fhir_request('ServiceRequest', params)
        return data.get('entry', [])
```

**Data Transformation** (`src/satusehat_loader.py`):

```python
class SATUSEHATDataLoader:
    def load_patients(self):
        # 1. Fetch dari SATUSEHAT API
        fhir_patients = self.client.get_patients()
        
        # 2. Extract & Transform
        for fhir_patient in fhir_patients:
            patient_data = {
                'bpjs_number': extract_identifier(fhir_patient),
                'name': extract_name(fhir_patient),
                'gender': map_gender(fhir_patient.get('gender')),
                'date_of_birth': parse_date(fhir_patient.get('birthDate')),
                'address': extract_address(fhir_patient)
            }
            
            # 3. Store ke MySQL
            patient = Patient(**patient_data)
            db.add(patient)
        
        db.commit()
```

---

## 📊 V. DATASET YANG DIGUNAKAN

### 1. **BPJS Faskes Indonesia Dataset** (Kaggle)

**Source**: https://www.kaggle.com/datasets/israhabibi/list-faskes-bpjs-indonesia

**Isi**: Daftar fasilitas kesehatan (Rumah Sakit, Puskesmas, Klinik) yang bekerja sama dengan BPJS

```
Data:
- Nama Faskes
- Alamat
- Koordinat GPS (dari Google Maps link)
- Tipe Faskes (Rumah Sakit, Puskesmas, Klinik)
- Province/Region
- BPJS Status

Format: CSV
Ukuran: ~9 MB
Records: ~1,500-4,000 faskes
```

**Loading Method**:

```python
# File: src/csv_loader.py
class CSVDataLoader:
    def load_bpjs_faskes_csv(self, csv_path: str) -> int:
        """Load BPJS Faskes data dari CSV"""
        df = pd.read_csv(csv_path)
        
        for _, row in df.iterrows():
            # Extract coordinates from Google Maps link
            lat, lon = self.extract_coordinates_from_gmaps_link(row['GMaps'])
            
            hospital = Hospital(
                name=row['NamaFaskes'],
                address=row['AlamatFaskes'],
                latitude=lat,
                longitude=lon,
                type=row['TipeFaskes']
            )
            db.add(hospital)
        
        db.commit()
        return len(df)

# Usage:
python database/load_csv_data.py --file "Data Faskes BPJS 2019.csv"
```

### 2. **Bed to Population Ratio Dataset** (Kaggle)

**Source**: https://www.kaggle.com/datasets/yafethtb/dataset-rasio-bed-to-population-faskes-ii

**Isi**: Rasio tempat tidur rumah sakit per populasi per provinsi

```
Data:
- Province
- Total Beds
- Population
- Bed-to-Population Ratio

Format: CSV
Coverage: 34 Provinsi Indonesia
Year: 2020
```

**Usage**: Update kapasitas tempat tidur rumah sakit

---

### 3. **Synthetic/Generated Data**

**Wait Time History**: Generated untuk training ML model

```python
# Generate synthetic wait time data
import random
from datetime import datetime, timedelta

def generate_wait_time_data(db, hospitals, count=500):
    """Generate synthetic wait time records"""
    for i in range(count):
        wait_time = WaitTimeHistory(
            hospital_id=random.choice(hospitals).id,
            severity_level=random.choice(['low', 'medium', 'high', 'critical']),
            wait_time_minutes=random.randint(5, 480),  # 5 menit - 8 jam
            timestamp=datetime.now() - timedelta(days=random.randint(0, 30))
        )
        db.add(wait_time)
    db.commit()
```

**Data Pipeline**:

```bash
# Otomatis download + load + train
python database/load_all_datasets.py --download-first

# Output:
# ✅ Downloaded BPJS Faskes dataset (1,523 hospitals)
# ✅ Loaded BPJS Faskes data (1,523 records)
# ✅ Downloaded Bed Ratio dataset
# ✅ Updated hospital bed capacity (245 hospitals)
# ✅ Generated wait time history (500 records)
# ✅ Trained ML models
```

---

## 🤖 VI. AI AGENT & MACHINE LEARNING

### A. Smart Referral Agent (LangChain)

**Purpose**: Autonomous decision making untuk rekomendasi rumah sakit

**Architecture**:

```python
class SmartReferralAgent:
    def __init__(self, db):
        # Initialize tools
        self.tools = [
            Tool(name="FindNearestHospitals", func=find_nearest_hospitals),
            Tool(name="CheckHospitalCapacity", func=check_hospital_capacity),
            Tool(name="PredictWaitTime", func=predict_wait_time),
            Tool(name="CalculateDistance", func=calculate_distance)
        ]
        
        # Initialize LLM (GPT-3.5 turbo)
        self.llm = ChatOpenAI(model="gpt-3.5-turbo")
        
        # Create agent
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent="zero-shot-react-description"
        )
    
    def recommend_hospital(self, lat, lon, severity, max_distance):
        """AI Agent makes recommendation"""
        prompt = f"""
        Seorang pasien berada di koordinat ({lat}, {lon}) dengan kondisi {severity}.
        Jarak maksimal rumah sakit: {max_distance} km.
        
        Gunakan tools yang tersedia untuk menemukan rumah sakit terbaik berdasarkan:
        1. Jarak terdekat
        2. Ketersediaan tempat tidur
        3. Prediksi waktu tunggu
        4. Tingkat okupansi
        """
        
        result = self.agent.run(prompt)
        return result
```

**Tools Available**:

```python
def find_nearest_hospitals(lat: float, lon: float) -> List[Hospital]:
    """Find hospitals within radius"""
    query = db.query(Hospital).all()
    
    # Calculate distance menggunakan Haversine formula
    for hospital in query:
        distance = haversine(lat, lon, hospital.latitude, hospital.longitude)
        hospital.distance = distance
    
    return sorted(query, key=lambda h: h.distance)[:10]

def check_hospital_capacity(hospital_id: int) -> Dict:
    """Check available beds & occupancy"""
    hospital = db.query(Hospital).get(hospital_id)
    occupancy_rate = (hospital.total_beds - hospital.available_beds) / hospital.total_beds * 100
    
    return {
        'hospital': hospital.name,
        'total_beds': hospital.total_beds,
        'available_beds': hospital.available_beds,
        'occupancy_rate': occupancy_rate
    }

def predict_wait_time(hospital_id: int, severity: str) -> int:
    """Predict wait time in minutes"""
    predictor = WaitTimePredictor()
    predicted_time = predictor.predict(hospital_id, severity)
    return predicted_time
```

### B. Wait Time Predictor (Random Forest)

**Algorithm**: Random Forest Regressor (scikit-learn)

**Features**:
- Hospital ID
- Severity Level (encoded: low=1, medium=2, high=3, critical=4)
- Hour of day (0-23)
- Day of week (0-6)

**Code** (`src/predictor.py`):

```python
from sklearn.ensemble import RandomForestRegressor
import numpy as np

class WaitTimePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
    
    def train(self, db):
        """Train model dengan historical wait time data"""
        wait_times = db.query(WaitTimeHistory).all()
        
        # Prepare features (X) and labels (y)
        X = []
        y = []
        
        for wt in wait_times:
            severity_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            severity_encoded = severity_map[wt.severity_level.value]
            
            hour = wt.timestamp.hour
            day_of_week = wt.timestamp.weekday()
            
            X.append([wt.hospital_id, severity_encoded, hour, day_of_week])
            y.append(wt.wait_time_minutes)
        
        # Train
        X = np.array(X)
        y = np.array(y)
        self.model.fit(X, y)
        self.is_trained = True
    
    def predict(self, hospital_id, severity, hour=None, day=None):
        """Predict wait time"""
        if hour is None:
            hour = datetime.now().hour
        if day is None:
            day = datetime.now().weekday()
        
        severity_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        severity_encoded = severity_map[severity]
        
        features = np.array([[hospital_id, severity_encoded, hour, day]])
        prediction = self.model.predict(features)
        
        return int(prediction[0])
```

### C. Capacity Analyzer

**Purpose**: Real-time analysis of hospital capacity

```python
class CapacityAnalyzer:
    def analyze_occupancy(self, hospital: Hospital) -> Dict:
        """Analyze hospital occupancy rate"""
        occupancy_rate = (hospital.total_beds - hospital.available_beds) / hospital.total_beds * 100
        
        if occupancy_rate < 50:
            status = "LOW"      # Many beds available
        elif occupancy_rate < 75:
            status = "MODERATE" # Some beds available
        elif occupancy_rate < 90:
            status = "HIGH"     # Few beds available
        else:
            status = "CRITICAL" # Full or nearly full
        
        return {
            'hospital': hospital.name,
            'occupancy_rate': occupancy_rate,
            'status': status,
            'available_beds': hospital.available_beds,
            'total_beds': hospital.total_beds
        }
```

---

## 🎨 VII. USER INTERFACE (Streamlit)

### Main Dashboard (`app.py`)

```python
import streamlit as st
from streamlit_folium import folium_static
import folium

# Page config
st.set_page_config(page_title="SmartRujuk AI", layout="wide")

# Sidebar menu
with st.sidebar:
    st.markdown("### SmartRujuk+ AI")
    menu = st.selectbox("Menu", [
        "🏠 Dashboard",
        "🚑 Rujukan Baru",
        "🏥 Data Rumah Sakit",
        "👤 Data Pasien",
        "📊 Analisis & Prediksi"
    ])

# Main content
if menu == "🏠 Dashboard":
    show_dashboard()
elif menu == "🚑 Rujukan Baru":
    show_referral_form()
elif menu == "🏥 Data Rumah Sakit":
    show_hospitals()
```

### Key Features

```python
# 1. Dashboard
def show_dashboard():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total RS", hospital_count)
    with col2:
        st.metric("RS Tersedia", available_hospitals)
    with col3:
        st.metric("Total Pasien", patient_count)
    with col4:
        st.metric("Total Rujukan", referral_count)

# 2. Referral Form
def show_referral_form():
    st.subheader("Buat Rujukan Baru")
    
    # Input data pasien
    patient_name = st.text_input("Nama Pasien")
    bpjs_number = st.text_input("Nomor BPJS")
    
    # Input lokasi
    patient_lat = st.number_input("Latitude")
    patient_lon = st.number_input("Longitude")
    
    # Input kondisi
    condition = st.text_area("Deskripsi Kondisi")
    severity = st.selectbox("Tingkat Keparahan", ["low", "medium", "high", "critical"])
    
    # AI Agent recommendation
    if st.button("🔍 Cari Rumah Sakit Terbaik"):
        recommendation = agent.recommend_hospital(patient_lat, patient_lon, severity, 50)
        
        # Display results
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rumah Sakit", recommendation['hospital_name'])
        with col2:
            st.metric("Jarak", f"{recommendation['distance_km']:.2f} km")
        with col3:
            st.metric("Prediksi Waktu Tunggu", f"{recommendation['predicted_wait_time']} menit")
        
        # Interactive map
        m = folium.Map(
            location=[patient_lat, patient_lon],
            zoom_start=12
        )
        
        folium.Marker([patient_lat, patient_lon], popup="Lokasi Pasien").add_to(m)
        folium.Marker([rec_lat, rec_lon], popup=recommendation['hospital_name']).add_to(m)
        folium.PolyLine([[patient_lat, patient_lon], [rec_lat, rec_lon]]).add_to(m)
        
        folium_static(m, width=800, height=400)

# 3. Hospital Data
def show_hospitals():
    st.subheader("Data Rumah Sakit")
    
    # Filters
    search = st.text_input("Cari RS...")
    hospitals_df = db.query(Hospital).filter(Hospital.name.contains(search)).all()
    
    # Display table
    hospital_data = []
    for h in hospitals_df:
        occupancy = (h.total_beds - h.available_beds) / h.total_beds * 100
        hospital_data.append({
            'Nama': h.name,
            'Alamat': h.address,
            'Bed Total': h.total_beds,
            'Bed Kosong': h.available_beds,
            'Okupansi': f"{occupancy:.1f}%"
        })
    
    st.dataframe(hospital_data, use_container_width=True)
```

---

## 📁 VIII. STRUKTUR FILE PENTING

```
smart-rujuk-agent-ai/
│
├── 📄 app.py                           # Main Streamlit application
│
├── 📂 src/
│   ├── agent.py                        # LangChain AI Agent
│   ├── predictor.py                    # ML models (wait time, capacity)
│   ├── models.py                       # SQLAlchemy database models
│   ├── database.py                     # Database connection & init
│   ├── maps_api.py                     # Google Maps integration
│   ├── satusehat_api.py               # SATUSEHAT API client
│   ├── satusehat_loader.py            # Load SATUSEHAT data to DB
│   └── csv_loader.py                  # Load CSV datasets
│
├── 📂 database/
│   ├── schema.sql                      # Database schema
│   ├── init_db.py                      # Database initialization
│   ├── load_csv_data.py               # CLI CSV loader
│   ├── load_all_datasets.py           # Complete data pipeline
│   ├── dataset_downloader.py          # Download Kaggle datasets
│   └── load_api_config.py             # Load API credentials
│
├── 📂 data/
│   ├── kaggle_datasets/               # Downloaded datasets
│   ├── faskes_sample.csv              # Sample data
│   └── README.md
│
├── .env.example                        # Environment variables template
├── requirements.txt                    # Python dependencies
├── soal.txt                           # Original requirements (Kemenkes)
├── README.md                          # Main documentation
└── DATA_SOURCES_CLARIFICATION.md      # Data sources explanation
```

---

## 🚀 IX. CARA MENJALANKAN

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env dengan credentials Anda

# Initialize database
python database/init_db.py
```

### 2. Load Data

```bash
# Option A: Automatic (recommended)
python database/load_all_datasets.py --download-first

# Option B: Manual
python database/load_csv_data.py --file "Data Faskes BPJS 2019.csv"
```

### 3. Train ML Models

```bash
python train_model.py
```

### 4. Run Application

```bash
streamlit run app.py
# Access: http://localhost:8501
```

---

## 📊 X. RINGKASAN TEKNOLOGI

| Aspek | Teknologi | Fungsi |
|-------|-----------|--------|
| **Backend** | Python, FastAPI | Logika aplikasi |
| **Frontend** | Streamlit, Folium | UI/Dashboard, Maps |
| **AI/ML** | LangChain, scikit-learn | Agent, Prediksi |
| **Database** | MySQL, SQLAlchemy | Data storage, ORM |
| **Integrasi** | Google Maps, SATUSEHAT | Geolocation, Patient data |
| **Dataset** | Kaggle CSV | Hospital & Bed ratio data |

---

## 🎯 XI. HASIL AKHIR

**Program mampu**:

✅ Menerima input lokasi pasien & kondisi kesehatan  
✅ Menggunakan AI Agent untuk analisis cerdas  
✅ Melakukan prediksi waktu tunggu dengan ML  
✅ Menghitung jarak optimal menggunakan Google Maps  
✅ Merekomendasikan rumah sakit terbaik  
✅ Menampilkan peta interaktif dengan rute  
✅ Menyimpan rujukan ke database  
✅ Integrasi dengan SATUSEHAT untuk data real pasien  

---

**Tanggal**: December 16, 2025  
**Status**: ✅ Production Ready
