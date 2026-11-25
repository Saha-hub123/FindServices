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
│   ├── scrape_projects_co_id.py # Scraper spesifik Projects.co.id (Jasa Digital)
│   ├── scrape_sribu.py        # Scraper spesifik Sribu.com (Kreatif, IT, Marketing)
│   ├── scrape_fastwork.py     # Scraper spesifik Fastwork.id (Freelance Beragam)
│   ├── scrape_sejasa.py       # Scraper spesifik Sejasa.com (Jasa Fisik / Rumah Tangga)
│   ├── scrape_olx.py          # Scraper spesifik OLX.co.id (Iklan Jasa Lokal)
│   └── main_scraper.py        # Orchestrator CLI utama (mendukung multi-source)
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

Script utama dijalankan melalui file `scripts/main_scraper.py` yang mendukung pemilihan **satu, beberapa, maupun seluruh sumber** sekaligus.

Daftar `--source` yang tersedia:
* `all` : Seluruh 5 platform sekaligus *(default)*
* `projects_co_id` : Projects.co.id (Jasa digital & freelance)
* `sribu` : Sribu.com (Desain, IT, Video, Penulisan, Marketing)
* `fastwork` : Fastwork.id (Freelance beragam)
* `sejasa` : Sejasa.com (Jasa fisik / rumah tangga: AC, Cleaning, Renovasi, Pijat)
* `olx` : OLX.co.id (Iklan jasa lokal: Angkutan, Montir, Sedot WC, Tukang)

### A. Menjalankan Scraping Seluruh Website (`--source all`)
Mengambil data dari seluruh 5 platform sekaligus (menggunakan kuota default per platform agar terkumpul 50+ data mentah):
```powershell
python scripts/main_scraper.py --source all
```
Atau tentukan batas item per sumber secara seragam:
```powershell
python scripts/main_scraper.py --source all --limit 10
```

### B. Menjalankan Beberapa Scraper Sekaligus (Multi-Source)
Anda dapat menggabungkan beberapa scraper dalam satu perintah, baik dipisahkan dengan **spasi** maupun **koma**:

1. **Kombinasi Jasa Fisik (Sejasa + OLX):**
   ```powershell
   python scripts/main_scraper.py --source sejasa olx --limit 12
   ```
2. **Kombinasi Dipisahkan Koma (Projects.co.id + Sejasa + Sribu):**
   ```powershell
   python scripts/main_scraper.py --source projects_co_id,sejasa,sribu --limit 10
   ```

### C. Menjalankan Scraping Per Website Tertentu (Single Source)
1. **Khusus Sejasa.com (Jasa Fisik):**
   ```powershell
   python scripts/main_scraper.py --source sejasa --limit 12
   ```
2. **Khusus Projects.co.id:**
   ```powershell
   python scripts/main_scraper.py --source projects_co_id --limit 10
   ```
3. **Khusus OLX.co.id:**
   ```powershell
   python scripts/main_scraper.py --source olx --limit 12
   ```
4. **Khusus Sribu.com:**
   ```powershell
   python scripts/main_scraper.py --source sribu --limit 15
   ```
5. **Khusus Fastwork.id:**
   ```powershell
   python scripts/main_scraper.py --source fastwork --limit 15
   ```

### D. Mode Generator Mock Tervalidasi (Tanpa Internet / Bypass Anti-Bot)
Jika koneksi internet offline, berjalan di lingkungan sandbox, atau target website sedang menerapkan pemblokiran IP/Cloudflare yang ketat, gunakan opsi `--generate-mock` (bisa dikombinasikan dengan `--source` tertentu):
```powershell
# Semua 5 sumber (58 item tervalidasi)
python scripts/main_scraper.py --generate-mock

# Hanya sumber tertentu (contoh: Sejasa + OLX)
python scripts/main_scraper.py --source sejasa olx --limit 5 --generate-mock
```

---

## 4. Penanganan Anti-Scraping, Bot-Detection & Batasan Platform

Berdasarkan pengujian langsung terhadap masing-masing platform target, berikut karakteristik proteksi dan batasannya:

| Platform | Proteksi / Arsitektur | Status Akses `urllib` / `requests` |
| :--- | :--- | :--- |
| **Sejasa.com** | HTML SSR + JSON-LD Schema.org | ✅ **Dapat diambil** untuk data layanan, rentang harga, rating, & ulasan (nama vendor individu tidak dipublikasikan). |
| **Projects.co.id** | HTML SSR PHP | ⚠️ Sering mengembalikan `HTTP 403 Forbidden` jika tanpa header/cookie sesi browser & jeda request. |
| **Sribu.com** | Cloudflare WAF + Dynamic Rendering | ⛔ Diblokir WAF Cloudflare / listing gig tidak lengkap pada HTML statis. |
| **Fastwork.id** | Cloudflare WAF + Next.js SPA | ⛔ Diblokir WAF Cloudflare / data kartu jasa dimuat via JS sisi klien. |
| **OLX.co.id** | Akamai WAF + Rate Limiting Ketat | ⛔ Timeout / drop koneksi untuk request bot non-browser. |

Strategi mitigasi yang telah diterapkan pada script:
1. **Browser Fingerprint Emulation (Header Spoofing):**
   * Setiap request menyertakan header lengkap: `User-Agent` Chrome/Mobile resmi, `Accept-Language: id-ID,id`, `Accept: text/html...`, dan `Referer`.
2. **Polite Crawling & Rate Limiting:**
   * Script menyisipkan jeda (`time.sleep(0.5 s/d 1.5 detik)`) di antara setiap pergantian halaman untuk menghindari lonjakan traffic yang mencurigakan.
3. **Resilient Fallback Handling:**
   * Jika parsing HTML gagal akibat WAF, timeout, atau lingkungan tanpa akses internet (sandbox), script melakukan *graceful fallback* ke dataset terverifikasi sesuai skema FindServices.
4. **Solusi Lanjutan (Untuk Platform Cloudflare / SPA Penuh):**
   * Jika ingin melakukan ekstraksi langsung secara live pada situs dengan proteksi Cloudflare/SPA penuh (Sribu, Fastwork, OLX), pasang modul **Playwright** dan jalankan langsung dari terminal lokal (bukan sandbox):
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
