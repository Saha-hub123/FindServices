# ANALISIS VARIABEL DATA & SARAN IMPLEMENTASI SCRAPING
### Proyek 3: FindServices Marketplace

Dokumen ini memuat analisis kritis terhadap variabel data yang diminta, perbandingannya dengan kondisi nyata platform sumber (Projects.co.id, Sribu.com, Fastwork.id), kesesuaian dengan skema basis data Laravel `FindServices`, serta rekomendasi strategis untuk pilar **Optimalisasi Algoritma** dan **Split Payment Midtrans**.

---

## 1. Analisis Kritis Variabel yang Diminta

### A. Tabel `SERVICES` (Layanan)

| Variabel Diminta | Ketersediaan di Platform Sumber | Rekomendasi & Solusi Penanganan |
| :--- | :--- | :--- |
| `id` | Tersedia (ID internal platform sumber). | Dibuatkan penomoran ID sekuensial yang aman (`start_service_id = 201`) agar tidak bertabrakan (*collision*) dengan data transaksi lokal yang sudah ada di database FindServices. |
| `title` | **100% Tersedia** di semua platform. | Dilakukan *trimming* maksimal 150 karakter sesuai spesifikasi kolom migration `$table->string('title', 150)`. |
| `description` | **100% Tersedia** (deskripsi detail paket). | Disimpan lengkap dalam kolom `text('description')`. Tag HTML tag kotor dibersihkan (*sanitized*). |
| `price_min` & `price_max` | **Tersedia Parsial**.<br>• Projects.co.id: Mayoritas 1 harga tetap (*fixed*).<br>• Sribu & Fastwork: Ada paket berjenjang (*Bronze/Silver/Gold*). | • Jika platform memiliki paket, `price_min` = harga paket dasar, `price_max` = paket terlengkap.<br>• Jika platform hanya memuat satu harga (contoh: Rp 250.000), script otomatis memetakan `price_min = 250.000` dan mengestimasi batas atas `price_max = price_min * 1.5` untuk mendukung filter rentang harga di frontend FindServices. |
| `location` | **Tersedia pada level Kota/Provinsi** (contoh: "Jakarta Selatan", "Bandung", "Surabaya"). | Teks kota dinormalisasi ke format standar bahasa Indonesia (contoh: "Bandung, Jawa Barat"). |
| `latitude` & `longitude` | **TIDAK TERSEDIA** di platform sumber. Freelance digital tidak mempublikasikan koordinat GPS. | **Solusi Inovatif (`geo_helper.py`):**<br>Script dilengkapi database geolokasi 50+ kota di Indonesia. Saat teks lokasi terdeteksi (misal "Bandung"), script otomatis menginjeksi koordinat riil Bandung (`lat: -6.9175, lng: 107.6191`) ditambah mikro-variasi acak (± 500m s/d 1km). Hasil ini memastikan algoritma Haversine Formula / pencarian radius di FindServices dapat diuji secara fungsional. |
| `status` | Tersedia (aktif/tersedia). | Dipetakan langsung sebagai `'active'`. |
| `rating_avg` | **100% Tersedia** (skala 1.0 - 5.0). | Dikonversi ke tipe numerik float berpresisi 2 desimal (contoh: `4.92`). |
| `tags` / `skills` | **Tersedia** (berupa badge keahlian / kategori). | Digabung menjadi string dipisahkan koma (*comma-separated values*, misal: `"Laravel, Vue.js, MySQL"`) yang siap digunakan untuk pengujian algoritma *Full-Text Search* dan kata kunci. |
| `total_completed_orders` | **Tersedia** (contoh: "48 pesanan selesai"). | Diparsing menggunakan regex ke bilangan bulat integer murni (contoh: `48`). Variabel ini sangat krusial untuk algoritma perankingan popularitas tanpa membebani query `COUNT(*)`. |
| `estimated_duration` | **Tersedia** (contoh: "Pengerjaan 3 hari"). | Disimpan dalam format string terstandarisasi (contoh: `"3 hari"` atau integer durasi). |

---

### B. Tabel `USER` (Penyedia Jasa / Freelancer)

