import openpyxl
from openpyxl.drawing.image import Image as XLImage
from PIL import Image as PILImage
import os

xlsx_path = r'c:\laragon\www\FindServices\keamanan_sistem_informasi\1. template_baru_Praktikum_STRIDE-DREAD.xlsx'
png_path  = r'c:\laragon\www\FindServices\keamanan_sistem_informasi\dfd_diagram.png'

# Check PNG dimensions
with PILImage.open(png_path) as im:
    orig_w, orig_h = im.size
    print(f"PNG size: {orig_w} x {orig_h} px")

# Target width in EMU (Excel units: 1 px = 9525 EMU at 96 dpi)
# We want the image to fit nicely in the sheet — ~900px wide
target_w_px = 900
scale = target_w_px / orig_w
target_h_px = int(orig_h * scale)
print(f"Resized to: {target_w_px} x {target_h_px} px")

wb = openpyxl.load_workbook(xlsx_path)
ws = wb['Profil_Aplikasi']

img = XLImage(png_path)
img.width  = target_w_px
img.height = target_h_px

# Anchor at A53 (Section E - DFD area)
ws.add_image(img, 'A53')

wb.save(xlsx_path)
print("[OK] Image embedded and file saved.")
