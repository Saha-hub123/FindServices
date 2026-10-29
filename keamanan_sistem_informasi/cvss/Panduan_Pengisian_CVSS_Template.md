# PANDUAN PENGISIAN MANUAL TEMPLATE LATIHAN CVSS v4.0
## Proyek: Aplikasi FindServices (Mata Kuliah Keamanan Sistem Informasi)
**Berkas Sasaran Pengisian:** `keamanan_sistem_informasi/cvss/TemplateLatihan_CVSS_1.xlsx` (Sheet: `CVSS_Template`)  
**Sumber Perbandingan DREAD:** `keamanan_sistem_informasi/1. template_baru_Praktikum_STRIDE-DREAD.xlsx` (Sheet: `STRIDE_DREAD_Template`)

---

### A. Petunjuk & Ketentuan Pengerjaan
1. **Pengisian Manual:** Berkas `TemplateLatihan_CVSS_1.xlsx` **tidak diubah otomatis** oleh skrip. Anda dapat menyalin data dari panduan ini ke dalam Excel secara manual.
2. **Jumlah Kerentanan (9 Baris):** Dari 10 ancaman sebelumnya, kerentanan **T-10 telah dimitigasi** (`APP_DEBUG=false`), sehingga dihilangkan dan tidak dihitung. Hanya ada **9 kerentanan aktif** (`T-01` sampai `T-09`).
3. **Tanpa CVE:** ID kerentanan cukup ditulis `T-01` hingga `T-09` tanpa embel-embel kode CVE.
4. **Warna Sel pada Excel:**
   - 🟨 **Sel Kuning / Font Biru (Input Manual):** Kolom B, C, D, E, F, G, H, I, J, K, L, M, N, P, S, dan V.
   - ⬜ **Sel Abu-abu (Rumus Otomatis - JANGAN DIUBAH):** Kolom O (Vector String), Kolom Q (Severity), Kolom R (Prioritas), Kolom T (Level DREAD), dan Kolom U (Sejalan dengan DREAD?).

---

### B. Tabel Matriks Lengkap Pengisian Sheet `CVSS_Template` (Baris 5 s.d. 13)

Gunakan tabel di bawah ini sebagai rujukan saat mengisi baris 5 hingga 13 pada sheet **`CVSS_Template`**:

