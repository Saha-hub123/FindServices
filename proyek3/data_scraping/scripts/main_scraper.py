"""
main_scraper.py
Orchestrator utama untuk menjalankan scraping, transformasi data, dan ekspor
ke format database FindServices (JSON, CSV, Laravel Seeder).

Cara menjalankan:
  python main_scraper.py --source all
  python main_scraper.py --source projects_co_id --limit 5
  python main_scraper.py --source sribu
  python main_scraper.py --source fastwork
  python main_scraper.py --generate-mock
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime

# Impor modul lokal
from scrape_projects_co_id import scrape_projects_co_id, get_sample_projects_co_id_data
from scrape_sribu import scrape_sribu, get_sample_sribu_data
from scrape_fastwork import scrape_fastwork, get_sample_fastwork_data
from data_transformer import DataTransformer

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
CLEAN_DATA_DIR = os.path.join(BASE_DIR, "data", "clean")
SEEDS_DIR = os.path.join(BASE_DIR, "data", "seeds")

def run(source: str = "all", limit: int = 5, use_mock: bool = False):
    logging.info(f"=== Menjalankan Data Scraping FindServices (Sumber: {source}) ===")
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(CLEAN_DATA_DIR, exist_ok=True)
    os.makedirs(SEEDS_DIR, exist_ok=True)

    collected_raw_items = []

    # 1. Scraping projects.co.id
    if source in ["all", "projects_co_id", "projects"]:
        logging.info("--- [1/3] Memproses Projects.co.id ---")
        if use_mock:
            p_data = get_sample_projects_co_id_data()
        else:
            p_pages = max(1, (limit + 24) // 25)
            p_data = scrape_projects_co_id(max_pages=p_pages)
        collected_raw_items.extend(p_data)

    # 2. Scraping Sribu.com
    if source in ["all", "sribu", "sribu_com"]:
        logging.info("--- [2/3] Memproses Sribu.com ---")
        if use_mock:
            s_data = get_sample_sribu_data()
        else:
            s_data = scrape_sribu(limit=limit)
        collected_raw_items.extend(s_data)

    # 3. Scraping Fastwork.id
    if source in ["all", "fastwork", "fastwork_id"]:
        logging.info("--- [3/3] Memproses Fastwork.id ---")
        if use_mock:
            f_data = get_sample_fastwork_data()
        else:
            f_data = scrape_fastwork(limit=limit)
        collected_raw_items.extend(f_data)

    logging.info(f"Total data mentah terkumpul: {len(collected_raw_items)} layanan.")

    # Simpan snapshot data mentah
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_file = os.path.join(RAW_DATA_DIR, f"raw_scraped_{source}_{timestamp}.json")
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(collected_raw_items, f, indent=2, ensure_ascii=False)
    logging.info(f"Raw data disimpan di: {raw_file}")

    # 4. Transformasi Data ke Standar FindServices
    logging.info("--- Memulai Transformasi Data & Normalisasi Schema ---")
    transformer = DataTransformer(collected_raw_items, start_user_id=101, start_service_id=201)
    users, services = transformer.transform()

    # 5. Ekspor ke JSON & CSV
    transformer.save_json(CLEAN_DATA_DIR)
    transformer.save_csv(CLEAN_DATA_DIR)

    # 6. Ekspor ke Laravel Seeder
    seeder_file = os.path.join(SEEDS_DIR, "ScrapedDataSeeder.php")
    transformer.save_laravel_seeder(seeder_file)

    logging.info("=== Proses Selesai dengan Sukses! ===")
    logging.info(f"Summary: {len(users)} Users & {len(services)} Services siap digunakan.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FindServices Data Scraping Orchestrator")
    parser.add_argument("--source", type=str, default="all", choices=["all", "projects_co_id", "sribu", "fastwork"],
                        help="Pilih sumber website: all, projects_co_id, sribu, fastwork")
    parser.add_argument("--limit", type=int, default=5, help="Batas jumlah item per sumber")
    parser.add_argument("--generate-mock", action="store_true", help="Gunakan data sampel tervalidasi tanpa akses web langsung")

    args = parser.parse_args()
    run(source=args.source, limit=args.limit, use_mock=args.generate_mock)
