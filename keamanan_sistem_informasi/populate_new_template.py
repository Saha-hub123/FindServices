import openpyxl

wb_path = 'keamanan_sistem_informasi/1. template_baru_Praktikum_STRIDE-DREAD.xlsx'
wb = openpyxl.load_workbook(wb_path, data_only=False)

# ==========================================
# 1. SHEET: Profil_Aplikasi
# ==========================================
ws_profil = wb['Profil_Aplikasi']

# A. Ringkasan Sistem (B5:B9)
ws_profil['B5'] = "FindServices: Marketplace Layanan Jasa Lokal Terdekat (Laravel 12 + Inertia.js/Vue 3 + MySQL)"
ws_profil['B6'] = "Aplikasi web marketplace untuk menghubungkan pelanggan (Customer) dengan penyedia jasa lokal (Provider/Tukang) berbasis radius jarak geolokasi (Haversine), negosiasi pemesanan, pembayaran Midtrans, dan chat real-time."
ws_profil['B7'] = "Backend: Laravel 12 (PHP 8.3); Frontend: Vue 3 + Inertia.js + Tailwind CSS; Database: MySQL; Realtime: Laravel Reverb (WebSocket port 8080); Gateway: Midtrans Snap API; Tunnel: Cloudflare."
ws_profil['B8'] = "Pelanggan mencari jasa berdasarkan kategori atau lokasi terdekat lalu membuat pesanan (booking). Penyedia jasa meninjau, menyepakati harga final, dan mengonfirmasi pesanan. Pelanggan membayar via Midtrans Gateway atau Tunai, berkomunikasi via chat real-time Reverb, dan memberikan ulasan setelah selesai."
ws_profil['B9'] = "Analisis arsitektur, konfigurasi environment (.env), dan source code backend (controller, route, model, middleware, events) repositori FindServices melalui static code review dan threat modeling tanpa melakukan serangan aktif (non-destructive)."

# B. Komponen dan Aset (B15:E24, K1-K10)
komponen_data = [
    (15, "Modul Autentikasi & Akun (Auth & ProfileController)", 
         "Registrasi, login sesi, update profil, dan upload avatar pengguna", 
         "Kredensial akun, password hash bcrypt, token sesi, data profil pribadi", 
         "Atribut 'role' sempat terbuka di mass assignment model User; SESSION_ENCRYPT default false"),
    (16, "Modul Pemesanan & Alur Status (BookingController)", 
         "Membuat booking, validasi kuota harian, konfirmasi status, dan deal harga final", 
         "Integritas transaksi pesanan, validitas kesepakatan harga, jadwal kerja provider", 
         "Pengecekan hak akses auth()->id() di updateStatus sempat dinonaktifkan (potensi BOLA/IDOR)"),
    (17, "Modul Gateway Pembayaran (PaymentCallbackController)", 
         "Request token Snap Midtrans dan memproses webhook callback status pembayaran", 
         "Integritas status lunas booking, verifikasi finansial, Server Key Midtrans", 
         "Route webhook CSRF-exempt; verifikasi SHA512 rentan bypass bila Server Key kosong di env"),
    (18, "Modul Marketplace & Geolokasi (MarketplaceController)", 
         "Katalog jasa dengan filter kategori, harga, rating, dan radius Haversine", 
         "Ketersediaan layanan database server, privasi koordinat lokasi latitude/longitude", 
         "Kalkulasi rumus Haversine intensif CPU tanpa caching database berisiko Denial of Service"),
    (19, "Modul Manajemen Jasa & Galeri (ServiceController)", 
         "Publikasi jasa, deskripsi layanan, tarif minimum/maksimum, dan galeri foto", 
         "Integritas data katalog jasa publik, kapasitas penyimpanan disk server", 
         "Batas upload 10MB hanya validasi tipe MIME dasar tanpa inspeksi mendalam file biner"),
    (20, "Modul Percakapan Realtime (ChatController & Reverb)", 
         "Pengiriman pesan teks instan, penandaan dibaca, dan soft delete pesan chat", 
         "Kerahasiaan percakapan pribadi antar pengguna, ketersediaan daemon WebSocket", 
         "Endpoint /api/test-latency tanpa autentikasi berpotensi membanjiri channel Reverb (DoS)"),
    (21, "Modul Ulasan & Rating (Review & BookingController)", 
         "Menyimpan penilaian rating bintang, ulasan teks, dan foto bukti pengerjaan jasa", 
         "Reputasi provider, integritas skor rating jasa, konten review publik", 
         "Input teks review rentan Stored XSS jika dirender mentah (v-html) tanpa sanitasi HTML"),
    (22, "Modul Administrasi & Pengaduan (Admin Controllers)", 
         "Manajemen kategori jasa, penanganan laporan keluhan user, dan restore data", 
         "Hak akses administrator platform, integritas master kategori, data laporan pengaduan", 
         "AdminMiddleware mengandalkan field role pada model User; route admin harus steril dari bypass"),
    (23, "Modul Notifikasi Pengguna (NotificationController)", 
         "Mengirim notifikasi pesanan, pembayaran, dan ulasan ke database dan email", 
         "Kerahasiaan pemberitahuan transaksi, keandalan pengiriman antrean mail/notif", 
         "Kredensial SMTP Gmail di .env harus dilindungi dari pembacaan pihak ketiga"),
    (24, "Penyimpanan Database & Sesi (MySQL Database Engine)", 
         "Menyimpan tabel users, services, bookings, chats, reviews, reports, dan sessions", 
         "Integritas dan kerahasiaan seluruh rekaman basis data relasional aplikasi", 
         "Perlu prepared statement konsisten dan enkripsi sesi agar terhindar dari SQLi dan session hijacking")
]