| No (A) | ID (B) | Deskripsi (C) | AV (D) | AC (E) | AT (F) | PR (G) | UI (H) | VC (I) | VI (J) | VA (K) | SC (L) | SI (M) | SA (N) | Vector String (O - Auto) | Skor Base (P) | Severity (Q - Auto) | Prioritas (R - Auto) | Skor DREAD (S) | Level DREAD (T - Auto) | Sejalan? (U - Auto) | Catatan / Alasan Pemetaan Metrik (V) |
|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **1** | **T-01** | Penyerang yang terautentikasi memanipulasi parameter order_id pada endpoint status booking di BookingController tanpa verifikasi kepemilikan akun, sehingga dapat mengubah status pesanan milik pengguna lain secara sepihak. | **N** | **L** | **N** | **L** | **N** | **L** | **H** | **N** | **N** | **N** | **N** | `CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N` | **7.1** | HIGH | 5 | **40** | CRITICAL | Berbeda | Penyerang login biasa (PR:L) memodifikasi status pesanan pengguna lain (VI:H, VC:L). Berbeda dengan DREAD (40 Critical) karena CVSS memperhitungkan pembatasan akses akun sah yang memperkecil populasi penyerang. |
| **2** | **T-02** | Penyerang tanpa autentikasi mengirimkan ribuan request ke endpoint uji latensi WebSocket Reverb secara masif, sehingga membanjiri channel Reverb dan mengakibatkan server socket mengalami kehabisan memori serta lumpuh. | **N** | **L** | **N** | **N** | **N** | **N** | **N** | **H** | **N** | **N** | **N** | `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N` | **8.7** | HIGH | 2 | **40** | CRITICAL | Berbeda | Serangan jarak jauh tanpa kredensial (AV:N/PR:N) melumpuhkan ketersediaan socket (VA:H). Berbeda dengan DREAD (40 Critical) karena DoS murni tanpa kebocoran data di CVSS v4 berplafon High 8.7. |
| **3** | **T-03** | Penyerang memalsukan notifikasi callback webhook Midtrans dengan mengeksploitasi kemungkinan kunci rahasia kosong pada berkas konfigurasi, sehingga status pembayaran booking berubah menjadi lunas tanpa transfer uang sesungguhnya. | **N** | **L** | **P** | **N** | **N** | **N** | **H** | **N** | **N** | **N** | **N** | `CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N` | **8.2** | HIGH | 3 | **39** | HIGH | Sama | Penyerang publik (AV:N/PR:N) memanipulasi status pembayaran transaksi (VI:H) dengan prasyarat kunci server kosong (AT:P). Sejalan dengan DREAD (39 High). |
| **4** | **T-04** | Pengguna jahat memicu pencarian katalog dengan koordinat radius geolokasi secara berulang dan mengunggah banyak berkas berukuran 10MB, sehingga membebani CPU database dan menghabiskan ruang penyimpanan server. | **N** | **L** | **N** | **L** | **N** | **N** | **N** | **L** | **N** | **N** | **N** | `CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N` | **5.3** | MEDIUM | 6 | **38** | HIGH | Berbeda | Pengguna login (PR:L) memicu degradasi ketersediaan dan beban disk/CPU parsial (VA:L). Berbeda dengan DREAD karena CVSS membedakan degradasi parsial secara ketat sebagai Medium. |
| **5** | **T-05** | Pengguna menyisipkan skrip berbahaya berupa payload JavaScript pada kolom ulasan review atau catatan pemesanan jasa, sehingga skrip dieksekusi di browser penyedia jasa atau administrator saat membuka halaman. | **N** | **L** | **N** | **L** | **P** | **L** | **L** | **N** | **N** | **N** | **N** | `CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N` | **5.1** | MEDIUM | 8 | **37** | HIGH | Berbeda | Stored XSS memerlukan login (PR:L) dan interaksi pasif korban (UI:P) berdampak terbatas di sisi klien (VC:L/VI:L). Berbeda dengan DREAD karena CVSS mengukur keparahan teknis spesifik tanpa pembobotan discoverability. |
| **6** | **T-06** | Pengguna mendaftar atau memperbarui profil lalu menambahkan parameter role=admin melalui manipulasi HTTP request payload, sehingga hak akses akun meningkat menjadi administrator karena atribut role masuk ke fillable model. | **N** | **L** | **N** | **N** | **N** | **H** | **H** | **H** | **N** | **N** | **N** | `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N` | **9.3** | CRITICAL | 1 | **37** | HIGH | Berbeda | Eskalasi hak akses penuh ke Admin tanpa autentikasi saat registrasi (PR:N) merusak seluruh pilar CIA (VC:H/VI:H/VA:H). Berbeda dengan DREAD karena CVSS menilai kompromi sistem total sebagai Critical, sedangkan DREAD teredam skor Discoverability. |
| **7** | **T-07** | Pengguna mengunggah berkas gambar manipulasi (seperti polyglot file atau SVG berbisa) pada fitur foto jasa dan avatar profil, sehingga berkas berbahaya tersimpan di direktori publik server dan dapat memicu SSRF atau XSS. | **N** | **L** | **N** | **L** | **P** | **L** | **L** | **N** | **N** | **N** | **N** | `CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N` | **5.1** | MEDIUM | 8 | **34** | HIGH | Berbeda | Unggah gambar SVG manipulatif butuh akun (PR:L) dan interaksi korban (UI:P) berdampak XSS/SSRF terbatas di klien (VC:L/VI:L). Berbeda dengan DREAD karena web server tidak mengeksekusi PHP di folder storage. |
| **8** | **T-08** | Pihak ketiga pada jaringan lokal atau perantara sniffing mencuri session ID pengguna karena konfigurasi sesi di database tidak dienkripsi, sehingga penyerang dapat membajak sesi login pengguna tanpa memerlukan password. | **A** | **L** | **P** | **N** | **P** | **H** | **H** | **N** | **N** | **N** | **N** | `CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N` | **7.4** | HIGH | 4 | **34** | HIGH | Sama | Sniffing sesi di jaringan lokal (AV:A) dengan prasyarat posisi MitM (AT:P) dan interaksi pasif korban (UI:P) mengambil alih akun korban (VC:H/VI:H). Sejalan dengan DREAD (34 High). |
| **9** | **T-09** | Pengguna yang terautentikasi memanipulasi parameter hash_id pada URL percakapan atau request penghapusan pesan, sehingga dapat membaca pesan rahasia atau menghapus riwayat chat milik pihak lain tanpa izin. | **N** | **L** | **N** | **L** | **N** | **L** | **L** | **N** | **N** | **N** | **N** | `CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N` | **5.3** | MEDIUM | 6 | **33** | HIGH | Berbeda | IDOR pada chat membutuhkan akun terdaftar (PR:L) dengan dampak kerahasiaan dan integritas terbatas pada pesan yang disasar (VC:L/VI:L). Berbeda dengan DREAD karena dampaknya terisolasi pada chat individual. |

