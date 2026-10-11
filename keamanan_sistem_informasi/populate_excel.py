import zipfile, io, os, shutil
import xml.etree.ElementTree as ET

# Paths
orig_path = 'keamanan_sistem_informasi/Latihan_STRIDE_DREAD_1_backup.xlsx'
target_path = 'keamanan_sistem_informasi/Latihan_STRIDE_DREAD_1.xlsx'

threats = [
    {
        'id': 'CVE-2023-28438 / CWE-285',
        'desc': 'Broken Object Level Authorization (BOLA/IDOR) pada perubahan status Booking (BookingController::updateStatus baris 230 dinonaktifkan)',
        'stride_S': 0, 'stride_T': 1, 'stride_R': 0, 'stride_I': 1, 'stride_D': 0, 'stride_E': 1,
        'dread_Damage': 8, 'dread_Reproducibility': 9, 'dread_Exploitability': 8, 'dread_AffectedUsers': 8, 'dread_Discoverability': 7,
        'note': 'Cek kepemilikan auth id dinonaktifkan sehingga pengguna lain dapat memanipulasi status order sembarang pengguna.'
    },
    {
        'id': 'CVE-2024-21516 / CWE-918',
        'desc': 'Server-Side Request Forgery (SSRF) & Unrestricted File Upload via validasi ekstensi/tipe MIME gambar (Image Upload)',
        'stride_S': 0, 'stride_T': 1, 'stride_R': 0, 'stride_I': 1, 'stride_D': 0, 'stride_E': 1,
        'dread_Damage': 8, 'dread_Reproducibility': 7, 'dread_Exploitability': 6, 'dread_AffectedUsers': 7, 'dread_Discoverability': 6,
        'note': 'Upload gambar hanya validasi mime image tanpa verifikasi isi binari mendalam atau sanitasi payload SVG/WebP bermasalah.'
    },
    {
        'id': 'CVE-2023-45133 / CWE-306',
        'desc': 'Missing Authentication & Authorization pada Webhook / API Callback Midtrans (PaymentCallbackController)',
        'stride_S': 1, 'stride_T': 1, 'stride_R': 1, 'stride_I': 0, 'stride_D': 0, 'stride_E': 0,
        'dread_Damage': 9, 'dread_Reproducibility': 8, 'dread_Exploitability': 7, 'dread_AffectedUsers': 8, 'dread_Discoverability': 7,
        'note': 'Verifikasi SHA512 rentan bypass jika secret key kosong/lemah di env, atau replay attack karena ketiadaan nonce/timestamp check.'
    },
    {
        'id': 'CVE-2022-31279 / CWE-862',
        'desc': 'Improper Access Control & BOLA pada Endpoint Pesan Chat (ChatController::destroy & context viewer)',
        'stride_S': 0, 'stride_T': 1, 'stride_R': 1, 'stride_I': 1, 'stride_D': 0, 'stride_E': 0,
        'dread_Damage': 6, 'dread_Reproducibility': 8, 'dread_Exploitability': 7, 'dread_AffectedUsers': 6, 'dread_Discoverability': 6,
        'note': 'Pengguna dapat menghapus atau melihat riwayat percakapan pihak lain dengan manipulasi hash ID booking/user.'
    },
    {
        'id': 'CVE-2023-40028 / CWE-209',
        'desc': '[TERMITIGASI] Information Disclosure via APP_DEBUG & Error Trace (Status: Dinonaktifkan di .env)',
        'stride_S': 0, 'stride_T': 0, 'stride_R': 0, 'stride_I': 1, 'stride_D': 0, 'stride_E': 0,
        'dread_Damage': 2, 'dread_Reproducibility': 1, 'dread_Exploitability': 1, 'dread_AffectedUsers': 1, 'dread_Discoverability': 1,
        'note': 'Termitigasi: Nilai APP_DEBUG telah diubah menjadi false pada .env sehingga detail exception/kredensial tidak lagi terekspos.'
    },
    {
        'id': 'CVE-2023-38035 / CWE-770',
        'desc': 'Denial of Service (DoS) via Unrestricted File Upload Size (10MB) & Uncached Heavy Haversine Geolocation Query',
        'stride_S': 0, 'stride_T': 0, 'stride_R': 0, 'stride_I': 0, 'stride_D': 1, 'stride_E': 0,
        'dread_Damage': 7, 'dread_Reproducibility': 8, 'dread_Exploitability': 8, 'dread_AffectedUsers': 8, 'dread_Discoverability': 7,
        'note': 'Endpoint marketplace dan upload gambar 10MB tanpa rate-limiting membebani CPU, RAM, dan I/O server web.'
    },
    {
        'id': 'CVE-2024-21501 / CWE-79',
        'desc': 'Stored Cross-Site Scripting (XSS) pada Kolom Ulasan (Review), Deskripsi Jasa, dan Catatan Booking',
        'stride_S': 1, 'stride_T': 1, 'stride_R': 0, 'stride_I': 1, 'stride_D': 0, 'stride_E': 1,
        'dread_Damage': 7, 'dread_Reproducibility': 8, 'dread_Exploitability': 7, 'dread_AffectedUsers': 8, 'dread_Discoverability': 7,
        'note': 'Payload script tersimpan dapat dieksekusi di browser admin atau pengguna lain jika sanitasi output HTML/v-html terlewat.'
    },
    {
        'id': 'CVE-2022-31129 / CWE-384',
        'desc': 'Session Hijacking & Insecure Session Configuration (SESSION_ENCRYPT=false, HTTP-only cookie missing over tunnel)',
        'stride_S': 1, 'stride_T': 0, 'stride_R': 0, 'stride_I': 1, 'stride_D': 0, 'stride_E': 1,
        'dread_Damage': 8, 'dread_Reproducibility': 7, 'dread_Exploitability': 6, 'dread_AffectedUsers': 7, 'dread_Discoverability': 6,
        'note': 'Sesi pengguna tidak dienkripsi dalam tabel sessions DB dan rentan jika MITM terjadi pada jaringan lokal/tunnel non-TLS murni.'
    },
    {
        'id': 'CVE-2023-22809 / CWE-269',
        'desc': 'Privilege Escalation via Mass Assignment pada Model User (Protected Fillable Role attribute exposure)',
        'stride_S': 1, 'stride_T': 1, 'stride_R': 0, 'stride_I': 0, 'stride_D': 0, 'stride_E': 1,
        'dread_Damage': 9, 'dread_Reproducibility': 8, 'dread_Exploitability': 7, 'dread_AffectedUsers': 7, 'dread_Discoverability': 6,
        'note': 'Atribut role terdaftar di array protected fillable User model, memungkinkan injeksi parameter role=admin jika form request longgar.'
    },
    {
        'id': 'CVE-2023-34449 / CWE-770',
        'desc': 'Denial of Service & Message Flooding via WebSocket Laravel Reverb (/test-latency & chat events)',
        'stride_S': 1, 'stride_T': 0, 'stride_R': 1, 'stride_I': 0, 'stride_D': 1, 'stride_E': 0,
        'dread_Damage': 6, 'dread_Reproducibility': 9, 'dread_Exploitability': 9, 'dread_AffectedUsers': 8, 'dread_Discoverability': 8,
        'note': 'Endpoint /api/test-latency tanpa autentikasi dapat dipicu untuk membanjiri channel Reverb dan menghabiskan resource daemon.'
    }
]

