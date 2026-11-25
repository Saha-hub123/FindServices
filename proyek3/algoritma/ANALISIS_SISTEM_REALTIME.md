# Analisis Sistem Realtime — FindServices (Laravel Reverb)

> **Dibuat:** 2026-11-26 | **Cakupan:** Semua fitur yang menggunakan WebSocket (Reverb/Echo) dan polling
> **File terkait:** `app/Events/`, `routes/channels.php`, `resources/js/Layouts/AuthenticatedLayout.vue`, `resources/js/Pages/Chats/Index.vue`, `resources/js/Pages/Bookings/Show.vue`, `resources/js/Pages/Bookings/Index.vue`

---

## 1. Peta Fitur Realtime Eksisting

| Fitur | Mekanisme | Event / Channel | Jenis Channel | Status |
|---|---|---|---|---|
| **Chat — Kirim Pesan** | WebSocket (Echo) | `MessageSent` → `chat.{userId}` | `PrivateChannel` | ✅ Tepat |
| **Chat — Pesan Dibaca** | WebSocket (Echo) | `MessageRead` → `chat.{senderId}` | `PrivateChannel` | ✅ Tepat |
| **Chat — Hapus Pesan** | WebSocket (Echo) | `MessageDeleted` → `chat.{receiverId}` | `PrivateChannel` | ✅ Tepat |
| **Chat — Status Online** | WebSocket (Echo) | `online` Presence Channel | `PresenceChannel` | ✅ Tepat |
| **Booking — Update Status** | WebSocket (Echo) | `BookingStatusUpdated` → `booking.{hashId}` | `PrivateChannel` | ✅ Tepat (ada isu minor) |
| **Booking — Review Masuk** | WebSocket (Echo) | `ReviewSubmitted` → `booking.{bookingId}` | `PrivateChannel` | ✅ Tepat (ada isu minor) |
| **Notifikasi Navbar** | **Polling 10 detik** + Echo `.notification()` | `auth` props reload | HTTP polling | ⚠️ **Duplikat!** |
| **Badge Chat Navbar** | Watcher `page.props.unread_global_count` | Inertia shared props | HTTP sync | ⚠️ Hanya update saat navigasi |
| **TestLatency** | WebSocket (Echo) | `test-channel` | `Channel` (public!) | ⚠️ **Channel publik tanpa auth!** |

---

## 2. Apakah Laravel Reverb Cocok untuk Masing-masing Fitur?

### ✅ 2.1 Chat (MessageSent, MessageRead, MessageDeleted) — SANGAT COCOK

**Reverb sangat tepat di sini.** Chat adalah use case paling klasik untuk WebSocket karena:
- Membutuhkan latensi rendah (< 100ms)
- Bersifat **bidirectional** dan event-driven
- Data harus sampai ke satu penerima spesifik (PrivateChannel cocok)

**Implementasi sudah benar:** `PrivateChannel('chat.{userId}')` dengan auth di `channels.php`:
```php
Broadcast::channel('chat.{user}', function ($currentUser, User $user) {
    return (int) $currentUser->id === (int) $user->id;
});
```

**Isu yang perlu diperbaiki:**
- Di `store()`: setelah broadcast, server melakukan `redirect()->back()` → ini memaksa full HTTP round-trip. Idealnya endpoint chat store mengembalikan JSON (`response()->json()`) agar frontend tidak perlu reload.
- N+1 query di sidebar (sudah dicatat di audit sebelumnya).

---

### ✅ 2.2 Booking Status & Review (BookingStatusUpdated, ReviewSubmitted) — COCOK

Reverb tepat karena update status booking adalah event satu arah (server → client) yang harus segera muncul tanpa user perlu refresh manual.

**Isu yang ditemukan:**

