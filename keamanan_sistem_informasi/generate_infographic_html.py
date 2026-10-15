import openpyxl
import json
import os

xlsx_path = r'c:\laragon\www\FindServices\keamanan_sistem_informasi\1. template_baru_Praktikum_STRIDE-DREAD.xlsx'
output_html_path = r'c:\laragon\www\FindServices\keamanan_sistem_informasi\infografik_threat_modeling.html'

wb = openpyxl.load_workbook(xlsx_path, data_only=True)

# 1. Read Profil_Aplikasi
ws_p = wb['Profil_Aplikasi']
sys_profile = {
    'nama': ws_p['B5'].value or 'FindServices',
    'tujuan': ws_p['B6'].value or '',
    'teknologi': ws_p['B7'].value or '',
    'cara_kerja': ws_p['B8'].value or '',
    'ruang_lingkup': ws_p['B9'].value or ''
}

komponen = []
for r in range(15, 25):
    kid = ws_p[f'B{r}'].value
    if kid:
        komponen.append({
            'id': kid,
            'nama': ws_p[f'C{r}'].value,
            'tipe': ws_p[f'D{r}'].value,
            'desc': ws_p[f'E{r}'].value
        })

aliran_data = []
for r in range(30, 40):
    fid = ws_p[f'B{r}'].value
    if fid:
        aliran_data.append({
            'id': fid,
            'sumber': ws_p[f'C{r}'].value,
            'tujuan': ws_p[f'D{r}'].value,
            'data': ws_p[f'E{r}'].value
        })

trust_boundaries = []
for r in range(45, 50):
    tbid = ws_p[f'B{r}'].value
    if tbid:
        trust_boundaries.append({
            'id': tbid,
            'desc': ws_p[f'C{r}'].value
        })

# 2. Read STRIDE_DREAD_Template
ws_t = wb['STRIDE_DREAD_Template']
threats = []
for r in range(5, 45):
    tid = ws_t[f'B{r}'].value
    if not tid:
        continue
    
    stride = []
    if ws_t[f'D{r}'].value: stride.append('S')
    if ws_t[f'E{r}'].value: stride.append('T')
    if ws_t[f'F{r}'].value: stride.append('R')
    if ws_t[f'G{r}'].value: stride.append('I')
    if ws_t[f'H{r}'].value: stride.append('D')
    if ws_t[f'I{r}'].value: stride.append('E')

    d_d = int(ws_t[f'K{r}'].value or 0)
    d_r = int(ws_t[f'L{r}'].value or 0)
    d_e = int(ws_t[f'M{r}'].value or 0)
    d_a = int(ws_t[f'N{r}'].value or 0)
    d_x = int(ws_t[f'O{r}'].value or 0)
    total = int(ws_t[f'P{r}'].value or (d_d + d_r + d_e + d_a + d_x))
    level = str(ws_t[f'Q{r}'].value or 'MEDIUM').strip()
    
    threats.append({
        'id': tid,
        'desc': ws_t[f'C{r}'].value or '',
        'stride': stride,
        'dread': {'D': d_d, 'R': d_r, 'E': d_e, 'A': d_a, 'X': d_x},
        'total': total,
        'level': level,
        'alasan': ws_t[f'S{r}'].value or '',
        'bukti': ws_t[f'T{r}'].value or '',
        'mitigasi': ws_t[f'U{r}'].value or ''
    })

# Summary stats
critical_count = sum(1 for t in threats if t['level'] == 'CRITICAL')
high_count = sum(1 for t in threats if t['level'] == 'HIGH')
medium_count = sum(1 for t in threats if t['level'] == 'MEDIUM')
low_count = sum(1 for t in threats if t['level'] == 'LOW')
avg_dread = round(sum(t['total'] for t in threats) / len(threats), 1) if threats else 0

stride_counts = {
    'Spoofing': sum(1 for t in threats if 'S' in t['stride']),
    'Tampering': sum(1 for t in threats if 'T' in t['stride']),
    'Repudiation': sum(1 for t in threats if 'R' in t['stride']),
    'Information Disclosure': sum(1 for t in threats if 'I' in t['stride']),
    'Denial of Service': sum(1 for t in threats if 'D' in t['stride']),
    'Elevation of Privilege': sum(1 for t in threats if 'E' in t['stride']),
}

print(f"Loaded {len(threats)} threats. Critical: {critical_count}, High: {high_count}, Low: {low_count}, Avg: {avg_dread}")

