import re
import openpyxl

# 1. Read dfd_threat_modeling copy.html
with open(r'c:\laragon\www\FindServices\keamanan_sistem_informasi\dfd_threat_modeling copy.html', 'r', encoding='utf-8') as f:
    copy_html = f.read()

# Extract the exact SVG
svg_match = re.search(r'(<svg\s+viewBox="0 0 1340 760".*?</svg>)', copy_html, re.DOTALL)
if not svg_match:
    raise ValueError("Could not find SVG in dfd_threat_modeling copy.html")

svg_content = svg_match.group(1)
print(f"Extracted SVG ({len(svg_content)} chars)")

# 2. Read and update infografik_threat_modeling_4x3.html
with open(r'c:\laragon\www\FindServices\keamanan_sistem_informasi\infografik_threat_modeling_4x3.html', 'r', encoding='utf-8') as f:
    html_4x3 = f.read()

# We replace the SVG container inside infografik_threat_modeling_4x3.html
# The current SVG container is in ROW 2 of left column
# Let's find ROW 2: DFD Level-1
new_dfd_section = f"""<!-- ROW 2: DFD Level-1 & Trust Boundaries Diagram (Height: ~950px) -->
      <div class="glass-box p-3.5 flex flex-col justify-between border-slate-800 flex-1 overflow-hidden">
        <div class="flex items-center justify-between pb-1.5 border-b border-slate-800 shrink-0">
          <span class="font-bold text-slate-200 flex items-center gap-1.5 text-xs">
            <svg class="w-3.5 h-3.5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1.5 3 3.5 3h9c2 0 3.5-1 3.5-3V7c0-2-1.5-3-3.5-3h-9C5.5 4 4 5 4 7z"/></svg>
            3. Data Flow Diagram (DFD Level-1) &amp; 5 Trust Boundaries (Clean Orthogonal Flow)
          </span>
          <div class="flex items-center gap-3 text-[10.5px]">
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-rose-500"></span> TB-1 Public</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span> TB-2 Ingress</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span> TB-3 Core App</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-purple-500"></span> TB-4 Daemon</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> TB-5 Storage</span>
          </div>
        </div>

        <!-- SVG DFD Container with High-Contrast Crisp Background -->
        <div class="w-full flex-1 flex items-center justify-center p-2 my-1 bg-white rounded-xl border border-slate-300 shadow-inner overflow-hidden">
          {svg_content}
        </div>

        <!-- Legend Bar Compact matching dfd_threat_modeling copy.html -->
        <div class="pt-1.5 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-300 shrink-0">
          <div class="flex items-center gap-4">
            <span class="flex items-center gap-1"><span class="w-3.5 h-2.5 rounded border border-rose-600 bg-white inline-block"></span> <strong>[ ]</strong> Entitas Luar</span>
            <span class="flex items-center gap-1"><span class="w-3.5 h-2.5 rounded-md border border-blue-600 bg-blue-50 inline-block"></span> <strong>( )</strong> Proses / Controller</span>
            <span class="flex items-center gap-1"><span class="w-3.5 h-2.5 border border-emerald-600 bg-emerald-50 inline-block"></span> <strong>[=]</strong> Data Store (MySQL/Disk)</span>
            <span class="flex items-center gap-1"><span class="w-4 h-0.5 border-b-2 border-dashed border-rose-500 inline-block"></span> Trust Boundary</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="mono bg-slate-900 text-rose-300 px-1.5 py-0.5 rounded border border-rose-800/60 font-bold">[T-x] Titik Ancaman</span>
            <span class="mono bg-slate-900 text-cyan-300 px-1.5 py-0.5 rounded border border-cyan-800/60 font-bold">F1–F10 Aliran Data</span>
          </div>
        </div>
      </div>"""

# Replace in html_4x3
pattern = r'<!-- ROW 2: DFD Level-1.*?<!-- Legend Bar Compact.*?</div>\s*</div>'
html_4x3_updated = re.sub(pattern, new_dfd_section, html_4x3, flags=re.DOTALL)

with open(r'c:\laragon\www\FindServices\keamanan_sistem_informasi\infografik_threat_modeling_4x3.html', 'w', encoding='utf-8') as f:
    f.write(html_4x3_updated)

print("Updated infografik_threat_modeling_4x3.html with clean orthogonal DFD.")

# 3. Also update Section 3 in infografik_threat_modeling.html (full long version)
with open(r'c:\laragon\www\FindServices\keamanan_sistem_informasi\infografik_threat_modeling.html', 'r', encoding='utf-8') as f:
    html_long = f.read()

# Replace SVG in html_long
pattern_long = r'<svg viewBox="0 0 1340 760".*?</svg>'
html_long_updated = re.sub(pattern_long, svg_content, html_long, flags=re.DOTALL)
with open(r'c:\laragon\www\FindServices\keamanan_sistem_informasi\infografik_threat_modeling.html', 'w', encoding='utf-8') as f:
    f.write(html_long_updated)
print("Updated infografik_threat_modeling.html with clean orthogonal DFD.")
