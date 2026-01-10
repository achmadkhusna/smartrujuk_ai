"""Loader for Indonesian faskes CSV files into Hospital table.

This module provides a simple CSV importer that upserts hospitals by
matching on name and coordinates (latitude/longitude).
"""
import csv
from typing import Iterable
from sqlalchemy.orm import Session
from src.models import Hospital


def load_faskes_csv(session: Session, csv_path: str) -> int:
    """
    Load faskes CSV and insert/update Hospital records.

    CSV expected headers: name,address,latitude,longitude,type,class,total_beds,available_beds,phone

    Returns number of upserts performed.
    """
    upserts = 0
    with open(csv_path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                lat = float(row.get('latitude') or 0.0)
                lon = float(row.get('longitude') or 0.0)
            except ValueError:
                continue

            name = (row.get('name') or '').strip()
            address = (row.get('address') or '').strip()

            # Try to find existing hospital by name + coords
            existing = session.query(Hospital).filter(
                Hospital.name == name,
                Hospital.latitude == lat,
                Hospital.longitude == lon
            ).first()

            if existing:
                # update fields
                existing.address = address or existing.address
                existing.type = row.get('type') or existing.type
                existing.class_ = row.get('class') or existing.class_
                try:
                    existing.total_beds = int(row.get('total_beds') or existing.total_beds or 0)
                except ValueError:
                    pass
                existing.phone = row.get('phone') or existing.phone
            else:
                h = Hospital(
                    name=name or 'Unknown',
                    address=address or 'Unknown',
                    latitude=lat,
                    longitude=lon,
                    type=row.get('type'),
                    class_=row.get('class'),
                )
                try:
                    h.total_beds = int(row.get('total_beds') or 0)
                except ValueError:
                    h.total_beds = 0
                try:
                    h.available_beds = int(row.get('available_beds') or 0)
                except ValueError:
                    h.available_beds = 0

                session.add(h)

            upserts += 1

    session.commit()
    return upserts