1. **`BookingStatusUpdated` di `Bookings/Index.vue` membuka terlalu banyak channel sekaligus**
   ```javascript
   // Eksisting: Loop semua booking, subscribe satu channel per booking
   all.forEach(booking => {
       window.Echo.private(`booking.${booking.hash_id}`)
           .listen('BookingStatusUpdated', ...)
   });
   ```
   Jika user punya 50 booking, akan ada **50 WebSocket subscription aktif** sekaligus.
   
   **Solusi yang lebih efisien:** Gunakan satu `PrivateChannel` milik user untuk menerima semua update booking:
   ```javascript
   // Lebih efisien: Satu channel per user, bukan per booking
   window.Echo.private(`user.${props.auth_id}.bookings`)
       .listen('BookingStatusUpdated', (e) => {
           router.reload({ only: ['myBookings', 'incomingOrders', 'history'] });
       });
   ```
   Ini membutuhkan perubahan di `BookingStatusUpdated.php`:
   ```php
   // Broadcast ke channel user, bukan channel booking
   return [
       new PrivateChannel('user.' . $this->booking->customer_id . '.bookings'),
       new PrivateChannel('user.' . $this->booking->provider_id . '.bookings'),
   ];
   ```

2. **`ReviewSubmitted` menggunakan `booking_id` integer** (bukan `hash_id`)
   ```php
   // ReviewSubmitted.php — Channel pakai integer ID biasa
   new PrivateChannel('booking.' . $this->review->booking_id)
   ```
   Tapi `channels.php` mendefinisikan:
   ```php
   Broadcast::channel('booking.{booking}', ...) // expects hash_id!
   ```
   → **Mismatch!** Auth channel akan selalu gagal karena format ID berbeda. Perlu konsistensi: pakai `hash_id` di semua tempat.

3. **Handler di `Bookings/Show.vue` melakukan `router.reload()` setiap kali ada event** — ini efektif tapi boros. Idealnya update langsung state lokal dari payload event tanpa reload, kecuali data sangat kompleks.

---

### ⚠️ 2.3 Notifikasi Navbar — DUPLIKAT & KONFLIK

Ini masalah **terbesar** dalam sistem realtime saat ini.

**Yang terjadi sekarang:**
```javascript
// AuthenticatedLayout.vue — DUA mekanisme berjalan bersamaan:

// Mekanisme 1: HTTP Polling setiap 10 detik (selalu aktif)
pollingInterval = setInterval(() => {
    router.reload({ only: ['auth'], ... });
}, 10000);

// Mekanisme 2: Laravel Echo WebSocket (juga aktif)
window.Echo.private(`chat.${user.value.id}`)
    .listen('MessageSent', ...)
    .notification((notification) => { ... });
```

**Masalahnya:**
- Polling 10 detik tetap berjalan meskipun Echo sudah memberikan update realtime
- Setiap 10 detik, 1 HTTP request ke server hanya untuk cek notifikasi
- Jika ada 100 user aktif → **600 request/menit** hanya dari polling notifikasi
- Echo `.notification()` sudah bisa menangani notifikasi `DatabaseNotification` secara realtime — **polling tidak diperlukan sama sekali**

**Solusi:**
```javascript
// Hapus polling sepenuhnya, andalkan Echo saja
onMounted(() => {
    if (window.Echo && user.value) {
        window.Echo.private(`App.Models.User.${user.value.id}`)
            .notification((notification) => {
                // Tambahkan notif baru ke list secara lokal
                notifications.value.unshift(notification);
                unreadNotifCount.value++;
            });

        window.Echo.private(`chat.${user.value.id}`)
            .listen('MessageSent', (e) => {
                unreadMsgCount.value++;
                // ... play sound
            });
    }
});
```

> **Catatan:** `.notification()` di Echo menggunakan channel `App.Models.User.{id}` — pastikan Reverb mengizinkan channel ini.

---

### ⚠️ 2.4 Badge Chat Navbar — TIDAK ADA REALTIME SEJATI

Saat ini badge "pesan belum dibaca" di navbar hanya update ketika:
1. User berpindah halaman (Inertia navigation → `HandleInertiaRequests` menghitung ulang)
2. Polling 10 detik reload `auth` props

Tidak ada update realtime murni. Jika seseorang mengirim pesan, badge tidak akan naik sampai 10 detik berikutnya atau user klik sesuatu.

**Solusi:** Badge langsung diupdate via Echo listener yang sudah ada di `AuthenticatedLayout.vue`:
```javascript
// Sudah ada! Tinggal pastikan logikanya benar:
.listen('MessageSent', (e) => {
    unreadMsgCount.value++; // ← Ini sudah benar
    // ... play sound
})
```
Masalahnya, counter ini hanya increment, **tidak pernah di-sync ulang** dengan data DB setelah user membuka chat. Perlu tambahkan listener `MessageRead` di layout:
```javascript
.listen('MessageRead', (e) => {
    // Jika saya yang membaca (reader adalah saya)
    if (e.reader_id === user.value.id) {
        unreadMsgCount.value = 0; // Reset setelah buka chat
    }
})
```

