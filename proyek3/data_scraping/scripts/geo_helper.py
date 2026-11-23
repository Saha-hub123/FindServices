"""
geo_helper.py
Modul pembantu geolokasi untuk memetakan nama kota/kabupaten di Indonesia
ke koordinat Latitude dan Longitude numerik secara otomatis.
"""

import re
import random

# Basis data koordinat kota-kota besar dan kabupaten di Indonesia
INDONESIAN_CITIES_COORDINATES = {
    "jakarta pusat": (-6.1805, 106.8284, "Jakarta Pusat, DKI Jakarta"),
    "jakarta selatan": (-6.2615, 106.8106, "Jakarta Selatan, DKI Jakarta"),
    "jakarta barat": (-6.1674, 106.7637, "Jakarta Barat, DKI Jakarta"),
    "jakarta timur": (-6.2250, 106.9004, "Jakarta Timur, DKI Jakarta"),
    "jakarta utara": (-6.1384, 106.8640, "Jakarta Utara, DKI Jakarta"),
    "jakarta": (-6.2088, 106.8456, "DKI Jakarta"),
    "bogor": (-6.5971, 106.8060, "Bogor, Jawa Barat"),
    "depok": (-6.4025, 106.7942, "Depok, Jawa Barat"),
    "tangerang": (-6.1783, 106.6319, "Tangerang, Banten"),
    "tangerang selatan": (-6.2888, 106.7179, "Tangerang Selatan, Banten"),
    "bekasi": (-6.2383, 106.9756, "Bekasi, Jawa Barat"),
    "bandung": (-6.9175, 107.6191, "Bandung, Jawa Barat"),
    "cimahi": (-6.8722, 107.5422, "Cimahi, Jawa Barat"),
    "semarang": (-6.9667, 110.4167, "Semarang, Jawa Tengah"),
    "surakarta": (-7.5755, 110.8243, "Surakarta (Solo), Jawa Tengah"),
    "solo": (-7.5755, 110.8243, "Surakarta (Solo), Jawa Tengah"),
    "yogyakarta": (-7.7956, 110.3695, "Kota Yogyakarta, DI Yogyakarta"),
    "jogja": (-7.7956, 110.3695, "Kota Yogyakarta, DI Yogyakarta"),
    "sleman": (-7.7165, 110.3556, "Sleman, DI Yogyakarta"),
    "bantul": (-7.8933, 110.3556, "Bantul, DI Yogyakarta"),
    "surabaya": (-7.2575, 112.7521, "Surabaya, Jawa Timur"),
    "malang": (-7.9666, 112.6326, "Malang, Jawa Timur"),
    "sidoarjo": (-7.4478, 112.7183, "Sidoarjo, Jawa Timur"),
    "denpasar": (-8.6705, 115.2126, "Denpasar, Bali"),
    "badung": (-8.5833, 115.1667, "Badung, Bali"),
    "medan": (3.5952, 98.6722, "Medan, Sumatera Utara"),
    "palembang": (-2.9761, 104.7754, "Palembang, Sumatera Selatan"),
    "padang": (-0.9471, 100.4172, "Padang, Sumatera Barat"),
    "pekanbaru": (0.5071, 101.4478, "Pekanbaru, Riau"),
    "bandar lampung": (-5.4297, 105.2625, "Bandar Lampung, Lampung"),
    "lampung": (-5.4297, 105.2625, "Bandar Lampung, Lampung"),
    "pontianak": (-0.0263, 109.3425, "Pontianak, Kalimantan Barat"),
    "banjarmasin": (-3.3194, 114.5908, "Banjarmasin, Kalimantan Selatan"),
    "balikpapan": (-1.2379, 116.8529, "Balikpapan, Kalimantan Timur"),
    "samarinda": (-0.5022, 117.1536, "Samarinda, Kalimantan Timur"),
    "makassar": (-5.1477, 119.4327, "Makassar, Sulawesi Selatan"),
    "manado": (1.4748, 124.8428, "Manado, Sulawesi Utara"),
}

DEFAULT_CITIES = list(INDONESIAN_CITIES_COORDINATES.values())

def lookup_coordinates(location_str: str) -> tuple:
    """
    Mencari koordinat (lat, lng, formatted_address) dari teks lokasi.
    Jika lokasi string kosong atau "Online"/"Remote", mengembalikan default acak kota di Indonesia
    dengan sedikit jitter/variasi koordinat realistis.
    """
    if not location_str or not isinstance(location_str, str):
        lat, lng, addr = random.choice(DEFAULT_CITIES)
        return (lat + random.uniform(-0.02, 0.02), lng + random.uniform(-0.02, 0.02), addr)
    
    clean_loc = location_str.lower().strip()
    
    # Deteksi kecocokan kota dalam string
    for city_key, (lat, lng, addr) in INDONESIAN_CITIES_COORDINATES.items():
        # Cek kata utuh atau substring
        if re.search(r'\b' + re.escape(city_key) + r'\b', clean_loc):
            # Berikan variasi mikro (+- 500m hingga 1km) agar tidak persis menumpuk di 1 titik
            jitter_lat = round(lat + random.uniform(-0.015, 0.015), 6)
            jitter_lng = round(lng + random.uniform(-0.015, 0.015), 6)
            return (jitter_lat, jitter_lng, f"{location_str} ({addr})")

    # Jika disebutkan "Indonesia", "Online", atau kota tidak terdaftar
    lat, lng, addr = INDONESIAN_CITIES_COORDINATES["jakarta selatan"]
    jitter_lat = round(lat + random.uniform(-0.03, 0.03), 6)
    jitter_lng = round(lng + random.uniform(-0.03, 0.03), 6)
    return (jitter_lat, jitter_lng, location_str if location_str else addr)
