import sys, io, zipfile, xml.etree.ElementTree as ET
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

xlsx_path = 'keamanan_sistem_informasi/1. template_baru_Praktikum_STRIDE-DREAD.xlsx'
zf = zipfile.ZipFile(xlsx_path)

shared_strings = []
if 'xl/sharedStrings.xml' in zf.namelist():
    ss_tree = ET.fromstring(zf.read('xl/sharedStrings.xml'))
    for si in ss_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
        text = ''.join([t.text or '' for t in si.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')])
        shared_strings.append(text)

wb_tree = ET.fromstring(zf.read('xl/workbook.xml'))
rels_tree = ET.fromstring(zf.read('xl/_rels/workbook.xml.rels'))
rel_map = {rel.attrib['Id']: rel.attrib['Target'] for rel in rels_tree}

sheet_targets = {}
for sheet in wb_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
    s_name = sheet.attrib.get('name')
    r_id = sheet.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
    tgt = rel_map[r_id].lstrip('/')
    if not tgt.startswith('xl/'):
        tgt = 'xl/' + tgt
    sheet_targets[s_name] = tgt

ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def get_cell_value(c):
    t = c.attrib.get('t')
    f = c.find('s:f', ns)
    formula_str = f' [f={f.text}]' if f is not None else ''
    
    if t == 'inlineStr':
        is_elem = c.find('s:is', ns)
        if is_elem is not None:
            val = ''.join([elem.text or '' for elem in is_elem.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')])
            return val + formula_str
    v = c.find('s:v', ns)
    if v is not None and v.text is not None:
        val = v.text
        if t == 's' and val.isdigit():
            val = shared_strings[int(val)]
        return val + formula_str
    return '' + formula_str

def inspect_range(s_name, start_row, end_row):
    sheet_path = sheet_targets[s_name]
    tree = ET.fromstring(zf.read(sheet_path))
    for r in range(start_row, end_row + 1):
        row = tree.find(f'.//s:sheetData/s:row[@r="{r}"]', ns)
        if row is not None:
            cells = [f'{c.attrib.get("r")}(s={c.attrib.get("s")},t={c.attrib.get("t")}): {get_cell_value(c)}' for c in row.findall('s:c', ns)]
            print(f'Row {r}: ' + ' | '.join(cells))

if __name__ == '__main__':
    sheet = sys.argv[1] if len(sys.argv) > 1 else 'Profil_Aplikasi'
    s_r = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    e_r = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    inspect_range(sheet, s_r, e_r)
