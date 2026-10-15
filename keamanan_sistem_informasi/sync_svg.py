import re

with open(r'c:\laragon\www\FindServices\keamanan_sistem_informasi\dfd_threat_modeling copy.html', 'r', encoding='utf-8') as f:
    copy_html = f.read()

# Extract the exact SVG from dfd_threat_modeling copy.html
match = re.search(r'(<svg\s+viewBox="0 0 1340 760".*?</svg>)', copy_html, re.DOTALL)
if not match:
    print("Error: Could not find SVG in dfd_threat_modeling copy.html")
    exit(1)

svg_clean = match.group(1)
print(f"Extracted SVG successfully. Length: {len(svg_clean)} characters.")

# Also update dfd_threat_modeling.html with copy_html to keep them identical
with open(r'c:\laragon\www\FindServices\keamanan_sistem_informasi\dfd_threat_modeling.html', 'w', encoding='utf-8') as f:
    f.write(copy_html)
print("Updated dfd_threat_modeling.html to match copy.")