---

### ❌ 2.5 TestLatency — BAHAYA: Channel Publik Tanpa Auth

```php
// TestLatency.php
return [
    new Channel('test-channel'), // ← Public channel, siapapun bisa subscribe!
];
```

Channel `test-channel` adalah **public channel** (bukan `PrivateChannel`). Siapapun yang tahu nama channel ini bisa subscribe dan menerima data test tersebut, termasuk payload booking/review yang dikirim untuk tes.

**Solusi:** Hapus atau jadikan private, dan pastikan tidak dipakai di production:
```php
// Opsi 1: Hapus file ini setelah testing selesai
// Opsi 2: Jadikan private dan hanya untuk admin
return [new PrivateChannel('admin.test')];
```

---

## 3. Apakah Sistem Realtime Menggunakan Algoritma? Perlu Dioptimalisasi?

**Ya — ada 3 aspek algoritma dalam sistem realtime ini:**

### 3.1 Algoritma Authorization Channel (Ada di `channels.php`)

```php
// Ini adalah algoritma access control / kebijakan otorisasi:
Broadcast::channel('booking.{booking}', function ($user, Booking $booking) {
    return (int) $user->id === (int) $booking->customer_id || 
           (int) $user->id === (int) $booking->provider_id;
});
```

Setiap kali client subscribe ke channel, Laravel Reverb memanggil callback ini. Jika banyak user menyubscribe secara bersamaan (mis. saat deploy/restart), ini bisa menjadi bottleneck.

**Potensi optimalisasi:** Tambahkan caching hasil authorization agar tidak hit DB setiap handshake:
```php
Broadcast::channel('booking.{booking}', function ($user, Booking $booking) {
    $cacheKey = "auth:booking:{$booking->id}:user:{$user->id}";
    return cache()->remember($cacheKey, 60, function () use ($user, $booking) {
        return (int) $user->id === (int) $booking->customer_id || 
               (int) $user->id === (int) $booking->provider_id;
    });
});
```

### 3.2 Algoritma Pengiriman Event (`ShouldBroadcastNow` vs `ShouldBroadcast`)

Semua event menggunakan `ShouldBroadcastNow`, artinya broadcast dilakukan **synchronous** di dalam request yang sama (tidak melalui queue).

```
Request masuk → Controller → Broadcast event → Reverb → Client
                              ↑ SYNCHRONOUS — Request tidak selesai sampai broadcast selesai
```

**Trade-off:**
- ✅ Latensi lebih rendah (tidak ada queue delay)
- ❌ Request time lebih lama jika Reverb lambat merespons
- ❌ Jika Reverb down → request API/form juga gagal

**Rekomendasi untuk production:**
- Chat: tetap pakai `ShouldBroadcastNow` (latensi adalah prioritas)
- BookingStatusUpdated: bisa pakai `ShouldBroadcast` (via queue) karena bukan chat interaktif
- Notifications: pakai `ShouldBroadcast` via queue

```php
// Hirarki yang disarankan:
class MessageSent implements ShouldBroadcastNow { } // Chat: langsung
class BookingStatusUpdated implements ShouldBroadcast { } // Booking: via queue
```

### 3.3 Algoritma Fan-Out (Siapa yang Menerima Event)

Saat `BookingStatusUpdated` broadcast:
- Reverb perlu mencari semua client yang subscribe ke `booking.{hashId}`
- Ini adalah operasi **fan-out**: satu event → banyak penerima potensial

Reverb menggunakan Redis (atau internal storage) sebagai message broker. Pastikan Redis dipakai (bukan database driver) untuk performa fan-out:

```env
# .env — Pastikan pakai Redis, bukan database:
BROADCAST_CONNECTION=reverb
CACHE_STORE=redis
SESSION_DRIVER=redis
QUEUE_CONNECTION=redis  # Jika pakai ShouldBroadcast (async)
```

---