---

### C. Rincian Teknis & Alasan Perbandingan DREAD vs CVSS per Kerentanan

#### 1. T-01: Broken Object Level Authorization (BOLA/IDOR) pada Status Booking
- **Konteks Kode:** `BookingController.php` baris 228–232 (pengecekan otorisasi `auth()->id()` dikomentari).
- **Nilai Metrik CVSS v4.0:** `AV:N / AC:L / AT:N / PR:L / UI:N / VC:L / VI:H / VA:N / SC:N / SI:N / SA:N`
- **Vector String:** `CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N`
- **Skor Base CVSS:** **7.1 (HIGH)** | **Skor DREAD:** **40 (CRITICAL)**
- **Status:** **Berbeda**
- **Analisis Mendalam:**  
  Dalam DREAD Latihan 3.1, ancaman ini memperoleh skor 40 (Critical) karena sifat penjumlahan aditif dari Reproducibility (9), Exploitability (8), dan Affected Users (8) yang tinggi. Namun pada CVSS v4.0, terdapat metrik **Privileges Required (PR: Low)** karena penyerang wajib memiliki akun sah untuk mengakses endpoint booking. Dalam algoritma Macro-Vector CVSS v4.0, kebutuhan otentikasi membatasi populasi penyerang potensial sehingga menurunkan skor keparahan ke **7.1 (High)**.

---

#### 2. T-02: Denial of Service (DoS) pada Endpoint Uji Latensi Reverb WebSocket
- **Konteks Kode:** `routes/api.php` baris 15–52 (route `POST /api/test-latency` tanpa middleware auth dan tanpa throttling).
- **Nilai Metrik CVSS v4.0:** `AV:N / AC:L / AT:N / PR:N / UI:N / VC:N / VI:N / VA:H / SC:N / SI:N / SA:N`
- **Vector String:** `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N`
- **Skor Base CVSS:** **8.7 (HIGH)** | **Skor DREAD:** **40 (CRITICAL)**
- **Status:** **Berbeda**
- **Analisis Mendalam:**  
  Pada DREAD, ketiadaan autentikasi dan kemudahan flooding menghasilkan skor 40 (Critical). Pada CVSS v4.0, serangan DoS murni hanya berdampak pada ketersediaan sistem rentan (`VA:H`), sementara kerahasiaan (`VC:N`) dan integritas data (`VI:N`) tetap terjaga sempurna. Dalam matriks kalibrasi pakar CVSS v4.0, kerentanan tanpa kompromi data memiliki batas maksimal pada level **8.7 (High)**.

---

#### 3. T-03: Pemalsuan Webhook Callback Midtrans (Empty Server Key)
- **Konteks Kode:** `PaymentCallbackController.php` baris 14–38 dan `bootstrap/app.php` baris 21–23 (route webhook tanpa CSRF, server key rentan kosong di `.env`).
- **Nilai Metrik CVSS v4.0:** `AV:N / AC:L / AT:P / PR:N / UI:N / VC:N / VI:H / VA:N / SC:N / SI:N / SA:N`
- **Vector String:** `CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N`
- **Skor Base CVSS:** **8.2 (HIGH)** | **Skor DREAD:** **39 (HIGH)**
- **Status:** **Sama (Sejalan)**
- **Analisis Mendalam:**  
  Kedua metode penilaian menyimpulkan tingkat keparahan yang sama (**HIGH**). Manipulasi status pembayaran menjadi lunas secara sepihak merupakan ancaman integritas fatal (`VI:H` / Damage: 9). Di sisi lain, serangan ini memerlukan kondisi prasyarat spesifik (`AT:P` pada CVSS dan Discoverability: 7 pada DREAD), yaitu file konfigurasi `.env` membiarkan kunci server kosong.

---

#### 4. T-04: DoS melalui Konsumsi CPU Geolokasi & Penyalahgunaan Upload 10MB
- **Konteks Kode:** `MarketplaceController.php` baris 57–68 (rumus Haversine tanpa indexing spasial) dan upload 10MB.
- **Nilai Metrik CVSS v4.0:** `AV:N / AC:L / AT:N / PR:L / UI:N / VC:N / VI:N / VA:L / SC:N / SI:N / SA:N`
- **Vector String:** `CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N`
- **Skor Base CVSS:** **5.3 (MEDIUM)** | **Skor DREAD:** **38 (HIGH)**
- **Status:** **Berbeda**
- **Analisis Mendalam:**  
  DREAD menghasilkan level HIGH (38) karena penilai mengkhawatirkan dampak kelambatan pada banyak pengguna (Affected Users: 8). Namun CVSS v4.0 membedakan antara kelumpuhan total (`VA:H`) dan penurunan performa/kapasitas penyimpanan sebagian (`VA:L`). Karena fitur upload mensyaratkan akun (`PR:L`) dan sistem tidak mengalami *hard crash*, CVSS secara objektif menilainya sebagai **5.3 (Medium)**.

