"""
Database models for SmartRujuk+ system
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum

class GenderEnum(enum.Enum):
    M = "M"
    F = "F"

class SeverityEnum(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class StatusEnum(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    completed = "completed"

class Hospital(Base):
    __tablename__ = 'hospitals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    type = Column(String(100))
    class_ = Column('class', String(50))
    total_beds = Column(Integer, default=0)
    available_beds = Column(Integer, default=0)
    phone = Column(String(50))
    emergency_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    referrals_to = relationship("Referral", back_populates="to_hospital", foreign_keys="Referral.to_hospital_id")
    referrals_from = relationship("Referral", back_populates="from_hospital", foreign_keys="Referral.from_hospital_id")

class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    bpjs_number = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    date_of_birth = Column(DateTime)
    gender = Column(Enum(GenderEnum), nullable=False)
    address = Column(Text)
    phone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    referrals = relationship("Referral", back_populates="patient")

class Referral(Base):
    __tablename__ = 'referrals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    from_hospital_id = Column(Integer, ForeignKey('hospitals.id'))
    to_hospital_id = Column(Integer, ForeignKey('hospitals.id'), nullable=False)
    condition_description = Column(Text, nullable=False)
    severity_level = Column(Enum(SeverityEnum), nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.pending)
    predicted_wait_time = Column(Integer)
    actual_wait_time = Column(Integer)
    distance_km = Column(Float)
    referral_date = Column(DateTime, default=datetime.utcnow)
    acceptance_date = Column(DateTime)
    completion_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="referrals")
    to_hospital = relationship("Hospital", back_populates="referrals_to", foreign_keys=[to_hospital_id])
    from_hospital = relationship("Hospital", back_populates="referrals_from", foreign_keys=[from_hospital_id])

class CapacityHistory(Base):
    __tablename__ = 'capacity_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    hospital_id = Column(Integer, ForeignKey('hospitals.id'), nullable=False)
    available_beds = Column(Integer, nullable=False)
    occupied_beds = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class WaitTimeHistory(Base):
    __tablename__ = 'wait_time_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    hospital_id = Column(Integer, ForeignKey('hospitals.id'), nullable=False)
    severity_level = Column(Enum(SeverityEnum), nullable=False)
    wait_time_minutes = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class APIConfig(Base):
    __tablename__ = 'api_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(String(100), nullable=False, unique=True)
    config_key = Column(String(255), nullable=False)
    config_value = Column(Text, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
