import re
import openpyxl

# 1. Read dfd_threat_modeling copy.html to get the clean orthogonal SVG
with open(r'c:\laragon\www\FindServices\keamanan_sistem_informasi\dfd_threat_modeling copy.html', 'r', encoding='utf-8') as f:
    copy_html = f.read()

svg_match = re.search(r'(<svg\s+viewBox="0 0 1340 760".*?</svg>)', copy_html, re.DOTALL)
if not svg_match:
    raise ValueError("SVG not found in copy file")
svg_clean = svg_match.group(1)

# 2. Hardcoded exact verified data from 1. template_baru_Praktikum_STRIDE-DREAD.xlsx
threats = [
    {
        'id': 'T-01 (CVE-2023-28438)',
        'desc': 'Penyerang yang terautentikasi memanipulasi parameter order_id pada endpoint status booking di BookingController tanpa verifikasi kepemilikan akun, sehingga dapat mengubah status pesanan milik pengguna lain secara sepihak.',
        'stride': ['T', 'E'],
        'dread': {'D': 8, 'R': 9, 'E': 8, 'A': 8, 'X': 7},
        'total': 40,
        'level': 'CRITICAL',
        'bukti': 'BookingController.php baris 228–232: pengecekan hak akses kepemilikan auth()->id() dikomentari.',
        'mitigasi': 'Aktifkan kembali validasi: if (auth()->id() !== $booking->provider_id && auth()->id() !== $booking->customer_id) abort(403); & BookingPolicy.'
    },
    {
        'id': 'T-02 (CVE-2023-34449)',
        'desc': 'Penyerang tanpa autentikasi mengirimkan ribuan request ke endpoint uji latensi WebSocket Reverb secara masif, sehingga membanjiri channel Reverb dan mengakibatkan server socket mengalami kehabisan memori serta lumpuh.',
        'stride': ['D'],
        'dread': {'D': 7, 'R': 9, 'E': 9, 'A': 8, 'X': 7},
        'total': 40,
        'level': 'CRITICAL',
        'bukti': 'routes/api.php baris 15–52: route POST /test-latency memicu TestLatency::dispatch tanpa middleware auth maupun rate limiting.',
        'mitigasi': 'Hapus route /test-latency di production atau lindungi dengan auth:sanctum dan throttle rate limit 5 req/min.'
    },
    {
        'id': 'T-03 (CVE-2023-45133)',
        'desc': 'Penyerang memalsukan notifikasi callback webhook Midtrans dengan mengeksploitasi kemungkinan kunci rahasia kosong pada berkas konfigurasi, sehingga status pembayaran booking berubah menjadi lunas tanpa transfer uang sesungguhnya.',
        'stride': ['S', 'T'],
        'dread': {'D': 9, 'R': 8, 'E': 7, 'A': 8, 'X': 7},
        'total': 39,
        'level': 'HIGH',
        'bukti': 'PaymentCallbackController.php:14–38 & bootstrap/app.php:21–23: route callback CSRF-exempt & key kosong.',
        'mitigasi': 'Validasi ketat MIDTRANS_SERVER_KEY tidak boleh kosong, verifikasi hash SHA512, dan inquiry API.'
    },
    {
        'id': 'T-04 (CVE-2023-38035)',
        'desc': 'Pengguna jahat memicu pencarian katalog dengan koordinat radius geolokasi secara berulang dan mengunggah banyak berkas berukuran 10MB, sehingga membebani CPU database dan menghabiskan ruang penyimpanan server.',
        'stride': ['D'],
        'dread': {'D': 7, 'R': 8, 'E': 8, 'A': 8, 'X': 7},
        'total': 38,
        'level': 'HIGH',
        'bukti': 'MarketplaceController.php baris 57–68: query Haversine tanpa cache & upload file mencapai 10MB.',
        'mitigasi': 'Terapkan Redis caching untuk hasil pencarian geolokasi, turunkan batas upload menjadi 2MB, dan pasang rate limiting.'
    },
    {
        'id': 'T-05 (CVE-2024-21501)',
        'desc': 'Pengguna menyisipkan skrip berbahaya berupa payload JavaScript pada kolom ulasan review atau catatan pemesanan jasa, sehingga skrip dieksekusi di browser penyedia jasa atau administrator saat membuka halaman.',
        'stride': ['T', 'I'],
        'dread': {'D': 7, 'R': 8, 'E': 7, 'A': 8, 'X': 7},
        'total': 37,
        'level': 'HIGH',
        'bukti': 'BookingController.php baris 470–502: kolom comment review divalidasi string tanpa pembersihan tag HTML.',
        'mitigasi': 'Terapkan sanitasi input strip_tags() pada backend dan pastikan Vue tidak memakai direktif v-html.'
    },
    {
        'id': 'T-06 (CVE-2023-22809)',
        'desc': 'Pengguna mendaftar atau memperbarui profil lalu menambahkan parameter role=admin melalui manipulasi HTTP request payload, sehingga hak akses akun meningkat menjadi administrator karena atribut role masuk ke fillable model.',
        'stride': ['T', 'E'],
        'dread': {'D': 9, 'R': 8, 'E': 7, 'A': 7, 'X': 6},
        'total': 37,
        'level': 'HIGH',
        'bukti': 'app/Models/User.php baris 26: kolom \'role\' terdaftar di properti protected $fillable User model.',
        'mitigasi': 'Keluarkan atribut \'role\' dari array $fillable pada User, dan atur peran admin via seeder/panel khusus.'
    },
    {
        'id': 'T-07 (CVE-2024-21516)',
        'desc': 'Pengguna mengunggah berkas gambar manipulasi (seperti polyglot file atau SVG berbisa) pada fitur foto jasa dan avatar profil, sehingga berkas berbahaya tersimpan di direktori publik server dan dapat memicu SSRF atau XSS.',
        'stride': ['T', 'I'],
        'dread': {'D': 8, 'R': 7, 'E': 6, 'A': 7, 'X': 6},
        'total': 34,
        'level': 'HIGH',
        'bukti': 'ServiceController.php:63–64 & UserReportController.php:36: validasi hanya cek ekstensi mimes tanpa magic bytes.',
        'mitigasi': 'Gunakan Intervention Image untuk merender ulang dan konversi semua gambar ke JPEG/WebP murni.'
    },
    {
        'id': 'T-08 (CVE-2022-31129)',
        'desc': 'Pihak ketiga pada jaringan lokal atau perantara sniffing mencuri session ID pengguna karena konfigurasi sesi di database tidak dienkripsi, sehingga penyerang dapat membajak sesi login pengguna tanpa memerlukan password.',
        'stride': ['S', 'I'],
        'dread': {'D': 8, 'R': 7, 'E': 6, 'A': 7, 'X': 6},
        'total': 34,
        'level': 'HIGH',
        'bukti': '.env baris 34–36: SESSION_DRIVER=database dan SESSION_ENCRYPT=false menyimpan sesi secara plaintext.',
        'mitigasi': 'Ubah konfigurasi .env menjadi SESSION_ENCRYPT=true dan pastikan flag cookie HttpOnly serta Secure aktif.'
    },
    {
        'id': 'T-09 (CVE-2022-31279)',
        'desc': 'Pengguna yang terautentikasi memanipulasi parameter hash_id pada URL percakapan atau request penghapusan pesan, sehingga dapat membaca pesan rahasia atau menghapus riwayat chat milik pihak lain tanpa izin.',
        'stride': ['T', 'I'],
        'dread': {'D': 6, 'R': 8, 'E': 7, 'A': 6, 'X': 6},
        'total': 33,
        'level': 'HIGH',
        'bukti': 'ChatController.php baris 59–97 & 240–253: pemuatan pesan konteks mengandalkan decode hash tanpa policy.',
        'mitigasi': 'Gunakan Laravel Policy untuk memeriksa relasi pesan sebelum memuat atau menghapus histori chat.'
    },
    {
        'id': 'T-10 (CVE-2023-40028)',
        'desc': '[TERMITIGASI] Pengunjung website memicu error sistem untuk melihat tampilan stack trace lengkap dan kredensial sensitif, namun saat ini risiko telah diminimalisasi karena parameter APP_DEBUG telah dinonaktifkan di berkas .env.',
        'stride': ['I'],
        'dread': {'D': 2, 'R': 1, 'E': 1, 'A': 1, 'X': 1},
        'total': 6,
        'level': 'LOW',
        'bukti': '.env baris 4: parameter APP_DEBUG telah bernilai false (APP_DEBUG=false) sehingga stack trace terlindungi.',
        'mitigasi': 'Pertahankan APP_DEBUG=false di production, aktifkan log rotasi, dan gunakan monitoring tertutup (Sentry).'
    }
]

