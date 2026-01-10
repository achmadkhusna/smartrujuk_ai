# System Architecture - SmartRujuk+ AI Agent

## Overview

SmartRujuk+ adalah sistem rujukan otomatis berbasis AI yang mengintegrasikan geolokasi, prediksi waktu tunggu, dan analisis kapasitas rumah sakit untuk mempercepat proses rujukan pasien JKN.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│                    (Streamlit Web App)                       │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  Dashboard   │   Rujukan    │     Data     │   Analytics    │
│              │     Baru     │  Management  │  & Prediction  │
└──────────────┴──────────────┴──────────────┴────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                          │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   AI Agent   │  Predictive  │     API      │   Database     │
│  (LangChain) │    Models    │ Integration  │    Manager     │
│              │  (Sklearn)   │              │  (SQLAlchemy)  │
└──────────────┴──────────────┴──────────────┴────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  MySQL DB    │ Google Maps  │  SATUSEHAT   │  OpenAI GPT    │
│              │     API      │     API      │   (Optional)   │
└──────────────┴──────────────┴──────────────┴────────────────┘
```

## Component Details

### 1. User Interface Layer (Streamlit)

**Purpose**: Provide interactive web interface for users

**Components**:
- `app.py`: Main Streamlit application
- Dashboard: Overview and statistics
- Rujukan Baru Form: Create new referrals
- Data Management: Hospital and patient CRUD
- Analytics Dashboard: Visualizations and predictions

**Key Features**:
- Responsive design
- Interactive maps (Folium)
- Real-time data updates
- Form validation

### 2. Application Layer

#### 2.1 AI Agent (`src/agent.py`)

**Purpose**: Intelligent decision making for hospital recommendations

**Technologies**: LangChain, OpenAI (optional)

**Key Methods**:
```python
class SmartReferralAgent:
    def recommend_hospital(patient_lat, patient_lon, severity_level, max_distance)
        # Returns best hospital recommendation
        
    def find_nearest_hospitals(location)
        # Returns list of nearby hospitals
        
    def check_hospital_capacity(hospital_id)
        # Returns capacity analysis
        
    def predict_wait_time(hospital_id, severity)
        # Returns predicted wait time
```

**Decision Algorithm**:
```
For each hospital within max_distance:
    1. Calculate distance using Haversine formula
    2. Analyze capacity (occupancy rate)
    3. Predict wait time using ML model
    4. Calculate composite score:
       - Critical cases: 70% distance + 30% wait_time
       - Non-critical: 40% distance + 30% wait_time + 30% capacity
    5. Sort by score (lower is better)
    6. Return best option + alternatives
```

#### 2.2 Predictive Models (`src/predictor.py`)

**Purpose**: Machine learning for wait time prediction and capacity analysis

**Technologies**: Scikit-learn, NumPy

**Components**:

1. **WaitTimePredictor**
   - Algorithm: Random Forest Regressor
   - Features: hospital_id, severity_level, hour_of_day, day_of_week
   - Training: Historical wait time data
   - Output: Predicted wait time in minutes

2. **CapacityAnalyzer**
   - Real-time capacity calculation
   - Occupancy rate: (total_beds - available_beds) / total_beds
   - Status classification: low, moderate, high, critical
   - Trending hospitals identification

**Model Training**:
```python
# Features
X = [hospital_id, severity_encoded, hour, day_of_week]
y = wait_time_minutes

# Training
model = RandomForestRegressor(n_estimators=100)
model.fit(X, y)

# Prediction
predicted_time = model.predict(features)
```

#### 2.3 API Integration

**Google Maps API** (`src/maps_api.py`):
```python
class GoogleMapsClient:
    - calculate_distance(lat1, lon1, lat2, lon2)
    - get_distance_matrix(origins, destinations)
    - get_directions(origin, destination)
    - geocode_address(address)
```

**SATUSEHAT API** (`src/satusehat_api.py`):
```python
class SATUSEHATClient:
    - get_access_token()
    - get_organizations()  # Hospitals
    - get_location(location_id)
```

#### 2.4 Database Manager (`src/database.py`, `src/models.py`)

**ORM**: SQLAlchemy

**Models**:
- Hospital: Healthcare facilities
- Patient: Patient records
- Referral: Referral transactions
- CapacityHistory: Historical capacity data
- WaitTimeHistory: Historical wait time data

### 3. Data Layer

#### Database Schema

**hospitals**
```sql
id, name, address, latitude, longitude, type, class, 
total_beds, available_beds, phone, emergency_available,
created_at, updated_at
```

**patients**
```sql
id, bpjs_number, name, date_of_birth, gender, address, 
phone, created_at, updated_at
```

**referrals**
```sql
id, patient_id, from_hospital_id, to_hospital_id,
condition_description, severity_level, status,
predicted_wait_time, actual_wait_time, distance_km,
referral_date, acceptance_date, completion_date, notes,
created_at, updated_at
```

**capacity_history**
```sql
id, hospital_id, available_beds, occupied_beds, timestamp
```

**wait_time_history**
```sql
id, hospital_id, severity_level, wait_time_minutes, timestamp
```

## Data Flow

### Referral Creation Flow

```
User Input
  ↓
1. Select/Create Patient
  ↓
2. Input Location & Condition
  ↓
