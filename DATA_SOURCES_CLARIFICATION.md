# Data Sources Clarification

## ⚠️ Penting: Koreksi Informasi Data Faskes

Dokumen ini menjelaskan sumber data yang sebenarnya digunakan dalam sistem SmartRujuk+ AI Agent.

---

## 📊 Pernyataan Sebelumnya (TIDAK AKURAT)

```
SmartRujuk+ menggunakan:
- AI Agent untuk rekomendasi cerdas
- Machine Learning untuk prediksi waktu tunggu
- Google Maps API untuk geolokasi
- SATUSEHAT API untuk data faskes ❌ SALAH
```

---

## ✅ Pernyataan yang BENAR

```
SmartRujuk+ menggunakan:
- AI Agent untuk rekomendasi cerdas
- Machine Learning untuk prediksi waktu tunggu
- Google Maps API untuk geolokasi
- Dataset Kaggle untuk data faskes (BPJS Faskes)
- SATUSEHAT API untuk data pasien & rujukan
```

---

## 📍 Alokasi Data Per Sumber

### 1. **Data Rumah Sakit/Faskes** ← Dataset Kaggle (CSV)
- **Source**: BPJS Faskes Indonesia Dataset dari Kaggle
- **URL**: https://www.kaggle.com/datasets/israhabibi/list-faskes-bpjs-indonesia
- **Format**: CSV import via `database/load_csv_data.py`
- **Total Records**: ~1,500-4,000 rumah sakit
- **Coverage**: Seluruh Indonesia
- **Fields**: Nama, Alamat, Koordinat GPS, Tipe Faskes, dll

### 2. **Data Pasien** ← SATUSEHAT API + Offline Sample
- **Source**: SATUSEHAT FHIR API (dengan offline fallback)
- **API Endpoint**: `GET /fhir-r4/v1/Patient`
- **Format**: FHIR Patient Resource (JSON)
- **Mapping**: Otomatis ke tabel `patients` di database
- **Fallback**: Sample data jika API tidak tersedia

### 3. **Data Rujukan** ← SATUSEHAT API + Offline Sample
- **Source**: SATUSEHAT FHIR API (dengan offline fallback)
- **API Endpoint**: `GET /fhir-r4/v1/ServiceRequest`
- **Format**: FHIR ServiceRequest Resource (JSON)
- **Mapping**: Otomatis ke tabel `referrals` di database
- **Fallback**: Sample data jika API tidak tersedia

### 4. **Data Organisasi (Hospitals)** ← SATUSEHAT API (Referensi Saja)
- **Source**: SATUSEHAT FHIR API
- **API Endpoint**: `GET /fhir-r4/v1/Organization`
- **Status**: ⚠️ **TIDAK DIGUNAKAN UNTUK DATA FASKES**
- **Catatan**: Sample data tersedia untuk testing, tetapi data rumah sakit utama dari CSV Kaggle

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   SmartRujuk+ System                    │
└─────────────────────────────────────────────────────────┘
           │                         │                │
           ▼                         ▼                ▼
    ┌────────────────┐      ┌────────────────┐  ┌──────────────┐
    │  Kaggle CSV    │      │  SATUSEHAT API │  │ Google Maps  │
    │  (BPJS Faskes) │      │  (FHIR R4)     │  │ API (offline)│
    └────────────────┘      └────────────────┘  └──────────────┘
           │                 │            │            │
           │    load_csv_    │ satusea    │          geolo
           │    data.py      │ hat_loader │          cate
           │                 │ .py        │
           │                 │            │
           ▼                 ▼            ▼
    ┌──────────────────────────────────────────────┐
    │           MySQL Database                     │
    │  ┌────────────┬──────────┬──────────────┐   │
    │  │ hospitals  │ patients │ referrals    │   │
    │  │ (1000+)    │ (FHIR)   │ (FHIR)       │   │
    │  └────────────┴──────────┴──────────────┘   │
    └──────────────────────────────────────────────┘
           │
           ▼
    ┌──────────────────────┐
    │  Streamlit App       │
    │  (Frontend)          │
    └──────────────────────┘
```

---

## 🔧 File-File yang Telah Dikoreksi

### 1. `app.py` ✅
**Baris 95-103**: Sidebar info box

**Sebelum:**
```python
st.info("""
SmartRujuk+ menggunakan:
- **AI Agent** untuk rekomendasi cerdas
- **Machine Learning** untuk prediksi waktu tunggu
- **Google Maps API** untuk geolokasi
- **SATUSEHAT API** untuk data faskes
""")
```

**Sesudah:**
```python
st.info("""
SmartRujuk+ menggunakan:
- **AI Agent** untuk rekomendasi cerdas
- **Machine Learning** untuk prediksi waktu tunggu
- **Google Maps API** untuk geolokasi
- **Dataset Kaggle** untuk data faskes (BPJS Faskes)
- **SATUSEHAT API** untuk data pasien & rujukan
""")
```

### 2. `README.md` ✅
**Baris 13-22**: Feature list

**Sebelum:**
```markdown
- **Integrasi SATUSEHAT API** untuk data faskes
```

**Sesudah:**
```markdown
- **Dataset Kaggle** untuk data faskes (BPJS Faskes Indonesia)
- **Integrasi SATUSEHAT API** untuk data pasien & rujukan
```

**Baris 470**: Data sources section

**Sebelum:**
```markdown
#### 3. **SATUSEHAT API** - Data fasilitas kesehatan resmi dari Kemenkes
```

**Sesudah:**
```markdown
#### 3. **SATUSEHAT API** - Data pasien dan rujukan dari Kemenkes
```

### 3. `SATUSEHAT_INTEGRATION_REPORT.md` ✅
**Section 2.1**: API Endpoints

**Ditambahkan catatan:**
```
- Organization resources (sample data only - not used for hospital data)
```

**Ditambahkan note:**
```
**Note:** Hospital data is loaded from Kaggle BPJS Faskes dataset via CSV import, 
NOT from SATUSEHAT API
```

---

## ✨ Ringkasan Koreksi

| Aspek | Sebelum | Sesudah |
|-------|---------|---------|
| **Data Faskes** | SATUSEHAT API ❌ | Dataset Kaggle CSV ✅ |
| **SATUSEHAT Usage** | Data faskes | Data pasien & rujukan |
| **Dokumentasi** | Tidak konsisten | Konsisten & akurat |
| **App UI** | Menyesatkan | Jelas & benar |
| **README** | Kurang akurat | Akurat & informatif |

---

## 🚀 Implementasi yang Benar

### Untuk Data Faskes:
```bash
# Load CSV dataset dari Kaggle
python database/load_csv_data.py --file "Data Faskes BPJS 2019.csv"

# Atau load semua datasets sekaligus
python database/load_all_datasets.py
```

### Untuk Data Pasien & Rujukan:
```bash
# Menggunakan SATUSEHAT API (dengan offline fallback)
# Code di: src/satusehat_loader.py
# Config: SATUSEHAT_ORG_ID, SATUSEHAT_CLIENT_ID, SATUSEHAT_CLIENT_SECRET
```

---

## 📚 Referensi

- **BPJS Faskes Dataset**: https://www.kaggle.com/datasets/israhabibi/list-faskes-bpjs-indonesia
- **Bed Ratio Dataset**: https://www.kaggle.com/datasets/yafethtb/dataset-rasio-bed-to-population-faskes-ii
- **SATUSEHAT Documentation**: https://satusehat.kemkes.go.id/platform/docs/
- **FHIR R4 Specification**: https://www.hl7.org/fhir/R4/

---

**Last Updated**: December 16, 2025
