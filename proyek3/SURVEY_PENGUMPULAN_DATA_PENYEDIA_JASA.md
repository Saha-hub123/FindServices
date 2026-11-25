# INSTRUMEN KUESIONER GOOGLE FORM
## Pengumpulan Data Profil & Layanan Penyedia Jasa (*FindServices*)

Dokumen ini berisi panduan dan daftar pertanyaan kuesioner yang dirancang khusus untuk dimuat pada **Google Form**. Survei ini ditujukan kepada para calon mitra penyedia jasa (teknisi, tukang, tenaga kebersihan, profesional mandiri, UMKM jasa) guna mengumpulkan data riil lapangan yang akan dipetakan langsung ke basis data platform **FindServices** (entitas `users` dan `services`) serta mendukung pengujian **Optimalisasi Algoritma Pencarian Geospasial Multi-Kriteria** dan **Split Payment Midtrans**.

---

## PENGATURAN UMUM FORMULIR (GOOGLE FORM SETTINGS)

* **Judul Formulir:**  
  `Formulir Pendaftaran & Pendataan Mitra Penyedia Jasa — FindServices`
* **Deskripsi Formulir:**  
  *Halo Rekan Penyedia Jasa! Kami dari tim riset & pengembang platform **FindServices** (marketplace pencarian jasa lokal terdekat) sedang melakukan pendataan dan validasi profil penyedia jasa untuk membantu mempertemukan Anda dengan pelanggan di sekitar Anda secara cepat, transparan, dan aman.*  
  *Pengisian kuesioner ini memerlukan waktu sekitar **3–5 menit**. Data yang Anda berikan akan digunakan sebagai basis data profil layanan dan pengujian fitur penemuan jasa lokal. Terima kasih atas partisipasi dan kontribusi Anda!*
* **Pengaturan Formulir:**
  - Batasi ke 1 tanggapan: *Opsional (dapat dinonaktifkan jika 1 orang ingin mendaftarkan lebih dari 1 jenis jasa).*
  - Kumpulkan alamat email: *Aktifkan (Centang 'Terverifikasi' atau 'Masukan responden').*

---

## STRUKTUR KUESIONER GOOGLE FORM

---

### BAGIAN 1: INFORMASI IDENTITAS & PROFIL MITRA (ENTITAS `USER`)
> *Deskripsi Bagian: Bagian ini bertujuan untuk mencatat identitas profil profesional penyedia jasa yang akan ditampilkan kepada pelanggan.*

#### 1. Nama Lengkap / Nama Usaha Jasa
* **Tipe Soal:** Jawaban Singkat (*Short Answer*)
* **Petunjuk Pengisian:** Tuliskan nama lengkap Anda atau nama merek usaha jasa Anda (Contoh: *Budi Santoso* atau *Budi Cool Service AC*).
* **Wajib Diisi:** Ya
* **Mapping Database:** `users.name`

#### 2. Nomor WhatsApp / Kontak Aktif
* **Tipe Soal:** Jawaban Singkat (*Short Answer*)
* **Petunjuk Pengisian:** Masukkan nomor telepon aktif yang terhubung dengan WhatsApp (Contoh: *081234567890*).
* **Validasi Respon:** Angka (*Is numeric*)
* **Wajib Diisi:** Ya
* **Mapping Database:** `users.phone`

#### 3. Alamat Email Aktif
* **Tipe Soal:** Jawaban Singkat (*Short Answer*)
* **Petunjuk Pengisian:** Alamat email yang digunakan untuk notifikasi akun dan transaksi.
* **Validasi Respon:** Email
* **Wajib Diisi:** Ya
* **Mapping Database:** `users.email`

#### 4. Deskripsi Diri / Profil Singkat (*Bio*)
* **Tipe Soal:** Paragraf (*Paragraph*)
* **Petunjuk Pengisian:** Ceritakan secara singkat pengalaman kerja Anda, latar belakang keahlian, atau keunggulan layanan Anda (Contoh: *Teknisi pendingin ruangan bersertifikat dengan pengalaman lebih dari 7 tahun menangani servis AC rumah tangga dan perkantoran. Selalu mengutamakan ketepatan waktu dan kebersihan kerja.*).
* **Wajib Diisi:** Ya
* **Mapping Database:** `users.bio`

