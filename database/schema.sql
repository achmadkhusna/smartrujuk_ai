-- SmartRujuk+ Database Schema

-- Create database
CREATE DATABASE IF NOT EXISTS smartrujuk;
USE smartrujuk;

-- Hospitals table
CREATE TABLE IF NOT EXISTS hospitals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    type VARCHAR(100),
    class VARCHAR(50),
    total_beds INT DEFAULT 0,
    available_beds INT DEFAULT 0,
    phone VARCHAR(50),
    emergency_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_location (latitude, longitude),
    INDEX idx_available_beds (available_beds)
);

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bpjs_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    gender ENUM('M', 'F') NOT NULL,
    address TEXT,
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_bpjs (bpjs_number)
);

-- Referrals table
CREATE TABLE IF NOT EXISTS referrals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    from_hospital_id INT,
    to_hospital_id INT NOT NULL,
    condition_description TEXT NOT NULL,
    severity_level ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    status ENUM('pending', 'accepted', 'rejected', 'completed') DEFAULT 'pending',
    predicted_wait_time INT,
    actual_wait_time INT,
    distance_km DECIMAL(10, 2),
    referral_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acceptance_date TIMESTAMP NULL,
    completion_date TIMESTAMP NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (from_hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL,
    FOREIGN KEY (to_hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
    INDEX idx_patient (patient_id),
    INDEX idx_status (status),
    INDEX idx_severity (severity_level)
);

-- Hospital capacity history for predictive modeling
CREATE TABLE IF NOT EXISTS capacity_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT NOT NULL,
    available_beds INT NOT NULL,
    occupied_beds INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
    INDEX idx_hospital_time (hospital_id, timestamp)
);

-- Wait time history for predictive modeling
CREATE TABLE IF NOT EXISTS wait_time_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT NOT NULL,
    severity_level ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    wait_time_minutes INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
    INDEX idx_hospital_severity (hospital_id, severity_level)
);

-- API configuration table for storing credentials and settings
CREATE TABLE IF NOT EXISTS api_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL UNIQUE,
    config_key VARCHAR(255) NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_service (service_name),
    INDEX idx_active (is_active)
);