# Exact metrics
critical_count = 2
high_count = 7
medium_count = 0
low_count = 1
avg_dread = 33.8
max_dread = 40

stride_counts = {
    'Tamper (T)': 6,
    'Info (I)': 5,
    'Spoof (S)': 2,
    'DoS (D)': 2,
    'Elevate (E)': 2,
    'Repudi (R)': 0
}

html_4x3 = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <title>Infografik Threat Modeling FindServices - Light Theme (4:3 Ratio)</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      background-color: #f1f5f9;
      color: #1e293b;
      width: 1920px;
      height: 1440px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 16px 20px 14px 20px;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
    .card-box {{
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }}
    .gradient-header {{
      background: linear-gradient(135deg, #0284c7 0%, #2563eb 50%, #7c3aed 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
  </style>
</head>
<body>

  <!-- ======================================================== -->
  <!-- HEADER BAR (Height: ~68px)                               -->
  <!-- ======================================================== -->
  <header class="card-box px-6 py-2.5 flex items-center justify-between shadow-sm">
    <div class="flex items-center gap-4">
      <div class="w-11 h-11 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center shadow-md text-white font-black text-xl">
        FS
      </div>
      <div>
        <div class="flex items-center gap-2.5">
          <h1 class="text-xl font-extrabold tracking-tight text-slate-900 uppercase">
            FINDSERVICES <span class="gradient-header">THREAT MODELING DASHBOARD</span>
          </h1>
          <span class="mono text-[10.5px] bg-blue-100 text-blue-800 border border-blue-300 px-2 py-0.5 rounded font-bold">STRIDE &amp; DREAD</span>
          <span class="mono text-[10.5px] bg-slate-100 text-slate-700 border border-slate-300 px-2 py-0.5 rounded">OWASP FRAMEWORK</span>
        </div>
        <p class="text-xs text-slate-500 mt-0.5">
          Target Sistem: <strong class="text-slate-800">FindServices Marketplace</strong> (Laravel 12 + Vue 3/Inertia + MySQL + Reverb + Midtrans) | Praktikum Keamanan SI
        </p>
      </div>
    </div>

    <!-- Top Key Badges (CORRECT VALUES FROM EXCEL) -->
    <div class="flex items-center gap-3">
      <div class="flex items-center gap-2 bg-slate-100 border border-slate-300 px-3 py-1.5 rounded-lg text-xs">
        <span class="text-slate-600 font-medium">Total Ancaman:</span>
        <span class="mono font-extrabold text-slate-900 text-sm">10</span>
      </div>
      <div class="flex items-center gap-2 bg-rose-50 border border-rose-300 px-3 py-1.5 rounded-lg text-xs">
        <span class="w-2.5 h-2.5 rounded-full bg-rose-600 animate-pulse"></span>
        <span class="text-rose-800 font-semibold">Critical:</span>
        <span class="mono font-extrabold text-rose-900 text-sm">{critical_count}</span>
      </div>
      <div class="flex items-center gap-2 bg-amber-50 border border-amber-300 px-3 py-1.5 rounded-lg text-xs">
        <span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
        <span class="text-amber-800 font-semibold">High:</span>
        <span class="mono font-extrabold text-amber-900 text-sm">{high_count}</span>
      </div>
      <div class="flex items-center gap-2 bg-emerald-50 border border-emerald-300 px-3 py-1.5 rounded-lg text-xs">
        <span class="w-2.5 h-2.5 rounded-full bg-emerald-600"></span>
        <span class="text-emerald-800 font-semibold">Mitigated:</span>
        <span class="mono font-extrabold text-emerald-900 text-sm">{low_count}</span>
      </div>
      <div class="flex items-center gap-2 bg-sky-50 border border-sky-300 px-3 py-1.5 rounded-lg text-xs">
        <span class="text-sky-800 font-semibold">Avg DREAD:</span>
        <span class="mono font-extrabold text-sky-900 text-sm">{avg_dread} <span class="text-[10px] text-slate-500 font-normal">/50</span></span>
      </div>
    </div>
  </header>

  <!-- ======================================================== -->
  <!-- MAIN WORKSPACE: 2 COLUMNS (Height: ~1320px)              -->
  <!-- ======================================================== -->
  <div class="grid grid-cols-12 gap-3.5 flex-1 mt-3 mb-1 overflow-hidden" style="height: 1315px;">
    
    <!-- ====================================================== -->
    <!-- LEFT COLUMN (Cols: 7 / 12) - System, Workflow, DFD     -->
    <!-- ====================================================== -->
    <div class="col-span-7 flex flex-col justify-between gap-3 h-full overflow-hidden">
      
      <!-- ROW 1: System Summary & Workflow (Height: ~285px) -->
      <div class="grid grid-cols-12 gap-3 shrink-0" style="height: 285px;">
        
        <!-- System Profile Card (Cols: 5) -->
        <div class="col-span-5 card-box p-3.5 flex flex-col justify-between text-xs">
          <div>
            <div class="flex items-center justify-between pb-1.5 border-b border-slate-200 mb-2">
              <span class="font-bold text-slate-900 flex items-center gap-1.5 text-xs">
                <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
                1. Profil &amp; Arsitektur Sistem
              </span>
              <span class="mono text-[10px] text-blue-700 bg-blue-50 border border-blue-200 px-1.5 py-0.5 rounded font-bold">FINDSERVICES</span>
            </div>
            <p class="text-slate-600 text-[11px] leading-relaxed line-clamp-3 mb-2">
              Platform marketplace berbasis web yang menghubungkan <em class="text-slate-800 font-medium">Customer</em> dengan <em class="text-slate-800 font-medium">Provider/Tukang</em> lokal terdekat berbasis radius koordinat (Haversine), negosiasi biaya, escrow Midtrans, dan chat real-time.
            </p>
            <div class="space-y-1 text-[10.5px]">
              <div class="flex justify-between py-0.5 border-b border-slate-100">
                <span class="text-slate-500">Backend Core:</span>
                <span class="text-slate-800 font-semibold">Laravel 12 (PHP 8.3)</span>
              </div>
              <div class="flex justify-between py-0.5 border-b border-slate-100">
                <span class="text-slate-500">Frontend Stack:</span>
                <span class="text-slate-800 font-semibold">Vue 3 + Inertia.js</span>
              </div>
              <div class="flex justify-between py-0.5 border-b border-slate-100">
                <span class="text-slate-500">Database &amp; Store:</span>
                <span class="text-slate-800 font-semibold">MySQL 8.0 &amp; Local Disk</span>
              </div>
              <div class="flex justify-between py-0.5">
                <span class="text-slate-500">Realtime Daemon:</span>
                <span class="text-purple-700 font-semibold">Laravel Reverb (:8080)</span>
              </div>
            </div>
          </div>
          <div class="pt-1.5 border-t border-slate-200 flex items-center justify-between text-[10px] text-slate-500">
            <span>Aktor: Customer, Provider, Admin</span>
            <span class="text-blue-700 font-semibold">Ruang Lingkup: Static Audit</span>
          </div>
        </div>

        <!-- Workflow Pipeline Card (Cols: 7) -->
        <div class="col-span-7 card-box p-3.5 flex flex-col justify-between text-xs">
          <div>
            <div class="flex items-center justify-between pb-1.5 border-b border-slate-200 mb-2">
              <span class="font-bold text-slate-900 flex items-center gap-1.5 text-xs">
                <svg class="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                2. Alur Kerja Pengguna &amp; Titik Ancaman (Touchpoints)
              </span>
              <span class="text-[10px] text-slate-500 font-medium">5 Siklus Layanan</span>
            </div>
            
            <!-- 5 Steps Flow (Light) -->
            <div class="grid grid-cols-5 gap-1.5 text-center mt-1">
              <!-- Step 1 -->
              <div class="p-1.5 rounded-lg bg-slate-50 border border-slate-200 flex flex-col justify-between h-[180px]">
                <div>
                  <div class="mono w-5 h-5 mx-auto rounded-full bg-blue-100 text-blue-700 border border-blue-300 text-[10px] font-bold flex items-center justify-center mb-1">1</div>
                  <div class="font-bold text-slate-800 text-[10.5px]">Pencarian &amp; Auth</div>
                  <div class="text-[9.5px] text-slate-500 mt-1 leading-tight">Customer login &amp; cari jasa via radius Haversine</div>
                </div>
                <div class="mt-2 pt-1 border-t border-slate-200 space-y-1">
                  <div class="mono text-[9px] bg-amber-50 text-amber-800 rounded px-1 py-0.5 border border-amber-300 font-bold" title="DoS Haversine Query">T-04 (DoS)</div>
                  <div class="mono text-[9px] bg-amber-50 text-amber-800 rounded px-1 py-0.5 border border-amber-300 font-bold" title="Plaintext Session">T-08 (Sess)</div>
                </div>
              </div>

              <!-- Step 2 -->
              <div class="p-1.5 rounded-lg bg-slate-50 border border-slate-200 flex flex-col justify-between h-[180px]">
                <div>
                  <div class="mono w-5 h-5 mx-auto rounded-full bg-blue-100 text-blue-700 border border-blue-300 text-[10px] font-bold flex items-center justify-center mb-1">2</div>
                  <div class="font-bold text-slate-800 text-[10.5px]">Booking &amp; Nego</div>
                  <div class="text-[9.5px] text-slate-500 mt-1 leading-tight">Buat pesanan, negosiasi dan kesepakatan harga</div>
                </div>
                <div class="mt-2 pt-1 border-t border-slate-200 space-y-1">
                  <div class="mono text-[9px] bg-rose-50 text-rose-800 rounded px-1 py-0.5 border border-rose-300 font-black" title="BOLA / IDOR Status Booking">T-01 (IDOR)</div>
                  <div class="mono text-[9px] bg-amber-50 text-amber-800 rounded px-1 py-0.5 border border-amber-300 font-bold" title="Mass Assignment Role">T-06 (Priv)</div>
                </div>
              </div>

              <!-- Step 3 -->
              <div class="p-1.5 rounded-lg bg-slate-50 border border-slate-200 flex flex-col justify-between h-[180px]">
                <div>
                  <div class="mono w-5 h-5 mx-auto rounded-full bg-blue-100 text-blue-700 border border-blue-300 text-[10px] font-bold flex items-center justify-center mb-1">3</div>
                  <div class="font-bold text-slate-800 text-[10.5px]">Pembayaran</div>
                  <div class="text-[9.5px] text-slate-500 mt-1 leading-tight">Snap Midtrans token &amp; callback webhook</div>
                </div>
                <div class="mt-2 pt-1 border-t border-slate-200 space-y-1">
                  <div class="mono text-[9px] bg-amber-50 text-amber-800 rounded px-1 py-0.5 border border-amber-300 font-bold" title="Webhook Signature Bypass">T-03 (Pay)</div>
                </div>
              </div>

              <!-- Step 4 -->
              <div class="p-1.5 rounded-lg bg-slate-50 border border-slate-200 flex flex-col justify-between h-[180px]">
                <div>
                  <div class="mono w-5 h-5 mx-auto rounded-full bg-blue-100 text-blue-700 border border-blue-300 text-[10px] font-bold flex items-center justify-center mb-1">4</div>
                  <div class="font-bold text-slate-800 text-[10.5px]">Chat &amp; Kerja</div>
                  <div class="text-[9.5px] text-slate-500 mt-1 leading-tight">Pengerjaan jasa &amp; komunikasi socket Reverb</div>
                </div>
                <div class="mt-2 pt-1 border-t border-slate-200 space-y-1">
                  <div class="mono text-[9px] bg-rose-50 text-rose-800 rounded px-1 py-0.5 border border-rose-300 font-black" title="Reverb WebSocket Flooding">T-02 (DoS)</div>
                  <div class="mono text-[9px] bg-amber-50 text-amber-800 rounded px-1 py-0.5 border border-amber-300 font-bold" title="Chat Hashids Tampering">T-09 (Chat)</div>
                </div>
              </div>

              <!-- Step 5 -->
              <div class="p-1.5 rounded-lg bg-slate-50 border border-slate-200 flex flex-col justify-between h-[180px]">
                <div>
                  <div class="mono w-5 h-5 mx-auto rounded-full bg-blue-100 text-blue-700 border border-blue-300 text-[10px] font-bold flex items-center justify-center mb-1">5</div>
                  <div class="font-bold text-slate-800 text-[10.5px]">Review &amp; Selesai</div>
                  <div class="text-[9.5px] text-slate-500 mt-1 leading-tight">Konfirmasi selesai, ulasan rating &amp; upload foto</div>
                </div>
                <div class="mt-2 pt-1 border-t border-slate-200 space-y-1">
                  <div class="mono text-[9px] bg-amber-50 text-amber-800 rounded px-1 py-0.5 border border-amber-300 font-bold" title="Stored XSS Review">T-05 (XSS)</div>
                  <div class="mono text-[9px] bg-amber-50 text-amber-800 rounded px-1 py-0.5 border border-amber-300 font-bold" title="Polyglot Image Upload">T-07 (File)</div>
                </div>
              </div>

            </div>
          </div>
          <div class="text-[10px] text-slate-500 pt-1 flex justify-between items-center">
            <span>Kode Risiko: <span class="text-rose-700 font-bold">Merah = Critical (Skor &ge;40)</span> | <span class="text-amber-700 font-bold">Kuning = High (Skor 30–39)</span></span>
            <span class="mono text-blue-700 font-semibold text-[9.5px]">End-to-End Mapped</span>
          </div>
        </div>

      </div>

      <!-- ROW 2: DFD Level-1 & Trust Boundaries Diagram (Height: ~1015px) -->
      <div class="card-box p-3.5 flex flex-col justify-between flex-1 overflow-hidden">
        <div class="flex items-center justify-between pb-1.5 border-b border-slate-200 shrink-0">
          <span class="font-bold text-slate-900 flex items-center gap-1.5 text-xs">
            <svg class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1.5 3 3.5 3h9c2 0 3.5-1 3.5-3V7c0-2-1.5-3-3.5-3h-9C5.5 4 4 5 4 7z"/></svg>
            3. Data Flow Diagram (DFD Level-1) &amp; 5 Trust Boundaries
          </span>
          <div class="flex items-center gap-3 text-[10.5px]">
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-rose-500"></span> TB-1 Public</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span> TB-2 Ingress</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span> TB-3 Core App</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-purple-500"></span> TB-4 Daemon</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> TB-5 Storage</span>
          </div>
        </div>

        <!-- SVG DFD Container (Crisp White Background) -->
        <div class="w-full flex-1 flex items-center justify-center p-1 my-1 bg-white rounded-lg border border-slate-200 shadow-inner overflow-hidden">
          {svg_clean}
        </div>

        <!-- Legend Bar Compact matching dfd_threat_modeling copy.html -->
        <div class="pt-1.5 border-t border-slate-200 flex items-center justify-between text-[10px] text-slate-600 shrink-0">
          <div class="flex items-center gap-4">
            <span class="flex items-center gap-1"><span class="w-3.5 h-2.5 rounded border border-rose-600 bg-white inline-block"></span> <strong>[ ]</strong> Entitas Luar</span>
            <span class="flex items-center gap-1"><span class="w-3.5 h-2.5 rounded-md border border-blue-600 bg-blue-50 inline-block"></span> <strong>( )</strong> Proses / Controller</span>
            <span class="flex items-center gap-1"><span class="w-3.5 h-2.5 border border-emerald-600 bg-emerald-50 inline-block"></span> <strong>[=]</strong> Data Store (MySQL/Disk)</span>
            <span class="flex items-center gap-1"><span class="w-4 h-0.5 border-b-2 border-dashed border-rose-500 inline-block"></span> Trust Boundary</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="mono bg-rose-50 text-rose-800 border border-rose-300 px-1.5 py-0.5 rounded font-bold">[T-x] Titik Ancaman</span>
            <span class="mono bg-blue-50 text-blue-800 border border-blue-300 px-1.5 py-0.5 rounded font-bold">F1–F10 Aliran Data</span>
          </div>
        </div>
      </div>

    </div>


    <!-- ====================================================== -->
    <!-- RIGHT COLUMN (Cols: 5 / 12) - Metrics & Threat Matrix  -->
    <!-- ====================================================== -->
    <div class="col-span-5 flex flex-col justify-between gap-3 h-full overflow-hidden">
      
      <!-- ==================================================== -->
      <!-- BAGIAN 4: RINGKASAN HASIL & METRIK STRIDE-DREAD      -->
      <!-- ==================================================== -->
      <div class="card-box p-3.5 flex flex-col justify-between shrink-0" style="height: 220px;">
        <div class="flex items-center justify-between pb-1.5 border-b border-slate-200">
          <span class="font-bold text-slate-900 flex items-center gap-1.5 text-xs">
            <svg class="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            4. Ringkasan Hasil &amp; Metrik Evaluasi Risiko (Sheet Ringkasan)
          </span>
          <span class="mono text-[10px] bg-slate-100 text-slate-700 border border-slate-300 px-1.5 py-0.5 rounded font-bold">Rata-rata: {avg_dread} / 50</span>
        </div>

        <div class="grid grid-cols-12 gap-3 items-center my-auto">
          <!-- Risk Distribution Progress (Cols: 5) -->
          <div class="col-span-5 space-y-1.5 text-xs">
            <div>
              <div class="flex justify-between text-[11px] mb-0.5">
                <span class="text-rose-700 font-bold flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full bg-rose-600"></span> CRITICAL (40–50)
                </span>
                <span class="mono font-extrabold text-rose-800">{critical_count} (20%)</span>
              </div>
              <div class="w-full bg-slate-100 border border-slate-200 h-2 rounded-full overflow-hidden">
                <div class="bg-rose-600 h-full rounded-full" style="width: 20%"></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-[11px] mb-0.5">
                <span class="text-amber-700 font-bold flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full bg-amber-500"></span> HIGH (30–39)
                </span>
                <span class="mono font-extrabold text-amber-800">{high_count} (70%)</span>
              </div>
              <div class="w-full bg-slate-100 border border-slate-200 h-2 rounded-full overflow-hidden">
                <div class="bg-amber-500 h-full rounded-full" style="width: 70%"></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-[11px] mb-0.5">
                <span class="text-emerald-700 font-bold flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full bg-emerald-600"></span> LOW / MITIGATED (&lt;20)
                </span>
                <span class="mono font-extrabold text-emerald-800">{low_count} (10%)</span>
              </div>
              <div class="w-full bg-slate-100 border border-slate-200 h-2 rounded-full overflow-hidden">
                <div class="bg-emerald-600 h-full rounded-full" style="width: 10%"></div>
              </div>
            </div>
          </div>

          <!-- STRIDE Badges Grid (Cols: 7) -->
          <div class="col-span-7 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
            <span class="text-[10px] text-slate-600 block mb-1.5 font-semibold uppercase tracking-wider">Distribusi Kategori STRIDE:</span>
            <div class="grid grid-cols-3 gap-1.5 text-[10.5px]">
              <div class="bg-white px-2 py-1 rounded flex justify-between border border-slate-200 shadow-sm">
                <span class="text-slate-600">Tamper</span>
                <span class="mono font-bold text-blue-700">{stride_counts['Tamper (T)']}</span>
              </div>
              <div class="bg-white px-2 py-1 rounded flex justify-between border border-slate-200 shadow-sm">
                <span class="text-slate-600">Info</span>
                <span class="mono font-bold text-blue-700">{stride_counts['Info (I)']}</span>
              </div>
              <div class="bg-white px-2 py-1 rounded flex justify-between border border-slate-200 shadow-sm">
                <span class="text-slate-600">Spoof</span>
                <span class="mono font-bold text-blue-700">{stride_counts['Spoof (S)']}</span>
              </div>
              <div class="bg-white px-2 py-1 rounded flex justify-between border border-slate-200 shadow-sm">
                <span class="text-slate-600">DoS</span>
                <span class="mono font-bold text-blue-700">{stride_counts['DoS (D)']}</span>
              </div>
              <div class="bg-white px-2 py-1 rounded flex justify-between border border-slate-200 shadow-sm">
                <span class="text-slate-600">Elevate</span>
                <span class="mono font-bold text-blue-700">{stride_counts['Elevate (E)']}</span>
              </div>
              <div class="bg-white px-2 py-1 rounded flex justify-between border border-slate-200 shadow-sm">
                <span class="text-slate-400">Repudi</span>
                <span class="mono font-bold text-slate-400">{stride_counts['Repudi (R)']}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="pt-1.5 border-t border-slate-200 flex items-center justify-between text-[10.5px]">
          <span class="text-slate-700">Prioritas 1: <strong class="text-rose-700">T-01 BOLA Booking (Skor 40)</strong> &bull; Prioritas 2: <strong class="text-rose-700">T-02 Reverb Socket DoS (Skor 40)</strong></span>
          <span class="text-emerald-800 font-bold bg-emerald-100 px-2 py-0.5 rounded border border-emerald-300">T-10 APP_DEBUG=false ✓</span>
        </div>
      </div>

      <!-- ==================================================== -->
      <!-- BAGIAN 5: DAFTAR LENGKAP 10 ANCAMAN & MITIGASI       -->
      <!-- ==================================================== -->
      <div class="card-box p-3.5 flex flex-col justify-between flex-1 overflow-hidden">
        <div class="flex items-center justify-between pb-1.5 border-b border-slate-200 shrink-0 mb-1.5">
          <span class="font-bold text-slate-900 flex items-center gap-1.5 text-xs">
            <svg class="w-4 h-4 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            5. Daftar Lengkap 10 Ancaman &amp; Rekomendasi Mitigasi (Sesuai Excel)
          </span>
          <span class="text-[10px] text-slate-500 font-medium">10 / 10 Terverifikasi Sesuai Sheet STRIDE_DREAD_Template</span>
        </div>

        <!-- 10 Verified Threat Rows with Correct Severity Badges & Colors -->
        <div class="space-y-1.5 overflow-hidden flex-1 flex flex-col justify-between">
"""

for t in threats:
    is_crit = (t['level'] == 'CRITICAL')
    is_low = (t['level'] == 'LOW')
    
    if is_crit:
        badge_bg = "bg-rose-100 text-rose-800 border-rose-300"
        border_accent = "border-l-4 border-l-rose-600"
        tag_bg = "bg-rose-50 text-rose-900 border-rose-200"
    elif is_low:
        badge_bg = "bg-emerald-100 text-emerald-800 border-emerald-300"
        border_accent = "border-l-4 border-l-emerald-600"
        tag_bg = "bg-emerald-50 text-emerald-900 border-emerald-200"
    else: # HIGH
        badge_bg = "bg-amber-100 text-amber-800 border-amber-300"
        border_accent = "border-l-4 border-l-amber-500"
        tag_bg = "bg-amber-50 text-amber-900 border-amber-200"
        
    stride_str = ",".join(t['stride'])
    
    # short desc
    short_desc = t['desc']
    if len(short_desc) > 110:
        short_desc = short_desc[:110] + "..."
        
    short_mitigasi = t['mitigasi']
    if len(short_mitigasi) > 125:
        short_mitigasi = short_mitigasi[:125] + "..."

    short_bukti = t['bukti']
    if len(short_bukti) > 42:
        short_bukti = short_bukti[:42] + "..."

    html_4x3 += f"""
          <div class="p-2 rounded-lg border bg-white {border_accent} border-slate-200 shadow-sm flex flex-col justify-between text-xs" style="height: 87px;">
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center gap-1.5 overflow-hidden">
                <span class="mono font-bold text-slate-900 text-[11px] bg-slate-100 border border-slate-300 px-1.5 py-0.5 rounded shrink-0">{t['id']}</span>
                <span class="mono text-[9px] bg-blue-50 text-blue-800 border border-blue-200 px-1.5 py-0.5 rounded shrink-0 font-bold">{stride_str}</span>
                <span class="font-bold text-slate-900 text-[11px] truncate" title="{t['desc']}">{short_desc}</span>
              </div>
              <div class="shrink-0 flex items-center gap-1.5">
                <span class="mono font-extrabold text-[10px] text-slate-800 bg-slate-100 border border-slate-300 px-1.5 py-0.5 rounded">{t['total']}/50</span>
                <span class="mono font-black text-[9px] px-2 py-0.5 rounded border {badge_bg}">{t['level']}</span>
              </div>
            </div>

            <div class="grid grid-cols-12 gap-2 text-[10px] mt-1 items-center">
              <div class="col-span-5 truncate text-slate-600" title="{t['bukti']}">
                <span class="text-slate-500 font-semibold">Bukti:</span> <code class="mono text-rose-700 bg-slate-100 border border-slate-200 px-1 rounded font-semibold">{short_bukti}</code>
              </div>
              <div class="col-span-7 truncate text-slate-700" title="{t['mitigasi']}">
                <span class="text-emerald-700 font-bold">Solusi:</span> {short_mitigasi}
              </div>
            </div>
          </div>
    """

html_4x3 += f"""
        </div>

        <!-- ROW 3: Strategic Roadmap Strip (Height: ~92px) -->
        <div class="mt-2 pt-2 border-t border-slate-200 grid grid-cols-3 gap-2 text-[10px] shrink-0">
          <div class="p-2 rounded-lg bg-rose-50 border border-rose-200">
            <div class="font-bold text-rose-800 mb-0.5 uppercase tracking-wide flex items-center justify-between">
              <span>Fase 1: Segera (&lt;48 Jam)</span>
              <span class="mono font-black text-[9px] bg-rose-200 px-1 rounded">HOTFIX</span>
            </div>
            <p class="text-slate-700 leading-tight">Un-comment auth check <code class="text-rose-800 font-semibold">BookingController:230</code> (T-01) &amp; amankan route <code class="text-rose-800 font-semibold">/api/test-latency</code> (T-02).</p>
          </div>
          <div class="p-2 rounded-lg bg-amber-50 border border-amber-200">
            <div class="font-bold text-amber-800 mb-0.5 uppercase tracking-wide flex items-center justify-between">
              <span>Fase 2: Hardening (1–2 Minggu)</span>
              <span class="mono font-black text-[9px] bg-amber-200 px-1 rounded">CONFIG</span>
            </div>
            <p class="text-slate-700 leading-tight">Set <code class="text-amber-800 font-semibold">SESSION_ENCRYPT=true</code> (T-08), hapus 'role' dari fillable User (T-06), &amp; sanitasi XSS (T-05).</p>
          </div>
          <div class="p-2 rounded-lg bg-blue-50 border border-blue-200">
            <div class="font-bold text-blue-800 mb-0.5 uppercase tracking-wide flex items-center justify-between">
              <span>Fase 3: Arsitektur (1 Bulan)</span>
              <span class="mono font-black text-[9px] bg-blue-200 px-1 rounded">DEFENSE</span>
            </div>
            <p class="text-slate-700 leading-tight">Pasang Redis cache untuk Haversine (T-04), re-encode WebP image (T-07), &amp; pasang Cloudflare WAF.</p>
          </div>
        </div>

      </div>

    </div>

  </div>

  <!-- ======================================================== -->
  <!-- FOOTER (Height: ~26px)                                   -->
  <!-- ======================================================== -->
  <footer class="card-box px-4 py-1.5 flex items-center justify-between text-[10.5px] text-slate-500 shadow-sm shrink-0">
    <div class="flex items-center gap-2">
      <span class="inline-block w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
      <span>FindServices Security Audit Report &bull; Data Source: <strong class="text-slate-700">1. template_baru_Praktikum_STRIDE-DREAD.xlsx</strong></span>
    </div>
    <div class="flex items-center gap-4">
      <span>Theme: <strong class="text-blue-700 font-bold">Light Mode</strong></span>
      <span>Rasio Gambar: <strong class="text-blue-700 mono font-bold">4:3 (1920 &times; 1440)</strong></span>
      <span>&copy; 2026 Praktikum Keamanan Sistem Informasi</span>
    </div>
  </footer>

</body>
</html>
"""

output_path = r'c:\laragon\www\FindServices\keamanan_sistem_informasi\infografik_threat_modeling_4x3.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_4x3)

print("Light Theme 4:3 Infographic generated successfully.")
