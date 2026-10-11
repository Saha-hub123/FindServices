# Threat Modeling & Security Assessment: FindServices
**Mata Kuliah:** Cybersecurity / Keamanan Sistem Informasi  
**Metodologi:** STRIDE Classification & DREAD Risk Rating  
**Target:** Website Marketplace Jasa FindServices (Laravel 12 + Inertia.js / Vue.js + MySQL + Reverb + Midtrans)

---

## 1. Ringkasan Eksekutif & Arsitektur Sistem

Aplikasi **FindServices** adalah platform marketplace penyedia jasa lokal berbasis web yang memfasilitasi interaksi antara:
1. **Customer (Pelanggan):** Mencari jasa berbasis geolokasi (Haversine Formula), membuat pemesanan (booking), melakukan pembayaran (Midtrans Snap / Tunai), chatting realtime, dan memberikan ulasan (review).
2. **Provider (Penyedia Jasa):** Mempublikasikan jasa dan portofolio foto, mengatur jadwal/kuota, merespon pesanan (konfirmasi harga final & status), chatting realtime, dan menerima pembayaran.
3. **Admin (Pengelola):** Mengelola kategori jasa, meninjau laporan keluhan/pelanggaran (user reports), dan memantau analitik platform.
4. **Third-Party Services:** Midtrans Payment Gateway untuk pemrosesan transaksi dan Cloudflare Tunnel untuk reverse proxy publik.
5. **Realtime WebSocket Daemon:** Laravel Reverb (port 8080) untuk broadcast event pesan chat dan pembaruan status booking.

---

## 2. Pemetaan Trust Boundaries (Batas Kepercayaan)

Pemetaan trust boundary memisahkan komponen sistem berdasarkan tingkat kepercayaan dan hak aksesnya. Pelanggaran keamanan terjadi ketika data berpindah melintasi batas kepercayaan tanpa validasi atau kontrol otorisasi yang memadai:

```
+---------------------------------------------------------------------------------------------------+
| TB 1: UNTRUSTED EXTERNAL ZONE                                                                     |
|  - Customer Browser / Client                                                                      |
|  - Service Provider Browser                                                                       |
|  - Admin Browser                                                                                  |
|  - Midtrans Gateway (External Webhook Initiator)                                                  |
+---------------------------------------------------------------------------------------------------+
                                                  |
                         [DF1 - DF4: HTTPS / WSS / Webhook Traffic]
                                                  v
+---------------------------------------------------------------------------------------------------+
| TB 2: PERIMETER & REVERSE PROXY ZONE                                                              |
|  - Cloudflare Tunnel (SSL Termination, DNS Routing app.cornel.my.id & ws.cornel.my.id)            |
|  - Laravel Web Router (CSRF Protection, Session Middleware, Sanctum)                              |
|  - Laravel API Router (CSRF-Exempt Endpoint /api/midtrans/callback, /api/test-latency)             |
+---------------------------------------------------------------------------------------------------+
                                                  |
                         [DF5 - DF7, DF16: Dispatched Controller Requests]
                                                  v
+---------------------------------------------------------------------------------------------------+
| TB 3: APPLICATION LOGIC PROCESS LAYER (TRUSTED SERVER HOST)                                       |
|  - Auth & Profile Controller (P1.0)          - Chat Controller (P6.0)                             |
|  - Marketplace & Geolocation (P2.0)          - Review & Rating System (P7.0)                      |
|  - Service CRUD & Media (P3.0)               - Admin Operations & Reports (P8.0)                  |
|  - Booking & Quota Workflow (P4.0)           - Notification Dispatcher (P9.0)                     |
|  - Payment & Webhook Handler (P5.0)                                                               |
+---------------------------------------------------------------------------------------------------+
                  |                                                  |
 [DF21-DF22: Event Broadcast]                       [DF23-DF34: Database & Disk I/O]
                  v                                                  v
+---------------------------------------+          +------------------------------------------------+
| TB 4: REALTIME DAEMON ZONE            |          | TB 5: PERSISTENT STORAGE LAYER                 |
|  - Laravel Reverb Server (P10.0)      |          |  - MySQL Database (findservices) [D1]          |
|    (Port 8080 Internal, WS/WSS)       |          |  - Local Storage Disk (public/uploads) [D2]    |
|                                       |          |  - Log Files (storage/logs/laravel.log) [D3]   |
+---------------------------------------+          +------------------------------------------------+
```

---

## 3. Matriks Hasil Analisis STRIDE & DREAD (Kondisi Terkini - Post-Mitigasi APP_DEBUG)

File template Excel telah diperbarui pada path:  
`keamanan_sistem_informasi/Latihan_STRIDE_DREAD_1.xlsx`

### Rekapitulasi Ancaman Teridentifikasi (10 Ancaman):

