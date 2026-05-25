# Kuliah_SPK-Bansos

> Sistem pendukung keputusan bantuan sosial menggunakan algoritma AHP, SAW, dan K-Means.

![GitHub stars](https://img.shields.io/github/stars/BimaniSakti/Kuliah_SPK-Bansos?style=for-the-badge\&logo=github) ![GitHub forks](https://img.shields.io/github/forks/BimaniSakti/Kuliah_SPK-Bansos?style=for-the-badge\&logo=github) ![GitHub issues](https://img.shields.io/github/issues/BimaniSakti/Kuliah_SPK-Bansos?style=for-the-badge\&logo=github) ![Last commit](https://img.shields.io/github/last-commit/BimaniSakti/Kuliah_SPK-Bansos?style=for-the-badge\&logo=github) ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge\&logo=python\&logoColor=white)

## 📑 Daftar Isi

* [Deskripsi](#deskripsi)
* [Fitur Utama](#fitur-utama)
* [Use Case](#use-case)
* [Tech Stack](#tech-stack)
* [Quick Start](#quick-start)
* [Dependensi Utama](#dependensi-utama)
* [Struktur Proyek](#struktur-proyek)
* [Setup Development](#setup-development)
* [Kontribusi](#kontribusi)

## 📝 Deskripsi

Kuliah_SPK-Bansos adalah sistem pendukung keputusan berbasis web yang dirancang untuk mengevaluasi dan menganalisis tingkat kemiskinan dalam distribusi bantuan sosial (Bansos) di Jawa Barat, Indonesia. Aplikasi ini menyediakan kerangka evaluasi yang lebih objektif untuk menilai dan memprioritaskan wilayah menggunakan metode statistik dan machine learning dibandingkan klasifikasi manual.

## ✨ Fitur Utama

* **📊 Mesin Keputusan AHP dan SAW** — Menghitung prioritas bantuan wilayah menggunakan metode Analytic Hierarchy Process (AHP) dan Simple Additive Weighting (SAW).
* **🔍 Analisis Clustering K-Means** — Mengelompokkan data kemiskinan wilayah ke dalam beberapa cluster serta mengevaluasi performa model menggunakan silhouette score.
* **📁 Import CSV dan Manajemen Data** — Memungkinkan administrator mengimpor file CSV sosial ekonomi langsung ke database serta melakukan operasi CRUD pada data wilayah.
* **🔒 Autentikasi Berbasis Session** — Mengamankan halaman admin dan pengelolaan data menggunakan sistem login dan logout berbasis session Flask.

## 🎯 Use Case

* Mengklasifikasikan dataset tingkat kemiskinan wilayah di Jawa Barat ke dalam beberapa tingkat prioritas menggunakan algoritma clustering.
* Melakukan perangkingan wilayah penerima bantuan sosial berdasarkan analisis multi-kriteria menggunakan metode SAW dan AHP.
* Menjadi media pembelajaran dan implementasi sistem pendukung keputusan dalam konteks akademik maupun perencanaan pemerintahan daerah.

## 🛠️ Tech Stack

* 🐍 **Python**

**Library utama:** NumPy, Pandas

## ⚡ Quick Start

```bash

# 1. Clone repository
git clone https://github.com/BimaniSakti/Kuliah_SPK-Bansos.git

# 2. Membuat & mengaktifkan virtual environment
python -m venv venv && source venv/bin/activate

# 3. Install dependency
pip install -r requirements.txt
```

## 🛠️ Setup Development

### Python

1. Install Python (disarankan versi 3.10+)
2. Jalankan `python -m venv venv && source venv/bin/activate`
   (Windows: `venv\Scripts\activate`)
3. Install dependency menggunakan `pip install -r requirements.txt`

## 👥 Kontribusi

Kontribusi sangat terbuka. Berikut alur kontribusi standar:

1. **Fork** repository
2. **Clone** repository hasil fork:

   ```bash
   git clone https://github.com/BimaniSakti/Kuliah_SPK-Bansos.git
   ```
3. Buat branch baru:

   ```bash
   git checkout -b feature/nama-fitur
   ```
4. Commit perubahan:

   ```bash
   git commit -m "feat: menambahkan fitur baru"
   ```
5. Push ke repository:

   ```bash
   git push origin feature/nama-fitur
   ```
6. Buat pull request

Harap mengikuti style kode yang sudah ada dan menambahkan pengujian untuk fitur baru jika diperlukan.

---
