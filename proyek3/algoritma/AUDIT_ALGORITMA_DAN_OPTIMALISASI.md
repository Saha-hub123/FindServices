# Audit Algoritma & Rekomendasi Optimalisasi — FindServices Proyek 3

> **Dibuat:** 2026-11-25 | **Sumber:** Audit menyeluruh kode FindServices vs jurnal ilmiah di folder `Proyek 3/Jurnal/`  
> **Cakupan:** `app/Http/Controllers/`, `resources/js/Pages/`, `resources/js/Components/`, semua Model, Migrasi, dan dokumen `proyek3/`

---

## 1. Evaluasi Folder `Proyek 3` (Kajian Jurnal & Justifikasi Algoritma)

Tiga pilar algoritma yang diusulkan dalam `KAJIAN_JURNAL_DAN_ANALISIS_VARIABEL_DATA.md` dan `Variabel.md`:

| Pilar | Jurnal Rujukan (dari folder) | Penilaian Kesesuaian | Catatan Kritis Teknis |
|---|---|---|---|
| **Full-Text Search (FTS)** | Jurnal tentang IR / NLP berbasis MySQL FULLTEXT | ✅ Relevan — MySQL FULLTEXT `IN NATURAL LANGUAGE MODE` sudah diimplementasi di `SearchController` | ❌ Celah: kata < 3 karakter (mis. "AC", "TV", "HP") dibuang MySQL FTS secara default (`ft_min_word_len=3`). Perlu **Boolean Mode** + fallback `LIKE` untuk kasus ini |
| **Haversine + Bounding Box** | Jurnal geospasial / location-aware service | ✅ Relevan — formula Haversine ada di `MarketplaceController` & `SearchController` | ⚠️ Belum ada **composite index** `(status, latitude, longitude)`. Tanpa itu, bounding-box filter tetap full-scan. Rujukan: Jovanović 2015 — bounding box harus jadi *pre-filter*, bukan post-filter |
| **Multi-Criteria Weighted Ranking** | Jurnal MCDM / scoring gabungan rating + jarak + popularitas | ✅ Relevan — formula skor sudah ada di `MarketplaceController` | ❌ Bayesian prior `C` (mean global) dihitung dari **semua** jasa termasuk yang belum punya ulasan (`rating_avg = 0`), sehingga `C` terdistorsi ke bawah. Harus filter `where('review_count', '>', 0)` |

### 1.1 Algoritma yang Belum Tercakup di Jurnal Namun Ada di Kode

| Komponen | Status di Kode | Saran |
|---|---|---|
| **State Machine Booking** | Ada (manual if-else di `BookingController`) | Perlu dijadikan topik tersendiri — transisi status belum divalidasi secara formal |
| **Kuota Harian Penyedia** | Ada, tapi inkonsisten | Perlu diaudit dan diseragamkan |
| **Real-Time Notification (WebSocket)** | Ada (Laravel Echo + Reverb) | Dapat menjadi poin optimalisasi latensi vs polling |
| **Rekomendasi Konten (Dashboard)** | Ada (`topProviders`, `trendingServices`) | Pakai `inRandomOrder()` — belum berbasis algoritma apapun |

---

## 2. Hasil Analisis `app/Http/Controllers` & `resources/js`

### A. `DashboardController.php` & `Dashboard.vue`

**Bug / Gap yang Ditemukan:**

1. **`topProviders` pakai `inRandomOrder()`**
   ```php
   // EKSISTING (tidak deterministik):
   User::where('role', 'provider')->inRandomOrder()->take(6)->get();
   ```
   Tidak ada kriteria ranking apapun. Setiap request menghasilkan urutan berbeda.

2. **Filter "Paling Laris" menghitung semua status booking**
   ```php
   // EKSISTING (menghitung booking cancelled juga):
   withCount('bookings')
   ```
   Seharusnya hanya `bookings` dengan status `completed` yang dihitung sebagai "laris".

3. **Filter "Rating Tinggi" tidak pakai Bayesian**
   ```php
   // EKSISTING (hanya sort by rating_avg mentah):
   orderBy('rating_avg', 'desc')
   ```
   Jasa baru dengan 1 ulasan bintang 5 muncul di atas jasa mapan dengan 100 ulasan bintang 4.8.

**Rekomendasi Fix:**
```php
// Bayesian Weighted Rating untuk Dashboard
$C = Service::where('review_count', '>', 0)->avg('rating_avg'); // prior mean
$m = 5; // minimum votes threshold

$topRated = Service::active()
    ->selectRaw("*, (review_count / (review_count + ?) * rating_avg + ? / (review_count + ?) * ?) as bayesian_score", [$m, $m, $m, $C])
    ->orderByDesc('bayesian_score')
    ->take(6)->get();
```

