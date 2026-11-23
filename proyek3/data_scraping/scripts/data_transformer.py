"""
data_transformer.py
Modul untuk membersihkan, menstandarisasi, dan mengekspor data hasil scraping
ke dalam format JSON, CSV, dan Laravel Seeder (ScrapedDataSeeder.php) yang siap
diintegrasikan ke sistem database FindServices.
"""

import json
import csv
import re
import os
import random
from datetime import datetime
from geo_helper import lookup_coordinates

# Mapping kategori website sumber ke Category ID FindServices
# 1: Service AC & Elektronik, 2: Pertukangan & Renovasi, 3: Kebersihan & Cleaning,
# 4: Otomotif & Bengkel, 5: Kecantikan & Salon, 6: Pijat & Kesehatan,
# 7: Desain & Kreatif, 8: IT & Komputer, 9: Pendidikan & Les,
# 10: Fotografi & Video, 11: Angkutan & Pindahan, 12: Lain-lain
CATEGORY_MAPPING = {
    "it": 8, "komputer": 8, "web": 8, "website": 8, "programming": 8, "developer": 8,
    "software": 8, "aplikasi": 8, "laravel": 8, "python": 8, "mobile": 8, "code": 8,
    "desain": 7, "design": 7, "logo": 7, "grafis": 7, "banner": 7, "ui/ux": 7, "illustrasi": 7,
    "video": 10, "animasi": 10, "fotografi": 10, "photo": 10, "audio": 10, "editing": 10,
    "les": 9, "kursus": 9, "edukasi": 9, "tutor": 9, "penerjemah": 9, "bahasa": 9,
    "elektronik": 1, "ac": 1, "laptop": 1, "komputer servis": 1, "servis hp": 1,
    "angkutan": 11, "pindahan": 11, "cargo": 11,
}

def detect_category_id(title: str, tags: str) -> int:
    """Mendeteksi category_id FindServices yang paling cocok berdasarkan judul dan tags."""
    combined = f"{title} {tags}".lower()
    for keyword, cat_id in CATEGORY_MAPPING.items():
        if re.search(r'\b' + re.escape(keyword) + r'\b', combined):
            return cat_id
    # Default ke IT & Komputer (8) atau Desain & Kreatif (7) atau Lain-lain (12)
    return 8 if "web" in combined or "app" in combined else 7

def generate_slug(text: str) -> str:
    """Membuat slug URL yang ramah SEO."""
    text = re.sub(r'[^a-zA-Z0-9\s-]', '', text).lower().strip()
    return re.sub(r'[\s-]+', '-', text)

def clean_phone(phone_raw: str, user_id: int) -> str:
    """Menghasilkan nomor HP Indonesia valid jika platform sumber menyembunyikan nomor asli."""
    if phone_raw and re.match(r'^(08|\+628)[0-9]{8,11}$', phone_raw):
        return phone_raw
    # Dummy nomor HP Indonesia realistis dengan prefix Telkomsel / Indosat / XL
    prefix = random.choice(["0812", "0813", "0821", "0857", "0878", "0896"])
    suffix = f"{user_id:04d}"[-4:]
    middle = f"{random.randint(1000, 9999)}"
    return f"{prefix}{middle}{suffix}"

def clean_email(email_raw: str, name: str, user_id: int) -> str:
    """Menghasilkan email valid unik jika platform sumber menyembunyikan email asli."""
    if email_raw and "@" in email_raw:
        return email_raw.strip().lower()
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', name).lower()
    if not clean_name:
        clean_name = f"freelancer_{user_id}"
    return f"{clean_name}{user_id}@findservices.local"

