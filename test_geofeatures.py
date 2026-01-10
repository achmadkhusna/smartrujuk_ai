from src.features.geospatial import haversine_km, multi_radius_counts, kernel_density_feature
from src.models import Hospital


class DummyHospital:
    def __init__(self, id, lat, lon):
        self.id = id
        self.latitude = lat
        self.longitude = lon


def test_haversine_basic():
    d = haversine_km(106.816666, -6.200000, 106.822000, -6.210000)
    assert d > 0


def test_multi_radius_counts_and_kernel():
    hospitals = [DummyHospital(1, -6.2, 106.8), DummyHospital(2, -6.21, 106.82), DummyHospital(3, -6.19, 106.79)]
    counts = multi_radius_counts(hospitals, [1.0, 5.0])
    assert isinstance(counts, dict)
    assert all(isinstance(v, list) for v in counts.values())
    kd = kernel_density_feature(hospitals, bandwidth_km=5.0)
    assert isinstance(kd, dict)
    assert all(k in kd for k in [1,2,3])
