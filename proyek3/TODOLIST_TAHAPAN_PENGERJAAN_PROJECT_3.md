# TODOLIST & ROADMAP PENGERJAAN PROYEK 3
### Website FindServices: Optimalisasi Algoritma dan Implementasi Split Payment Midtrans

Dokumen ini memuat panduan langkah-demi-langkah (*step-by-step roadmap*), urutan prioritas, dan daftar checklist tugas (*ToDo List*) untuk menyelesaikan Proyek 3 secara terstruktur, terbagi atas kontribusi masing-masing anggota dan tahapan kolaboratif.

---

## DAFTAR PEMBAGIAN PERAN & TANGGUNG JAWAB

* **Faidil Zahpar (NIM: 714240007):** Penanggung jawab **Pilar I: Optimalisasi Algoritma** (Pencarian *Full-Text*, Geospasial *Bounding Box Haversine*, dan *Multi-Criteria Weighted Ranking*).
* **Mohammad Isa Widianto (NIM: 714240013):** Penanggung jawab **Pilar II: Implementasi Split Payment Midtrans** (Integrasi Midtrans Snap Escrow, Midtrans Iris Automated Disbursement, Pengaturan Rekening Bank Mitra, dan Keamanan Webhook).

---

## DIAGRAM ALUR FASE PENGERJAAN

```
[FASE 0: PERSIAPAN & BASIS DATA BERSAMA]
  ├── Setup Git Feature Branching & Sandbox Environment
  ├── Migrasi Skema Basis Data Baru (users, services, bookings, payout_logs)
  └── Pembuatan Database Seeder Uji (100 - 5.000 data jasa)
           │
           ├───────────────────────────────────────┐
           ▼                                       ▼
[FASE 1: OPTIMALISASI ALGORITMA]        [FASE 2: SPLIT PAYMENT MIDTRANS]
  (Penanggung Jawab: Faidil)              (Penanggung Jawab: Isa)
  ├── Audit & Catat Latensi Lama          ├── Setup Kredensial Midtrans Iris
  ├── Implementasi MySQL Full-Text        ├── Fitur Pengaturan Rekening Mitra
  ├── Bounding Box Pre-Filtering          ├── Penyesuaian Snap Token & Escrow
  ├── Multi-Criteria Weighted Ranking     ├── Job Queue Automated Disbursement
  └── Benchmarking & Stress Testing       └── Verifikasi Signature & Idempotency
           │                                       │
           └───────────────────┬───────────────────┘
                               ▼
[FASE 3: INTEGRASI & PENGUJIAN AKHIR BERSAMA]
  ├── Pengujian End-to-End Transaksi & Pencarian
  ├── Uji Penanganan Error (Edge Cases & Concurrency)
  └── Pengumpulan Metrik Evaluasi untuk Sidang
                               ▼
[FASE 4: DOKUMENTASI LAPORAN & PRESENTASI]
```

---

## CHECKLIST LENGKAP TAHAPAN PENGERJAAN

### FASE 0: FONDASI BERSAMA & PERSIAPAN LINGKUNGAN
*(Dikerjakan bersama oleh Faidil & Isa pada Minggu 1)*

- [ ] **0.1 Standarisasi Git Repository & Feature Branches**
  - [ ] Pastikan branch `main` stabil dan terbebas dari error linting/runtime.
  - [ ] Buat branch khusus: `feature/algorithm-optimization` (Faidil) dan `feature/split-payment-midtrans` (Isa).
- [ ] **0.2 Pembuatan Migrasi Basis Data Baru**
  - [ ] Buat migration untuk tabel `users`: tambah kolom `bank_code`, `bank_account_number`, `bank_account_holder`, `is_verified`, `response_time_minutes`.
  - [ ] Buat migration untuk tabel `services`: tambah kolom `price_unit`, `coverage_radius_km`, `tags` (JSON), `total_completed_orders`.
  - [ ] Buat migration untuk tabel `bookings`: tambah kolom `provider_earnings`, `payout_status`, `payout_reference_no`, `disbursed_at`.
  - [ ] Buat migration tabel baru `payout_logs` (riwayat detail request & response disbursement Iris untuk audit trail).
  - [ ] Jalankan `php artisan migrate` dan pastikan skema terbentuk sempurna.
