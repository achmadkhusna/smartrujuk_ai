"""Geospatial feature utilities.

Provides haversine distance, patient-to-hospital distance pipeline,
multi-radius counts, and a simple kernel-density approximation for hospitals.
"""
from math import radians, cos, sin, asin, sqrt, exp
from typing import List, Dict
import numpy as np
from src.models import Hospital


def haversine_km(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return 6371 * c


def compute_patient_distance(patient_lat: float, patient_lon: float, hospital: Hospital) -> float:
    return haversine_km(patient_lon, patient_lat, hospital.longitude, hospital.latitude)


def multi_radius_counts(hospitals: List[Hospital], radii_km: List[float]) -> Dict[int, List[int]]:
    """
    For each hospital, compute counts of other hospitals within each radius.

    Returns dict: hospital_id -> [count_within_radius_1, count_within_radius_2, ...]
    """
    coords = {h.id: (h.latitude, h.longitude) for h in hospitals}
    ids = list(coords.keys())
    result = {}
    for hid in ids:
        lat1, lon1 = coords[hid]
        counts = []
        for r in radii_km:
            cnt = 0
            for oid in ids:
                if oid == hid:
                    continue
                lat2, lon2 = coords[oid]
                d = haversine_km(lon1, lat1, lon2, lat2)
                if d <= r:
                    cnt += 1
            counts.append(cnt)
        result[hid] = counts
    return result


def kernel_density_feature(hospitals: List[Hospital], bandwidth_km: float = 5.0) -> Dict[int, float]:
    """
    Approximate kernel density for each hospital using Gaussian kernel over pairwise distances.
    Returns hospital_id -> density value (not normalized).
    """
    coords = {h.id: (h.latitude, h.longitude) for h in hospitals}
    ids = list(coords.keys())
    density = {}
    for hid in ids:
        lat1, lon1 = coords[hid]
        s = 0.0
        for oid in ids:
            if oid == hid:
                continue
            lat2, lon2 = coords[oid]
            d = haversine_km(lon1, lat1, lon2, lat2)
            # Gaussian kernel
            s += exp(-0.5 * (d / (bandwidth_km + 1e-9))**2)
        density[hid] = s
    return density