---

#### 5. T-05: Stored Cross-Site Scripting (XSS) pada Ulasan & Catatan Booking
- **Konteks Kode:** `BookingController.php` baris 470–502 (kolom ulasan hanya divalidasi string tanpa pembersihan tag HTML).
- **Nilai Metrik CVSS v4.0:** `AV:N / AC:L / AT:N / PR:L / UI:P / VC:L / VI:L / VA:N / SC:N / SI:N / SA:N`
- **Vector String:** `CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N`
- **Skor Base CVSS:** **5.1 (MEDIUM)** | **Skor DREAD:** **37 (HIGH)**
- **Status:** **Berbeda**
- **Analisis Mendalam:**  
  DREAD menetapkan HIGH (37) akibat potensi penyebaran ke pengunjung ulasan. Pada CVSS v4.0, XSS tersimpan pada form ulasan membutuhkan akun pengguna (`PR:L`), memerlukan korban membuka halaman ulasan (`UI:P`), dan dampaknya terbatas pada konteks sesi klien (`VC:L/VI:L`). Oleh karena itu, CVSS v4.0 memeringkatnya sebagai **5.1 (Medium)**.

---

#### 6. T-06: Privilege Escalation via Mass Assignment pada Model User (`role=admin`)
- **Konteks Kode:** `app/Models/User.php` baris 26 (atribut `'role'` tercantum di `$fillable`).
- **Nilai Metrik CVSS v4.0:** `AV:N / AC:L / AT:N / PR:N / UI:N / VC:H / VI:H / VA:H / SC:N / SI:N/ SA:N`
- **Vector String:** `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N`
- **Skor Base CVSS:** **9.3 (CRITICAL)** | **Skor DREAD:** **37 (HIGH)**
- **Status:** **Berbeda**
- **Analisis Mendalam:**  
  Ini adalah perbedaan paling signifikan. Pada DREAD, skor tertahan pada level HIGH (37) karena penilai memberi skor moderat pada Discoverability (6) dan Exploitability (7). Namun pada CVSS v4.0, penyerang yang mendaftar langsung sebagai Administrator tanpa autentikasi awal (`PR:N`) mendapatkan kendali penuh atas seluruh aspek Kerahasiaan, Integritas, dan Ketersediaan sistem (`VC:H/VI:H/VA:H`), sehingga CVSS menilainya secara tepat sebagai kerentanan paling berbahaya: **9.3 (Critical, Prioritas 1)**.

---

#### 7. T-07: Insecure File Upload (Polyglot / Malicious SVG)
- **Konteks Kode:** `ServiceController.php` baris 63–64 dan `UserReportController.php` baris 36 (validasi ekstensi tanpa verifikasi magic bytes).
- **Nilai Metrik CVSS v4.0:** `AV:N / AC:L / AT:N / PR:L / UI:P / VC:L / VI:L / VA:N / SC:N / SI:N / SA:N`
- **Vector String:** `CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N`
- **Skor Base CVSS:** **5.1 (MEDIUM)** | **Skor DREAD:** **34 (HIGH)**
- **Status:** **Berbeda**
- **Analisis Mendalam:**  
  DREAD memberi skor HIGH (34) karena asumsi Damage (8) pada server. Namun secara teknis, Laravel menyimpan berkas pada direktori publik tanpa mengeksekusi PHP di dalamnya, sehingga ancaman berkas SVG hanya tereksekusi di browser korban yang melihat gambar (`UI:P`) dengan dampak lokal klien (`VC:L/VI:L`), menghasilkan skor **5.1 (Medium)** di CVSS v4.0.

---

#### 8. T-08: Penyimpanan Sesi Tanpa Enkripsi (Session Sniffing)
- **Konteks Kode:** `.env` baris 34–36 (`SESSION_DRIVER=database` dan `SESSION_ENCRYPT=false`).
- **Nilai Metrik CVSS v4.0:** `AV:A / AC:L / AT:P / PR:N / UI:P / VC:H / VI:H / VA:N / SC:N / SI:N / SA:N`
- **Vector String:** `CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N`
- **Skor Base CVSS:** **7.4 (HIGH)** | **Skor DREAD:** **34 (HIGH)**
- **Status:** **Sama (Sejalan)**
- **Analisis Mendalam:**  
  Keduanya sepakat pada level **HIGH**. Dampak pembajakan sesi bernilai fatal (`VC:H/VI:H` / Damage: 8) karena akun korban diambil alih secara penuh. Namun eksploitasinya dibatasi oleh keharusan berada pada jaringan lokal/segmen WiFi yang sama (`AV:A`) dengan prasyarat posisi sniffing (`AT:P`).

