**Evaluation Report**

- **Project**: `smart-rujuk-ai-agent`
- **Date**: 2025-12-03

**Summary**
- Implemented an evaluation harness (`src/evaluation.py`) that computes regression metrics (MAE, RMSE, R2) and timing.
- Implemented a geolocation augmentation loader (`src/data/faskes_loader.py`) and a demo + production runner (`scripts/merge_faskes.py`).
- Added a small sample CSV `data/faskes_sample.csv` and a unit test `test_evaluation.py`.

**What I ran**
- Unit test (isolated):
  - `python -m pytest -q test_evaluation.py` — passed (in-memory DB)
- Demo augmentation + evaluation (in-memory):
  - `python scripts/merge_faskes.py` — loads `data/faskes_sample.csv` into an in-memory DB, seeds synthetic wait-time history, and compares baseline vs augmented models.
- Production augmentation + evaluation (uses configured DB via `SessionLocal()`):
  - `python scripts/merge_faskes.py --db-prod` — upserts `data/faskes_sample.csv` into configured DB and runs baseline vs augmented evaluation.

**Results (demo in-memory)**
- Baseline model (RandomForestRegressor):
  - n_samples: 120
  - mae: 19.6060
  - rmse: 23.4098
  - r2: -0.8141
- Augmented model (nearby_count within 5km added):
  - n_samples: 120
  - mae: 19.6137
  - rmse: 23.4375
  - r2: -0.8184

Observation: On this synthetic demo dataset, augmenting with `nearby_count` did not improve MAE; R2 remained poor (dataset synthetic).

**Results (production DB)**
- Baseline model (RandomForestRegressor):
  - n_samples: 500
  - mae: 19.9202
  - rmse: 27.1553
  - r2: 0.6780
- Augmented model (nearby_count within 5km added):
  - n_samples: 500
  - mae: 19.9550
  - rmse: 26.7358
  - r2: 0.6879

Observation: On your production dataset, adding `nearby_count` produced a negligible change in MAE (slightly worse) and a small increase in R2. This suggests the simple `nearby_count` feature alone is not a clear win for reducing absolute error on wait-time prediction.

**Recommendations / Next steps**
- Feature engineering:
  - Add patient-location-based distance features (distance from patient to hospital) when available.
  - Add hospital capacity/utilization features (recent `CapacityHistory`) and rolling averages of wait times.
  - Try richer geospatial features: distance to nearest higher-capacity hospital, travel time estimate, hospitals within multiple radii, kernel density of facilities.
- Model & training:
  - Use cross-validation and hyperparameter search (GridSearchCV/RandomizedSearchCV).
  - Try gradient boosting (XGBoost/LightGBM) and calibration.
- Evaluation:
  - Use time-aware splits for temporal validation (if data is time series).
  - Produce error distribution plots, per-severity metrics, and hospital-level breakdowns.
- Data:
  - Ingest larger faskes datasets for coverage beyond the sample CSV.

**How to reproduce**
1. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

2. Run the unit test:

```powershell
python -m pytest -q test_evaluation.py
```

3. Run demo augmentation + compare:

```powershell
python scripts/merge_faskes.py
```

4. Run against configured production DB (will upsert `data/faskes_sample.csv` into `hospitals`):

```powershell
python scripts/merge_faskes.py --db-prod
```

**Files added/changed**
- `src/evaluation.py` — evaluation + augmented evaluation + compare function
- `src/data/faskes_loader.py` — CSV loader/upsert
- `scripts/merge_faskes.py` — runner script (demo & production)
- `data/faskes_sample.csv` — small sample CSV
- `test_evaluation.py` — unit test

If you want, I can now:
- Run additional feature experiments (e.g., patient distance) and re-evaluate automatically, or
- Add a CI workflow to run `pytest` and optionally run evaluation on a sanitized dataset.
