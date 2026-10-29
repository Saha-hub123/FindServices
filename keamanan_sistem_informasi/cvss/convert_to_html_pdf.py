import os
import re
import subprocess
import markdown

md_path = r'c:\laragon\www\FindServices\keamanan_sistem_informasi\cvss\Laporan_Tugas_Mandiri_CVSS.md'
html_path = r'c:\laragon\www\FindServices\keamanan_sistem_informasi\cvss\Laporan_Tugas_Mandiri_CVSS.html'
pdf_path = r'c:\laragon\www\FindServices\keamanan_sistem_informasi\cvss\Laporan_Tugas_Mandiri_CVSS.pdf'

with open(md_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace KaTeX / math delimiters with clean text or bold text for HTML readability
text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)
text = text.replace(r'$$\text{', '').replace(r'}$$', '').replace(r'$$', '')
text = re.sub(r'\$([^$]+)\$', r'<b>\1</b>', text)

# Convert markdown
html_body = markdown.markdown(text, extensions=['tables', 'fenced_code'])

css = """
@page {
    size: A4;
    margin: 8mm 10mm 8mm 10mm;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-size: 8pt;
    line-height: 1.3;
    color: #1e293b;
    margin: 0;
    padding: 0;
}
h1 {
    font-size: 12pt;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 2px 0;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}
h2 {
    font-size: 9.5pt;
    font-weight: 700;
    color: #1e40af;
    margin: 0 0 4px 0;
    border-bottom: 1.5px solid #3b82f6;
    padding-bottom: 2px;
}
h3 {
    font-size: 8.5pt;
    font-weight: 700;
    color: #1e293b;
    margin: 6px 0 2px 0;
    background: #f1f5f9;
    padding: 2px 5px;
    border-left: 3px solid #2563eb;
}
h4 {
    font-size: 8pt;
    font-weight: 700;
    color: #334155;
    margin: 4px 0 1px 0;
}
p {
    margin: 1.5px 0 2px 0;
}
ul, ol {
    margin: 1.5px 0 2px 0;
    padding-left: 15px;
}
li {
    margin-bottom: 1px;
}
hr {
    border: none;
    border-top: 1px solid #cbd5e1;
    margin: 4px 0;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 3px 0 4px 0;
    font-size: 7.2pt;
    page-break-inside: avoid;
}
th, td {
    border: 1px solid #cbd5e1;
    padding: 2px 4px;
    text-align: left;
    vertical-align: top;
}
th {
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
}
tr:nth-child(even) td {
    background-color: #f8fafc;
}
code {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 7.2pt;
    background-color: #f1f5f9;
    color: #0969da;
    padding: 1px 2px;
    border-radius: 2px;
    word-break: break-all;
}
pre {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 4px 5px;
    border-radius: 3px;
    overflow-x: auto;
    font-size: 6.8pt;
    line-height: 1.15;
    margin: 2px 0 4px 0;
    page-break-inside: avoid;
}
pre code {
    background: none;
    padding: 0;
    color: #334155;
}
blockquote {
    margin: 2px 0;
    padding: 2px 5px;
    background-color: #eff6ff;
    border-left: 2.5px solid #3b82f6;
    font-size: 7.5pt;
    color: #1e3a8a;
}
strong, b {
    color: #0f172a;
}
@media print {
    body {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
}
"""

template = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<title>Laporan Praktikum Mandiri CVSS v4.0</title>
<style>
{css}
</style>
</head>
<body>
{body}
</body>
</html>
"""

full_html = template.replace("{css}", css).replace("{body}", html_body)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(full_html)

browser_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(browser_exe):
    browser_exe = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

cmd = [
    browser_exe,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    html_path
]
subprocess.run(cmd, capture_output=True, text=True)

with open(pdf_path, 'rb') as pf:
    content = pf.read()
    pages = len(re.findall(rb'/Type\s*/Page\b', content))
size_kb = os.path.getsize(pdf_path) / 1024
print(f"Generated PDF: {size_kb:.1f} KB, Total Pages: {pages}")