class DataTransformer:
    def __init__(self, raw_items: list, start_user_id: int = 101, start_service_id: int = 201):
        self.raw_items = raw_items
        self.start_user_id = start_user_id
        self.start_service_id = start_service_id
        self.users = []
        self.services = []

    def transform(self):
        """Memproses data mentah menjadi skema final SERVICES dan USER."""
        user_map = {}
        curr_user_id = self.start_user_id
        curr_svc_id = self.start_service_id

        for item in self.raw_items:
            raw_user = item.get("user", {})
            user_name = raw_user.get("name", "Mitra Penyedia Jasa").strip()
            
            # Cek apakah user sudah terdaftar
            if user_name not in user_map:
                u_lat, u_lng, u_addr = lookup_coordinates(raw_user.get("location", ""))
                u_email = clean_email(raw_user.get("email"), user_name, curr_user_id)
                u_phone = clean_phone(raw_user.get("phone"), curr_user_id)
                u_bio = raw_user.get("bio") or f"Penyedia jasa profesional di bidang {item.get('title', 'layanan digital')} dengan pengalaman terverifikasi."
                
                # Jam operasional
                working_hours = raw_user.get("working_hours") or random.choice([
                    "Senin - Jumat: 08:00 - 17:00 WIB",
                    "Senin - Sabtu: 09:00 - 18:00 WIB",
                    "Setiap Hari: 08:00 - 20:00 WIB",
                    "Fleksibel (Respon Cepat < 1 Jam)"
                ])

                user_obj = {
                    "id": curr_user_id,
                    "name": user_name,
                    "email": u_email,
                    "phone": u_phone,
                    "bio": u_bio[:500],
                    "address": u_addr,
                    "working_hours": working_hours,
                    "role": "user",
                    "avatar": raw_user.get("avatar") or f"https://ui-avatars.com/api/?name={user_name.replace(' ', '+')}&background=random",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                user_map[user_name] = user_obj
                self.users.append(user_obj)
                curr_user_id += 1

            matched_user = user_map[user_name]
            
            # Olah data Service
            title = item.get("title", "Layanan Profesional").strip()
            desc = item.get("description", "").strip() or f"Layanan terpercaya untuk pengerjaan {title}. Dikerjakan dengan standar profesional dan garansi revisi."
            
            # Harga
            price_min = float(item.get("price_min", 100000))
            price_max = float(item.get("price_max", price_min))
            if price_max < price_min:
                price_max = price_min

            # Lokasi & Geospasial
            loc_str = item.get("location") or matched_user["address"]
            s_lat, s_lng, s_formatted_loc = lookup_coordinates(loc_str)
            
            # Rating & Order
            rating_avg = round(float(item.get("rating_avg", random.uniform(4.5, 5.0))), 2)
            completed_orders = int(item.get("total_completed_orders", random.randint(5, 80)))
            
            # Durasi pengerjaan
            duration_raw = item.get("estimated_duration", "3 hari")
            if isinstance(duration_raw, (int, float)):
                duration = f"{int(duration_raw)} hari"
            else:
                duration = str(duration_raw)

            # Tags / Skills
            tags_raw = item.get("tags", [])
            if isinstance(tags_raw, list):
                tags_str = ", ".join(tags_raw)
            else:
                tags_str = str(tags_raw)
            if not tags_str:
                tags_str = "Profesional, Cepat, Berkualitas"

            cat_id = detect_category_id(title, tags_str)
            slug = f"{generate_slug(title)}-{curr_svc_id}"

            service_obj = {
                "id": curr_svc_id,
                "user_id": matched_user["id"],
                "category_id": cat_id,
                "title": title[:150],
                "slug": slug[:180],
                "description": desc,
                "price_min": price_min,
                "price_max": price_max,
                "location": s_formatted_loc,
                "latitude": s_lat,
                "longitude": s_lng,
                "status": item.get("status", "active"),
                "rating_avg": rating_avg,
                "tags": tags_str,
                "total_completed_orders": completed_orders,
                "estimated_duration": duration,
                "source_url": item.get("source_url", ""),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.services.append(service_obj)
            curr_svc_id += 1

        return self.users, self.services

    def save_json(self, output_dir: str):
        """Menyimpan data hasil transformasi ke JSON."""
        os.makedirs(output_dir, exist_ok=True)
        users_file = os.path.join(output_dir, "users.json")
        services_file = os.path.join(output_dir, "services.json")

        with open(users_file, "w", encoding="utf-8") as f:
            json.dump(self.users, f, indent=2, ensure_ascii=False)
        with open(services_file, "w", encoding="utf-8") as f:
            json.dump(self.services, f, indent=2, ensure_ascii=False)

        print(f"[OK] JSON tersimpan: {users_file} ({len(self.users)} users)")
        print(f"[OK] JSON tersimpan: {services_file} ({len(self.services)} services)")

    def save_csv(self, output_dir: str):
        """Menyimpan data hasil transformasi ke CSV."""
        os.makedirs(output_dir, exist_ok=True)
        users_file = os.path.join(output_dir, "users.csv")
        services_file = os.path.join(output_dir, "services.csv")

        if self.users:
            with open(users_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(self.users[0].keys()))
                writer.writeheader()
                writer.writerows(self.users)

        if self.services:
            with open(services_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(self.services[0].keys()))
                writer.writeheader()
                writer.writerows(self.services)

        print(f"[OK] CSV tersimpan: {users_file}")
        print(f"[OK] CSV tersimpan: {services_file}")

    def save_laravel_seeder(self, output_path: str):
        """Menghasilkan file PHP Seeder untuk Laravel FindServices."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        seeder_template = f"""<?php

namespace Database\\Seeders;

use Illuminate\\Database\\Seeder;
use Illuminate\\Support\\Facades\\DB;
use Illuminate\\Support\\Facades\\Hash;
use Carbon\\Carbon;

/**
 * ScrapedDataSeeder
 * Di-generate otomatis dari data hasil scraping platform:
 * - projects.co.id
 * - sribu.com
 * - fastwork.id
 * 
 * Tanggal Generate: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
 */
class ScrapedDataSeeder extends Seeder
{{
    public function run(): void
    {{
        // 1. Nonaktifkan foreign key checks untuk import bersih
        DB::statement('SET FOREIGN_KEY_CHECKS=0;');

        $now = Carbon::now();
        $defaultPassword = Hash::make('password123');

        // 2. Insert Data USERS (Penyedia Jasa / Freelancers)
        $users = [
"""
        for u in self.users:
            clean_bio = u['bio'].replace("'", "\\'").replace("\n", " ")
            clean_addr = u['address'].replace("'", "\\'")
            clean_name = u['name'].replace("'", "\\'")
            seeder_template += f"""            [
                'id' => {u['id']},
                'name' => '{clean_name}',
                'email' => '{u['email']}',
                'phone' => '{u['phone']}',
                'bio' => '{clean_bio}',
                'address' => '{clean_addr}',
                'role' => 'user',
                'password' => $defaultPassword,
                'email_verified_at' => $now,
                'created_at' => $now,
                'updated_at' => $now,
            ],
"""
        seeder_template += """        ];

        foreach ($users as $userData) {
            DB::table('users')->updateOrInsert(
                ['email' => $userData['email']],
                $userData
            );
        }

        // 3. Insert Data SERVICES (Layanan)
        $services = [
"""
        for s in self.services:
            clean_title = s['title'].replace("'", "\\'")
            clean_desc = s['description'].replace("'", "\\'").replace("\n", " ")
            clean_loc = s['location'].replace("'", "\\'")
            clean_slug = s['slug'].replace("'", "\\'")
            seeder_template += f"""            [
                'id' => {s['id']},
                'user_id' => {s['user_id']},
                'category_id' => {s['category_id']},
                'title' => '{clean_title}',
                'slug' => '{clean_slug}',
                'description' => '{clean_desc}',
                'price_min' => {s['price_min']},
                'price_max' => {s['price_max']},
                'location' => '{clean_loc}',
                'latitude' => {s['latitude']},
                'longitude' => {s['longitude']},
                'rating_avg' => {s['rating_avg']},
                'status' => '{s['status']}',
                'created_at' => $now,
                'updated_at' => $now,
            ],
"""
        seeder_template += """        ];

        foreach ($services as $serviceData) {
            DB::table('services')->updateOrInsert(
                ['id' => $serviceData['id']],
                $serviceData
            );
        }

        DB::statement('SET FOREIGN_KEY_CHECKS=1;');
        $this->command->info('ScrapedDataSeeder berhasil mengimpor data user dan services!');
    }
}
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(seeder_template)
        print(f"[OK] Laravel Seeder tersimpan: {output_path}")