#### 5. Alamat Pangkalan / Lokasi Operasional Jasa
* **Tipe Soal:** Paragraf (*Paragraph*)
* **Petunjuk Pengisian:** Tuliskan alamat lengkap tempat tinggal, pangkalan, atau workshop/bengkel Anda (Nama jalan, nomor rumah/ruko, RT/RW, Kelurahan, Kecamatan, Kota/Kabupaten).
* **Wajib Diisi:** Ya
* **Mapping Database:** `users.address` / `services.location`

#### 6. Tautan (*Link*) Google Maps / Titik Koordinat Pangkalan
* **Tipe Soal:** Jawaban Singkat (*Short Answer*)
* **Petunjuk Pengisian:** Buka aplikasi Google Maps, tandai pangkalan/lokasi Anda, lalu salin tautan bagikan lokasinya (*Share Link*), atau tuliskan angka Lintang & Bujur jika mengetahui (Contoh: *https://maps.app.goo.gl/...* atau *-6.9175, 107.6191*).
* **Keterangan untuk Admin:** Tautan ini akan dikonversi menjadi angka `latitude` dan `longitude` presisi oleh tim teknis.
* **Wajib Diisi:** Ya
* **Mapping Database:** `services.latitude`, `services.longitude`

#### 7. Hari & Jam Kerja Operasional (*Working Hours*)
* **Tipe Soal:** Kotak Centang (*Checkboxes*) & Jawaban Singkat
* **Petunjuk:** 
  - **Hari Buka Operasional (Pilih semua yang sesuai):**
    - [ ] Senin – Jumat
    - [ ] Sabtu
    - [ ] Minggu / Hari Libur Tetap Buka
    - [ ] Buka Setiap Hari (7 Hari Penuh)
  - **Jam Operasional Harian:** (Isian singkat, misal: *08.00 - 17.00 WIB* atau *Siap Panggilan 24 Jam*)
* **Wajib Diisi:** Ya
* **Mapping Database:** `users.working_hours` (disimpan dalam format JSON / teks terstruktur)

---

### BAGIAN 2: SPESIFIKASI LAYANAN DAN JASA (ENTITAS `SERVICES`)
> *Deskripsi Bagian: Bagian ini mengumpulkan rincian teknis jasa yang Anda tawarkan, estimasi biaya, kata kunci keahlian, serta durasi pengerjaan.*

#### 8. Kategori Layanan Jasa
* **Tipe Soal:** Pilihan Ganda (*Multiple Choice*) / Dropdown
* **Petunjuk Pengisian:** Pilih bidang kategori yang paling sesuai dengan layanan utama Anda.
* **Pilihan Jawaban:**
  1. Service AC & Elektronik
  2. Pertukangan & Renovasi
  3. Kebersihan & Cleaning Service
  4. Otomotif & Bengkel Kendaraan
  5. Kecantikan & Perawatan Diri
  6. Pijat & Terapi Kesehatan
  7. Desain & Industri Kreatif
  8. IT, Komputer & Jaringan
  9. Pendidikan & Les Privat
  10. Fotografi & Videografi
  11. Angkutan Barang & Pindahan
  12. Lain-lain (Sebutkan: _________)
* **Wajib Diisi:** Ya
* **Mapping Database:** `services.category_id`

#### 9. Judul / Nama Layanan Jasa
* **Tipe Soal:** Jawaban Singkat (*Short Answer*)
* **Petunjuk Pengisian:** Berikan judul jasa yang jelas dan mudah dicari pelanggan (Contoh: *Jasa Cuci AC & Tambah Freon Cepat*, *Tukang Cat & Renovasi Plafon*, *Service Panggilan Pompa Air*).
* **Wajib Diisi:** Ya
* **Mapping Database:** `services.title`

#### 10. Deskripsi Lengkap Layanan Jasa
* **Tipe Soal:** Paragraf (*Paragraph*)
* **Petunjuk Pengisian:** Jelaskan secara rinci apa saja yang dikerjakan dalam layanan ini, ketentuan pemesanan, apakah alat dan bahan sudah disiapkan oleh penyedia, serta jaminan garansi kerja bila ada.
* **Wajib Diisi:** Ya
* **Mapping Database:** `services.description`

#### 11. Kata Kunci Spesialisasi / Tag Keahlian (*Tags / Skills*)
* **Tipe Soal:** Jawaban Singkat (*Short Answer*)
* **Petunjuk Pengisian:** Tuliskan 3–8 kata kunci keahlian spesifik yang sering dicari pelanggan terkait jasa Anda, pisahkan dengan tanda koma (Contoh untuk Teknisi AC: *cuci ac, tambah freon, ac bocor, ac tidak dingin, inverter, pasang ac baru, bongkar pasang*).
* **Alasan Ilmiah:** Variabel ini sangat penting untuk pengujian efektivitas algoritma **Full-Text Search (FTS)** dan *relevance scoring*.
* **Wajib Diisi:** Ya
* **Mapping Database:** `services.tags` (disimpan dalam format JSON/Array)

#### 12. Estimasi Tarif Minimum (Biaya Terendah)
* **Tipe Soal:** Jawaban Singkat (*Short Answer*)
* **Petunjuk Pengisian:** Masukkan perkiraan biaya paling rendah untuk pekerjaan paling ringan / biaya pemeriksaan awal (Hanya angka dalam Rupiah, contoh: *75000* untuk Rp 75.000).
* **Validasi Respon:** Angka (*Is numeric, >= 0*)
* **Wajib Diisi:** Ya
* **Mapping Database:** `services.price_min`

#### 13. Estimasi Tarif Maksimum (Biaya Tertinggi / Rata-rata Penuh)
* **Tipe Soal:** Jawaban Singkat (*Short Answer*)
* **Petunjuk Pengisian:** Masukkan estimasi biaya tertinggi untuk pekerjaan menyeluruh (Hanya angka dalam Rupiah, contoh: *350000* untuk Rp 350.000).
* **Validasi Respon:** Angka (*Is numeric, >= price_min*)
* **Wajib Diisi:** Ya
* **Mapping Database:** `services.price_max`

#### 14. Skema / Satuan Penagihan Biaya (*Price Unit*)
* **Tipe Soal:** Pilihan Ganda (*Multiple Choice*)
* **Petunjuk Pengisian:** Bagaimana cara Anda biasanya menentukan harga jasa?
* **Pilihan Jawaban:**
  - [ ] Per Kunjungan / Per Panggilan (Tarif dasar datang ke lokasi)
  - [ ] Per Unit / Per Perangkat (Misal: hitungan per 1 unit AC, per 1 unit mesin)
  - [ ] Per Jam (Tarif dihitung berdasarkan durasi waktu kerja)
  - [ ] Per Hari / Harian
  - [ ] Borongan / Kesepakatan di Lokasi (Setelah melihat kondisi kerusakan)
* **Wajib Diisi:** Ya
* **Mapping Database:** `services.price_unit`

#### 15. Estimasi Durasi Pengerjaan Jasa (*Estimated Duration*)
* **Tipe Soal:** Pilihan Ganda (*Multiple Choice*) / Dropdown
* **Petunjuk Pengisian:** Berapa rata-rata waktu yang dibutuhkan untuk menyelesaikan 1 kali sesi pekerjaan normal?
* **Pilihan Jawaban:**
  - [ ] Kurang dari 1 Jam
  - [ ] 1 – 2 Jam
  - [ ] 3 – 5 Jam
  - [ ] 1 Hari Penuh (6 – 8 Jam)
  - [ ] Lebih dari 1 Hari (Sistem pengerjaan bertahap)
* **Wajib Diisi:** Ya
* **Mapping Database:** `services.estimated_duration`

#### 16. Radius Maksimal Jangkauan Panggilan Layanan (*Coverage Radius*)
* **Tipe Soal:** Pilihan Ganda (*Multiple Choice*)
* **Petunjuk Pengisian:** Seberapa jauh jarak dari pangkalan Anda yang bersedia Anda layani untuk datang ke rumah pelanggan?
* **Alasan Ilmiah:** Variabel ini menjadi acuan batas kotak koordinat pada algoritma **Bounding Box Pre-Filtering** sebelum perhitungan **Haversine Formula**.
* **Pilihan Jawaban:**
  - [ ] Hingga 5 km (Sekitar lingkungan kelurahan/kecamatan terdekat)
  - [ ] Hingga 10 km (Antar-kecamatan dalam satu kota)
  - [ ] Hingga 15 km (Cakupan luas dalam kota)
  - [ ] Hingga 25 km (Termasuk area perbatasan / pinggiran kota)
  - [ ] Lebih dari 25 km (Wilayah regional)
* **Wajib Diisi:** Ya
* **Mapping Database:** `services.coverage_radius_km`

---

### BAGIAN 3: RIWAYAT PEKERJAAN & REPUTASI (VALIDASI ALGORITMA)
> *Deskripsi Bagian: Data pada bagian ini digunakan untuk memodelkan algoritma perankingan popularitas dan normalisasi ulasan Bayes (Bayesian Weighted Rating).*

#### 17. Perkiraan Jumlah Pekerjaan/Pesanan yang Telah Diselesaikan
* **Tipe Soal:** Pilihan Ganda (*Multiple Choice*)
* **Petunjuk Pengisian:** Selama menjalankan usaha jasa ini, berapa total pesanan atau pelanggan yang pernah Anda layani hingga saat ini?
* **Pilihan Jawaban:**
  - [ ] Pemula / Baru Memulai (< 5 pesanan)
  - [ ] 5 – 25 pesanan
  - [ ] 26 – 50 pesanan
  - [ ] 51 – 100 pesanan
  - [ ] Lebih dari 100 pesanan (Sangat Berpengalaman)
* **Wajib Diisi:** Ya
* **Mapping Database:** `services.total_completed_orders` (diambil nilai median/representatif untuk inisialisasi basis data)

#### 18. Rata-rata Tingkat Kepuasan Pelanggan Selama Ini
* **Tipe Soal:** Skala Linier (*Linear Scale*) 1 s/d 5
* **Petunjuk Pengisian:** Berdasarkan pengalaman Anda dan penilaian pelanggan selama ini, seberapa puas pelanggan terhadap hasil kerja Anda?
  - `1`: Kurang Memuaskan / Sering Dikomplain
  - `3`: Cukup Puas
  - `5`: Sangat Puas / Hampir Tidak Pernah Ada Komplain
* **Wajib Diisi:** Ya
* **Mapping Database:** `services.rating_avg`

#### 19. Bukti Foto / Portofolio Hasil Kerja (Opsional)
* **Tipe Soal:** Unggah Berkas (*File Upload*) — Gambar (JPG, PNG) / Tautan Google Drive
* **Petunjuk Pengisian:** Unggah 1–3 foto contoh pengerjaan jasa, kartu nama, atau seragam/bengkel kerja Anda jika tersedia.
* **Wajib Diisi:** Tidak (Opsional)
* **Mapping Database:** `galleries` (sebagai foto galeri jasa)

---

### BAGIAN 4: KESIAPAN METODE PENCAIRAN DANA (SPLIT PAYMENT)
> *Deskripsi Bagian: Bagian ini bersifat opsional/tambahan untuk mendukung kebutuhan pengujian modul pencairan otomatis (Midtrans Iris).*

#### 20. Rekening Bank atau E-Wallet Utama untuk Menerima Pembayaran
* **Tipe Soal:** Pilihan Ganda & Isian Singkat
* **Nama Bank / E-Wallet:**
  - [ ] BCA
  - [ ] Bank Mandiri
  - [ ] BRI
  - [ ] BNI
  - [ ] GoPay / OVO / DANA
  - [ ] Lainnya: _______
* **Nomor Rekening / No. HP E-Wallet:** (Jawaban Singkat)
* **Nama Pemilik Rekening:** (Harus sesuai dengan buku tabungan)
* **Wajib Diisi:** Opsional (Bisa diisi dummy/simulasi jika responden ragu memberikan data asli)
* **Mapping Database:** `users.bank_name`, `users.bank_account_number`, `users.bank_account_holder`

---

## MATRIKS PEMETAAN: GOOGLE FORM KE BASIS DATA MYSQL

Tabel berikut menunjukkan bagaimana setiap nomor pertanyaan di Google Form langsung terhubung ke kolom pada basis data `FindServices`:

| No. Pertanyaan Form | Label di Formulir | Tabel Target | Kolom Database | Tipe Data SQL | Catatan Implementasi |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **Q1** | Nama Lengkap / Usaha | `users` | `name` | `VARCHAR(255)` | Digunakan untuk display profil |
| **Q2** | No. WhatsApp | `users` | `phone` | `VARCHAR(20)` | Validasi komunikasi pemesanan |
| **Q3** | Email Aktif | `users` | `email` | `VARCHAR(255)` | Autentikasi & notifikasi |
| **Q4** | Bio / Profil Pengalaman | `users` | `bio` | `TEXT` | Halaman detail provider |
| **Q5** | Alamat Operasional | `users` / `services` | `address` / `location` | `TEXT` | Alamat fisik pangkalan |
| **Q6** | Koordinat Maps | `services` | `latitude`, `longitude` | `DECIMAL(10,8), (11,8)` | **Kunci Bounding Box & Haversine** |
| **Q7** | Jam Kerja Operasional | `users` | `working_hours` | `VARCHAR(100)` / `JSON` | Validasi ketersediaan jadwal |
| **Q8** | Kategori Jasa | `services` | `category_id` | `BIGINT (FK)` | Relasi ke tabel `categories` |
| **Q9** | Judul Jasa | `services` | `title` | `VARCHAR(255)` | **Indeks Full-Text Search (FTS)** |
| **Q10** | Deskripsi Lengkap | `services` | `description` | `TEXT` | **Indeks Full-Text Search (FTS)** |
| **Q11** | Tags / Skills | `services` | `tags` | `JSON` / `TEXT` | **Kunci Relevance Matching** |
| **Q12** | Tarif Minimum | `services` | `price_min` | `DECIMAL(12,2)` | Filter harga & perankingan |
| **Q13** | Tarif Maksimum | `services` | `price_max` | `DECIMAL(12,2)` | Filter harga batas atas |
| **Q14** | Skema / Satuan Tarif | `services` | `price_unit` | `ENUM` / `VARCHAR` | Transparansi biaya |
| **Q15** | Estimasi Durasi Kerja | `services` | `estimated_duration` | `VARCHAR(50)` | Informasi estimasi pengerjaan |
| **Q16** | Radius Layanan | `services` | `coverage_radius_km` | `INT` | **Parameter Delta Bounding Box** |
| **Q17** | Total Pesanan Selesai | `services` | `total_completed_orders` | `INT` | **Parameter Bobot Bayes ($v$)** |
| **Q18** | Rata-rata Kepuasan | `services` | `rating_avg` | `DECIMAL(3,2)` | **Parameter Rating Bayes ($R_s$)** |
| **Q19** | Foto Portofolio | `galleries` | `image_path` | `VARCHAR(255)` | Galeri visual kartu jasa |
| **Q20** | Data Rekening Payout | `users` | `bank_name`, `bank_account_...` | `VARCHAR` | Kebutuhan Midtrans Iris API |

---

## SARAN & REKOMENDASI UNTUK DISTRIBUSI KUESIONER

1. **Target Responden Nyata:**
   - Bagikan kuesioner ke grup komunitas UMKM lokal, grup Facebook teknisi lokal (contoh: *Komunitas Teknisi AC Bandung / Servis Elektronik*), paguyuban pertukangan, atau teman/kenalan mahasiswa yang memiliki usaha sampingan jasa.
   - Targetkan setidaknya **15–30 responden riil** agar Anda memiliki dataset lokal yang bervariasi untuk dimasukkan ke database seeder (*seeding data*).

2. **Kerahasiaan Rekening (Data Finansial):**
   - Pada bagian rekening bank (Bagian 4), beri keterangan jelas bahwa data tersebut **hanya untuk pengujian sistem simulasi pembayaran (Sandbox)** dan responden boleh mengisi dengan nomor dummy/rekening simulasi jika merasa kurang nyaman membagikan data asli.

3. **Kemudahan Konversi Data:**
   - Setelah kuesioner disebar dan mendapatkan responden, Google Form dapat langsung di-*export* ke format **Google Sheets / CSV**.
   - Dari CSV tersebut, Anda bisa membuat skrip seeder Laravel otomatis (`php artisan db:seed`) untuk langsung memasukkan semua data survei ke tabel `users` dan `services`.