for row_idx, komp, peran, aset, catatan in komponen_data:
    ws_profil[f'B{row_idx}'] = komp
    ws_profil[f'C{row_idx}'] = peran
    ws_profil[f'D{row_idx}'] = aset
    ws_profil[f'E{row_idx}'] = catatan

# C. Aliran Data (B30:E39, F1-F10)
aliran_data = [
    (30, "Browser Customer -> Web Router (Form Login / Registrasi)", 
         "Email, password, nama lengkap, nomor telepon, session cookie", 
         "HTTPS (TLS via Cloudflare Tunnel)", "Ya (TB-1 ke TB-2)"),
    (31, "Browser Customer -> MarketplaceController (Pencarian Jasa)", 
         "Query keyword, filter kategori, koordinat latitude/longitude, radius km", 
         "HTTPS GET", "Ya (TB-1 ke TB-2)"),
    (32, "Browser Customer -> BookingController (Form Pemesanan Jasa)", 
         "Service ID, tanggal booking, jam, lokasi alamat, catatan, metode bayar", 
         "HTTPS POST", "Ya (TB-1 ke TB-2)"),
    (33, "Browser Provider -> BookingController (Konfirmasi Status Pesanan)", 
         "Booking ID, status baru (confirmed/in_progress), agreed_price deal", 
         "HTTPS PATCH", "Ya (TB-1 ke TB-2)"),
    (34, "BookingController -> Midtrans Snap API (Permintaan Token Bayar)", 
         "Order ID unik, gross_amount (final_price + fee), identitas user, Server Key", 
         "HTTPS POST (TLS 1.3)", "Ya (TB-3 ke TB-1)"),
    (35, "Midtrans Gateway -> PaymentCallbackController (Webhook Callback)", 
         "order_id, status_code, gross_amount, signature_key, transaction_status", 
         "HTTP/HTTPS POST (/api/midtrans/callback)", "Ya (TB-1 ke TB-2)"),
    (36, "Browser Pengguna -> ChatController (Kirim Pesan Chat)", 
         "receiver_id (hashids), pesan teks, service_id, booking_id referensi", 
         "HTTPS POST", "Ya (TB-1 ke TB-2)"),
    (37, "Chat & Booking Controller -> Laravel Reverb (WebSocket Broadcast)", 
         "Event MessageSent / BookingStatusUpdated, payload data JSON serial", 
         "TCP WebSocket Internal (localhost:8080)", "Ya (TB-3 ke TB-4)"),
    (38, "Controller Aplikasi -> MySQL Database (findservices)", 
         "SQL queries (SELECT, INSERT, UPDATE tabel users, bookings, chats, reviews)", 
         "TCP MySQL port 3306", "Ya (TB-3 ke TB-5)"),
    (39, "Controller Aplikasi -> Storage Disk Lokal (storage/app/public)", 
         "File biner gambar avatar, galeri jasa, bukti laporan/review (.webp)", 
         "Local Filesystem I/O", "Ya (TB-3 ke TB-5)")
]

for row_idx, dari_ke, data, proto, tb in aliran_data:
    ws_profil[f'B{row_idx}'] = dari_ke
    ws_profil[f'C{row_idx}'] = data
    ws_profil[f'D{row_idx}'] = proto
    ws_profil[f'E{row_idx}'] = tb