# Read original zip
zf_in = zipfile.ZipFile(orig_path, 'r')

# 1. Update sharedStrings.xml
ss_xml = zf_in.read('xl/sharedStrings.xml')
ss_tree = ET.fromstring(ss_xml)
ns_main = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'

existing_strings = []
for si in ss_tree.findall(f'{{{ns_main}}}si'):
    t = ''.join([elem.text or '' for elem in si.iter(f'{{{ns_main}}}t')])
    existing_strings.append(t)

string_to_idx = {s: i for i, s in enumerate(existing_strings)}

def get_or_add_string(text):
    if text in string_to_idx:
        return string_to_idx[text]
    idx = len(existing_strings)
    existing_strings.append(text)
    string_to_idx[text] = idx
    si_elem = ET.SubElement(ss_tree, f'{{{ns_main}}}si')
    t_elem = ET.SubElement(si_elem, f'{{{ns_main}}}t')
    t_elem.text = text
    return idx

# Pre-add all strings
for t in threats:
    get_or_add_string(t['id'])
    get_or_add_string(t['desc'])
    get_or_add_string(t['note'])

ss_tree.attrib['count'] = str(len(existing_strings) + 20)
ss_tree.attrib['uniqueCount'] = str(len(existing_strings))

new_ss_bytes = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n' + ET.tostring(ss_tree, encoding='utf-8')