| Variabel Diminta | Ketersediaan di Platform Sumber | Rekomendasi & Solusi Penanganan |
| :--- | :--- | :--- |
| `name` | **100% Tersedia** (nama tampilan atau username freelancer). | Disimpan langsung ke kolom `name`. |
| `email` | **TIDAK TERSEDIA / DISEMBUNYIKAN KETAT** oleh semua platform. | **Analisis Privasi & Solusi:**<br>Platform freelancer secara tegas memblokir publikasi email untuk mencegah transaksi luar (*disintermediation*) dan mematuhi UU No. 27 Tahun 2022 tentang Perlindungan Data Pribadi (UU PDP).<br>• *Solusi Script:* Meng-generate email sintetis yang rapi dan unik berbasis username (contoh: `budisantoso101@findservices.local`). Ini memenuhi syarat `UNIQUE` & `NOT NULL` pada database Laravel tanpa melanggar privasi orang lain. |
| `phone` | **TIDAK TERSEDIA / DISEMBUNYIKAN KETAT**. | **Solusi Script:** Menghasilkan nomor telepon Indonesia realistis dengan kode operator resmi (0812, 0813, 0857, 0878) yang diikat unik ke ID pengguna, sehingga fitur WhatsApp/kontak di FindServices dapat langsung diuji coba. |
| `bio` | **Tersedia** di halaman profil freelancer. | Diambil dari bio profil publik atau di-generate ringkasan profesional relevan berdasarkan spesialisasi jasa. |
| `address` | **Tersedia pada level Kota**. | Diformat selaras dengan lokasi jasa (`SERVICES.location`). |
| `working_hours` | **Parsial** (biasanya ditampilkan sebagai *response time*, contoh: "Membalas dalam 1 jam"). | Diformat menjadi jam operasional kerja Indonesia yang terstruktur (contoh: `"Senin - Jumat: 08:00 - 17:00 WIB"` atau `"Fleksibel (Respon Cepat < 1 Jam)"`). |

---

## 2. Saran & Masukan Strategis untuk Proyek 3

### 1. Karakteristik Jasa Fisik vs Jasa Digital
* **Kondisi Eksisting Proyek:**  
  FindServices pada awalnya memiliki kategori jasa fisik lokal (seperti *Service AC*, *Pertukangan & Renovasi*, *Kebersihan/Cleaning*).  
* **Karakteristik Data Scraping:**  
  Platform seperti Projects.co.id, Sribu.com, dan Fastwork.id didominasi oleh jasa kreatif & digital (*Desain Grafis*, *Pembuatan Website*, *Editing Video*, *Penerjemahan*).
* **Saran Integrasi:**  
  Ini merupakan peluang bagus! Anda dapat memperkaya katalog FindServices sehingga memiliki portofolio ganda: **Jasa Fisik (On-site)** dan **Jasa Digital/Kreatif (Remote)**. Modul `data_transformer.py` sudah secara cerdas memetakan kategori hasil scraping ke `category_id: 7` (Desain & Kreatif), `category_id: 8` (IT & Komputer), `category_id: 9` (Pendidikan & Les), dan `category_id: 10` (Fotografi & Video).

### 2. Kebutuhan Data Tambahan untuk Pilar "Split Payment Midtrans"
Sebagaimana tercantum dalam kajian dokumen Proyek 3 (`KAJIAN_JURNAL_DAN_ANALISIS_VARIABEL_DATA.md`), implementasi **Split Payment (Midtrans Iris API)** membutuhkan data perbankan mitra penyedia jasa untuk proses pencairan dana (*payout/disbursement*).
* **Saran:**  
  Jika nantinya Anda menjalankan migrasi penambahan kolom rekening bank pada tabel `users`, tambahkan atribut dummy berikut pada seeder:
  * `bank_name` (contoh: `"BCA"`, `"Mandiri"`, `"BRI"`)
  * `bank_account_number` (contoh: `"1234567890"`)
  * `bank_account_holder` (sesuai `name` user)

### 3. Kebutuhan Kolom Baru pada Tabel `services` di FindServices
Saat ini tabel `services` eksisting FindServices belum memiliki kolom fisik untuk `tags`, `total_completed_orders`, dan `estimated_duration`.
* Pada `ScrapedDataSeeder.php`, data yang di-insert disesuaikan 100% dengan kolom migrasi eksisting agar *tidak terjadi error SQL*.
* Seluruh data lengkap (termasuk `tags`, `total_completed_orders`, dan `estimated_duration`) tersimpan utuh di dalam file `data/clean/services.json` dan `data/clean/services.csv`.
* **Saran:** Segera buat migration baru di Laravel untuk menambahkan 3 kolom tersebut:
  ```php
  Schema::table('services', function (Blueprint $table) {
      $table->string('tags')->nullable()->after('rating_avg');
      $table->unsignedInteger('total_completed_orders')->default(0)->after('tags');
      $table->string('estimated_duration', 50)->nullable()->after('total_completed_orders');
  });
  ```
  Setelah migrasi dijalankan, seeder dapat langsung mengisikan ketiga kolom ini secara permanen untuk mendukung algoritma rekomendasi dan pencarian.
