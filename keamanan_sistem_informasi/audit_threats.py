import openpyxl

wb = openpyxl.load_workbook(r'c:\laragon\www\FindServices\keamanan_sistem_informasi\1. template_baru_Praktikum_STRIDE-DREAD.xlsx', data_only=False)
ws_t = wb['STRIDE_DREAD_Template']

print("=== 10 THREATS DETAILED AUDIT ===")
threats_data = []
for r in range(5, 15):
    tid = ws_t[f'B{r}'].value
    desc = ws_t[f'C{r}'].value
    s = ws_t[f'D{r}'].value
    t = ws_t[f'E{r}'].value
    rep = ws_t[f'F{r}'].value
    i = ws_t[f'G{r}'].value
    d = ws_t[f'H{r}'].value
    e = ws_t[f'I{r}'].value
    
    k = ws_t[f'K{r}'].value
    l = ws_t[f'L{r}'].value
    m = ws_t[f'M{r}'].value
    n = ws_t[f'N{r}'].value
    o = ws_t[f'O{r}'].value
    
    p = k + l + m + n + o
    if p >= 40:
        lvl = "CRITICAL"
    elif p >= 30:
        lvl = "HIGH"
    elif p >= 20:
        lvl = "MEDIUM"
    else:
        lvl = "LOW"
        
    alasan = ws_t[f'S{r}'].value
    bukti = ws_t[f'T{r}'].value
    mitigasi = ws_t[f'U{r}'].value
    
    stride_list = []
    if s == 1: stride_list.append("S")
    if t == 1: stride_list.append("T")
    if rep == 1: stride_list.append("R")
    if i == 1: stride_list.append("I")
    if d == 1: stride_list.append("D")
    if e == 1: stride_list.append("E")
    
    threats_data.append({
        'row': r,
        'id': tid,
        'desc': desc,
        'stride': stride_list,
        'dread': [k, l, m, n, o],
        'total': p,
        'level': lvl,
        'alasan': alasan,
        'bukti': bukti,
        'mitigasi': mitigasi
    })
    print(f"Row {r:2d} | ID: {tid} | Total: {p} | Lvl: {lvl} | STRIDE: {','.join(stride_list)} | DREAD: {k},{l},{m},{n},{o}")

print("\n=== SUMMARY RECALCULATION ===")
print("Critical count:", sum(1 for t in threats_data if t['level'] == 'CRITICAL'))
print("High count:", sum(1 for t in threats_data if t['level'] == 'HIGH'))
print("Medium count:", sum(1 for t in threats_data if t['level'] == 'MEDIUM'))
print("Low count:", sum(1 for t in threats_data if t['level'] == 'LOW'))
print("Average DREAD:", sum(t['total'] for t in threats_data) / len(threats_data))

stride_sum = {
    'S': sum(1 for t in threats_data if 'S' in t['stride']),
    'T': sum(1 for t in threats_data if 'T' in t['stride']),
    'R': sum(1 for t in threats_data if 'R' in t['stride']),
    'I': sum(1 for t in threats_data if 'I' in t['stride']),
    'D': sum(1 for t in threats_data if 'D' in t['stride']),
    'E': sum(1 for t in threats_data if 'E' in t['stride'])
}
print("STRIDE Counts:", stride_sum)
