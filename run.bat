@echo off
REM SmartRujuk+ AI Agent - Quick Start Script for Windows

echo ==================================
echo SmartRujuk+ AI Agent
echo ==================================
echo.

REM Check if .env exists
if not exist .env (
    echo [WARNING] File .env tidak ditemukan!
    echo [INFO] Copying .env.example to .env...
    copy .env.example .env
    echo [SUCCESS] File .env dibuat!
    echo.
    echo [CONFIG] Silakan edit file .env dan sesuaikan konfigurasi database Anda:
    echo    - DB_PASSWORD: Password MySQL Anda
    echo.
    pause
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan! Silakan install Python 3.8+
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Install dependencies
echo.
echo [INFO] Installing dependencies...
pip install -r requirements.txt

REM Check database
echo.
echo [INFO] Checking database...
python -c "from src.database import engine; engine.connect(); print('[OK] Database connection successful!')" 2>nul

if errorlevel 1 (
    echo [WARNING] Database connection failed!
    echo    Pastikan:
    echo    1. MySQL server berjalan
    echo    2. Database smartrujuk_db sudah dibuat
    echo    3. Credentials di .env sudah benar
    echo.
    set /p init="Initialize database now? (y/n): "
    if /i "%init%"=="y" (
        echo [INFO] Initializing database...
        python database/init_db.py
    )
)

REM Run application
echo.
echo [INFO] Starting SmartRujuk+ AI Agent...
echo    Open your browser at: http://localhost:8501
echo.
streamlit run app.py