---

### B. `MarketplaceController.php` & `Marketplace/Index.vue`

**Bug / Gap yang Ditemukan:**

1. **Correlated subquery padahal kolom sudah ada**
   ```php
   // EKSISTING (lambat — subquery per-row):
   ->whereRaw('(SELECT AVG(rating) FROM reviews WHERE service_id = services.id) >= ?', [$minRating])

   // SEHARUSNYA (pakai kolom denormalisasi):
   ->where('rating_avg', '>=', $minRating)
   ```
   Kolom `rating_avg` sudah ada dan dijaga oleh `ReviewObserver`, tapi tidak dipakai di filter.

2. **`withAvg` dipanggil tapi tidak dipakai**
   ```php
   ->withAvg('reviews', 'rating') // dipanggil
   // tapi frontend pakai service.rating_avg, bukan service.reviews_avg_rating
   ```
   Membuang resource query tanpa manfaat.

3. **Kolom yang direferensikan di kode tapi belum ada di migrasi:**
   - `tags` (array/JSON untuk kategori tambahan)
   - `total_completed_orders` (denormalisasi hitungan order selesai)
   - `coverage_radius_km` / `is_remote`

4. **Tidak ada Sort By control di UI**
   `Marketplace/Index.vue` tidak punya dropdown untuk memilih kriteria urutan (Relevansi / Rating / Jarak / Harga). Filter hanya ada di sidebar (kategori, harga, rating slider).

5. **Mobile filter tidak punya dropdown autocomplete lokasi**
   Desktop punya autocomplete untuk input kota/lokasi, mobile tidak — inkonsistensi UX.

**Rekomendasi Fix — Ranking Formula:**
```php
// Multi-Criteria Weighted Score
$scoreExpr = "
    (0.40 * (rating_avg / 5.0) * (review_count / (review_count + 5)))  -- Bayesian Rating 40%
  + (0.30 * LEAST(total_completed_orders / 100.0, 1.0))                 -- Popularitas 30%
  + (0.30 * (1.0 - LEAST(distance_km / 50.0, 1.0)))                     -- Kedekatan 30%
";
->selectRaw("*, ($scoreExpr) as rank_score")
->orderByDesc('rank_score')
```

---

### C. `SearchController.php`, `Search/Index.vue` & `AuthenticatedLayout.vue`

**Bug / Gap yang Ditemukan:**

1. **Pencarian user mengekspos data sensitif**
   ```php
   // EKSISTING:
   User::where('name', 'like', "%{$query}%")
       ->orWhere('email', 'like', "%{$query}%") // ← email diekspos ke frontend!
       ->get(['id', 'name', 'email', 'avatar'])
   ```
   Email provider terekspos ke semua pengguna yang melakukan pencarian.

2. **`orWhere` tanpa closure grouping — SQL logic error**
   ```php
   // EKSISTING (salah — OR merusak WHERE sebelumnya):
   ->where('status', 'active')
   ->orWhere('name', 'like', "%{$q}%")

   // SEHARUSNYA:
   ->where('status', 'active')
   ->where(function($q) use ($query) {
       $q->where('name', 'like', "%{$query}%")
         ->orWhere('description', 'like', "%{$query}%");
   })
   ```

3. **Navbar search belum pakai ranking**
   `AuthenticatedLayout.vue` mengirim `q` ke `/search` tapi hasil tidak diurutkan berdasarkan skor relevansi apapun.

4. **FTS tidak menangani kata pendek**
   Kata < 3 karakter (AC, TV, HP, ojek) tidak diindeks oleh MySQL FULLTEXT secara default.

**Rekomendasi Fix — Dual-Mode FTS:**
```php
public function search(Request $request)
{
    $q = trim($request->input('q', ''));
    $isShortWord = mb_strlen($q) < 3;

    $services = Service::active()
        ->when(!$isShortWord, fn($query) =>
            $query->whereRaw("MATCH(name, description, tags) AGAINST(? IN BOOLEAN MODE)", ["+{$q}*"])
                  ->selectRaw("*, MATCH(name, description, tags) AGAINST(? IN BOOLEAN MODE) as fts_score", ["+{$q}*"])
        )
        ->when($isShortWord, fn($query) =>
            $query->where(function($q2) use ($q) {
                $q2->where('name', 'like', "%{$q}%")
                   ->orWhere('tags', 'like', "%{$q}%");
            })->selectRaw("*, 1.0 as fts_score")
        )
        ->orderByDesc('fts_score')
        ->paginate(20);
}
```

