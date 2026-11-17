# KAJIAN JURNAL ILMIAH DAN ANALISIS VARIABEL DATA
### Proyek 3: Optimalisasi Algoritma dan Implementasi Split Payment Midtrans pada Website FindServices

Dokumen ini berisi tinjauan pustaka jurnal ilmiah terkait *data collection/scraping* pada *service marketplace*, evaluasi kelayakan variabel data eksisting pada `app/Models` website FindServices, serta rekomendasi skema penambahan variabel basis data untuk mendukung pilar **Optimalisasi Algoritma** dan **Split Payment Midtrans**.

---

## BAGIAN I: TINJAUAN JURNAL ILMIAH INTERNASIONAL

Berikut adalah jurnal ilmiah internasional *peer-reviewed* yang melakukan riset terhadap *service marketplace* (pasar jasa fisik/lokal dan digital) dengan metode *web scraping/data collection* untuk mengidentifikasi variabel-variabel kunci:

### 1. Jurnal 1: Analisis Ekstraksi Data Platform Jasa Fisik & Digital (TaskRabbit & Fiverr)
* **Judul:** *Bias in Online Freelance Marketplaces: Evidence from TaskRabbit and Fiverr*
* **Penulis:** Anikó Hannák, Claudia Wagner, David Garcia, Alan Mislove, Markus Strohmaier, Christo Wilson
* **Publikasi:** *Proceedings of the 2017 ACM Conference on Computer Supported Cooperative Work and Social Computing (CSCW '17)*, ACM, hlm. 1914–1933.
* **Tautan DOI:** [https://doi.org/10.1145/2998181.2998327](https://doi.org/10.1145/2998181.2998327)
* **Relevansi & Variabel yang Dikumpulkan (*Scraped Variables*):**
  Riset ini mengaudit algoritma pencarian dan perankingan pada **TaskRabbit** (platform jasa lokal on-demand untuk pertukangan, reparasi, kebersihan, pemindahan barang) dan **Fiverr**. Peneliti mengumpulkan lebih dari **13.500 profil mitra jasa** dengan mengekstraksi variabel-variabel kunci:
  1. **Variabel Jasa & Penawaran:** Kategori jasa (*service category*), tarif dasar per jam (*hourly rate*), jenis penagihan (tarif tetap vs tarif per jam), serta batas minimum tagihan (*minimum hours/rate*).
  2. **Variabel Lokasi & Visibilitas:** Koordinat/zona kota layanan (*service area / geographic radius*), serta nomor urut posisi (*search rank placement*) pada halaman pencarian.
  3. **Variabel Reputasi & Performa Mitra:** Jumlah pesanan yang diselesaikan (*completed tasks count*), waktu respon (*response time*), tingkat penerimaan pesanan (*acceptance rate*), nilai ulasan bintang (*star ratings*), dan status lencana performa (*Elite Tasker / verified badge*).

---

### 2. Jurnal 2: Identifikasi Variabel Kunci Perekrutan dan Transaksi pada Platform Jasa
* **Judul:** *Exploring Influential Factors in Hiring Freelancers in Online Labor Platforms: An Empirical Study*
* **Penulis:** Jie Ren, Vishal Raghupathi, Wullianallur Raghupathi
* **Publikasi:** *Economies (MDPI)*, Vol. 11, No. 3, Art. 80, 2023.
* **Tautan DOI:** [https://doi.org/10.3390/economies11030080](https://doi.org/10.3390/economies11030080)
* **Relevansi & Variabel yang Dikumpulkan (*Scraped Variables*):**
  Riset ini menggunakan teknik *web scraping* otomatis untuk mengumpulkan ribuan profil dan transaksi penyedia jasa guna memodelkan faktor penentu keberhasilan transaksi dan penetapan harga.
  1. **Variabel Kualifikasi & Human Capital:** Daftar keahlian spesifik (*skills taxonomy / tags*), sertifikasi terverifikasi (*verified credentials*), kelengkapan portofolio (jumlah gambar sampel karya), dan panjang deskripsi profil (*bio length*).
  2. **Variabel Transaksi Finansial:** Tarif penawaran, estimasi durasi pengerjaan (*estimated duration*), riwayat pendapatan kotor (*cumulative earnings*), dan rasio pemesanan ulang (*repeat client rate*).
  3. **Variabel Keandalan Sistem:** *Job Success Score (JSS)*, rasio pembatalan pesanan (*cancellation rate*), serta keaktifan terakhir mitra (*last active timestamp*).

---

### 3. Jurnal 3: Nilai Reputasi dan Mekanisme Penawaran pada Pasar Jasa Online
* **Judul:** *The Value of Reputation in an Online Freelance Marketplace*
* **Penulis:** Hema Yoganarasimhan
* **Publikasi:** *Marketing Science (INFORMS)*, Vol. 32, No. 6, hlm. 860–891, 2013.
* **Tautan DOI:** [https://doi.org/10.1287/mksc.2013.0809](https://doi.org/10.1287/mksc.2013.0809)
* **Relevansi & Variabel yang Dikumpulkan (*Scraped Variables*):**
  Riset empiris skala besar yang mengekstraksi data riwayat transaksi, mekanisme bidding/penawaran harga, bobot ulasan (*reputation scoring*), dan interaksi verifikasi identitas terhadap probabilitas pemilihan penyedia jasa.

---

## BAGIAN II: EVALUASI VARIABEL DATA PADA PROYEK FINDSERVICES

Berdasarkan audit teknis terhadap direktori `app/Models/`:
- `Service.php`
- `User.php`
- `Booking.php`
- `Review.php`
- `Category.php`
- `Gallery.php`
- `Chat.php`
- `Report.php`

### Kesimpulan Audit:
> **Status:** Variabel data yang diterapkan saat ini sudah cukup untuk kebutuhan **MVP (Minimum Viable Product)** fungsional, namun **BELUM MEMENUHI STANDAR** platform marketplace komersial dan **MASIH KURANG** untuk menopang dua pilar utama Proyek 3 (*Optimalisasi Algoritma* dan *Split Payment Midtrans*).

---

### Analisis Rinci per Model

#### 1. Model `Service.php` (Entitas Jasa)
* **Variabel Eksisting:**  
  `id`, `user_id`, `category_id`, `title`, `description`, `price_min`, `price_max`, `location`, `latitude`, `longitude`, `status`, `rating_avg`, `slug`, `timestamps`, `softDeletes`.
* **Kelebihan:**  
  Sudah memiliki data geolokasi numerik (`latitude`, `longitude`) dan rentang harga awal (`price_min`, `price_max`).
* **Kekurangan / Kesenjangan Data:**
  1. **`coverage_radius_km` (Radius Jangkauan Layanan):** Saat ini filter radius hanya diinput oleh customer di frontend. Seharusnya penyedia jasa dapat menentukan sendiri batas jangkauan layanannya (misal teknisi AC maksimal 10 km, tukang sedot WC 30 km).
  2. **`price_unit` (Satuan Tarif):** Tidak ada unit harga (apakah per jam, per kunjungan, per m², borongan, atau per unit perangkat).
  3. **`tags` / `skills` (Kata Kunci Keahlian):** Hanya memiliki 1 kategori umum (`category_id`). Tanpa tags keahlian (misal: "inverter", "las karbit", "cuci toren"), algoritma pencarian teks *Full-Text Search* tidak dapat melakukan pencocokan spesifik.
  4. **`total_completed_orders` (Counter Pesanan Selesai):** Untuk perankingan popularitas, sistem saat ini harus menghitung relasi `bookings` secara berulang (`COUNT(*)`) yang membebani query database.
  5. **`estimated_duration`:** Tidak ada perkiraan lama pengerjaan jasa.

---

#### 2. Model `User.php` (Pengguna & Mitra Penyedia Jasa)
* **Variabel Eksisting:**  
  `id`, `name`, `email`, `password`, `role`, `avatar`, `phone`, `bio`, `address`, `email_verified_at`, `timestamps`, `softDeletes`.
* **Kekurangan Krusial untuk Split Payment (Midtrans Iris API):**
  1. **`bank_code` / `bank_name`:** Belum ada kolom nama/kode bank mitra (BCA, Mandiri, BRI, BNI, dll.).
  2. **`bank_account_number`:** Belum ada kolom nomor rekening atau nomor e-wallet tujuan pencairan dana mitra.
  3. **`bank_account_holder`:** Belum ada nama pemilik rekening untuk validasi kesesuaian identitas sebelum eksekusi *automated disbursement*.
* **Kekurangan untuk Reputasi & Algoritma:**
  4. **`is_verified` (Status Verifikasi Identitas / KYC):** Ketiadaan verifikasi KTP/SIM mengurangi faktor kepercayaan (*trust & safety*) pada marketplace jasa fisik.
  5. **`response_time_minutes`:** Tidak ada pencatatan rata-rata kecepatan respon provider terhadap pesanan baru.
  6. **`working_hours` (Jadwal Operasional):** Sistem kuota saat ini hanya membatasi 5 pesanan per hari tanpa jam kerja operasional mitra.

---

#### 3. Model `Booking.php` (Transaksi Pemesanan)
* **Variabel Eksisting:**  
  `id`, `service_id`, `customer_id`, `provider_id`, `booking_date`, `booking_time`, `location`, `latitude`, `longitude`, `notes`, `initial_price`, `final_price`, `admin_fee`, `payment_method`, `status`, `payment_status`, `snap_token`, `timestamps`, `softDeletes`.
* **Kelebihan:**  
  State mesin status sudah cukup lengkap (`unpaid`, `pending`, `confirmed`, `in_progress`, `waiting_completion`, `completed`, `cancelled`, `rejected`).
* **Kekurangan Krusial untuk Split Payment:**
  1. **`provider_earnings` (Pendapatan Bersih Mitra):** Nilai bersih (`final_price - admin_fee`) belum tersimpan permanen secara eksplisit, menyulitkan audit keuangan.
  2. **`payout_status` (Status Pencairan Dana Mitra):** Belum ada pemisahan status pencairan (`pending`, `processing`, `disbursed`, `failed`) yang terpisah dari status bayar pelanggan (`payment_status`).
  3. **`payout_reference_no`:** Nomor referensi transfer dari API Midtrans Iris belum dicatat.
  4. **`disbursed_at`:** Waktu sukses pencairan dana ke rekening mitra belum terdokumentasi.

---

#### 4. Model `Review.php` (Ulasan & Rating)
* **Variabel Eksisting:**  
  `id`, `booking_id`, `service_id`, `user_id`, `rating`, `review`, `images` (JSON array), `timestamps`, `softDeletes`.
* **Kekurangan:**
  1. **Single-Metric Rating:** Hanya 1 rating agregat (1–5). Tidak ada penilaian multi-kriteria (Ketepatan Waktu, Kualitas Kerja, Keramahan).
  2. **`provider_reply`:** Belum ada fitur tanggapan balik penyedia jasa atas review pelanggan.

---

## BAGIAN III: MATRIKS PERBANDINGAN VARIABEL DATA

| Entitas | Variabel Eksisting di FindServices | Variabel Standar Industri / Literatur (TaskRabbit, Upwork) | Status Pemenuhan | Dampak terhadap Proyek 3 |
| :--- | :--- | :--- | :--- | :--- |
| **Service (Jasa)** | `title`, `description`, `price_min`, `price_max`, `lat/lng`, `rating_avg` | `coverage_radius_km`, `price_unit`, `tags/skills`, `total_completed_orders`, `estimated_duration` | ⚠️ Cukup untuk MVP, Kurang untuk Optimasi | Algoritma *Multi-Criteria Ranking* dan *Bounding Box* kurang presisi tanpa radius operasional & tags. |
| **User (Provider)** | `name`, `email`, `phone`, `avatar`, `bio`, `address` | `bank_code`, `bank_account_number`, `bank_account_holder`, `is_verified`, `response_time_minutes` | ❌ Kurang untuk Split Payment | Midtrans Iris API tidak dapat mentransfer dana otomatis tanpa nomor dan bank rekening tujuan. |
| **Booking** | `booking_date`, `initial_price`, `final_price`, `admin_fee`, `status`, `payment_status` | `provider_earnings`, `payout_status`, `payout_reference_no`, `disbursed_at` | ❌ Kurang untuk Rekonsiliasi Finansial | Sulit melacak status transfer dana escrow ke mitra secara transparan dan akuntabel. |
| **Review** | `rating` (1-5), `review`, `images` | `rating_punctuality`, `rating_quality`, `rating_communication`, `provider_reply` | ⚠️ Cukup untuk MVP | Rating Bayes bekerja baik, namun penilaian multi-dimensi akan meningkatkan kualitas review. |

---

## BAGIAN IV: REKOMENDASI SKEMA MIGRATION BASIS DATA (ACTION PLAN)

Agar Proyek 3 dapat berjalan maksimal, berikut adalah rancangan migrasi database yang disarankan:

```sql
-- 1. Penambahan pada tabel 'users' (Khusus Provider & Payout Rekening)
ALTER TABLE users ADD (
    bank_code VARCHAR(20) NULL AFTER address,
    bank_account_number VARCHAR(50) NULL AFTER bank_code,
    bank_account_holder VARCHAR(150) NULL AFTER bank_account_number,
    is_verified BOOLEAN DEFAULT FALSE AFTER bank_account_holder,
    response_time_minutes INT DEFAULT 0 AFTER is_verified
);

-- 2. Penambahan pada tabel 'services' (Khusus Algoritma & Filter Pencarian)
ALTER TABLE services ADD (
    price_unit ENUM('per_jam', 'per_hari', 'per_unit', 'per_kunjungan', 'borongan') DEFAULT 'per_kunjungan' AFTER price_max,
    coverage_radius_km INT DEFAULT 15 AFTER location,
    tags JSON NULL AFTER description,
    total_completed_orders INT DEFAULT 0 AFTER rating_avg
);

-- 3. Penambahan pada tabel 'bookings' (Khusus Split Payment & Midtrans Iris Engine)
ALTER TABLE bookings ADD (
    provider_earnings DECIMAL(12, 2) NULL AFTER admin_fee,
    payout_status ENUM('pending', 'processing', 'disbursed', 'failed') DEFAULT 'pending' AFTER payment_status,
    payout_reference_no VARCHAR(100) NULL AFTER payout_status,
    disbursed_at TIMESTAMP NULL AFTER payout_reference_no
);
```

---

## BAGIAN V: PEMBAGIAN TUGAS IMPLEMENTASI KELOMPOK

1. **Mohammad Isa Widianto (Split Payment Midtrans):**
   * Mengimplementasikan migrasi data rekening bank pada `users`.
   * Mengimplementasikan kalkulasi `provider_earnings` dan pelacakan `payout_status` pada `bookings`.
   * Menghubungkan endpoint API Midtrans Iris untuk eksekusi transfer dana otomatis saat status booking berubah menjadi `completed`.
   * Memvalidasi keamanan *webhook* Midtrans Iris untuk mencatat status keberhasilan transfer pada kolom `disbursed_at`.

2. **Faidil Zahpar (Optimalisasi Algoritma):**
   * Mengimplementasikan kolom `coverage_radius_km`, `tags`, dan `total_completed_orders` pada `services`.
   * Membangun indeks *Full-Text Search (FTS)* pada `title`, `description`, dan `tags`.
   * Merancang kueri geospasial *Bounding Box Pre-Filtering* berbasis koordinat lintang/bujur dan radius layanan mitra sebelum eksekusi rumus *Haversine*.
   * Mengintegrasikan formula perankingan multi-kriteria: Relevansi Teks + Jarak Geografis + Bayesian Rating.
