# Smart Rujuk AI

## Deskripsi Singkat

**Smart Rujuk AI** adalah aplikasi berbasis **Streamlit** yang memanfaatkan **AI** untuk membantu proses rujukan (smart referral). Aplikasi ini dirancang agar **mudah dijalankan dan direproduksi** menggunakan **Docker** dan **Docker Compose**, tanpa perlu instalasi Python, MySQL, atau dependensi lain secara manual.

Project ini dibuat untuk keperluan **akademik (tugas kuliah / evaluasi dosen)** dengan pendekatan **deployment-ready** seperti di industri.

---

## Teknologi yang Digunakan

* **Python 3.11**
* **Streamlit** (Web App)
* **MySQL 8.0** (Database)
* **SQLAlchemy** (ORM)
* **Docker & Docker Compose**
* **Docker Hub** (Image Registry)

---

## Arsitektur Aplikasi

Aplikasi ini menggunakan **arsitektur multi-container**:

* **Container App**: Streamlit + AI logic
* **Container Database**: MySQL 8.0

Kedua container dikelola menggunakan **docker-compose** dan berkomunikasi melalui **Docker internal network**.

---

## Prasyarat (Sebelum Menjalankan)

Pastikan di komputer Anda sudah terinstall:

1. **Docker** (Desktop / Engine)
2. **Docker Compose** (sudah termasuk di Docker Desktop terbaru)

> Tidak perlu menginstall Python, MySQL, atau library lain.

---

## Struktur File yang Digunakan

Struktur minimal untuk menjalankan aplikasi:

```
smart-rujuk-ai/
├── docker-compose.yml
└── .env
```

---

## Konfigurasi Environment (.env)

Buat file `.env` di folder yang sama dengan `docker-compose.yml`.

Contoh **.env (versi demo akademik)**:

```
DB_NAME=smartrujuk_db
DB_USER=root
DB_PASSWORD=smartrujuk_demo
```

> ⚠️ Catatan:
>
> * File `.env` ini **hanya untuk demo akademik**
> * Tidak berisi credential produksi atau data sensitif

---

## Docker Compose Configuration

File `docker-compose.yml` akan:

* Menjalankan MySQL
* Menunggu MySQL siap (healthcheck)
* Menjalankan aplikasi Streamlit dari Docker Hub

Image aplikasi diambil langsung dari Docker Hub:

```
khusnafz/smartrujuk-agent:latest
```

---

## Cara Menjalankan Aplikasi (Satu Perintah)

Dari folder project, jalankan:

```bash
docker compose up -d
```

Docker akan otomatis:

1. Mengunduh image aplikasi dari Docker Hub
2. Menjalankan MySQL
3. Menjalankan aplikasi Streamlit

---

## Mengakses Aplikasi

Buka browser dan akses:

```
http://localhost:8501
```

Jika halaman Streamlit terbuka, maka aplikasi **berjalan dengan sukses**.

---

## Menghentikan Aplikasi

Untuk menghentikan aplikasi:

```bash
docker compose down
```

Untuk menghentikan sekaligus menghapus database (fresh start):

```bash
docker compose down -v
```

---

## Keunggulan Pendekatan Ini

* ✅ Tidak perlu setup manual environment
* ✅ Mudah direproduksi di komputer lain
* ✅ Konsisten antara development dan deployment
* ✅ Mendekati standar industri
* ✅ Cocok untuk evaluasi akademik

---

## Catatan Akademik

* Project ini dibuat untuk keperluan **pembelajaran dan evaluasi**
* Konfigurasi database dan environment **bukan untuk produksi**
* Seluruh dependency dikemas menggunakan Docker untuk kemudahan penilaian

---

## Penutup

Dengan pendekatan Docker-based deployment ini, aplikasi **Smart Rujuk AI** dapat dijalankan di berbagai environment secara konsisten hanya dengan satu perintah.

Terima kasih.
