import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models import Hospital, WaitTimeHistory, SeverityEnum
from src.evaluation import evaluate_wait_time_model


def create_inmemory_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def seed_synthetic_data(session):
    # create a few hospitals
    hospitals = []
    for i in range(1, 6):
        h = Hospital(
            name=f'H{i}',
            address=f'Address {i}',
            latitude=0.0 + i * 0.01,
            longitude=0.0 + i * 0.01,
        )
        session.add(h)
        hospitals.append(h)
    session.commit()

    # create synthetic wait time history
    now = datetime.datetime.utcnow()
    for i in range(120):
        hosp = hospitals[i % len(hospitals)]
        sev = SeverityEnum.medium if (i % 3 != 0) else SeverityEnum.high
        ts = now - datetime.timedelta(hours=(i % 48))
        wt = WaitTimeHistory(hospital_id=hosp.id, severity_level=sev, timestamp=ts, wait_time_minutes=30 + (i % 60))
        session.add(wt)

    session.commit()


def test_evaluate_wait_time_model_runs_and_returns_report():
    session = create_inmemory_session()
    seed_synthetic_data(session)

    report = evaluate_wait_time_model(session, test_size=0.2, random_state=1, min_samples=20)

    assert report is not None, "Expected a report dict, got None (insufficient data?)"
    assert 'mae' in report and 'r2' in report and 'n_samples' in report
    assert report['n_samples'] >= 20