- [ ] **0.3 Pembuatan Data Dummy Seeder untuk Pengujian**
  - [ ] Buat Seeder `BenchmarkServiceSeeder` yang mampu menghasilkan data 100, 1.000, hingga 5.000 data jasa lengkap dengan koordinat acak di sekitar area tertentu (misal: area Bandung/Jakarta) dan relasi kategori.
  - [ ] Siapkan data ulasan dummy agar perhitungan Bayesian Rating dapat diuji.

---

### FASE 1: OPTIMALISASI ALGORITMA
*(Fokus Penanggung Jawab: **Faidil Zahpar**)*

#### Tahap 1.1: Audit & Baseline Latency (Merekam Data Awal)
- [ ] Pasang alat profiler kueri (aktifkan Laravel DB Query Logging atau Laravel Telescope).
- [ ] Uji performa kueri lama (`SearchController.php` dengan `LIKE '%query%'` dan `MarketplaceController.php` dengan raw Haversine).
- [ ] Catat metrik awal ke dalam tabel catatan:
  * Waktu eksekusi query (*Execution Time* dalam milidetik).
  * Penggunaan memori (*Memory Peak*).
  * Efisiensi CPU pada jumlah data 100, 1.000, dan 5.000 record.

#### Tahap 1.2: Implementasi MySQL Full-Text Search (FTS)
- [ ] Tambahkan indeks `FULLTEXT` pada kolom `title`, `description`, dan `tags` di migration tabel `services`.
- [ ] Perbarui kueri pencarian pada `SearchController.php`:
  * Ganti klausa `WHERE title LIKE ? OR description LIKE ?` menjadi `WHERE MATCH(title, description) AGAINST(? IN NATURAL LANGUAGE MODE)`.
  * Ambil skor relevansi teks menggunakan kueri `SELECT *, MATCH(title, description) AGAINST(?) AS relevance_score`.
- [ ] Tambahkan sanitasi input kata kunci pencarian untuk mencegah syntax error pada operator FTS.

#### Tahap 1.3: Implementasi Bounding Box Pre-Filtering (Optimasi Spasial)
- [ ] Buat fungsi pembantu (*helper class* atau *scope model*) `scopeWithinBoundingBox($query, $userLat, $userLng, $radiusKm)` di model `Service.php`.
- [ ] Hitung selisih batas kotak koordinat:
  $$\Delta \text{lat} = \frac{r}{6371} \times \frac{180}{\pi}$$
  $$\Delta \text{lon} = \frac{r}{6371 \times \cos(\text{userLat} \times \frac{\pi}{180})} \times \frac{180}{\pi}$$
- [ ] Pasang filter koordinat cepat sebelum rumus trigonometri dijalankan:
  ```php
  $query->whereBetween('latitude', [$userLat - $deltaLat, $userLat + $deltaLat])
        ->whereBetween('longitude', [$userLng - $deltaLon, $userLng + $deltaLon]);
  ```
- [ ] Tambahkan indeks numerik komposit pada tabel `services`: `INDEX(latitude, longitude)` agar filter bounding box langsung memanfaatkan B-Tree index.

#### Tahap 1.4: Implementasi Multi-Criteria Weighted Ranking
- [ ] Rumuskan dan terapkan formula pembobotan hibrida pada `MarketplaceController.php`:
  1. **Skor Relevansi Teks ($S_{\text{text}}$):** Dinormalisasi ke skala $[0, 1]$.
  2. **Skor Jarak ($S_{\text{distance}}$):** Dihitung berbanding terbalik: $\max(0, 1 - \frac{d}{r_{\text{max}}})$.
  3. **Skor Reputasi Bayes ($S_{\text{rating}}$):** Dihitung dengan rumus:
     $$S_{\text{rating}} = \frac{v}{v + m} \cdot R_s + \frac{m}{v + m} \cdot C$$
     *(di mana $v = \text{jumlah ulasan jasa}, m = 5 \text{ (ambang batas)}, R_s = \text{rating jasa}, C = \text{rata-rata rating platform})*.*
- [ ] Gabungkan ke dalam satu skor total:
  $$S_{\text{final}} = (w_1 \cdot S_{\text{text}}) + (w_2 \cdot S_{\text{distance}}) + (w_3 \cdot S_{\text{rating}})$$
  *(Rekomendasi bobot awal: $w_1 = 0.4$, $w_2 = 0.35$, $w_3 = 0.25$)*.
