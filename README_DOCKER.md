## SmartRujuk+ AI (Docker Setup) 🐳🏥

SmartRujuk+ AI adalah aplikasi berbasis Streamlit dengan database MySQL yang telah dikontainerisasi menggunakan Docker, sehingga dapat dijalankan dengan mudah tanpa konfigurasi manual environment.

## 🧱 Arsitektur Docker

Project ini berjalan menggunakan 2 container Docker:

MySQL → Database utama

Streamlit → Web Application (AI Agent & Dashboard)

User Browser
     │
     ▼
Streamlit App (Container)
     │
     ▼
MySQL Database (Container)

## 📋 Prasyarat

Pastikan sistem telah memenuhi syarat berikut:

- Docker Desktop sudah terinstal dan dalam kondisi running

- Browser (Chrome / Edge / Firefox)

- Tidak perlu install Python, MySQL, atau dependency lain secara manual.

## 📁 Struktur File Penting

Pastikan file dan folder berikut berada di root project:

- docker-compose.yml

- Dockerfile

- entrypoint.sh

- requirements.txt

- app.py

- .env.example

- docker/mysql-init/ (berisi file .sql untuk inisialisasi database)

## ⚙️ Konfigurasi Environment (.env)

Sebelum menjalankan aplikasi dari source, buat file .env.

=> Windows (PowerShell)
- Copy-Item .env.example .env

- File .env berisi konfigurasi database dan kredensial aplikasi.
- Tidak perlu diubah kecuali ada kebutuhan khusus.


## ============== CARA KE-1 ===============

🚀 Menjalankan Aplikasi (Direkomendasikan — Docker Hub)

## Ini adalah cara paling mudah tanpa build ulang.

- docker pull khusnafz/smartrujuk-agent-ai:latest
- docker run -d -p 8501:8501 khusnafz/smartrujuk-agent-ai:latest


## Akses aplikasi melalui browser:

http://localhost:8501

## 🐳 Docker Image

Docker image tersedia di Docker Hub:

🔗 https://hub.docker.com/r/khusnafz/smartrujuk-agent-ai



## ========== CARA KE-2 ==============

🧪 Menjalankan Aplikasi (Dari Source / File ZIP)
1️⃣ Menjalankan Aplikasi (Pertama Kali)

## Buka terminal di folder project, lalu jalankan:

- docker compose up -d --build

2️⃣ Akses Aplikasi

## Buka browser dan akses:

http://localhost:8501

3️⃣ Menghentikan Aplikasi (Aman)
- docker compose stop

4️⃣ Menjalankan Aplikasi Kembali
- docker compose start

📝 Catatan Penting

- Pastikan Docker Desktop berjalan

- Port default aplikasi adalah 8501

- Jika terjadi konflik port, ubah konfigurasi port di docker-compose.yml

✅ Ringkasan

- Aplikasi telah dikontainerisasi menggunakan Docker

- Mendukung eksekusi melalui:

- Docker Hub (tanpa build ulang)

- Source Code / ZIP (menggunakan Docker Compose)


- Setup cepat, portable, dan siap dijalankan di berbagai environment
