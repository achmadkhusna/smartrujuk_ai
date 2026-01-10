"""
LangChain AI Agent for Smart Referral System
"""
import os
from typing import List, Dict, Optional, Any

# Updated imports for LangChain v0.1.0+
# Removed unused imports that were causing ImportErrors
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session
from src.models import Hospital, Patient, Referral
from src.predictor import WaitTimePredictor, CapacityAnalyzer
from src.maps_api import GoogleMapsClient
from dotenv import load_dotenv

load_dotenv()

class SmartReferralAgent:
    def __init__(self, db: Session):
        self.db = db
        self.wait_time_predictor = WaitTimePredictor()
        self.capacity_analyzer = CapacityAnalyzer()
        self.maps_client = GoogleMapsClient()
        
        # Initialize OpenAI (optional, will work without it)
        self.llm = None
        if os.getenv('OPENAI_API_KEY'):
            try:
                self.llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
            except:
                print("OpenAI API not available, using rule-based system")
        
        self.tools = self._create_tools()
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent"""
        tools = [
            Tool(
                name="FindNearestHospitals",
                func=self.find_nearest_hospitals,
                description="Find nearest hospitals to a given location. Input: 'latitude,longitude'"
            ),
            Tool(
                name="CheckHospitalCapacity",
                func=self.check_hospital_capacity,
                description="Check capacity of a specific hospital. Input: hospital_id"
            ),
            Tool(
                name="PredictWaitTime",
                func=self.predict_wait_time,
                description="Predict wait time for a hospital and severity. Input: 'hospital_id,severity_level'"
            ),
            Tool(
                name="CalculateDistance",
                func=self.calculate_distance,
                description="Calculate distance between two points. Input: 'lat1,lon1,lat2,lon2'"
            )
        ]
        return tools
    
    def find_nearest_hospitals(self, location: str) -> str:
        """Find nearest hospitals to a location"""
        try:
            lat, lon = map(float, location.split(','))
            
            # Get all hospitals with available beds
            hospitals = self.db.query(Hospital).filter(
                Hospital.available_beds > 0,
                Hospital.emergency_available == True
            ).all()
            
            # Calculate distances
            hospital_distances = []
            for hospital in hospitals:
                distance = self.maps_client.calculate_distance(
                    lat, lon, hospital.latitude, hospital.longitude
                )
                hospital_distances.append({
                    'id': hospital.id,
                    'name': hospital.name,
                    'distance': distance,
                    'available_beds': hospital.available_beds
                })
            
            # Sort by distance
            hospital_distances.sort(key=lambda x: x['distance'])
            
            # Return top 5
            result = []
            for h in hospital_distances[:5]:
                result.append(f"{h['name']} - {h['distance']}km, {h['available_beds']} beds available")
            
            return "\n".join(result) if result else "No hospitals available"
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def check_hospital_capacity(self, hospital_id: str) -> str:
        """Check capacity of a hospital"""
        try:
            hospital_id = int(hospital_id)
            capacity_info = self.capacity_analyzer.analyze_hospital_capacity(self.db, hospital_id)
            
            return (f"Status: {capacity_info['status']}, "
                   f"Available Beds: {capacity_info['available_beds']}, "
                   f"Total Beds: {capacity_info['total_beds']}, "
                   f"Occupancy: {capacity_info['occupancy_rate']}%")
        except Exception as e:
            return f"Error: {str(e)}"
    
    def predict_wait_time(self, input_str: str) -> str:
        """Predict wait time for a hospital"""
        try:
            hospital_id, severity = input_str.split(',')
            hospital_id = int(hospital_id)
            severity = severity.strip()
            
            wait_time = self.wait_time_predictor.predict_wait_time(hospital_id, severity)
            
            return f"Predicted wait time: {wait_time} minutes"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def calculate_distance(self, input_str: str) -> str:
        """Calculate distance between two points"""
        try:
            coords = list(map(float, input_str.split(',')))
            if len(coords) != 4:
                return "Invalid input format"
            
            distance = self.maps_client.calculate_distance(
                coords[0], coords[1], coords[2], coords[3]
            )
            
            return f"Distance: {distance} km"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def recommend_hospital(self, patient_lat: float, patient_lon: float, 
                          severity_level: str, max_distance: float = 50.0) -> Dict:
        """
        Recommend best hospital for patient referral
        Args:
            patient_lat: Patient latitude
            patient_lon: Patient longitude
            severity_level: Severity level (low, medium, high, critical)
            max_distance: Maximum distance in kilometers
        Returns:
            Dictionary with recommendation
        """
        try:
            # Get available hospitals
            hospitals = self.db.query(Hospital).filter(
                Hospital.available_beds > 0,
                Hospital.emergency_available == True
            ).all()
            
            if not hospitals:
                return {
                    'success': False,
                    'message': 'No hospitals available'
                }
            
            # Score each hospital
            scored_hospitals = []
            for hospital in hospitals:
                # Calculate distance
                distance = self.maps_client.calculate_distance(
                    patient_lat, patient_lon, hospital.latitude, hospital.longitude
                )
                
                if distance > max_distance:
                    continue
                
                # Get capacity info
                capacity = self.capacity_analyzer.analyze_hospital_capacity(self.db, hospital.id)
                
                # Predict wait time
                wait_time = self.wait_time_predictor.predict_wait_time(hospital.id, severity_level)
                
                # Calculate score (lower is better)
                # For critical cases, prioritize distance and wait time
                if severity_level == 'critical':
                    score = distance * 0.7 + (wait_time / 60) * 0.3
                else:
                    # For non-critical, balance distance, wait time, and capacity
                    capacity_score = (100 - capacity['occupancy_rate']) / 100
                    score = distance * 0.4 + (wait_time / 60) * 0.3 + (1 - capacity_score) * 0.3
                
                scored_hospitals.append({
                    'hospital': hospital,
                    'distance': distance,
                    'wait_time': wait_time,
                    'capacity': capacity,
                    'score': score
                })
            
            if not scored_hospitals:
                return {
                    'success': False,
                    'message': f'No hospitals within {max_distance}km'
                }
            
            # Sort by score and get best option
            scored_hospitals.sort(key=lambda x: x['score'])
            best = scored_hospitals[0]
            
            return {
                'success': True,
                'hospital_id': best['hospital'].id,
                'hospital_name': best['hospital'].name,
                'hospital_address': best['hospital'].address,
                'latitude': best['hospital'].latitude,
                'longitude': best['hospital'].longitude,
                'distance_km': best['distance'],
                'predicted_wait_time': best['wait_time'],
                'available_beds': best['capacity']['available_beds'],
                'occupancy_rate': best['capacity']['occupancy_rate'],
                'alternatives': [
                    {
                        'name': h['hospital'].name,
                        'distance': h['distance'],
                        'wait_time': h['wait_time']
                    } for h in scored_hospitals[1:4]
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }