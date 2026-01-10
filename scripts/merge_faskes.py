"""Script to load sample faskes CSV, upsert into DB, and compare baseline vs augmented evaluation.

Usage:
    python scripts/merge_faskes.py [--db-prod]

By default uses an in-memory DB seeded with small synthetic wait_time_history for demo.
If `--db-prod` is provided, uses `SessionLocal()` from `src.database` to run on configured DB (reads only).
"""
import sys
import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ensure project root is on sys.path so `src` package is importable when running script
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.data.faskes_loader import load_faskes_csv
from src.evaluation import compare_baseline_vs_augmented
from src.database import Base
from src.models import Hospital, WaitTimeHistory, SeverityEnum


def create_inmemory_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def seed_demo_data(session):
    # insert hospitals matching sample CSV area
    with open('data/faskes_sample.csv', encoding='utf-8') as fh:
        # use loader to upsert
        load_faskes_csv(session, 'data/faskes_sample.csv')

    hospitals = session.query(Hospital).all()

    now = datetime.datetime.utcnow()
    for i in range(120):
        hosp = hospitals[i % len(hospitals)]
        sev = SeverityEnum.medium if (i % 3 != 0) else SeverityEnum.high
        ts = now - datetime.timedelta(hours=(i % 48))
        wt = WaitTimeHistory(hospital_id=hosp.id, severity_level=sev, timestamp=ts, wait_time_minutes=30 + (i % 60))
        session.add(wt)

    session.commit()


def main():
    use_prod = '--db-prod' in sys.argv
    if use_prod:
        from src.database import SessionLocal
        session = SessionLocal()
        print('Using configured production DB via SessionLocal()')
        # load provided faskes CSV into DB (upsert)
        print('Loading data/faskes_sample.csv into DB...')
        upserts = load_faskes_csv(session, 'data/faskes_sample.csv')
        print(f'Upserted {upserts} faskes rows into Hospital table')
        print('Running baseline vs augmented evaluation on production DB (read-only operations)...')
        result = compare_baseline_vs_augmented(session)
        print('Result:', result)
    else:
        session = create_inmemory_session()
        seed_demo_data(session)
        print('Running baseline vs augmented evaluation on demo in-memory DB...')
        result = compare_baseline_vs_augmented(session)
        print('Baseline metrics:', result['baseline'])
        print('Augmented metrics:', result['augmented'])


if __name__ == '__main__':
    main()