## 4. Rekomendasi Prioritas

| # | Masalah | Severity | Aksi |
|---|---|---|---|
| 1 | Polling 10 detik tetap aktif meski Echo berjalan | 🔴 Tinggi | Hapus `setInterval` polling, andalkan Echo `.notification()` |
| 2 | `ReviewSubmitted` channel pakai integer bukan `hash_id` | 🔴 Tinggi | Konsistenkan dengan `hash_id` atau ubah channel ke format baru |
| 3 | `TestLatency` menggunakan public channel | 🟠 Tinggi | Hapus atau jadikan private, jangan ada di production |
| 4 | 50+ subscription channel per user di halaman daftar booking | 🟠 Tinggi | Refactor ke satu channel `user.{id}.bookings` |
| 5 | Badge chat tidak sync setelah buka percakapan | 🟡 Sedang | Tambah listener `MessageRead` di `AuthenticatedLayout` |
| 6 | Semua event pakai `ShouldBroadcastNow` (sync) | 🟡 Sedang | Pindahkan `BookingStatusUpdated` & notifikasi ke async queue |
| 7 | `HandleInertiaRequests` menghitung `unread_global_count` di setiap request | 🟡 Sedang | Cache nilai ini per-user, invalidate saat ada `MessageSent` / `MessageRead` |
| 8 | Channel authorization tidak di-cache | 🟢 Rendah | Tambah `cache()->remember()` di `channels.php` |
| 9 | `store()` di ChatController redirect (bukan JSON) | 🟢 Rendah | Kembalikan JSON agar frontend tidak perlu full round-trip |

---

## 5. Arsitektur Realtime yang Disarankan

```
┌─────────────────────────────────────────────────────────────┐
│                    FINDSERVICES REALTIME                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FITUR CHAT (Latensi Kritis)                               │
│  ─────────────────────────                                 │
│  MessageSent  → ShouldBroadcastNow → PrivateChannel        │
│  MessageRead  → ShouldBroadcastNow → PrivateChannel        │
│  MessageDeleted → ShouldBroadcastNow → PrivateChannel      │
│  Online Status → PresenceChannel 'online'                  │
│                                                             │
│  FITUR BOOKING (Latensi Toleran)                           │
│  ─────────────────────────────                             │
│  BookingStatusUpdated → ShouldBroadcast (Queue)            │
│                       → PrivateChannel 'user.{id}.bookings'│
│  ReviewSubmitted      → ShouldBroadcast (Queue)            │
│                       → PrivateChannel 'booking.{hash_id}' │
│                                                             │
│  NOTIFIKASI SISTEM                                         │
│  ─────────────────                                         │
│  DatabaseNotification → Echo .notification()               │
│                       → PrivateChannel App.Models.User.{id}│
│  ❌ Hapus HTTP Polling 10 detik                            │
│                                                             │
│  TESTING (Development Only)                                │
│  ─────────────────────────                                 │
│  TestLatency → PrivateChannel 'admin.test' (atau hapus)    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Relevansi ke Variabel Penelitian Proyek 3

Sistem realtime sendiri **bukan variabel independen** dalam penelitian ini (yang fokus pada optimalisasi algoritma pencarian/ranking), tapi berdampak pada:

| Variabel / Aspek | Dampak Realtime |
|---|---|
| **Performa Sistem (Y)** | Polling 10 detik menambah beban server ~600 req/menit per 100 user aktif — mempengaruhi response time keseluruhan |
| **Waktu Respons Penyedia (X5)** | Jika notifikasi booking baru sampai lebih cepat (realtime vs polling), provider bisa respons lebih cepat → data X5 lebih akurat |
| **Keandalan Data** | Bug `ReviewSubmitted` channel mismatch → update realtime gagal → user tidak tahu ada review baru |

> **Kesimpulan:** Reverb adalah pilihan **tepat dan sudah benar** untuk semua fitur chat dan booking di FindServices. Masalahnya bukan pada pilihan teknologi, tapi pada **implementasi detail** — terutama duplikasi polling vs WebSocket dan manajemen subscription channel yang belum efisien.

---

*File ini adalah bagian dari dokumentasi audit Proyek 3 — Optimalisasi Algoritma FindServices*  
*Terakhir diperbarui: 2026-11-26*