3. AI Agent Analysis
   ├─ Query Available Hospitals from DB
   ├─ Calculate Distances (Google Maps API)
   ├─ Analyze Capacity (CapacityAnalyzer)
   ├─ Predict Wait Time (ML Model)
   └─ Score & Rank Hospitals
  ↓
4. Display Recommendations
   ├─ Best Hospital
   ├─ Map with Route
   └─ Alternative Options
  ↓
5. User Confirms
  ↓
6. Save to Database
  ↓
7. Update Capacity
```

### Prediction Model Training Flow

```
Historical Data Collection
  ↓
1. Gather Wait Time History
  ↓
2. Feature Engineering
   - Hospital ID
   - Severity Level (encoded)
   - Temporal features (hour, day)
  ↓
3. Train Random Forest Model
  ↓
4. Validate Predictions
  ↓
5. Deploy for Real-time Predictions
```

## API Endpoints (Internal)

### Hospital Recommendation

```python
agent.recommend_hospital(
    patient_lat: float,
    patient_lon: float,
    severity_level: str,  # 'low', 'medium', 'high', 'critical'
    max_distance: float = 50.0  # km
) -> Dict
```

**Response**:
```json
{
    "success": true,
    "hospital_id": 1,
    "hospital_name": "RSUP Dr. Cipto Mangunkusumo",
    "hospital_address": "Jl. Diponegoro No.71, Jakarta",
    "latitude": -6.1862,
    "longitude": 106.8311,
    "distance_km": 3.45,
    "predicted_wait_time": 45,
    "available_beds": 45,
    "occupancy_rate": 82.0,
    "alternatives": [...]
}
```

### Wait Time Prediction

```python
predictor.predict_wait_time(
    hospital_id: int,
    severity_level: str
) -> int  # minutes
```

### Capacity Analysis

```python
analyzer.analyze_hospital_capacity(
    db: Session,
    hospital_id: int
) -> Dict
```

**Response**:
```json
{
    "status": "moderate",
    "available_beds": 45,
    "total_beds": 250,
    "occupancy_rate": 82.0,
    "emergency_available": true
}
```

## Scalability Considerations

### Current Implementation
- Single server deployment
- MySQL database
- Synchronous processing
- Suitable for: Small to medium healthcare networks (10-100 hospitals)

### Scaling Strategies

**Horizontal Scaling**:
- Deploy multiple Streamlit instances behind load balancer
- Use Redis for session management
- Implement database read replicas

**Caching**:
```python
@st.cache_data(ttl=300)
def get_hospitals():
    return db.query(Hospital).all()
```

**Async Processing**:
- Queue system (Celery + Redis) for ML predictions
- Background jobs for data synchronization
- Webhook notifications for referral updates

**Database Optimization**:
- Partitioning for historical tables
- Materialized views for analytics
- Index optimization on query patterns

## Security Architecture

### Authentication & Authorization
- Environment-based configuration
- API key management in .env
- (Future) Role-based access control (RBAC)

### Data Protection
- MySQL user permissions
- SQL injection prevention (ORM)
- Input sanitization (Streamlit)
- HTTPS in production

### API Security
- API key rotation policy
- Rate limiting for external APIs
- Error message sanitization

## Monitoring & Logging

### Metrics to Track
- Referral creation rate
- API response times
- Prediction accuracy
- Database query performance
- Hospital availability changes

### Logging Strategy
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smartrujuk.log'),
        logging.StreamHandler()
    ]
)
```

## Deployment Architecture

### Development
```
Local Machine
├── MySQL (localhost:3306)
├── Streamlit Dev Server (localhost:8501)
└── Python Environment (venv)
```

### Production (Recommended)
```
Cloud Infrastructure (AWS/GCP/Azure)
├── Application Server (EC2/Compute Engine)
│   ├── Nginx (Reverse Proxy)
│   ├── Streamlit App (Gunicorn)
│   └── ML Models
├── Database (RDS/Cloud SQL)
│   └── MySQL (managed service)
├── Cache Layer (ElastiCache/Memorystore)
│   └── Redis
└── Storage (S3/Cloud Storage)
    └── Model artifacts, logs
```

## Future Enhancements

1. **Real-time Updates**
   - WebSocket for live capacity updates
   - Push notifications for referral status

2. **Advanced ML**
   - Deep learning for prediction
   - NLP for condition analysis
   - Patient outcome prediction

3. **Mobile App**
   - React Native/Flutter
   - Offline mode
   - GPS integration

4. **Integration**
   - EMR systems (SIMRS)
   - Ambulance tracking
   - Telemedicine platforms

5. **Analytics**
   - Predictive analytics dashboard
   - Trend analysis
   - Resource optimization

## Performance Benchmarks

| Operation | Target | Current |
|-----------|--------|---------|
| Hospital recommendation | < 1s | ~0.5s |
| Wait time prediction | < 100ms | ~50ms |
| Map rendering | < 2s | ~1.5s |
| Database query (hospitals) | < 50ms | ~20ms |
| Page load time | < 3s | ~2s |

## Technology Stack Summary

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend | Streamlit | 1.29.0 |
| Backend | Python | 3.8+ |
| Database | MySQL | 5.7+ |
| ORM | SQLAlchemy | 2.0.23 |
| ML Framework | Scikit-learn | 1.3.2 |
| AI Agent | LangChain | 0.1.0 |
| Maps | Folium | 0.15.1 |
| API Client | googlemaps | 4.10.0 |

---

For implementation details, see code documentation in respective modules.
