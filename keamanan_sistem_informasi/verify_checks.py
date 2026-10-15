import openpyxl

wb_path = 'keamanan_sistem_informasi/1. template_baru_Praktikum_STRIDE-DREAD.xlsx'
wb = openpyxl.load_workbook(wb_path, data_only=False)

ws_stride = wb['STRIDE_DREAD_Template']
ws_prof = wb['Profil_Aplikasi']

print("\n=== SIMULATED CHECKS ===")
# 1. Bagian A terisi:
b5_9 = [ws_prof[f'B{i}'].value for i in range(5, 10)]
print("1. Bagian A terisi (COUNTA B5:B9):", len([x for x in b5_9 if x is not None and str(x).strip() != '']), "/ 5 ->", "OK" if len([x for x in b5_9 if x is not None and str(x).strip() != '']) >= 5 else "PERIKSA")

# 2. Komponen:
b15_24 = [ws_prof[f'B{i}'].value for i in range(15, 25)]
print("2. Komponen terisi (COUNTA B15:B24):", len([x for x in b15_24 if x is not None and str(x).strip() != '']), ">= 4 ->", "OK" if len([x for x in b15_24 if x is not None and str(x).strip() != '']) >= 4 else "PERIKSA")

# 3. Aliran data:
b30_39 = [ws_prof[f'B{i}'].value for i in range(30, 40)]
print("3. Aliran data terisi (COUNTA B30:B39):", len([x for x in b30_39 if x is not None and str(x).strip() != '']), ">= 4 ->", "OK" if len([x for x in b30_39 if x is not None and str(x).strip() != '']) >= 4 else "PERIKSA")

# 4. Trust boundary:
b45_49 = [ws_prof[f'B{i}'].value for i in range(45, 50)]
print("4. Trust boundary terisi (COUNTA B45:B49):", len([x for x in b45_49 if x is not None and str(x).strip() != '']), ">= 2 ->", "OK" if len([x for x in b45_49 if x is not None and str(x).strip() != '']) >= 2 else "PERIKSA")

# 5. Jumlah ancaman:
c5_44 = [ws_stride[f'C{i}'].value for i in range(5, 45)]
c_filled = [x for x in c5_44 if x is not None and str(x).strip() != '']
print("5. Jumlah ancaman (COUNTA C5:C44):", len(c_filled), ">= 6 ->", "OK" if len(c_filled) >= 6 else "PERIKSA")

# 6. Ancaman tanpa ID:
b5_44 = [ws_stride[f'B{i}'].value for i in range(5, 45)]
tanpa_id = sum(1 for c, b in zip(c5_44, b5_44) if c and not b)
print("6. Ancaman tanpa ID:", tanpa_id, "== 0 ->", "OK" if tanpa_id == 0 else "PERIKSA")

# 7. ID kembar:
b_filled = [b for b in b5_44 if b and str(b).strip() != '']
kembar = len(b_filled) - len(set(b_filled))
print("7. ID kembar:", kembar, "== 0 ->", "OK" if kembar == 0 else "PERIKSA")

# 8. Deskripsi terlalu pendek (< 40):
pendek = sum(1 for c in c_filled if len(str(c)) < 40)
print("8. Deskripsi < 40 karakter:", pendek, "== 0 ->", "OK" if pendek == 0 else "PERIKSA")

# 9. Ancaman belum punya kategori STRIDE:
no_stride = 0
stride_counts = []
e_counts = 0
for i in range(5, 5 + len(c_filled)):
    stride_sum = sum(ws_stride[f'{col}{i}'].value or 0 for col in ['D', 'E', 'F', 'G', 'H', 'I'])
    stride_counts.append(stride_sum)
    if stride_sum == 0:
        no_stride += 1
    if ws_stride[f'I{i}'].value == 1:
        e_counts += 1
print("9. Ancaman tanpa STRIDE:", no_stride, "== 0 ->", "OK" if no_stride == 0 else "PERIKSA")

# 10. Skor DREAD belum lengkap:
incomplete_dread = 0
for i in range(5, 5 + len(c_filled)):
    scores = [ws_stride[f'{col}{i}'].value for col in ['K', 'L', 'M', 'N', 'O']]
    if any(s is None for s in scores):
        incomplete_dread += 1
print("10. Skor DREAD belum lengkap:", incomplete_dread, "== 0 ->", "OK" if incomplete_dread == 0 else "PERIKSA")

# 12. Ancaman dengan >= 4 STRIDE:
four_stride = sum(1 for s in stride_counts if s >= 4)
print("12. Ancaman >= 4 kategori STRIDE:", four_stride, "== 0 ->", "OK" if four_stride == 0 else "PERIKSA")

# 13. Porsi E:
porsi_e = e_counts / len(c_filled)
print("13. Porsi ancaman bertanda E:", porsi_e, "< 0.5 ->", "OK" if porsi_e < 0.5 else "PERIKSA")

# 14. Level risiko berbeda:
dread_totals = []
for i in range(5, 5 + len(c_filled)):
    tot = sum(ws_stride[f'{col}{i}'].value or 0 for col in ['K', 'L', 'M', 'N', 'O'])
    dread_totals.append(tot)

levels = set()
for t in dread_totals:
    if t >= 40: levels.add('CRITICAL')
    elif t >= 30: levels.add('HIGH')
    elif t >= 20: levels.add('MEDIUM')
    else: levels.add('LOW')
print("14. Jumlah level risiko berbeda:", len(levels), ">= 2 ->", "OK" if len(levels) >= 2 else "PERIKSA (Levels:", levels, ")")

# 15. Rentang DREAD:
rentang = max(dread_totals) - min(dread_totals)
print("15. Rentang DREAD:", rentang, ">= 6 ->", "OK" if rentang >= 6 else "PERIKSA")

# 16. Skor identik 5:
identik = 0
for i in range(5, 5 + len(c_filled)):
    scores = [ws_stride[f'{col}{i}'].value for col in ['K', 'L', 'M', 'N', 'O']]
    if len(set(scores)) == 1:
        identik += 1
print("16. Baris 5 skor identik:", identik, "== 0 ->", "OK" if identik == 0 else "PERIKSA")

# 17. Alasan skor (S):
s_kosong = sum(1 for i in range(5, 5 + len(c_filled)) if not ws_stride[f'S{i}'].value)
print("17. Ancaman tanpa alasan skor (kolom S):", s_kosong, "== 0 ->", "OK" if s_kosong == 0 else "PERIKSA")

# 18. Bukti (T):
t_kosong = sum(1 for i in range(5, 5 + len(c_filled)) if not ws_stride[f'T{i}'].value)
print("18. Ancaman tanpa bukti (kolom T):", t_kosong, "== 0 ->", "OK" if t_kosong == 0 else "PERIKSA")

# 19. Saran mitigasi (U):
u_kosong = sum(1 for i in range(5, 5 + len(c_filled)) if not ws_stride[f'U{i}'].value)
print("19. Ancaman tanpa saran mitigasi (kolom U):", u_kosong, "== 0 ->", "OK" if u_kosong == 0 else "PERIKSA")
