"""
main_scraper.py
Orchestrator utama untuk menjalankan scraping, transformasi data, dan ekspor
ke format database FindServices (JSON, CSV, Laravel Seeder).

Sumber Data (5 platform):
  1. projects_co_id — Jasa digital/freelance Indonesia
  2. sribu          — Jasa kreatif, desain, IT & marketing
  3. fastwork       — Jasa profesional beragam bidang
  4. sejasa         — Jasa fisik rumah tangga & on-site
  5. olx            — Iklan jasa lokal rumah tangga

Cara menjalankan:
  python main_scraper.py --source all
  python main_scraper.py --source sejasa olx --limit 12
  python main_scraper.py --source projects_co_id,sejasa,sribu --limit 10
  python main_scraper.py --source sejasa --limit 12
  python main_scraper.py --generate-mock
  python main_scraper.py --source sejasa olx --generate-mock
"""

import os
import json
import argparse
import logging
from datetime import datetime
from typing import List

# Impor modul lokal
from scrape_projects_co_id import scrape_projects_co_id, get_sample_projects_co_id_data
from scrape_sribu import scrape_sribu, get_sample_sribu_data
from scrape_fastwork import scrape_fastwork, get_sample_fastwork_data
from scrape_sejasa import scrape_sejasa, get_sample_sejasa_data
from scrape_olx import scrape_olx, get_sample_olx_data
from data_transformer import DataTransformer

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
CLEAN_DATA_DIR = os.path.join(BASE_DIR, "data", "clean")
SEEDS_DIR = os.path.join(BASE_DIR, "data", "seeds")

VALID_SOURCES = ["projects_co_id", "sribu", "fastwork", "sejasa", "olx"]
SOURCE_ALIASES = {
    "projects": "projects_co_id",
    "projects_co_id": "projects_co_id",
    "sribu": "sribu",
    "sribu_com": "sribu",
    "fastwork": "fastwork",
    "fastwork_id": "fastwork",
    "sejasa": "sejasa",
    "sejasa_com": "sejasa",
    "olx": "olx",
    "olx_id": "olx",
    "all": "all",
}

# Distribusi default per sumber saat mode --source all (tanpa --limit kustom)
DEFAULT_LIMITS = {
    "projects_co_id": 10,  # Jasa digital freelance
    "sribu":          15,  # Jasa kreatif, IT, marketing
    "fastwork":       15,  # Jasa profesional beragam
    "sejasa":         12,  # Jasa fisik/rumah tangga
    "olx":            12,  # Iklan jasa lokal
}


def parse_sources(raw_sources: List[str]) -> List[str]:
    """Mem-parsing daftar sumber dari CLI (mendukung pemisah spasi maupun koma)."""
    tokens: List[str] = []
    for item in raw_sources:
        for part in item.split(","):
            cleaned = part.strip().lower()
            if cleaned:
                tokens.append(cleaned)

    if not tokens:
        return list(VALID_SOURCES)

    normalized: List[str] = []
    for tok in tokens:
        if tok not in SOURCE_ALIASES:
            valid_str = ", ".join(["all"] + VALID_SOURCES)
            raise ValueError(f"Sumber '{tok}' tidak dikenali. Pilihan valid: {valid_str}")
        canonical = SOURCE_ALIASES[tok]
        if canonical == "all":
            return list(VALID_SOURCES)
        if canonical not in normalized:
            normalized.append(canonical)

    return normalized


