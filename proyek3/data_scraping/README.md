# Data Scraping FindServices (Proyek 3)

Modul ekstraksi data layanan (*services*) dan mitra (*users*) dari 3 platform marketplace freelance Indonesia:
1. **Projects.co.id** (https://projects.co.id/)
2. **Sribu.com** (https://www.sribu.com/id)
3. **Fastwork.id** (https://fastwork.id/)

---

## 🚀 Quick Start (Cara Cepat)

### 1. Masuk ke Folder & Pasang Dependensi
```powershell
cd c:\laragon\www\FindServices\proyek3\data_scraping
pip install -r requirements.txt
```

### 2. Jalankan Scraping Data
```powershell
# Jalankan scraping untuk semua sumber (Projects.co.id, Sribu, Fastwork):
python scripts/main_scraper.py --source all --limit 10

# ATAU jalankan mode mock/representatif (Cepat, aman, tanpa terhalang internet/anti-bot):
python scripts/main_scraper.py --generate-mock
```

### 3. Hasil Output Data
Data langsung tersedia di direktori:
* `data/clean/services.json` & `data/clean/services.csv`
* `data/clean/users.json` & `data/clean/users.csv`
* `data/seeds/ScrapedDataSeeder.php` (Laravel Seeder siap pakai)

### 4. Seeding ke Database FindServices (Laravel)
```powershell
# Salin seeder ke Laravel
Copy-Item "data\seeds\ScrapedDataSeeder.php" "..\..\database\seeders\ScrapedDataSeeder.php"

# Jalankan seeder
cd ..\..
php artisan db:seed --class=ScrapedDataSeeder
```

---

## 📋 Daftar Variabel Terkumpul

### Tabel SERVICES:
* `id` : ID unik numerik layanan
* `title` : Judul layanan
* `description` : Deskripsi lengkap layanan
* `price_min` : Batas harga terendah / harga paket dasar
* `price_max` : Batas harga tertinggi / harga paket premium
* `location` : Nama kota & wilayah di Indonesia
* `latitude` : Koordinat lintang numerik (Geocoded otomatis)
* `longitude` : Koordinat bujur numerik (Geocoded otomatis)
* `status` : Status layanan (`active`)
* `rating_avg` : Rata-rata nilai ulasan (skala 1.0 - 5.0)
* `tags / skills` : Daftar kata kunci keahlian / teknologi
* `total_completed_orders` : Jumlah pesanan yang berhasil diselesaikan
* `estimated_duration` : Estimasi waktu pengerjaan (contoh: "3 hari")

### Tabel USER:
* `name` : Nama lengkap / display name penyedia jasa
* `email` : Email unik terstandarisasi (`name@findservices.local`)
* `phone` : Nomor telepon/WhatsApp aktif format Indonesia (0812xxxxxxxx)
* `bio` : Deskripsi profil dan kualifikasi keahlian
* `address` : Alamat kota domisili penyedia jasa
* `working_hours` : Jam operasional / estimasi SLA respon

---

## 📖 Dokumentasi Lengkap
* [Panduan Teknis Scraping & Anti-Bot](file:///c:/laragon/www/FindServices/proyek3/data_scraping/docs/PANDUAN_SCRAPING.md)
* [Analisis Kritis Variabel, Isu Privasi & Saran Proyek 3](file:///c:/laragon/www/FindServices/proyek3/data_scraping/docs/ANALISIS_VARIABEL_DAN_SARAN.md)