---

### D. `BookingController.php`

**Bug / Gap yang Ditemukan:**

1. **Kuota harian inkonsisten antara `create()` dan `store()`**

   Di `create()` (halaman form):
   ```php
   // Cek kuota by provider_id, include 'rejected'
   Booking::where('provider_id', $service->user_id)
       ->whereIn('status', ['pending', 'confirmed', 'rejected'])
       ->whereDate('booking_date', $date)
       ->count()
   ```

   Di `store()` (saat submit):
   ```php
   // Cek kuota by service_id, include 'completed'
   Booking::where('service_id', $service->id)
       ->whereIn('status', ['pending', 'confirmed', 'completed'])
       ->whereDate('booking_date', $date)
       ->count()
   ```

   Dua implementasi berbeda untuk logika yang sama → race condition dan ketidakkonsistenan.

2. **Tidak ada DB::transaction + lockForUpdate**
   ```php
   // EKSISTING (rawan race condition):
   if ($currentBookings < $maxBookings) {
       Booking::create([...]); // dua request bisa lolos bersamaan
   }

   // SEHARUSNYA:
   DB::transaction(function () use (...) {
       $currentBookings = Booking::where(...)
           ->lockForUpdate() // pessimistic lock
           ->count();
       if ($currentBookings >= $maxBookings) {
           throw new \Exception('Kuota penuh');
       }
       Booking::create([...]);
   });
   ```

3. **State machine tanpa validasi transisi**
   ```php
   // EKSISTING — semua transisi diizinkan:
   $booking->update(['status' => $request->status]);

   // SEHARUSNYA — validasi transisi:
   $validTransitions = [
       'pending'   => ['confirmed', 'rejected', 'cancelled'],
       'confirmed' => ['completed', 'cancelled'],
       'completed' => [], // terminal
       'rejected'  => [], // terminal
       'cancelled' => [], // terminal
   ];
   ```

---

### E. Bottleneck Kueri Lainnya

| Controller / File | Masalah | Dampak |
|---|---|---|
| `ChatController.php` | N+1 query pada sidebar — `lastMessage` tidak di-eager-load | Setiap percakapan = 1 query extra |
| `HandleInertiaRequests.php` | Polling notifikasi 10 detik tetap aktif meski WebSocket Echo sudah berjalan | Double-fetch, boros bandwidth |
| `ProfileController.php` | Statistik provider dihitung dari `paginate()` (hanya page pertama), bukan `count()` / `sum()` seluruh data | Statistik salah untuk provider dengan banyak data |
| `NotificationController.php` | `markAllAsRead` update satu per satu dalam loop | Seharusnya `whereIn` / bulk update |
| `Admin/AdminDashboardController.php` | `revenueByMonth` tanpa index pada `updated_at` / `created_at` di tabel `bookings` | Slow query di data besar |

---

## 3. Rekomendasi Peta Optimalisasi

### Prioritas 1 — Fondasi Database (Harus sebelum optimalisasi apapun)

```sql
-- 1. Composite index untuk Haversine bounding box
ALTER TABLE services ADD INDEX idx_geo_status (status, latitude, longitude);

-- 2. Composite index untuk ranking & filter
ALTER TABLE services ADD INDEX idx_ranking (status, rating_avg, review_count, total_completed_orders);

-- 3. FULLTEXT index untuk dual-mode search (jika belum ada)
ALTER TABLE services ADD FULLTEXT INDEX ft_search (name, description, tags);

-- 4. Kolom yang belum ada tapi direferensikan di kode
ALTER TABLE services
    ADD COLUMN tags JSON NULL AFTER description,
    ADD COLUMN total_completed_orders INT UNSIGNED NOT NULL DEFAULT 0,
    ADD COLUMN coverage_radius_km FLOAT NULL,
    ADD COLUMN is_remote TINYINT(1) NOT NULL DEFAULT 0;
```

### Prioritas 2 — Perbaikan Algoritma Core

| # | Komponen | Aksi |
|---|---|---|
| 1 | `SearchController` | Implementasi Dual-Mode FTS (Boolean Mode + fallback LIKE) |
| 2 | `MarketplaceController` | Ganti correlated subquery → kolom `rating_avg`; implementasi Multi-Criteria Weighted Ranking |
| 3 | `BookingController` | Seragamkan cek kuota; tambah `DB::transaction` + `lockForUpdate`; tambah state machine validator |
| 4 | `DashboardController` | Ganti `inRandomOrder()` dengan Bayesian Weighted Rating |

