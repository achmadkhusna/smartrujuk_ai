"""
Predictive modeling module for wait time estimation
"""
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.models import WaitTimeHistory, CapacityHistory, Hospital

class WaitTimePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
    
    def train(self, db: Session):
        """Train the wait time prediction model"""
        try:
            # Get historical data
            wait_times = db.query(WaitTimeHistory).all()
            
            if len(wait_times) < 10:
                print("Not enough data to train the model")
                return False
            
            # Prepare features and labels
            X = []
            y = []
            
            for wt in wait_times:
                # Features: hospital_id, severity_level (encoded), hour of day, day of week
                severity_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
                severity_encoded = severity_map.get(wt.severity_level.value, 2)
                
                hour = wt.timestamp.hour
                day_of_week = wt.timestamp.weekday()
                
                X.append([wt.hospital_id, severity_encoded, hour, day_of_week])
                y.append(wt.wait_time_minutes)
            
            # Train the model
            X = np.array(X)
            y = np.array(y)
            
            self.model.fit(X, y)
            self.is_trained = True
            print(f"Model trained with {len(wait_times)} samples")
            return True
            
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return False
    
    def predict_wait_time(self, hospital_id: int, severity_level: str) -> int:
        """
        Predict wait time for a given hospital and severity level
        Args:
            hospital_id: Hospital ID
            severity_level: Severity level (low, medium, high, critical)
        Returns:
            Predicted wait time in minutes
        """
        if not self.is_trained:
            # Return default values if model is not trained
            default_wait_times = {
                'low': 30,
                'medium': 60,
                'high': 90,
                'critical': 15
            }
            return default_wait_times.get(severity_level, 60)
        
        try:
            severity_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            severity_encoded = severity_map.get(severity_level, 2)
            
            now = datetime.now()
            hour = now.hour
            day_of_week = now.weekday()
            
            features = np.array([[hospital_id, severity_encoded, hour, day_of_week]])
            predicted_time = self.model.predict(features)[0]
            
            return max(5, int(predicted_time))  # Minimum 5 minutes
            
        except Exception as e:
            print(f"Error predicting wait time: {str(e)}")
            # Return default value on error
            default_wait_times = {
                'low': 30,
                'medium': 60,
                'high': 90,
                'critical': 15
            }
            return default_wait_times.get(severity_level, 60)

class CapacityAnalyzer:
    def __init__(self):
        pass
    
    def calculate_utilization(self, hospital: Hospital) -> float:
        """
        Calculate hospital utilization rate
        Args:
            hospital: Hospital object
        Returns:
            Utilization rate (0.0 to 1.0)
        """
        if hospital.total_beds == 0:
            return 0.0
        return (hospital.total_beds - hospital.available_beds) / hospital.total_beds
    
    def predict_capacity_trend(self, db: Session, hospital_id: int, hours_ahead: int = 24) -> str:
        """
        Predict capacity trend for a hospital
        Args:
            db: Database session
            hospital_id: Hospital ID
            hours_ahead: Hours to predict ahead
        Returns:
            Trend prediction (increasing, stable, decreasing)
        """
        try:
            # Get recent capacity history
            recent_history = db.query(CapacityHistory).filter(
                CapacityHistory.hospital_id == hospital_id
            ).order_by(CapacityHistory.timestamp.desc()).limit(24).all()
            
            if len(recent_history) < 10:
                return "stable"
            
            # Calculate trend
            utilization_rates = []
            for history in recent_history:
                total = history.available_beds + history.occupied_beds
                if total > 0:
                    utilization = history.occupied_beds / total
                    utilization_rates.append(utilization)
            
            if len(utilization_rates) < 2:
                return "stable"
            
            # Simple trend analysis
            first_half_avg = sum(utilization_rates[:len(utilization_rates)//2]) / (len(utilization_rates)//2)
            second_half_avg = sum(utilization_rates[len(utilization_rates)//2:]) / (len(utilization_rates) - len(utilization_rates)//2)
            
            diff = second_half_avg - first_half_avg
            
            if diff > 0.05:
                return "increasing"
            elif diff < -0.05:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            print(f"Error predicting capacity trend: {str(e)}")
            return "stable"
    
    def analyze_hospital_capacity(self, db: Session, hospital_id: int) -> Dict:
        """
        Analyze hospital capacity and trends
        Args:
            db: Database session
            hospital_id: Hospital ID
        Returns:
            Dictionary with capacity analysis
        """
        try:
            hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
            
            if not hospital:
                return {
                    'status': 'unknown',
                    'available_beds': 0,
                    'total_beds': 0,
                    'occupancy_rate': 0
                }
            
            available_beds = hospital.available_beds
            total_beds = hospital.total_beds
            occupancy_rate = ((total_beds - available_beds) / total_beds * 100) if total_beds > 0 else 0
            
            # Determine status
            if occupancy_rate < 50:
                status = 'low'
            elif occupancy_rate < 75:
                status = 'moderate'
            elif occupancy_rate < 90:
                status = 'high'
            else:
                status = 'critical'
            
            return {
                'status': status,
                'available_beds': available_beds,
                'total_beds': total_beds,
                'occupancy_rate': round(occupancy_rate, 2),
                'emergency_available': hospital.emergency_available
            }
            
        except Exception as e:
            print(f"Error analyzing capacity: {str(e)}")
            return {
                'status': 'unknown',
                'available_beds': 0,
                'total_beds': 0,
                'occupancy_rate': 0
            }
    
    def get_trending_hospitals(self, db: Session, limit: int = 10) -> List[Dict]:
        """
        Get hospitals with best capacity status
        Args:
            db: Database session
            limit: Number of hospitals to return
        Returns:
            List of hospital capacity info
        """
        try:
            hospitals = db.query(Hospital).filter(
                Hospital.available_beds > 0,
                Hospital.emergency_available == True
            ).order_by(Hospital.available_beds.desc()).limit(limit).all()
            
            result = []
            for hospital in hospitals:
                capacity_info = self.analyze_hospital_capacity(db, hospital.id)
                result.append({
                    'id': hospital.id,
                    'name': hospital.name,
                    'address': hospital.address,
                    'latitude': hospital.latitude,
                    'longitude': hospital.longitude,
                    'capacity': capacity_info
                })
            
            return result
            
        except Exception as e:
            print(f"Error getting trending hospitals: {str(e)}")
            return []
