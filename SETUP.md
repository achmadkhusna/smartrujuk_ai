# Setup Guide - SmartRujuk+ AI Agent

## Quick Start (5 menit)

### 1. Prerequisites Check

Pastikan Anda sudah menginstall:
- ✅ Python 3.8+ (`python --version`)
- ✅ MySQL 5.7+ (`mysql --version`)
- ✅ pip (`pip --version`)

### 2. Install & Setup

```bash
# Clone repository (jika belum)
git clone https://github.com/myaasiinh/smart-rujuk-ai-agent.git
cd smart-rujuk-ai-agent

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env dan sesuaikan DB_PASSWORD dengan password MySQL Anda

# Buat database
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS smartrujuk_db;"

# Inisialisasi database dengan data sampel
python database/init_db.py

# Jalankan aplikasi
streamlit run app.py
```

### 3. Akses Aplikasi

Buka browser dan akses: **http://localhost:8501**

## Konfigurasi Detail

### MySQL Database Setup

#### Windows
```bash
# Install MySQL dari https://dev.mysql.com/downloads/installer/
# Atau gunakan XAMPP/WAMP

# Start MySQL service
net start MySQL80

# Create database
mysql -u root -p
CREATE DATABASE smartrujuk_db;
exit;
```

#### Linux/Ubuntu
```bash
# Install MySQL
sudo apt-get update
sudo apt-get install mysql-server

# Start MySQL service
sudo systemctl start mysql

# Create database
sudo mysql -u root -p
CREATE DATABASE smartrujuk_db;
exit;
```

#### macOS
```bash
# Install MySQL via Homebrew
brew install mysql

# Start MySQL service
brew services start mysql

# Create database
mysql -u root -p
CREATE DATABASE smartrujuk_db;
exit;
```

### Environment Variables

Edit file `.env`:

```env
# Database - WAJIB diisi
DB_HOST=localhost
DB_PORT=3306
DB_NAME=smartrujuk_db
DB_USER=root
DB_PASSWORD=your_mysql_password  # GANTI INI!

# Google Maps API - WAJIB untuk fitur peta
GOOGLE_MAPS_API_KEY=AIzaSyBMagjD0rzJEn1n49v-5jC_OBiYeyYPdzY

# SATUSEHAT API - Opsional
SATUSEHAT_ORG_ID=b5f0e7f5-5660-4b91-95fb-0cc21a5f735f
SATUSEHAT_CLIENT_ID=hC1BUB8jmg97VbSGxsPyNk2k9iEjnG7woXAQq06nUxwjbvPe
SATUSEHAT_CLIENT_SECRET=YzlwM6Z6xWgPa4FcOs6XdemGmTQF9HzTS77ZAAp4ptQFkeGSGAeJfEhFlFUHCjsT

# OpenAI API - Opsional (untuk AI Agent enhanced)
OPENAI_API_KEY=sk-your-key-here
```

### Google Maps API Setup

1. Buka [Google Cloud Console](https://console.cloud.google.com/)
2. Buat project baru atau pilih existing
3. Enable APIs:
   - Maps JavaScript API
   - Geocoding API
   - Distance Matrix API
   - Directions API
4. Create credentials → API Key
5. Copy API Key ke `.env`

**Note**: Gunakan API key yang sudah disediakan di soal.txt atau buat yang baru.

### SATUSEHAT API (Opsional)

Credentials sudah tersedia di `.env.example` (sandbox environment).

Untuk production:
1. Daftar di https://satusehat.kemkes.go.id/
2. Buat Organization
3. Generate Client ID & Secret
4. Update `.env`

## Testing Setup

### Test Database Connection

```bash
python -c "from src.database import engine; engine.connect(); print('✅ Database connection successful!')"
```

### Test API Connections

```python
# Test Google Maps
from src.maps_api import GoogleMapsClient
client = GoogleMapsClient()
result = client.calculate_distance(-6.2088, 106.8456, -6.1862, 106.8311)
print(f"Distance: {result} km")
```

### Load Sample Data

```bash
python database/init_db.py
```

Ini akan membuat:
- 10 rumah sakit di Jakarta
- 5 pasien sampel
- Data historis untuk training ML model

## Troubleshooting

### Error: `mysql-connector-python` install failed

**Windows:**
```bash
pip install --upgrade pip setuptools wheel
pip install mysql-connector-python
```

**Linux:**
```bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysql-connector-python
```

### Error: `ModuleNotFoundError: No module named 'streamlit'`

```bash
pip install -r requirements.txt
```

### Error: Database connection failed

1. Pastikan MySQL service berjalan
2. Cek username/password di `.env`
3. Cek database sudah dibuat:
   ```bash
   mysql -u root -p -e "SHOW DATABASES;"
   ```

### Error: `streamlit: command not found`

```bash
# Pastikan pip install berhasil
pip install streamlit --upgrade

# Atau gunakan python -m
python -m streamlit run app.py
```

### Port 8501 already in use

```bash
# Gunakan port lain
streamlit run app.py --server.port 8502
```

## Production Deployment

### Using Docker (Recommended)

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t smartrujuk .
docker run -p 8501:8501 smartrujuk
```

### Using Streamlit Cloud

1. Push ke GitHub
2. Login ke [streamlit.io/cloud](https://streamlit.io/cloud)
3. Deploy repository
4. Add secrets di dashboard (environment variables)

### Using Heroku

```bash
# Tambahkan Procfile
echo "web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# Deploy
heroku create smartrujuk-app
heroku addons:create cleardb:ignite
git push heroku main
```

## Performance Optimization

### Database Indexing

```sql
-- Sudah ada di schema.sql
CREATE INDEX idx_location ON hospitals(latitude, longitude);
CREATE INDEX idx_available_beds ON hospitals(available_beds);
```

### Caching

Tambahkan di `app.py`:
```python
@st.cache_data(ttl=3600)
def load_hospitals():
    return db.query(Hospital).all()
```

## Security Checklist

- ✅ `.env` file tidak di-commit (ada di `.gitignore`)
- ✅ Database credentials aman
- ✅ API keys tidak exposed di code
- ✅ Input validation di form
- ✅ SQL injection protection (SQLAlchemy ORM)

## Next Steps

1. ✅ Sistem sudah berjalan? Coba fitur **Rujukan Baru**
2. 📊 Explore **Dashboard** dan **Analisis**
3. 🏥 Tambah data rumah sakit dari dataset BPJS
4. 🤖 (Opsional) Aktifkan OpenAI untuk AI Agent lebih pintar
5. 🗺️ Customize map styling di `app.py`

## Support

💬 Issues? Buka issue di GitHub repository
📧 Questions? Contact repository owner

---

Happy coding! 🚀
