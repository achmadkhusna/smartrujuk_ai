"""
Load API configuration from soal.txt to database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal
from src.models import APIConfig
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_api_credentials_from_soal():
    """
    Extract API credentials from soal.txt
    Returns: Dictionary of API credentials
    """
    soal_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'soal.txt')
    
    credentials = {}
    
    try:
        with open(soal_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract SATUSEHAT credentials
        org_id_match = re.search(r'Organization ID\s*\n\s*\n\s*([a-f0-9\-]+)', content, re.IGNORECASE)
        if org_id_match:
            credentials['SATUSEHAT_ORG_ID'] = org_id_match.group(1).strip()
        
        client_id_match = re.search(r'Client ID\s*\n\s*\n\s*([a-zA-Z0-9]+)', content, re.IGNORECASE)
        if client_id_match:
            credentials['SATUSEHAT_CLIENT_ID'] = client_id_match.group(1).strip()
        
        client_secret_match = re.search(r'Client Secret\s*\n\s*\n\s*([a-zA-Z0-9]+)', content, re.IGNORECASE)
        if client_secret_match:
            credentials['SATUSEHAT_CLIENT_SECRET'] = client_secret_match.group(1).strip()
        
        # Extract Google Maps API Key
        gmaps_match = re.search(r'key=([a-zA-Z0-9\-_]+)', content)
        if gmaps_match:
            credentials['GOOGLE_MAPS_API_KEY'] = gmaps_match.group(1).strip()
        
        logger.info(f"Extracted {len(credentials)} API credentials from soal.txt")
        return credentials
        
    except Exception as e:
        logger.error(f"Error extracting credentials from soal.txt: {str(e)}")
        return {}


def load_api_config_to_db():
    """
    Load API configuration to database
    """
    db = SessionLocal()
    
    try:
        # Extract credentials from soal.txt
        credentials = extract_api_credentials_from_soal()
        
        if not credentials:
            logger.warning("No credentials found in soal.txt")
            return
        
        # SATUSEHAT API Configuration
        if 'SATUSEHAT_ORG_ID' in credentials:
            config = db.query(APIConfig).filter(APIConfig.service_name == 'SATUSEHAT').first()
            if not config:
                config = APIConfig(
                    service_name='SATUSEHAT',
                    config_key='credentials',
                    config_value='{}',
                    description='SATUSEHAT API credentials for healthcare facility data',
                    is_active=True
                )
                db.add(config)
            
            # Update config value with credentials
            import json
            config_data = {
                'org_id': credentials.get('SATUSEHAT_ORG_ID', ''),
                'client_id': credentials.get('SATUSEHAT_CLIENT_ID', ''),
                'client_secret': credentials.get('SATUSEHAT_CLIENT_SECRET', ''),
                'base_url': 'https://api-satusehat.kemkes.go.id'
            }
            config.config_value = json.dumps(config_data)
            logger.info("Loaded SATUSEHAT API configuration")
        
        # Google Maps API Configuration
        if 'GOOGLE_MAPS_API_KEY' in credentials:
            config = db.query(APIConfig).filter(APIConfig.service_name == 'GOOGLE_MAPS').first()
            if not config:
                config = APIConfig(
                    service_name='GOOGLE_MAPS',
                    config_key='api_key',
                    config_value='',
                    description='Google Maps API key for geocoding and directions',
                    is_active=True
                )
                db.add(config)
            
            config.config_value = credentials['GOOGLE_MAPS_API_KEY']
            logger.info("Loaded Google Maps API configuration")
        
        db.commit()
        logger.info("✅ API configuration loaded successfully to database")
        
    except Exception as e:
        logger.error(f"Error loading API config to database: {str(e)}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def main():
    """Main function"""
    print("=== Loading API Configuration to Database ===")
    load_api_config_to_db()


if __name__ == "__main__":
    main()