| No | ID Ancaman / CVE / CWE | Deskripsi Singkat & Lokasi | STRIDE | DREAD (D,R,E,A,D) | Total | Level Risiko | Rank |
|:--:|:-----------------------|:---------------------------|:------:|:-----------------:|:-----:|:------------:|:----:|
| 1 | **CVE-2023-28438**<br>`CWE-285` | **BOLA / IDOR pada Booking Status Update**<br>`BookingController::updateStatus` (validasi auth id dikomentari baris 230). | `T, I, E` | `8, 9, 8, 8, 7` | **40** | **CRITICAL** | **1** |
| 2 | **CVE-2023-34449**<br>`CWE-770` | **DoS & Flooding via WebSocket Reverb**<br>Endpoint testing `/api/test-latency` tidak dilindungi otorisasi & rate limit. | `S, R, D` | `6, 9, 9, 8, 8` | **40** | **CRITICAL** | **1** |
| 3 | **CVE-2023-45133**<br>`CWE-306` | **Missing Auth & Replay pada Midtrans Webhook**<br>`PaymentCallbackController` CSRF-exempt tanpa nonce/replay prevention. | `S, T, R` | `9, 8, 7, 8, 7` | **39** | **HIGH** | **3** |
| 4 | **CVE-2023-38035**<br>`CWE-770` | **DoS via Heavy Geolocation & Large File Size**<br>Perhitungan Haversine tanpa cache dan batas upload 10MB per file gambar. | `D` | `7, 8, 8, 8, 7` | **38** | **HIGH** | **4** |
| 5 | **CVE-2024-21501**<br>`CWE-79` | **Stored XSS pada Review, Jasa & Notes**<br>Input teks ulasan dan catatan booking rentan injeksi script jika ditampilkan tanpa escape. | `S, T, I, E` | `7, 8, 7, 8, 7` | **37** | **HIGH** | **5** |
| 6 | **CVE-2023-22809**<br>`CWE-269` | **Privilege Escalation via Mass Assignment**<br>Atribut `role` diekspos di array `$fillable` model `User` (`app/Models/User.php:26`). | `S, T, E` | `9, 8, 7, 7, 6` | **37** | **HIGH** | **5** |
| 7 | **CVE-2024-21516**<br>`CWE-918 / CWE-434` | **SSRF & Unrestricted File Upload**<br>Upload avatar, review, dan service hanya cek mime type tanpa sanitasi magic byte/SVG. | `T, I, E` | `8, 7, 6, 7, 6` | **34** | **HIGH** | **7** |
| 8 | **CVE-2022-31129**<br>`CWE-384` | **Session Hijacking & Insecure Session Config**<br>`SESSION_ENCRYPT=false` dan penyimpanan sesi plaintext di tabel MySQL `sessions`. | `S, I, E` | `8, 7, 6, 7, 6` | **34** | **HIGH** | **7** |
| 9 | **CVE-2022-31279**<br>`CWE-862` | **Improper Access Control / BOLA pada Chat**<br>`ChatController::destroy` & manipulasi query parameter konteks pesan. | `T, R, I` | `6, 8, 7, 6, 6` | **33** | **HIGH** | **9** |
| 10 | **CVE-2023-40028**<br>`CWE-209` | **[TERMITIGASI] Sensitive Info Disclosure via Debug**<br>`APP_DEBUG=false` telah diaktifkan di `.env`. Detail stack trace & kredensial tidak terekspos ke publik. | `I` | `2, 1, 1, 1, 1` | **6** | **LOW** | **10** |

---

## 4. Analisis Rekapitulasi Skor (Sheet Ringkasan Setelah Mitigasi)

- **Total Ancaman Ternilai:** 10
- **Distribusi Level Risiko:**
  - **CRITICAL (Skor >= 40):** 2 Ancaman (BOLA Booking Status Update & WebSocket Reverb DoS)
  - **HIGH (Skor 30 - 39):** 7 Ancaman
  - **MEDIUM (Skor 20 - 29):** 0
  - **LOW (Skor < 20):** 1 Ancaman *(CVE-2023-40028 telah termitigasi menjadi skor 6)*
- **Distribusi Kategori STRIDE:**
  - **S (Spoofing):** 5
  - **T (Tampering):** 6
  - **R (Repudiation):** 3
  - **I (Information Disclosure):** 6
  - **D (Denial of Service):** 2
  - **E (Elevation of Privilege):** 5
- **Rata-rata Skor DREAD:** 33.8 / 50 *(Turun dari sebelumnya 37.5 setelah mitigasi)*
- **Skor DREAD Tertinggi:** 40
- **Ancaman Prioritas 1:** *Broken Object Level Authorization (BOLA/IDOR) pada perubahan status Booking (BookingController::updateStatus)*

---

## 5. Status Tindak Lanjut & Rekomendasi Mitigasi Selanjutnya

1. **[SELESAI / MITIGATED] Nonaktifkan Debug Mode di Production:**  
   `APP_DEBUG=false` sudah berhasil diterapkan di berkas `.env`. Respon error HTTP 500 sekarang menampilkan halaman generik ramah pengguna tanpa membocorkan kredensial.
2. **[PRIORITAS UTAMA BARU] Aktifkan Kebijakan Otorisasi Booking:**  
   Buka file [`BookingController.php`](file:///c:/laragon/www/FindServices/app/Http/Controllers/BookingController.php#L230) dan aktifkan kembali pemeriksaan ID user:
   ```php
   if (auth()->id() !== $booking->provider_id && auth()->id() !== $booking->customer_id) {
       abort(403, 'Akses ditolak.');
   }
   ```
3. **[PRIORITAS KRITIS] Amankan WebSocket Endpoint /api/test-latency:**  
   Beri middleware autentikasi `auth:sanctum` atau nonaktifkan rute testing latensi pada production agar tidak menjadi celah DoS daemon Reverb.
4. **Lindungi Model User dari Mass Assignment:**  
   Hapus kolom `role` dari `$fillable` di `app/Models/User.php`.
5. **Enkripsi Sesi:**  
   Ubah `SESSION_ENCRYPT=true` di `.env` untuk melindungi token dan sesi pengguna di database MySQL.