- [ ] Urutkan data berdasarkan `ORDER BY final_score DESC`.

#### Tahap 1.5: Penyesuaian Antarmuka Frontend (Vue 3 / Inertia)
- [ ] Perbarui halaman `Marketplace/Index.vue` untuk mendukung filter baru (pilihan satuan tarif, filter jarak dinamis, dan tags keahlian).
- [ ] Tampilkan indikator jarak akurat (misal: "2.3 km dari lokasi Anda") dan lencana rating pada kartu jasa.

#### Tahap 1.6: Pengujian & Benchmarking Kinerja Algoritma
- [ ] Jalankan pengujian komparasi antara algoritma lama vs algoritma baru pada dataset 100, 1.000, dan 5.000 data.
- [ ] Ekspor hasil perbandingan latensi ke dalam format grafik/tabel untuk bahan Bab IV Laporan Proyek 3.

---

### FASE 2: IMPLEMENTASI SPLIT PAYMENT MIDTRANS
*(Fokus Penanggung Jawab: **Mohammad Isa Widianto**)*

#### Tahap 2.1: Persiapan Akun & Kredensial Midtrans
- [ ] Akses portal [Midtrans Merchant Dashboard](https://dashboard.sandbox.midtrans.com) mode **Sandbox**.
- [ ] Ambil kredensial API: `Server Key`, `Client Key`, dan `Merchant ID`.
- [ ] Pelajari dokumentasi [Midtrans Iris (Disbursement API)](https://iris-docs.midtrans.com/): pahami endpoint `/api/v1/beneficiaries`, `/api/v1/payouts`, dan `/api/v1/payouts/approve`.
- [ ] Tambahkan konfigurasi di `.env` dan `config/services.php`:
  * `MIDTRANS_SERVER_KEY`, `MIDTRANS_CLIENT_KEY`, `MIDTRANS_IS_PRODUCTION=false`
  * `MIDTRANS_IRIS_API_KEY`, `MIDTRANS_IRIS_MERCHANT_KEY`, `MIDTRANS_IRIS_BASE_URL`

#### Tahap 2.2: Modul Manajemen Rekening Bank Mitra (Provider Bank Settings)
- [ ] Buat form pengaturan profil mitra di frontend (`Profile/Partials/BankInformationForm.vue`):
  * Dropdown pilihan bank (BCA, Mandiri, BNI, BRI, Permata, GoPay, OVO, DANA).
  * Input nomor rekening / nomor HP e-wallet.
  * Input nama pemilik rekening.
- [ ] Buat Controller & Request Validation untuk menyimpan dan memverifikasi data rekening mitra ke tabel `users`.
- [ ] *(Opsional/Nilai Tambah)*: Integrasikan fitur validasi nomor rekening via API Iris `/api/v1/account_validation` untuk memastikan nama pemilik rekening sesuai sebelum disimpan.

#### Tahap 2.3: Pembaruan Alur Transaksi & Snap Token (Escrow Hold)
- [ ] Perbarui `BookingController::store` dan `BookingController::updateStatus`:
  * Hitung nilai kesepakatan harga jasa (`final_price`).
  * Hitung nominal biaya platform (`admin_fee`) misal Rp2.000 atau persentase komisi platform (misal 5%).
  * Hitung otomatis pendapatan bersih penyedia jasa:
    $$\text{provider\_earnings} = \text{final\_price} - \text{admin\_fee}$$
  * Simpan nilai `provider_earnings` dan atur `payout_status = 'pending'`.
- [ ] Buat Snap Token di `BookingController::getSnapToken` dengan rincian `item_details` yang transparan (Harga Jasa + Biaya Admin).
- [ ] Pastikan dana masuk ke rekening penampung FindServices (status pembayaran `paid`, status booking `confirmed`/`in_progress`, namun dana mitra masih berstatus *hold*).

#### Tahap 2.4: Integrasi Service Otomatisasi Pencairan (Automated Disbursement)
- [ ] Buat Service Class khusus: `app/Services/MidtransIrisService.php` untuk membungkus pemanggilan API Iris:
  * `createBeneficiary(...)`: Mendaftarkan rekening mitra sebagai penerima transfer.
  * `createPayout(...)`: Mengirimkan request transfer dana sebesar nominal `provider_earnings`.
  * `approvePayout(...)`: Menyetujui request pencairan dana (khusus alur Iris 2-step approval).
- [ ] Buat Event & Listener atau Queue Job: `app/Jobs/ProcessProviderDisbursement.php`.
- [ ] Hubungkan trigger: Ketika customer melakukan konfirmasi pekerjaan selesai di `BookingController::updateStatus` (status pesanan menjadi `completed`), sistem otomatis men-dispatch job `ProcessProviderDisbursement`.

#### Tahap 2.5: Keamanan Transaksi, Idempotency, & Webhook Callback
- [ ] Perbarui [`PaymentCallbackController.php`](file:///c:/laragon/www/FindServices/app/Http/Controllers/PaymentCallbackController.php):
  * Perketat validasi tanda tangan SHA-512 `signature_key`.
  * Tambahkan *idempotency lock* menggunakan `Cache::lock("payment_booking_{$booking->id}", 10)` agar request callback yang terkirim berulang dari Midtrans tidak memproses transaksi dua kali.
- [ ] Buat endpoint webhook baru untuk Midtrans Iris: `/api/midtrans/iris-callback` (dikecualikan dari CSRF di `bootstrap/app.php`).
- [ ] Tangani respon callback Iris: jika status payout `processed` / `settled`:
  * Ubah `payout_status` pada `bookings` menjadi `disbursed`.
  * Isi tanggal `disbursed_at` dengan waktu saat ini.
  * Simpan log lengkap ke tabel `payout_logs`.
  * Kirim notifikasi realtime via Laravel Reverb ke akun mitra: *"Dana sebesar Rp... telah berhasil dicairkan ke rekening Anda."*
- [ ] Tangani skenario gagal (*payout failed* / nomor rekening salah): ubah `payout_status = 'failed'` dan kirim notifikasi ke admin serta mitra untuk perbaikan data rekening.

#### Tahap 2.6: Pengujian Siklus Transaksi di Sandbox
- [ ] Uji siklus penuh: Pemesanan -> Bayar Snap -> Pelaksanaan Jasa -> Konfirmasi Selesai -> Otomatis Trigger Iris -> Payout Berhasil.
- [ ] Simulasikan kegagalan pembayaran dan kegagalan transfer untuk membuktikan ketahanan sistem (*error resilience*).

---

### FASE 3: INTEGRASI SISTEM & CROSS-TESTING BERSAMA
*(Dikerjakan bersama oleh Faidil & Isa pada Minggu 3 - 4)*

- [ ] **3.1 Penggabungan Kode (Git Merge)**
  - [ ] Merge branch `feature/algorithm-optimization` dan `feature/split-payment-midtrans` ke branch `development`/`main`.
  - [ ] Selesaikan konflik kode (*merge conflicts*) terutama pada rute dan model.
- [ ] **3.2 Pengujian Black-Box Terintegrasi (End-to-End User Flow)**
  - [ ] Skenario 1: Customer mencari jasa dengan keyword dan radius lokasi terdekat -> Booking diterima -> Pembayaran Snap lunas -> Jasa diselesaikan -> Dana otomatis masuk ke rekening mitra.
  - [ ] Skenario 2: Customer membatalkan pesanan sebelum pengerjaan -> Kebijakan pembatalan / penanganan dana *escrow*.
  - [ ] Skenario 3: Customer mencari jasa di luar radius jangkauan layanan mitra -> Sistem secara tepat menolak atau memberi tanda peringatan jarak.
- [ ] **3.3 Stress & Concurrency Testing**
  - [ ] Simulasikan klik ganda (*double click*) pada tombol konfirmasi selesai pesanan untuk memastikan tidak terjadi transfer dana ganda (*double disbursement*).
  - [ ] Simulasikan lonjakan pencarian serentak (*concurrent queries*) untuk melihat performa basis data setelah diindeks.

---

### FASE 4: PENYUSUNAN LAPORAN AKHIR & PERSIAPAN SIDANG
*(Dikerjakan bersama pada Minggu 4 - 5)*

- [ ] **4.1 Dokumentasi Hasil & Pembahasan (Bab IV)**
  - [ ] Faidil menyusun sub-bab: Analisis Algoritma Eksisting vs Baru, Tabel & Grafik Perbandingan Waktu Eksekusi Kueri (*Query Latency Benchmark*), serta Evaluasi Akurasi Perankingan.
  - [ ] Isa menyusun sub-bab: Arsitektur Alur Pembayaran *Split Payment*, Skema *Escrow-to-Disbursement*, Implementasi Webhook Keamanan SHA-512, serta Bukti Pengujian Siklus Transaksi pada Dashboard Midtrans.
- [ ] **4.2 Dokumentasi Kesimpulan & Saran (Bab V)**
  - [ ] Menjawab rumusan masalah secara lugas berdasarkan data kuantitatif pengujian.
- [ ] **4.3 Persiapan Demo Aplikasi & Presentasi Sidang**
  - [ ] Siapkan akun demo untuk 3 aktor: Customer, Provider Jasa, dan Admin.
  - [ ] Siapkan simulator Midtrans Sandbox & browser tab monitoring log database / Reverb.
  - [ ] Latihan presentasi pembagian peran dan tanya-jawab penguji.

---

## SARAN & CATATAN TEKNIS PENTING DARI SISTEM

> [!TIP]
> ### 1. Solusi Praktis Jika Akses Midtrans Iris API Belum Aktif di Sandbox
> Midtrans Snap sudah langsung aktif di Sandbox, namun Midtrans Iris terkadang membutuhkan persetujuan aktivasi fitur *Disbursement* dari tim Midtrans.
> **Solusi antisipasi (*Best Practice*):**
> Buat arsitektur kode menggunakan pola **Interface / Service Pattern**:
> ```
> App\Contracts\DisbursementGatewayInterface
>   ├── App\Services\MidtransIrisDisbursementService (Implementasi API asli)
>   └── App\Services\MockDisbursementService (Implementasi simulasi untuk testing lokal)
> ```
> Dengan cara ini, jika akun Iris Sandbox masih menunggu persetujuan, sistem tetap dapat diuji secara lokal menggunakan mode *Mock*, dan saat akun aktif tinggal mengubah satu baris konfigurasi di `.env`. Ini akan dinilai sangat profesional oleh dosen penguji!

> [!IMPORTANT]
> ### 2. Konfigurasi Minimum Token Size MySQL Full-Text Search
> Secara default, MySQL InnoDB memiliki parameter `ft_min_word_len = 3` atau `innodb_ft_min_token_size = 3`. Artinya, kata kunci yang panjangnya kurang dari 3 huruf (seperti "AC", "cat", "las") tidak akan terindeks secara default!
> **Solusi:**
> - Tambahkan kata kunci singkatan umum ke kolom `tags` (misal: "servis_ac", "pengecatan", "pengelasan"), ATAU
> - Atur konfigurasi MySQL `innodb_ft_min_token_size=2` jika Anda mengelola server sendiri di Laragon (`my.ini`).

> [!WARNING]
> ### 3. Mitigasi Race Condition pada Tombol Konfirmasi Selesai
> Ketika customer mengklik tombol *"Pesanan Selesai"*, ada jeda beberapa detik sebelum API Midtrans Iris merespons. Jika user menekan tombol berulang kali dengan cepat, transfer ganda bisa terjadi!
> **Solusi Wajib:**
> Gunakan Database Transaction dan Atomic Lock di Laravel:
> ```php
> Cache::lock("disburse_booking_{$booking->id}", 15)->block(5, function() use ($booking) {
>     if ($booking->payout_status === 'pending') {
>         $booking->update(['payout_status' => 'processing']);
>         ProcessProviderDisbursement::dispatch($booking);
>     }
> });
> ```

---

## PERTANYAAN UNTUK MEMASTIKAN DETAIL PROYEK

Sebelum memulai koding pada masing-masing fase, berikut beberapa hal yang bisa diputuskan bersama:

1. **Skema Pembagian Biaya Admin (*Split Model*):**
   * Apakah biaya admin platform dipotong dari harga jasa (misal: Harga Rp100.000 -> Mitra dapat Rp98.000, Platform Rp2.000), ATAU ditambahkan ke total tagihan customer (Customer bayar Rp102.000 -> Mitra dapat Rp100.000, Platform Rp2.000)?
2. **Ketersediaan Akses Akun Sandbox:**
   * Apakah Anda sudah memiliki akun Midtrans Developer/Sandbox yang siap digunakan?
3. **Target Wilayah Uji Geolokasi:**
   * Untuk pembuatan data seeder dummy 100-5.000 jasa, kota/area mana yang ingin dijadikan pusat titik koordinat (misalnya Kota Bandung, DKI Jakarta, atau area kampus Anda)?
