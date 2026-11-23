# PANDUAN LENGKAP DATA SCRAPING FINDSERVICES (PROYEK 3)

Dokumen ini merupakan panduan operasional teknis untuk melakukan ekstraksi (*scraping*), pembersihan data (*data cleaning*), normalisasi skema, dan seeding ke dalam basis data aplikasi **FindServices**.

---

## 1. Arsitektur Folder `data_scraping`

Struktur folder dirancang terisolasi, modular, dan terorganisir:

```text
proyek3/data_scraping/
├── data/
│   ├── clean/                 # Output data bersih & terstandarisasi
│   │   ├── services.json      # Dataset layanan (JSON)
│   │   ├── services.csv       # Dataset layanan (CSV / Excel)
│   │   ├── users.json         # Dataset user/freelancer (JSON)
│   │   └── users.csv          # Dataset user/freelancer (CSV)
│   ├── raw/                   # Snapshot data mentah hasil scraping
│   │   └── raw_scraped_*.json
│   └── seeds/                 # File Laravel Seeder siap pakai
│       └── ScrapedDataSeeder.php
├── docs/                      # Dokumentasi & panduan teknis
│   ├── PANDUAN_SCRAPING.md    # Panduan eksekusi & teknis scraper
│   └── ANALISIS_VARIABEL_DAN_SARAN.md # Kajian variabel, privasi, & saran
├── scripts/                   # Kode sumber scraper (Python)
│   ├── geo_helper.py          # Modul pemetaan geospasial & koordinat (Lat/Lng)
│   ├── data_transformer.py    # Modul pembersih data & konversi ke Seeder
│   ├── scrape_projects_co_id.py # Scraper spesifik Projects.co.id
│   ├── scrape_sribu.py        # Scraper spesifik Sribu.com
│   ├── scrape_fastwork.py     # Scraper spesifik Fastwork.id
│   └── main_scraper.py        # Orchestrator CLI utama
├── requirements.txt           # Daftar dependensi Python
└── README.md                  # Quickstart panduan ringkas
```

---

## 2. Prasyarat & Instalasi Lingkungan

Pastikan pada komputer Anda telah terpasang **Python 3.9+** dan manajer paket **pip**.

### Langkah 1: Buka Terminal PowerShell / Command Prompt
Arahkan ke folder `data_scraping`:
```powershell
cd c:\laragon\www\FindServices\proyek3\data_scraping
```

### Langkah 2: (Opsional) Buat Virtual Environment
Disarankan menggunakan virtual environment agar paket dependensi tidak bentrok dengan sistem global:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Langkah 3: Install Dependensi
Jalankan instalasi modul yang dibutuhkan:
```powershell
pip install -r requirements.txt
```
*Paket yang diinstal:*
* `requests`: Pengirim HTTP Request otomatis.
* `beautifulsoup4`: Parser HTML DOM tree.
* `pandas`: Pengolah data tabular dan export CSV/Excel.
* `fake-useragent`: Rotasi identitas header browser agar tidak terdeteksi sebagai bot sederhana.

---

## 3. Cara Menjalankan Scraper

Script utama dijalankan melalui file `scripts/main_scraper.py` yang memiliki argumen fleksibel:

### A. Menjalankan Scraping Seluruh Website (All Sources)
Mengambil data dari Projects.co.id, Sribu.com, dan Fastwork.id sekaligus:
```powershell
python scripts/main_scraper.py --source all --limit 10
```

### B. Menjalankan Scraping Per Website Tertentu
1. **Khusus Projects.co.id:**
   ```powershell
   python scripts/main_scraper.py --source projects_co_id --limit 10
   ```
2. **Khusus Sribu.com:**
   ```powershell
   python scripts/main_scraper.py --source sribu --limit 10
   ```
3. **Khusus Fastwork.id:**
   ```powershell
   python scripts/main_scraper.py --source fastwork --limit 10
   ```

### C. Mode Generator Mock Tervalidasi (Tanpa Internet / Bypass Anti-Bot)
Jika koneksi internet offline, jaringan lambat, atau target website sedang menerapkan pemblokiran IP/Cloudflare Turnstile yang ketat, gunakan opsi `--generate-mock`. Opsi ini akan memproses dataset representatif yang telah divalidasi ke skema FindServices:
```powershell
python scripts/main_scraper.py --generate-mock
```

---

## 4. Penanganan Anti-Scraping, Bot-Detection & WAF

Situs modern seperti Sribu dan Fastwork sering menggunakan WAF (*Web Application Firewall*) seperti Cloudflare, DataDome, atau AWS WAF. Berikut strategi mitigasi yang telah diterapkan pada script:

1. **Browser Fingerprint Emulation (Header Spoofing):**
   * Setiap request menyertakan header lengkap: `User-Agent` Chrome Windows resmi, `Accept-Language: id-ID,id`, `Accept: text/html...`, dan `Referer`.
2. **Polite Crawling & Rate Limiting:**
   * Script menyisipkan jeda (`time.sleep(1.5 s/d 3.0 detik)`) di antara setiap pergantian halaman untuk menghindari lonjakan traffic yang mencurigakan (*DDoS-like behavior*).
3. **Resilient Fallback Handling:**
   * Jika parsing HTML gagal akibat struktur DOM yang dinamis atau captcha, script tidak akan mengalami *crash*, melainkan melakukan *graceful fallback* ke mode representatif terverifikasi.
4. **Solusi Lanjutan (Jika Menghadapi JavaScript SPA Penuh):**
   * Jika ingin mengekstrak data dari halaman yang 100% dirender oleh klien JavaScript tanpa SSR, pasang modul **Playwright**:
     ```powershell
     pip install playwright
     playwright install chromium
     ```

---

## 5. Cara Impor Data ke Database FindServices (Laravel)

Hasil scraping telah otomatis dikompilasi menjadi sebuah **Laravel Database Seeder** bernama `ScrapedDataSeeder.php` di dalam folder `data/seeds/`.

### Langkah Eksekusi ke Database:
1. Salin file `ScrapedDataSeeder.php` ke folder seeder Laravel:
   ```powershell
   Copy-Item "c:\laragon\www\FindServices\proyek3\data_scraping\data\seeds\ScrapedDataSeeder.php" "c:\laragon\www\FindServices\database\seeders\ScrapedDataSeeder.php" -Force
   ```

2. Jalankan perintah database seed Laravel dari direktori root proyek:
   ```powershell
   cd c:\laragon\www\FindServices
   php artisan db:seed --class=ScrapedDataSeeder
   ```

3. Data `users` (penyedia jasa) dan `services` (layanan) langsung masuk ke basis data MySQL/MariaDB Laragon dengan status `active`, harga yang terformat rapi, koordinat latitude/longitude valid, dan relasi kategori yang sesuai!
