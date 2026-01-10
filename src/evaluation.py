"""
Evaluation helpers for wait time prediction models.

Provides functions to run a train/test split on historical wait-time
data, compute regression metrics (MAE, RMSE, R2) and timing information,
and produce a simple report dict (suitable for writing to JSON/markdown).
"""
from typing import Dict, Optional
import time
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sqlalchemy.orm import Session
from src.models import WaitTimeHistory
from src.models import Hospital
from src.features.geospatial import haversine_km, multi_radius_counts, kernel_density_feature, compute_patient_distance
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from math import radians, cos, sin, asin, sqrt
from src.models import Hospital


def _prepare_dataframe(wait_times):
    rows = []
    severity_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}

    for wt in wait_times:
        try:
            sev = wt.severity_level.value if wt.severity_level is not None else 'medium'
        except Exception:
            sev = 'medium'

        severity_encoded = severity_map.get(sev, 2)
        timestamp = wt.timestamp
        hour = timestamp.hour if timestamp is not None else 0
        day = timestamp.weekday() if timestamp is not None else 0

        rows.append({
            'hospital_id': int(wt.hospital_id),
            'severity': severity_encoded,
            'hour': int(hour),
            'day_of_week': int(day),
            'wait_time': int(wt.wait_time_minutes)
        })

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


def evaluate_wait_time_model(db: Session, test_size: float = 0.2, random_state: int = 42, min_samples: int = 20) -> Optional[Dict]:
    """
    Train/test evaluation for wait time model.

    Args:
        db: SQLAlchemy session
        test_size: fraction to reserve for test
        random_state: reproducible seed
        min_samples: minimum samples required to run evaluation

    Returns:
        report dict containing metrics and timings or None if insufficient data
    """
    wait_times = db.query(WaitTimeHistory).all()
    df = _prepare_dataframe(wait_times)

    if df.shape[0] < min_samples:
        return None

    X = df[['hospital_id', 'severity', 'hour', 'day_of_week']].values
    y = df['wait_time'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    model = RandomForestRegressor(n_estimators=100, random_state=random_state)

    t0 = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - t0

    t0 = time.time()
    preds = model.predict(X_test)
    predict_time = time.time() - t0

    mae = float(mean_absolute_error(y_test, preds))
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    r2 = float(r2_score(y_test, preds))

    # Baseline: median predictor
    baseline_pred = np.median(y_train)
    baseline_mae = float(mean_absolute_error(y_test, np.full_like(y_test, baseline_pred)))

    report = {
        'n_samples': int(df.shape[0]),
        'train_size': int(X_train.shape[0]),
        'test_size': int(X_test.shape[0]),
        'train_time_seconds': train_time,
        'predict_time_seconds': predict_time,
        'mae': mae,
        'rmse': rmse,
        'r2': r2,
        'baseline_median_mae': baseline_mae,
        'model': 'RandomForestRegressor',
        'notes': 'Regression metrics for wait-time prediction (minutes)'
    }

    return report


def haversine(lon1, lat1, lon2, lat2):
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km


def evaluate_wait_time_model_augmented(db: Session, radius_km: float = 5.0, test_size: float = 0.2, random_state: int = 42, min_samples: int = 20) -> Optional[Dict]:
    """
    Augmented evaluation that adds a feature: count of hospitals within `radius_km`
    of the hospital corresponding to each WaitTimeHistory row.
    """
    wait_times = db.query(WaitTimeHistory).all()
    if len(wait_times) < min_samples:
        return None

    # load hospitals into memory
    hospitals = {h.id: h for h in db.query(Hospital).all()}

    rows = []
    severity_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}

    for wt in wait_times:
        hosp = hospitals.get(wt.hospital_id)
        if not hosp:
            continue
        # count neighbors
        count_nearby = 0
        for other in hospitals.values():
            d = haversine(hosp.longitude, hosp.latitude, other.longitude, other.latitude)
            if d <= radius_km and other.id != hosp.id:
                count_nearby += 1

        try:
            sev = wt.severity_level.value if wt.severity_level is not None else 'medium'
        except Exception:
            sev = 'medium'

        severity_encoded = severity_map.get(sev, 2)
        timestamp = wt.timestamp
        hour = timestamp.hour if timestamp is not None else 0
        day = timestamp.weekday() if timestamp is not None else 0

        rows.append({
            'hospital_id': int(wt.hospital_id),
            'severity': severity_encoded,
            'hour': int(hour),
            'day_of_week': int(day),
            'nearby_count': int(count_nearby),
            'wait_time': int(wt.wait_time_minutes)
        })

    import pandas as pd
    df = pd.DataFrame(rows)
    if df.empty or df.shape[0] < min_samples:
        return None

    X = df[['hospital_id', 'severity', 'hour', 'day_of_week', 'nearby_count']].values
    y = df['wait_time'].values

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    model = RandomForestRegressor(n_estimators=100, random_state=random_state)

    import time
    t0 = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - t0

    t0 = time.time()
    preds = model.predict(X_test)
    predict_time = time.time() - t0

    mae = float(mean_absolute_error(y_test, preds))
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    r2 = float(r2_score(y_test, preds))

    baseline_pred = np.median(y_train)
    baseline_mae = float(mean_absolute_error(y_test, np.full_like(y_test, baseline_pred)))

    report = {
        'n_samples': int(df.shape[0]),
        'train_size': int(X_train.shape[0]),
        'test_size': int(X_test.shape[0]),
        'train_time_seconds': train_time,
        'predict_time_seconds': predict_time,
        'mae': mae,
        'rmse': rmse,
        'r2': r2,
        'baseline_median_mae': baseline_mae,
        'model': 'RandomForestRegressor_augmented',
        'notes': f'Augmented with nearby_count (radius_km={radius_km})'
    }

    return report


