# Referensi Jurnal & Pemetaan Implementasi Optimalisasi Sistem Realtime — FindServices

> **Dibuat:** 2026-11-26 | **Topik:** Optimalisasi Sistem Realtime (Laravel Reverb / WebSocket / Pub-Sub / Queue)  
> **Dokumen Terkait:** [ANALISIS_SISTEM_REALTIME.md](./ANALISIS_SISTEM_REALTIME.md) | [AUDIT_ALGORITMA_DAN_OPTIMALISASI.md](./AUDIT_ALGORITMA_DAN_OPTIMALISASI.md)

---

Berikut adalah **3 jurnal ilmiah** (beserta link DOI terverifikasi) yang menjadi dasar teori dan acuan implementasi untuk mengoptimalkan algoritma pada sistem realtime Laravel Reverb di FindServices:

---

## 1. Optimasi Arsitektur Publish–Subscribe (Channel Routing & Multiplexing)

* **Judul:** *A Platform-Agnostic Publish–Subscribe Architecture with Dynamic Optimization*
* **Penulis:** Ahmed Twabi, Yepeng Ding, & Tohru Kondo (2025)
* **Jurnal:** *Future Internet* (MDPI), Vol. 17, Issue 9, Hal. 426
* **Link DOI:** https://doi.org/10.3390/fi17090426
* **Relevansi Algoritma:** Membahas pemisahan (*decoupling*) logika aplikasi dengan mekanisme *publish-subscribe* serta optimasi perutean topik/channel untuk menekan latensi transmisi dan beban *fan-out* pada sistem realtime.

### Bagian Implementasi di Kode FindServices

1. **Channel Multiplexing (Mengurangi jumlah koneksi/subscription per user):**
   * `app/Events/BookingStatusUpdated.php` (baris 31–38): Mengubah target broadcast dari per-booking (`booking.{hash_id}`) menjadi channel terpusat milik user (`user.{customer_id}.bookings` dan `user.{provider_id}.bookings`).
   * `resources/js/Pages/Bookings/Index.vue` (baris 98–108): Menghapus loop `all.forEach(...)` yang membuka puluhan WebSocket subscription sekaligus, dan menggantinya dengan 1 listener `window.Echo.private('user.${auth_id}.bookings')`.
   * `routes/channels.php` (baris 14–19): Menambahkan aturan otorisasi untuk channel `user.{user}.bookings`.
2. **Konsistensi Routing ID Channel:**
   * `app/Events/ReviewSubmitted.php` (baris 25–32): Memperbaiki *channel mismatch* dengan menggunakan `hash_id` (`booking.{hash_id}`) agar cocok dengan definisi route binding di `routes/channels.php` (baris 14).

---

## 2. Optimasi Asynchronous Message Queue & In-Memory Broker (Redis)

* **Judul:** *Benchmarking Message Queues*
* **Penulis:** Rokin Maharjan, Md Showkat Hossain Chy, Muhammad Ashfakur Arju, & Tomas Cerny (2023)
* **Jurnal:** *Telecom* (MDPI), Vol. 4, Issue 2, Hal. 298–312
* **Link DOI:** https://doi.org/10.3390/telecom4020018
* **Relevansi Algoritma:** Mengevaluasi kinerja *message queue* (termasuk Redis, RabbitMQ, dan Kafka) terkait *trade-off* antara latensi, *throughput*, dan manajemen antrean asinkron. Jurnal ini menegaskan keunggulan Redis sebagai *in-memory broker* berlatensi sangat rendah untuk distribusi pesan dan *state* sementara.

### Bagian Implementasi di Kode FindServices

1. **Asynchronous Dispatch (`ShouldBroadcast` vs `ShouldBroadcastNow`):**
   * `app/Events/BookingStatusUpdated.php` (baris 14) dan `app/Events/ReviewSubmitted.php` (baris 14): Mengubah interface dari `ShouldBroadcastNow` (synchronous, memblokir HTTP request) menjadi `ShouldBroadcast` (asynchronous via queue worker), sementara fitur chat (`app/Events/MessageSent.php`, baris 15) tetap memakai `ShouldBroadcastNow` demi latensi instan.
2. **Migrasi Broker & Caching Otorisasi ke Redis:**
   * `.env` (baris 1–16): Mengganti `QUEUE_CONNECTION=database` menjadi `redis` agar antrean broadcast dan *fan-out* tidak membebani database MySQL utama.
   * `routes/channels.php` (baris 14–19): Membungkus query pengecekan `Booking` di `Broadcast::channel` dengan `cache()->remember(...)` agar handshake WebSocket tidak mengulang query DB terus-menerus.
   * `app/Http/Middleware/HandleInertiaRequests.php` (baris 86–90): Meng-cache nilai `unread_global_count` di Redis per user dan melakukan invalidasi saat event `MessageSent` atau `MessageRead` terjadi.

---

## 3. Eliminasi HTTP Polling Menuju Full-Duplex WebSocket

* **Judul:** *Design and Development of a Real-Time Delivery Tracking App Using WebSocket and Haversine*
* **Penulis:** Bima Arya Kurniawan, Retno Mumpuni, & Muhammad Muharrom Al Haromainy (2025)
* **Jurnal:** *bit-Tech*, Vol. 8, No. 2, Hal. 2482–2494
* **Link DOI:** https://doi.org/10.32877/bt.v8i2.3275
* **Relevansi Algoritma:** Membuktikan bahwa mekanisme *polling* HTTP konvensional menimbulkan jeda waktu (*delay*) dan pemborosan *bandwidth*/CPU akibat siklus request-response berulang, sedangkan arsitektur *push* full-duplex WebSocket memangkas overhead jaringan dan mempercepat sinkronisasi data.

### Bagian Implementasi di Kode FindServices

* `resources/js/Layouts/AuthenticatedLayout.vue` (baris 30–91):
  1. **Menghapus blok `setInterval(..., 10000)`** (HTTP polling setiap 10 detik yang melakukan `router.reload({ only: ['auth'] })`).
  2. **Mengandalkan penuh listener Laravel Echo** pada channel `App.Models.User.{id}` (`.notification()`) untuk pembaruan notifikasi navbar secara langsung.
  3. **Menambahkan listener `MessageRead`** pada channel `chat.{user.id}` di layout agar badge `unreadMsgCount` langsung tersinkronisasi (reset ke `0`) tanpa menunggu reload halaman atau polling.

---

## Ringkasan Pemetaan

| Jurnal (DOI) | Fokus Algoritma / Optimasi | File Target di FindServices |
|---|---|---|
| Twabi et al., 2025 ([10.3390/fi17090426](https://doi.org/10.3390/fi17090426)) | Pub/Sub Channel Multiplexing & Topic Routing | `BookingStatusUpdated.php`, `ReviewSubmitted.php`, `Bookings/Index.vue`, `routes/channels.php` |
| Maharjan et al., 2023 ([10.3390/telecom4020018](https://doi.org/10.3390/telecom4020018)) | Async Message Queue & Redis In-Memory Broker | `BookingStatusUpdated.php`, `ReviewSubmitted.php`, `.env`, `routes/channels.php`, `HandleInertiaRequests.php` |
| Kurniawan et al., 2025 ([10.32877/bt.v8i2.3275](https://doi.org/10.32877/bt.v8i2.3275)) | Full-Duplex WebSocket vs HTTP Polling | `resources/js/Layouts/AuthenticatedLayout.vue` |

---

*File ini adalah bagian dari dokumentasi Proyek 3 — Optimalisasi Algoritma FindServices*  
*Terakhir diperbarui: 2026-11-26*
