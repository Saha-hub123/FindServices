import openpyxl

xlsx_path = r'c:\laragon\www\FindServices\keamanan_sistem_informasi\1. template_baru_Praktikum_STRIDE-DREAD.xlsx'
html_path = r'c:\laragon\www\FindServices\keamanan_sistem_informasi\infografik_threat_modeling_4x3.html'

wb = openpyxl.load_workbook(xlsx_path, data_only=True)
ws_p = wb['Profil_Aplikasi']
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
    
    # short title extraction from desc
    desc_full = ws_t[f'C{r}'].value or ''
    
    threats.append({
        'id': tid,
        'desc': desc_full,
        'stride': stride,
        'dread': {'D': d_d, 'R': d_r, 'E': d_e, 'A': d_a, 'X': d_x},
        'total': total,
        'level': level,
        'alasan': ws_t[f'S{r}'].value or '',
        'bukti': ws_t[f'T{r}'].value or '',
        'mitigasi': ws_t[f'U{r}'].value or ''
    })

critical_count = sum(1 for t in threats if t['level'] == 'CRITICAL')
high_count = sum(1 for t in threats if t['level'] == 'HIGH')
medium_count = sum(1 for t in threats if t['level'] == 'MEDIUM')
low_count = sum(1 for t in threats if t['level'] == 'LOW')
avg_dread = round(sum(t['total'] for t in threats) / len(threats), 1)

# Generate Compact 4:3 HTML (1920 x 1440)
html = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <title>Infografik Threat Modeling FindServices - 4:3 Ratio</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      background-color: #080c14;
      color: #e2e8f0;
      width: 1920px;
      height: 1440px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 18px 24px 16px 24px;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
    .glass-box {{
      background: rgba(15, 23, 42, 0.7);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 10px;
    }}
    .gradient-header {{
      background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 50%, #a855f7 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    /* custom scrollbar if needed */
    ::-webkit-scrollbar {{ width: 4px; height: 4px; }}
    ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 4px; }}
  </style>