def compare_baseline_vs_augmented(db: Session, radius_km: float = 5.0):
    base = evaluate_wait_time_model(db)
    aug = evaluate_wait_time_model_augmented(db, radius_km=radius_km)
    return {'baseline': base, 'augmented': aug}


def evaluate_with_geofeatures(db: Session, include_patient_distance: bool = False, patient_locations: dict = None, radii_km: list = None, include_kernel: bool = False, test_size: float = 0.2, random_state: int = 42):
    """
    Build a dataframe with optional geospatial features and evaluate.

    - patient_locations: dict mapping wait_time_history.id -> (lat, lon)
    - radii_km: list of radii to compute counts for
    """
    import pandas as pd
    wait_times = db.query(WaitTimeHistory).all()
    if not wait_times:
        return None

    hospitals = db.query(Hospital).all()
    hosp_map = {h.id: h for h in hospitals}

    rows = []
    severity_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}

    radii_km = radii_km or [1.0, 5.0, 10.0]
    # precompute multi-radius counts and kernel density
    mrc = multi_radius_counts(hospitals, radii_km)
    kd = kernel_density_feature(hospitals, bandwidth_km=5.0) if include_kernel else {}

    for wt in wait_times:
        hosp = hosp_map.get(wt.hospital_id)
        if not hosp:
            continue
        try:
            sev = wt.severity_level.value if wt.severity_level is not None else 'medium'
        except Exception:
            sev = 'medium'

        severity_encoded = severity_map.get(sev, 2)
        ts = wt.timestamp
        hour = ts.hour if ts is not None else 0
        day = ts.weekday() if ts is not None else 0

        row = {
            'hospital_id': int(wt.hospital_id),
            'severity': severity_encoded,
            'hour': int(hour),
            'day_of_week': int(day),
            'wait_time': int(wt.wait_time_minutes)
        }

        # add multi-radius counts
        counts = mrc.get(wt.hospital_id, [0]*len(radii_km))
        for i, r in enumerate(radii_km):
            row[f'count_within_{int(r)}km'] = counts[i]

        # kernel density
        if include_kernel:
            row['kernel_density'] = float(kd.get(wt.hospital_id, 0.0))

        # patient distance
        if include_patient_distance and patient_locations:
            ploc = patient_locations.get(wt.id)
            if ploc:
                pdist = compute_patient_distance(ploc[0], ploc[1], hosp)
            else:
                pdist = 0.0
            row['patient_distance_km'] = float(pdist)

        rows.append(row)

    df = pd.DataFrame(rows)
    if df.shape[0] < 20:
        return None

    feature_cols = [c for c in df.columns if c not in ('wait_time',)]
    X = df[feature_cols].values
    y = df['wait_time'].values

    # simple train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    model = RandomForestRegressor(n_estimators=100, random_state=random_state)
    import time
    t0 = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - t0

    t0 = time.time()
    preds = model.predict(X_test)
    predict_time = time.time() - t0

    mae = float(mean_absolute_error(y_test, preds))
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    r2 = float(r2_score(y_test, preds))

    return {
        'n_samples': int(df.shape[0]),
        'train_time_seconds': train_time,
        'predict_time_seconds': predict_time,
        'mae': mae,
        'rmse': rmse,
        'r2': r2,
        'features_used': feature_cols
    }


def run_hyperparameter_tuning(db: Session, param_grid: dict = None, cv_splits: int = 3, use_time_series: bool = False):
    """
    Run a quick GridSearchCV over RandomForestRegressor and GradientBoostingRegressor.
    Returns best estimator info and CV results (kept small for demo).
    """
    import pandas as pd
    wait_times = db.query(WaitTimeHistory).all()
    if len(wait_times) < 50:
        return None

    hospitals = db.query(Hospital).all()
    hosp_map = {h.id: h for h in hospitals}

    rows = []
    severity_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
    for wt in wait_times:
        hosp = hosp_map.get(wt.hospital_id)
        if not hosp:
            continue
        try:
            sev = wt.severity_level.value if wt.severity_level is not None else 'medium'
        except Exception:
            sev = 'medium'
        severity_encoded = severity_map.get(sev, 2)
        ts = wt.timestamp
        hour = ts.hour if ts is not None else 0
        day = ts.weekday() if ts is not None else 0
        rows.append({'hospital_id': wt.hospital_id, 'severity': severity_encoded, 'hour': hour, 'day_of_week': day, 'wait_time': wt.wait_time_minutes})

    df = pd.DataFrame(rows)
    X = df[['hospital_id', 'severity', 'hour', 'day_of_week']].values
    y = df['wait_time'].values

    # default small grid
    param_grid = param_grid or {
        'n_estimators': [50, 100],
        'max_depth': [5, 10]
    }

    estimator = RandomForestRegressor(random_state=42)
    if use_time_series:
        cv = TimeSeriesSplit(n_splits=cv_splits)
    else:
        cv = cv_splits

    gs = GridSearchCV(estimator, param_grid, cv=cv, scoring='neg_mean_absolute_error', n_jobs=1)
    gs.fit(X, y)

    # also try gradient boosting quickly
    gb = GradientBoostingRegressor(random_state=42)
    gb_grid = {'n_estimators': [50], 'max_depth': [3]}
    gs_gb = GridSearchCV(gb, gb_grid, cv=3, scoring='neg_mean_absolute_error', n_jobs=1)
    gs_gb.fit(X, y)

    return {
        'rf_best_params': gs.best_params_,
        'rf_best_score': -float(gs.best_score_),
        'gb_best_params': gs_gb.best_params_,
        'gb_best_score': -float(gs_gb.best_score_)
    }


if __name__ == '__main__':
    print('This module provides evaluation utilities. Import and call evaluate_wait_time_model(db).')
