# SmartRujuk+ AI (Docker Setup)

Project ini berjalan menggunakan **2 container Docker**:
- **MySQL** (database)
- **Streamlit** (web app)


## Prasyarat
- **Docker Desktop** sudah terinstal & running
- (Opsional) Git, kalau project dijalankan dari repository GitHub

---

## Struktur File Penting
Pastikan file-file ini ada di root project:
- `docker-compose.yml`
- `Dockerfile`
- `entrypoint.sh`
- `requirements.txt`
- `app.py`
- folder `docker/mysql-init/` (berisi file `.sql`)


---

## Konfigurasi Environment (.env)
1. Salin file contoh menjadi `.env`:

   **Windows (PowerShell):**
   ```powershell
   Copy-Item .env.example .env


---


## Menjalankan Aplikasi (Pertama Kali)
1. Buka terminal di folder project
   ```powershell
   docker compose up -d --build

2. Akses aplikasi di browser
   http://localhost:8501

3. Menghentikan Aplikasi (Aman)
   ```powershell
   docker compose stop

4. Menjalankan Aplikasi lagi 
   ```powershell
   docker compose start