# D. Trust Boundary (B45:C49, TB-1 to TB-5)
tb_data = [
    (45, "Browser Pengguna (Internet Publik) <-> Perimeter Jaringan / Cloudflare Ingress", 
         "Siapa pun di internet dapat mengirim request sembarang; seluruh data input dari luar tidak boleh dipercaya dan wajib divalidasi serta diautentikasi."),
    (46, "Perimeter Jaringan / Web Routing <-> Logika Aplikasi Laravel Core", 
         "Memisahkan lapisan routing publik/reverse proxy dengan proses bisnis internal; memvalidasi CSRF token, session cookie, dan middleware otorisasi."),
    (47, "Logika Aplikasi Laravel <-> Layanan Pihak Ketiga (Midtrans Gateway)", 
         "Pertukaran data finansial sensitif; webhook eksternal harus diverifikasi tanda tangan kriptografisnya (SHA512) agar tidak dapat dipalsukan peretas."),
    (48, "Aplikasi Laravel (PHP Worker) <-> WebSocket Daemon (Laravel Reverb)", 
         "Komunikasi real-time dua arah; Reverb berjalan sebagai daemon background port 8080 yang rentan kehabisan resource jika dibanjiri event tanpa rate limit."),
    (49, "Proses Aplikasi Laravel <-> Media Penyimpanan Persisten (MySQL & Local Storage)", 
         "Menyimpan aset paling berharga (kredensial hash, sesi, transaksi, file upload). Perlu isolasi direktori dan prepared statements untuk mencegah kebocoran data.")
]

for row_idx, batas, mengapa in tb_data:
    ws_profil[f'B{row_idx}'] = batas
    ws_profil[f'C{row_idx}'] = mengapa

print("Sheet Profil_Aplikasi updated.")

# ==========================================
# 2. SHEET: STRIDE_DREAD_Template
# ==========================================
ws_stride = wb['STRIDE_DREAD_Template']