</head>
<body>

  <!-- ======================================================== -->
  <!-- HEADER BAR (Height: ~68px)                               -->
  <!-- ======================================================== -->
  <header class="glass-box px-6 py-3 flex items-center justify-between border-slate-800 shadow-md">
    <div class="flex items-center gap-4">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 text-white font-black text-lg">
        FS
      </div>
      <div>
        <div class="flex items-center gap-2.5">
          <h1 class="text-xl font-extrabold tracking-tight text-white uppercase">
            FINDSERVICES <span class="gradient-header">THREAT MODELING DASHBOARD</span>
          </h1>
          <span class="mono text-[10px] bg-cyan-950 text-cyan-400 border border-cyan-800 px-2 py-0.5 rounded font-bold">STRIDE &amp; DREAD</span>
          <span class="mono text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded">OWASP FRAMEWORK</span>
        </div>
        <p class="text-xs text-slate-400">
          Target: <strong class="text-slate-200">FindServices Marketplace</strong> (Laravel 12 + Vue 3/Inertia + MySQL + Reverb + Midtrans) | Praktikum Keamanan SI
        </p>
      </div>
    </div>

    <!-- Top Key Badges -->
    <div class="flex items-center gap-3">
      <div class="flex items-center gap-2 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-lg text-xs">
        <span class="text-slate-400">Total Ancaman:</span>
        <span class="mono font-bold text-white text-sm">10</span>
      </div>
      <div class="flex items-center gap-2 bg-rose-950/50 border border-rose-500/40 px-3 py-1.5 rounded-lg text-xs">
        <span class="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
        <span class="text-rose-300 font-semibold">Critical:</span>
        <span class="mono font-bold text-rose-200 text-sm">{critical_count}</span>
      </div>
      <div class="flex items-center gap-2 bg-amber-950/50 border border-amber-500/40 px-3 py-1.5 rounded-lg text-xs">
        <span class="w-2 h-2 rounded-full bg-amber-500"></span>
        <span class="text-amber-300 font-semibold">High:</span>
        <span class="mono font-bold text-amber-200 text-sm">{high_count}</span>
      </div>
      <div class="flex items-center gap-2 bg-emerald-950/50 border border-emerald-500/40 px-3 py-1.5 rounded-lg text-xs">
        <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
        <span class="text-emerald-300 font-semibold">Mitigated:</span>
        <span class="mono font-bold text-emerald-200 text-sm">{low_count}</span>
      </div>
      <div class="flex items-center gap-2 bg-cyan-950/50 border border-cyan-500/40 px-3 py-1.5 rounded-lg text-xs">
        <span class="text-cyan-300 font-semibold">Avg DREAD:</span>
        <span class="mono font-bold text-cyan-200 text-sm">{avg_dread} <span class="text-[10px] text-slate-400">/50</span></span>
      </div>
    </div>
  </header>

  <!-- ======================================================== -->
  <!-- MAIN WORKSPACE: 2 COLUMNS (Height: ~1320px)              -->
  <!-- ======================================================== -->
  <div class="grid grid-cols-12 gap-4 flex-1 mt-3.5 mb-1 overflow-hidden" style="height: 1315px;">
    
    <!-- ====================================================== -->
    <!-- LEFT COLUMN (Cols: 7 / 12) - System, Workflow, DFD     -->
    <!-- ====================================================== -->
    <div class="col-span-7 flex flex-col justify-between gap-3.5 h-full overflow-hidden">
      
      <!-- ROW 1: System Summary & Workflow (Height: ~295px) -->
      <div class="grid grid-cols-12 gap-3 shrink-0" style="height: 295px;">
        
        <!-- System Profile Card (Cols: 5) -->
        <div class="col-span-5 glass-box p-3.5 flex flex-col justify-between border-slate-800 text-xs">
          <div>
            <div class="flex items-center justify-between pb-1.5 border-b border-slate-800 mb-2">
              <span class="font-bold text-slate-200 flex items-center gap-1.5 text-xs">
                <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
                1. Profil &amp; Arsitektur Sistem
              </span>
              <span class="mono text-[10px] text-cyan-400 bg-cyan-950/80 px-1.5 py-0.5 rounded">FINDSERVICES</span>
            </div>
            <p class="text-slate-300 text-[11px] leading-relaxed line-clamp-3 mb-2">
              Marketplace penghubung pelanggan (<em class="text-slate-200">Customer</em>) dengan penyedia jasa lokal (<em class="text-slate-200">Provider/Tukang</em>) berbasis jarak radius geolokasi (Haversine), negosiasi harga, pembayaran Midtrans, dan chat real-time.
            </p>
            <div class="space-y-1 text-[10.5px]">
              <div class="flex justify-between py-0.5 border-b border-slate-800/60">
                <span class="text-slate-400">Backend Core:</span>
                <span class="text-cyan-300 font-semibold">Laravel 12 (PHP 8.3)</span>
              </div>
              <div class="flex justify-between py-0.5 border-b border-slate-800/60">
                <span class="text-slate-400">Frontend Stack:</span>
                <span class="text-emerald-300 font-semibold">Vue 3 + Inertia.js</span>
              </div>
              <div class="flex justify-between py-0.5 border-b border-slate-800/60">
                <span class="text-slate-400">Database &amp; Storage:</span>
                <span class="text-amber-300 font-semibold">MySQL 8.0 &amp; Local Storage</span>
              </div>
              <div class="flex justify-between py-0.5">
                <span class="text-slate-400">Realtime Engine:</span>
                <span class="text-purple-300 font-semibold">Laravel Reverb (:8080)</span>
              </div>
            </div>
          </div>
          <div class="pt-1.5 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-400">
            <span>Aktor: Customer, Provider, Admin</span>
            <span class="text-emerald-400 font-semibold">Static Audit</span>
          </div>
        </div>

        <!-- Workflow Pipeline Card (Cols: 7) -->
        <div class="col-span-7 glass-box p-3.5 flex flex-col justify-between border-slate-800 text-xs">
          <div>
            <div class="flex items-center justify-between pb-1.5 border-b border-slate-800 mb-2">
              <span class="font-bold text-slate-200 flex items-center gap-1.5 text-xs">
                <svg class="w-3.5 h-3.5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                2. Alur Kerja Pengguna &amp; Titik Ancaman (Touchpoints)
              </span>
              <span class="text-[10px] text-slate-400">5 Siklus Layanan</span>
            </div>
            
            <!-- 5 Steps Flow -->
            <div class="grid grid-cols-5 gap-1.5 text-center mt-1">
              <!-- Step 1 -->
              <div class="p-1.5 rounded-lg bg-slate-900/90 border border-slate-800 flex flex-col justify-between h-[190px]">
                <div>
                  <div class="mono w-5 h-5 mx-auto rounded-full bg-cyan-950 text-cyan-400 text-[10px] font-bold flex items-center justify-center mb-1">1</div>
                  <div class="font-bold text-slate-200 text-[10.5px]">Pencarian &amp; Auth</div>
                  <div class="text-[9.5px] text-slate-400 mt-1 leading-tight">Customer login &amp; cari jasa via radius GPS Haversine</div>
                </div>
                <div class="mt-2 pt-1 border-t border-slate-800 space-y-1">
                  <div class="mono text-[9px] bg-rose-950 text-rose-300 rounded px-1 py-0.5 border border-rose-800/50" title="DoS Haversine Query">T-04 (DoS)</div>
                  <div class="mono text-[9px] bg-amber-950 text-amber-300 rounded px-1 py-0.5 border border-amber-800/50" title="Plaintext Session">T-08 (Sess)</div>
                </div>
              </div>

              <!-- Step 2 -->
              <div class="p-1.5 rounded-lg bg-slate-900/90 border border-slate-800 flex flex-col justify-between h-[190px]">
                <div>
                  <div class="mono w-5 h-5 mx-auto rounded-full bg-blue-950 text-blue-400 text-[10px] font-bold flex items-center justify-center mb-1">2</div>
                  <div class="font-bold text-slate-200 text-[10.5px]">Booking &amp; Nego</div>
                  <div class="text-[9.5px] text-slate-400 mt-1 leading-tight">Buat pesanan, negosiasi dan kesepakatan harga</div>
                </div>
                <div class="mt-2 pt-1 border-t border-slate-800 space-y-1">
                  <div class="mono text-[9px] bg-rose-950 text-rose-300 rounded px-1 py-0.5 border border-rose-800 font-bold" title="BOLA / IDOR Status Booking">T-01 (IDOR)</div>
                  <div class="mono text-[9px] bg-amber-950 text-amber-300 rounded px-1 py-0.5 border border-amber-800/50" title="Mass Assignment Role">T-06 (Priv)</div>
                </div>
              </div>

              <!-- Step 3 -->
              <div class="p-1.5 rounded-lg bg-slate-900/90 border border-slate-800 flex flex-col justify-between h-[190px]">
                <div>
                  <div class="mono w-5 h-5 mx-auto rounded-full bg-emerald-950 text-emerald-400 text-[10px] font-bold flex items-center justify-center mb-1">3</div>
                  <div class="font-bold text-slate-200 text-[10.5px]">Pembayaran</div>
                  <div class="text-[9.5px] text-slate-400 mt-1 leading-tight">Checkout via Snap Midtrans &amp; verifikasi webhook</div>
                </div>
                <div class="mt-2 pt-1 border-t border-slate-800 space-y-1">
                  <div class="mono text-[9px] bg-amber-950 text-amber-300 rounded px-1 py-0.5 border border-amber-800/50" title="Webhook Signature Bypass">T-03 (Pay)</div>
                </div>
              </div>

              <!-- Step 4 -->
              <div class="p-1.5 rounded-lg bg-slate-900/90 border border-slate-800 flex flex-col justify-between h-[190px]">
                <div>
                  <div class="mono w-5 h-5 mx-auto rounded-full bg-purple-950 text-purple-400 text-[10px] font-bold flex items-center justify-center mb-1">4</div>
                  <div class="font-bold text-slate-200 text-[10.5px]">Chat &amp; Kerja</div>
                  <div class="text-[9.5px] text-slate-400 mt-1 leading-tight">Pengerjaan jasa &amp; komunikasi socket Reverb</div>
                </div>
                <div class="mt-2 pt-1 border-t border-slate-800 space-y-1">
                  <div class="mono text-[9px] bg-rose-950 text-rose-300 rounded px-1 py-0.5 border border-rose-800 font-bold" title="Reverb WebSocket Flooding">T-02 (DoS)</div>
                  <div class="mono text-[9px] bg-amber-950 text-amber-300 rounded px-1 py-0.5 border border-amber-800/50" title="Chat Hashids Tampering">T-09 (Chat)</div>
                </div>
              </div>

              <!-- Step 5 -->
              <div class="p-1.5 rounded-lg bg-slate-900/90 border border-slate-800 flex flex-col justify-between h-[190px]">
                <div>
                  <div class="mono w-5 h-5 mx-auto rounded-full bg-amber-950 text-amber-400 text-[10px] font-bold flex items-center justify-center mb-1">5</div>
                  <div class="font-bold text-slate-200 text-[10.5px]">Review &amp; Selesai</div>
                  <div class="text-[9.5px] text-slate-400 mt-1 leading-tight">Konfirmasi selesai, ulasan rating &amp; upload foto</div>
                </div>
                <div class="mt-2 pt-1 border-t border-slate-800 space-y-1">
                  <div class="mono text-[9px] bg-amber-950 text-amber-300 rounded px-1 py-0.5 border border-amber-800/50" title="Stored XSS Review">T-05 (XSS)</div>
                  <div class="mono text-[9px] bg-amber-950 text-amber-300 rounded px-1 py-0.5 border border-amber-800/50" title="Polyglot Image Upload">T-07 (File)</div>
                </div>
              </div>

            </div>
          </div>
          <div class="text-[10px] text-slate-400 pt-1 flex justify-between items-center">
            <span>Legenda: Titik rawan ancaman (<span class="text-rose-400 font-bold">Merah: Critical</span>, <span class="text-amber-400 font-bold">Kuning: High</span>)</span>
            <span class="mono text-cyan-400 text-[9.5px]">End-to-End Mapped</span>
          </div>
        </div>

      </div>

      <!-- ROW 2: DFD Level-1 & Trust Boundaries Diagram (Height: ~1005px) -->
      <div class="glass-box p-3 flex flex-col justify-between border-slate-800 flex-1 overflow-hidden">
        <div class="flex items-center justify-between pb-1.5 border-b border-slate-800 shrink-0">
          <span class="font-bold text-slate-200 flex items-center gap-1.5 text-xs">
            <svg class="w-3.5 h-3.5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1.5 3 3.5 3h9c2 0 3.5-1 3.5-3V7c0-2-1.5-3-3.5-3h-9C5.5 4 4 5 4 7z"/></svg>
            3. Data Flow Diagram (DFD Level-1) &amp; 5 Trust Boundaries
          </span>
          <div class="flex items-center gap-3 text-[10px]">
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-rose-500"></span> TB-1 Public</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span> TB-2 Ingress</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span> TB-3 Core App</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-purple-500"></span> TB-4 Daemon</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> TB-5 APIs</span>
          </div>
        </div>

        <!-- SVG DFD Container (Compact Landscape) -->
        <div class="w-full flex-1 flex items-center justify-center p-1 overflow-hidden">
          <svg viewBox="0 0 1080 870" class="w-full h-full max-h-[920px]" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <marker id="arr-gray" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#64748b"/></marker>
              <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#38bdf8"/></marker>
              <marker id="arr-orange" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#fb923c"/></marker>
              <marker id="arr-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#34d399"/></marker>
              <marker id="arr-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#c084fc"/></marker>
            </defs>

            <!-- TB-1: Public Untrusted (x=10, y=10, w=220, h=850) -->
            <rect x="10" y="10" width="220" height="850" rx="10" fill="#1e1014" stroke="#f43f5e" stroke-width="1.8" stroke-dasharray="5,3" fill-opacity="0.5"/>
            <rect x="20" y="20" width="200" height="24" rx="5" fill="#881337"/>
            <text x="120" y="36" text-anchor="middle" font-size="10" font-weight="700" fill="#fecdd3" font-family="'Plus Jakarta Sans'">TB-1: Zona Eksternal (Public)</text>

            <!-- Entities in TB-1 -->
            <!-- Customer -->
            <rect x="25" y="60" width="190" height="70" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
            <text x="120" y="85" text-anchor="middle" font-size="12" font-weight="700" fill="#f8fafc">Pelanggan (Customer)</text>
            <text x="120" y="102" text-anchor="middle" font-size="9.5" fill="#94a3b8">K1 Web Client / Vue 3</text>
            <rect x="35" y="108" width="170" height="15" rx="3" fill="#78350f"/>
            <text x="120" y="119" text-anchor="middle" font-size="8.5" font-weight="700" fill="#fef3c7">T-08 Plaintext Session Sniff</text>

            <!-- Provider -->
            <rect x="25" y="150" width="190" height="70" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
            <text x="120" y="175" text-anchor="middle" font-size="12" font-weight="700" fill="#f8fafc">Penyedia Jasa (Provider)</text>
            <text x="120" y="192" text-anchor="middle" font-size="9.5" fill="#94a3b8">K1 Web Client / Mitra</text>
            <rect x="35" y="198" width="170" height="15" rx="3" fill="#78350f"/>
            <text x="120" y="209" text-anchor="middle" font-size="8.5" font-weight="700" fill="#fef3c7">T-07 Polyglot File Upload</text>

            <!-- Admin -->
            <rect x="25" y="240" width="190" height="65" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
            <text x="120" y="265" text-anchor="middle" font-size="12" font-weight="700" fill="#f8fafc">Administrator Platform</text>
            <text x="120" y="282" text-anchor="middle" font-size="9.5" fill="#94a3b8">K1 Web Admin Dashboard</text>
            <rect x="35" y="288" width="170" height="14" rx="3" fill="#78350f"/>
            <text x="120" y="299" text-anchor="middle" font-size="8" font-weight="700" fill="#fef3c7">T-06 Role Admin Escalation</text>

            <!-- Threat Actor Box -->
            <rect x="25" y="325" width="190" height="520" rx="8" fill="#2d0b13" stroke="#f43f5e" stroke-width="1.5"/>
            <text x="120" y="350" text-anchor="middle" font-size="12" font-weight="800" fill="#fb7185">Penyerang (Threat Actor)</text>
            <text x="120" y="368" text-anchor="middle" font-size="9" fill="#fda4af">Vektor Serangan Teridentifikasi:</text>

            <g transform="translate(32, 380)">
              <rect x="0" y="0" width="176" height="38" rx="4" fill="#7f1d1d" stroke="#f43f5e" stroke-width="1"/>
              <text x="88" y="16" text-anchor="middle" font-size="9.5" font-weight="800" fill="#fff">🚨 T-01 IDOR Booking</text>
              <text x="88" y="30" text-anchor="middle" font-size="8" fill="#fecaca">Manipulasi status pesanan (40)</text>

              <rect x="0" y="44" width="176" height="38" rx="4" fill="#7f1d1d" stroke="#f43f5e" stroke-width="1"/>
              <text x="88" y="60" text-anchor="middle" font-size="9.5" font-weight="800" fill="#fff">🚨 T-02 Reverb Socket DoS</text>
              <text x="88" y="74" text-anchor="middle" font-size="8" fill="#fecaca">Flooding endpoint latensi (40)</text>

              <rect x="0" y="88" width="176" height="36" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
              <text x="88" y="103" text-anchor="middle" font-size="9" font-weight="700" fill="#fef3c7">⚠️ T-03 Webhook Forgery (39)</text>
              <text x="88" y="117" text-anchor="middle" font-size="8" fill="#fde68a">Secret key bypass Midtrans</text>

              <rect x="0" y="130" width="176" height="36" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
              <text x="88" y="145" text-anchor="middle" font-size="9" font-weight="700" fill="#fef3c7">⚠️ T-04 Haversine DoS (38)</text>
              <text x="88" y="159" text-anchor="middle" font-size="8" fill="#fde68a">Exhaustion CPU &amp; 10MB upload</text>

              <rect x="0" y="172" width="176" height="36" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
              <text x="88" y="187" text-anchor="middle" font-size="9" font-weight="700" fill="#fef3c7">⚠️ T-05 Stored XSS (37)</text>
              <text x="88" y="201" text-anchor="middle" font-size="8" fill="#fde68a">Payload di review booking</text>

              <rect x="0" y="214" width="176" height="36" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
              <text x="88" y="229" text-anchor="middle" font-size="9" font-weight="700" fill="#fef3c7">⚠️ T-06 Role Escalation (37)</text>
              <text x="88" y="243" text-anchor="middle" font-size="8" fill="#fde68a">Mass assignment 'role' di User</text>

              <rect x="0" y="256" width="176" height="36" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
              <text x="88" y="271" text-anchor="middle" font-size="9" font-weight="700" fill="#fef3c7">⚠️ T-07 Insecure Upload (34)</text>
              <text x="88" y="285" text-anchor="middle" font-size="8" fill="#fde68a">Polyglot file &amp; MIME bypass</text>

              <rect x="0" y="298" width="176" height="36" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
              <text x="88" y="313" text-anchor="middle" font-size="9" font-weight="700" fill="#fef3c7">⚠️ T-08 Session Plaintext (34)</text>
              <text x="88" y="327" text-anchor="middle" font-size="8" fill="#fde68a">Cookie &amp; database unencrypted</text>

              <rect x="0" y="340" width="176" height="36" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
              <text x="88" y="355" text-anchor="middle" font-size="9" font-weight="700" fill="#fef3c7">⚠️ T-09 Chat IDOR Hashids (33)</text>
              <text x="88" y="369" text-anchor="middle" font-size="8" fill="#fde68a">Decode hash tanpa policy check</text>

              <rect x="0" y="382" width="176" height="36" rx="4" fill="#064e3b" stroke="#10b981" stroke-width="1"/>
              <text x="88" y="397" text-anchor="middle" font-size="9" font-weight="700" fill="#a7f3d0">✓ T-10 APP_DEBUG=false (6)</text>
              <text x="88" y="411" text-anchor="middle" font-size="8" fill="#6ee7b7">Termitigasi di .env:4</text>
            </g>


            <!-- TB-2: Ingress & DMZ (x=245, y=10, w=175, h=850) -->
            <rect x="245" y="10" width="175" height="850" rx="10" fill="#1c160c" stroke="#f59e0b" stroke-width="1.8" stroke-dasharray="5,3" fill-opacity="0.5"/>
            <rect x="255" y="20" width="155" height="24" rx="5" fill="#78350f"/>
            <text x="332" y="36" text-anchor="middle" font-size="10" font-weight="700" fill="#fef3c7" font-family="'Plus Jakarta Sans'">TB-2: Ingress &amp; DMZ</text>

            <!-- Components in TB-2 -->
            <rect x="255" y="90" width="155" height="90" rx="8" fill="#1e293b" stroke="#f59e0b" stroke-width="1.5"/>
            <text x="332" y="118" text-anchor="middle" font-size="12" font-weight="700" fill="#fef3c7">Nginx Web Server</text>
            <text x="332" y="138" text-anchor="middle" font-size="9.5" fill="#cbd5e1">Reverse Proxy / SSL</text>
            <text x="332" y="156" text-anchor="middle" font-size="9" font-weight="600" fill="#fcd34d">K2 Ingress Gateway</text>

            <rect x="255" y="280" width="155" height="85" rx="8" fill="#1e293b" stroke="#f59e0b" stroke-width="1.5"/>
            <text x="332" y="308" text-anchor="middle" font-size="12" font-weight="700" fill="#fef3c7">Cloudflare Tunnel</text>
            <text x="332" y="328" text-anchor="middle" font-size="9.5" fill="#cbd5e1">DNS / DDoS Shield</text>
            <text x="332" y="346" text-anchor="middle" font-size="9" font-weight="600" fill="#fcd34d">K8 Network Ingress</text>

            <rect x="255" y="520" width="155" height="85" rx="8" fill="#1e293b" stroke="#f59e0b" stroke-width="1.5"/>
            <text x="332" y="548" text-anchor="middle" font-size="12" font-weight="700" fill="#fef3c7">Auth &amp; Session</text>
            <text x="332" y="568" text-anchor="middle" font-size="9.5" fill="#cbd5e1">K9 Cookie &amp; Identity</text>
            <rect x="265" y="578" width="135" height="18" rx="3" fill="#78350f"/>
            <text x="332" y="591" text-anchor="middle" font-size="8.5" font-weight="700" fill="#fef3c7">T-08 Plaintext DB</text>


            <!-- TB-3: Core Application Logic (x=435, y=10, w=375, h=850) -->
            <rect x="435" y="10" width="375" height="850" rx="10" fill="#0c172e" stroke="#3b82f6" stroke-width="1.8" stroke-dasharray="5,3" fill-opacity="0.5"/>
            <rect x="445" y="20" width="355" height="24" rx="5" fill="#1e3a8a"/>
            <text x="622" y="36" text-anchor="middle" font-size="10" font-weight="700" fill="#dbeafe" font-family="'Plus Jakarta Sans'">TB-3: Core Application (Laravel 12 / PHP 8.3 Host)</text>

            <!-- Processes in TB-3 -->
            <!-- 1.0 Booking -->
            <rect x="450" y="60" width="165" height="90" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
            <text x="532" y="86" text-anchor="middle" font-size="11.5" font-weight="700" fill="#e2e8f0">1.0 Booking Lifecycle</text>
            <text x="532" y="103" text-anchor="middle" font-size="9" fill="#94a3b8">BookingController.php</text>
            <rect x="458" y="112" width="149" height="26" rx="4" fill="#7f1d1d" stroke="#f43f5e" stroke-width="1"/>
            <text x="532" y="128" text-anchor="middle" font-size="9" font-weight="800" fill="#fff">🚨 T-01 BOLA (Skor 40)</text>

            <!-- 2.0 Search -->
            <rect x="630" y="60" width="165" height="90" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
            <text x="712" y="86" text-anchor="middle" font-size="11.5" font-weight="700" fill="#e2e8f0">2.0 Search &amp; Catalog</text>
            <text x="712" y="103" text-anchor="middle" font-size="9" fill="#94a3b8">MarketplaceController.php</text>
            <rect x="638" y="112" width="149" height="26" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
            <text x="712" y="128" text-anchor="middle" font-size="8.5" font-weight="700" fill="#fef3c7">⚠️ T-04 Haversine DoS</text>

            <!-- 3.0 Chat -->
            <rect x="450" y="175" width="165" height="90" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
            <text x="532" y="201" text-anchor="middle" font-size="11.5" font-weight="700" fill="#e2e8f0">3.0 Chat Controller</text>
            <text x="532" y="218" text-anchor="middle" font-size="9" fill="#94a3b8">ChatController.php</text>
            <rect x="458" y="227" width="149" height="26" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
            <text x="532" y="243" text-anchor="middle" font-size="8.5" font-weight="700" fill="#fef3c7">⚠️ T-09 Hashids IDOR</text>

            <!-- 4.0 Payment -->
            <rect x="630" y="175" width="165" height="90" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
            <text x="712" y="201" text-anchor="middle" font-size="11.5" font-weight="700" fill="#e2e8f0">4.0 Payment Handler</text>
            <text x="712" y="218" text-anchor="middle" font-size="9" fill="#94a3b8">PaymentCallback.php</text>
            <rect x="638" y="227" width="149" height="26" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
            <text x="712" y="243" text-anchor="middle" font-size="8.5" font-weight="700" fill="#fef3c7">⚠️ T-03 Webhook Replay</text>

            <!-- 5.0 User Profile Model -->
            <rect x="450" y="290" width="165" height="85" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
            <text x="532" y="316" text-anchor="middle" font-size="11.5" font-weight="700" fill="#e2e8f0">5.0 User Profile Model</text>
            <text x="532" y="333" text-anchor="middle" font-size="9" fill="#94a3b8">app/Models/User.php</text>
            <rect x="458" y="342" width="149" height="22" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
            <text x="532" y="357" text-anchor="middle" font-size="8.5" font-weight="700" fill="#fef3c7">⚠️ T-06 Role Fillable</text>

            <!-- 6.0 Review & Report -->
            <rect x="630" y="290" width="165" height="85" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
            <text x="712" y="316" text-anchor="middle" font-size="11.5" font-weight="700" fill="#e2e8f0">6.0 Review &amp; Report</text>
            <text x="712" y="333" text-anchor="middle" font-size="9" fill="#94a3b8">UserReportController.php</text>
            <rect x="638" y="342" width="149" height="22" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
            <text x="712" y="357" text-anchor="middle" font-size="8.5" font-weight="700" fill="#fef3c7">⚠️ T-05 Stored XSS</text>

            <!-- D1: MySQL Database Server -->
            <g transform="translate(450, 420)">
              <path d="M 0 25 C 0 8, 345 8, 345 25 L 345 200 C 345 217, 0 217, 0 200 Z" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
              <path d="M 0 25 C 0 42, 345 42, 345 25" fill="none" stroke="#38bdf8" stroke-width="2"/>
              <text x="172" y="70" text-anchor="middle" font-size="13" font-weight="800" fill="#38bdf8">D1: MySQL Database Server (K5)</text>
              <text x="172" y="95" text-anchor="middle" font-size="9.5" fill="#cbd5e1">Tabel: users, bookings, services, messages, payments, sessions</text>
              <rect x="20" y="115" width="145" height="24" rx="4" fill="#0369a1"/>
              <text x="92" y="131" text-anchor="middle" font-size="9" font-weight="600" fill="#e0f2fe">F4: SQL &amp; Eloquent ORM</text>
              <rect x="180" y="115" width="145" height="24" rx="4" fill="#7f1d1d"/>
              <text x="252" y="131" text-anchor="middle" font-size="8.5" font-weight="700" fill="#fecaca">⚠️ T-08 Plaintext Session</text>
              <text x="172" y="165" text-anchor="middle" font-size="9" fill="#94a3b8">Koneksi internal TCP 3306 dilindungi Network ACL</text>
            </g>


            <!-- TB-4: Realtime Daemon & Storage (x=825, y=10, w=245, h=415) -->
            <rect x="825" y="10" width="245" height="415" rx="10" fill="#180e29" stroke="#a855f7" stroke-width="1.8" stroke-dasharray="5,3" fill-opacity="0.5"/>
            <rect x="835" y="20" width="225" height="24" rx="5" fill="#581c87"/>
            <text x="947" y="36" text-anchor="middle" font-size="10" font-weight="700" fill="#f3e8ff" font-family="'Plus Jakarta Sans'">TB-4: Daemon &amp; Storage</text>

            <!-- Reverb -->
            <rect x="840" y="60" width="215" height="145" rx="8" fill="#1e293b" stroke="#c084fc" stroke-width="1.5"/>
            <text x="947" y="90" text-anchor="middle" font-size="12.5" font-weight="700" fill="#f3e8ff">Laravel Reverb Engine</text>
            <text x="947" y="110" text-anchor="middle" font-size="9.5" fill="#d8b4fe">WebSocket Service (:8080)</text>
            <text x="947" y="128" text-anchor="middle" font-size="9" font-weight="600" fill="#c084fc">K4 Realtime Broadcaster</text>
            <rect x="855" y="142" width="185" height="45" rx="4" fill="#7f1d1d" stroke="#f43f5e" stroke-width="1"/>
            <text x="947" y="162" text-anchor="middle" font-size="10" font-weight="800" fill="#fff">🚨 T-02 Flooding DoS (40)</text>
            <text x="947" y="178" text-anchor="middle" font-size="8.5" fill="#fecaca">Route /api/test-latency tanpa auth</text>

            <!-- Local Storage -->
            <g transform="translate(840, 230)">
              <path d="M 0 18 C 0 5, 215 5, 215 18 L 215 140 C 215 153, 0 153, 0 140 Z" fill="#1e293b" stroke="#c084fc" stroke-width="1.5"/>
              <path d="M 0 18 C 0 31, 215 31, 215 18" fill="none" stroke="#c084fc" stroke-width="1.5"/>
              <text x="107" y="55" text-anchor="middle" font-size="12" font-weight="700" fill="#f3e8ff">D2: Local File Storage (K6)</text>
              <text x="107" y="75" text-anchor="middle" font-size="9.5" fill="#d8b4fe">public/storage/uploads</text>
              <rect x="15" y="90" width="185" height="30" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
              <text x="107" y="106" text-anchor="middle" font-size="9" font-weight="700" fill="#fef3c7">⚠️ T-07 Polyglot Upload (34)</text>
              <text x="107" y="117" text-anchor="middle" font-size="8" fill="#fde68a">MIME-only check bypass</text>
            </g>


            <!-- TB-5: Third-Party APIs (x=825, y=440, w=245, h=420) -->
            <rect x="825" y="440" width="245" height="420" rx="10" fill="#061c16" stroke="#10b981" stroke-width="1.8" stroke-dasharray="5,3" fill-opacity="0.5"/>
            <rect x="835" y="450" width="225" height="24" rx="5" fill="#064e3b"/>
            <text x="947" y="466" text-anchor="middle" font-size="10" font-weight="700" fill="#d1fae5" font-family="'Plus Jakarta Sans'">TB-5: Layanan Pihak Ketiga</text>

            <!-- Midtrans -->
            <rect x="840" y="490" width="215" height="150" rx="8" fill="#1e293b" stroke="#34d399" stroke-width="1.5"/>
            <text x="947" y="520" text-anchor="middle" font-size="12.5" font-weight="700" fill="#d1fae5">Midtrans Payment Gateway</text>
            <text x="947" y="540" text-anchor="middle" font-size="9.5" fill="#a7f3d0">Snap Checkout &amp; Webhook</text>
            <text x="947" y="558" text-anchor="middle" font-size="9" font-weight="600" fill="#34d399">K7 Payment Gateway</text>
            <rect x="855" y="572" width="185" height="45" rx="4" fill="#78350f" stroke="#f59e0b" stroke-width="1"/>
            <text x="947" y="592" text-anchor="middle" font-size="9.5" font-weight="700" fill="#fef3c7">⚠️ T-03 Secret Key Empty (39)</text>
            <text x="947" y="608" text-anchor="middle" font-size="8.5" fill="#fde68a">Webhook replay &amp; CSRF exempt</text>

            <!-- Google Maps -->
            <rect x="840" y="660" width="215" height="110" rx="8" fill="#1e293b" stroke="#34d399" stroke-width="1.5"/>
            <text x="947" y="695" text-anchor="middle" font-size="12.5" font-weight="700" fill="#d1fae5">Google Maps API (K10)</text>
            <text x="947" y="718" text-anchor="middle" font-size="9.5" fill="#a7f3d0">Geolocation &amp; Reverse Geocode</text>
            <text x="947" y="740" text-anchor="middle" font-size="9" font-weight="600" fill="#34d399">Client-side Map SDK</text>


            <!-- FLOW ARROWS (F1 to F10) -->
            <!-- F1: Browser -> Nginx -->
            <line x1="215" y1="110" x2="255" y2="110" stroke="#38bdf8" stroke-width="2" marker-end="url(#arr-blue)"/>
            <rect x="220" y="98" width="30" height="13" rx="2" fill="#0c4a6e"/>
            <text x="235" y="108" text-anchor="middle" font-size="7.5" font-weight="700" fill="#bae6fd">F1</text>

            <!-- F2: Nginx -> Laravel App -->
            <line x1="410" y1="110" x2="450" y2="110" stroke="#fb923c" stroke-width="2" marker-end="url(#arr-orange)"/>
            <rect x="415" y="98" width="30" height="13" rx="2" fill="#7c2d12"/>
            <text x="430" y="108" text-anchor="middle" font-size="7.5" font-weight="700" fill="#fed7aa">F2</text>

            <!-- F4: Core App -> DB -->
            <line x1="532" y1="375" x2="532" y2="420" stroke="#38bdf8" stroke-width="2" marker-end="url(#arr-blue)"/>
            <line x1="712" y1="375" x2="712" y2="420" stroke="#38bdf8" stroke-width="2" marker-end="url(#arr-blue)"/>

            <!-- F5: Core App -> Local Storage -->
            <line x1="795" y1="330" x2="840" y2="330" stroke="#c084fc" stroke-width="2" marker-end="url(#arr-purple)"/>
            <rect x="803" y="320" width="28" height="13" rx="2" fill="#581c87"/>
            <text x="817" y="330" text-anchor="middle" font-size="7.5" font-weight="700" fill="#e9d5ff">F5</text>

            <!-- F6 & F7: Payment <-> Midtrans -->
            <line x1="795" y1="220" x2="840" y2="520" stroke="#34d399" stroke-width="2" marker-end="url(#arr-green)"/>
            <line x1="840" y1="540" x2="795" y2="240" stroke="#34d399" stroke-width="1.8" stroke-dasharray="3,2" marker-end="url(#arr-green)"/>
            <rect x="805" y="370" width="30" height="13" rx="2" fill="#064e3b"/>
            <text x="820" y="380" text-anchor="middle" font-size="7.5" font-weight="700" fill="#a7f3d0">F6/7</text>

            <!-- F8: Core App -> Reverb -->
            <line x1="615" y1="200" x2="840" y2="135" stroke="#c084fc" stroke-width="2" marker-end="url(#arr-purple)"/>
            <rect x="715" y="160" width="28" height="13" rx="2" fill="#581c87"/>
            <text x="729" y="170" text-anchor="middle" font-size="7.5" font-weight="700" fill="#e9d5ff">F8</text>

            <!-- F3: Browser -> Reverb WebSocket -->
            <path d="M 215 130 C 350 40, 750 40, 840 80" fill="none" stroke="#c084fc" stroke-width="1.8" stroke-dasharray="4,2" marker-end="url(#arr-purple)"/>
            <rect x="490" y="32" width="45" height="13" rx="2" fill="#581c87"/>
            <text x="512" y="42" text-anchor="middle" font-size="7.5" font-weight="700" fill="#e9d5ff">F3 WSS</text>

          </svg>
        </div>

        <!-- Legend Bar Compact -->
        <div class="pt-1.5 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-400 shrink-0">
          <div class="flex items-center gap-4">
            <span class="flex items-center gap-1"><span class="w-3 h-2 rounded border border-cyan-400 bg-slate-800"></span> Entitas Luar</span>
            <span class="flex items-center gap-1"><span class="w-3 h-2 rounded-md border border-cyan-400 bg-slate-800"></span> Proses Inti</span>
            <span class="flex items-center gap-1"><span class="w-3 h-2 border-y border-cyan-400 bg-slate-800"></span> Data Store</span>
            <span class="flex items-center gap-1"><span class="w-4 h-0.5 border-b border-dashed border-rose-500"></span> Trust Boundary</span>
          </div>
          <span class="mono text-cyan-400 text-[10px] font-semibold">10 Aliran Data (F1-F10) &amp; 10 Titik Ancaman (T01-T10)</span>
        </div>
      </div>

    </div>


    <!-- ====================================================== -->
    <!-- RIGHT COLUMN (Cols: 5 / 12) - Metrics & Threat Matrix  -->
    <!-- ====================================================== -->
    <div class="col-span-5 flex flex-col justify-between gap-3.5 h-full overflow-hidden">
      
      <!-- ROW 1: Executive Metrics & Risk Profile (Height: ~210px) -->
      <div class="glass-box p-3.5 flex flex-col justify-between border-slate-800 shrink-0" style="height: 210px;">
        <div class="flex items-center justify-between pb-1.5 border-b border-slate-800">
          <span class="font-bold text-slate-200 flex items-center gap-1.5 text-xs">
            <svg class="w-3.5 h-3.5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            4. Ringkasan Hasil &amp; Metrik STRIDE-DREAD
          </span>
          <span class="mono text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded">Rata-rata: {avg_dread}/50</span>
        </div>

        <div class="grid grid-cols-12 gap-3 items-center my-auto">
          <!-- Risk Distribution Progress (Cols: 5) -->
          <div class="col-span-5 space-y-1.5 text-xs">
            <div>
              <div class="flex justify-between text-[11px] mb-0.5">
                <span class="text-rose-400 font-bold">CRITICAL (40-50)</span>
                <span class="mono font-bold text-rose-300">{critical_count} (20%)</span>
              </div>
              <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div class="bg-rose-500 h-full rounded-full" style="width: 20%"></div>
              </div>
            </div>
            <div>
              <div class="flex justify-between text-[11px] mb-0.5">
                <span class="text-amber-400 font-bold">HIGH (25-39)</span>
                <span class="mono font-bold text-amber-300">{high_count} (70%)</span>
              </div>
              <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div class="bg-amber-500 h-full rounded-full" style="width: 70%"></div>
              </div>
            </div>
            <div>
              <div class="flex justify-between text-[11px] mb-0.5">
                <span class="text-emerald-400 font-bold">LOW/MITIGATED (&le;14)</span>
                <span class="mono font-bold text-emerald-300">{low_count} (10%)</span>
              </div>
              <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div class="bg-emerald-500 h-full rounded-full" style="width: 10%"></div>
              </div>
            </div>
          </div>

          <!-- STRIDE Badges Grid (Cols: 7) -->
          <div class="col-span-7 bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
            <span class="text-[10px] text-slate-400 block mb-1.5 font-semibold uppercase tracking-wider">Distribusi STRIDE:</span>
            <div class="grid grid-cols-3 gap-1.5 text-[10.5px]">
              <div class="bg-slate-950 px-2 py-1 rounded flex justify-between border border-slate-800/80">
                <span class="text-slate-400">Tamper</span>
                <span class="mono font-bold text-cyan-400">6</span>
              </div>
              <div class="bg-slate-950 px-2 py-1 rounded flex justify-between border border-slate-800/80">
                <span class="text-slate-400">Info</span>
                <span class="mono font-bold text-cyan-400">5</span>
              </div>
              <div class="bg-slate-950 px-2 py-1 rounded flex justify-between border border-slate-800/80">
                <span class="text-slate-400">Spoof</span>
                <span class="mono font-bold text-cyan-400">2</span>
              </div>
              <div class="bg-slate-950 px-2 py-1 rounded flex justify-between border border-slate-800/80">
                <span class="text-slate-400">DoS</span>
                <span class="mono font-bold text-cyan-400">2</span>
              </div>
              <div class="bg-slate-950 px-2 py-1 rounded flex justify-between border border-slate-800/80">
                <span class="text-slate-400">Elevate</span>
                <span class="mono font-bold text-cyan-400">2</span>
              </div>
              <div class="bg-slate-950 px-2 py-1 rounded flex justify-between border border-slate-800/80">
                <span class="text-slate-400">Repudi</span>
                <span class="mono font-bold text-slate-500">0</span>
              </div>
            </div>
          </div>
        </div>

        <div class="pt-1.5 border-t border-slate-800/80 flex items-center justify-between text-[10px]">
          <span class="text-slate-300">Prioritas Utama: <strong class="text-rose-400">T-01 BOLA Booking</strong> &amp; <strong class="text-rose-400">T-02 Reverb Socket DoS</strong></span>
          <span class="text-emerald-400 font-bold bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800/60">T-10 APP_DEBUG=false ✓</span>
        </div>
      </div>

      <!-- ROW 2: Compact Threat & Mitigation Matrix (Height: ~970px) -->
      <div class="glass-box p-3.5 flex flex-col justify-between border-slate-800 flex-1 overflow-hidden">
        <div class="flex items-center justify-between pb-1.5 border-b border-slate-800 shrink-0 mb-1.5">
          <span class="font-bold text-slate-200 flex items-center gap-1.5 text-xs">
            <svg class="w-3.5 h-3.5 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            5. Daftar Lengkap 10 Ancaman &amp; Rekomendasi Mitigasi
          </span>
          <span class="text-[10px] text-slate-400">10 / 10 Terisi Sesuai Excel</span>
        </div>

        <!-- 10 Compact Threat Rows -->
        <div class="space-y-1.5 overflow-hidden flex-1 flex flex-col justify-between">