---

#### 9. T-09: IDOR pada Percakapan Chat via Hashids
- **Konteks Kode:** `ChatController.php` baris 59–97 dan baris 240–253 (validasi kepemilikan mengandalkan decode hash tanpa Policy terpusat).
- **Nilai Metrik CVSS v4.0:** `AV:N / AC:L / AT:N / PR:L / UI:N / VC:L / VI:L / VA:N / SC:N / SI:N / SA:N`
- **Vector String:** `CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N`
- **Skor Base CVSS:** **5.3 (MEDIUM)** | **Skor DREAD:** **33 (HIGH)**
- **Status:** **Berbeda**
- **Analisis Mendalam:**  
  DREAD menilainya HIGH (33) karena kemudahan manipulasi ID (Reproducibility: 8). CVSS v4.0 secara lebih proporsional melihat bahwa eksploitasi IDOR ini memerlukan akun login (`PR:L`) dan dampaknya terisolasi hanya pada ruang obrolan individu yang disasar (`VC:L/VI:L`), bukan kebocoran basis data global, sehingga terklasifikasi sebagai **5.3 (Medium)**.

---

### D. Ekspektasi Hasil pada Sheet `Ringkasan`

Setelah Anda menginputkan data di atas ke sheet `CVSS_Template`, tabel pada sheet **`Ringkasan`** akan otomatis menampilkan nilai-nilai berikut:

```
┌────────────────────────────────────────────────────────────────────────┐
│ RINGKASAN HASIL CVSS v4.0 — APLIKASI FINDSERVICES                     │
├────────────────────────────────────────┬───────────────────────────────┤
│ Severity CVSS                          │ Jumlah Kerentanan             │
├────────────────────────────────────────┼───────────────────────────────┤
│ CRITICAL                               │ 1                             │
│ HIGH                                   │ 4                             │
│ MEDIUM                                 │ 4                             │
│ LOW                                    │ 0                             │
│ NONE                                   │ 0                             │
├────────────────────────────────────────┼───────────────────────────────┤
│ Total Ternilai                         │ 9                             │
├────────────────────────────────────────┴───────────────────────────────┤
│ PERBANDINGAN DENGAN DREAD                                              │
├────────────────────────────────────────┬───────────────────────────────┤
│ Sama (Sejalan)                         │ 2                             │
│ Berbeda                                │ 7                             │
├────────────────────────────────────────┴───────────────────────────────┤
│ INDIKATOR STATISTIK                                                    │
├────────────────────────────────────────┬───────────────────────────────┤
│ Rata-rata Skor Base CVSS               │ 6.83                          │
│ Skor Base Tertinggi                    │ 9.3                           │
│ Kerentanan Prioritas 1                 │ T-06                          │
└────────────────────────────────────────┴───────────────────────────────┘
```

---

### E. Langkah Praktis Pengisian ke Excel
1. Buka berkas `keamanan_sistem_informasi/cvss/TemplateLatihan_CVSS_1.xlsx`.
2. Klik tab sheet **`CVSS_Template`**.
3. Pada baris **5 sampai 13**:
   - Salin isi kolom **B** (ID) dan **C** (Deskripsi).
   - Pada kolom **D sampai N**, klik tanda panah dropdown di masing-masing sel lalu pilih huruf sesuai tabel di atas (`N`, `L`, `H`, `P`).
   - Periksa kolom **O (Vector String)**: rumus otomatis akan membentuk vector string.
   - Ketikkan angka pada kolom **P (Skor Base)** (misal `7.1`, `8.7`, `8.2`, dst).
   - Kolom **Q (Severity)** dan **R (Prioritas)** akan terhitung otomatis.
   - Ketikkan angka pada kolom **S (Skor DREAD)** (misal `40`, `40`, `39`, dst).
   - Kolom **T (Level DREAD)** dan **U (Sejalan?)** akan terisi otomatis.
   - Salin penjelasan singkat ke kolom **V (Catatan / Alasan)**.
4. Klik tab sheet **`Ringkasan`** untuk melihat rekapitulasi grafik dan tabel statistik otomatis.
5. Simpan (*Save*) berkas Excel Anda.
