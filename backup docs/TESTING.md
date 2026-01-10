# Testing Guide - SmartRujuk+ AI Agent

## Manual Testing Checklist

### 1. Installation & Setup ✓

#### Test Database Connection
```bash
python3 -c "from src.database import engine; engine.connect(); print('✅ Connection OK')"
```

Expected: `✅ Connection OK`

#### Test Environment Variables
```bash
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('DB_HOST:', os.getenv('DB_HOST')); print('GOOGLE_MAPS_API_KEY:', os.getenv('GOOGLE_MAPS_API_KEY')[:20] + '...')"
```

Expected: Should print your configuration values

### 2. Database Models ✓

#### Test Model Creation
```bash
python3 database/init_db.py
```

Expected Output:
```
=== SmartRujuk+ Database Initialization ===
Creating database tables...
Tables created successfully!
Adding sample hospitals...
10 sample hospitals added!
Adding sample patients...
5 sample patients added!
Adding sample history data...
Historical data added!

✅ Database initialization completed successfully!
```

#### Verify Data
```bash
mysql -u root -p smartrujuk_db -e "SELECT COUNT(*) as hospital_count FROM hospitals;"
mysql -u root -p smartrujuk_db -e "SELECT COUNT(*) as patient_count FROM patients;"
```

Expected: 10 hospitals, 5 patients

### 3. API Integrations ✓

#### Test Google Maps API
```python
from src.maps_api import GoogleMapsClient

client = GoogleMapsClient()

# Test distance calculation
distance = client.calculate_distance(-6.2088, 106.8456, -6.1862, 106.8311)
print(f"Distance: {distance} km")  # Expected: ~3-5 km

# Test geocoding (if API key is valid)
coords = client.geocode_address("Jakarta")
print(f"Jakarta coordinates: {coords}")  # Expected: (-6.2088, 106.8456) approx
```

#### Test SATUSEHAT API
```python
from src.satusehat_api import SATUSEHATClient

client = SATUSEHATClient()

# Test authentication
token = client.get_access_token()
print(f"Token received: {token is not None}")  # Expected: True (if credentials valid)
```

### 4. AI Agent ✓

#### Test Hospital Recommendation
```python
from src.database import SessionLocal
from src.agent import SmartReferralAgent

db = SessionLocal()
agent = SmartReferralAgent(db)

# Test recommendation
result = agent.recommend_hospital(
    patient_lat=-6.2088,
    patient_lon=106.8456,
    severity_level='high',
    max_distance=50.0
)

print(f"Success: {result['success']}")
print(f"Hospital: {result.get('hospital_name', 'N/A')}")
print(f"Distance: {result.get('distance_km', 'N/A')} km")

db.close()
```

Expected: Should return a hospital recommendation

### 5. Predictive Models ✓

#### Test Wait Time Predictor
```python
from src.database import SessionLocal
from src.predictor import WaitTimePredictor

db = SessionLocal()
predictor = WaitTimePredictor()

# Train model
predictor.train(db)

# Test prediction
wait_time = predictor.predict_wait_time(
    hospital_id=1,
    severity_level='critical'
)

print(f"Predicted wait time: {wait_time} minutes")
# Expected: 5-60 minutes depending on training data

db.close()
```

#### Test Capacity Analyzer
```python
from src.database import SessionLocal
from src.predictor import CapacityAnalyzer

db = SessionLocal()
analyzer = CapacityAnalyzer()

# Analyze capacity
capacity = analyzer.analyze_hospital_capacity(db, hospital_id=1)

print(f"Status: {capacity['status']}")
print(f"Available beds: {capacity['available_beds']}")
print(f"Occupancy rate: {capacity['occupancy_rate']}%")

db.close()
```

### 6. Streamlit Application ✓

#### Run Application
```bash
streamlit run app.py
```

#### Test Cases in UI

**Dashboard:**
- ✓ Should show metrics (Total RS, RS Tersedia, Total Pasien, Total Rujukan)
- ✓ Map should load and show hospital markers
- ✓ Recent referrals table should display

**Rujukan Baru:**
- ✓ Can select existing patient
- ✓ Can create new patient
- ✓ Can input location (coordinates or address)
- ✓ Can describe condition and select severity
- ✓ Click "Cari Rumah Sakit Terbaik" should show recommendations
- ✓ Map should show patient location and hospital location with route
- ✓ Can confirm and create referral

**Data Rumah Sakit:**
- ✓ Table displays all hospitals
- ✓ Can add new hospital
- ✓ Data persists after adding

**Data Pasien:**
- ✓ Table displays all patients
- ✓ Shows BPJS numbers and contact info

**Analisis & Prediksi:**
- ✓ Capacity analysis shows all hospitals with status
- ✓ Wait time prediction shows predictions for all severity levels
- ✓ Statistics show referral distribution

## Automated Testing

### Unit Tests

