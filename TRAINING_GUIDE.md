# ML Model Training Guide - SmartRujuk+ AI Agent 🤖

Panduan lengkap untuk melatih dan mengelola model Machine Learning dalam sistem SmartRujuk+.

## 📋 Daftar Isi

1. [Overview](#overview)
2. [Model Architecture](#model-architecture)
3. [Training Data](#training-data)
4. [Training Process](#training-process)
5. [Model Evaluation](#model-evaluation)
6. [Deployment](#deployment)
7. [Monitoring & Maintenance](#monitoring--maintenance)

## 🎯 Overview

SmartRujuk+ menggunakan Machine Learning untuk:
- **Prediksi Waktu Tunggu**: Memperkirakan waktu tunggu pasien di rumah sakit
- **Analisis Kapasitas**: Menganalisis tingkat hunian dan ketersediaan bed
- **Rekomendasi Cerdas**: AI Agent untuk merekomendasikan rumah sakit optimal

## 🏗️ Model Architecture

### 1. Wait Time Predictor

**Type**: Supervised Learning - Regression

**Algorithm**: Random Forest Regressor

**Configuration**:
```python
RandomForestRegressor(
    n_estimators=100,      # Number of trees
    random_state=42,       # Reproducibility
    max_depth=None,        # No limit on tree depth
    min_samples_split=2,   # Minimum samples to split
    min_samples_leaf=1     # Minimum samples at leaf
)
```

**Features** (Input):
- `hospital_id`: Integer - Hospital identifier
- `severity_level`: Encoded (1=low, 2=medium, 3=high, 4=critical)
- `hour_of_day`: Integer (0-23) - Time of admission
- `day_of_week`: Integer (0-6) - Day (Monday=0, Sunday=6)

**Target** (Output):
- `wait_time_minutes`: Integer - Predicted wait time in minutes

**Why Random Forest?**:
- Handles non-linear relationships
- Robust to outliers
- No need for feature scaling
- Provides feature importance
- Good performance with limited data

### 2. Capacity Analyzer

**Type**: Rule-based Analysis

**Metrics**:
- Occupancy Rate = (Total Beds - Available Beds) / Total Beds × 100%
- Status Classification:
  - `low`: < 50% occupancy
  - `moderate`: 50-75% occupancy
  - `high`: 75-90% occupancy
  - `critical`: > 90% occupancy

### 3. AI Agent (LangChain)

**Type**: Agentic AI

**Tools**:
1. **FindNearestHospitals**: Query hospitals by location
2. **CheckHospitalCapacity**: Get real-time capacity status
3. **PredictWaitTime**: Get ML-based wait time predictions
4. **CalculateDistance**: Compute distances using Haversine formula

**Scoring Algorithm**:
```python
# For non-critical cases
score = (
    distance_score * 0.4 +        # 40% weight
    wait_time_score * 0.3 +        # 30% weight
    capacity_score * 0.3           # 30% weight
)

# For critical cases (prioritize proximity)
score = (
    distance_score * 0.7 +        # 70% weight
    capacity_score * 0.3           # 30% weight
)
```

## 📊 Training Data

### Data Sources

**1. Historical Data** (Real):
- `wait_time_history` table
- `capacity_history` table
- `referrals` table with actual outcomes

**2. Synthetic Data** (Generated):
- Realistic patterns based on:
  - Time of day (peak hours: 8-12, 16-20)
  - Severity levels
  - Hospital characteristics
  - Day of week patterns

### Data Generation

**Automatic Generation**:
```bash
# Generate during pipeline
python database/load_all_datasets.py
```

**Manual Generation**:
```python
from database.load_all_datasets import DataPipeline

pipeline = DataPipeline()

# Generate 1000 training records
pipeline.generate_training_data(num_records=1000)
```

**Generation Logic**:

```python
# Wait time based on severity
severity_weights = {
    'low': (20, 60),      # 20-60 minutes
    'medium': (40, 120),   # 40-120 minutes
    'high': (60, 180),     # 60-180 minutes
    'critical': (10, 30)   # 10-30 minutes (priority)
}

# Peak hour multiplier: 1.3x
# Time variance: ±20%
# Hospital-specific factors
```

### Data Requirements

**Minimum Requirements**:
- At least 10 records per hospital
- Coverage across all severity levels
- Distribution across different times of day
- Mix of weekdays and weekends

**Recommended**:
- 500+ wait time records
- 250+ capacity records
- 90 days historical data
- Multiple hospitals

### Data Quality

**Validation Checks**:
```python
# Check data distribution
SELECT 
    severity_level,
    COUNT(*) as count,
    AVG(wait_time_minutes) as avg_wait,
    MIN(wait_time_minutes) as min_wait,
    MAX(wait_time_minutes) as max_wait
FROM wait_time_history
GROUP BY severity_level;

# Check temporal distribution
SELECT 
    HOUR(timestamp) as hour,
    COUNT(*) as count
FROM wait_time_history
GROUP BY hour
ORDER BY hour;
```

## 🎓 Training Process

### Automatic Training (Recommended)

**Full Pipeline**:
```bash
# Complete setup: download, load, generate, train
python database/load_all_datasets.py --download-first
```

**Results**:
```
Training ML Models
==========================================
Model trained with 500 samples
✅ ML models trained successfully
```

### Manual Training

**Step 1: Prepare Environment**
```bash
# Ensure database is populated
python database/init_db.py

# Load datasets
python database/load_all_datasets.py --no-train
```

**Step 2: Train Model**
```python
from src.predictor import WaitTimePredictor
from src.database import SessionLocal

# Initialize
db = SessionLocal()
predictor = WaitTimePredictor()

# Train
success = predictor.train(db)

if success:
    print("✅ Training successful!")
    print(f"Model is trained: {predictor.is_trained}")
else:
    print("❌ Training failed - insufficient data")

db.close()
```

**Step 3: Verify Training**
```python
# Test predictions
test_cases = [
    (1, 'low'),      # Hospital 1, low severity
    (1, 'medium'),
    (1, 'high'),
    (1, 'critical'),
]

for hospital_id, severity in test_cases:
    wait_time = predictor.predict_wait_time(hospital_id, severity)
    print(f"Hospital {hospital_id}, {severity}: {wait_time} minutes")
```

### Training Script

Create `train_models.py`:
```python
#!/usr/bin/env python3
"""
Standalone training script
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.predictor import WaitTimePredictor
from src.database import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting model training...")
    
    db = SessionLocal()
    predictor = WaitTimePredictor()
    
    try:
        # Train model
        success = predictor.train(db)
        
        if success:
            logger.info("✅ Model trained successfully!")
            
            # Test predictions
            logger.info("\nTesting predictions:")
            for severity in ['low', 'medium', 'high', 'critical']:
                wait = predictor.predict_wait_time(1, severity)
                logger.info(f"  {severity}: {wait} minutes")
            
            return 0
        else:
            logger.error("❌ Training failed")
            return 1
            
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())
```

Run:
```bash
chmod +x train_models.py
python train_models.py
```

## 📈 Model Evaluation

### Performance Metrics

**For Regression (Wait Time)**:

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

# After training, evaluate on test set
y_pred = predictor.model.predict(X_test)
y_true = y_test

# Calculate metrics
mae = mean_absolute_error(y_true, y_pred)
mse = mean_squared_error(y_true, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_true, y_pred)

print(f"MAE: {mae:.2f} minutes")
print(f"RMSE: {rmse:.2f} minutes")
print(f"R²: {r2:.4f}")
```

**Expected Performance**:
- MAE: < 15 minutes
- RMSE: < 20 minutes
- R²: > 0.7

### Feature Importance

```python
# Get feature importance
importances = predictor.model.feature_importances_
features = ['hospital_id', 'severity_level', 'hour', 'day_of_week']

for feat, imp in zip(features, importances):
    print(f"{feat}: {imp:.4f}")
```

### Cross-Validation

```python
from sklearn.model_selection import cross_val_score

# K-fold cross-validation
scores = cross_val_score(
    predictor.model, 
    X, y, 
    cv=5, 
    scoring='neg_mean_absolute_error'
)

print(f"CV MAE: {-scores.mean():.2f} ± {scores.std():.2f}")
```

### Validation Tests

```python
# Test 1: Severity ordering
wait_times = []
for severity in ['low', 'medium', 'high', 'critical']:
    wait = predictor.predict_wait_time(1, severity)
    wait_times.append((severity, wait))
    
print("Severity ordering test:")
for sev, wait in wait_times:
    print(f"  {sev}: {wait} minutes")

# Test 2: Time of day effect
morning_wait = predictor.predict_wait_time(1, 'medium')  # Current time
# Simulate different hours by modifying features

# Test 3: Consistency
predictions = []
for _ in range(10):
    wait = predictor.predict_wait_time(1, 'medium')
    predictions.append(wait)

print(f"Consistency: std={np.std(predictions):.2f}")
```

## 🚀 Deployment

### Model Persistence

**Save Model**:
```python
import joblib

# Save trained model
joblib.dump(predictor.model, 'models/wait_time_predictor.pkl')

# Save with metadata
model_data = {
    'model': predictor.model,
    'is_trained': predictor.is_trained,
    'training_date': datetime.now(),
    'version': '1.0'
}
joblib.dump(model_data, 'models/wait_time_predictor_v1.pkl')
```

**Load Model**:
```python
# Load model
loaded_model = joblib.load('models/wait_time_predictor.pkl')
predictor.model = loaded_model
predictor.is_trained = True

# Verify
wait_time = predictor.predict_wait_time(1, 'high')
print(f"Predicted: {wait_time} minutes")
```

### Integration with App

**In Streamlit App** (`app.py`):
```python
from src.predictor import WaitTimePredictor

# Initialize once at startup
@st.cache_resource
def load_predictor():
    predictor = WaitTimePredictor()
    db = SessionLocal()
    predictor.train(db)  # Or load from file
    db.close()
    return predictor

# Use in app
predictor = load_predictor()
wait_time = predictor.predict_wait_time(hospital_id, severity)
```

### API Endpoint

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
predictor = WaitTimePredictor()

class PredictionRequest(BaseModel):
    hospital_id: int
    severity: str

@app.post("/predict-wait-time")
def predict_wait_time(request: PredictionRequest):
    wait_time = predictor.predict_wait_time(
        request.hospital_id,
        request.severity
    )
    return {"wait_time_minutes": wait_time}
```

## 🔍 Monitoring & Maintenance

### Model Monitoring

**Track Predictions**:
```python
# Log predictions for monitoring
class MonitoredPredictor(WaitTimePredictor):
    def predict_wait_time(self, hospital_id, severity_level):
        prediction = super().predict_wait_time(hospital_id, severity_level)
        
        # Log prediction
        logger.info(f"Prediction: hospital={hospital_id}, "
                   f"severity={severity_level}, wait={prediction}")
        
        return prediction
```

**Monitor Drift**:
```sql
-- Compare predictions vs actuals
SELECT 
    DATE(referral_date) as date,
    severity_level,
    AVG(predicted_wait_time) as avg_predicted,
    AVG(actual_wait_time) as avg_actual,
    AVG(ABS(predicted_wait_time - actual_wait_time)) as mae
FROM referrals
WHERE actual_wait_time IS NOT NULL
GROUP BY date, severity_level
ORDER BY date DESC;
```

### Retraining Schedule

**When to Retrain**:
- Every 30 days (scheduled)
- When MAE increases > 20%
- After significant data updates
- When new hospitals added

**Retraining Script**:
```bash
#!/bin/bash
# retrain.sh

echo "Starting model retraining..."

# Backup current model
cp models/wait_time_predictor.pkl models/wait_time_predictor_backup.pkl

# Retrain
python train_models.py

# Validate
python validate_model.py

if [ $? -eq 0 ]; then
    echo "✅ Retraining successful"
else
    echo "❌ Retraining failed, restoring backup"
    cp models/wait_time_predictor_backup.pkl models/wait_time_predictor.pkl
fi
```

**Automated Retraining**:
```python
# Add to scheduled task
from datetime import datetime, timedelta

def should_retrain(last_training_date):
    days_since_training = (datetime.now() - last_training_date).days
    return days_since_training >= 30

if should_retrain(last_training_date):
    logger.info("Initiating automatic retraining...")
    predictor.train(db)
```

### Model Versioning

```python
# Version tracking
MODEL_VERSION = {
    'version': '1.2.0',
    'training_date': '2024-01-15',
    'training_samples': 1500,
    'performance': {
        'mae': 12.5,
        'rmse': 18.3,
        'r2': 0.85
    },
    'features': ['hospital_id', 'severity', 'hour', 'day'],
    'algorithm': 'RandomForestRegressor',
    'hyperparameters': {
        'n_estimators': 100,
        'max_depth': None
    }
}

# Save with model
joblib.dump({
    'model': predictor.model,
    'metadata': MODEL_VERSION
}, f'models/wait_time_predictor_v{MODEL_VERSION["version"]}.pkl')
```

## 🎯 Best Practices

### 1. Data Quality First
- Validate input data before training
- Remove outliers carefully
- Ensure balanced distribution

### 2. Regular Monitoring
- Track prediction accuracy
- Monitor for data drift
- Log all predictions

### 3. Incremental Improvement
- Start with simple models
- Add complexity gradually
- Document all changes

### 4. Testing
- Unit tests for prediction functions
- Integration tests with database
- Performance tests

### 5. Documentation
- Document training process
- Record hyperparameters
- Track model versions

## 🔧 Troubleshooting

### Issue 1: "Not enough data to train"

**Solution**:
```bash
# Generate more training data
python -c "
from database.load_all_datasets import DataPipeline
p = DataPipeline()
p.generate_training_data(num_records=1000)
"
```

### Issue 2: Poor Prediction Accuracy

**Causes**:
- Insufficient training data
- Unbalanced severity distribution
- Lack of temporal variance

**Solution**:
- Generate more diverse training data
- Tune hyperparameters
- Add more features (hospital type, capacity, etc.)

### Issue 3: Model Not Loading

**Solution**:
```python
# Retrain and save
predictor = WaitTimePredictor()
predictor.train(db)

# Verify
if predictor.is_trained:
    joblib.dump(predictor.model, 'models/wait_time_predictor.pkl')
```

## 📚 Additional Resources

- [Scikit-learn Random Forest Documentation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html)
- [Model Deployment Best Practices](https://ml-ops.org/)
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)

---

**SmartRujuk+ Training Guide** - Model yang lebih baik, prediksi yang lebih akurat! 🤖✨