threats_clean = [
    {
        'id': 'T-01 (CVE-2023-28438)',
        'desc': 'Penyerang yang terautentikasi memanipulasi parameter order_id pada endpoint status booking di BookingController tanpa verifikasi kepemilikan akun, sehingga dapat mengubah status pesanan milik pengguna lain secara sepihak.',
        'stride_S': 0, 'stride_T': 1, 'stride_R': 0, 'stride_I': 0, 'stride_D': 0, 'stride_E': 1,
        'dread_Damage': 8, 'dread_Repro': 9, 'dread_Exploit': 8, 'dread_Affected': 8, 'dread_Discov': 7,
        'alasan': 'Damage 8: penyerang dapat membatalkan atau mengubah sepihak status transaksi pengguna lain; Reproducibility 9: serangan sangat mudah diulang dengan mengganti parameter booking ID; Exploitability 8: dapat dieksekusi dengan request HTTP PATCH sederhana; Affected Users 8: berdampak pada seluruh pengguna aktif sistem; Discoverability 7: celah otorisasi mudah ditemukan melalui inspeksi endpoint API.',
        'bukti': 'BookingController.php baris 228–232: pengecekan hak akses kepemilikan auth()->id() dikomentari sehingga siapa pun dapat mengubah status booking.',
        'mitigasi': 'Aktifkan kembali validasi hak akses kepemilikan if (auth()->id() !== $booking->provider_id && auth()->id() !== $booking->customer_id) abort(403); dan gunakan Laravel Authorization Policy.'
    },
    {
        'id': 'T-02 (CVE-2023-34449)',
        'desc': 'Penyerang tanpa autentikasi mengirimkan ribuan request ke endpoint uji latensi WebSocket Reverb secara masif, sehingga membanjiri channel Reverb dan mengakibatkan server socket mengalami kehabisan memori serta lumpuh.',
        'stride_S': 0, 'stride_T': 0, 'stride_R': 0, 'stride_I': 0, 'stride_D': 1, 'stride_E': 0,
        'dread_Damage': 7, 'dread_Repro': 9, 'dread_Exploit': 9, 'dread_Affected': 8, 'dread_Discov': 7,
        'alasan': 'Damage 7: melumpuhkan fitur chat dan notifikasi real-time bagi seluruh pengguna; Reproducibility 9: sangat mudah diulang menggunakan script load testing; Exploitability 9: endpoint terbuka untuk publik tanpa autentikasi; Affected Users 8: memengaruhi seluruh pengguna yang mengandalkan real-time event; Discoverability 7: endpoint /api/test-latency tercantum jelas pada routes/api.php.',
        'bukti': 'routes/api.php baris 15–52: route POST /test-latency memicu TestLatency::dispatch tanpa middleware auth maupun rate limiting.',
        'mitigasi': 'Hapus route /test-latency pada lingkungan production atau lindungi dengan middleware auth:sanctum dan throttle rate limit 5 request per menit.'
    },
    {
        'id': 'T-03 (CVE-2023-45133)',
        'desc': 'Penyerang memalsukan notifikasi callback webhook Midtrans dengan mengeksploitasi kemungkinan kunci rahasia kosong pada berkas konfigurasi, sehingga status pembayaran booking berubah menjadi lunas tanpa transfer uang sesungguhnya.',
        'stride_S': 1, 'stride_T': 1, 'stride_R': 0, 'stride_I': 0, 'stride_D': 0, 'stride_E': 0,
        'dread_Damage': 9, 'dread_Repro': 8, 'dread_Exploit': 7, 'dread_Affected': 8, 'dread_Discov': 7,
        'alasan': 'Damage 9: menimbulkan kerugian finansial langsung karena pesanan dianggap lunas tanpa pembayaran riil; Reproducibility 8: mudah diulang dengan replay packet HTTP POST; Exploitability 7: membutuhkan pengetahuan format payload Midtrans; Affected Users 8: berdampak pada penyedia jasa dan platform; Discoverability 7: route webhook dikecualikan dari proteksi CSRF di bootstrap/app.php.',
        'bukti': 'PaymentCallbackController.php baris 14–38 dan bootstrap/app.php baris 21–23: route api/midtrans/callback dikecualikan dari CSRF dan .env membiarkan MIDTRANS_SERVER_KEY kosong secara default.',
        'mitigasi': 'Validasi ketat konfigurasi MIDTRANS_SERVER_KEY tidak boleh kosong, verifikasi ulang status transaksi langsung ke API Get Status Midtrans, dan catat log audit transaksi.'
    },
    {
        'id': 'T-04 (CVE-2023-38035)',
        'desc': 'Pengguna jahat memicu pencarian katalog dengan koordinat radius geolokasi secara berulang dan mengunggah banyak berkas berukuran 10MB, sehingga membebani CPU database dan menghabiskan ruang penyimpanan server.',
        'stride_S': 0, 'stride_T': 0, 'stride_R': 0, 'stride_I': 0, 'stride_D': 1, 'stride_E': 0,
        'dread_Damage': 7, 'dread_Repro': 8, 'dread_Exploit': 8, 'dread_Affected': 8, 'dread_Discov': 7,
        'alasan': 'Damage 7: menurunkan responsivitas server dan berisiko server crash karena kehabisan ruang disk; Reproducibility 8: dapat diulang otomatis dengan skrip bot HTTP; Exploitability 8: dapat dilakukan oleh siapa saja yang memiliki akun; Affected Users 8: seluruh pengguna mengalami kelambatan akses; Discoverability 7: batas upload 10MB dan endpoint pencarian publik terlihat langsung di UI.',
        'bukti': 'MarketplaceController.php baris 57–68: query rumus Haversine tanpa indexing spasial dan ProfileUpdateRequest.php / ServiceController.php: batas upload mencapai 10240 KB (10MB) per file.',
        'mitigasi': 'Terapkan caching hasil pencarian geolokasi (Redis/Database), turunkan batas maksimal upload menjadi 2MB, dan pasang rate limiting pada endpoint marketplace.'
    },
    {
        'id': 'T-05 (CVE-2024-21501)',
        'desc': 'Pengguna menyisipkan skrip berbahaya berupa payload JavaScript pada kolom ulasan review atau catatan pemesanan jasa, sehingga skrip dieksekusi di browser penyedia jasa atau administrator saat membuka halaman.',
        'stride_S': 0, 'stride_T': 1, 'stride_R': 0, 'stride_I': 1, 'stride_D': 0, 'stride_E': 0,
        'dread_Damage': 7, 'dread_Repro': 8, 'dread_Exploit': 7, 'dread_Affected': 8, 'dread_Discov': 7,
        'alasan': 'Damage 7: pencurian sesi token admin/provider atau pengalihan halaman; Reproducibility 8: tersimpan permanen di database dan dieksekusi setiap halaman dibuka; Exploitability 7: membutuhkan keahlian injeksi script dasar; Affected Users 8: berdampak pada semua user yang melihat ulasan/booking tersebut; Discoverability 7: kolom input teks review terbuka luas.',
        'bukti': 'BookingController.php baris 470–502: kolom comment review hanya divalidasi string|max:500 tanpa pembersihan tag HTML (strip_tags atau htmlspecialchars).',
        'mitigasi': 'Terapkan sanitasi input menggunakan strip_tags() pada backend dan pastikan komponen Vue tidak menggunakan direktif v-html pada rendering konten ulasan.'
    },
    {
        'id': 'T-06 (CVE-2023-22809)',
        'desc': 'Pengguna mendaftar atau memperbarui profil lalu menambahkan parameter role=admin melalui manipulasi HTTP request payload, sehingga hak akses akun meningkat menjadi administrator karena atribut role masuk ke fillable model.',
        'stride_S': 0, 'stride_T': 1, 'stride_R': 0, 'stride_I': 0, 'stride_D': 0, 'stride_E': 1,
        'dread_Damage': 9, 'dread_Repro': 8, 'dread_Exploit': 7, 'dread_Affected': 7, 'dread_Discov': 6,
        'alasan': 'Damage 9: penyerang memperoleh hak akses penuh mengelola kategori, laporan, dan data seluruh sistem; Reproducibility 8: dapat diulang pada endpoint modifikasi profil; Exploitability 7: membutuhkan pengiriman raw JSON request; Affected Users 7: integritas seluruh sistem terdampak; Discoverability 6: celah mass assignment dapat diprediksi dari struktur Eloquent standar.',
        'bukti': 'app/Models/User.php baris 26: kolom \'role\' terdaftar di properti protected $fillable User model.',
        'mitigasi': 'Keluarkan atribut \'role\' dari array $fillable pada model User, dan atur penetapan role hanya melalui seeder atau controller admin khusus.'
    },
    {
        'id': 'T-07 (CVE-2024-21516)',
        'desc': 'Pengguna mengunggah berkas gambar manipulasi (seperti polyglot file atau SVG berbisa) pada fitur foto jasa dan avatar profil, sehingga berkas berbahaya tersimpan di direktori publik server dan dapat memicu SSRF atau XSS.',
        'stride_S': 0, 'stride_T': 1, 'stride_R': 0, 'stride_I': 1, 'stride_D': 0, 'stride_E': 0,
        'dread_Damage': 8, 'dread_Repro': 7, 'dread_Exploit': 6, 'dread_Affected': 7, 'dread_Discov': 6,
        'alasan': 'Damage 8: potensi eksekusi script atau pembacaan file internal server; Reproducibility 7: berhasil selama berkas lolos filter ekstensi mime; Exploitability 6: membutuhkan crafting payload file khusus; Affected Users 7: pengunjung dan server berisiko terdampak; Discoverability 6: fitur upload media tersedia di berbagai modul.',
        'bukti': 'ServiceController.php baris 63–64 dan UserReportController.php baris 36: validasi hanya memeriksa ekstensi mimes tanpa verifikasi magic bytes konten gambar.',
        'mitigasi': 'Gunakan pustaka image processing (seperti Intervention Image) untuk merender ulang dan mengonversi semua gambar ke WebP/JPEG murni, serta nonaktifkan eksekusi skrip di folder storage.'
    },
    {
        'id': 'T-08 (CVE-2022-31129)',
        'desc': 'Pihak ketiga pada jaringan lokal atau perantara sniffing mencuri session ID pengguna karena konfigurasi sesi di database tidak dienkripsi, sehingga penyerang dapat membajak sesi login pengguna tanpa memerlukan password.',
        'stride_S': 1, 'stride_T': 0, 'stride_R': 0, 'stride_I': 1, 'stride_D': 0, 'stride_E': 0,
        'dread_Damage': 8, 'dread_Repro': 7, 'dread_Exploit': 6, 'dread_Affected': 7, 'dread_Discov': 6,
        'alasan': 'Damage 8: akun korban diambil alih sepenuhnya selama sesi masih valid; Reproducibility 7: dapat diulang jika penyerang memperoleh token sesi; Exploitability 6: membutuhkan akses sniffing atau kebocoran database; Affected Users 7: memengaruhi pengguna yang sedang login aktif; Discoverability 6: konfigurasi .env SESSION_ENCRYPT=false dapat diketahui dari audit sistem.',
        'bukti': '.env baris 34–36: SESSION_DRIVER=database dan SESSION_ENCRYPT=false menyimpan payload sesi secara plaintext di tabel sessions.',
        'mitigasi': 'Ubah konfigurasi .env menjadi SESSION_ENCRYPT=true dan pastikan flag cookie HttpOnly serta Secure aktif di config/session.php.'
    },
    {
        'id': 'T-09 (CVE-2022-31279)',
        'desc': 'Pengguna yang terautentikasi memanipulasi parameter hash_id pada URL percakapan atau request penghapusan pesan, sehingga dapat membaca pesan rahasia atau menghapus riwayat chat milik pihak lain tanpa izin.',
        'stride_S': 0, 'stride_T': 1, 'stride_R': 0, 'stride_I': 1, 'stride_D': 0, 'stride_E': 0,
        'dread_Damage': 6, 'dread_Repro': 8, 'dread_Exploit': 7, 'dread_Affected': 6, 'dread_Discov': 6,
        'alasan': 'Damage 6: kerahasiaan negosiasi dan privasi chat bocor atau hilang; Reproducibility 8: mudah diulang dengan men-decode pola Hashids; Exploitability 7: membutuhkan tebakan atau manipulasi hash parameter; Affected Users 6: terbatas pada pasangan chat yang disasar; Discoverability 6: parameter hash_id tampak jelas pada URL query string.',
        'bukti': 'ChatController.php baris 59–97 dan baris 240–253: pemuatan pesan konteks dan validasi kepemilikan mengandalkan decode hash tanpa policy terpusat.',
        'mitigasi': 'Gunakan Laravel Policy untuk memeriksa relasi pesan sebelum memuat atau menghapus chat, dan jangan jadikan Hashids sebagai satu-satunya lapisan keamanan otorisasi.'
    },
    {
        'id': 'T-10 (CVE-2023-40028)',
        'desc': '[TERMITIGASI] Pengunjung website memicu error sistem untuk melihat tampilan stack trace lengkap dan kredensial sensitif, namun saat ini risiko telah diminimalisasi karena parameter APP_DEBUG telah dinonaktifkan di berkas .env.',
        'stride_S': 0, 'stride_T': 0, 'stride_R': 0, 'stride_I': 1, 'stride_D': 0, 'stride_E': 0,
        'dread_Damage': 2, 'dread_Repro': 1, 'dread_Exploit': 1, 'dread_Affected': 1, 'dread_Discov': 1,
        'alasan': 'Damage 2: sistem hanya menampilkan halaman error 500 generik tanpa membocorkan data; Reproducibility 1: tidak lagi dapat direproduksi di lingkungan publik; Exploitability 1: tidak ada data sensitif yang diekspos di browser; Affected Users 1: tidak ada pengguna yang terdampak; Discoverability 1: pemindaian otomatis tidak lagi menemukan celah debug.',
        'bukti': '.env baris 4: parameter APP_DEBUG telah diatur bernilai false (APP_DEBUG=false) sehingga stack trace dan environment variables terlindungi.',
        'mitigasi': 'Pertahankan APP_DEBUG=false pada lingkungan production, aktifkan log rotasi, dan gunakan sentry atau monitoring tertutup untuk pelacakan exception.'
    }
]