### Prioritas 3 — Perbaikan UI/UX

| # | Komponen | Aksi |
|---|---|---|
| 1 | `Marketplace/Index.vue` | Tambah Sort By dropdown (Relevansi / Rating / Jarak / Harga) |
| 2 | `Marketplace/Index.vue` mobile | Seragamkan autocomplete lokasi dengan desktop |
| 3 | `AuthenticatedLayout.vue` | Navbar search tampilkan preview hasil dengan skor relevansi |

### Prioritas 4 — Optimalisasi Performa

| # | Komponen | Aksi |
|---|---|---|
| 1 | `ChatController` | Eager-load `lastMessage` + `unreadCount` di sidebar query |
| 2 | `HandleInertiaRequests` | Nonaktifkan polling saat WebSocket Echo aktif |
| 3 | `NotificationController` | Ganti loop `markAllAsRead` → bulk `whereIn()->update()` |
| 4 | `ProfileController` | Hitung statistik dengan agregat DB, bukan dari hasil paginate |

### Prioritas 5 — Benchmark & Validasi

- Dataset uji: **10.000–50.000 baris** di tabel `services` dan `bookings`
- Gunakan `EXPLAIN ANALYZE` untuk validasi index usage setelah setiap perubahan
- Bandingkan query time sebelum vs sesudah dengan Laravel Telescope / Debugbar

---

## 4. Ringkasan Bug Kritis

| Severity | Bug | File | Dampak |
|---|---|---|---|
| 🔴 KRITIS | Race condition booking + kuota inkonsisten | `BookingController.php` | Double-booking, data korup |
| 🔴 KRITIS | Email provider terekspos di search response | `SearchController.php` | Pelanggaran privasi |
| 🟠 TINGGI | Bayesian prior `C` terdistorsi (include `rating_avg=0`) | `MarketplaceController.php` | Ranking tidak akurat |
| 🟠 TINGGI | `orWhere` tanpa closure merusak WHERE chain | `SearchController.php` | Filter status diabaikan |
| 🟡 SEDANG | `inRandomOrder()` di topProviders | `DashboardController.php` | Tidak deterministik, tidak relevan |
| 🟡 SEDANG | Correlated subquery padahal kolom sudah ada | `MarketplaceController.php` | Query lambat O(n) |
| 🟡 SEDANG | N+1 query di sidebar chat | `ChatController.php` | Performa buruk saat banyak percakapan |
| 🟡 SEDANG | Statistik dari paginate, bukan agregat | `ProfileController.php` | Data statistik salah |
| 🟢 RENDAH | Double-fetch notif (polling + WebSocket) | `HandleInertiaRequests.php` | Boros bandwidth |
| 🟢 RENDAH | `withAvg` dipanggil tapi tidak dipakai | `MarketplaceController.php` | Query resource terbuang |

---

## 5. Mapping ke Variabel Penelitian Proyek 3

Berdasarkan `Variabel.md` dan `KAJIAN_JURNAL_DAN_ANALISIS_VARIABEL_DATA.md`:

| Variabel Penelitian | Implementasi di Kode | Status |
|---|---|---|
| **Relevansi Pencarian (X1)** | FTS score dari MATCH...AGAINST | ⚠️ Ada tapi belum Dual-Mode |
| **Kedekatan Lokasi (X2)** | Haversine di MarketplaceController | ⚠️ Ada tapi index belum optimal |
| **Rating Penyedia (X3)** | `rating_avg` + `review_count` | ⚠️ Ada tapi Bayesian belum benar |
| **Popularitas (X4)** | `total_completed_orders` | ❌ Kolom belum ada di migrasi |
| **Waktu Respons (X5)** | — | ❌ Belum diimplementasi sama sekali |
| **Ketersediaan Slot (Y)** | Kuota harian di BookingController | ⚠️ Ada tapi race condition & inkonsisten |

> **Catatan:** Variabel X5 (Waktu Respons) belum ada implementasinya. Jika masuk ke scope penelitian, perlu kolom `avg_response_time_minutes` di tabel `users` yang diupdate setiap kali provider menjawab booking.

---

*File ini dibuat otomatis dari hasil audit kode FindServices — Proyek 3 Optimalisasi Algoritma*  
*Terakhir diperbarui: 2026-11-25*