html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infografik Threat Modeling FindServices - STRIDE &amp; DREAD</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: #0b0f19;
      color: #f1f5f9;
    }}
    .mono {{
      font-family: 'JetBrains Mono', monospace;
    }}
    @media print {{
      body {{ background: #ffffff; color: #000000; }}
      .no-print {{ display: none !important; }}
      .page-break {{ page-break-before: always; }}
    }}
    .glass {{
      background: rgba(17, 24, 39, 0.75);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }}
    .glass-card {{
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }}
    .glow-cyan {{
      box-shadow: 0 0 25px -5px rgba(6, 182, 212, 0.25);
    }}
    .glow-rose {{
      box-shadow: 0 0 25px -5px rgba(244, 63, 94, 0.25);
    }}
    .gradient-text {{
      background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
  </style>
</head>
<body class="antialiased min-h-screen selection:bg-cyan-500 selection:text-white">

  <!-- Top Announcement Bar / Meta -->
  <div class="border-b border-slate-800 bg-slate-950/80 px-6 py-2.5 text-xs text-slate-400 flex flex-wrap items-center justify-between gap-3 sticky top-0 z-50 backdrop-blur-md">
    <div class="flex items-center gap-2">
      <span class="inline-block w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
      <span class="font-semibold text-slate-200">FINDSERVICES THREAT MODELING INTELLIGENCE</span>
      <span class="text-slate-600">|</span>
      <span>Praktikum Keamanan Sistem Informasi</span>
    </div>
    <div class="flex items-center gap-4">
      <span class="mono bg-slate-800 text-cyan-400 px-2 py-0.5 rounded text-[11px]">Metodologi: STRIDE + DREAD</span>
      <span class="mono bg-slate-800 text-slate-300 px-2 py-0.5 rounded text-[11px]">Target: Laravel 12.x</span>
      <button onclick="window.print()" class="no-print bg-cyan-600 hover:bg-cyan-500 text-white px-3 py-1 rounded text-xs font-semibold transition flex items-center gap-1.5 shadow-sm">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/></svg>
        Cetak / Simpan PDF
      </button>
    </div>
  </div>

  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">

    <!-- HERO HEADER -->
    <header class="glass rounded-2xl p-8 sm:p-10 border border-slate-800 relative overflow-hidden glow-cyan">
      <div class="absolute -top-24 -right-24 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute -bottom-24 -left-24 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>
      
      <div class="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div class="space-y-3 max-w-3xl">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800/60 text-cyan-400 text-xs font-medium">
            <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
            Laporan Analisis Ancaman &amp; Pemetaan Keamanan Sistem
          </div>
          <h1 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight">
            INFOGRAFIK <span class="gradient-text">THREAT MODELING</span>
          </h1>
          <p class="text-slate-300 text-base sm:text-lg leading-relaxed">
            Pemetaan komprehensif profil sistem, DFD 5-Trust Boundaries, simulasi alur kerja pengguna, metrik risiko STRIDE-DREAD, serta katalog mitigasi teknis untuk repositori <span class="text-cyan-300 font-semibold">FindServices</span>.
          </p>
        </div>

        <!-- Quick KPI Box -->
        <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-2 gap-3 lg:w-72 shrink-0">
          <div class="glass-card p-3.5 rounded-xl border border-rose-500/30 bg-rose-950/20">
            <div class="text-xs font-semibold text-rose-400 uppercase tracking-wider">Critical</div>
            <div class="text-2xl font-black text-rose-300 mt-1">{critical_count} <span class="text-xs font-normal text-slate-400">Ancaman</span></div>
          </div>
          <div class="glass-card p-3.5 rounded-xl border border-amber-500/30 bg-amber-950/20">
            <div class="text-xs font-semibold text-amber-400 uppercase tracking-wider">High Risk</div>
            <div class="text-2xl font-black text-amber-300 mt-1">{high_count} <span class="text-xs font-normal text-slate-400">Ancaman</span></div>
          </div>
          <div class="glass-card p-3.5 rounded-xl border border-emerald-500/30 bg-emerald-950/20">
            <div class="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Mitigated</div>
            <div class="text-2xl font-black text-emerald-300 mt-1">{low_count} <span class="text-xs font-normal text-slate-400">Low</span></div>
          </div>
          <div class="glass-card p-3.5 rounded-xl border border-cyan-500/30 bg-cyan-950/20">
            <div class="text-xs font-semibold text-cyan-400 uppercase tracking-wider">Avg DREAD</div>
            <div class="text-2xl font-black text-cyan-300 mt-1">{avg_dread} <span class="text-xs font-normal text-slate-400">/ 50</span></div>
          </div>
        </div>
      </div>
    </header>


    <!-- ============================================================ -->
    <!-- BAGIAN 1: RINGKASAN SISTEM                                    -->
    <!-- ============================================================ -->
    <section class="space-y-5">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-cyan-500/20 border border-cyan-500/40 text-cyan-400 font-bold flex items-center justify-center text-sm shadow-sm">01</div>
        <div>
          <h2 class="text-2xl font-bold tracking-tight text-white">Ringkasan Sistem &amp; Profil Arsitektur</h2>
          <p class="text-xs sm:text-sm text-slate-400">Karakteristik target aplikasi, profil aktor, tumpukan teknologi, dan ruang lingkup audit</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        <!-- Card 1: Identitas & Tujuan -->
        <div class="glass-card rounded-xl p-6 space-y-4 border border-slate-800">
          <div class="flex items-center gap-3">
            <div class="p-2.5 rounded-lg bg-blue-500/20 text-blue-400">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
            </div>
            <h3 class="font-bold text-slate-100 text-base">Identitas &amp; Tujuan Platform</h3>
          </div>
          <p class="text-sm text-slate-300 leading-relaxed">
            <strong class="text-cyan-300 font-semibold">FindServices</strong> adalah platform marketplace berbasis web yang memfasilitasi pencarian dan pemesanan penyedia jasa lokal (tukang/teknisi) terdekat.
          </p>
          <div class="space-y-2 pt-2 border-t border-slate-800/80 text-xs">
            <div class="flex justify-between">
              <span class="text-slate-400">Fitur Utama:</span>
              <span class="text-slate-200 font-medium">Haversine GPS, Chat Socket, Midtrans</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Basis Jarak:</span>
              <span class="text-slate-200 font-medium">Radius Koordinat Latitude / Longitude</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Tipe Transaksi:</span>
              <span class="text-slate-200 font-medium">Escrow Digital (Snap) &amp; Tunai (COD)</span>
            </div>
          </div>
        </div>

        <!-- Card 2: Stack Teknologi -->
        <div class="glass-card rounded-xl p-6 space-y-4 border border-slate-800">
          <div class="flex items-center gap-3">
            <div class="p-2.5 rounded-lg bg-cyan-500/20 text-cyan-400">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg>
            </div>
            <h3 class="font-bold text-slate-100 text-base">Stack Teknologi Terverifikasi</h3>
          </div>
          <div class="grid grid-cols-2 gap-2.5 text-xs">
            <div class="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
              <span class="text-slate-400 block text-[11px]">Backend Framework</span>
              <span class="text-cyan-300 font-semibold">Laravel 12 (PHP 8.3)</span>
            </div>
            <div class="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
              <span class="text-slate-400 block text-[11px]">Frontend Stack</span>
              <span class="text-emerald-300 font-semibold">Vue 3 + Inertia.js</span>
            </div>
            <div class="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
              <span class="text-slate-400 block text-[11px]">Database Utama</span>
              <span class="text-amber-300 font-semibold">MySQL 8.0 Engine</span>
            </div>
            <div class="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
              <span class="text-slate-400 block text-[11px]">Real-time Engine</span>
              <span class="text-purple-300 font-semibold">Laravel Reverb :8080</span>
            </div>
            <div class="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
              <span class="text-slate-400 block text-[11px]">Payment Gateway</span>
              <span class="text-rose-300 font-semibold">Midtrans Snap API</span>
            </div>
            <div class="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
              <span class="text-slate-400 block text-[11px]">Ingress / Tunnel</span>
              <span class="text-indigo-300 font-semibold">Cloudflare Tunnel</span>
            </div>
          </div>
        </div>

        <!-- Card 3: Actors & Scope -->
        <div class="glass-card rounded-xl p-6 space-y-4 border border-slate-800">
          <div class="flex items-center gap-3">
            <div class="p-2.5 rounded-lg bg-purple-500/20 text-purple-400">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
            </div>
            <h3 class="font-bold text-slate-100 text-base">Aktor Pengguna &amp; Batasan Ruang Lingkup</h3>
          </div>
          <div class="space-y-2 text-xs">
            <div class="flex items-start gap-2">
              <span class="mono px-1.5 py-0.5 rounded bg-blue-900/60 text-blue-300 text-[10px]">CUSTOMER</span>
              <span class="text-slate-300">Pencari jasa, membuat booking, bayar, rating review.</span>
            </div>
            <div class="flex items-start gap-2">
              <span class="mono px-1.5 py-0.5 rounded bg-emerald-900/60 text-emerald-300 text-[10px]">PROVIDER</span>
              <span class="text-slate-300">Penyedia jasa, verifikasi order, negosiasi harga, eksekusi.</span>
            </div>
            <div class="flex items-start gap-2">
              <span class="mono px-1.5 py-0.5 rounded bg-rose-900/60 text-rose-300 text-[10px]">ADMIN</span>
              <span class="text-slate-300">Pengelola master data kategori, resolusi dispute &amp; audit.</span>
            </div>
          </div>
          <div class="pt-2 border-t border-slate-800 text-[11px] text-slate-400">
            <span class="font-semibold text-slate-200">Ruang Lingkup:</span> Static code review, audit konfigurasi environment (.env), dan threat modeling non-destruktif.
          </div>
        </div>
      </div>

      <!-- 10 Komponen Terpetakan -->
      <div class="glass-card rounded-xl p-5 border border-slate-800 space-y-3">
        <h4 class="text-sm font-bold text-slate-200 flex items-center gap-2">
          <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>
          Inventarisasi 10 Komponen Sistem Kunci (K-01 s/d K-10)
        </h4>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5 text-xs">
          {"".join(f'''<div class="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 transition">
            <div class="flex items-center justify-between mb-1">
              <span class="mono font-bold text-cyan-400">{k['id']}</span>
              <span class="text-[10px] text-slate-500 uppercase">{k['tipe'][:12]}</span>
            </div>
            <div class="font-semibold text-slate-200 truncate" title="{k['nama']}">{k['nama']}</div>
            <div class="text-[11px] text-slate-400 mt-0.5 line-clamp-2" title="{k['desc']}">{k['desc']}</div>
          </div>''' for k in komponen)}
        </div>
      </div>
    </section>


    <!-- ============================================================ -->
    <!-- BAGIAN 2: DIAGRAM ALUR KERJA (WORKFLOW & TOUCHPOINTS)        -->
    <!-- ============================================================ -->
    <section class="space-y-5">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-purple-500/20 border border-purple-500/40 text-purple-400 font-bold flex items-center justify-center text-sm shadow-sm">02</div>
        <div>
          <h2 class="text-2xl font-bold tracking-tight text-white">Diagram Alur Kerja &amp; Titik Rawan Keamanan</h2>
          <p class="text-xs sm:text-sm text-slate-400">User journey dari pencarian hingga penyelesaian layanan dengan penanda potensi ancaman (Touchpoints)</p>
        </div>
      </div>

      <!-- Workflow Timeline / Steps -->
      <div class="grid grid-cols-1 md:grid-cols-5 gap-3.5">
        
        <!-- Step 1 -->
        <div class="glass-card rounded-xl p-5 border border-slate-800 flex flex-col justify-between relative group hover:border-cyan-500/50 transition">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="mono w-7 h-7 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800/60 font-bold flex items-center justify-center text-xs">1</span>
              <span class="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Discovery</span>
            </div>
            <h4 class="font-bold text-slate-100 text-sm">Pencarian &amp; Otentikasi</h4>
            <p class="text-xs text-slate-300 leading-relaxed">
              Customer login, mencari jasa terdekat berbasis koordinat geolokasi (Haversine formula).
            </p>
          </div>
          <div class="mt-4 pt-3 border-t border-slate-800/80 space-y-1.5">
            <span class="text-[10px] uppercase font-bold text-rose-400 flex items-center gap-1">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>
              Titik Rawan (Threat):
            </span>
            <div class="flex flex-wrap gap-1">
              <span class="mono px-1.5 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800/50 text-[10px]" title="DoS Haversine Query">T-04 (DoS)</span>
              <span class="mono px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800/50 text-[10px]" title="Plaintext Session">T-08 (Session)</span>
            </div>
          </div>
        </div>

        <!-- Step 2 -->
        <div class="glass-card rounded-xl p-5 border border-slate-800 flex flex-col justify-between relative group hover:border-cyan-500/50 transition">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="mono w-7 h-7 rounded-lg bg-blue-950 text-blue-400 border border-blue-800/60 font-bold flex items-center justify-center text-xs">2</span>
              <span class="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Booking</span>
            </div>
            <h4 class="font-bold text-slate-100 text-sm">Pemesanan &amp; Penawaran</h4>
            <p class="text-xs text-slate-300 leading-relaxed">
              Customer membuat order pesanan. Provider mereview, menyepakati harga final, dan konfirmasi.
            </p>
          </div>
          <div class="mt-4 pt-3 border-t border-slate-800/80 space-y-1.5">
            <span class="text-[10px] uppercase font-bold text-rose-400 flex items-center gap-1">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>
              Titik Rawan (Threat):
            </span>
            <div class="flex flex-wrap gap-1">
              <span class="mono px-1.5 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800/50 text-[10px] font-bold" title="BOLA / IDOR Status Booking">T-01 (IDOR)</span>
              <span class="mono px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800/50 text-[10px]" title="Mass Assignment Role Admin">T-06 (Privilege)</span>
            </div>
          </div>
        </div>

        <!-- Step 3 -->
        <div class="glass-card rounded-xl p-5 border border-slate-800 flex flex-col justify-between relative group hover:border-cyan-500/50 transition">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="mono w-7 h-7 rounded-lg bg-emerald-950 text-emerald-400 border border-emerald-800/60 font-bold flex items-center justify-center text-xs">3</span>
              <span class="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Payment</span>
            </div>
            <h4 class="font-bold text-slate-100 text-sm">Pembayaran &amp; Escrow</h4>
            <p class="text-xs text-slate-300 leading-relaxed">
              Customer membayar via Midtrans Snap. Sistem menunggu callback webhook untuk validasi lunas.
            </p>
          </div>
          <div class="mt-4 pt-3 border-t border-slate-800/80 space-y-1.5">
            <span class="text-[10px] uppercase font-bold text-rose-400 flex items-center gap-1">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>
              Titik Rawan (Threat):
            </span>
            <div class="flex flex-wrap gap-1">
              <span class="mono px-1.5 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800/50 text-[10px]" title="Webhook Signature Forgery">T-03 (Webhook)</span>
            </div>
          </div>
        </div>

        <!-- Step 4 -->
        <div class="glass-card rounded-xl p-5 border border-slate-800 flex flex-col justify-between relative group hover:border-cyan-500/50 transition">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="mono w-7 h-7 rounded-lg bg-purple-950 text-purple-400 border border-purple-800/60 font-bold flex items-center justify-center text-xs">4</span>
              <span class="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Realtime</span>
            </div>
            <h4 class="font-bold text-slate-100 text-sm">Komunikasi &amp; Pengerjaan</h4>
            <p class="text-xs text-slate-300 leading-relaxed">
              Provider &amp; Customer berinteraksi via chat WebSocket Laravel Reverb hingga pekerjaan selesai.
            </p>
          </div>
          <div class="mt-4 pt-3 border-t border-slate-800/80 space-y-1.5">
            <span class="text-[10px] uppercase font-bold text-rose-400 flex items-center gap-1">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>
              Titik Rawan (Threat):
            </span>
            <div class="flex flex-wrap gap-1">
              <span class="mono px-1.5 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800/50 text-[10px] font-bold" title="Reverb WebSocket Flooding DoS">T-02 (DoS)</span>
              <span class="mono px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800/50 text-[10px]" title="Chat IDOR Hashids Tampering">T-09 (Hashids)</span>
            </div>
          </div>
        </div>

        <!-- Step 5 -->
        <div class="glass-card rounded-xl p-5 border border-slate-800 flex flex-col justify-between relative group hover:border-cyan-500/50 transition">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="mono w-7 h-7 rounded-lg bg-amber-950 text-amber-400 border border-amber-800/60 font-bold flex items-center justify-center text-xs">5</span>
              <span class="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Completion</span>
            </div>
            <h4 class="font-bold text-slate-100 text-sm">Review, Rating &amp; Selesai</h4>
            <p class="text-xs text-slate-300 leading-relaxed">
              Customer mengonfirmasi selesai, memberikan ulasan review, rating, dan foto bukti pengerjaan.
            </p>
          </div>
          <div class="mt-4 pt-3 border-t border-slate-800/80 space-y-1.5">
            <span class="text-[10px] uppercase font-bold text-rose-400 flex items-center gap-1">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>
              Titik Rawan (Threat):
            </span>
            <div class="flex flex-wrap gap-1">
              <span class="mono px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800/50 text-[10px]" title="Stored XSS Review">T-05 (XSS)</span>
              <span class="mono px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800/50 text-[10px]" title="Polyglot Image Upload">T-07 (Upload)</span>
            </div>
          </div>
        </div>

      </div>
    </section>


    <!-- ============================================================ -->
    <!-- BAGIAN 3: DATA FLOW DIAGRAM (DFD) & 5 TRUST BOUNDARIES        -->
    <!-- ============================================================ -->
    <section class="space-y-5">
      <div class="flex items-center justify-between flex-wrap gap-4">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 font-bold flex items-center justify-center text-sm shadow-sm">03</div>
          <div>
            <h2 class="text-2xl font-bold tracking-tight text-white">Data Flow Diagram (DFD) &amp; Trust Boundaries</h2>
            <p class="text-xs sm:text-sm text-slate-400">Pemetaan relasional entitas, proses inti, data store, dan 5 batas kepercayaan (TB-1 s/d TB-5)</p>
          </div>
        </div>
        <div class="flex items-center gap-2 text-xs">
          <span class="inline-block w-3 h-3 rounded-full bg-rose-500/80"></span> <span class="text-slate-300">TB-1</span>
          <span class="inline-block w-3 h-3 rounded-full bg-amber-500/80 ml-2"></span> <span class="text-slate-300">TB-2</span>
          <span class="inline-block w-3 h-3 rounded-full bg-blue-500/80 ml-2"></span> <span class="text-slate-300">TB-3</span>
          <span class="inline-block w-3 h-3 rounded-full bg-purple-500/80 ml-2"></span> <span class="text-slate-300">TB-4</span>
          <span class="inline-block w-3 h-3 rounded-full bg-emerald-500/80 ml-2"></span> <span class="text-slate-300">TB-5</span>
        </div>
      </div>

      <!-- DFD Vector Graphic Container -->
      <div class="glass-card rounded-2xl p-4 sm:p-6 border border-slate-800 overflow-x-auto shadow-2xl">
        <svg viewBox="0 0 1340 760" class="w-full min-w-[1000px] h-auto" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#64748b" />
            </marker>
            <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#38bdf8" />
            </marker>
            <marker id="arrow-orange" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#fb923c" />
            </marker>
            <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#34d399" />
            </marker>
            <marker id="arrow-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#c084fc" />
            </marker>
          </defs>

          <!-- ============================================== -->
          <!-- TRUST BOUNDARIES (BACKGROUND CLUSTERS)         -->
          <!-- ============================================== -->

          <!-- TB 1: Untrusted Public Zone -->
          <rect x="20" y="20" width="310" height="720" rx="14" fill="#1e1014" stroke="#f43f5e" stroke-width="2" stroke-dasharray="6,4" fill-opacity="0.6"/>
          <rect x="35" y="32" width="280" height="26" rx="6" fill="#881337" stroke="#fb7185" stroke-width="1"/>
          <text x="175" y="49" text-anchor="middle" font-size="11" font-weight="700" fill="#fecdd3" font-family="'Plus Jakarta Sans', sans-serif">TB-1: Zona Eksternal (Untrusted Public)</text>

          <!-- TB 2: Network Perimeter & Ingress -->
          <rect x="350" y="20" width="220" height="720" rx="14" fill="#1c160c" stroke="#f59e0b" stroke-width="2" stroke-dasharray="6,4" fill-opacity="0.6"/>
          <rect x="365" y="32" width="190" height="26" rx="6" fill="#78350f" stroke="#fcd34d" stroke-width="1"/>
          <text x="460" y="49" text-anchor="middle" font-size="11" font-weight="700" fill="#fef3c7" font-family="'Plus Jakarta Sans', sans-serif">TB-2: Perimeter &amp; Ingress</text>

          <!-- TB 3: Core Application Logic -->
          <rect x="590" y="20" width="460" height="720" rx="14" fill="#0c172e" stroke="#3b82f6" stroke-width="2" stroke-dasharray="6,4" fill-opacity="0.6"/>
          <rect x="605" y="32" width="430" height="26" rx="6" fill="#1e3a8a" stroke="#93c5fd" stroke-width="1"/>
          <text x="820" y="49" text-anchor="middle" font-size="11" font-weight="700" fill="#dbeafe" font-family="'Plus Jakarta Sans', sans-serif">TB-3: Core Application (Laravel 12 / PHP 8.3)</text>

          <!-- TB 4: Internal Daemon & Local Storage -->
          <rect x="1070" y="20" width="250" height="350" rx="14" fill="#180e29" stroke="#a855f7" stroke-width="2" stroke-dasharray="6,4" fill-opacity="0.6"/>
          <rect x="1085" y="32" width="220" height="26" rx="6" fill="#581c87" stroke="#d8b4fe" stroke-width="1"/>
          <text x="1195" y="49" text-anchor="middle" font-size="11" font-weight="700" fill="#f3e8ff" font-family="'Plus Jakarta Sans', sans-serif">TB-4: Realtime Daemon &amp; Storage</text>

          <!-- TB 5: External Third-Party APIs -->
          <rect x="1070" y="390" width="250" height="350" rx="14" fill="#061c16" stroke="#10b981" stroke-width="2" stroke-dasharray="6,4" fill-opacity="0.6"/>
          <rect x="1085" y="402" width="220" height="26" rx="6" fill="#064e3b" stroke="#6ee7b7" stroke-width="1"/>
          <text x="1195" y="419" text-anchor="middle" font-size="11" font-weight="700" fill="#d1fae5" font-family="'Plus Jakarta Sans', sans-serif">TB-5: Layanan Pihak Ketiga</text>


          <!-- ============================================== -->
          <!-- ENTITAS EKSTERNAL (TB-1)                       -->
          <!-- ============================================== -->

          <!-- Pelanggan / Customer (K1) -->
          <rect x="50" y="90" width="250" height="85" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
          <text x="175" y="118" text-anchor="middle" font-size="13" font-weight="700" fill="#f8fafc">Pelanggan (Customer)</text>
          <text x="175" y="137" text-anchor="middle" font-size="11" fill="#94a3b8">Entitas: Web Browser / Vue 3</text>
          <rect x="65" y="148" width="85" height="18" rx="4" fill="#0369a1"/>
          <text x="107" y="161" text-anchor="middle" font-size="10" font-weight="600" fill="#e0f2fe">K1 Client</text>
          <rect x="160" y="148" width="125" height="18" rx="4" fill="#7f1d1d"/>
          <text x="222" y="161" text-anchor="middle" font-size="9" font-weight="700" fill="#fecaca">T-08 Session Sniff</text>

          <!-- Penyedia Jasa / Provider (K1) -->
          <rect x="50" y="220" width="250" height="85" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
          <text x="175" y="248" text-anchor="middle" font-size="13" font-weight="700" fill="#f8fafc">Penyedia Jasa (Provider)</text>
          <text x="175" y="267" text-anchor="middle" font-size="11" fill="#94a3b8">Entitas: Web Browser / Mitra</text>
          <rect x="65" y="278" width="85" height="18" rx="4" fill="#0369a1"/>
          <text x="107" y="291" text-anchor="middle" font-size="10" font-weight="600" fill="#e0f2fe">K1 Client</text>
          <rect x="160" y="278" width="125" height="18" rx="4" fill="#78350f"/>
          <text x="222" y="291" text-anchor="middle" font-size="9" font-weight="700" fill="#fef3c7">T-07 File Upload</text>

          <!-- Administrator (K1) -->
          <rect x="50" y="350" width="250" height="75" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
          <text x="175" y="378" text-anchor="middle" font-size="13" font-weight="700" fill="#f8fafc">Administrator Platform</text>
          <text x="175" y="397" text-anchor="middle" font-size="11" fill="#94a3b8">Entitas: Web Admin Dashboard</text>
          <rect x="90" y="405" width="170" height="16" rx="4" fill="#7f1d1d"/>
          <text x="175" y="417" text-anchor="middle" font-size="9" font-weight="700" fill="#fecaca">T-06 Role Escalation</text>

          <!-- Attacker / External Threat Box -->
          <rect x="50" y="460" width="250" height="250" rx="8" fill="#2d0b13" stroke="#f43f5e" stroke-width="2"/>
          <text x="175" y="488" text-anchor="middle" font-size="13" font-weight="800" fill="#fb7185">Penyerang / Penguji (Threat)</text>
          <text x="175" y="508" text-anchor="middle" font-size="10" fill="#fda4af">Vektor Serangan Teridentifikasi:</text>
          
          <rect x="65" y="520" width="220" height="24" rx="4" fill="#7f1d1d" stroke="#f43f5e" stroke-width="1"/>
          <text x="175" y="536" text-anchor="middle" font-size="10" font-weight="700" fill="#fff">T-01 BOLA Status Booking (40)</text>
          
          <rect x="65" y="552" width="220" height="24" rx="4" fill="#7f1d1d" stroke="#f43f5e" stroke-width="1"/>
          <text x="175" y="568" text-anchor="middle" font-size="10" font-weight="700" fill="#fff">T-02 Reverb Socket Flooding (40)</text>
          
          <rect x="65" y="584" width="220" height="24" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
          <text x="175" y="600" text-anchor="middle" font-size="10" font-weight="700" fill="#fef3c7">T-03 Webhook Callback Bypass (39)</text>
          
          <rect x="65" y="616" width="220" height="24" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
          <text x="175" y="632" text-anchor="middle" font-size="10" font-weight="700" fill="#fef3c7">T-04 DoS Haversine &amp; Upload (38)</text>
          
          <rect x="65" y="648" width="220" height="24" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
          <text x="175" y="664" text-anchor="middle" font-size="10" font-weight="700" fill="#fef3c7">T-05 Stored XSS Review Form (37)</text>

          <rect x="65" y="680" width="220" height="20" rx="4" fill="#064e3b" stroke="#10b981" stroke-width="1"/>
          <text x="175" y="694" text-anchor="middle" font-size="9" font-weight="700" fill="#a7f3d0">T-10 APP_DEBUG=false (Termitigasi)</text>


          <!-- ============================================== -->
          <!-- PERIMETER & INGRESS (TB-2)                     -->
          <!-- ============================================== -->

          <!-- Nginx Reverse Proxy (K2) -->
          <rect x="375" y="110" width="170" height="95" rx="10" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
          <text x="460" y="140" text-anchor="middle" font-size="13" font-weight="700" fill="#fef3c7">Nginx Web Server</text>
          <text x="460" y="160" text-anchor="middle" font-size="10" fill="#cbd5e1">Reverse Proxy / SSL</text>
          <text x="460" y="178" text-anchor="middle" font-size="10" font-weight="600" fill="#fcd34d">K2 Ingress Gateway</text>

          <!-- Cloudflare Tunnel (K8) -->
          <rect x="375" y="270" width="170" height="90" rx="10" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
          <text x="460" y="302" text-anchor="middle" font-size="13" font-weight="700" fill="#fef3c7">Cloudflare Tunnel</text>
          <text x="460" y="322" text-anchor="middle" font-size="10" fill="#cbd5e1">DNS / DDoS Shield</text>
          <text x="460" y="340" text-anchor="middle" font-size="10" font-weight="600" fill="#fcd34d">K8 Network Ingress</text>

          <!-- Session/Auth Subsystem (K9) -->
          <rect x="375" y="430" width="170" height="90" rx="10" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
          <text x="460" y="462" text-anchor="middle" font-size="13" font-weight="700" fill="#fef3c7">Auth &amp; Session</text>
          <text x="460" y="482" text-anchor="middle" font-size="10" fill="#cbd5e1">K9 Cookie &amp; Identity</text>
          <rect x="390" y="493" width="140" height="18" rx="4" fill="#78350f"/>
          <text x="460" y="506" text-anchor="middle" font-size="9" font-weight="700" fill="#fef3c7">T-08 Plaintext DB</text>


          <!-- ============================================== -->
          <!-- CORE APPLICATION LOGIC (TB-3)                  -->
          <!-- ============================================== -->

          <!-- Process 1: Booking Lifecycle (P1) -->
          <rect x="620" y="90" width="180" height="90" rx="12" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
          <text x="710" y="118" text-anchor="middle" font-size="12" font-weight="700" fill="#e2e8f0">1.0 Booking Lifecycle</text>
          <text x="710" y="136" text-anchor="middle" font-size="10" fill="#94a3b8">BookingController.php</text>
          <rect x="635" y="148" width="150" height="22" rx="4" fill="#7f1d1d" stroke="#f43f5e" stroke-width="1"/>
          <text x="710" y="163" text-anchor="middle" font-size="9" font-weight="800" fill="#fff">⚠️ T-01 BOLA (Skor 40)</text>

          <!-- Process 2: Marketplace & Search (P2) -->
          <rect x="840" y="90" width="180" height="90" rx="12" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
          <text x="930" y="118" text-anchor="middle" font-size="12" font-weight="700" fill="#e2e8f0">2.0 Search &amp; Catalog</text>
          <text x="930" y="136" text-anchor="middle" font-size="10" fill="#94a3b8">MarketplaceController.php</text>
          <rect x="855" y="148" width="150" height="22" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
          <text x="930" y="163" text-anchor="middle" font-size="9" font-weight="700" fill="#fef3c7">⚠️ T-04 Haversine DoS</text>

          <!-- Process 3: Chat Controller (P3) -->
          <rect x="620" y="240" width="180" height="90" rx="12" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
          <text x="710" y="268" text-anchor="middle" font-size="12" font-weight="700" fill="#e2e8f0">3.0 Chat &amp; Messaging</text>
          <text x="710" y="286" text-anchor="middle" font-size="10" fill="#94a3b8">ChatController.php</text>
          <rect x="635" y="298" width="150" height="22" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
          <text x="710" y="313" text-anchor="middle" font-size="9" font-weight="700" fill="#fef3c7">⚠️ T-09 Hashids Bypass</text>

          <!-- Process 4: Payment Controller (P4) -->
          <rect x="840" y="240" width="180" height="90" rx="12" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
          <text x="930" y="268" text-anchor="middle" font-size="12" font-weight="700" fill="#e2e8f0">4.0 Payment Handler</text>
          <text x="930" y="286" text-anchor="middle" font-size="10" fill="#94a3b8">PaymentCallback.php</text>
          <rect x="855" y="298" width="150" height="22" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
          <text x="930" y="313" text-anchor="middle" font-size="9" font-weight="700" fill="#fef3c7">⚠️ T-03 Webhook Replay</text>

          <!-- Process 5: Profile & Role Model (P5) -->
          <rect x="620" y="390" width="180" height="85" rx="12" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
          <text x="710" y="418" text-anchor="middle" font-size="12" font-weight="700" fill="#e2e8f0">5.0 User Profile Model</text>
          <text x="710" y="436" text-anchor="middle" font-size="10" fill="#94a3b8">app/Models/User.php</text>
          <rect x="635" y="445" width="150" height="20" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
          <text x="710" y="459" text-anchor="middle" font-size="9" font-weight="700" fill="#fef3c7">⚠️ T-06 Role Fillable</text>

          <!-- Process 6: Review & User Report (P6) -->
          <rect x="840" y="390" width="180" height="85" rx="12" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
          <text x="930" y="418" text-anchor="middle" font-size="12" font-weight="700" fill="#e2e8f0">6.0 Review &amp; Report</text>
          <text x="930" y="436" text-anchor="middle" font-size="10" fill="#94a3b8">UserReportController.php</text>
          <rect x="855" y="445" width="150" height="20" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
          <text x="930" y="459" text-anchor="middle" font-size="9" font-weight="700" fill="#fef3c7">⚠️ T-05 Stored XSS</text>

          <!-- DATA STORE 1: MySQL Database (D1 / K5) -->
          <g>
            <path d="M 640 540 C 640 528, 1000 528, 1000 540 L 1000 660 C 1000 672, 640 672, 640 660 Z" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
            <path d="M 640 540 C 640 552, 1000 552, 1000 540" fill="none" stroke="#38bdf8" stroke-width="2"/>
            <text x="820" y="580" text-anchor="middle" font-size="14" font-weight="800" fill="#38bdf8">D1: MySQL Database Server (K5)</text>
            <text x="820" y="605" text-anchor="middle" font-size="11" fill="#cbd5e1">Tabel: users, bookings, services, messages, payments, sessions</text>
            <rect x="670" y="620" width="140" height="20" rx="4" fill="#0369a1"/>
            <text x="740" y="634" text-anchor="middle" font-size="9" font-weight="600" fill="#e0f2fe">F4: SQL &amp; Eloquent</text>
            <rect x="830" y="620" width="140" height="20" rx="4" fill="#7f1d1d"/>
            <text x="900" y="634" text-anchor="middle" font-size="9" font-weight="700" fill="#fecaca">⚠️ T-08 Session Cleartext</text>
          </g>


          <!-- ============================================== -->
          <!-- DAEMON & LOCAL STORAGE (TB-4)                  -->
          <!-- ============================================== -->

          <!-- Laravel Reverb (K4) -->
          <rect x="1090" y="90" width="210" height="120" rx="10" fill="#1e293b" stroke="#c084fc" stroke-width="2"/>
          <text x="1195" y="118" text-anchor="middle" font-size="13" font-weight="700" fill="#f3e8ff">Laravel Reverb</text>
          <text x="1195" y="136" text-anchor="middle" font-size="10" fill="#d8b4fe">WebSocket Engine (:8080)</text>
          <text x="1195" y="154" text-anchor="middle" font-size="10" font-weight="600" fill="#c084fc">K4 Realtime Daemon</text>
          <rect x="1105" y="165" width="180" height="24" rx="4" fill="#7f1d1d" stroke="#f43f5e" stroke-width="1"/>
          <text x="1195" y="181" text-anchor="middle" font-size="9" font-weight="800" fill="#fff">⚠️ T-02 Flooding DoS (40)</text>

          <!-- DATA STORE 2: Local File Storage (D2 / K6) -->
          <g>
            <path d="M 1090 250 C 1090 240, 1300 240, 1300 250 L 1300 330 C 1300 340, 1090 340, 1090 330 Z" fill="#1e293b" stroke="#c084fc" stroke-width="2"/>
            <path d="M 1090 250 C 1090 260, 1300 260, 1300 250" fill="none" stroke="#c084fc" stroke-width="2"/>
            <text x="1195" y="280" text-anchor="middle" font-size="12" font-weight="700" fill="#f3e8ff">D2: Local Storage (K6)</text>
            <text x="1195" y="298" text-anchor="middle" font-size="10" fill="#d8b4fe">public/storage/uploads</text>
            <rect x="1115" y="307" width="160" height="18" rx="4" fill="#78350f"/>
            <text x="1195" y="320" text-anchor="middle" font-size="9" font-weight="700" fill="#fef3c7">⚠️ T-07 Polyglot Upload</text>
          </g>


          <!-- ============================================== -->
          <!-- THIRD PARTY SERVICES (TB-5)                    -->
          <!-- ============================================== -->

          <!-- Midtrans Gateway (K7) -->
          <rect x="1090" y="440" width="210" height="110" rx="10" fill="#1e293b" stroke="#34d399" stroke-width="2"/>
          <text x="1195" y="470" text-anchor="middle" font-size="13" font-weight="700" fill="#d1fae5">Midtrans Gateway</text>
          <text x="1195" y="490" text-anchor="middle" font-size="10" fill="#a7f3d0">Snap API &amp; Webhook</text>
          <text x="1195" y="508" text-anchor="middle" font-size="10" font-weight="600" fill="#34d399">K7 Payment Gateway</text>
          <rect x="1110" y="516" width="170" height="20" rx="4" fill="#78350f"/>
          <text x="1195" y="530" text-anchor="middle" font-size="9" font-weight="700" fill="#fef3c7">⚠️ T-03 Secret Key Empty</text>

          <!-- Google Maps API (K10) -->
          <rect x="1090" y="590" width="210" height="100" rx="10" fill="#1e293b" stroke="#34d399" stroke-width="2"/>
          <text x="1195" y="625" text-anchor="middle" font-size="13" font-weight="700" fill="#d1fae5">Google Maps API</text>
          <text x="1195" y="645" text-anchor="middle" font-size="10" fill="#a7f3d0">Maps SDK &amp; Reverse Geo</text>
          <text x="1195" y="663" text-anchor="middle" font-size="10" font-weight="600" fill="#34d399">K10 Map Subsystem</text>


          <!-- ============================================== -->
          <!-- ALIRAN DATA / FLOWS (F1 - F10)                 -->
          <!-- ============================================== -->

          <!-- F1: Browser -> Nginx -->
          <line x1="300" y1="135" x2="375" y2="135" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow-blue)"/>
          <rect x="308" y="118" width="55" height="15" rx="3" fill="#0c4a6e"/>
          <text x="335" y="129" text-anchor="middle" font-size="8.5" font-weight="700" fill="#bae6fd">F1 HTTP</text>

          <!-- F2: Nginx -> Laravel App -->
          <line x1="545" y1="135" x2="620" y2="135" stroke="#fb923c" stroke-width="2" marker-end="url(#arrow-orange)"/>
          <rect x="555" y="118" width="55" height="15" rx="3" fill="#7c2d12"/>
          <text x="582" y="129" text-anchor="middle" font-size="8.5" font-weight="700" fill="#fed7aa">F2 FCGI</text>

          <!-- F3: Browser -> Reverb WebSocket (Cross Boundary) -->
          <path d="M 300 160 C 420 200, 950 60, 1090 120" fill="none" stroke="#c084fc" stroke-width="2" stroke-dasharray="4,3" marker-end="url(#arrow-purple)"/>
          <rect x="560" y="70" width="55" height="15" rx="3" fill="#581c87"/>
          <text x="587" y="81" text-anchor="middle" font-size="8.5" font-weight="700" fill="#e9d5ff">F3 WSS</text>

          <!-- F4: Core App -> MySQL -->
          <line x1="710" y1="475" x2="710" y2="530" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow-blue)"/>
          <line x1="930" y1="475" x2="930" y2="530" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow-blue)"/>

          <!-- F5: Core App -> Local Storage -->
          <line x1="1020" y1="285" x2="1090" y2="285" stroke="#c084fc" stroke-width="2" marker-end="url(#arrow-purple)"/>
          <rect x="1030" y="268" width="50" height="15" rx="3" fill="#581c87"/>
          <text x="1055" y="279" text-anchor="middle" font-size="8.5" font-weight="700" fill="#e9d5ff">F5 File</text>

          <!-- F6: Payment Handler -> Midtrans API -->
          <line x1="1020" y1="310" x2="1090" y2="455" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
          <rect x="1028" y="380" width="55" height="15" rx="3" fill="#064e3b"/>
          <text x="1055" y="391" text-anchor="middle" font-size="8.5" font-weight="700" fill="#a7f3d0">F6 Snap</text>

          <!-- F7: Midtrans Webhook -> Payment Handler -->
          <line x1="1090" y1="495" x2="1020" y2="330" stroke="#34d399" stroke-width="2" stroke-dasharray="4,2" marker-end="url(#arrow-green)"/>
          <rect x="1028" y="415" width="55" height="15" rx="3" fill="#064e3b"/>
          <text x="1055" y="426" text-anchor="middle" font-size="8.5" font-weight="700" fill="#a7f3d0">F7 Notif</text>

          <!-- F8: Core App -> Reverb Broadcasting -->
          <line x1="800" y1="250" x2="1090" y2="150" stroke="#c084fc" stroke-width="2" marker-end="url(#arrow-purple)"/>
          <rect x="915" y="195" width="55" height="15" rx="3" fill="#581c87"/>
          <text x="942" y="206" text-anchor="middle" font-size="8.5" font-weight="700" fill="#e9d5ff">F8 Event</text>

          <!-- F9: Core App -> Browser (Inertia Props) -->
          <path d="M 620 160 C 450 210, 400 230, 300 240" fill="none" stroke="#38bdf8" stroke-width="2" stroke-dasharray="3,3" marker-end="url(#arrow-blue)"/>
          <rect x="420" y="215" width="60" height="15" rx="3" fill="#0c4a6e"/>
          <text x="450" y="226" text-anchor="middle" font-size="8.5" font-weight="700" fill="#bae6fd">F9 Inertia</text>

          <!-- F10: Browser -> Google Maps API -->
          <path d="M 300 280 C 420 380, 850 710, 1090 650" fill="none" stroke="#34d399" stroke-width="2" stroke-dasharray="4,4" marker-end="url(#arrow-green)"/>
          <rect x="560" y="585" width="55" height="15" rx="3" fill="#064e3b"/>
          <text x="587" y="596" text-anchor="middle" font-size="8.5" font-weight="700" fill="#a7f3d0">F10 Map</text>

        </svg>
      </div>

      <!-- DFD Legend Bar -->
      <div class="glass-card rounded-xl p-4 border border-slate-800 text-xs flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-2">
          <span class="font-bold text-slate-200 uppercase tracking-wider">Legenda Notasi:</span>
        </div>
        <div class="flex flex-wrap items-center gap-4 text-slate-300">
          <div class="flex items-center gap-1.5">
            <span class="w-4 h-3 rounded-sm border border-cyan-400 bg-slate-800 inline-block"></span>
            <span>Entitas Eksternal (Kotak)</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="w-4 h-3 rounded-md border border-cyan-400 bg-slate-800 inline-block"></span>
            <span>Proses Aplikasi (Rounded)</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="w-4 h-3 border-y-2 border-cyan-400 bg-slate-800 inline-block"></span>
            <span>Data Store / DB (Silinder)</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="w-5 h-0.5 border-b-2 border-dashed border-rose-500 inline-block"></span>
            <span>Trust Boundary (Dashed Border)</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="w-3.5 h-3.5 rounded bg-rose-900 border border-rose-500 text-[9px] font-bold text-rose-200 flex items-center justify-center">T#</span>
            <span>Penanda Titik Ancaman</span>
          </div>
        </div>
      </div>
    </section>


    <!-- ============================================================ -->
    <!-- BAGIAN 4: RINGKASAN HASIL & METRIK STRIDE-DREAD              -->
    <!-- ============================================================ -->
    <section class="space-y-5">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-amber-500/20 border border-amber-500/40 text-amber-400 font-bold flex items-center justify-center text-sm shadow-sm">04</div>
        <div>
          <h2 class="text-2xl font-bold tracking-tight text-white">Ringkasan Hasil Evaluasi Risiko &amp; Metrik</h2>
          <p class="text-xs sm:text-sm text-slate-400">Distribusi tingkat keparahan risiko, klasifikasi STRIDE, profil skor DREAD, dan status mitigasi</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-4 gap-5">
        
        <!-- Risk Distribution Chart Box -->
        <div class="glass-card rounded-xl p-5 border border-slate-800 space-y-4 md:col-span-1">
          <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Distribusi Level Risiko</h3>
          <div class="space-y-3">
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-rose-400 font-semibold flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-rose-500"></span> CRITICAL (Skor 40-50)
                </span>
                <span class="mono font-bold text-rose-300">{critical_count} (20%)</span>
              </div>
              <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div class="bg-rose-500 h-full rounded-full" style="width: 20%"></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-amber-400 font-semibold flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-amber-500"></span> HIGH (Skor 25-39)
                </span>
                <span class="mono font-bold text-amber-300">{high_count} (70%)</span>
              </div>
              <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div class="bg-amber-500 h-full rounded-full" style="width: 70%"></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-yellow-400 font-semibold flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-yellow-500"></span> MEDIUM (Skor 15-24)
                </span>
                <span class="mono font-bold text-yellow-300">{medium_count} (0%)</span>
              </div>
              <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div class="bg-yellow-500 h-full rounded-full" style="width: 0%"></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-emerald-400 font-semibold flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-emerald-500"></span> LOW / MITIGATED (&le;14)
                </span>
                <span class="mono font-bold text-emerald-300">{low_count} (10%)</span>
              </div>
              <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div class="bg-emerald-500 h-full rounded-full" style="width: 10%"></div>
              </div>
            </div>
          </div>

          <div class="pt-3 border-t border-slate-800 text-[11px] text-slate-400">
            Sebanyak <strong class="text-rose-400">90%</strong> ancaman berada pada spektrum kritis &amp; tinggi yang memerlukan penanganan langsung.
          </div>
        </div>

        <!-- STRIDE Breakdown -->
        <div class="glass-card rounded-xl p-5 border border-slate-800 space-y-4 md:col-span-1">
          <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Distribusi Kategori STRIDE</h3>
          <div class="grid grid-cols-2 gap-2 text-xs">
            {"".join(f'''<div class="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800 flex flex-col justify-between">
              <span class="text-[10px] text-slate-400 truncate">{k}</span>
              <div class="flex items-baseline justify-between mt-1">
                <span class="mono font-bold text-lg text-cyan-400">{v}</span>
                <span class="text-[10px] text-slate-500">ancaman</span>
              </div>
            </div>''' for k, v in stride_counts.items())}
          </div>
          <div class="text-[11px] text-slate-400 pt-1">
            Kategori dominan adalah <strong class="text-cyan-300">Tampering (6)</strong> dan <strong class="text-cyan-300">Information Disclosure (5)</strong>.
          </div>
        </div>

        <!-- Prioritas Utama & Highlight -->
        <div class="glass-card rounded-xl p-5 border border-slate-800 space-y-4 md:col-span-2 flex flex-col justify-between">
          <div>
            <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Temuan Kritis Utama &amp; Bukti Kode Sumber</h3>
            <div class="space-y-3">
              <div class="p-3 rounded-lg bg-rose-950/40 border border-rose-500/30 flex items-start gap-3">
                <div class="w-7 h-7 rounded-lg bg-rose-900/80 text-rose-300 font-bold flex items-center justify-center shrink-0 text-xs">!</div>
                <div class="space-y-1 text-xs">
                  <div class="flex items-center gap-2">
                    <span class="font-bold text-rose-300">T-01: BOLA / IDOR Status Booking (Skor 40 - CRITICAL)</span>
                    <span class="mono text-[10px] bg-rose-900 px-1.5 py-0.2 rounded text-rose-200">CVE-2023-28438</span>
                  </div>
                  <p class="text-slate-300">
                    Pengecekan hak akses <code class="mono bg-slate-900 px-1 py-0.5 rounded text-rose-300">auth()->id()</code> dikomentari pada <span class="text-slate-200 font-medium">BookingController.php:230</span>. Siapa saja dapat mengubah status pesanan milik pengguna lain!
                  </p>
                </div>
              </div>

              <div class="p-3 rounded-lg bg-rose-950/40 border border-rose-500/30 flex items-start gap-3">
                <div class="w-7 h-7 rounded-lg bg-rose-900/80 text-rose-300 font-bold flex items-center justify-center shrink-0 text-xs">!</div>
                <div class="space-y-1 text-xs">
                  <div class="flex items-center gap-2">
                    <span class="font-bold text-rose-300">T-02: Unauthenticated Socket Flooding DoS (Skor 40 - CRITICAL)</span>
                    <span class="mono text-[10px] bg-rose-900 px-1.5 py-0.2 rounded text-rose-200">CVE-2023-34449</span>
                  </div>
                  <p class="text-slate-300">
                    Endpoint <code class="mono bg-slate-900 px-1 py-0.5 rounded text-rose-300">POST /api/test-latency</code> di <span class="text-slate-200 font-medium">routes/api.php:15</span> bebas diakses publik tanpa middleware auth/rate limiter, memicu event broadcast tak terbatas.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Highlight Mitigasi Sukses -->
          <div class="p-3 rounded-lg bg-emerald-950/40 border border-emerald-500/30 flex items-center justify-between text-xs">
            <div class="flex items-center gap-2.5">
              <span class="w-6 h-6 rounded-full bg-emerald-900 text-emerald-300 font-bold flex items-center justify-center text-xs">✓</span>
              <div>
                <span class="font-bold text-emerald-300">Mitigasi Berhasil: APP_DEBUG=false</span>
                <span class="text-slate-400 block text-[11px]">T-10 dinonaktifkan di .env baris 4. Skor DREAD turun dari 43 (Critical) menjadi 6 (Low).</span>
              </div>
            </div>
            <span class="mono text-emerald-400 font-bold bg-emerald-900/80 px-2 py-1 rounded">TERVERIFIKASI</span>
          </div>
        </div>

      </div>
    </section>


    <!-- ============================================================ -->
    <!-- BAGIAN 5: DAFTAR LENGKAP 10 ANCAMAN & MITIGASI              -->
    <!-- ============================================================ -->
    <section class="space-y-5">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-rose-500/20 border border-rose-500/40 text-rose-400 font-bold flex items-center justify-center text-sm shadow-sm">05</div>
          <div>
            <h2 class="text-2xl font-bold tracking-tight text-white">Daftar Lengkap 10 Ancaman &amp; Rekomendasi Mitigasi</h2>
            <p class="text-xs sm:text-sm text-slate-400">Rincian parameter STRIDE, skor DREAD, bukti kode, dan solusi teknis terstruktur</p>
          </div>
        </div>

        <!-- Filter Buttons (Interactive) -->
        <div class="flex items-center gap-1.5 bg-slate-900 p-1 rounded-xl border border-slate-800 text-xs no-print">
          <button onclick="filterThreats('ALL')" id="btn-ALL" class="px-3 py-1.5 rounded-lg bg-cyan-600 text-white font-semibold transition">Semua (10)</button>
          <button onclick="filterThreats('CRITICAL')" id="btn-CRITICAL" class="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition">Critical (2)</button>
          <button onclick="filterThreats('HIGH')" id="btn-HIGH" class="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition">High (7)</button>
          <button onclick="filterThreats('LOW')" id="btn-LOW" class="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition">Low (1)</button>
        </div>
      </div>

      <!-- Threat Cards Container -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4" id="threats-grid">
"""

for t in threats:
    level_color = "rose" if t['level'] == 'CRITICAL' else ("amber" if t['level'] == 'HIGH' else "emerald")
    badge_bg = f"bg-{level_color}-950/80 border-{level_color}-500/50 text-{level_color}-300"
    
    stride_badges = "".join([f'<span class="mono px-1.5 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700 text-[10px] font-bold">{s}</span>' for s in t['stride']])
    
    d = t['dread']
    
    html_content += f"""
        <div class="threat-card glass-card rounded-xl p-5 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between space-y-4" data-level="{t['level']}">
          <div class="space-y-3">
            <!-- Header Card -->
            <div class="flex items-start justify-between gap-3">
              <div class="space-y-1">
                <div class="flex items-center gap-2">
                  <span class="mono text-xs font-black text-cyan-400 bg-cyan-950 px-2 py-0.5 rounded border border-cyan-800/60">{t['id']}</span>
                  <div class="flex items-center gap-1">{stride_badges}</div>
                </div>
                <h4 class="font-bold text-slate-100 text-sm leading-snug pt-1">{t['desc']}</h4>
              </div>
              <div class="shrink-0 text-right">
                <span class="inline-block px-2.5 py-1 rounded-md text-xs font-extrabold border {badge_bg}">{t['level']}</span>
                <div class="mono text-xs font-bold text-slate-300 mt-1">Skor: {t['total']}/50</div>
              </div>
            </div>

            <!-- DREAD Breakdown Bars -->
            <div class="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800 text-[11px] grid grid-cols-5 gap-2 text-center">
              <div>
                <span class="text-slate-400 block text-[10px]">Damage</span>
                <span class="mono font-bold text-cyan-300">{d['D']}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[10px]">Reprod</span>
                <span class="mono font-bold text-cyan-300">{d['R']}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[10px]">Exploit</span>
                <span class="mono font-bold text-cyan-300">{d['E']}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[10px]">Affected</span>
                <span class="mono font-bold text-cyan-300">{d['A']}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[10px]">Discov</span>
                <span class="mono font-bold text-cyan-300">{d['X']}</span>
              </div>
            </div>

            <!-- Bukti & Alasan -->
            <div class="space-y-1.5 text-xs">
              <div>
                <span class="font-semibold text-slate-400">Bukti Kode Sumber:</span>
                <div class="mono text-[11px] bg-slate-950 p-2 rounded border border-slate-800/80 text-rose-300/90 mt-1 break-all">
                  {t['bukti']}
                </div>
              </div>
              <div class="text-slate-300 text-[11px] leading-relaxed pt-1">
                <span class="font-semibold text-slate-400">Alasan Skoring:</span> {t['alasan']}
              </div>
            </div>
          </div>

          <!-- Rekomendasi Mitigasi -->
          <div class="pt-3 border-t border-slate-800/80">
            <div class="p-3 rounded-lg bg-emerald-950/30 border border-emerald-500/20 text-xs">
              <span class="font-bold text-emerald-400 flex items-center gap-1.5 mb-1">
                <svg class="w-3.5 h-3.5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                Rekomendasi Tindakan Mitigasi:
              </span>
              <p class="text-slate-200 text-[11px] leading-relaxed">
                {t['mitigasi']}
              </p>
            </div>
          </div>
        </div>
    """

html_content += f"""
      </div>
    </section>


    <!-- ============================================================ -->
    <!-- BAGIAN 6: SARAN & ROADMAP STRATEGIS                          -->
    <!-- ============================================================ -->
    <section class="glass rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-6">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-cyan-500/20 border border-cyan-500/40 text-cyan-400 font-bold flex items-center justify-center text-sm shadow-sm">06</div>
        <div>
          <h2 class="text-2xl font-bold tracking-tight text-white">Saran &amp; Pendapat Ahli Keamanan (Action Roadmap)</h2>
          <p class="text-xs sm:text-sm text-slate-400">Rencana mitigasi bertahap untuk tim pengembang dan pengambil keputusan</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-5 text-xs">
        
        <!-- Fase 1 -->
        <div class="p-5 rounded-xl bg-rose-950/20 border border-rose-500/30 space-y-3">
          <div class="flex items-center justify-between">
            <span class="mono px-2 py-0.5 rounded bg-rose-900 text-rose-200 font-bold text-[10px]">FASE 1: SEGERA (0 - 48 JAM)</span>
            <span class="text-rose-400 font-bold">Hotfix Kritis</span>
          </div>
          <h4 class="font-bold text-slate-100 text-sm">Penutupan Celah BOLA &amp; DoS Socket</h4>
          <ul class="space-y-2 text-slate-300 list-disc list-inside leading-relaxed">
            <li><strong>Aktifkan auth check di T-01:</strong> Un-comment pengecekan kepemilikan di <code class="mono text-rose-300">BookingController.php:230</code>.</li>
            <li><strong>Proteksi Endpoint T-02:</strong> Hapus atau bungkus route <code class="mono text-rose-300">/api/test-latency</code> dengan <code class="mono text-rose-300">auth:sanctum</code> &amp; throttle rate limiter.</li>
            <li><strong>Validasi MIDTRANS_SERVER_KEY (T-03):</strong> Wajibkan kunci server Midtrans tidak boleh null atau kosong di production.</li>
          </ul>
        </div>

        <!-- Fase 2 -->
        <div class="p-5 rounded-xl bg-amber-950/20 border border-amber-500/30 space-y-3">
          <div class="flex items-center justify-between">
            <span class="mono px-2 py-0.5 rounded bg-amber-900 text-amber-200 font-bold text-[10px]">FASE 2: JANGKA MENENGAH (1-2 MINGGU)</span>
            <span class="text-amber-400 font-bold">Hardening Kode</span>
          </div>
          <h4 class="font-bold text-slate-100 text-sm">Pengerasan Konfigurasi &amp; Input Sanitization</h4>
          <ul class="space-y-2 text-slate-300 list-disc list-inside leading-relaxed">
            <li><strong>Enkripsi Sesi (T-08):</strong> Ubah <code class="mono text-amber-300">SESSION_ENCRYPT=true</code> di .env dan pasang flag <code class="mono text-amber-300">HttpOnly</code>, <code class="mono text-amber-300">Secure</code>.</li>
            <li><strong>Mass Assignment Fix (T-06):</strong> Keluarkan properti <code class="mono text-amber-300">'role'</code> dari array <code class="mono text-amber-300">$fillable</code> model User.</li>
            <li><strong>Sanitasi XSS &amp; Upload (T-05 &amp; T-07):</strong> Terapkan strip_tags pada komentar review dan validasi magic-bytes untuk upload gambar.</li>
          </ul>
        </div>

        <!-- Fase 3 -->
        <div class="p-5 rounded-xl bg-cyan-950/20 border border-cyan-500/30 space-y-3">
          <div class="flex items-center justify-between">
            <span class="mono px-2 py-0.5 rounded bg-cyan-900 text-cyan-200 font-bold text-[10px]">FASE 3: STRATEGIS (1 BULAN)</span>
            <span class="text-cyan-400 font-bold">Arsitektur Tangguh</span>
          </div>
          <h4 class="font-bold text-slate-100 text-sm">Infrastruktur &amp; Otomasi DevSecOps</h4>
          <ul class="space-y-2 text-slate-300 list-disc list-inside leading-relaxed">
            <li><strong>Spatial Caching (T-04):</strong> Tambahkan Redis caching untuk query rumus Haversine geolokasi katalog.</li>
            <li><strong>WAF &amp; Rate Limiting:</strong> Konfigurasikan Cloudflare WAF rule untuk inspeksi webhook payload dan mitigasi DDoS.</li>
            <li><strong>Automated Security Scanning:</strong> Integrasikan SAST (SonarQube / PHPStan Security) pada CI/CD pipeline GitHub Actions.</li>
          </ul>
        </div>

      </div>
    </section>

    <!-- FOOTER -->
    <footer class="border-t border-slate-800/80 pt-6 pb-10 text-center text-xs text-slate-500 space-y-2">
      <p>Infografik Threat Modeling Sistem Informasi &copy; 2026 FindServices Project. Seluruh data diekstraksi dari lembar kerja <code class="mono text-slate-400">1. template_baru_Praktikum_STRIDE-DREAD.xlsx</code>.</p>
      <p class="text-[11px] text-slate-600">Dibuat untuk keperluan evaluasi keamanan perangkat lunak, pelaporan audit, dan pembelajaran praktikum keamanan sistem informasi.</p>
    </footer>

  </main>

  <script>
    function filterThreats(level) {{
      const cards = document.querySelectorAll('.threat-card');
      const buttons = ['ALL', 'CRITICAL', 'HIGH', 'LOW'];
      
      buttons.forEach(b => {{
        const btn = document.getElementById('btn-' + b);
        if (b === level) {{
          btn.className = 'px-3 py-1.5 rounded-lg bg-cyan-600 text-white font-semibold transition';
        }} else {{
          btn.className = 'px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition';
        }}
      }});

      cards.forEach(card => {{
        if (level === 'ALL' || card.getAttribute('data-level') === level) {{
          card.style.display = 'flex';
        }} else {{
          card.style.display = 'none';
        }}
      }});
    }}
  </script>
</body>
</html>
"""

with open(output_html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Infographic HTML successfully created at: {output_html_path}")