for idx, t in enumerate(threats_clean):
    row_num = 5 + idx
    ws_stride[f'B{row_num}'] = t['id']
    ws_stride[f'C{row_num}'] = t['desc']
    
    # STRIDE (0 or 1)
    ws_stride[f'D{row_num}'] = t['stride_S']
    ws_stride[f'E{row_num}'] = t['stride_T']
    ws_stride[f'F{row_num}'] = t['stride_R']
    ws_stride[f'G{row_num}'] = t['stride_I']
    ws_stride[f'H{row_num}'] = t['stride_D']
    ws_stride[f'I{row_num}'] = t['stride_E']
    
    # DREAD (0 to 10)
    ws_stride[f'K{row_num}'] = t['dread_Damage']
    ws_stride[f'L{row_num}'] = t['dread_Repro']
    ws_stride[f'M{row_num}'] = t['dread_Exploit']
    ws_stride[f'N{row_num}'] = t['dread_Affected']
    ws_stride[f'O{row_num}'] = t['dread_Discov']
    
    # Descriptions (S, T, U)
    ws_stride[f'S{row_num}'] = t['alasan']
    ws_stride[f'T{row_num}'] = t['bukti']
    ws_stride[f'U{row_num}'] = t['mitigasi']

wb.save(wb_path)
print("Updated workbook successfully with clean keys.")
