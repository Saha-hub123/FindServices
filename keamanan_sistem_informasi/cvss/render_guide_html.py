import os
import markdown

md_path = r'c:\laragon\www\FindServices\keamanan_sistem_informasi\cvss\Panduan_Pengisian_CVSS_Template.md'
html_path = r'c:\laragon\www\FindServices\keamanan_sistem_informasi\cvss\Panduan_Pengisian_CVSS_Template.html'

with open(md_path, 'r', encoding='utf-8') as f:
    text = f.read()

html_body = markdown.markdown(text, extensions=['tables', 'fenced_code'])

css = """
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.5;
    color: #1e293b;
    max-width: 1300px;
    margin: 0 auto;
    padding: 24px;
    background-color: #f8fafc;
}
.container {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 32px;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}
h1 {
    color: #0f172a;
    font-size: 18pt;
    border-bottom: 3px solid #2563eb;
    padding-bottom: 8px;
    margin-top: 0;
}
h2 {
    color: #1e40af;
    font-size: 14pt;
    margin-top: 24px;
}
h3 {
    color: #0f172a;
    font-size: 12pt;
    background: #f1f5f9;
    padding: 6px 12px;
    border-left: 4px solid #2563eb;
    border-radius: 2px;
    margin-top: 24px;
}
h4 {
    color: #334155;
    font-size: 10.5pt;
    margin-top: 16px;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 4px;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 8pt;
    background: #ffffff;
}
th, td {
    border: 1px solid #cbd5e1;
    padding: 6px 8px;
    text-align: left;
    vertical-align: top;
}
th {
    background-color: #0f172a;
    color: #ffffff;
    font-weight: 600;
}
tr:nth-child(even) td {
    background-color: #f8fafc;
}
tr:hover td {
    background-color: #f1f5f9;
}
code {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 8pt;
    background-color: #f1f5f9;
    color: #0969da;
    padding: 2px 4px;
    border-radius: 3px;
    word-break: break-all;
}
pre {
    background: #1e293b;
    color: #f8fafc;
    padding: 14px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 8pt;
    line-height: 1.35;
}
pre code {
    background: none;
    color: inherit;
    padding: 0;
}
ul, ol {
    padding-left: 24px;
}
li {
    margin-bottom: 4px;
}
hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 20px 0;
}
.badge-critical {
    background: #fee2e2;
    color: #991b1b;
    font-weight: bold;
    padding: 2px 6px;
    border-radius: 4px;
}
.badge-high {
    background: #ffedd5;
    color: #9a3412;
    font-weight: bold;
    padding: 2px 6px;
    border-radius: 4px;
}
.badge-med {
    background: #fef9c3;
    color: #854d0e;
    font-weight: bold;
    padding: 2px 6px;
    border-radius: 4px;
}
"""

template = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<title>Panduan Pengisian Manual Template CVSS v4.0 - FindServices</title>
<style>
{css}
</style>
</head>
<body>
<div class="container">
{body}
</div>
</body>
</html>
"""

full_html = template.replace("{css}", css).replace("{body}", html_body)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(full_html)

print("Generated HTML at:", html_path)