# 2. Update sheet2.xml
s2_xml = zf_in.read('xl/worksheets/sheet2.xml')
s2_tree = ET.fromstring(s2_xml)
sheetData = s2_tree.find(f'{{{ns_main}}}sheetData')

p_totals = []
for t in threats:
    p_totals.append(t['dread_Damage'] + t['dread_Reproducibility'] + t['dread_Exploitability'] + t['dread_AffectedUsers'] + t['dread_Discoverability'])

sorted_totals = sorted(p_totals, reverse=True)
ranks = [sorted_totals.index(p) + 1 for p in p_totals]

for idx, t in enumerate(threats):
    row_num = 5 + idx
    row_elem = sheetData.find(f'{{{ns_main}}}row[@r="{row_num}"]')
    
    def set_cell(col, val=None, cell_type=None, formula=None):
        cell_ref = f'{col}{row_num}'
        cell = row_elem.find(f'{{{ns_main}}}c[@r="{cell_ref}"]')
        if cell is None:
            cell = ET.SubElement(row_elem, f'{{{ns_main}}}c', {'r': cell_ref})
        for elem in list(cell):
            cell.remove(elem)
        if cell_type:
            cell.attrib['t'] = cell_type
        elif 't' in cell.attrib:
            del cell.attrib['t']
            
        if formula is not None:
            f_elem = ET.SubElement(cell, f'{{{ns_main}}}f')
            f_elem.text = formula
            cell.attrib['t'] = 'str'
            
        if val is not None:
            v_elem = ET.SubElement(cell, f'{{{ns_main}}}v')
            v_elem.text = str(val)

    # Col B: ID (string)
    set_cell('B', val=get_or_add_string(t['id']), cell_type='s')
    # Col C: Deskripsi (string)
    set_cell('C', val=get_or_add_string(t['desc']), cell_type='s')
    # Col D-I: STRIDE (0 or 1)
    set_cell('D', val=t['stride_S'])
    set_cell('E', val=t['stride_T'])
    set_cell('F', val=t['stride_R'])
    set_cell('G', val=t['stride_I'])
    set_cell('H', val=t['stride_D'])
    set_cell('I', val=t['stride_E'])
    # Col J: Formula J (SUM)
    stride_sum = t['stride_S'] + t['stride_T'] + t['stride_R'] + t['stride_I'] + t['stride_D'] + t['stride_E']
    set_cell('J', val=stride_sum, formula=f'IF(COUNT(D{row_num}:I{row_num})=0,"",SUM(D{row_num}:I{row_num}))')
    
    # Col K-O: DREAD scores
    set_cell('K', val=t['dread_Damage'])
    set_cell('L', val=t['dread_Reproducibility'])
    set_cell('M', val=t['dread_Exploitability'])
    set_cell('N', val=t['dread_AffectedUsers'])
    set_cell('O', val=t['dread_Discoverability'])
    
    # Col P: Total DREAD
    p_tot = p_totals[idx]
    set_cell('P', val=p_tot, formula=f'IF(COUNT(K{row_num}:O{row_num})=5,SUM(K{row_num}:O{row_num}),"")')
    
    # Col Q: Level Risiko
    risk_level = 'CRITICAL' if p_tot >= 40 else ('HIGH' if p_tot >= 30 else ('MEDIUM' if p_tot >= 20 else 'LOW'))
    set_cell('Q', val=risk_level, formula=f'IF(P{row_num}="","",IF(P{row_num}>=DREAD_Guidelines!$B$13,"CRITICAL",IF(P{row_num}>=DREAD_Guidelines!$B$14,"HIGH",IF(P{row_num}>=DREAD_Guidelines!$B$15,"MEDIUM","LOW"))))')
    
    # Col R: Prioritas (Rank)
    rank_val = ranks[idx]
    set_cell('R', val=rank_val, formula=f'IF(P{row_num}="","",RANK(P{row_num},$P$5:$P$44,0))')
    
    # Col S: Catatan
    set_cell('S', val=get_or_add_string(t['note']), cell_type='s')