def run(sources: List[str], limit: int = None, use_mock: bool = False):
    selected = parse_sources(sources)
    is_all = len(selected) == len(VALID_SOURCES)
    source_label = "all" if is_all else "_".join(selected)

    logging.info(f"=== Menjalankan Data Scraping FindServices (Sumber: {', '.join(selected)}) ===")
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(CLEAN_DATA_DIR, exist_ok=True)
    os.makedirs(SEEDS_DIR, exist_ok=True)

    collected_raw_items = []
    total_steps = len(selected)

    for idx, src in enumerate(selected, start=1):
        lim = limit if limit is not None else DEFAULT_LIMITS[src]

        if src == "projects_co_id":
            logging.info(f"--- [{idx}/{total_steps}] Memproses Projects.co.id (target: {lim}) ---")
            if use_mock:
                data = get_sample_projects_co_id_data()[:lim]
            else:
                p_pages = max(1, (lim + 24) // 25)
                data = scrape_projects_co_id(max_pages=p_pages)[:lim]

        elif src == "sribu":
            logging.info(f"--- [{idx}/{total_steps}] Memproses Sribu.com (target: {lim}) ---")
            if use_mock:
                data = get_sample_sribu_data()[:lim]
            else:
                data = scrape_sribu(limit=lim)

        elif src == "fastwork":
            logging.info(f"--- [{idx}/{total_steps}] Memproses Fastwork.id (target: {lim}) ---")
            if use_mock:
                data = get_sample_fastwork_data()[:lim]
            else:
                data = scrape_fastwork(limit=lim)

        elif src == "sejasa":
            logging.info(f"--- [{idx}/{total_steps}] Memproses Sejasa.com (target: {lim}) ---")
            if use_mock:
                data = get_sample_sejasa_data()[:lim]
            else:
                data = scrape_sejasa(limit=lim)

        elif src == "olx":
            logging.info(f"--- [{idx}/{total_steps}] Memproses OLX.co.id (target: {lim}) ---")
            if use_mock:
                data = get_sample_olx_data()[:lim]
            else:
                data = scrape_olx(limit=lim)

        else:
            data = []

        collected_raw_items.extend(data)
        logging.info(f"    {src}: {len(data)} layanan dikumpulkan.")

    total_raw = len(collected_raw_items)
    logging.info(f"Total data mentah terkumpul: {total_raw} layanan dari [{', '.join(selected)}].")

    if total_raw == 0:
        logging.error("Tidak ada data terkumpul. Periksa koneksi internet atau gunakan --generate-mock.")
        return

    # Simpan snapshot data mentah
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_file = os.path.join(RAW_DATA_DIR, f"raw_scraped_{source_label}_{timestamp}.json")
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(collected_raw_items, f, indent=2, ensure_ascii=False)
    logging.info(f"Raw data snapshot disimpan di: {raw_file}")

    # Transformasi Data ke Standar FindServices
    logging.info("--- Memulai Transformasi Data & Normalisasi Schema ---")
    transformer = DataTransformer(collected_raw_items, start_user_id=101, start_service_id=201)
    users, services = transformer.transform()

    # Ekspor ke JSON & CSV
    transformer.save_json(CLEAN_DATA_DIR)
    transformer.save_csv(CLEAN_DATA_DIR)

    # Ekspor ke Laravel Seeder
    seeder_file = os.path.join(SEEDS_DIR, "ScrapedDataSeeder.php")
    transformer.save_laravel_seeder(seeder_file)

    logging.info("=== Proses Selesai dengan Sukses! ===")
    logging.info("Summary Akhir:")
    logging.info(f"  - Sumber aktif      : {', '.join(selected)}")
    logging.info(f"  - Raw data mentah   : {total_raw} item")
    logging.info(f"  - Users (penyedia)  : {len(users)}")
    logging.info(f"  - Services (layanan): {len(services)}")
    logging.info(f"  - Output raw        : {raw_file}")
    logging.info(f"  - Output clean      : {CLEAN_DATA_DIR}/")
    logging.info(f"  - Laravel Seeder    : {seeder_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="FindServices Data Scraping Orchestrator (5 Sumber, Multi-Source CLI)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--source",
        nargs="+",
        default=["all"],
        help=(
            "Pilih satu atau beberapa sumber (pisahkan dengan spasi atau koma):\n"
            "  all            = semua 5 platform (default)\n"
            "  projects_co_id = projects.co.id (jasa digital)\n"
            "  sribu          = sribu.com (desain, IT, marketing)\n"
            "  fastwork       = fastwork.id (freelance beragam)\n"
            "  sejasa         = sejasa.com (jasa fisik rumah tangga)\n"
            "  olx            = olx.co.id (jasa lokal)\n"
            "Contoh: --source sejasa olx  atau  --source projects_co_id,sejasa"
        )
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Batas jumlah item per sumber yang dipilih (jika kosong, memakai default per platform)"
    )
    parser.add_argument(
        "--generate-mock",
        action="store_true",
        help="Gunakan dataset terverifikasi tanpa akses internet langsung"
    )

    args = parser.parse_args()
    try:
        run(sources=args.source, limit=args.limit, use_mock=args.generate_mock)
    except ValueError as err:
        parser.error(str(err))
