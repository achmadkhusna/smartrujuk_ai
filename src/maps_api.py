"""
Google Maps API Integration Module with Offline Fallback
"""
import os
import googlemaps
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleMapsClient:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        self.client = None
        self.offline_mode = False
        
        try:
            if self.api_key:
                self.client = googlemaps.Client(key=self.api_key)
                logger.info("Google Maps API initialized successfully")
            else:
                logger.warning("No Google Maps API key found, using offline mode")
                self.offline_mode = True
        except Exception as e:
            logger.warning(f"Failed to initialize Google Maps API: {str(e)}, using offline mode")
            self.offline_mode = True
    
    def get_distance_matrix(self, origins: List[Tuple[float, float]], 
                           destinations: List[Tuple[float, float]]) -> Optional[Dict]:
        """
        Get distance matrix between multiple origins and destinations
        Args:
            origins: List of (latitude, longitude) tuples
            destinations: List of (latitude, longitude) tuples
        Returns:
            Distance matrix data
        """
        if not self.client:
            return None
        
        try:
            result = self.client.distance_matrix(origins, destinations, mode="driving")
            return result
        except Exception as e:
            print(f"Error getting distance matrix: {str(e)}")
            return None
    
    def get_directions(self, origin: Tuple[float, float], 
                      destination: Tuple[float, float]) -> Optional[Dict]:
        """
        Get directions between two points
        Args:
            origin: (latitude, longitude) tuple
            destination: (latitude, longitude) tuple
        Returns:
            Directions data
        """
        if not self.client:
            return None
        
        try:
            result = self.client.directions(origin, destination, mode="driving")
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting directions: {str(e)}")
            return None
    
    def calculate_distance(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
        Returns:
            Distance in kilometers
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        distance = R * c
        return round(distance, 2)
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates with offline fallback
        Args:
            address: Address string
        Returns:
            (latitude, longitude) tuple
        """
        if self.offline_mode or not self.client:
            logger.info(f"Geocoding in offline mode for: {address}")
            return self._geocode_offline(address)
        
        try:
            result = self.client.geocode(address)
            if result:
                location = result[0]['geometry']['location']
                return (location['lat'], location['lng'])
            return self._geocode_offline(address)
        except Exception as e:
            logger.warning(f"Error geocoding address: {str(e)}, falling back to offline mode")
            return self._geocode_offline(address)
    
    def _geocode_offline(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Offline fallback for geocoding using simple location matching
        Args:
            address: Address string
        Returns:
            (latitude, longitude) tuple or None
        """
        # Sample coordinates for common Indonesian cities/regions
        location_map = {
            'jakarta': (-6.2088, 106.8456),
            'jakarta pusat': (-6.1862, 106.8311),
            'jakarta selatan': (-6.2921, 106.7970),
            'jakarta timur': (-6.1890, 106.8941),
            'jakarta barat': (-6.1746, 106.7857),
            'jakarta utara': (-6.1496, 106.8600),
            'bekasi': (-6.2383, 107.0012),
            'tangerang': (-6.1780, 106.6297),
            'depok': (-6.4025, 106.7942),
            'bogor': (-6.5950, 106.8164),
            'bandung': (-6.9175, 107.6191),
            'surabaya': (-7.2575, 112.7521),
            'medan': (3.5952, 98.6722),
            'semarang': (-6.9667, 110.4167),
            'yogyakarta': (-7.7956, 110.3695),
            'makassar': (-5.1477, 119.4327),
            'palembang': (-2.9761, 104.7754),
            'malang': (-7.9666, 112.6326),
            'solo': (-7.5705, 110.8284),
            'batam': (1.0456, 104.0305)
        }
        
        address_lower = address.lower()
        for city, coords in location_map.items():
            if city in address_lower:
                logger.info(f"Matched offline location: {city} -> {coords}")
                return coords
        
        # Default to Jakarta if no match found
        logger.warning(f"No offline match for '{address}', defaulting to Jakarta")
        return (-6.2088, 106.8456)