"""

for t in threats:
    is_crit = (t['level'] == 'CRITICAL')
    is_low = (t['level'] == 'LOW')
    
    badge_bg = "bg-rose-950 text-rose-300 border-rose-800/80" if is_crit else ("bg-emerald-950 text-emerald-300 border-emerald-800/80" if is_low else "bg-amber-950 text-amber-300 border-amber-800/80")
    border_accent = "border-l-4 border-l-rose-500" if is_crit else ("border-l-4 border-l-emerald-500" if is_low else "border-l-4 border-l-amber-500")
    
    stride_str = ",".join(t['stride'])
    
    # shorten desc to crisp sentence
    short_desc = t['desc']
    if len(short_desc) > 115:
        short_desc = short_desc[:115] + "..."
        
    short_mitigasi = t['mitigasi']
    if len(short_mitigasi) > 130:
        short_mitigasi = short_mitigasi[:130] + "..."
        
    html += f"""
          <div class="p-2 rounded-lg bg-slate-900/90 border border-slate-800/80 {border_accent} flex flex-col justify-between text-xs" style="height: 87px;">
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center gap-1.5 overflow-hidden">
                <span class="mono font-black text-cyan-400 text-[11px] bg-slate-950 px-1.5 py-0.5 rounded shrink-0">{t['id']}</span>
                <span class="mono text-[9px] bg-slate-800 text-slate-300 px-1 rounded shrink-0 font-bold">{stride_str}</span>
                <span class="font-bold text-slate-200 text-[11px] truncate" title="{t['desc']}">{short_desc}</span>
              </div>
              <div class="shrink-0 flex items-center gap-1.5">
                <span class="mono font-extrabold text-[10px] text-white bg-slate-800 px-1.5 py-0.5 rounded">{t['total']}/50</span>
                <span class="mono font-bold text-[9px] px-1.5 py-0.5 rounded border {badge_bg}">{t['level']}</span>
              </div>
            </div>

            <div class="grid grid-cols-12 gap-2 text-[10px] mt-1 items-center">
              <div class="col-span-5 truncate text-slate-400" title="{t['bukti']}">
                <span class="text-slate-500 font-semibold">Bukti:</span> <code class="mono text-rose-300/90 bg-slate-950 px-1 rounded">{t['bukti'][:38]}...</code>
              </div>
              <div class="col-span-7 truncate text-slate-300" title="{t['mitigasi']}">
                <span class="text-emerald-400 font-semibold">Solusi:</span> {short_mitigasi}
              </div>
            </div>
          </div>
    """

html += f"""
        </div>

        <!-- ROW 3: Strategic Roadmap Strip (Height: ~95px) -->
        <div class="mt-2 pt-2 border-t border-slate-800 grid grid-cols-3 gap-2 text-[10px] shrink-0">
          <div class="p-2 rounded bg-rose-950/20 border border-rose-500/30">
            <div class="font-bold text-rose-300 mb-0.5 uppercase tracking-wide">Fase 1: Segera (&lt;48 Jam)</div>
            <p class="text-slate-300 leading-tight">Un-comment auth check di <code class="text-rose-200">BookingController:230</code> (T-01) &amp; hapus route publik <code class="text-rose-200">/test-latency</code> (T-02).</p>
          </div>
          <div class="p-2 rounded bg-amber-950/20 border border-amber-500/30">
            <div class="font-bold text-amber-300 mb-0.5 uppercase tracking-wide">Fase 2: Hardening (1-2 Minggu)</div>
            <p class="text-slate-300 leading-tight">Set <code class="text-amber-200">SESSION_ENCRYPT=true</code> (T-08), hapus 'role' dari fillable User (T-06), &amp; sanitasi strip_tags (T-05).</p>
          </div>
          <div class="p-2 rounded bg-cyan-950/20 border border-cyan-500/30">
            <div class="font-bold text-cyan-300 mb-0.5 uppercase tracking-wide">Fase 3: Arsitektur (1 Bulan)</div>
            <p class="text-slate-300 leading-tight">Pasang Redis spatial cache untuk Haversine (T-04), re-encode WebP image (T-07), &amp; pasang Cloudflare WAF.</p>
          </div>
        </div>

      </div>

    </div>

  </div>

  <!-- ======================================================== -->
  <!-- FOOTER (Height: ~26px)                                   -->
  <!-- ======================================================== -->
  <footer class="glass-box px-4 py-1.5 flex items-center justify-between text-[10.5px] text-slate-400 border-slate-800 shrink-0">
    <div class="flex items-center gap-2">
      <span class="inline-block w-2 h-2 rounded-full bg-emerald-400"></span>
      <span>FindServices Security Audit Report &bull; Data Source: <strong class="text-slate-200">1. template_baru_Praktikum_STRIDE-DREAD.xlsx</strong></span>
    </div>
    <div class="flex items-center gap-4">
      <span>Rasio Gambar: <strong class="text-cyan-400 mono">4:3 (1920 &times; 1440)</strong></span>
      <span>&copy; 2026 Praktikum Keamanan Sistem Informasi</span>
    </div>
  </footer>

</body>
</html>
"""

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML 4:3 generated successfully.")
