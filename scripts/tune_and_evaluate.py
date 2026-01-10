"""Script to run hyperparameter tuning and geospatial feature evaluation.

Usage:
  python scripts/tune_and_evaluate.py [--db-prod]

By default runs on a demo in-memory DB seeded from `data/faskes_sample.csv`.
With `--db-prod` uses configured `SessionLocal()`.
"""
import sys
import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.data.faskes_loader import load_faskes_csv
from src.evaluation import evaluate_with_geofeatures, run_hyperparameter_tuning
from src.database import Base
from src.models import Hospital, WaitTimeHistory, SeverityEnum


def create_inmemory_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def seed_demo(session):
    load_faskes_csv(session, 'data/faskes_sample.csv')
    hospitals = session.query(Hospital).all()
    now = datetime.datetime.utcnow()
    for i in range(300):
        hosp = hospitals[i % len(hospitals)]
        sev = SeverityEnum.medium if (i % 3 != 0) else SeverityEnum.high
        ts = now - datetime.timedelta(hours=(i % 72))
        wt = WaitTimeHistory(hospital_id=hosp.id, severity_level=sev, timestamp=ts, wait_time_minutes=30 + (i % 60))
        session.add(wt)
    session.commit()


def main():
    use_prod = '--db-prod' in sys.argv
    if use_prod:
        from src.database import SessionLocal
        session = SessionLocal()
        print('Using production DB')
    else:
        session = create_inmemory_session()
        seed_demo(session)

    # Build fake patient locations mapping for demo: map wait_time_history.id -> (lat, lon)
    patient_locations = {}
    for wt in session.query(WaitTimeHistory).all():
        # small jitter around hospital
        hosp = session.query(Hospital).filter(Hospital.id == wt.hospital_id).first()
        if hosp:
            patient_locations[wt.id] = (hosp.latitude + 0.001 * (wt.id % 3), hosp.longitude + 0.001 * ((wt.id+1) % 3))

    print('Evaluating with geospatial features (patient distance, multi-radius, kernel density)')
    r = evaluate_with_geofeatures(session, include_patient_distance=True, patient_locations=patient_locations, radii_km=[1.0,5.0,10.0], include_kernel=True)
    print('Evaluation result:', r)

    print('Running quick hyperparameter tuning...')
    tuning = run_hyperparameter_tuning(session, cv_splits=3, use_time_series=False)
    print('Tuning results:', tuning)


if __name__ == '__main__':
    main()
