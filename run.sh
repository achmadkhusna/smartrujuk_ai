#!/bin/bash
# SmartRujuk+ AI Agent - Quick Start Script

echo "=================================="
echo "SmartRujuk+ AI Agent"
echo "=================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  File .env tidak ditemukan!"
    echo "📝 Copying .env.example to .env..."
    cp .env.example .env
    echo "✅ File .env dibuat!"
    echo ""
    echo "⚙️  Silakan edit file .env dan sesuaikan konfigurasi database Anda:"
    echo "   - DB_PASSWORD: Password MySQL Anda"
    echo ""
    read -p "Tekan Enter setelah edit .env..."
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 tidak ditemukan! Silakan install Python 3.8+"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Check MySQL
if ! command -v mysql &> /dev/null; then
    echo "⚠️  MySQL command tidak ditemukan!"
    echo "   Pastikan MySQL sudah terinstall dan berjalan"
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Check database
echo ""
echo "🗄️  Checking database..."
python3 -c "from src.database import engine; engine.connect(); print('✅ Database connection successful!')" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "⚠️  Database connection failed!"
    echo "   Pastikan:"
    echo "   1. MySQL server berjalan"
    echo "   2. Database smartrujuk_db sudah dibuat"
    echo "   3. Credentials di .env sudah benar"
    echo ""
    read -p "Initialize database now? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔧 Initializing database..."
        python3 database/init_db.py
    fi
fi

# Run application
echo ""
echo "🚀 Starting SmartRujuk+ AI Agent..."
echo "   Open your browser at: http://localhost:8501"
echo ""
streamlit run app.py