Create `tests/test_models.py`:
```python
import unittest
from src.models import Hospital, Patient, GenderEnum

class TestModels(unittest.TestCase):
    def test_hospital_creation(self):
        hospital = Hospital(
            name="Test Hospital",
            address="Test Address",
            latitude=-6.2088,
            longitude=106.8456,
            total_beds=100,
            available_beds=50
        )
        self.assertEqual(hospital.name, "Test Hospital")
        self.assertEqual(hospital.total_beds, 100)
    
    def test_patient_creation(self):
        patient = Patient(
            bpjs_number="1234567890",
            name="Test Patient",
            gender=GenderEnum.M
        )
        self.assertEqual(patient.name, "Test Patient")

if __name__ == '__main__':
    unittest.main()
```

Run: `python -m unittest tests/test_models.py`

### Integration Tests

Create `tests/test_agent.py`:
```python
import unittest
from src.database import SessionLocal
from src.agent import SmartReferralAgent

class TestAgent(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.agent = SmartReferralAgent(self.db)
    
    def tearDown(self):
        self.db.close()
    
    def test_recommend_hospital(self):
        result = self.agent.recommend_hospital(
            patient_lat=-6.2088,
            patient_lon=106.8456,
            severity_level='medium',
            max_distance=50.0
        )
        self.assertTrue(result['success'])
        self.assertIn('hospital_name', result)
        self.assertIn('distance_km', result)

if __name__ == '__main__':
    unittest.main()
```

## Performance Testing

### Load Testing

Test with multiple concurrent requests:

```python
import time
from concurrent.futures import ThreadPoolExecutor
from src.database import SessionLocal
from src.agent import SmartReferralAgent

def test_recommendation():
    db = SessionLocal()
    agent = SmartReferralAgent(db)
    result = agent.recommend_hospital(-6.2088, 106.8456, 'medium', 50.0)
    db.close()
    return result['success']

# Test with 10 concurrent requests
with ThreadPoolExecutor(max_workers=10) as executor:
    start = time.time()
    futures = [executor.submit(test_recommendation) for _ in range(10)]
    results = [f.result() for f in futures]
    elapsed = time.time() - start
    
    print(f"Completed {len(results)} requests in {elapsed:.2f} seconds")
    print(f"Success rate: {sum(results)}/{len(results)}")
```

### Database Query Performance

```sql
-- Test query performance
EXPLAIN SELECT * FROM hospitals WHERE available_beds > 0 AND emergency_available = TRUE;

-- Should use index idx_available_beds
```

## Security Testing

### SQL Injection Prevention
✓ Using SQLAlchemy ORM - automatically parameterized queries

### Environment Variables
✓ Sensitive data in .env, not in code
✓ .env in .gitignore

### Input Validation
Test with malicious inputs in Streamlit forms:
- SQL injection attempts: `'; DROP TABLE hospitals; --`
- XSS attempts: `<script>alert('xss')</script>`

Expected: Should be sanitized by Streamlit

## Error Handling Testing

### Test Database Connection Failure
```python
# Stop MySQL and try to connect
from src.database import SessionLocal
try:
    db = SessionLocal()
    db.query(Hospital).first()
except Exception as e:
    print(f"Expected error: {e}")
```

### Test API Failure
```python
# Use invalid API key
from src.maps_api import GoogleMapsClient
client = GoogleMapsClient()
client.api_key = "invalid_key"
result = client.geocode_address("Jakarta")
# Expected: None or error message
```

## Test Results Template

| Test Category | Test Case | Status | Notes |
|--------------|-----------|--------|-------|
| Setup | Database connection | ✅ Pass | - |
| Setup | Environment variables | ✅ Pass | - |
| Models | Hospital creation | ✅ Pass | - |
| Models | Patient creation | ✅ Pass | - |
| APIs | Google Maps distance | ✅ Pass | - |
| APIs | SATUSEHAT auth | ⚠️ Skip | Requires valid credentials |
| Agent | Hospital recommendation | ✅ Pass | - |
| Predictor | Wait time prediction | ✅ Pass | - |
| UI | Dashboard load | ✅ Pass | - |
| UI | Create referral | ✅ Pass | - |
| UI | Add hospital | ✅ Pass | - |

## Bug Report Template

**Title**: [Bug] Brief description

**Steps to Reproduce**:
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected Behavior**:
A clear description of what you expected to happen.

**Actual Behavior**:
What actually happened.

**Screenshots**:
If applicable, add screenshots.

**Environment**:
- OS: [e.g. Windows 10, Ubuntu 20.04]
- Python Version: [e.g. 3.9.7]
- MySQL Version: [e.g. 8.0.27]
- Browser: [e.g. Chrome 96]

## Known Issues

1. **Google Maps API Quota**: Free tier has limited quota. Use sparingly.
2. **SATUSEHAT API**: Sandbox credentials may have limitations.
3. **Database Connection Pool**: Default pool size may need adjustment for production.

## Continuous Testing

Set up GitHub Actions for automated testing:

```yaml
# .github/workflows/test.yml
name: Test SmartRujuk+

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: password
          MYSQL_DATABASE: smartrujuk_db
        ports:
          - 3306:3306
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: python -m unittest discover tests
```

---

Happy Testing! 🧪✅