# Rows 15..44 clear shared references
for row_num in range(15, 45):
    row_elem = sheetData.find(f'{{{ns_main}}}row[@r="{row_num}"]')
    if row_elem is not None:
        for col in ['J', 'P', 'Q', 'R']:
            c = row_elem.find(f'{{{ns_main}}}c[@r="{col}{row_num}"]')
            if c is not None:
                for elem in list(c):
                    c.remove(elem)
                if col == 'J':
                    f = ET.SubElement(c, f'{{{ns_main}}}f')
                    f.text = f'IF(COUNT(D{row_num}:I{row_num})=0,"",SUM(D{row_num}:I{row_num}))'
                elif col == 'P':
                    f = ET.SubElement(c, f'{{{ns_main}}}f')
                    f.text = f'IF(COUNT(K{row_num}:O{row_num})=5,SUM(K{row_num}:O{row_num}),"")'
                elif col == 'Q':
                    f = ET.SubElement(c, f'{{{ns_main}}}f')
                    f.text = f'IF(P{row_num}="","",IF(P{row_num}>=DREAD_Guidelines!$B$13,"CRITICAL",IF(P{row_num}>=DREAD_Guidelines!$B$14,"HIGH",IF(P{row_num}>=DREAD_Guidelines!$B$15,"MEDIUM","LOW"))))'
                elif col == 'R':
                    f = ET.SubElement(c, f'{{{ns_main}}}f')
                    f.text = f'IF(P{row_num}="","",RANK(P{row_num},$P$5:$P$44,0))'

new_s2_bytes = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n' + ET.tostring(s2_tree, encoding='utf-8')

# 3. Update sheet3.xml (Ringkasan)
s3_xml = zf_in.read('xl/worksheets/sheet3.xml')
s3_tree = ET.fromstring(s3_xml)

crit_count = sum(1 for p in p_totals if p >= 40)
high_count = sum(1 for p in p_totals if 30 <= p < 40)
med_count = sum(1 for p in p_totals if 20 <= p < 30)
low_count = sum(1 for p in p_totals if p < 20)
tot_count = len(threats)

stride_s = sum(t['stride_S'] for t in threats)
stride_t = sum(t['stride_T'] for t in threats)
stride_r = sum(t['stride_R'] for t in threats)
stride_i = sum(t['stride_I'] for t in threats)
stride_d = sum(t['stride_D'] for t in threats)
stride_e = sum(t['stride_E'] for t in threats)

avg_dread = round(sum(p_totals) / len(p_totals), 1)
max_dread = max(p_totals)
top1_desc = threats[ranks.index(1)]['desc']
top1_str_idx = get_or_add_string(top1_desc)

def set_s3_val(cell_ref, val, is_str=False):
    c = s3_tree.find(f'.//{{{ns_main}}}c[@r="{cell_ref}"]')
    if c is not None:
        v = c.find(f'{{{ns_main}}}v')
        if v is None:
            v = ET.SubElement(c, f'{{{ns_main}}}v')
        v.text = str(val)
        if is_str:
            c.attrib['t'] = 's'

set_s3_val('C5', crit_count)
set_s3_val('C6', high_count)
set_s3_val('C7', med_count)
set_s3_val('C8', low_count)
set_s3_val('C9', tot_count)

set_s3_val('C12', stride_s)
set_s3_val('C13', stride_t)
set_s3_val('C14', stride_r)
set_s3_val('C15', stride_i)
set_s3_val('C16', stride_d)
set_s3_val('C17', stride_e)

set_s3_val('C20', avg_dread)
set_s3_val('C21', max_dread)
set_s3_val('C22', top1_str_idx, is_str=True)

new_s3_bytes = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n' + ET.tostring(s3_tree, encoding='utf-8')

# 4. Write back new zip file
temp_out = 'keamanan_sistem_informasi/temp_out.xlsx'
with zipfile.ZipFile(temp_out, 'w', compression=zipfile.ZIP_DEFLATED) as zf_out:
    for item in zf_in.infolist():
        if item.filename == 'xl/sharedStrings.xml':
            zf_out.writestr(item, new_ss_bytes)
        elif item.filename == 'xl/worksheets/sheet2.xml':
            zf_out.writestr(item, new_s2_bytes)
        elif item.filename == 'xl/worksheets/sheet3.xml':
            zf_out.writestr(item, new_s3_bytes)
        else:
            zf_out.writestr(item, zf_in.read(item.filename))

zf_in.close()

if os.path.exists(target_path):
    os.remove(target_path)
shutil.move(temp_out, target_path)
print('Successfully updated Excel workbook:', target_path)
